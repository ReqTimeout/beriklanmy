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
# Zen free, non-reasoning chat models. Round-robin across these for best
# throughput. Avoid reasoning models (e.g. qwen3.8-max-free) — they consume
# tokens on internal reasoning before returning the answer, burning quota
# without producing more content. Per-model rate limits vary, so rotation
# spreads load. Add new free models here when discovered.
TOKENROUTER_URL = "https://api.tokenrouter.com/v1/chat/completions"
TOKENROUTER_KEY = "sk-ggb0nO6f0cMdIBkcWhsxwvry5F4Fc1oAmhV9gkL0yt0wMBWI"

# Pool order = priority. big-pickle first (fastest non-reasoning chat).
ZEN_MODELS = [
    "big-pickle", "mimo-v2.5-free", "hy3-free", "nemotron-3-ultra-free",
]
# Flat pool of (model, endpoint_name); endpoint_name indexes ENDPOINTS below.
MODEL_POOL = []
for _m in ZEN_MODELS:
    MODEL_POOL.append((_m, "zen"))

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
    ("600-800", [
        ("Introduction", "define {kw} in 1-2 short paragraphs with local {loc}/Malaysia context."),
        ("Key Benefits", "3-4 points in a <ul>."),
        ("How It Works", "3-4 steps in an <ol>."),
        ("Pricing in Malaysia", "realistic ranges in RM (e.g. \"from RM990/month\"); explain what affects cost."),
        ("Common Mistakes to Avoid", "2-3 pitfalls in a <ul>."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Conclusion", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("600-800", [
        ("What Is {kw}?", "explain the concept in 1-2 paragraphs for a Malaysian business owner."),
        ("Why It Matters for Malaysian Businesses", "2-3 paragraphs on real business impact."),
        ("Step-by-Step Process", "3-4 steps in an <ol>."),
        ("Cost & Budget Guide (RM)", "realistic RM ranges; explain what drives the budget."),
        ("Questions Business Owners Ask", "3 <h3> questions, each answered in a <p>."),
        ("Getting Started", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("600-800", [
        ("Overview", "introduce {kw} with {loc}/Malaysia context in 1-2 paragraphs."),
        ("Who Should Consider This", "describe the ideal business or situation in a <ul>."),
        ("Key Advantages", "3-4 points in a <ul>."),
        ("How the Process Works", "3-4 steps in an <ol>."),
        ("Pricing Explained (RM)", "realistic RM ranges and the main cost factors."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Final Thoughts", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("600-800", [
        ("{kw}: A Practical Guide", "1-2 paragraph introduction with {loc}/Malaysia context."),
        ("Benefits You Can Expect", "3-4 points in a <ul>."),
        ("How We Approach It", "3-4 steps in an <ol>."),
        ("Investment & Pricing (RM)", "realistic RM ranges; explain what affects cost."),
        ("Local Considerations in {loc}", "1-2 paragraphs on the local market."),
        ("Frequently Asked Questions", "3 <h3> questions, each answered in a <p>."),
        ("Next Steps", "1 paragraph, ending with a WhatsApp call to action."),
    ]),
    ("600-800", [
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

ANGLES_MS = [
    "Tekankan ROI yang boleh diukur dan kualiti prospek.",
    "Tulis untuk pembaca yang baru berkecimpung dalam iklan berbayar.",
    "Fokus kepada pasaran Malaysia tempatan dan tingkah laku pembeli.",
    "Ambil sudut praktikal, tanpa hype, dan berhemah dari segi bajet.",
    "Tonjolkan jangkaan realistik dan hasil yang biasa dilihat oleh pelanggan.",
]

# BM (Bahasa Melayu) prompt variants — struktur sama dengan EN, headings
# diterjemah secara natural ke Bahasa Melayu profesional. Voice: 'kami' (we),
# 'anda' (you), RM currency, nada profesional agensi sejak 2016.
PROMPT_VARIANTS_MS = [
    ("600-800", [
        ("Pengenalan", "takrifkan {kw} dalam 1-2 perenggan pendek dengan konteks tempatan {loc}/Malaysia."),
        ("Kelebihan Utama", "3-4 poin dalam <ul>."),
        ("Cara Ia Berfungsi", "3-4 langkah dalam <ol>."),
        ("Harga di Malaysia", "julat harga realistik dalam RM (cth \"dari RM990/sebulan\"); jelaskan apa yang mempengaruhi kos."),
        ("Kesilapan Lazim", "2-3 jebakan dalam <ul>."),
        ("Soalan Lazim", "3 soalan <h3>, setiap satu dijawab dalam <p>."),
        ("Kesimpulan", "1 perenggan, diakhiri dengan panggilan tindakan WhatsApp."),
    ]),
    ("600-800", [
        ("Apa Itu {kw}?", "jelaskan konsep dalam 1-2 perenggan untuk pemilik perniagaan di Malaysia."),
        ("Mengapa Ia Penting untuk Perniagaan Malaysia", "2-3 perenggan tentang kesan sebenar terhadap perniagaan."),
        ("Proses Langkah demi Langkah", "3-4 langkah dalam <ol>."),
        ("Panduan Kos & Belanjawan (RM)", "julat RM yang realistik; jelaskan apa yang mendorong bajet."),
        ("Soalan Pemilik Perniagaan", "3 soalan <h3>, setiap satu dijawab dalam <p>."),
        ("Cara Mula", "1 perenggan, diakhiri dengan panggilan tindakan WhatsApp."),
    ]),
    ("600-800", [
        ("Gambaran Keseluruhan", "perkenalkan {kw} dengan konteks {loc}/Malaysia dalam 1-2 perenggan."),
        ("Siapa Patut Pertimbangkan", "terangkan perniagaan atau situasi yang sesuai dalam <ul>."),
        ("Kelebihan Utama", "3-4 poin dalam <ul>."),
        ("Bagaimana Proses Berfungsi", "3-4 langkah dalam <ol>."),
        ("Penjelasan Harga (RM)", "julat RM yang realistik dan faktor kos utama."),
        ("Soalan Lazim", "3 soalan <h3>, setiap satu dijawab dalam <p>."),
        ("Fikiran Akhir", "1 perenggan, diakhiri dengan panggilan tindakan WhatsApp."),
    ]),
    ("600-800", [
        ("{kw}: Panduan Praktikal", "1-2 perenggan pengenalan dengan konteks {loc}/Malaysia."),
        ("Kelebihan Yang Boleh Dijangka", "3-4 poin dalam <ul>."),
        ("Pendekatan Kami", "3-4 langkah dalam <ol>."),
        ("Pelaburan & Harga (RM)", "julat RM yang realistik; jelaskan apa yang mempengaruhi kos."),
        ("Pertimbangan Tempatan di {loc}", "1-2 perenggan tentang pasaran tempatan."),
        ("Soalan Lazim", "3 soalan <h3>, setiap satu dijawab dalam <p>."),
        ("Langkah Seterusnya", "1 perenggan, diakhiri dengan panggilan tindakan WhatsApp."),
    ]),
    ("600-800", [
        ("Memahami {kw}", "takrifkan dalam 1-2 perenggan dengan konteks Malaysia."),
        ("Bilakah Menggunakan Ia", "2-3 senario dalam <ul>."),
        ("Proses & Tempoh", "3-4 langkah dalam <ol>."),
        ("Julat Belanjawan dalam RM", "angka RM yang realistik dan apa yang mempengaruhinya."),
        ("Soalan Lazim", "3 soalan <h3>, setiap satu dijawab dalam <p>."),
        ("Kesimpulan", "1 perenggan, diakhiri dengan panggilan tindakan WhatsApp."),
    ]),
]

def build_prompt(kw, svc_name, city, svc_key, lang="en"):
    loc = city.title() if city else "Malaysia"
    svc_path = SERVICE_PATHS.get(svc_key, svc_key)
    ilink = f"https://beriklan.my/{svc_path}/"

    platform = svc_name.lower()
    if "google" in platform: elink = "https://ads.google.com/intl/en_my/home/"
    elif "facebook" in platform or "instagram" in platform: elink = "https://www.facebook.com/business/ads"
    elif "tiktok" in platform: elink = "https://ads.tiktok.com/"
    elif "youtube" in platform: elink = "https://www.youtube.com/ads/"
    else: elink = "https://business.google.com/my/"

    hv = int(hashlib.md5(f"{kw}|{svc_key}|{lang}".encode("utf-8")).hexdigest(), 16)
    if lang == "ms":
        variants = PROMPT_VARIANTS_MS
        angles = ANGLES_MS
        lang_directive = "Tulis artikel HTML yang berstruktur dan faktual dalam Bahasa Melayu profesional (BM Malaysia) tentang: {kw}"
        voice_lines = [
            "- Voice: pasukan Beriklan, agensi yang menguruskan kempen iklan sejak 2016.",
            "- Bahasa Melayu profesional semula jadi. Guna 'kami' untuk diri sendiri, 'anda' untuk pembaca.",
            "- Mata wang dalam RM sahaja (jangan sekali-kali guna Rp).",
            "- Elakkan perkataan hype: dijamin, terbaik, 100%, termurah.",
        ]
    else:
        variants = PROMPT_VARIANTS
        angles = ANGLES
        lang_directive = "Write a well-structured, factual HTML article ({wr} words) in professional Malaysian English about: {kw}"
        voice_lines = [
            "- Voice: the Beriklan team, an agency running ad campaigns since 2016.",
            "- Natural professional Malaysian English. Currency in RM only (never Rp).",
            "- Avoid hype words: guaranteed, best, 100%, cheapest.",
        ]
    word_range, sections = variants[hv % len(variants)]
    angle = angles[(hv // 7) % len(angles)]
    heading_block = "\n".join(
        f"<h2>{t.format(kw=kw, loc=loc)}</h2> {g.format(kw=kw, loc=loc)}"
        for t, g in sections
    )

    return f"""{lang_directive.format(kw=kw, wr=word_range)}
Service: {svc_name}. Location: {loc}.
Editorial angle: {angle}

Use these exact <h2> headings in order:
{heading_block}

Requirements:
- STRICTLY keep the entire article between 600 and 800 words. Be thorough — include specific examples, concrete numbers (RM prices, percentages), and 1 inline comparison or mini-list where it helps clarity. Do NOT exceed 800 words.
- Link twice to {ilink} with natural anchor text.
- Link once to <a href="{elink}" rel="nofollow"> as an external reference.
{chr(10).join(voice_lines)}
- Vary sentence structure and openings; do not reuse boilerplate phrasing across sections.
- Output ONLY the article HTML. Start directly with the first <h2>. Do NOT include any planning notes,
  internal monologue, meta-commentary, requirement lists ("1.", "2.", "3."), restating of these
  instructions, or any other text before/after the article. The reader must see ONLY clean article HTML."""

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
                      "max_tokens": 1800, "temperature": 0.4, **extra},
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

# Reasoning-leak markers — when a free model bypasses the "output ONLY HTML"
# directive and starts including planning notes / meta-commentary. Used by
# make_article() to detect & retry such generations.
LEAK_MARKERS = [
    "the user wants", "the user asked", "the user is asking",
    "let me draft", "let me write", "let me create", "let me carefully",
    "let me start", "let me begin", "let me think", "let me outline",
    "i need to", "i will write", "i will draft", "i will create", "i will now",
    "i should write", "i should include", "i need", "i'll write",
    "here is the article", "here's the article", "here is a",
    "looking at the requirements", "based on the requirements",
    "following the requirements", "following these requirements",
    "in this article", "this article will",
    "we need to", "we need", "we will", "we'll", "we should", "we must",
    "now i will", "now let me", "first, i", "first, let me",
    "draft:", "outline:", "structure:", "plan:",
    "saya akan", "saya perlu", "mari saya", "berikut adalah artikel",
    "pengguna mahu", "pengguna ingin",
    "1.", "2.", "3.",  # numbered requirement lists at start
]

def _has_reasoning_leak(html):
    """Detect AI planning notes / meta-commentary leaking into article body."""
    # strip the first <h2>...</h2> block (legitimate article heading) before scanning
    body = re.sub(r"^\s*<h2[^>]*>.*?</h2>", "", html, count=1, flags=re.S).strip()
    # Take first 600 chars of the body — leak typically appears right after heading
    sample = body[:600].lower()
    if not sample:
        return False
    # numbered requirement list at very start (e.g. "1. Exact h2 headings...")
    if re.match(r"^\s*\d+\.\s+\w", sample):
        return True
    # common leak phrasings
    for m in LEAK_MARKERS:
        if m in sample:
            return True
    return False

def _strip_leak(html):
    """If leak is sandwiched between the title <h2> and a real section <h2>,
    drop the leak and keep from the real section onward. A 'real section <h2>'
    has non-empty content (no nested tags) and is followed by a block-level tag.
    Leak <h2>s from requirement lists are either empty or unclosed — filtered out."""
    # Pattern requires well-formed h2 with non-empty content (no nested tags).
    # This excludes empty leak <h2></h2> and unclosed <h2> in requirement lists.
    real_h2_re = re.compile(r"<h2[^>]*>[^<]+</h2>")
    matches = list(real_h2_re.finditer(html))
    if len(matches) < 2:
        return html  # not enough well-formed h2 → can't strip safely
    first_close = matches[0].end()
    block_tags = ("<p>", "<ul>", "<ol>", "<blockquote>", "<h3>", "<hr/>", "<table>")
    # find first real-h2 (after title) whose tail starts with a block-level tag
    for m in matches[1:]:
        tail = html[m.end():m.end() + 50].lstrip()
        if any(tail.startswith(t) for t in block_tags):
            return html[:first_close] + "\n" + html[m.start():]
    return html  # no real section h2 detected — leave as-is

WA_LINK = "https://wa.me/62811919328"

def cta_block(svc_name, svc_key, lang="en"):
    svc_path = SERVICE_PATHS.get(svc_key, svc_key)
    if lang == "ms":
        return (
            "\n<hr/>\n<h2>Bekerja Bersama Beriklan</h2>\n"
            "<p>Beriklan menguruskan kempen iklan berbayar sejak 2016 — telus, boleh diukur, "
            "dengan laporan mingguan dan akses penuh ke akaun iklan anda. "
            f"Terokai <a href=\"https://beriklan.my/{svc_path}/\">pakej {svc_name} kami</a> "
            "atau mulakan rundingan.</p>\n"
            f"<p><a href=\"{WA_LINK}?text=Hai%20Beriklan%2C%20saya%20ingin%20rundingan.\" "
            "rel=\"nofollow\">Berhubung dengan kami di WhatsApp</a> — balasan dalam 1 jam (waktu perniagaan).</p>"
        )
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
    lang = item.get("language") or "en"
    slug = item.get("slug") or re.sub(r"[^a-z0-9-]", "", kw.lower().replace(" ", "-"))[:80]

    if slug in live_slugs:
        return None  # skip duplicate

    svc = item.get("service") or "digital-marketing-agency"
    city = item.get("city") or ""
    svc_name = SERVICE_NAMES.get(svc, svc)

    title = " ".join(w.capitalize() for w in kw.split())
    prompt = build_prompt(kw, svc_name, city, svc, lang)
    raw = call_zen(prompt, zen_key)
    if not raw:
        return None

    content = clean_html(raw)
    # QC: retry once if too short (<200 words) for better quality
    if len(content.split()) < 200:
        raw2 = call_zen(prompt, zen_key)
        if raw2 and len(clean_html(raw2).split()) > len(content.split()):
            content = clean_html(raw2)
    # QC: retry once if AI leaked planning notes / meta-commentary into body.
    # Prefer a clean shorter article over a leaked long one.
    if _has_reasoning_leak(content):
        raw2 = call_zen(prompt, zen_key)
        if raw2:
            content2 = clean_html(raw2)
            if not _has_reasoning_leak(content2) and len(content2.split()) >= 200:
                content = content2
    # QC: if still leaked after retry, try post-process strip (drop the text
    # sandwiched between first <h2> and second <h2>). Common with Qwen-style
    # reasoning models that emit planning notes before the actual article.
    if _has_reasoning_leak(content):
        stripped = _strip_leak(content)
        if not _has_reasoning_leak(stripped):
            content = stripped
    if not content.startswith("<h2>"):
        content = f"<h2>{title}</h2>\n" + content

    # Guarantee internal link to service page + WhatsApp CTA
    if content.count(f"/{SERVICE_PATHS.get(svc, svc)}/") < 1 or "wa.me" not in content:
        content += cta_block(svc_name, svc, lang)

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
        "language": lang,
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