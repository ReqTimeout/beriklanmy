#!/usr/bin/env python3
"""
pack_llm_drafts.py — Pack LLM-generated drafts into R2 publish-queue NDJSON shards.
LLM-ONLY: reads drafts/batch_*.json (from bulk_generate_all.py), writes NDJSON shards
to drafts_patched/queue_NNNNN.ndjson. NO deterministic re-render.
Each line matches refillBufferCore: { slug, title, content, service, city, source }
Skips slugs already live and de-dupes. Worker stamps MYT date at publish time.
Usage: python3 scripts/pack_llm_drafts.py [--shard-size 5000] [--out drafts_patched]
"""
import os, sys, json, glob, argparse, re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "src" / "data"
DRAFTS = ROOT / "drafts"

def load_live_slugs():
    try:
        posts = json.load(open(DATA / "posts.json", encoding="utf-8"))
        return {p.get("slug") for p in posts if p.get("slug")}
    except Exception:
        return set()

def qc(rec):
    c = rec.get("content") or ""
    if len(c) < 1000:
        return False, "too_short"
    low = c.lower()
    if "<h1" in low or "<!doctype" in low or "<script" in low:
        return False, "bad_html"
    if re.search(r"\bdi\s{2,}|\bdi\s*(</|[.,])", c):
        return False, "empty_city"
    if not rec.get("slug") or not rec.get("title"):
        return False, "missing_field"
    return True, "ok"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard-size", type=int, default=5000)
    ap.add_argument("--out", default="drafts_patched")
    args = ap.parse_args()
    OUT = ROOT / args.out
    OUT.mkdir(exist_ok=True)
    live = load_live_slugs()
    seen = set(live)
    print(f"Live slugs (skip): {len(live)}", flush=True)
    written = 0
    qc_fail = Counter()
    shard_idx = 0
    shard = []
    shard_files = []
    def flush_shard():
        nonlocal shard_idx, shard
        if not shard:
            return
        fn = OUT / f"queue_{shard_idx:05d}.ndjson"
        with open(fn, "w", encoding="utf-8") as fh:
            for rec in shard:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        shard_files.append(fn.name)
        print(f"  wrote {fn.name} ({len(shard)} recs)", flush=True)
        shard_idx += 1
        shard = []
    files = sorted(glob.glob(str(DRAFTS / "batch_*.json")))
    print(f"Draft batch files: {len(files)}", flush=True)
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"  skip {f}: {e}", flush=True)
            continue
        arts = d.get("articles", d) if isinstance(d, dict) else d
        for a in arts:
            sg = a.get("slug")
            if not sg or sg in seen:
                qc_fail["dup_or_live"] += 1
                continue
            rec = {
                "slug": sg,
                "title": a.get("title") or sg.replace("-", " ").title(),
                "content": a.get("content") or "",
                "service": a.get("service") or "digital-marketing-agency",
                "city": a.get("city") or "",
                "source": "bulk_generate_llm",
            }
            ok, reason = qc(rec)
            if not ok:
                qc_fail[reason] += 1
                continue
            seen.add(sg)
            shard.append(rec)
            written += 1
            if len(shard) >= args.shard_size:
                flush_shard()
    flush_shard()
    manifest = {
        "generated_by": "pack_llm_drafts.py",
        "live_existing": len(live),
        "written": written,
        "qc_failed": sum(qc_fail.values()),
        "qc_fail_reasons": dict(qc_fail),
        "shards": shard_files,
        "shard_size": args.shard_size,
    }
    json.dump(manifest, open(OUT / "manifest.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)

if __name__ == "__main__":
    main()
