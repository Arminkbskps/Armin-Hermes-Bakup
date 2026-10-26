# Cloudflare Agent Account Provisioning Walkthrough

Step-by-step verified flow for creating and verifying a Cloudflare account using an autonomous agent email inbox and browser automation.

## Step 1: Prepare Credentials & Inbox
- Email inbox created via Atomic Mail: `hermes-armin@atomicmail.ai`.
- Password generated (min 8 chars, uppercase, lowercase, number, symbol): `Hrm$Wf3nuv58NzVdO8qllbkv!9A`.
- Credentials stored locally in `~/.atomicmail/cloudflare-account.txt` (chmod 600).

## Step 2: Form Completion & Turnstile Solving
1. Navigate browser to `https://dash.cloudflare.com/sign-up`.
2. Fill inputs:
   - `fill_input('input[name="email"]', EMAIL)`
   - `fill_input('input[name="password"]', PASSWORD)`
3. Cloudflare Turnstile widget appears inside an out-of-process iframe (invisible to standard DOM `querySelector('iframe')`).
   - Find Turnstile container DIV: bounds top ~611, left ~656.
   - Deliver click at `(x=700, y=646)`.
   - Verify `document.querySelector('input[name="cf_challenge_response"]').value.length > 700`.
4. Click `Sign up` button (`button[type="submit"]`).

## Step 3: Email Verification Loop
1. Cloudflare redirects to dashboard with an unverified banner and sends an activation email.
2. Poll Atomic Mail inbox:
   ```bash
   npx --package=@atomicmail/agent-skill atomicmail jmap_request --ops-file list_inbox.json
   ```
3. Fetch full email body with `fetchAllBodyValues: true`:
   ```bash
   npx --package=@atomicmail/agent-skill atomicmail jmap_request \
     --ops '[["Email/get", {"accountId": "$ACCOUNT_ID", "ids": ["<ID>"], "properties": ["id", "subject", "bodyValues"], "fetchAllBodyValues": true}, "g0"]]'
   ```
4. Extract verification URL: `https://dash.cloudflare.com/email-verification?token=...`.
5. Open verification URL in browser: redirects to `https://dash.cloudflare.com/<ACCOUNT_ID>/home`. Account is now active.

## Step 4: Global API Key Extraction & Verification
1. Navigate browser to `https://dash.cloudflare.com/profile/api-tokens`.
2. Click `View` button next to `Global API Key`.
3. Modal prompts for identity verification: click `Send Verification Code`.
4. Poll inbox for subject `"Your login verification code"`.
5. Extract the 7-digit code from plaintext body (`grep -oE '[0-9]{7}'`).
6. In modal:
   - Click modal's challenge widget (`div[data-testid="challenge-widget-container"]` around x=770, y=495).
   - Fill input `input[data-testid="confirm-code-field"]` with the 7-digit code.
   - Click `button[data-testid="confirm-code-modal-confirm-btn"]`.
7. Extract Global API Key from revealed `textarea[name="api_key"]` (starts with `cfk_...`).
8. Verify key immediately via direct API:
   ```bash
   curl -s "https://api.cloudflare.com/client/v4/user" \
     -H "X-Auth-Email: <EMAIL>" \
     -H "X-Auth-Key: <GLOBAL_API_KEY>"
   ```
