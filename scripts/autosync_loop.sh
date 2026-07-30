#!/bin/bash
# autosync_loop.sh — every 3h: pack drafts -> upload R2 -> reset cursor. Keeps drip fed.
ROOT="/Users/maabook/Desktop/beriklan.my"
while true; do
  echo "===== autosync $(date) ====="
  bash "$ROOT/scripts/publish_drafts_to_r2.sh" || echo "autosync iteration failed (will retry)"
  sleep 10800
done
