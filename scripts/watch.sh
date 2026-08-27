#!/bin/bash
# watch.sh — monitor real-time (refresh 10 detik). Ctrl+C untuk berhenti.
# Laju dihitung dari rolling window 3 menit (bukan delta 10 detik), karena
# _progress.json hanya update tiap batch selesai (~2 menit). Delta pendek = 0 terus.
# Compatible with bash 3.2 (macOS) — no negative array indices.
ROOT="/Users/maabook/Desktop/beriklan.my"
TOTAL=298736
TS_HIST=()
CNT_HIST=()

log_progress() {
  NOW=$(python3 -c "import json;print(len(json.load(open('$ROOT/drafts/_progress.json'))['processed_slugs']))" 2>/dev/null || echo 0)
  NOW_T=$(date +%s)
  TS_HIST[${#TS_HIST[@]}]=$NOW_T
  CNT_HIST[${#CNT_HIST[@]}]=$NOW
  CUT=$((NOW_T-360))
  local i
  for i in "${!TS_HIST[@]}"; do
    if [ "${TS_HIST[$i]}" -ge "$CUT" ]; then
      if [ "$i" -gt 0 ]; then
        TS_HIST=("${TS_HIST[@]:$i}")
        CNT_HIST=("${CNT_HIST[@]:$i}")
      fi
      break
    fi
  done
}

rate_over_window() {
  local WINDOW=$1
  local TARGET=$(( $(date +%s) - WINDOW ))
  local n=${#TS_HIST[@]}
  local first_i=-1 last_i=$((n-1)) i
  for i in "${!TS_HIST[@]}"; do
    if [ "${TS_HIST[$i]}" -ge "$TARGET" ]; then first_i=$i; break; fi
  done
  [ "$first_i" -lt 0 ] && return 1
  [ "$last_i" -le "$first_i" ] && return 1
  local DT=$(( ${TS_HIST[$last_i]} - ${TS_HIST[$first_i]} ))
  local DN=$(( ${CNT_HIST[$last_i]} - ${CNT_HIST[$first_i]} ))
  [ "$DT" -le 0 ] && return 1
  echo $(( DN*3600/DT ))
}

log_progress
while true; do
  clear
  log_progress
  NOW=${CNT_HIST[${#CNT_HIST[@]}-1]}
  # 1) Laju dari log batch terakhir (akurat, contoh: "→ 30 ok, 0 fail (110s, 1007/hr)")
  LAST_LINE=$(grep -E "→.*ok,.*fail" "$ROOT/logs/gen_full.log" 2>/dev/null | tail -1)
  RATE_LOG=$(echo "$LAST_LINE" | grep -oE "[0-9]+/hr" | grep -oE "^[0-9]+")
  # 2) Fallback: rolling window 3 menit
  RATE=$(rate_over_window 180)
  RATE=${RATE:-0}
  [ -n "$RATE_LOG" ] && RATE=$RATE_LOG
  LEFT=$((TOTAL-NOW))
  ETA="?"
  [ $RATE -gt 0 ] && ETA=$(python3 -c "print(f'{($LEFT/$RATE):.0f}h')")
  echo "========== LIVE MONITOR (refresh 10s, Ctrl+C stop) =========="
  echo "  waktu     : $(date '+%H:%M:%S')"
  pgrep -f bulk_generate_all >/dev/null && echo "  generator : ✅ JALAN" || echo "  generator : ❌ MATI"
  pgrep -f autosync_loop     >/dev/null && echo "  autosync  : ✅ JALAN" || echo "  autosync  : ❌ MATI"
  echo "  generated : $NOW / $TOTAL"
  echo "  laju (3m) : ~$RATE artikel/jam"
  echo "  sisa      : $LEFT  (ETA ~$ETA)"
  echo "============================================================="
  sleep 10
done
