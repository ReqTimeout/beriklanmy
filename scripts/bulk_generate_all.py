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
# Multi-model rotation. Each model has independent rate limit on free tier.
MODELS = ["nemotron-3-ultra-free", "ling-3.0-flash-free", "north-mini-code-free", "deepseek-v4-flash-free", "mimo-v2.5-free", "laguna-s-2.1-free"]
MAX_WORKERS = 5
ERR_LOG = "/tmp/bulk_generate_err.log"

# Per-model lockout timestamps (epoch seconds). If a model hits rate limit,
# it's locked out for LOCKOUT_S seconds.
model_lockout = {m: 0 for m in MODELS}
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
    try:
        return open(ZEN_KEY_PATH).read().strip()
    except:
        print("ERROR: Zen API key not found at", ZEN_KEY_PATH)
        sys.exit(1)

def get_model(attempt=0):
    """Return a model that's not currently locked out. Rotate through MODELS."""
    now = time.time()
    with model_lock:
        for m in MODELS:
            if model_lockout[m] < now:
                return m
    # All models locked out — pick the soonest-to-unlock one
    with model_lock:
        return min(MODELS, key=lambda m: model_lockout[m])

def lock_model(model, seconds=LOCKOUT_S):
    with model_lock:
        model_lockout[model] = time.time() + seconds

def load_live_slugs():
    try:
        posts = json.load(open(LIVE_POSTS))
        return set(x.get("slug") for x in posts)
    except:
        return set()

# Anti-doorway: deterministic per-keyword structure variants so the ~298k articles
# do NOT share one identical heading template (scaled-content-abuse footprint).
PROMPT_VARIANTS = [
    ("600-750", [
        ("Introduction", "define {kw} in 1-2 short paragraphs with local {loc}/Malaysia context."),
        ("Key Benefits", "3-4 points in a <ul>."),
        ("How It Works", "3-4 steps in an <ol>."),
        ("Pricing in Malaysia", "realistic ranges in RM (e.g. \"from RM990/month\"); explain what affects cost."),
        ("Common Mistakes to Avoid", "2-3 pitfalls in a <ul>."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Conclusion", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("550-700", [
        ("What Is {kw}?", "explain the concept in 1-2 paragraphs for a Malaysian business owner."),
        ("Why It Matters for Malaysian Businesses", "2-3 paragraphs on real business impact."),
        ("Step-by-Step Process", "3-4 steps in an <ol>."),
        ("Cost & Budget Guide (RM)", "realistic RM ranges; explain what drives the budget."),
        ("Questions Business Owners Ask", "3 <h3> questions, each answered in a <p>."),
        ("Getting Started", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("650-800", [
        ("Overview", "introduce {kw} with {loc}/Malaysia context in 1-2 paragraphs."),
        ("Who Should Consider This", "describe the ideal business or situation in a <ul>."),
        ("Key Advantages", "3-4 points in a <ul>."),
        ("How the Process Works", "3-4 steps in an <ol>."),
        ("Pricing Explained (RM)", "realistic RM ranges and the main cost factors."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Final Thoughts", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("600-750", [
        ("{kw}: A Practical Guide", "1-2 paragraph introduction with {loc}/Malaysia context."),
        ("Benefits You Can Expect", "3-4 points in a <ul>."),
        ("How We Approach It", "3-4 steps in an <ol>."),
        ("Investment & Pricing (RM)", "realistic RM ranges; explain what affects cost."),
        ("Local Considerations in {loc}", "1-2 paragraphs on the local market."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Next Steps", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("550-700", [
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

def call_zen(prompt, zen_key, timeout=90):
    """Try models in rotation; lock out rate-limited ones."""
    last_err = None
    for attempt in range(4):
        model = get_model(attempt)
        try:
            r = requests.post(ZEN_URL,
                headers={"Authorization": f"Bearer {zen_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 1500, "temperature": 0.6, "thinking": {"type": "disabled"}},
                timeout=timeout)
            if r.status_code == 200:
                try:
                    data = r.json()
                except:
                    last_err = "json parse fail"
                    continue
                if data.get("error"):
                    err_type = data["error"].get("type", "")
                    if "FreeUsageLimit" in err_type or "rate_limit" in err_type or "insufficient" in str(data["error"]).lower():
                        lock_model(model, LOCKOUT_S)
                        last_err = f"{model}: {err_type}"
                        continue
                    last_err = f"{model}: {data['error'].get('message','')[:100]}"
                    continue
                text = (data.get("choices", [{}])[0].get("message", {}).get("content", "") or "").strip()
                if len(text) > 300:
                    return text
                # Sometimes content is in reasoning_content
                text2 = (data.get("choices", [{}])[0].get("message", {}).get("reasoning_content", "") or "").strip()
                if len(text2) > 300:
                    return text2
                last_err = f"{model}: too short ({len(text)})"
                continue
            elif r.status_code == 429:
                lock_model(model, LOCKOUT_S)
                last_err = f"{model}: 429"
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
    # QC: retry once if too short (<450 words) for better quality
    if len(content.split()) < 450:
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
    args = parser.parse_args()
    
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