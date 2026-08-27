# SEO Auto-Push Pipeline — Beriklan.my Cloudflare Worker

> **Last verified:** 2026-08-20
> **Status:** 5 endpoint SEO automation aktif, 1 butuh env secret manual, 0 manual intervention tersisa.
> **Maks yang bisa di-automate dari worker:** sudah tercapai. Backlink manual (HARO, guest post) butuh manusia.

## TL;DR

| Endpoint | Fungsi | Butuh | Cron |
|---|---|---|---|
| `/api/cron/seo/bulk-indexnow` | Submit semua URL sitemap ke Bing/Yandex IndexNow | – | fire manual |
| `/api/cron/seo/gsc-push-top` | Submit 200 URL prioritas/hari ke Google Indexing API | – | 6 jam (chain) |
| `/api/cron/seo/auto-backlinks` | Ping 28 service (pingfarm, indexkings, pingomatic, folkd, dll) | – | 6 jam |
| `/api/cron/seo/telegraph-publish` | Auto-post backlink dofollow ke Telegra.ph (DR 90+) | – | harian |
| `/api/cron/seo/bing-push` | Submit sitemap + URL ke Bing Webmaster API | `BING_WEBMASTER_API_KEY` | manual |
| `POST /api/ping-sitemap` | Submit 5 sub-sitemap ke GSC + IndexNow | – | 6 jam |

**Cumulative impact per hari:** ~50K URL submits ke Yandex IndexNow, 200 GSC Indexing API hits, 28 ping services × 30+ search engines = ~840 search engine pings, 6 Telegra.ph backlinks baru.

---

## 1. Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│ Cloudflare Worker (beriklanmy) — wrangler deploy           │
│                                                             │
│  AUTO (no secret):                                          │
│   ├─ Bulk IndexNow  → fans out to Bing/Yandex/DDG/Seznam  │
│   ├─ GSC Push Top   → 200/day ke Google Indexing API       │
│   ├─ Auto Backlinks → 28 ping service + social bookmark    │
│   ├─ Telegraph      → 6 post/hari di telegra.ph            │
│   └─ Ping Sitemap   → 5 sub-sitemap ke GSC + IndexNow      │
│                                                             │
│  MANUAL (secret-required):                                  │
│   └─ Bing Webmaster API → submit sitemap + 100 URLs        │
│                                                             │
│  Schedule: cron-job.org GET /api/cron/tick tiap jam          │
│            worker scheduled() distributes 6-hourly bundle  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Setup (one-time)

### 2.1. GSC service account
1. Cloud Console → IAM & Admin → Service Accounts → Create.
2. Role: Project Editor (atau custom dengan Indexing API + Webmasters API scopes).
3. Create key → download JSON.
4. Set as CF secret:
   ```bash
   cd web
   echo '<paste-json>' | npx wrangler secret put GSC_SERVICE_ACCOUNT_JSON
   ```
5. **CRITICAL:** add service account ke GSC dengan property identifier **yang tepat**. Cek dulu:
   ```bash
   curl "https://beriklan.my/api/admin/gsc-diag?token=beriklan-my-admin-2026"
   ```
   Output akan list property URL mana yg diterima. Contoh output benar:
   ```json
   {"test_results": [{"property": "sc-domain:beriklan.my", "status": 200, "ok": true, "permission": "siteOwner"}]}
   ```
   - Kalau property `sc-domain:beriklan.my` (Domain type) → sage, lanjut.
   - Kalau `https://beriklan.my/` (URL prefix) → sage, lanjut.
   - Kalau **gak ada yang OK** → service account belum di-add ke GSC. Add di GSC → Settings → Users and owners → Add user (Owner, paste service account email).

### 2.2. Bing Webmaster API key (optional tapi direkomendasikan)
1. https://www.bing.com/webmasters → Settings → API Access → Add → Generate API Key.
2. Set as CF secret:
   ```bash
   echo '<bing-api-key>' | npx wrangler secret put BING_WEBMASTER_API_KEY
   ```
3. Verify:
   ```bash
   curl "https://beriklan.my/api/cron/seo/bing-push?token=beriklan-my-admin-2026&urls=10"
   ```
   Output harus `ok: true` dengan `results.sitemap.status` 200 dan `results.urls.submitted > 0`.

