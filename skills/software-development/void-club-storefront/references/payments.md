# Payments: PayPing v2 + Card-to-Card (updated 2026-09-10)

## PayPing v2 (official endpoints, amounts in TOMAN)
- Create invoice: `POST https://api.payping.ir/v2/pay` with header
  `Authorization: Bearer <TOKEN>` and body
  `{amount, returnUrl, description, clientRefId, payerIdentity, payerName}`.
  Success returns `{"code": "..."}`.
- Redirect user: `https://api.payping.ir/v2/pay/gotoipg/{code}`.
- Verify: `POST https://api.payping.ir/v2/pay/verify` with `{amount, refId}`.
- `401` = bad token. `400 {"Error":"درگاه پرداخت فعال برای پذیرنده یافت نشد"}`
  = token valid but NO active gateway on the merchant panel — merchant must
  activate a Shaparak gateway in the PayPing panel before live testing.
- `returnUrl` must be a PUBLIC URL (localhost/127.0.0.1 never works for real pay).
- Token storage: env var / `.env`, never in code or docs — redact as `[REDACTED]`.

## Card-to-Card flow (implemented 2026-09-08, cache v=5.2)
- Settings keys in `settings` table: `bank_card_number` (stored formatted
  `XXXX-XXXX-XXXX-XXXX`), `bank_name`, `bank_card_holder`.
  NOTE the inconsistent prefix: bank NAME key is `bank_name`, not
  `bank_card_bank_name` — always read the exact keys from `settings.py`
  (`_bank_card_payload`), never guess.
- Routes: `GET /api/settings/bank-card` (public, checkout reads it),
  `PUT /api/settings/bank-card` (admin; 16-digit validation server-side),
  `POST /api/upload/receipt` (customer-facing, NO admin dep, images only
  ≤8MB, no watermark, stored under `frontend/uploads/receipts/`).
- Order: `payment_method='card_to_card'`, `payment_status='awaiting_verification'`,
  `receipt_image='uploads/receipts/xxx'`. Admin confirms via
  `PUT /api/orders/{id}/status {payment_status:'paid', status:'processing'}`
  (admin-only — receipt confirmation is safe).
- Frontend: `checkout.html` radio `card_to_card` → `#card-to-card-container`
  (bank card UI + `#c2c-file-input` + `#c2c-receipt-url` hidden + preview box
  `#c2c-receipt-preview-box`); `payment-callback.html` handles
  `?status=c2c_pending&method=card_to_card`; admin `account.html` has the
  `bank-card` subtab + C2C badge/receipt lightbox/`handleConfirmReceiptPayment`
  in the orders list. All handlers bound on `window`.
- Schema migration gotcha: `Order.receipt_image` required a manual
  `ALTER TABLE orders ADD COLUMN receipt_image VARCHAR(500)` on ALL THREE
  `fashion_shop.db` files — `create_all` never backfills columns.

## Payment toggles + receipt reject flow (added 2026-09-10, cache v=5.3)
- Settings keys: `pay_online_enabled`, `pay_card_to_card_enabled`,
  `pay_receipt_required` (`"1"/"0"`, default on). Exposed via the SAME
  `/settings/bank-card` payload (`online_enabled`, `card_to_card_enabled`,
  `receipt_required`). Admin toggles live in the bank-card subtab
  (`#toggle-online-enabled`, `#toggle-c2c-enabled`, `#toggle-receipt-required`).
- Enforcement is SERVER-side (`orders.py` `_payment_toggles`): blocked method
  → 400 «روش پرداخت ... غیرفعال است»; receipt optional when
  `pay_receipt_required=0`. Frontend `applyPaymentMethodVisibility()` hides
  the radio row, auto-picks the remaining method, and when BOTH are off,
  disables the place-order button.
- Reject flow: admin sets `payment_status='rejected'` via
  `PUT /orders/{id}/status` — reason is MANDATORY (backend 400 without it),
  stored in `Order.receipt_reject_reason` (ALTER TABLE'd on all 3 DBs).
  Customer sees the red reason box in their orders list and resubmits via
  `PUT /orders/{id}/receipt {receipt_image}` → status back to
  `awaiting_verification`, reason cleared.
- Bank name is injected into the checkout radio label (`#c2c-radio-label-text`)
  and `payment-callback.html` has a `#res-bank-name-row` fed by
  `/settings/bank-card`.

## Rial amount display + copy (added 2026-09-10, cache v=5.4)
- Checkout bank card shows payable amount twice: Toman
  (`#c2c-amount-display`, green) and Rial (`#c2c-amount-rial-display`, cyan
  `#00f0ff`) — Rial = Toman × 10. Each has its own copy button.
- `updateCardToCardAmountDisplays(totalUnits)` recomputes both from
  `renderCheckoutTotals` AND from `renderCheckoutBankCard` — the units→Toman
  conversion is `units * 1000` (DB prices are per-1000). `copyPayableAmount('toman'|'rial')`
  copies PLAIN DIGITS (`String(rawVal)`, no separators/units) so the
  companion-bank app pastes a valid number; it reuses
  `fallbackCopyCardNumber` for non-secure-clipboard contexts.
- Pitfall: inline `onclick="copyPayableAmount('rial')"` requires
  `window.copyPayableAmount` binding — new c2c functions MUST be added to the
  window-binding block at the bottom of `app.js` or the button is dead.
