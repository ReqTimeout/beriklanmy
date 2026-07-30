#!/bin/bash
# watch.sh — monitor real-time (refresh tiap 10 detik). Ctrl+C untuk berhenti.
ROOT="/Users/maabook/Desktop/beriklan.my"
PREV=0; PREV_T=$(date +%s)
while true; do
  clear
  NOW=$(python3 -c "import json;print(len(json.load(open('$ROOT/drafts/_progress.json'))['processed_slugs']))" 2>/dev/null || echo 0)
  NOW_T=$(date +%s)
  DT=$((NOW_T-PREV_T)); DN=$((NOW-PREV))
  RATE=0; [ $DT -gt 0 ] && RATE=$(( DN*3600/DT ))
  LEFT=$((298736-NOW)); ETA="?"
  [ $RATE -gt 0 ] && ETA=$(python3 -c "print(round($LEFT/$RATE,1))")
  echo "========== LIVE MONITOR (refresh 10s, Ctrl+C stop) =========="
  echo "  waktu     : $(date '+%H:%M:%S')"
  pgrep -f bulk_generate_all >/dev/null && echo "  generator : ✅ JALAN" || echo "  generator : ❌ MATI"
  pgrep -f autosync_loop     >/dev/null && echo "  autosync  : ✅ JALAN" || echo "  autosync  : ❌ MATI"
  echo "  generated : $NOW / 298736"
  echo "  laju      : ~$RATE artikel/jam (+$DN dalam ${DT}s)"
  echo "  sisa      : $LEFT  (ETA ~$ETA jam)"
  echo "============================================================="
  PREV=$NOW; PREV_T=$NOW_T
  sleep 10
done
