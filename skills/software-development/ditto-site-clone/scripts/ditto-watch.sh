#!/usr/bin/env bash
# ditto-watch.sh — watchdog for the queued ditto.site clone job (7wears.ir).
# Silent (exit 0, no output) while the job is queued/running or on network errors.
# When the job completes: downloads + unpacks the app, prints a summary (gets delivered).
# Gives up with a message after 24 silent ticks (~8h at 20m cadence).
KEY_FILE="$HOME/.ditto/api_key"
JOB="5483b633-f9a9-4179-b574-42b541f7fc6f"
OUT="C:/Users/Radon System/workspace/clones/7wears"
API="https://api.ditto.site"
CNT_FILE="$HOME/.ditto/.watch_count"

[ -f "$KEY_FILE" ] || { echo "watchdog: api key file missing"; exit 0; }
KEY="$(tr -d ' \r\n' < "$KEY_FILE")"

STATUS="$(curl -sS --max-time 30 "$API/v1/clones/$JOB" -H "authorization: Bearer $KEY" 2>/dev/null | sed -n 's/.*"status":"\([a-z]*\)".*/\1/p' | head -1)"
[ -z "$STATUS" ] && exit 0   # network hiccup — retry next tick

case "$STATUS" in
  queued|running)
    N=$(( $(cat "$CNT_FILE" 2>/dev/null || echo 0) + 1 ))
    echo "$N" > "$CNT_FILE"
    if [ "$N" -ge 24 ]; then
      echo "still $STATUS after ~8h — hosted worker seems stalled. Consider local run or re-POST later. Job: $JOB"
    fi
    exit 0 ;;
  failed)
    echo "clone job FAILED. Details: GET $API/v1/clones/$JOB — tell Hermes to inspect events."; exit 0 ;;
esac

if [ "$STATUS" != "succeeded" ]; then exit 0; fi

# succeeded → fetch bundle once (idempotent via marker)
mkdir -p "$OUT" 2>/dev/null
cd "$OUT" || { echo "watchdog: cannot cd $OUT"; exit 0; }
if [ -f package.json ]; then
  echo "7wears.ir clone ready (was already fetched): $OUT"
  exit 0
fi
if curl -sS -L --max-time 300 "$API/v1/clones/$JOB/bundle?format=tgz" -H "authorization: Bearer $KEY" -o .ditto-bundle.tgz 2>/dev/null \
   && [ -s .ditto-bundle.tgz ] && tar -xzf .ditto-bundle.tgz 2>/dev/null; then
  rm -f .ditto-bundle.tgz
  FILES=$(find . -type f | wc -l)
  echo "7wears.ir clone is READY: $OUT ($FILES files)"
  ls -A "$OUT" | head -15
else
  echo "job succeeded but bundle download failed — tell Hermes to re-run the fetch for job $JOB"
fi
