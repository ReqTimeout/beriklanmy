# Beriklan.my — Operations Runbook & Status

> Runbook operasional untuk generate + publish artikel SEO beriklan.my.
> Update terakhir: proses generate FULL 298.736 keyword sedang berjalan.

---

## 1. STATUS FASE

| Fase | Judul | Status |
|------|-------|--------|
| Fase 0 | Infrastruktur & Duplikasi Repo | ✅ SELESAI |
| Fase 1 | Translate Situs + Pricing MYR | ✅ SELESAI |
| Fase 2 | Data Layer Malaysia (25 kota) | ✅ SELESAI |
| Fase 3 | Keyword Mining (298.736 keyword) | ✅ SELESAI |
| Fase 4 | Worker & Automation | ✅ SELESAI |
| **Fase 5** | **Bulk Generation Lokal (AI)** | �� **BERJALAN** (~807 → 298.736) |
| **Fase 6** | **Launch Sequence (drip publish + indexing)** | 🔄 **BERJALAN** (150/hari) |
| Fase 7 | Post-Launch: monitoring indexing, kualitas, backlink | ⏭️ BERIKUTNYA |

**Sekarang di:** Fase 5 + 6 berjalan paralel. Setelah generate 298.736 selesai (~9-10 hari)
dan publish drip menyusul, lanjut ke **Fase 7 (post-launch SEO)**.

---

## 2. MESIN AI (ZEN — FREE)

- Endpoint: `https://opencode.ai/zen/v1/chat/completions`
- API key: `~/.beriklan/zen-key`
- Model (gratis): `deepseek-v4-flash-free`, `nemotron-3-ultra-free`
- Auto-rotate antar model kalau kena rate-limit (lockout 15 detik)
- Laju: ~1.200-1.300 artikel/jam (4 workers)

---

## 3. ARSITEKTUR PIPELINE

```
generate lokal (LLM, ZEN free)
  -> drafts/batch_*.json + drafts/_progress.json
  -> pack (pack_llm_drafts.py) -> drafts_patched/queue_NNNNN.ndjson
  -> upload R2 (myberiklan/publish-queue/)
  -> worker refill buffer (generated_drafts, <300 -> isi s/d 2000)
  -> DRIP publish 150/hari (via hourly /api/cron/tick cron-job.org)
  -> D1 posts_meta + posts_content + commit GitHub posts.json
  -> serving dinamis + sitemap-blog.xml dinamis + IndexNow + GSC
```

Kunci anti-spam: publish DITAHAN 150/hari walau generate ribuan (indexing merata).
Anti-duplikat: `generated_drafts.slug UNIQUE` -> INSERT OR IGNORE aman di-refresh berulang.

---

## 4. CARA PANTAU PROGRESS

```bash
# A. LIVE monitor (auto-refresh 10 detik, ada laju + ETA). Ctrl+C untuk keluar.
bash /Users/maabook/Desktop/beriklan.my/scripts/watch.sh

# B. Snapshot lengkap (generate + publish + sitemap)
bash /Users/maabook/Desktop/beriklan.my/scripts/status.sh

# C. Cek cepat jumlah generate saja
cat /Users/maabook/Desktop/beriklan.my/drafts/_progress.json | \
  python3 -c "import sys,json;print(len(json.load(sys.stdin)['processed_slugs']),'generated')"
```

Catatan: JANGAN pantau lewat `logs/gen_full.log` (Python buffer output -> telat).
Pantau lewat `_progress.json` (update tiap batch) = paling akurat.

---

## 5. KALAU FAIL / MATI — RECOVERY

Semua RESUMABLE, tidak ada data hilang, tidak ada artikel dobel.

**A. Generator MATI** (Mac sleep/restart/ke-kill):
```bash
cd /Users/maabook/Desktop/beriklan.my
nohup python3 -u scripts/bulk_generate_all.py --limit 0 --batch 40 --workers 4 --resume > logs/gen_full.log 2>&1 &
```

**B. Auto-sync MATI:**
```bash
cd /Users/maabook/Desktop/beriklan.my
nohup bash scripts/autosync_loop.sh > logs/autosync.log 2>&1 &
```

