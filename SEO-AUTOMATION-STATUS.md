# Beriklan.my — Status SEO Automation & Keyword Report

> Dibuat: 17 Agustus 2026. Dokumentasi status terkini sistem beriklan.my.

---

## 1. STATUS SEO AUTOMATION (double-check live)

Dicek langsung ke worker `beriklanmy` (D1 `beriklan-my-seo`, R2 `myberiklan`) via
`https://beriklan.my/api/admin?token=beriklan-my-admin-2026&format=json`.

### Funnel saat ini

| Stage | Count |
|---|---|
| Keyword pending (D1 keyword_queue) | 35.863 |
| Keyword generated | 0 |
| Drafts (generated_drafts) | 1.873 |
| **Published (posts_meta)** | **98** |
| Submitted (GSC Indexing API) | 58 |
| **Indexed (GSC verdict PASS)** | **0** |
| Pending index queue | 40 |
| Index rate | 0% (0/58) |

> **indexed=0 = crawl delay Google untuk domain baru**, bukan error. Artikel
> tetap `index,follow`. Baru 58 URL disubmit dari 98 published.

### Cron yang berjalan (via cron-job.org → `/api/cron/tick` tiap jam)

| Cron | Status | Catatan |
|---|---|---|
| `hourly` (generate) | ⚠️ failed | "no articles generated (check ZEN_API_KEY)" — **normal**: generate dilakukan LOKAL (Mac), bukan di worker. Bukan error yang harus diperbaiki. |
| `sync-posts` (drip publish) | ✅ ok | Publish dari buffer ke posts_meta + commit GitHub |
| `indexnow` (Bing/Yandex) | ✅ ok | Submit batch URL baru |
| `gsc-indexing` | ✅ terjadwal | Tiap 6 jam (h%6==0), kuota 200/hari |
| `index-verify` (URL Inspection) | ✅ terjadwal | Tiap 6 jam, verdict PASS |
| `sitemap-ping` | ✅ terjadwal | Submit sitemap ke GSC tiap 6 jam |
| `rank-sync` | ✅ terjadwal | Tarik data GSC ranking |

### Endpoint publik (semua 200)

- `sitemap-blog.xml` → 200 (dinamis dari D1)
- `llms.txt` → 200
- `rss.xml` → 200
- IndexNow key file → 200

### Catatan penting
1. **`hourly` "failed" adalah false alarm** — arsitektur .my generate artikel di
   Mac lokal (ZEN free API via `scripts/bulk_generate_all.py`), bukan di worker.
   Worker `hourly` menunggu ZEN_API_KEY/GROQ_API_KEY yang memang tidak di-set
   (generate lokal). Yang penting `sync-posts` (publish) jalan normal.
2. **indexed=0 normal** untuk domain baru — Google butuh waktu crawl. Jalur
   percepatan sudah aktif: IndexNow on-publish + GSC tiap 6 jam + sitemap dinamis
   + internal linking pillar↔cluster + RSS feed.
3. **View-live (blue ocean) hampir 0 generated** — lihat §2.

---

## 2. KEYWORD REPORT — VIEW-LIVE ADALAH BLUE OCEAN (PRIORITAS PUSH RANK)

File Excel: **`beriklan.my_keyword_report.xlsx`** (16 sheet layanan + Ringkasan).

### Ringkasan per layanan (view-live di atas)