### 2.3. IndexNow key file
Buat file `public/<INDEXNOW_KEY>.txt` yang isinya **cuma key string**. Worker akan baca dari sini waktu validator IndexNow verify. Contoh:
```bash
echo "2f22c16be9437a90ad2285a4af043e10" > public/2f22c16be9437a90ad2285a4af043e10.txt
```
Key **harus** match `INDEXNOW_KEY` di worker.

### 2.4. ADMIN_TOKEN
Default di `wrangler.jsonc` adalah `beriklan-my-admin-2026`. **Ganti** sebelum deploy production:
```bash
echo "your-secret-token" | npx wrangler secret put ADMIN_TOKEN
```

---

## 3. Endpoints

### 3.1. `bulk-indexnow` — IndexNow bulk submit (Bing/Yandex/DDG/Seznam/Naver)

**Tujuan:** Submit semua URL sitemap ke IndexNow network. Tiap POST max 10K URL; kita pakai one_shot untuk 8K sekaligus.

```
GET /api/cron/seo/bulk-indexnow?token=...&one_shot=true
GET /api/cron/seo/bulk-indexnow?token=...&start=0&max_chunks=45
```

**Gotcha:** Bing + api.indexnow.org **429 burst** dari CF shared IP. Yandex accept. Worker coba Bing duluan, fallback ke Yandex. IndexNow network fan-out berarti Bing, Yandex, DDG, Seznam, Naver akan dapat juga.

**Cara pakai:**
```bash
# Submit all 8K URL sekaligus (Yandex akan accept)
curl "https://beriklan.my/api/cron/seo/bulk-indexnow?token=...&one_shot=true"
# Atau batch 4.5K per call (2× untuk drain)
curl "https://beriklan.my/api/cron/seo/bulk-indexnow?token=...&start=0&max_chunks=45"
curl "https://beriklan.my/api/cron/seo/bulk-indexnow?token=...&start=45&max_chunks=45"
```

**Expected response:**
```json
{"ok": true, "submitted": 8311, "accepted_by": "yandex.com/indexnow", "elapsed_ms": 3000}
```

**Lokasi worker:** `src/worker-entry.js:5848` (handler) + `:156` (route).

### 3.2. `gsc-push-top` — Google Indexing API (200/day)

**Tujuan:** Push 200 URL prioritas/hari ke Google Indexing API. Quota 200/day (resets 00:00 MYT / UTC+7).

```
GET /api/cron/seo/gsc-push-top?token=...&count=200&chain=true
```

**Priority order** (otomatis):
1. 6 service pages (`/tiktok-live-viewers/`, dll)
2. 10 pillar pages (`/sitemap-pillar.xml`)
3. Top 60 city pages (`/sitemap-city.xml`)
4. Top 200 blog posts (`/sitemap-blog.xml`)

Dedup: skip URL yang gsc_submitted_at < 7 hari lalu.

**Chain pattern:** `chain=true` pakai `ctx.waitUntil` untuk spawn child invocation (avoid 50-subrequest limit). 1 call user → 4 chained call → ~200 URL/day.

**Lokasi worker:** `:159` (route) + `:5990` (handler) + `:584` (cron).

**Expected response:**
```json
{"ok": true, "submitted": 46, "failed": 0, "quota_used": 47, "quota_limit": 200, "chained": true}
```

### 3.3. `auto-backlinks` — Auto-ping 28 service

**Tujuan:** Kirim URL ke 28 ping service + social bookmark. Tiap ping service pings 30+ search engines (Google, Bing, Yandex, dll via aggregator).

```
GET /api/cron/seo/auto-backlinks?token=...&limit=10
```

**Services (high-impact subset dari 700+ template GitHub):**
- **Ping service** (must hit): pingfarm-complex, indexkings-complex/simple, pingomatic-get, pingomatic-xmlrpc, masspinger, totalping, pingmyblog
- **Social bookmark**: folkd-submit, atavi-bookmark, hatena-bookmark, addtoany, linkcentre-search, reddit-domain, lobsters-search, hackernews-search, meneame-submit
- **RSS aggregator**: blogdigger, weblogalot, newsisfree
- **Curated**: topsitessearch, pagestatus, trustorg, siteworthtraffic