**C. Keduanya MATI (Mac restart):** jalankan A dan B dua-duanya.

**D. Publish tidak naik (padahal buffer ada):** paksa 1 siklus:
```bash
curl -s "https://beriklan.my/api/cron/tick?token=beriklan-my-admin-2026" | python3 -m json.tool
```

**E. Upload draft manual (kalau autosync mati lama):**
```bash
bash /Users/maabook/Desktop/beriklan.my/scripts/publish_drafts_to_r2.sh
```

**PENTING:** Jaga Mac JANGAN sleep/mati selama generate (colok charger + prevent sleep).
Itu satu-satunya hal yang menghentikan proses lokal.

---

## 6. SCRIPT PENTING

| File | Fungsi |
|------|--------|
| `scripts/bulk_generate_all.py` | Generate artikel via ZEN (prioritas skor tertinggi dulu) |
| `scripts/pack_llm_drafts.py` | Pack drafts -> NDJSON shards + QC |
| `scripts/publish_drafts_to_r2.sh` | Pack -> upload R2 -> reset cursor |
| `scripts/autosync_loop.sh` | Loop tiap 3 jam: jalankan publish_drafts_to_r2.sh |
| `scripts/status.sh` | Snapshot status lengkap |
| `scripts/watch.sh` | Monitor real-time |

---

## 7. INFRA (referensi)

- Worker: `beriklanmy` | D1: `beriklan-my-seo` (id 9339554e-c00a-4b8c-96cf-2ccbf69a6e20)
- R2: `myberiklan` | Repo: `ReqTimeout/beriklanmy`
- Domain: https://beriklan.my | Admin token: `beriklan-my-admin-2026`
- GSC service account (Owner): `beriklanmy@cool-component-463913-b7.iam.gserviceaccount.com`
- IndexNow key: `2f22c16be9437a90ad2285a4af043e10`
- daily_publish_limit (D1 cron_settings): `150`

> JANGAN pernah sentuh/overwrite produksi beriklan.co.id.

---

## 8. FASE 7 (BERIKUTNYA) — Post-Launch SEO

Setelah 298.736 ter-generate & drip publish jalan stabil:
1. Pantau indexing di Google Search Console (coverage, impressions).
2. Cek kualitas sampel artikel (bahasa Melayu/English, internal link, CTA WA).
3. Rotasi GitHub PAT (token lama sudah bocor di chat).
4. Naikkan `daily_publish_limit` bertahap bila indexing sehat (mis. 150 -> 300).
5. Bangun internal linking + backlink Malaysia.
6. Tracking ranking keyword prioritas.

---

## 9. LOG FASE 7 (progress)

- ✅ **GSC Indexing API aktif** (SA jadi Owner): `/api/cron/gsc-indexing` submit per-URL, kuota 200/hari. 58 URL awal sudah disubmit. Sitemap juga diterima GSC (204 x5).
- ✅ **QC skala penuh 58 artikel**: semua HTTP 200, rata-rata 3.287 kata (min 3.019/max 3.548), semua ada WhatsApp + harga RM, 0 artikel tipis.
- ✅ **Fix schema kontak**: telepon placeholder `+62-22-XXXXXXX` → `+62811919328`; schema fallback worker diselaraskan ke Malaysia (RM + English + areaServed Malaysia). WhatsApp tetap +62811919328 (keputusan owner).
- ✅ **Fix blog hub orphan**: `/data/posts-index.json` dulu statis kosong (`[]`) menutupi worker → ditambto `run_worker_first`. Sekarang dinamis dari D1 (58 entri, tumbuh otomatis). `/blog/` kini listing semua artikel.
- ✅ **robots.txt** terverifikasi: `Sitemap:` dideklarasikan, `User-agent: * Allow: /` (hanya blokir AI-scraper).
- ⏭️ Sisa (butuh aksi/waktu): ganti WA ke +60 (kasih nomor), rotasi GitHub PAT, naikkan `daily_publish_limit` 150→300 setelah indexing GSC terbukti sehat.