| Layanan | Total KW | Generated | Pending | % |
|---|---|---|---|---|
| Live Stream Viewers (overview) | 1.367 | 2 | 1.365 | 0,1% |
| TikTok Live Viewers | 1.446 | 0 | 1.446 | 0% |
| Shopee Live Viewers | 1.423 | 0 | 1.423 | 0% |
| YouTube Live Viewers | 1.361 | 0 | 1.361 | 0% |
| Twitch Live Viewers | 1.367 | 0 | 1.367 | 0% |
| Instagram Live Viewers | 1.347 | 0 | 1.347 | 0% |
| **Sub-total view-live** | **8.311** | **2** | **8.309** | **0,02%** |
| Facebook Ads Management | 32.610 | 1.499 | 31.111 | 4,6% |
| Instagram Ads Management | 28.576 | 92 | 28.484 | 0,3% |
| TikTok Ads Management | 30.498 | 90 | 30.408 | 0,3% |
| Google Ads Management | 30.482 | 96 | 30.386 | 0,3% |
| YouTube Ads Management | 28.575 | 88 | 28.487 | 0,3% |
| Digital Marketing Agency | 28.682 | 156 | 28.526 | 0,5% |
| Instagram Management | 28.639 | 109 | 28.530 | 0,4% |
| TikTok Management | 26.764 | 168 | 26.596 | 0,6% |
| Website Development | 26.899 | 137 | 26.762 | 0,5% |
| Landing Page Design | 28.700 | 115 | 28.585 | 0,4% |
| **TOTAL** | **298.736** | **2.552** | **296.184** | **0,9%** |

### Mengapa view-live = blue ocean
1. **Kompetisi rendah** — layanan live viewers adalah niche baru; kompetitor MY
   mayoritas panel murahan (bot), bukan "real viewers + WhatsApp support".
2. **Hampir 0 artikel live** — dari 8.311 keyword view-live hanya 2 ter-generate.
   Ini wilayah kosong yang bisa didominasi cepat.
3. **Intent commercial/transactional tinggi** — keyword seperti `buy tiktok live
   views`, `shopee live viewers price`, `boost live stream malaysia` = pembeli siap.
4. **Positioning harga premium vs panel** — real account, gradual join, support.

### Rekomendasi push rank view-live (Fase 7)
1. **Prioritaskan generate view-live dulu** — ubah urutan prioritas di
   `bulk_generate_all.py` atau seed `priority_score` view-live ke 95.
2. **Publish drip khusus view-live** — target 6 halaman pilar view-live + 25 kota
   tier-1 dulu (KL, PJ, JB, Penang, KK).
3. **Internal link**: setiap artikel view-live → link ke pilar
   `/tiktok-live-viewers/`, `/shopee-live-viewers/`, dst.
4. **Schema**: pastikan FAQ + HowTo + Service schema di 6 pilar view-live.
5. **Featured image**: sudah port 5 gambar view-live (tiktok/shopee/instagram/
   youtube/twitch) ke `/images/blog/` — artikel view-live kini pakai gambar lokal
   sesuai platform (lihat commit `8efefff`).

---

## 3. FEATURED IMAGE LOKAL (baru deploy)

Commit `8efefff` — 13 gambar webp dari `imageartikel/` .co.id di-port ke
`web/public/images/blog/`:

| File | Layanan |
|---|---|
| jasadigitalmarketing1/2 | digital-marketing-agency |
| jasafacebokads | facebook-ads-management |
| jasagoogleads | google-ads-management |
| jasainstagramads | instagram-ads / instagram-management |
| jasatiktokads | tiktok-ads / tiktok-management |
| jasayoutubeads | youtube-ads-management |
| jasapembuatanwebsite | website-development / landing-page-design |
| jasaviewlivetiktok | tiktok-live-viewers / live-stream-viewers |
| jasaviewliveshopee | shopee-live-viewers |
| jasaviewliveinstagram | instagram-live-viewers |
| jasaviewliveyoutube | youtube-live-viewers |
| jasaviewlivetwitch | twitch-live-viewers |

- `featured_image.js` ditulis ulang → SERVICE_IMAGES lokal (English slug) +
  `inferServiceFromTitle` + `viewLiveImage` (platform-specific).
- `worker-entry.js` tambah `_featuredImageFor()` + `<figure>` di header artikel
  + og:image/twitter:image per service.
- Tidak ada URL unsplash/picsum tersisa di featured_image.js.

---

## 4. FILE TERKAIT

- `beriklan.my_keyword_report.xlsx` — report keyword (generated vs pending)
- `scripts/gen_keyword_excel.py` — generator Excel (bisa re-run)
- `OPERATIONS-MY.md` — runbook operasional (generate + publish + recovery)
- `GENERATOR-AGENT-GUIDE.md` — panduan agent generator
