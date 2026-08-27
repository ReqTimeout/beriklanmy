# Cron-job.org URLs — Beriklan.my (siap paste)

> Token admin: `beriklan-my-admin-2026`
> Endpoint base: `https://beriklan.my`

---

## Endpoint yang SUDAH jalan

```
POST https://beriklan.my/api/cron/tick?token=beriklan-my-admin-2026
```

Schedule: tiap jam (cron-job.org default).

---

## Endpoint BARU (perlu ditambah setelah deploy Phase 1+2)

| Cron | URL | Schedule yang disarankan |
|---|---|---|
| **News sitemap ping** | `https://beriklan.my/api/cron/news/ping?token=beriklan-my-admin-2026` | `0 */2 * * *` (tiap 2 jam) |
| **Multi-channel distribute** | `https://beriklan.my/api/cron/distribute?token=beriklan-my-admin-2026&limit=30` | `0 */3 * * *` (tiap 3 jam) |
| **Recategorize-check** | `https://beriklan.my/api/admin/posts/categories?token=beriklan-my-admin-2026&format=json` | `0 */6 * * *` (monitoring) |

### News sitemap ping detail
- Push freshest 100 URL ke IndexNow (Bing fan-out ke Yandex/DuckDuckGo/Naver).
- Quota: aman, IndexNow tidak ada rate limit (kecuali Bing returning 429).
- Aman dipanggil 12x/hari.

### Distribute detail
- Share 30 freshest ke IndexNow + (kalau env diset) Telegram / generic webhook.
- Mark `posts_meta.last_distributed_at` supaya tidak duplikat.

---

## Cara pakai di cron-job.org

1. Login https://cron-job.org (free account: 200 cron jobs/day)
2. Create cron → paste URL di atas → set schedule
3. Recommended: timezone = Asia/Kuala_Lumpur (MYT UTC+8)
4. Enable "Send POST request" kalau pakai POST endpoint (default GET juga OK untuk semua endpoint di atas)

---

## POST endpoint .my juga perlu di-update

`POST https://beriklan.my/api/cron/tick?token=beriklan-my-admin-2026` → kalau pakai POST lebih reliable, tambahkan `Content-Type: application/json`.

Untuk test manual:

```bash
# Test news-ping
curl -s "https://beriklan.my/api/cron/news/ping?token=beriklan-my-admin-2026" | python3 -m json.tool | head -15

# Test distribute (dry-run)
curl -s "https://beriklan.my/api/cron/distribute?token=beriklan-my-admin-2026&dry=1&limit=5" | python3 -m json.tool | head -20

# Test category monitor
curl -s "https://beriklan.my/api/admin/posts/categories?token=beriklan-my-admin-2026" | python3 -m json.tool | head -20
```

Setelah deploy Phase 1+2 endpoint baru, semua di atas return JSON.