**Catatan penting (shadowing CF):** file statis di `dist/` selalu menang atas route worker. Route dinamis apa pun (sitemap-blog.xml, data/posts-index.json) WAJIB didaftarkan di `run_worker_first` (wrangler.jsonc) kalau ada file statis senama.



## 10. LOG FASE 4/7 — Dashboard, Interlinking, Publish Limit (progress)

Tanggal: 2026-07-30

### Selesai & terverifikasi (deployed)
- **daily_publish_limit 150 -> 300** di D1 `cron_settings` (name='daily_publish_limit', cron='300'). Per-run tetap Math.min(50, sisa hari); cron-job.org hourly `/api/cron/tick` yang mengisi.
- **Dashboard admin diperkaya** di `/api/admin?token=ADMIN_TOKEN` (HTML) & `&format=json`:
  - Block 9 `coverage`: target per layanan (settings.service_targets, 16 layanan / 298.736) vs `posts_meta` GROUP BY service -> pct. Sekarang 58/298.736 = 0,02%.
  - Block 10 `recent_posts`: 20 artikel terbaru (slug, title, service, iso_date).
  - Block 11 `ranking`: dari `keyword_ranks` (GSC) — latest_date, top3/top10/top100, avg_position, top_keywords, tren 7 hari. Kosong sampai GSC punya data (site baru).
