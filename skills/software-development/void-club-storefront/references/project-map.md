# VOID CLUB Project Map & Operational Reference

## Workspace Structure & Deploy Folders
- Root Development: `D:/Hermes file`
- Local Standalone Deploy: `D:/Hermes file/VOID_CLUB_PROJECT`
- Cloud Deploy (Railway/Cloudflare): `D:/Hermes file/VOID_CLUB_CLOUD_DEPLOY`

## Key Files & Endpoints
- Server Entrypoint: `run_server.py` (FastAPI + Uvicorn on port 8000)
- Database: SQLite `fashion_shop.db`
- Frontend Pages:
  - `frontend/index.html` — Homepage with Hero Slider & Featured Categories
  - `frontend/shop.html` — Catalog and filters
  - `frontend/product.html` — Product detail view
  - `frontend/account.html` — User Profile, Orders, and Enterprise Admin Portal
  - `frontend/login.html` — Auth (Login/Register)
  - `frontend/checkout.html` — Cart & Checkout flow
- Frontend Scripts & Controllers:
  - `frontend/js/app.js` — Core router, modal handlers, admin dashboard & gallery logic
  - `frontend/js/enterprise-admin.js` — Batch actions, coupons, watermarks
  - `frontend/js/api.js` — REST client wrapper
  - `frontend/js/auth.js` — Session & token management
  - `frontend/js/sr7-slider.js` — Hero banner slider engine

## Folder Synchronization Script Pattern
When changes are made in the root dev copy, sync to deployment folders using:

```python
import shutil, os

files_to_sync = [
    'start.bat',
    'fashion_shop.db',
    'frontend/account.html',
    'frontend/index.html',
    'frontend/shop.html',
    'frontend/login.html',
    'frontend/product.html',
    'frontend/checkout.html',
    'frontend/js/app.js',
    'frontend/js/api.js',
    'frontend/js/auth.js',
    'frontend/js/enterprise-admin.js',
    'frontend/css/responsive.css',
    'frontend/css/login-responsive.css',
    'frontend/css/sr7-slider.css'
]

targets = ['VOID_CLUB_PROJECT', 'VOID_CLUB_CLOUD_DEPLOY']

for target in targets:
    for rel_path in files_to_sync:
        src = os.path.join('.', rel_path)
        dst = os.path.join(target, rel_path)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f'Synced {src} -> {dst}')
```

## Admin Panel State & Lifecycle Rules
1. **Always trigger data fetch on tab switch**: `switchAccountPanel('admin')` must trigger `switchAdminSection(activeSection)` which immediately runs `loadAdminProducts()`, `loadAdminOrders()`, `loadAdminCategories()`, `loadAdminBanners()`, `loadAdminUsers()`, or `loadAdminStats()`.
2. **Explicit Window Attachment**: Any function referenced in `onclick`, `onchange`, `oninput` inside HTML must be attached via `window.<functionName> = <functionName>` in `app.js` to avoid `is not a function` errors.
3. **Cache Busting**: Always append or increment version query strings (e.g. `?v=2.2`) to `<script>` tags in HTML templates after editing JavaScript logic.
