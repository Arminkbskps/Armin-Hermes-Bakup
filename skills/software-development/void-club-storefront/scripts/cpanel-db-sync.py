"""VOID CLUB — local SQLite -> cPanel MySQL sync via the live PHP API.

Usage:
  1. Dump local SQLite tables to JSON:
       sqlite3 fashion_shop.db -> vc_local.json with keys
       categories/products/product_images/product_variants/banners/settings
     (each row as a dict; see SKILL references/cpanel-deploy.md "DB sync" section)
  2. python cpanel-db-sync.py vc_local.json --base http://voidclubs.ir
     --email ADMIN_EMAIL --password ADMIN_PASSWORD

Never hardcode real credentials — pass them as CLI args.
"""
import argparse
import json
import urllib.error
import urllib.request


def call(base, method, path, body=None, token=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return (r.status, json.loads(r.read().decode("utf-8")))
    except urllib.error.HTTPError as e:
        return (e.code, e.read().decode("utf-8")[:1000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dump", help="path to vc_local.json")
    ap.add_argument("--base", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    args = ap.parse_args()

    st, login = call(args.base, "POST", "/api/auth/login",
                     {"email": args.email, "password": args.password})
    assert st == 200, f"login failed: {st} {login}"
    tok = login["access_token"]

    local = json.load(open(args.dump, encoding="utf-8"))

    # --- categories: upsert by slug ---
    _, cats = call(args.base, "GET", "/api/categories")
    smap = {c["slug"]: c["id"] for c in cats}
    for c in local["categories"]:
        if c["slug"] not in smap:
            st, res = call(args.base, "POST", "/api/categories",
                           {"name": c["name"], "slug": c["slug"],
                            "description": c["description"] or "",
                            "image_url": c["image_url"]}, tok)
            print("cat POST", c["slug"], "->", st)
            if st in (200, 201):
                smap[c["slug"]] = res["id"]
        else:
            st, _ = call(args.base, "PUT", f"/api/categories/{smap[c['slug']]}",
                         {"name": c["name"], "slug": c["slug"],
                          "description": c["description"] or "",
                          "image_url": c["image_url"]}, tok)
            print("cat PUT", c["slug"], "->", st)
    lslug = {c["id"]: c["slug"] for c in local["categories"]}

    # --- products (category ids remapped to server ids) ---
    for p in local["products"]:
        imgs = [{"url": i["url"], "is_featured": bool(i["is_featured"])}
                for i in local["product_images"] if i["product_id"] == p["id"]]
        varz = [{"size": v["size"], "color": v["color"], "stock": v["stock"]}
                for v in local["product_variants"] if v["product_id"] == p["id"]]
        payload = {"title": p["title"], "subtitle": p["subtitle"] or "",
                   "slug": p["slug"], "description": p["description"] or "",
                   "price": p["price"], "old_price": p["old_price"],
                   "badge": p["badge"] or "",
                   "category_id": smap.get(lslug.get(p["category_id"])),
                   "is_featured": bool(p["is_featured"]),
                   "images": imgs, "variants": varz}
        st, res = call(args.base, "POST", "/api/products", payload, tok)
        print("prod", p["title"], "->", st,
              (res.get("id") if isinstance(res, dict) else res[:200]))

    # --- banners ---
    for b in local["banners"]:
        st, res = call(args.base, "POST", "/api/banners",
                       {"title": b["title"] or "", "subtitle": b["subtitle"] or "",
                        "image_url": b["image_url"], "link_url": b["link_url"] or "",
                        "button_text": b["button_text"] or "",
                        "display_order": b["display_order"] or 0,
                        "is_active": True}, tok)
        print("banner", b["image_url"], "->", st)

    # --- settings ---
    s = {x["key"]: x["value"] for x in local["settings"]}
    st, _ = call(args.base, "PUT", "/api/settings/storefront",
                 {"search_tags": s.get("search_tags", "")}, tok)
    print("storefront:", st)
    st, _ = call(args.base, "PUT", "/api/settings/bank-card",
                 {"card_number": s.get("bank_card_number", ""),
                  "bank_name": s.get("bank_name", ""),
                  "card_holder": s.get("bank_card_holder", "")}, tok)
    print("bank-card:", st)


if __name__ == "__main__":
    main()