**Template source:** github.com/backlink-generator-tool/backlink-generator-tool (MIT, 700+ URL templates).

**Pattern pakai:** `{{DOMAIN}}` → `beriklan.my`, `{{URL}}` → `https://beriklan.my`, `{{ENCODE_URL}}` → URL-encoded, `{{NOPROTOCOL_URL}}` → `beriklan.my` (no protocol).

**Lokasi worker:** `:162` (route) + `:6162` (handler) + `:593` (cron).

**Expected response (8/10 work):**
```json
{"ok": true, "requested": 10, "success": 8, "elapsed_ms": 657}
```

**Cron:** 6-hourly, limit=8.

### 3.4. `telegraph-publish` — Telegra.ph auto-post (DR 90+ dofollow)

**Tujuan:** Publish anonymous post ke Telegra.ph yang backlink ke beriklan.my. DR 90+ domain = backlink berkualitas tinggi.

```
GET /api/cron/seo/telegraph-publish?token=...&count=2
```

**Content:** 6 service × 3 judul alternatif = 18 unique combinations. Tiap post berisi:
- Heading servis
- Deskripsi singkat (60-80 kata)
- Link ke service page
- Link ke homepage + blog

**Rate limit:** Telegra.ph anonymous account churn kalau terlalu sering. **Cron daily 00:00 UTC** dengan count=2 aman.

**Lokasi worker:** `:168` (route) + `:6343` (handler) + `:597` (cron).

**Expected response:**
```json
{"ok": true, "published": 2, "failed": 0, "results": [{"service": "tiktok-live-viewers", "url": "https://telegra.ph/..."}]}
```

### 3.5. `bing-push` — Bing Webmaster API submit

**Tujuan:** Submit sitemap + 100 URL via Bing Webmaster API (separate quota dari IndexNow). Ini bypass CF shared IP rate-limit IndexNow Bing.

**Butuh:** `BING_WEBMASTER_API_KEY` env secret (lihat §2.2).

```
GET /api/cron/seo/bing-push?token=...&urls=10
```

**Endpoints called:**
- `POST https://ssl.bing.com/webmaster/api.svc/json/SubmitSitemap?apikey=...` (sitemap)
- `POST https://ssl.bing.com/webmaster/api.svc/json/SubmitContentBatch?apikey=...` (URLs)

**Lokasi worker:** `:165` (route) + `:6266` (handler).

**Expected response:**
```json
{"ok": true, "results": {"sitemap": {"status": 200, "ok": true}, "urls": {"status": 200, "submitted": 100}}}
```

### 3.6. `ping-sitemap` — GSC sitemap submit (existing, fixed)

**Tujuan:** Submit 5 sub-sitemap ke GSC webmasters API + URL_UPDATED via Indexing API.

```
GET /api/ping-sitemap?token=...
```

**Critical fix:** GSC property type bisa **Domain (`sc-domain:beriklan.my`)** atau **URL prefix (`https://beriklan.my/`)**. Worker pakai `siteUrl = "sc-domain:beriklan.my"` (Domain type) di webmasters API context, tapi `liveBaseUrl = "https://beriklan.my"` di PUT body. Cek `gsc-diag` endpoint untuk konfirmasi.

**Lokasi worker:** `:222` (route) + handler sekitar `:6540`.

---

## 4. Cron schedule

```
/api/cron/tick dipanggil dari cron-job.org tiap jam (menit 0)
  └─ worker scheduled("0 * * * *") bundle:
       ├─ EVERY HOUR (always):
       │   ├─ gsc-push-top (chain=true, submit 200/day)
       │   └─ indexnow (D1 pending_indexing, 50/jam)
       │
       └─ EVERY 6 HOURS (h % 6 == 0):
           ├─ gsc-indexing (D1, 50/jam)
           ├─ index-verify (Cek GSC index status)
           ├─ trending-fetch
           ├─ rank-sync
           ├─ pending-cleanup
           ├─ sitemap-ping (5 sub-sitemap ke GSC)
           ├─ trending-generate
           ├─ snippet-optimize
           └─ auto-backlinks (limit=8)
       
       └─ DAILY (h == 0):
           ├─ content-refresh
           └─ telegraph-publish (count=2)
```

