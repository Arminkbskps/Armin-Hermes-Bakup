# Cut refinement: white-halo removal for AI/flood bg cuts (verified 2026-09-10)

Raw BiRefNet/flood cuts carry the OLD background color inside semi-transparent
edge pixels. Pasted on a dark recolor (e.g. `#240046`) this shows as a white
halo + jagged edges. Measured on a 1200×1200 hoodie mockup cut: edge pixels
averaged brightness **157** vs garment **57**, **44%** of edge pixels near-pure
white (>200). After refinement: edge mean **70**, white share **7%**,
refine cost **~0.4s** (cheap enough for weak hosts).

## `_refine_cut()` — apply to EVERY cut before `apply_background()`

1. **Decontaminate** (standard un-premultiply against white):
   `F = (C − (1−α)·255) / α`, applied ONLY to edge pixels
   (`0.01 < α < 0.99`) and ONLY when the edge mean brightness > 140 —
   the guard keeps light-colored garments untouched.
2. **Erode ~1px** on the alpha channel (`MinFilter(3)`) — eats the last
   white fringe row the model left behind.
3. **Soft edge** (`GaussianBlur(0.7)`) — smooth transition instead of a
   hard threshold cut, so no stair-step jaggies on dark backgrounds.

Wire into all three return points: flood output, HF Space output (both the
in-function return and the chain-level guard), and any future provider.
A second pass is harmless (idempotent-ish) — prefer double coverage over a
missed path.

## Verification recipe (numbers, not eyeballing)

```python
a = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA")).astype(float)
alpha = a[..., 3] / 255.0
edge = (alpha > 0.02) & (alpha < 0.98)
e = a[..., :3][edge]
print(edge.mean(), e.mean(axis=0).round(1), (e.mean(axis=1) > 200).mean())
# healthy cut on dark bg: edge mean < 90, white share < 0.10
```

Note: `vision_analyze` on 1200×1200 PNGs timed out repeatedly this session —
the numpy edge stats above were the reliable check, not visual inspection.
Output size is NOT the quality lever here: mockups stay 1200×1200 end to
end, no resize anywhere; "low quality" complaints on dark recolors are
almost always halo + hard edges, fixed by this pass.
