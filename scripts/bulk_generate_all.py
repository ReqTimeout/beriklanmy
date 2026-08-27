#!/usr/bin/env python3
"""
bulk_generate_all.py — Massive local article generator in DRAFT mode.

Reads keyword-queue.json (27K keywords), generates articles via ZEN API,
saves to drafts/ locally. Skips existing live post slugs.

Usage:
  python3 scripts/bulk_generate_all.py --batch 20 --workers 5
  python3 scripts/bulk_generate_all.py --resume
  python3 scripts/bulk_generate_all.py --limit 100
"""
import argparse, hashlib, json, os, re, sys, time, requests, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(WEB, "web", "src", "data", "keyword-queue.json")
LIVE_POSTS = os.path.join(WEB, "web", "src", "data", "posts.json")
DRAFTS_DIR = os.path.join(WEB, "drafts")
PROGRESS_FILE = os.path.join(DRAFTS_DIR, "_progress.json")
ZEN_KEY_PATH = os.path.expanduser("~/.beriklan/zen-key")

ZEN_URL = "https://opencode.ai/zen/v1/chat/completions"
# TokenRouter free models. qwen3.8-max-free is a reasoning model — returns
# content in `content` (with `reasoning_content` separate), needs large max_tokens
# because reasoning consumes tokens before the answer. deepseek-v4-pro-0813-free
# returned garbage (Chinese boilerplate) in testing, so it's excluded.
TOKENROUTER_URL = "https://api.tokenrouter.com/v1/chat/completions"
TOKENROUTER_KEY = "sk-ggb0nO6f0cMdIBkcWhsxwvry5F4Fc1oAmhV9gkL0yt0wMBWI"

# Multi-endpoint pool: each free source has its OWN rate limit, so round-robining
# across all of them lets us run many parallel workers without any single key
# getting 429'd. ZEN has several models; TokenRouter adds qwen3.8-max-free.
ZEN_MODELS = [
    "ling-3.0-flash-free", "mimo-v2.5-free", "deepseek-v4-flash-free",
    "laguna-s-2.1-free",
]
# Flat pool of (model, endpoint_name); endpoint_name indexes ENDPOINTS below.
MODEL_POOL = []
for _m in ZEN_MODELS:
    MODEL_POOL.append((_m, "zen"))
for _m in ["qwen/qwen3.8-max-free", "qwen/qwen3.8-max-free"]:
    MODEL_POOL.append((_m, "tokenrouter"))

ENDPOINTS = {
    "zen":         {"url": ZEN_URL, "key": None},  # filled at runtime (read_zen_key)
    "tokenrouter": {"url": TOKENROUTER_URL, "key": TOKENROUTER_KEY},
}
# Per-endpoint min interval (seconds). TokenRouter free ≈3 req/min; ZEN freer.
ENDPOINT_MIN_INTERVAL = {"zen": 2, "tokenrouter": 20}
_endpoint_last = {k: 0.0 for k in ENDPOINTS}
_endpoint_pace_lock = threading.Lock()
MAX_WORKERS = 10
ERR_LOG = "/tmp/bulk_generate_err.log"

# Per-model lockout timestamps (epoch seconds). If a model hits rate limit,
# it's locked out for LOCKOUT_S seconds.
model_lockout = [0] * len(MODEL_POOL)
model_lock = threading.Lock()
LOCKOUT_S = 15  # seconds to wait before retrying a rate-limited model

SERVICE_NAMES = {
    "facebook-ads-management": "Facebook Ads Management",
    "instagram-ads-management": "Instagram Ads Management",
    "tiktok-ads-management": "TikTok Ads Management",
    "google-ads-management": "Google Ads Management",
    "youtube-ads-management": "YouTube Ads Management",
    "instagram-management": "Instagram Management",
    "tiktok-management": "TikTok Management",
    "website-development": "Website Development",
    "landing-page-design": "Landing Page Design",
    "digital-marketing-agency": "Digital Marketing Agency",
    "live-stream-viewers": "Live Stream Viewers",
    "tiktok-live-viewers": "TikTok Live Viewers",
    "shopee-live-viewers": "Shopee Live Viewers",
    "youtube-live-viewers": "YouTube Live Viewers",
    "twitch-live-viewers": "Twitch Live Viewers",
    "instagram-live-viewers": "Instagram Live Viewers",
}