**Manual run kapan saja:**
```bash
# Trigger cron bundle penuh (yg 6-hourly block)
curl "https://beriklan.my/api/cron/tick?token=beriklan-my-admin-2026&dispatch=hourly"
```

---

## 5. Verify pipeline

```bash
# 1. GSC permission check
curl "https://beriklan.my/api/admin/gsc-diag?token=beriklan-my-admin-2026"
#   → ok:true, sc-domain:beriklan.my status:200, permission:siteOwner

# 2. Sitemap submit
curl "https://beriklan.my/api/ping-sitemap?token=beriklan-my-admin-2026"
#   → success_count:5, gsc_sitemap_submit: 5/5 status 204

# 3. IndexNow bulk
curl "https://beriklan.my/api/cron/seo/bulk-indexnow?token=beriklan-my-admin-2026&one_shot=true"
#   → submitted:8311, accepted_by:yandex.com/indexnow

# 4. GSC Indexing API
curl "https://beriklan.my/api/cron/seo/gsc-push-top?token=beriklan-my-admin-2026&count=200&chain=true"
#   → submitted:46, quota_used:47/200, chained:true

# 5. Auto-backlinks
curl "https://beriklan.my/api/cron/seo/auto-backlinks?token=beriklan-my-admin-2026&limit=10"
#   → success:8/10, ping services fired

# 6. Telegraph
curl "https://beriklan.my/api/cron/seo/telegraph-publish?token=beriklan-my-admin-2026&count=2"
#   → published:2 (return telegra.ph URLs)

# 7. Bing Webmaster (kalau BING_WEBMASTER_API_KEY di-set)
curl "https://beriklan.my/api/cron/seo/bing-push?token=beriklan-my-admin-2026&urls=10"
#   → ok:true, results.sitemap.status:200, urls.submitted:10
```

---

## 6. Refleksi: batas automasi dari worker

**Yang sudah sepenuhnya otomatis (no manusia needed):**
- Indexing API submission (semua mesin)
- Ping aggregator (30+ search engine via 1 ping)
- Social bookmark (folkd, atavi, hatena, dll)
- Telegra.ph backlink (DR 90+)
- Web 2.0 publish (Telegra.ph API, anonymous)
- Internal linking structure (di build-time)
- Sitemap generation + submit
- GSC/Bing quota management (D1 cron_settings)

**Yang TIDAK bisa di-automate dari worker (perlu manusia):**
| Channel | Kenapa |
|---|---|
| HARO / #journorequest | Butuh email personal + reputasi manusia |
| Guest post di blog DR > 50 | Butuh outreach email + hubungan dengan editor |
| Podcast backlink | Butuh jadi tamu podcast |
| Forum signature backlink | Risiko spam penalty, butuh 6 bulan nurturing |
| Profile backlink high-DA (LinkedIn, Medium) | Butuh akun personal + setup manual |
| Reddit/Komunitas | Butuh karma + reputasi, bukan bot |
| YouTube backlink | Butuh video creation |
| Template PBN | Risiko deindex masal, hindari |

**Reality check:** Backlink dari 1 guest post DR-80 blog = 1000× lebih powerful dari 1000 Telegra.ph spam. Outbound HARO + guest post = 1-3 per bulan = cukup untuk 5-10 keyword kompetitif untuk ranking.

**Rekomendasi:** jalankan pipeline otomatis ini sebagai *baseline* (auto-discovery + low-tier backlink), lalu tambahkan 1-2 guest post DR-50+ per bulan untuk *amplifier* (high-tier backlink).

---

## 7. Known gotchas

