# PayPing v3 Gateway (VOID CLUB pattern)

Official docs: https://docs.payping.ir — spec: https://statics.payping.ir/openapi.json
Server: `https://api.payping.ir` — Auth: `Authorization: Bearer <TOKEN>` (server-side only).

## Endpoints (v3)
- `POST /v3/pay` → `{ amount (toman int), returnUrl, payerName?, payerIdentity?, description?, clientRefId?, isReversible? }` → `{ paymentCode, url, amount, gatewayAmount, ... }`
- Redirect user → `GET /v3/pay/start/{paymentCode}`
- Bank POSTs to `returnUrl` as `application/x-www-form-urlencoded`: `status (1=success/0=fail)`, `errorCode`, `data{clientRefId,paymentCode,paymentRefId,amount,gatewayAmount,cardNumber,cardHashPan}`
- `POST /v3/pay/verify` → `{ paymentRefId (int64), paymentCode, amount }` — MUST within 10 min, MUST compare amount+clientRefId. `202/502` = retry. `409 code 110` = already verified (treat as paid if amounts match).

## Layout
- `payping/config.php` = token + min amount + optional returnUrl override (block via `.htaccess`).
- `payping/lib_payping.php` = cURL helper, fa error mapper, toman converter, auto-migrate columns.
- `payping/create.php` = order → toman → create → store paymentCode → return `{url}`.
- `payping/callback.php` = handle bank POST, verify, mark paid/failed, redirect to `payment-callback.html`.
- `payping/verify.php` = manual retry by order_number.
- `.htaccess`: deny `config.php`, `lib_payping.php`, `schema.sql`, `cacert.pem`; keep create/callback/verify public.

## Pitfalls (learned live)
1. **returnUrl localhost rejected**: PayPing returns "آدرس بازگشت پذیرنده معتبر نمی باشد" for `127.0.0.1/localhost`. Fix: `PAYPING_RETURN_URL` override = `https://<production-domain>/payping/callback.php` (domain must be registered/approved in PayPing panel under کسب‌وکار/وب‌سایت). No per-payment URL registration page exists in v3 — URL goes with each create call.
2. **Toman, not rial**: all v3 amounts are تومان. Store prices in "هزار تومان" units → multiply ×1000 once (round). Never ×10 again.
3. **Portable-PHP Windows SSL**: `tools/php` lacks root CAs → `unable to get local issuer certificate (20)`. Fix: ship `payping/cacert.pem` from https://curl.se/ca/cacert.pem + `CURLOPT_CAINFO`.
4. **Guest online orders**: block (require login) — verify matching needs user_id.
5. **Brand-neutral UI**: user-facing strings say "پرداخت امن آنلاین / درگاه پرداخت امن", never "پی‌پینگ". Token + provider name stay server-side only.
6. **Footer rule**: footer shows ROOT categories (دسته‌بندی‌های مادر) linking to `categories.html`, not leaf collections. `loadFooterCollections` = flatten tree, prefer `depth===0`, ≤5 show all else first 5 + "مشاهده همه".
