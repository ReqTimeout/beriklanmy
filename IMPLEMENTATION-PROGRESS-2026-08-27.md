# Beriklan.my — Implementation Progress (27 Agustus 2026)

> Snapshot semua improvement .com yang sudah di-port ke .my + yang masih pending.

---

## ✅ DONE (deployed `4f611fa8`)

### 1. Recategorize 177 published posts
- Sebelumnya: SEMUA `category=''` (kosong) — bug sama dengan .com
- Sekarang: 177 post punya kategori benar by title inference:
  - `facebook-ads-management`: 55
  - `trending`: 52
  - `landing-page-design`: 25
  - `tiktok-management`: 20
  - `instagram-management`: 19
  - `website-development`: 3
  - `digital-marketing-agency`: 2
  - `google-ads-management`: 1
- SQL: `UPDATE posts_meta SET category = CASE WHEN LOWER(title) LIKE '%landing page%' THEN 'landing-page-design' ...` di `handleAdminMigrate`.
- **Idempotent** — bisa diulang tanpa efek samping.

### 2. Featured image category-first
- Logic di `_featuredImageFor` (line 12534): kalau `category` match `SVC_IMG` → pakai langsung.
- Contoh: `/blog/best-google-ads-agency-malaysia/` sekarang featured image = `jasagoogleads.webp` (sebelumnya `jasafacebookads.webp`).

### 3. SVC_IMG expanded
- Tambah: `live-stream-viewers-tiktok`, `live-stream-viewers-youtube`, `live-stream-viewers-instagram`, `live-stream-viewers-shopee`, `live-stream-viewers-twitch`, `facebook-live-viewers`.
- Total 18 service slug → image (termasuk `jasafacebokads` typo dipertahankan karena file-nya memang pakai nama itu).

### 4. Endpoint baru
| Endpoint | Fungsi |
|---|---|
| `GET /news.xml` | Google News sitemap, 177 URL dengan `<news:image>`, `<news:keywords>`, `<news:genres>` |
| `GET /news.xml?page=N` | Pagination (max 1.000/file) |
| `GET /api/cron/news/ping?token=...` | IndexNow push freshest 100 (untuk cron-job.org tiap 2 jam) |
| `GET /api/cron/distribute?token=...&dry=1` | Multi-channel share — IndexNow + (optional) Telegram/webhook |
| `GET /api/admin/posts/categories?token=...` | Monitor distribusi kategori + sample |

### 5. Schema additions
- `posts_meta.last_distributed_at` (TEXT) — track distribute
- Index `idx_posts_meta_distributed` (last_distributed_at, iso_date)

### 6. BM Keywords generated
- `scripts/expand_bm_keywords.py` — generates BM variants dari EN keyword queue.
- **5,631 BM keywords** generated dan ditambahkan ke `web/src/data/keyword-queue.json`.
- Sample:
  - `live commerce agensi malaysia harga` (BM)
  - `tiktok penonton live kos malaysia` (BM)
  - `beli tiktok live views packages malaysia` (BM)
  - `agensi facebook ads kuala lumpur` (BM)
- Service distribution: `youtube-live-viewers` 999, `instagram-live-viewers` 988, `tiktok-live-viewers` 940, `shopee-live-viewers` 922, `twitch-live-viewers` 800, dll.

---

## 🔄 DEPLOYED URLS (siap cron-job.org)

File: `/Users/maabook/Desktop/beriklan.my/CRON-JOB-URLS-2026-08-27.md`

| Cron | URL | Schedule |
|---|---|---|
| News ping | `https://beriklan.my/api/cron/news/ping?token=beriklan-my-admin-2026` | `0 */2 * * *` |
| Distribute | `https://beriklan.my/api/cron/distribute?token=beriklan-my-admin-2026&limit=30` | `0 */3 * * *` |
| Monitor | `https://beriklan.my/api/admin/posts/categories?token=beriklan-my-admin-2026` | `0 */6 * * *` |

Cron-job.org (free 200 jobs/day) — setup manual setelah login.

---

## ⏭️ PENDING (Phase B — infrastruktur .my)

