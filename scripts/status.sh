#!/bin/bash
# status.sh — cek progress generator + drip + sitemap dalam 1 layar
ROOT="/Users/maabook/Desktop/beriklan.my"
cd "$ROOT/web" 2>/dev/null

echo "========== BERIKLAN.MY STATUS =========="
echo "waktu: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

echo "--- 1. PROSES LOKAL ---"
if pgrep -f "bulk_generate_all" >/dev/null; then echo "  ✅ Generator: JALAN (pid $(pgrep -f bulk_generate_all))"; else echo "  ❌ Generator: MATI"; fi
if pgrep -f "autosync_loop" >/dev/null; then echo "  ✅ Auto-sync : JALAN (pid $(pgrep -f autosync_loop))"; else echo "  ❌ Auto-sync : MATI"; fi
echo ""

echo "--- 2. GENERATE (lokal) ---"
GEN=$(python3 -c "import json;print(len(json.load(open('$ROOT/drafts/_progress.json'))['processed_slugs']))" 2>/dev/null || echo "?")
echo "  Artikel ter-generate: $GEN / 298736"
echo "  Batch terakhir di log:"
grep -iE "batch|done|error|fail" "$ROOT/logs/gen_full.log" 2>/dev/null | tail -3 | sed 's/^/    /'
echo ""

echo "--- 3. PUBLISH (live di web) ---"
npx wrangler d1 execute beriklan-my-seo --remote --command \
"SELECT (SELECT COUNT(*) FROM posts_meta) AS live_published, (SELECT COUNT(*) FROM generated_drafts WHERE status='draft') AS buffer_antri, (SELECT cron FROM cron_settings WHERE name='daily_publish_limit') AS per_hari" 2>/dev/null | grep -iE "live_published|buffer_antri|per_hari|[0-9]{1,}" | grep -iE ":" | sed 's/^/  /'
echo ""

echo "--- 4. SITEMAP (yang dilihat Google) ---"
N=$(curl -s "https://beriklan.my/sitemap-blog.xml" | grep -oE "<loc>" | wc -l | tr -d ' ')
echo "  URL blog di sitemap: $N"
echo "========================================"
