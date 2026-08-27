# Beriklan.my — Roadmap per Phase

> **Single source of truth** untuk status & langkah berikutnya beriklan.my.
> Update: 17 Agustus 2026.
>
> Sumber detail: `OPERATIONS-MY.md` (runbook), `SEO-AUTOMATION-STATUS.md` (funnel
> & keyword), `GENERATOR-AGENT-GUIDE.md` (panduan generator).

---

## Status Ringkas per Phase

| Fase | Judul | Status | Catatan |
|---|---|---|---|
| 0 | Infrastruktur & duplikasi repo | ✅ Selesai | Worker/D1/R2 MY terisolasi |
| 1 | Translate situs + pricing MYR | ✅ Selesai | English + RM |
| 2 | Data layer Malaysia (25 kota) | ✅ Selesai | 400 city pages |
| 3 | Keyword mining MY (298.736) | ✅ Selesai | 16 layanan |
| 4 | Worker & automation | ✅ Selesai | IndexNow on-publish, RSS, llms.txt |
| 5 | Bulk generation lokal (AI) | 🔄 Berjalan | 3.296 generated (lokal), 2.552 di D1 |
| 6 | Launch sequence (drip publish) | 🔄 Berjalan | 98 published, drip 40/hari |
| **7** | **Post-launch SEO (push rank)** | ⏭️ **FOKUS SEKARANG** | view-live = blue ocean |

---

## FASE 7 — Post-Launch SEO (PRIORITAS SEKARANG)

### 7.1 Push rank VIEW-LIVE (blue ocean) — PALING PENTING
- [ ] Generate 8.311 keyword view-live (tiktok/shopee/instagram/youtube/twitch live viewers) — saat ini baru 2 generated
- [ ] Naikkan `priority_score` view-live → 95 di keyword-queue
- [ ] Publish drip khusus view-live (6 pilar + kota tier-1: KL, PJ, JB, Penang, KK)
- [ ] Internal link setiap artikel view-live → pilar view-live
- [ ] Schema FAQ + HowTo + Service di 6 pilar view-live
- [x] Featured image view-live per platform (commit 8efefff)

### 7.2 Percepat indexing (sudah aktif)
- [x] IndexNow on-publish (tiap artikel baru langsung submit Bing/Yandex)
- [x] GSC Indexing API tiap 6 jam (kuota 200/hari)
- [x] Index-verify (URL Inspection) tiap 6 jam
- [x] Sitemap dinamis + ping tiap 6 jam
- [x] RSS feed + llms.txt
- [x] Internal linking pillar↔cluster
- [ ] Pantau index rate (target > 30% sebelum naikkan drip)

### 7.3 Kualitas & trust
- [ ] Rotasi GitHub PAT (token lama bocor)
- [ ] Naikkan daily_publish_limit 40→100→200 setelah indexing sehat
- [ ] Backlink Malaysia (directory, listing, partner)
- [ ] Tracking ranking keyword prioritas via rank-sync
- [ ] QC sampel artikel (bahasa English, RM, internal link, CTA WA)

---

## FASE 5+6 — Rincian Berjalan

### Generator (lokal, Mac)
- Proses: `scripts/bulk_generate_all.py` (ZEN free, 6 model rotation)
- Progress: `drafts/_progress.json` → `processed_slugs` (3.296 saat terakhir cek)
- Resume: `nohup python3 -u scripts/bulk_generate_all.py --limit 0 --batch 15 --workers 4 --resume`

### Publish drip
- Upload: `scripts/publish_drafts_to_r2.sh` (pack → R2 `myberiklan/publish-queue/`)
- Autosync: `scripts/autosync_loop.sh` (tiap 3 jam)
- Publish: cron-job.org → `/api/cron/tick` tiap jam → sync-posts (drip 40/hari)

### Recovery kalau mati
```bash
# A. Generator mati
nohup python3 -u scripts/bulk_generate_all.py --limit 0 --batch 15 --workers 4 --resume > logs/gen_full.log 2>&1 &
# B. Autosync mati
nohup bash scripts/autosync_loop.sh > logs/autosync.log 2>&1 &
# C. Publish tidak naik
curl -s "https://beriklan.my/api/cron/tick?token=beriklan-my-admin-2026"
```

---

## FASE 8 — Scale (setelah index rate > 30%)

- [ ] Mining tambahan → 30K+ keyword MY
- [ ] Bulk generate gelombang kedua
- [ ] Drip naik ke 200/hari
- [ ] Ekspansi layanan baru (kalau ada demand)

---

## INFRA REFERENSI

| Resource | Nilai |
|---|---|
| Worker | `beriklanmy` |
| D1 | `beriklan-my-seo` (id 9339554e-c00a-4b8c-96cf-2ccbf69a6e20) |
| R2 | `myberiklan` |
| Repo | `ReqTimeout/beriklanmy` |
| Domain | https://beriklan.my |
| Admin token | `beriklan-my-admin-2026` |
| IndexNow key | `2f22c16be9437a90ad2285a4af043e10` |
| daily_publish_limit | 40 (naik bertahap) |
| Deploy | `git push` → CF auto-build (jangan wrangler CLI) |

> **JANGAN** sentuh produksi beriklan.co.id.