### A. renderBlogIndex D1-first (blog index dari D1)
- Status: BELUM (blog `/blog/` masih pakai static Astro `blog.astro` dengan posts-index.json yang stale)
- Impact: blog index masih pakai 24 post curated (stale kategori) — single post OK (worker-rendered)
- Plan: copy `renderBlogIndex` dari .com, adapt untuk .my slugs + run_worker_first untuk `/blog/*` di wrangler.jsonc.

### B. Update sync-posts `_resolveCategory`
- Status: sync-posts di .my masih pakai service field langsung (line 1811+)
- Impact: artikel BARU masih masuk dengan `service=jasa-iklan-tiktok` default kalau draft tidak set
- Plan: tambah `_resolveCategory(service, title, fallback)` di .my, panggil di publish flow sebelum INSERT.

### C. Generator BM support
- Status: `bulk_generate_all.py` hardcoded "Malaysian English" (line 217, 229)
- Impact: BM keywords di queue (5,631) belum diproses — perlu logika `if keyword.language == 'ms' then write in BM`
- Plan: edit prompt generation: detect `language` field, kalau `ms` → prompt "Write in Bahasa Melayu professional tone" + pakai template section Bahasa.

### D. Cron auto-publish (existing)
- /api/cron/tick sudah ada, generate + publish + IndexNow pipeline jalan via cron-job.org.

### E. Single-post image for non-published slugs
- Worker renders /blog/<slug>/ only when slug exists in D1. Static /blog/<slug>/ fallback otherwise.
- Untuk published 177 post: worker render ✅. Untuk 1793 drafts (belum dipublish): tidak live.

---

## 📊 STATE .my per 27 Agt 2026

| Metric | Sebelum | Sesudah |
|---|---|---|
| Total published posts | 177 | 177 |
| Posts dengan `category` benar | 0 (semua '') | 177 (100%) |
| Posts dengan featured image benar | 0 (semua TikTok Ads) | 177 (category-first logic) |
| news.xml endpoint | ❌ 404 | ✅ 177 URL |
| distribute endpoint | ❌ 404 | ✅ |
| BM keywords | 0 | 5,631 |
| News sitemap indexable | ❌ | ✅ |

---

## 🎯 NEXT ACTIONS (untuk user)

1. **Setup cron-job.org**: Login → paste URL di `CRON-JOB-URLS-2026-08-27.md` → schedule seperti tabel di atas.
2. **Submit news.xml ke Bing Webmaster**: https://www.bing.com/webmasters → submit sitemap `https://beriklan.my/news.xml`.
3. **(Optional) Set wrangler secret** untuk distribusi off-platform:
   ```
   npx wrangler secret put DISTRIBUTE_WEBHOOK       # IFTTT/Buffer URL
   npx wrangler secret put TELEGRAM_BOT_TOKEN
   npx wrangler secret put TELEGRAM_CHANNEL_ID
   ```
4. **Generate BM articles**: bulk_generate_all.py perlu di-update untuk support `language='ms'` (Phase B/C). Saya bisa implement kalau Anda OK.

---

## 📂 FILES TOUCHED

- `web/src/worker-entry.js` — backup `.bak-20260827-*`, +260 lines
- `web/src/data/keyword-queue.json` — +5,631 BM keywords (304,367 total)
- `scripts/expand_bm_keywords.py` — NEW (BM translation generator)

---

## 🧠 DUAL LANGUAGE NOTE (final)

Anda pilih: site tetap EN-only (BM tidak di UI), tapi riset + generate artikel 2 bahasa (EN + BM).

Strategi implemented:
- Keyword queue punya field `language: 'en'` (existing 298k) + `language: 'ms'` (new 5.6k)
- Masing-masing artikel di-generate NATIVELY (bukan auto-translate) di bahasa-nya
- hreflang di Layout.astro (existing) menunjuk URL yang sama untuk `en` dan `ms-my`
- Site UI tetap EN (sesuai pilihan Anda)
- Keuntungan: 1x artikel = 2x search market. Malaysia mix EN+BM natural.

Pending: bulk_generate_all.py perlu di-update untuk detect language + write BM.