- **service_targets** di-seed ke D1 `settings` (16 layanan, denominator 298.736 dari web/src/data/keyword-queue.json).
- **Cluster interlinking FIX (lever ranking #1)**: `renderBlogPost` related-query salah tabel `FROM posts_content` (cuma kolom slug+content -> error -> 0 link). Diperbaiki ke `FROM posts_meta LIMIT 6`. Verified: artikel facebook-ads kini render 6 link `/blog/<slug>/` (dari 0). Berlaku untuk semua artikel lama+baru tanpa regen.
- **GSC Indexing API aktif** (SA jadi Owner): 58 URL pending di-flush (quota 58/200/hari).
- **Blog hub orphan fix**: `/data/posts-index.json` kini dinamis via run_worker_first (58 entri, auto-grow).
- **WhatsApp**: DIKONFIRMASI tetap nomor .co.id `62811919328` (76 file, 0 nomor +60). JANGAN diganti.

### Catatan / risiko terbuka
- **Generator lokal (pid 92903) idle 0% CPU** — free LLM (ZEN) balikin None / konten terlalu pendek -> generasi artikel baru stall. Buffer masih ada: 29 draft + 58 committed di `generated_drafts`. Publish harian tetap jalan dari buffer, tapi buffer akan habis. Perlu keputusan: ganti model / API key / turunkan target.
- **Ranking dashboard kosong** normal untuk site baru; akan terisi setelah GSC mulai kumpulkan impresi (butuh beberapa hari–minggu) + cron rank-sync jalan.


## 11. LOG FASE 7 — Generator fix, publish rhythm, pillar->cluster (2026-07-30)

- **Generator diperbaiki**: MODELS di scripts/bulk_generate_all.py diperluas 2 -> 6 model gratis ZEN (nemotron-3-ultra-free, ling-3.0-flash-free, north-mini-code-free, deepseek-v4-flash-free, mimo-v2.5-free, laguna-s-2.1-free). Rotasi + lockout otomatis pilih model sehat. Root cause stall: cuma 2 model, 1 kena FreeUsageLimit -> sering kehabisan opsi. Proses di-restart (--resume), verified batch_0013 tertulis, _progress.json 1005 slug, 4 koneksi API aktif. Catatan: stdout ke file di-block-buffer; pantau progres via drafts/_progress.json + batch_*.json, bukan tail log.
- **Publish rhythm -> 40/hari** (cron_settings.daily_publish_limit='40'). MENIMPA angka 300 sebelumnya: user pilih "aman & bertahap" setelah diberi tahu risiko scaled-content-abuse. Kalau mau agresif lagi, set balik ke 300.
- **Pillar -> cluster interlinking (BARU)**: worker inject seksi "Knowledge Hub" (server-rendered, <a href=/blog/slug/>) ke 16 halaman layanan via HTMLRewriter sebelum <footer>. Query posts_meta WHERE service=? ORDER BY iso_date DESC LIMIT 12. 16 path layanan ditambah ke wrangler run_worker_first (kalau tidak, static asset bypass worker). Deployed b60e39c6. Verified: facebook-ads 12 link, landing-page 12, google-ads 1, instagram-management 0 (skip, belum ada artikel). Cache max-age=300.
- **Loop interlinking sekarang lengkap**: cluster->pillar (cta_block artikel) + cluster<->cluster (6 related, fix FROM posts_meta) + pillar->cluster (inject 12) = topical authority penuh.


## 12. LOG FASE 7 — E-E-A-T + Anti-doorway (2026-07-30 17:53)
Worker version 1917f6a7 deployed.

### E-E-A-T (web/src/worker-entry.js, _buildArticleBody + tagAsTrending)
- FIX broken author URL: /tentang-kami/ (404) -> /about-us/ (existing credential page w/ Organization+Person schema, Meta/Google/TikTok Partner awards, foundingDate 2016). Applied in Article schema author.url + author bio card link.
- Byline now a real link: "By <a href=/about-us/>Tim Beriklan</a>" (was plain "Oleh ...").
- Removed Indonesian leftovers on EN site: Dipublikasikan->Published, Oleh->By, "Ditulis oleh"->"Written by", bio text -> English + "across Malaysia" (was "bisnis menengah Indonesia"), "Belum ada artikel."->"No articles yet."
- tagAsTrending CTA: Indonesian -> English, broken /jasa-digital-marketing/ -> /digital-marketing-agency/.
- Verified live: schema url=/about-us/ (1), tentang-kami (0), byline link OK, no ID leftovers, /about-us/=200.

### Anti-doorway (scripts/bulk_generate_all.py, build_prompt)
- Was: identical fixed <h2> template (Introduction/Key Benefits/How It Works/Pricing/FAQ/Conclusion) for ALL 298k -> scaled-content-abuse footprint.
- Now: deterministic per-keyword variant via md5(kw|svc_key): 5 structure templates x 5 editorial angles = 25 combos. Varies heading text, order, extra sections (Common Mistakes / Who Should Consider / Local Considerations / When to Use), word range (550-800). FAQ schema unaffected (site-wide, not content-derived).
- Only affects FUTURE articles; ~1165 already generated keep old structure (small fraction).

### Generator restart
- Killed pid 76399, relaunched pid 19466: --limit 0 --batch 15 --workers 4 --resume (batch 40->15 so progress writes ~3x more often; fixes "looks macet"). Resumed at 1165 processed. 6 ZEN free models rotation. autosync pid 93940 still running.

## 13. LOG — Blog pagination fix + article typography (worker 7b463dec)
- **Bug:** `/blog/page/N/` returned 404 (blog.astro linked page/2 + rel=next, but no route existed).
  **Fix:** added `renderBlogListPage(pageNum, env)` + route `^/blog/page/(\d+)/?$` in worker-entry.js.
  24 posts/page, merges posts_meta + committed drafts (dedupe by slug), newest first.
  page 1 → 301 to /blog/; out-of-range page → 404. Adds canonical + rel prev/next + breadcrumb.
  Verified live: /blog/page/2/ = 200, /blog/page/3/ = 200 (last, "Page 3/3", no dangling next), page/4+ = 404 (only ~3 pages of real posts).
- **Bug:** single-post body used `class="prose prose-lg"` but NO @tailwindcss/typography plugin
  and `.prose-content` not shipped → Tailwind preflight zeroed all h2/p/ul margins → text cramped.
  **Fix:** injected scoped `<style>.article-body{...}</style>` (line-height 1.85, h2 2.75rem top margin,
  proper list/blockquote/table spacing) + switched wrapper to `class="article-body"`.
- **Cleanup:** translated leftover Indonesian labels in `_buildArticleBody` sidebar/related to English
  (Kategori→Categories, Semua Topik→All Topics, Strategi→Strategy, Studi Kasus→Case Studies,
  Artikel Terbaru→Latest Articles, Tag→Tags, Topik Terkait→Related Topics, Artikel Serupa→Related Articles).
- Note: edge propagation took ~50s after deploy before all PoPs served new HTML.
