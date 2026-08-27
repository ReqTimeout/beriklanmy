# Beriklan.my — Migration Plan from .com

> Tujuan: replikasi semua improvement .com ke .my. Update: 27 Agustus 2026.

---

## STATUS (.my saat ini)

| Komponen | Status | Keterangan |
|---|---|---|
| Worker `beriklanmy` | ✅ Active | 13.947 lines |
| D1 `beriklan-my-seo` | ✅ Active | database_id `9339554e-...` |
| R2 `myberiklan` | ✅ Active | publish-queue |
| Bulk Generation | ✅ Berjalan | 3.296 generated (1.873 di D1, 98 published) |
| Publish drip | ✅ Berjalan | 40/hari via cron-job.org → `/api/cron/tick` |
| IndexNow + GSC | ✅ Active | on-publish + tiap 6 jam |
| Sitemap dinamis | ✅ Active | sitemap-blog.xml + llms.txt + rss.xml |
| Internal link mesh | ✅ Active | pillar↔cluster |

---

## PERBEDAAN KRUSIAL .com vs .my

| Aspek | `.com` | `.my` |
|---|---|---|
| Bahasa | Indonesia | English + BM (pricing RM) |
| Service slugs | `jasa-iklan-facebook` | `facebook-ads-management` |
| View-live slugs | `jasa-view-live-tiktok` | `live-stream-viewers` + `jasa-view-live-tiktok` |
| DM slug | `jasa-digital-marketing` | `digital-marketing-agency` |
| Cron trigger | 2 di CF (hourly + email) | 0 di CF (pakai cron-job.org) |
| Kota | Indonesia (kota Indo) | Malaysia (KL, PJ, JB, dll — 25 kota) |
| WhatsApp | +62 811-919-328 | +60 11-XXXX (lokal MY) |
| Pricing | Rp (IDR) | RM (MYR) |
| Hourly generate | Di worker | LOKAL di Mac (ZEN free) |

**Penting:** Service slug NAMA BEDA, jadi:
- SVC_IMG map perlu di-update dengan slug .my
- BLOG_CAT_META label perlu bilingual
- Inference rules perlu detect English keyword (e.g. "facebook ads" → `facebook-ads-management`)

---

## GAP ANALYSIS (.my belum punya)

| # | Fitur | `.com` | `.my` | Action |
|---|---|---|---|---|
| 1 | **news.xml** (Google News sitemap) | ✅ `/news.xml` (1000/page × 13 halaman = 12.756 URL) | ❌ 404 | **Copy handler A1** |
| 2 | **renderBlogIndex** (D1-first blog index) | ✅ `/blog/`, `/blog/page/N/`, `/blog/category/<cat>/` | ❌ Static Astro `blog.astro` | **Copy handler A1** |
| 3 | **handleNewsPing** | ✅ Tiap 2 jam | ❌ | **Copy handler D2** |
| 4 | **handleDistributeCron** | ✅ Tiap 3 jam | ❌ | **Copy handler D3** |
| 5 | **`_featuredImageFor` category-first** | ✅ | ❌ (cuma service-based) | **Replace logic B1** |
| 6 | **`_resolveCategory` di sync-posts** | ✅ | ❌ | **Replace logic B2** |
| 7 | **SVC_IMG +12 service (view-live-platform + buzzer)** | ✅ | partial (live-stream-viewers only) | **Expand B4** |
| 8 | **BLOG_CAT_META bilingual** | ✅ | ❌ | **Build C2 + C3 + C4** |
| 9 | **Recategorize migration (platform-specific)** | ✅ | ❌ | **Copy C1 + add platform rules** |
| 10 | **handleAdminPostsCategories** endpoint | ✅ | ❌ | **Copy endpoint** |
| 11 | **last_distributed_at column + distribute cron** | ✅ | ❌ | **Add migration + cron-job.org call** |
| 12 | **Single-post chrome islands + bodyPre** | ✅ | partial (likely needs check) | **Verify + fix A2 + A3** |
| 13 | **AdSense head script injection** | ✅ | ❌ | **Copy A4** |
| 14 | **Buzzers** sebagai kategori | ✅ | ❌ (view-live covers) | **Add as alias di BLOG_CAT_META** |
| 15 | **TRAFFIC-BOOST-STRATEGY doc** | ✅ | ❌ | **Copy file** |

---

## RENCANA IMPLEMENTASI (5 FASE)

### FASE 1 — Infrastruktur (siap implement sekarang)
- A1, A2, A3, A4 (blog rendering)
- D1, D2, D3 (news.xml + cron)
- E1, E2, E3 (AdSense)
- F1 (WIB → MYT untuk .my — `myTodayStr` UTC+8)
- **Tidak butuh artikel-level changes.**

### FASE 2 — Featured Image + Categori (siap implement)
- B1, B2, B3, B4 (image logic + SVC_IMG update)
- C2, C3, C4, C5, C6 (BLOG_CAT_META bilingual, view-live-platform, buzzer)
- C10 (handleAdminPostsCategories endpoint)
- **Tidak butuh artikel-level changes** (kecuali C1 recategorize yang butuh studi existing).

