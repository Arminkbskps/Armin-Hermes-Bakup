#!/usr/bin/env bash
# ditto-fetch.sh — clone a public URL into a Next.js/Vite app via the ditto.site hosted API.
# Source project: https://github.com/ion-design/ditto.site (MIT). Companion skill: ditto-site-clone.
# Run via terminal(background=true, notify=true) — foreground terminal calls cap ~7 min and kill the poll loop.
# Usage: ditto-fetch.sh <url> <out-dir> [mode=single] [styling=tailwind] [framework=next]
# Env: DITTO_POLL_MAX (poll ticks, default 60 ≈ 10 min), DITTO_API_URL, DITTO_API_KEY.
set -uo pipefail

URL="${1:?usage: ditto-fetch.sh <url> <out-dir> [mode] [styling] [framework]}"
OUT="${2:?usage: ditto-fetch.sh <url> <out-dir> [mode] [styling] [framework]}"
MODE="${3:-single}"; STYLING="${4:-tailwind}"; FRAMEWORK="${5:-next}"
DITTO_API_URL="${DITTO_API_URL:-https://api.ditto.site}"

# key: env var wins, else read from ~/.ditto/api_key. Never echo the key.
KEY="${DITTO_API_KEY:-}"
if [ -z "$KEY" ] && [ -f "$HOME/.ditto/api_key" ]; then
  KEY="$(tr -d ' \r\n' < "$HOME/.ditto/api_key")"
fi
if [ -z "$KEY" ]; then
  echo "ERROR: set DITTO_API_KEY or create ~/.ditto/api_key (single line, dtto_live_...)" >&2
  exit 2
fi

# curl that survives a flaky/broken local proxy: retry once in-path, then try direct.
req() { curl -sS --retry 2 --retry-delay 2 --max-time 45 "$@" 2>/dev/null || curl -sS --noproxy '*' --retry 2 --retry-delay 2 --max-time 45 "$@" 2>/dev/null; }

# jsonget <field> — read JSON on stdin, print top-level field (or "" on parse failure)
jsonget() {
  JFIELD="$1" node -e 'let d="";process.stdin.on("data",c=>d+=c);process.stdin.on("end",()=>{try{const j=JSON.parse(d);const v=j[process.env.JFIELD];console.log(v===undefined||v===null?"":String(v))}catch(e){console.log("")}})'
}

echo ">> POST $DITTO_API_URL/v1/clones  (url=$URL mode=$MODE styling=$STYLING framework=$FRAMEWORK)"
RESP="$(curl -sS --max-time 240 -X POST "$DITTO_API_URL/v1/clones" \
  -H "authorization: Bearer $KEY" -H "content-type: application/json" \
  -d "{\"url\":\"$URL\",\"options\":{\"mode\":\"$MODE\",\"styling\":\"$STYLING\",\"framework\":\"$FRAMEWORK\"}}" 2>/dev/null \
  || curl -sS --noproxy '*' --max-time 240 -X POST "$DITTO_API_URL/v1/clones" \
  -H "authorization: Bearer $KEY" -H "content-type: application/json" \
  -d "{\"url\":\"$URL\",\"options\":{\"mode\":\"$MODE\",\"styling\":\"$STYLING\",\"framework\":\"$FRAMEWORK\"}}" 2>/dev/null)"
JOB="$(printf '%s' "$RESP" | jsonget jobId)"
STATUS="$(printf '%s' "$RESP" | jsonget status)"
if [ -z "$JOB" ]; then
  echo "ERROR: no jobId in response. Truncated response:" >&2
  printf '%s\n' "${RESP:-<empty>}" | head -c 800; echo
  echo "Hint: empty = both proxy and direct paths failed (start the proxy app on 127.0.0.1:10808, or run from another host). Non-empty = read the API error." >&2
  exit 3
fi
echo ">> jobId=$JOB status=${STATUS:-queued}"

# poll until a terminal state; abort after 5 consecutive network failures
POLL_MAX="${DITTO_POLL_MAX:-60}"
i=0; FAILS=0
while [ "$STATUS" != "succeeded" ] && [ "$STATUS" != "failed" ] && [ "$i" -lt "$POLL_MAX" ]; do
  sleep 10; i=$((i+1))
  S="$(req "$DITTO_API_URL/v1/clones/$JOB" -H "authorization: Bearer $KEY" | jsonget status)"
  if [ -z "$S" ]; then
    FAILS=$((FAILS+1))
    if [ "$FAILS" -ge 5 ]; then
      echo "ERROR: 5 consecutive failed status polls (network). Job $JOB may still be running server-side — check GET $DITTO_API_URL/v1/clones/$JOB and re-fetch the bundle." >&2
      exit 6
    fi
  else
    FAILS=0; STATUS="$S"
  fi
  echo "   [$i] status=${STATUS:-?}"
done
if [ "$STATUS" != "succeeded" ]; then
  echo "ERROR: clone did not succeed (status=${STATUS:-unknown}). Inspect: GET $DITTO_API_URL/v1/clones/$JOB" >&2
  exit 4
fi

mkdir -p "$OUT" || { echo "ERROR: cannot create $OUT" >&2; exit 5; }
cd "$OUT" || exit 5

# delivery path 1: one-shot tgz bundle (single request, includes binaries)
if req -L "$DITTO_API_URL/v1/clones/$JOB/bundle?format=tgz" -H "authorization: Bearer $KEY" -o .ditto-bundle.tgz \
   && [ -s .ditto-bundle.tgz ] && tar -xzf .ditto-bundle.tgz 2>/dev/null; then
  rm -f .ditto-bundle.tgz
  echo ">> OK: app unpacked from bundle into $OUT"
else
  # delivery path 2: result JSON + zero-dep unpacker (binaries fetched by reference)
  echo ">> bundle path failed; falling back to result JSON + unpacker"
  req "$DITTO_API_URL/v1/clones/$JOB/result" -H "authorization: Bearer $KEY" -o .ditto-result.json
  if [ -s .ditto-result.json ]; then
    node "$(dirname "$0")/ditto-unpack.mjs" .ditto-result.json . \
      --base-url "$DITTO_API_URL" --api-key "$KEY" || true
  else
    echo "ERROR: could not download result JSON either." >&2
  fi
  rm -f .ditto-result.json
fi

echo ">> jobId=$JOB (inspect: GET $DITTO_API_URL/v1/clones/$JOB)"
echo ">> out-dir contents:"
ls -A "$OUT" | head -20