SERVICE_PATHS = {
    "facebook-ads-management": "facebook-ads-management",
    "instagram-ads-management": "instagram-ads-management",
    "tiktok-ads-management": "tiktok-ads-management",
    "google-ads-management": "google-ads-management",
    "youtube-ads-management": "youtube-ads-management",
    "instagram-management": "instagram-management",
    "tiktok-management": "tiktok-management",
    "website-development": "website-development",
    "landing-page-design": "landing-page-design",
    "digital-marketing-agency": "digital-marketing-agency",
    "live-stream-viewers": "live-stream-viewers",
    "tiktok-live-viewers": "tiktok-live-viewers",
    "shopee-live-viewers": "shopee-live-viewers",
    "youtube-live-viewers": "youtube-live-viewers",
    "twitch-live-viewers": "twitch-live-viewers",
    "instagram-live-viewers": "instagram-live-viewers",
}

def read_zen_key():
    # env override wins (ZEN_API_KEY), then ~/.beriklan/zen-key
    env_key = os.environ.get("ZEN_API_KEY")
    if env_key:
        return env_key.strip()
    try:
        return open(ZEN_KEY_PATH).read().strip()
    except:
        return None  # TokenRouter-only mode is fine if ZEN key absent

# Round-robin cursor so concurrent threads spread evenly across all models
# instead of all piling onto the first available one (that caused 503 storms).
_rr_cursor = 0

def get_model(attempt=0):
    """Return (model, endpoint_name) that's not currently locked out. Round-robin across MODEL_POOL."""
    global _rr_cursor
    now = time.time()
    with model_lock:
        for _ in range(len(MODEL_POOL)):
            i = _rr_cursor % len(MODEL_POOL)
            _rr_cursor += 1
            if model_lockout[i] < now:
                return MODEL_POOL[i]
    # All models locked out — pick the soonest-to-unlock one
    with model_lock:
        i = min(range(len(MODEL_POOL)), key=lambda j: model_lockout[j])
        return MODEL_POOL[i]

def lock_model(idx, seconds=LOCKOUT_S):
    with model_lock:
        model_lockout[idx] = time.time() + seconds

def load_live_slugs():
    try:
        posts = json.load(open(LIVE_POSTS))
        return set(x.get("slug") for x in posts)
    except:
        return set()