### FASE 3 — Article-level (PAKAI PANDUAN USER)
- C1 (recategorize migration): user pelajari existing 98 published + 1.873 drafts → kasih panduan keyword mana yang harus recategorize ke platform-specific
- View-live platform-specific subcategories: butuh konfirmasi mana platform prioritas
- Study existing view-live keywords & drafts
- **FASE INI TIDAK BISA AUTONOMOUS — perlu user input.**

### FASE 4 — Distribute Off-Platform
- D4 (env vars opsional): user provide Telegram bot / Buffer webhook
- Pinterest setup (OAuth manual)
- **Tergantung user punya akun.**

### FASE 5 — Tuning MY-specific
- Pricing di RM (sudah ada di build)
- Kota MY-specific sudah ada
- Tone of voice: perlu adapt copywriting untuk MY market (British English + Bahasa Melayu campur)
- **Review needed by user.**

---

## PHASE 1 + 2 — DETAIL IMPLEMENTASI

### A. Handler baru di worker-entry.js

```js
// ─── News sitemap (bilingual MY) ───
async function handleNewsSitemap(request, env) {
  // Sama seperti .com tapi:
  //   - URLs https://beriklan.my/...
  //   - <news:language>en</news:language>
  //   - <news:keywords> dari tags + service + city
}

// ─── Distribute multi-channel ───
async function handleDistributeCron(request, env) {
  // Sama seperti .com tapi URL prefix beriklan.my
}

// ─── Render blog index from D1 ───
async function renderBlogIndex(env, pageNum, category) {
  // Sama seperti .com
}

// ─── _featuredImageFor (category-first) ───
function _featuredImageFor(meta) {
  const catRaw = (meta?.category || "").toLowerCase();
  if (catRaw && SVC_IMG[catRaw]) return `/images/blog/${SVC_IMG[catRaw]}.webp`;
  // ... existing logic
}

// ─── _resolveCategory (sync-posts) ───
function _resolveCategory(service, title, fallback) { ... }
```

### B. SVC_IMG (.my version)

```js
const SVC_IMG = {
  "facebook-ads-management": "jasafacebookads",
  "instagram-ads-management": "jasainstagramads",
  "tiktok-ads-management": "jasatiktokads",
  "google-ads-management": "jasagoogleads",
  "youtube-ads-management": "jasayoutubeads",
  "digital-marketing-agency": "jasadigitalmarketing1",
  "website-development": "jasapembuatanwebsite",
  "landing-page-design": "jasapembuatanwebsite",
  "instagram-management": "jasainstagramads",
  "tiktok-management": "jasatiktokads",
  "live-stream-viewers": "jasaviewlivetiktok",
  "live-stream-viewers-tiktok": "jasaviewlivetiktok",
  "live-stream-viewers-youtube": "jasaviewliveyoutube",
  "live-stream-viewers-instagram": "jasaviewliveinstagram",
  "live-stream-viewers-shopee": "jasaviewliveshopee",
  "live-stream-viewers-twitch": "jasaviewlivetwitch",
  "jasa-view-live-tiktok": "jasaviewlivetiktok",
  "jasa-view-live-youtube": "jasaviewliveyoutube",
  "jasa-view-live-instagram": "jasaviewliveinstagram",
  "jasa-view-live-shopee": "jasaviewliveshopee",
  "jasa-view-live-twitch": "jasaviewlivetwitch",
};
```

### C. BLOG_CAT_META (.my bilingual)

```js
const BLOG_CAT_META = {
  'meta': { label: 'Facebook & Instagram' },
  'tiktok': { label: 'TikTok' },
  'google': { label: 'Google Ads' },
  'youtube': { label: 'YouTube' },
  'facebook-ads-management': { label: 'Facebook Ads' },
  'instagram-ads-management': { label: 'Instagram Ads' },
  'tiktok-ads-management': { label: 'TikTok Ads' },
  'google-ads-management': { label: 'Google Ads Mgmt' },
  'youtube-ads-management': { label: 'YouTube Ads' },
  'digital-marketing-agency': { label: 'Digital Marketing' },
  'live-stream-viewers': { label: 'Live Viewers' },
  'live-stream-viewers-tiktok': { label: 'Live TikTok' },
  'live-stream-viewers-youtube': { label: 'Live YouTube' },
  'live-stream-viewers-instagram': { label: 'Live Instagram' },
  'live-stream-viewers-shopee': { label: 'Live Shopee' },
  'live-stream-viewers-twitch': { label: 'Live Twitch' },
  'jasa-view-live-tiktok': { label: 'Live TikTok (MY)' },
  'jasa-view-live-youtube': { label: 'Live YouTube (MY)' },
  'jasa-view-live-instagram': { label: 'Live Instagram (MY)' },
  'jasa-view-live-shopee': { label: 'Live Shopee (MY)' },
  'jasa-view-live-twitch': { label: 'Live Twitch (MY)' },
  'website-development': { label: 'Website Dev' },
  'landing-page-design': { label: 'Landing Page' },
  'instagram-management': { label: 'Instagram Mgmt' },
  'tiktok-management': { label: 'TikTok Mgmt' },
  'strategy': { label: 'Strategy' },
  'trending': { label: 'Trending' },
  'case-study': { label: 'Case Study' },
};
```

