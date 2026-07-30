# Beriklan.my — Article Generator Runbook (for an autonomous agent)

> Purpose: let an OpenCode agent run the bulk article generator to produce SEO
> articles faster. This file is a complete, self-contained operating guide.
> Project root on the host machine: `/Users/maabook/Desktop/beriklan.my`

---

## 0. TL;DR (just run this)

```bash
cd /Users/maabook/Desktop/beriklan.my
# make sure the ZEN key exists (see section 3)
nohup python3 scripts/bulk_generate_all.py --limit 0 --batch 15 --workers 4 --resume \
  >> logs/gen_full.log 2>&1 &
# watch progress (updates every batch)
cat drafts/_progress.json | python3 -c "import sys,json;print(len(json.load(sys.stdin)['processed_slugs']),'processed')"
```

Generated articles land in `drafts/batch_*.json`. They are NOT live yet — a
separate step ships them to production (section 5).

---

## 1. What the generator does

`scripts/bulk_generate_all.py`:
1. Loads the keyword queue `web/src/data/keyword-queue.json` (~298,736 keywords).
2. Filters to `status == "pending"` and `has_post == false`, skips slugs already
   live (`web/src/data/posts.json`) and already in `drafts/_progress.json`.
3. Sorts by `priority_score` DESC — best keywords first.
4. For each keyword, calls the ZEN LLM API to write a 550-800 word HTML article
   (English, Malaysian context, prices in RM), guarantees an internal link to the
   matching service page + a WhatsApp CTA.
5. Writes results per batch to `drafts/batch_NNNN_<timestamp>.json` and updates
   `drafts/_progress.json` after every batch (resumable).

Output record shape (one per article): `slug, title, excerpt, content(HTML),
date, iso_date, category, readTime, tags[], service, city, source`.

---

## 2. CLI arguments

| Flag | Default | Meaning |
|------|---------|---------|
| `--limit N` | `0` | Max articles this run. `0` = the entire pending queue. |
| `--batch N` | `20` | Articles per batch (progress saved after each batch). Smaller = more frequent saves + steadier buffer. Use `15`. |
| `--workers N` | `5` | Parallel threads. `4` is a good balance vs free-model rate limits. |
| `--resume` | off | Continue from `_progress.json`. ALWAYS pass this so you never redo work or overwrite progress. |

Recommended run: `--limit 0 --batch 15 --workers 4 --resume`.

---

## 3. Prerequisites

- **Python 3** with `requests` (`pip3 install requests` if missing).
- **ZEN API key** at `~/.beriklan/zen-key` (a single-line file with the key).
  Verify: `test -f ~/.beriklan/zen-key && echo OK || echo MISSING`.
  If missing, get the key from the project owner and write it:
  `mkdir -p ~/.beriklan && printf '%s' 'THE_KEY' > ~/.beriklan/zen-key`.
- The repo folder present at `/Users/maabook/Desktop/beriklan.my` (needs
  `scripts/` and `web/src/data/keyword-queue.json`).

### ZEN API facts
- Endpoint: `https://opencode.ai/zen/v1/chat/completions`
- Models are rotated automatically (free tier, each has its own rate limit):
  `nemotron-3-ultra-free`, `ling-3.0-flash-free`, `north-mini-code-free`,
  `deepseek-v4-flash-free`, `mimo-v2.5-free`, `laguna-s-2.1-free`.
- A rate-limited model is locked out for 15s, then retried. If >50% of a batch
  fails, the script backs off automatically. This is normal; let it run.
- Test a model quickly:
  ```bash
  ZK=$(cat ~/.beriklan/zen-key)
  curl -s https://opencode.ai/zen/v1/chat/completions -H "Authorization: Bearer $ZK" \
    -H "Content-Type: application/json" \
    -d '{"model":"nemotron-3-ultra-free","messages":[{"role":"user","content":"say hi"}],"max_tokens":30,"thinking":{"type":"disabled"}}'
  ```

---

## 4. Monitoring

```bash
# how many processed so far
cat drafts/_progress.json | python3 -c "import sys,json;print(len(json.load(sys.stdin)['processed_slugs']))"

# newest batch files (should grow while running)
ls -lt drafts/batch_*.json | head -5

# is the process alive + actively calling the API?
pgrep -f bulk_generate_all.py
NP=$(pgrep -f bulk_generate_all.py | head -1); lsof -nP -p $NP 2>/dev/null | grep -c ESTABLISHED   # >0 means working

# recent errors (low count is fine)
tail -20 /tmp/bulk_generate_err.log
```

