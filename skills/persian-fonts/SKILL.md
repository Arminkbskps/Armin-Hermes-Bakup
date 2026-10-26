---
name: persian-fonts
description: "Use when installing Persian font packs."
version: 1.0.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [persian, fonts, webfonts, typography]
    related_skills: [persian-motion-director]
---

# Persian Fonts

## When to Use
- The user sends a font pack (zip/rar) to install and use instead of defaults.
- A web project must self-host a font (woff2 + @font-face) instead of loading a CDN.

Install font packs the user sends (zips/rar from font channels) system-wide, and self-host them for web projects instead of CDN defaults.

## Install a pack

1. Extract. System `unzip` cannot handle AES zips ("unsupported compression method 99") — use Python `pyzipper` (`AESZipFile(path)`, `z.pwd = b'...'`), trying the channel name as password first. For RAR, p7zip/7z silently extracts 0-byte files on some compression methods — use the official `unrar`/`rar` binary instead; when apt has no `unrar` candidate, fetch the rarlinux tarball from rarlab.com, unpack it, and run `./rar/rar x -p<password> <archive> <dest/>`.
2. Install only the needed subset (standard TTF over FaNum/NoEn/OTF/webfont duplicates) to save disk: `mkdir -p ~/.fonts/<family> && cp *.ttf ~/.fonts/<family>/`, then `fc-cache -f ~/.fonts && fc-list | grep -i <family>`.
3. Smoke-test shaping before use: render a Persian line with PIL + raqm (`direction='rtl', language='fa'`) and inspect at full size — joined letters, dots in place, no tofu. A font that installs is not necessarily a font that shapes.

## Self-host for a site

1. Convert one file per weight with fontTools (`TTFont(src); f.flavor = 'woff2'; f.save(out.woff2)`) into the site's fonts dir, add `@font-face` rules with `font-display:swap`, and delete the CDN `<link>` tags.
2. Grep the whole file for leftover references — they hide in three places: body CSS `font-family`, visible footer/credit text, and canvas `c.font=` strings. Zero matches before deploy.
3. Serve locally and curl every weight (expect 200 on each) before pushing.

## Pitfalls

- Verify extraction by file size, not exit code — failed archive methods can exit 0 while writing 0-byte outputs; check bytes before installing.
- Remove extraction temp dirs and archives after a confirmed install; packs are tens of MB on a constrained SSD.