### D. Cron-job.org URLs (pengganti CF trigger)

```
POST https://beriklan.my/api/cron/tick?token=beriklan-my-admin-2026  (hourly)
POST https://beriklan.my/api/cron/news/ping?token=beriklan-my-admin-2026  (every 2h)
POST https://beriklan.my/api/cron/distribute?token=beriklan-my-admin-2026&limit=30  (every 3h)
POST https://beriklan.my/api/cron/growth/gsc-loop?token=beriklan-my-admin-2026  (every 6h)
```

(Sudah ada di OPERATIONS-MY.md — perlu tambah 3 endpoint baru.)

### E. SQL migrations (.my version)

```sql
ALTER TABLE posts_meta ADD COLUMN last_distributed_at TEXT;
CREATE INDEX IF NOT EXISTS idx_posts_meta_distributed ON posts_meta (last_distributed_at, iso_date);
INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('news-ping', '*/15 * * * *', 1, '...');
INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('distribute', '*/30 * * * *', 1, '...');

-- Recategorize platform-specific view-live + buzzer
UPDATE posts_meta SET category = CASE
  WHEN LOWER(title) LIKE '%buzzer tiktok%' THEN 'live-stream-viewers-tiktok'
  ...
END
WHERE slug NOT LIKE 'seed-%' AND slug NOT LIKE 'exp-%'
  AND (category LIKE 'live-stream-viewers%' OR category LIKE 'jasa-view-live%');
```

---

## ARTIKEL YANG PERLU STUDI USER (Phase 3 input)

Sample kategori existing di .my (per 27 Agt):
- 98 published posts_meta
- 1.873 generated_drafts
- 35.863 pending keywords (queue)
- 25 kota Malaysia

**Yang harus user putuskan:**
1. Platform view-live mana prioritas untuk .my? (TikTok = dominan MY, Shopee Live juga besar)
2. Apakah "buzzer" perlu kategori sendiri atau alias view-live?
3. Recategorize rule mana yang dijalankan untuk existing 98 published + 1.873 drafts?
4. Untuk kata kunci MY-specific (e.g. "live streaming KL", "tiktok booster Malaysia"), mapping ke kategori mana?

**Setelah user decide** → implement Fase 3 (SQL migration + re-process).

---

## CHECKLIST SEBELUM DEPLOY

- [ ] Backup `web/src/worker-entry.js` → `.bak-<timestamp>`
- [ ] Backup `web/src/utils/featured_image.js` (kalau ada)
- [ ] Backup `web/src/data/posts.json`
- [ ] Test endpoint manual di localhost:4321 (kalau dev jalan) atau curl langsung ke .my
- [ ] wrangler deploy → catat version_id
- [ ] Verify live:
  - `curl https://beriklan.my/news.xml | head -c 500`
  - `curl https://beriklan.my/blog/ | grep bi-card | head -1`
  - `curl https://beriklan.my/api/admin/posts/categories?token=...&format=json`
  - Sample post: `curl -s https://beriklan.my/blog/<slug>/ | grep featuredImage`

---

## TARGETED IMPROVEMENT UNTUK .my (lebih impactful daripada .com karena domain baru)

Domain `.my` masih sangat baru (index rate 0%). Dengan:
- news.xml → indexing naik (Google News crawler suka sitemap dedicated)
- distribute cron → instant Bing indexing
- featured image match → CTR naik, bounce turun
- recategorize → long-tail internal link naik

**Proyeksi 90 hari untuk .my:**
- Indexed: 200 → 5.000 (25x)
- Impressions/hari: 30 → 500 (16x)
- Revenue AdSense: <Rp100rb → Rp2-5jt/bulan

(Traffic .my memang akan lebih kecil dari .com karena market lebih kecil, tapi CTR bisa lebih tinggi karena less competition.)

---

## NEXT ACTION (menunggu user)

1. ✅ Konfirmasi FASE 1 + 2 boleh implement sekarang (infrastruktur + image logic + kategori structure)
2. ❓ Untuk FASE 3 (recategorize existing articles), user pelajari existing 98 published + sample 1.873 drafts → kasih panduan keyword mana ke platform-specific mana
3. ❓ Setup cron-job.org endpoints untuk news-ping + distribute (pakai token `beriklan-my-admin-2026`)
4. ❓ Confirm view-live platform priority untuk .my (TikTok dulu? atau Shopee Live dulu?)
5. ❓ AdSense setup untuk .my (publisher ID + slot ID beda dari .com)