# Anti-doorway: deterministic per-keyword structure variants so the ~298k articles
# do NOT share one identical heading template (scaled-content-abuse footprint).
PROMPT_VARIANTS = [
    ("350-450", [
        ("Introduction", "define {kw} in 1-2 short paragraphs with local {loc}/Malaysia context."),
        ("Key Benefits", "3-4 points in a <ul>."),
        ("How It Works", "3-4 steps in an <ol>."),
        ("Pricing in Malaysia", "realistic ranges in RM (e.g. \"from RM990/month\"); explain what affects cost."),
        ("Common Mistakes to Avoid", "2-3 pitfalls in a <ul>."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Conclusion", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("350-450", [
        ("What Is {kw}?", "explain the concept in 1-2 paragraphs for a Malaysian business owner."),
        ("Why It Matters for Malaysian Businesses", "2-3 paragraphs on real business impact."),
        ("Step-by-Step Process", "3-4 steps in an <ol>."),
        ("Cost & Budget Guide (RM)", "realistic RM ranges; explain what drives the budget."),
        ("Questions Business Owners Ask", "3 <h3> questions, each answered in a <p>."),
        ("Getting Started", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("350-450", [
        ("Overview", "introduce {kw} with {loc}/Malaysia context in 1-2 paragraphs."),
        ("Who Should Consider This", "describe the ideal business or situation in a <ul>."),
        ("Key Advantages", "3-4 points in a <ul>."),
        ("How the Process Works", "3-4 steps in an <ol>."),
        ("Pricing Explained (RM)", "realistic RM ranges and the main cost factors."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Final Thoughts", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("350-450", [
        ("{kw}: A Practical Guide", "1-2 paragraph introduction with {loc}/Malaysia context."),
        ("Benefits You Can Expect", "3-4 points in a <ul>."),
        ("How We Approach It", "3-4 steps in an <ol>."),
        ("Investment & Pricing (RM)", "realistic RM ranges; explain what affects cost."),
        ("Local Considerations in {loc}", "1-2 paragraphs on the local market."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Next Steps", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("350-450", [
        ("Understanding {kw}", "define it in 1-2 paragraphs with Malaysia context."),
        ("When to Use It", "2-3 scenarios in a <ul>."),
        ("Process & Timeline", "3-4 steps in an <ol>."),
        ("Budget Ranges in RM", "realistic RM figures and what affects them."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Conclusion", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
]

ANGLES = [
    "Emphasise measurable ROI and lead quality.",
    "Write for a beginner who is new to paid advertising.",
    "Focus on the local Malaysian market and buyer behaviour.",
    "Take a practical, no-hype, budget-conscious angle.",
    "Highlight realistic expectations and common outcomes.",
]

def build_prompt(kw, svc_name, city, svc_key):
    loc = city.title() if city else "Malaysia"
    svc_path = SERVICE_PATHS.get(svc_key, svc_key)
    ilink = f"https://beriklan.my/{svc_path}/"

    platform = svc_name.lower()
    if "google" in platform: elink = "https://ads.google.com/intl/en_my/home/"
    elif "facebook" in platform or "instagram" in platform: elink = "https://www.facebook.com/business/ads"
    elif "tiktok" in platform: elink = "https://ads.tiktok.com/"
    elif "youtube" in platform: elink = "https://www.youtube.com/ads/"
    else: elink = "https://business.google.com/my/"

    hv = int(hashlib.md5(f"{kw}|{svc_key}".encode("utf-8")).hexdigest(), 16)
    word_range, sections = PROMPT_VARIANTS[hv % len(PROMPT_VARIANTS)]
    angle = ANGLES[(hv // 7) % len(ANGLES)]
    heading_block = "\n".join(
        f"<h2>{t.format(kw=kw, loc=loc)}</h2> {g.format(kw=kw, loc=loc)}"
        for t, g in sections
    )

    return f"""Write a well-structured, factual HTML article ({word_range} words) in professional Malaysian English about: {kw}
Service: {svc_name}. Location: {loc}.
Editorial angle: {angle}

Use these exact <h2> headings in order:
{heading_block}

Requirements:
- STRICTLY keep the entire article between 350 and 450 words. Do NOT exceed 450 words — be concise.
- Link twice to {ilink} with natural anchor text.
- Link once to <a href="{elink}" rel="nofollow"> as an external reference.
- Voice: the Beriklan team, an agency running ad campaigns since 2016.
- Natural professional Malaysian English. Currency in RM only (never Rp).
- Vary sentence structure and openings; do not reuse boilerplate phrasing across sections.
- Avoid hype words: guaranteed, best, 100%, cheapest.
- Output ONLY HTML starting from the first <h2>. No preamble, no markdown code fences."""

ERR_LOG = "/tmp/bulk_generate_err.log"

def log_err(keyword, slug, reason):
    line = f"[{datetime.now().isoformat()}] {slug}: {reason}"
    with open(ERR_LOG, "a") as f:
        f.write(line + "\n")
    print(f"  ⚠ ERROR: {slug} — {reason}", file=sys.stderr)

def call_zen(prompt, zen_key=None, timeout=180):
    """Try models in rotation across ALL endpoints; lock out rate-limited ones."""
    last_err = None
    for attempt in range(6):
        model, ep_name = get_model(attempt)
        ep = ENDPOINTS[ep_name]
        key = ep["key"] if ep_name == "tokenrouter" else zen_key
        if not key:
            # no key for this endpoint — skip it
            lock_model(MODEL_POOL.index((model, ep_name)), 60)
            continue
        # Pace per-endpoint to respect each free-tier's own rate limit
        with _endpoint_pace_lock:
            global _endpoint_last
            wait = ENDPOINT_MIN_INTERVAL[ep_name] - (time.time() - _endpoint_last[ep_name])
            if wait > 0:
                time.sleep(wait)
            _endpoint_last[ep_name] = time.time()
        idx = MODEL_POOL.index((model, ep_name))
        extra = {}
        if ep_name == "tokenrouter":
            extra = {"enable_thinking": False, "reasoning_effort": "low"}
        try:
            r = requests.post(ep["url"],
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 900, "temperature": 0.4, **extra},
                timeout=timeout)
            if r.status_code == 200:
                try:
                    data = r.json()
                except:
                    last_err = "json parse fail"
                    continue
                if data.get("error"):
                    err_type = str(data.get("error", ""))
                    if "FreeUsageLimit" in err_type or "rate_limit" in err_type or "insufficient" in err_type.lower() or "quota" in err_type.lower():
                        lock_model(idx, LOCKOUT_S)
                        last_err = f"{model}: {err_type[:80]}"
                        continue
                    last_err = f"{model}: {err_type[:100]}"
                    continue
                msg = data.get("choices", [{}])[0].get("message", {})
                # reasoning model: answer is in `content` (not reasoning_content)
                text = (msg.get("content") or "").strip()
                if len(text) > 300:
                    return text
                # fallback: some providers put the answer in reasoning_content
                text2 = (msg.get("reasoning_content") or "").strip()
                if len(text2) > 300:
                    return text2
                # Empty/too-short reply often means the model is degraded — cool it off
                lock_model(idx, LOCKOUT_S)
                last_err = f"{model}: too short ({len(text)})"
                continue
            elif r.status_code == 429:
                ra = r.headers.get("Retry-After")
                try:
                    wait = int(float(ra))
                except (TypeError, ValueError):
                    wait = 30
                wait = min(wait, 45)
                lock_model(idx, wait)
                time.sleep(wait)
                last_err = f"{model}: 429 (backoff {wait}s)"
                continue
            elif r.status_code in (502, 503):
                lock_model(idx, 8)
                last_err = f"{model}: HTTP {r.status_code}"
                time.sleep(1)
                continue
            else:
                last_err = f"{model}: HTTP {r.status_code}"
                time.sleep(1)
        except Exception as e:
            last_err = f"{model}: {str(e)[:100]}"
            time.sleep(1)
    return None

def clean_html(html):
    h = html.strip()
    for pfx in ["```html", "```"]:
        if h.startswith(pfx): h = h[len(pfx):]
    if h.endswith("```"): h = h[:-3]
    return h.strip()

WA_LINK = "https://wa.me/62811919328"

def cta_block(svc_name, svc_key):
    svc_path = SERVICE_PATHS.get(svc_key, svc_key)
    return (
        "\n<hr/>\n<h2>Work With Beriklan</h2>\n"
        "<p>Beriklan has managed paid ad campaigns since 2016 — transparent, measurable, "
        "with weekly reporting and full access to your ad accounts. "
        f"Explore our <a href=\"https://beriklan.my/{svc_path}/\">{svc_name} packages</a> "
        "or start a consultation.</p>\n"
        f"<p><a href=\"{WA_LINK}?text=Hi%20Beriklan%2C%20I%20would%20like%20a%20consultation.\" "
        "rel=\"nofollow\">Chat with our team on WhatsApp</a> — reply within 1 hour (business hours).</p>"
    )

def make_article(item, zen_key, live_slugs):
    kw = item["keyword"]
    slug = item.get("slug") or re.sub(r"[^a-z0-9-]", "", kw.lower().replace(" ", "-"))[:80]
    
    if slug in live_slugs:
        return None  # skip duplicate
    
    svc = item.get("service") or "digital-marketing-agency"
    city = item.get("city") or ""
    svc_name = SERVICE_NAMES.get(svc, svc)
    
    title = " ".join(w.capitalize() for w in kw.split())
    prompt = build_prompt(kw, svc_name, city, svc)
    raw = call_zen(prompt, zen_key)
    if not raw:
        return None

    content = clean_html(raw)
    # QC: retry once if too short (<200 words) for better quality
    if len(content.split()) < 200:
        raw2 = call_zen(prompt, zen_key)
        if raw2 and len(clean_html(raw2).split()) > len(content.split()):
            content = clean_html(raw2)
    if not content.startswith("<h2>"):
        content = f"<h2>{title}</h2>\n" + content

    # Guarantee internal link to service page + WhatsApp CTA
    if content.count(f"/{SERVICE_PATHS.get(svc, svc)}/") < 1 or "wa.me" not in content:
        content += cta_block(svc_name, svc)
    
    excerpt = re.sub(r'<[^>]+>', ' ', content).strip()
    excerpt = re.sub(r'\s+', ' ', excerpt)[:180] + "..."
    words = len(content.split())
    now = datetime.now()
    
    return {
        "slug": slug, "title": title, "excerpt": excerpt, "content": content,
        "date": now.strftime("%d %b %Y"), "iso_date": now.isoformat(),
        "category": "strategy",
        "readTime": f"{max(2, round(words/200))} min",
        "tags": [w for w in kw.lower().split() if len(w) > 3][:5],
        "featured": False, "generated": True, "service": svc,
        "city": city or None, "liveUrl": None,
        "publish_date": now.strftime("%d %b %Y"), "source": "bulk_generate",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=20)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    parser.add_argument("--services", type=str, default="",
                        help="Comma-separated service slugs to generate ONLY (e.g. tiktok-live-viewers,shopee-live-viewers)")
    args = parser.parse_args()
    only_services = {s.strip() for s in args.services.split(",") if s.strip()} if args.services else None
    
    zen_key = read_zen_key()
    live_slugs = load_live_slugs()
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    
    processed = set()
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            processed = set(json.load(f).get("processed_slugs", []))
        print(f"Progress file found: {len(processed)} already processed")
        if not args.resume:
            print("  (use --resume to continue; running fresh will overwrite)")
    
    queue = json.load(open(QUEUE))
    pending = [x for x in queue if x.get("status") == "pending" and not x.get("has_post")]
    if only_services:
        before = len(pending)
        pending = [x for x in pending if x.get("service") in only_services]
        print(f"Service filter {sorted(only_services)}: {before} → {len(pending)} pending")
    print(f"Queue: {len(queue)} total, {len(pending)} pending, {len(live_slugs)} live slugs")
    
    pending = [x for x in pending if x.get("slug") not in processed and x.get("slug") not in live_slugs]
    # Priority order: best keywords first (highest priority_score)
    pending.sort(key=lambda x: int(x.get("priority_score") or 0), reverse=True)
    if args.limit > 0:
        pending = pending[:args.limit]
    
    print(f"To generate: {len(pending)} articles")
    if not pending:
        print("Nothing to generate. Done.")
        return
    
    total_gen = 0
    batch_num = 0
    t_start = time.time()
    consecutive_errors = 0
    
    for start in range(0, len(pending), args.batch):
        batch = pending[start:start+args.batch]
        batch_num += 1
        results = []
        err_count = 0
        
        print(f"\nBatch {batch_num}/{len(pending)//args.batch+1}: {len(batch)} articles...")
        t0 = time.time()
        
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            fut_map = {ex.submit(make_article, item, zen_key, live_slugs): item for item in batch}
            for fut in as_completed(fut_map):
                item = fut_map[fut]
                slug = item.get("slug", "?")
                kw = item.get("keyword", slug)
                try:
                    post = fut.result()
                    if post:
                        results.append(post)
                        processed.add(slug)
                        item["status"] = "generated"
                        item["has_post"] = True
                        item["generated_at"] = datetime.now().isoformat()
                    else:
                        if slug in live_slugs:
                            # duplicate — mark as processed silently
                            processed.add(slug)
                            item["status"] = "generated"
                            item["has_post"] = True
                        else:
                            err_count += 1
                            log_err(kw, slug, "API gagal atau konten terlalu pendek (None)")
                except Exception as e:
                    err_count += 1
                    log_err(kw, slug, f"exception: {str(e)[:200]}")
        
        elapsed = time.time() - t0
        total_gen += len(results)
        err_rate = err_count / len(batch) if batch else 0
        
        # Save batch file
        if results:
            batch_file = os.path.join(DRAFTS_DIR, f"batch_{batch_num:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(batch_file, "w") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        
        rate = total_gen / max(time.time() - t_start, 1) * 3600
        eta_h = max(0, (len(pending) - start - len(batch))) / max(rate, 1) * 3600
        print(f"  → {len(results)} ok, {err_count} fail ({elapsed:.0f}s, {rate:.0f}/hr, ETA ~{eta_h/3600:.1f}h)")
        
        # Save progress every batch
        with open(PROGRESS_FILE, "w") as f:
            json.dump({"processed_slugs": list(processed), "last_run": datetime.now().isoformat()}, f)
        
        # Save queue every 10 batches (reduce disk I/O)
        if batch_num % 10 == 0:
            json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)
        
        # Backoff: if >50% errors, slow down
        if err_rate > 0.5:
            consecutive_errors += 1
            backoff = min(consecutive_errors * 10, 120)
            print(f"  ⏳ High error rate ({err_rate:.0%}), backing off {backoff}s...")
            time.sleep(backoff)
        else:
            consecutive_errors = 0
            if start + args.batch < len(pending):
                time.sleep(2)
    
    elapsed_total = time.time() - t_start
    print(f"\n{'='*50}")
    print(f"Complete: {total_gen} articles in {elapsed_total/3600:.1f}h")
    print(f"Speed: {total_gen/elapsed_total*3600:.0f}/hr")
    print(f"Drafts: {DRAFTS_DIR}/")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()