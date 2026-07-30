#!/bin/bash
# publish_drafts_to_r2.sh — Pack LLM drafts -> upload shards to R2 -> reset queue cursor.
# Re-runnable anytime while bulk_generate_all.py keeps producing drafts.
set -e
ROOT="/Users/maabook/Desktop/beriklan.my"
cd "$ROOT"
echo "=== 1. pack LLM drafts -> NDJSON shards ==="
python3 scripts/pack_llm_drafts.py
echo "=== 2. upload all shards to R2 (myberiklan/publish-queue/) ==="
cd "$ROOT/web"
for f in "$ROOT"/drafts_patched/queue_*.ndjson; do
  name=$(basename "$f")
  echo "  uploading $name ..."
  npx wrangler r2 object put "myberiklan/publish-queue/$name" --file="$f" --remote >/dev/null 2>&1 && echo "    ok"
done
echo "=== 3. reset queue cursor to {shard:0,line:0} ==="
npx wrangler d1 execute beriklan-my-seo --remote --command "INSERT OR REPLACE INTO cron_settings (name, cron) VALUES ('queue_cursor', '{\"shard\":0,\"line\":0}')" >/dev/null 2>&1 && echo "  cursor reset"
echo "=== DONE. Worker drips via hourly /api/cron/tick (150/day). ==="