IMPORTANT: the log file looks "frozen" because Python buffers stdout to a file.
Judge progress by `drafts/_progress.json` and new `batch_*.json` files, NOT the log tail.

---

## 5. Getting drafts LIVE (publish pipeline)

Generation only fills `drafts/`. To publish:

```bash
bash scripts/publish_drafts_to_r2.sh
```
This: packs drafts into NDJSON shards (`scripts/pack_llm_drafts.py` ->
`drafts_patched/queue_*.ndjson`), uploads them to R2 bucket
`myberiklan/publish-queue/`, and resets the D1 `queue_cursor`. The Cloudflare
Worker then drips them live via the hourly `/api/cron/tick` (currently 40/day).

A background loop already does this every 3 hours: `scripts/autosync_loop.sh`.
If you only generate, the existing autosync will pick up your new drafts.

---

## 6. Running MULTIPLE agents in parallel (avoid duplicates!)

The script has NO built-in sharding: two agents on the same full queue will both
start from the highest priority and generate the SAME articles (wasteful).
To split work safely, give each machine a NON-OVERLAPPING shard of the queue.

On each machine, create its own shard as the queue file (example: 3 machines,
this is machine index 0 -> change `IDX` to 1, 2 on the others):

```bash
cd /Users/maabook/Desktop/beriklan.my
python3 - <<'PY'
import json
IDX, N = 0, 3          # <-- machine index (0..N-1) and total machines
q = json.load(open("web/src/data/keyword-queue.json"))
shard = [x for i,x in enumerate(q) if i % N == IDX]
json.dump(shard, open("web/src/data/keyword-queue.json","w"), ensure_ascii=False)
print("shard size:", len(shard))
PY
```
Modulo split keeps a mix of high/low priority in every shard. Each machine keeps
its own `drafts/_progress.json`, so they never collide. All machines' drafts get
packed & uploaded independently; publish dedupes by `slug`.

---

## 7. Honest note — does faster generation = rank #1 faster? NO.

The ranking bottleneck is NOT generation speed. Two hard caps downstream:
- **Publishing is capped at 40 articles/day** on purpose (Google "scaled content
  abuse" avoidance). Configurable in D1 `cron_settings.daily_publish_limit`.
- **Google indexes ~200 URLs/day max** (hard quota).

So a few thousand drafts already buffer many weeks of publishing. Spinning up
extra agents mainly builds a bigger backlog; it does not make Google rank pages
sooner. The real levers are: topical interlinking (done), E-E-A-T (done),
content uniqueness/anti-doorway (done), and off-site backlinks (manual).
Generate ahead if you want a safety buffer — just know the cap is intentional.

---

## 8. Safety rules for the agent

- NEVER touch or deploy anything on the Indonesian site `beriklan.co.id`. This is
  the Malaysian site `beriklan.my` only.
- ALWAYS pass `--resume`. Do not delete `drafts/` or `_progress.json`.
- Do not raise `daily_publish_limit` — publishing cadence is deliberate.
- Do not commit the ZEN key or any secret anywhere.
- If unsure, only generate (section 0). Publishing (section 5) already runs
  automatically via autosync.

---

## 9. Key paths reference

| Thing | Path |
|-------|------|
| Generator | `scripts/bulk_generate_all.py` |
| Keyword queue | `web/src/data/keyword-queue.json` |
| Live posts (dedupe) | `web/src/data/posts.json` |
| Drafts output | `drafts/batch_*.json` |
| Progress (resume) | `drafts/_progress.json` |
| Error log | `/tmp/bulk_generate_err.log` |
| ZEN key | `~/.beriklan/zen-key` |
| Publish to prod | `scripts/publish_drafts_to_r2.sh` |
| Autosync loop (3h) | `scripts/autosync_loop.sh` |
| Cloudflare: worker / D1 / R2 | `beriklanmy` / `beriklan-my-seo` / `myberiklan` |
| Admin dashboard | `https://beriklan.my/api/admin?token=beriklan-my-admin-2026` |