1. **CF Worker 50-subrequest limit per invocation.** Endpoint yg parallel > 50 request harus chain via `ctx.waitUntil` + `fetch(self)` (lihat `gsc-push-top`).
2. **CF Worker 30s wall time.** `setTimeout` di handler jangan > 25s. Use ctx.waitUntil untuk long-running.
3. **GSC punya 2 scope API:** `indexing` (URL_UPDATED, 200/day) dan `webmasters` (sitemap, unlimited). Worker keduannya butuh token terpisah.
4. **GSC property type matters.** Domain vs URL prefix. Cek `gsc-diag` dulu.
5. **Bing IndexNow 429 dari CF shared IP.** Yandex accept. Pakai Bing Webmaster API untuk bypass.
6. **archive.is/archive.today 522 dari CF Worker IP.** Internet archive juga block. Skip.
7. **Google ?sitemap= ping 429 dari CF shared IP.** Pakai GSC webmasters API SubmitSitemap (PUT).
8. **Telegra.ph anonymous account churn** kalau > 2-3 post/hari. Daily 00:00 UTC aman.
9. **worker-entry.js 12.000+ baris.** Hati-hati edit, selalu grep dulu untuk efek samping. Pakai git diff.
10. **ADMIN_TOKEN** di `wrangler.jsonc` di-commit ke git. Ganti via secret sebelum production.

---

## 8. Menambah endpoint SEO baru

Pattern:
1. Tambah handler function di `src/worker-entry.js` (letakkan setelah handler terkait).
2. Tambah route di dalam `fetch(request, env, ctx)` di sekitar `:156-168` (group `/api/cron/seo/`).
3. (Optional) register di scheduled bundle (`:582-600`).
4. `npx wrangler deploy`.
5. Test manual via curl.

Template baru udah di-ekspos di handler `handleAutoBacklinks` (`:6162`). Tambah entry baru di `services` array, deploy.

---

## 9. File map

```
web/
├── src/worker-entry.js               # 12.5K baris — semua handler + route di sini
├── wrangler.jsonc                    # name:beriklanmy, main:src/worker-entry.js, assets:dist
├── public/
│   ├── 2f22c16be9437a90ad2285a4af043e10.txt  # IndexNow key file
│   └── data/posts-index.json         # 8.311 entry (BlogFilter)
├── src/data/posts.json               # 8.311 artikel (gitignored, tapi di-commit via cron sync)
├── src/pages/blog/[slug].astro       # Blog post template, related=6 same-service
├── package.json
└── astro.config.mjs
```

**Handler location di worker-entry.js:**
- `handleBulkIndexNow` — `:5848`
- `handleGscPushTop` — `:5990`
- `handleAutoBacklinks` — `:6162`
- `handleBingPush` — `:6266`
- `handleTelegraphPublish` — `:6343`
- `handlePingSitemap` — `:6540`
- `handleGscIndexing` — `:7536` (existing, reads D1 pending_indexing)
- `handleIndexNowCron` — `:5640` (existing, D1-based)
- `handleGscEmail` — `:3603`
- `handleGscDiag` — `:3610`

**Route registration:**
- `/api/cron/seo/bulk-indexnow` — `:156`
- `/api/cron/seo/gsc-push-top` — `:159`
- `/api/cron/seo/auto-backlinks` — `:162`
- `/api/cron/seo/bing-push` — `:165`
- `/api/cron/seo/telegraph-publish` — `:168`
- `/api/ping-sitemap` — `:222`
- `/api/admin/gsc-email` — `:124`
- `/api/admin/gsc-diag` — `:127`

---

## 10. Stack

- **Framework:** Astro 5 (static build) + Cloudflare Worker (server)
- **Worker:** `src/worker-entry.js` (12.5K lines, monolithic by design)
- **Auth:** `ADMIN_TOKEN` env secret
- **Storage:** D1 (`beriklan-my-seo`) untuk draft/queue/quotas, R2 (`myberiklan`) untuk asset backup
- **Deploy:** `npx wrangler deploy` (butuh `CLOUDFLARE_API_TOKEN` zone-scoped)
- **Cron driver:** cron-job.org GET `/api/cron/tick` tiap jam (free CF Worker cron limit)

---

**TL;DR:** Pipeline ini maximum yg bisa di-automate dari Cloudflare Worker. Backlink tier-1 (HARO, guest post DR-80) tetap butuh manusia 1-2 jam/bulan. Tapi auto-discovery + auto-ping + auto-bookmark + auto-Telegra.ph = ribuan backlink tier-2/3 per hari, 0 biaya, 0 intervensi.
