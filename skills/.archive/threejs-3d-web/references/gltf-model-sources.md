# GLTF/GLB Model Sources for 3D Web Projects

## Sketchfab API (Free Search, No Auth)

Search for downloadable CC-licensed models:

```bash
curl -s "https://api.sketchfab.com/v3/search?type=models&q=low+poly+gaming+room&downloadable=true&sort_by=-likeCount&count=10"
```

Parse results:
```python
import json, sys
data = json.load(sys.stdin)
for m in data.get('results', []):
    print(f"Name: {m['name']}")
    print(f"UID: {m['uid']}")
    print(f"Likes: {m.get('likeCount', 0)}")
    print(f"License: {m.get('license', {}).get('label', 'N/A')}")
```

**Download** requires a Sketchfab API token (free account). Use `/v3/models/{uid}/download` endpoint.

Good search queries for portfolio scenes:
- `low poly gaming room` / `low poly computer desk setup`
- `low poly office` / `programmer desk setup`
- `isometric room` / `stylized 3d room`

Filter for `CC Attribution` license. Vertex counts under 30K load fast.

## Known Good Models (Verified Aug 2026)

| Model | UID / URL | Size | Notes |
|-------|-----------|------|-------|
| jesse-zhou ramenShop | `https://www.jesse-zhou.com/models/ramenShop/glTF/ramenShop.gltf` | 1.5MB | 51 meshes, embedded buffer, **CORS enabled**. Good for demos. |
| Low Poly Gaming Setup | Sketchfab `69145aa6647a42849487b6c3404f5075` | ~15K vertices | 270 likes, CC-BY |
| Low Poly Computer Desk | Sketchfab `c67f61fa444042bcb88ec3e28f0ca7ac` | ~212 likes | CC-BY |
| Gaming Setup (low-poly) | Sketchfab `caffb0d42a594ac2b67970af07d10a5f` | 116 likes | CC-BY |
| Programmer Desk Setup | Sketchfab `ede58cf414534e47b57bf788dc075b17` | 9 likes | CC-BY, stylized |

## Model Format Tips

- **Embedded buffers** (base64 in GLTF JSON): single-file, no texture dependencies. Larger file but simpler deployment.
- **Separate .bin + textures**: smaller initial JSON but needs all files served. Watch CORS on texture URLs.
- **GLB (binary)**: single binary file, most compact. Preferred for production.
- Always set up DRACOLoader even if model isn't Draco-compressed — prevents errors on compressed models.

## Other Sources

- **Three.js official examples repo**: `https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/` — many high-quality GLB models with CORS and no auth. Browse the directory listing via GitHub API. Notable scene models:
  - **LittlestTokyo.glb** (4MB) — detailed animated Japanese street scene, Draco-compressed. Excellent for portfolios. Scale down with `model.scale.set(0.01, 0.01, 0.01)`. Has 1 animation (AnimationMixer auto-play). **Requires DRACOLoader.**
  - `coffeemat.glb` (4.6MB), `space_ship_hallway.glb` (2.8MB), `dungeon_warkarma.glb` (7.8MB)
- **KhronosGroup glTF-Sample-Assets**: `https://github.com/KhronosGroup/glTF-Sample-Assets` — official test models
- **poly.pizza**: Free low-poly models, many CC0 (requires API key for search)
- **Quaternius**: `https://quaternius.com/` — free CC0 low-poly packs (characters, environments, props)

## Sketchfab Gotchas

- API search is free and unauthenticated. Download endpoint requires auth token from a registered account.
- **Programmatic signup fails**: even with no visible CAPTCHA, form submission returns "Registration unexpectedly failed". Create account manually in a browser.
- Viewer CDN URLs for models are not publicly predictable — can't bypass auth by URL guessing.
- The oEmbed endpoint (`/oembed?url=...`) reveals thumbnail and embed iframe but NOT the model download URL.
