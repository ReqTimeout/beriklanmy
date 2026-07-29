#!/usr/bin/env python3
"""
expand_massive_v3.py — Phase 1 massive expansion v3.
Updated SERVICE_INDUSTRY_MATCH persis tabel user + industry-specific keyword patterns.
"""
import json, os, re

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')
QUEUE = os.path.join(WEB, "src", "data", "keyword-queue.json")

CITIES = ["jakarta","bandung","surabaya","yogyakarta","semarang","medan","makassar",
          "denpasar","bekasi","depok","tangerang","bogor","malang","batam",
          "palembang","pekanbaru","sidoarjo","solo","padang","manado",
          "pontianak","banjarmasin","lampung","jambi","cimahi","balikpapan"]

# Updated industries — beauty added
INDUSTRIES = [
    ("e-commerce", "E-Commerce", ["e-commerce","online shop","toko online","marketplace"]),
    ("properti", "Properti", ["properti","real estate","developer"]),
    ("pendidikan", "Pendidikan", ["pendidikan","edutech","sekolah","kursus","bimbel"]),
    ("kesehatan", "Kesehatan", ["kesehatan","klinik","rumah sakit","dokter","skincare"]),
    ("fnb", "F&B", ["fnb","restoran","makanan","kuliner","kafe"]),
    ("fashion", "Fashion", ["fashion","busana","pakaian","brand fashion"]),
    ("beauty", "Beauty", ["beauty","kosmetik","skincare","makeup","perawatan"]),
    ("travel", "Travel", ["travel","hotel","wisata","hospitality","pariwisata"]),
    ("otomotif", "Otomotif", ["otomotif","mobil","motor","bengkel","dealer"]),
    ("jasa-profesional", "Jasa Profesional", ["jasa profesional","konsultan","b2b","advokat","notaris"]),
]

# Updated match matrix — persis tabel user
SERVICE_INDUSTRY_MATCH = {
    "digital-marketing-agency": None,
    "facebook-ads-management": ["e-commerce","fashion","fnb","properti","kesehatan","otomotif","jasa-profesional"],
    "instagram-ads-management": ["fashion","beauty","fnb","travel","e-commerce"],
    "tiktok-ads-management": ["fashion","beauty","fnb","e-commerce","pendidikan"],
    "google-ads-management": ["properti","kesehatan","jasa-profesional","otomotif","pendidikan","travel"],
    "youtube-ads-management": ["otomotif","properti","pendidikan","travel","fnb"],
    "instagram-management": ["fashion","beauty","fnb","kesehatan","travel"],
    "tiktok-management": ["fashion","beauty","fnb","e-commerce","pendidikan"],
    "website-development": ["e-commerce","properti","pendidikan","kesehatan","fnb","jasa-profesional"],
    "landing-page-design": ["e-commerce","properti","pendidikan","kesehatan","jasa-profesional"],
    "live-stream-viewers": ["e-commerce","fashion","fnb"],
}

SERVICES = [
    ("digital-marketing-agency", "Jasa Digital Marketing", ["jasa digital marketing", "digital marketing", "jasa marketing"]),
    ("facebook-ads-management", "Jasa Iklan Facebook", ["jasa iklan facebook", "iklan facebook", "facebook ads"]),
    ("instagram-ads-management", "Jasa Iklan Instagram", ["jasa iklan instagram", "iklan instagram", "instagram ads"]),
    ("tiktok-ads-management", "Jasa Iklan TikTok", ["jasa iklan tiktok", "iklan tiktok", "tiktok ads"]),
    ("google-ads-management", "Jasa Iklan Google", ["jasa iklan google", "iklan google", "google ads"]),
    ("youtube-ads-management", "Jasa Iklan YouTube", ["jasa iklan youtube", "iklan youtube", "youtube ads"]),
    ("instagram-management", "Jasa Kelola Instagram", ["jasa kelola instagram", "kelola instagram", "jasa instagram"]),
    ("tiktok-management", "Jasa Kelola TikTok", ["jasa kelola tiktok", "kelola tiktok", "jasa tiktok"]),
    ("website-development", "Jasa Pembuatan Website", ["jasa pembuatan website", "pembuatan website", "jasa buat website"]),
    ("landing-page-design", "Jasa Pembuatan Landing Page", ["jasa landing page", "landing page"]),
    ("live-stream-viewers", "Jasa View Live", ["view live", "viewers live", "jasa view"]),
]

def slugify(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s

def score_keyword(kw):
    base = 30
    if any(m in kw for m in ["murah","harga","biaya","tarif","paket","promo","diskon"]): base += 25
    if any(m in kw for m in ["2026","2027","terbaru"]): base += 15
    if any(m in kw for m in ["cara","tips","tutorial","bagaimana","belajar"]): base += 15
    if any(m in kw for m in ["terbaik","profesional","berpengalaman","rekomendasi"]): base += 10
    if any(c in kw for c in CITIES): base += 10
    if "untuk" in kw: base += 5
    return min(base, 100)

def generate():
    queue = json.load(open(QUEUE))
    seen_slugs = {q["slug"] for q in queue}
    seen_kw = {q["keyword_normalized"] for q in queue}
    new = []

    def add(kw_text, svc_slug, ind_id=None, city=None, score_bonus=0):
        kw_norm = re.sub(r"\s+", " ", kw_text.lower().strip())
        slug = slugify(kw_norm)
        if not slug or slug in seen_slugs or kw_norm in seen_kw:
            return
        seen_slugs.add(slug); seen_kw.add(kw_norm)
        new.append({
            "keyword": kw_text.title() if kw_text[0].islower() else kw_text,
            "keyword_normalized": kw_norm, "slug": slug, "has_post": False,
            "priority_score": score_keyword(kw_norm) + score_bonus,
            "source": "expansion_v3",
            "status": "pending", "rank": 0,
            "created_at": "2026-07-24T12:00:00+00:00",
            "service": svc_slug, "city": city, "industry": ind_id,
        })

    # ────────────────────────────────────────────────
    # PASS A: Industry-specific keyword patterns (NEW)
    # ────────────────────────────────────────────────
    industry_patterns = {
        "e-commerce": [
            "jasa {svc} untuk toko online", "{svc} marketplace", "{svc} e commerce indonesia",
            "strategi {svc} online shop", "{svc} untuk jualan online", "{svc} e commerce murah",
            "optimasi {svc} toko online", "{svc} untuk penjual marketplace",
            "kelola {svc} e commerce", "boost penjualan {svc} online",
        ],
        "properti": [
            "jasa {svc} properti", "{svc} developer properti", "{svc} untuk agen properti",
            "marketing properti {svc}", "{svc} perumahan", "{svc} properti komersial",
            "iklan properti {svc}", "promosi properti {svc}", "pasang {svc} properti",
            "{svc} untuk broker properti",
        ],
        "pendidikan": [
            "jasa {svc} pendidikan", "{svc} untuk sekolah", "{svc} kursus online",
            "{svc} edutech", "{svc} untuk bimbel", "{svc} lembaga pendidikan",
            "promosi sekolah {svc}", "{svc} untuk universitas", "iklan {svc} pendidikan",
            "{svc} untuk pelatihan online",
        ],
        "kesehatan": [
            "jasa {svc} klinik", "{svc} untuk rumah sakit", "{svc} dokter praktik",
            "{svc} kesehatan", "promosi klinik {svc}", "iklan {svc} rumah sakit",
            "{svc} untuk bidan", "{svc} klinik kecantikan", "{svc} untuk apotek",
            "{svc} tenaga kesehatan",
        ],
        "fnb": [
            "jasa {svc} restoran", "{svc} untuk kafe", "{svc} bisnis kuliner",
            "promosi makanan {svc}", "{svc} rumah makan", "{svc} untuk catering",
            "{svc} fnb indonesia", "marketing restoran {svc}", "iklan {svc} kuliner",
            "{svc} untuk bisnis makanan",
        ],
        "fashion": [
            "jasa {svc} fashion", "{svc} brand fashion", "{svc} untuk butik",
            "promosi fashion {svc}", "{svc} clothing brand", "{svc} fashion lokal",
            "iklan {svc} fashion", "{svc} untuk distro", "marketing fashion {svc}",
            "{svc} fashion muslim",
        ],
        "beauty": [
            "jasa {svc} beauty", "{svc} brand skincare", "{svc} kosmetik indonesia",
            "promosi beauty {svc}", "{svc} makeup lokal", "{svc} untuk klinik kecantikan",
            "iklan {svc} kosmetik", "marketing {svc} beauty", "{svc} produk perawatan",
            "{svc} beauty influencer",
        ],
        "travel": [
            "jasa {svc} travel", "{svc} hotel", "{svc} agen perjalanan",
            "promosi wisata {svc}", "{svc} hospitality", "{svc} untuk villa",
            "iklan {svc} travel", "{svc} paket wisata", "marketing {svc} hospitality",
            "{svc} destinasi wisata",
        ],
        "otomotif": [
            "jasa {svc} otomotif", "{svc} dealer mobil", "{svc} bengkel",
            "promosi {svc} otomotif", "{svc} showroom motor", "{svc} untuk showroom",
            "iklan {svc} otomotif", "{svc} aksesoris mobil", "marketing {svc} otomotif",
            "{svc} showroom mobil",
        ],
        "jasa-profesional": [
            "jasa {svc} profesional", "{svc} untuk konsultan", "{svc} jasa b2b",
            "promosi {svc} profesional", "{svc} advokat", "{svc} untuk notaris",
            "iklan {svc} profesional", "{svc} akuntan publik", "marketing {svc} b2b",
            "{svc} bisnis jasa",
        ],
    }

    for svc_slug, svc_name, base_names in SERVICES:
        svc_short = base_names[0]
        matched = SERVICE_INDUSTRY_MATCH.get(svc_slug)
        for ind_id, ind_name, ind_aliases in INDUSTRIES:
            if matched is not None and ind_id not in matched:
                continue
            patterns = industry_patterns.get(ind_id, [])
            for pat in patterns:
                kw = pat.replace("{svc}", svc_short)
                add(kw, svc_slug, ind_id)
                for city in CITIES:
                    kc = f"{kw} di {city}"
                    add(kc, svc_slug, ind_id, city)

    # ────────────────────────────────────────────────
    # PASS B: View Live — 6 segments (from user's table)
    # ────────────────────────────────────────────────
    view_segments = [
        ("seller", "Live Commerce Seller", ["shopee live","tiktok shop","live commerce","live shopping"]),
        ("fashion-beauty", "Fashion Beauty Live", ["fashion live","beauty live","live fashion"]),
        ("fnb", "F&B Kuliner Live", ["kuliner live","makanan live","fnb live"]),
        ("gaming", "Gaming Streamer", ["gaming live","streamer","game live"]),
        ("event", "Brand Launching Event", ["launching event","brand launching","event live"]),
        ("affiliate", "Affiliate Creator", ["affiliate live","creator live","affiliate"]),
    ]
    for seg_id, seg_name, seg_aliases in view_segments:
        for alias in seg_aliases:
            for city in CITIES:
                pats = [
                    f"jasa view {alias} di {city}",
                    f"beli view {alias} di {city}",
                    f"paket view {alias} di {city}",
                    f"view {alias} murah di {city}",
                    f"jasa live {alias} di {city}",
                    f"boost viewer {alias} di {city}",
                ]
                for p in pats:
                    add(p, "live-stream-viewers", seg_id, city)

    # ────────────────────────────────────────────────
    # PASS C: Kelola-specific patterns (personal brand)
    # ────────────────────────────────────────────────
    for svc_slug in ["instagram-management", "tiktok-management"]:
        svc_short = "jasa kelola instagram" if "instagram" in svc_slug else "jasa kelola tiktok"
        for city in CITIES:
            pb_pats = [
                f"{svc_short} personal branding di {city}",
                f"bangun personal brand {svc_short} di {city}",
                f"{svc_short} untuk influencer di {city}",
                f"{svc_short} untuk content creator di {city}",
                f"{svc_short} personal brand profesional di {city}",
            ]
            for p in pb_pats:
                add(p, svc_slug, city=city)

    # ────────────────────────────────────────────────
    # PASS D: Landing page — event specific
    # ────────────────────────────────────────────────
    for city in CITIES:
        event_pats = [
            f"landing page untuk event di {city}",
            f"buat landing page webinar di {city}",
            f"landing page pendaftaran event di {city}",
            f"landing page acara di {city}",
            f"halaman pendaftaran webinar di {city}",
        ]
        for p in event_pats:
            add(p, "landing-page-design", city=city)

    # ────────────────────────────────────────────────
    # PASS E: Service-specific deep niche patterns
    # ────────────────────────────────────────────────
    for svc_slug, svc_name, base_names in SERVICES:
        svc_short = base_names[0]
        matched = SERVICE_INDUSTRY_MATCH.get(svc_slug)
        
        # "Untuk" variations with industry aliases
        for ind_id, ind_name, ind_aliases in INDUSTRIES:
            if matched is not None and ind_id not in matched:
                continue
            # Use ALL aliases for industry
            for alias in ind_aliases[1:]:  # skip first (already used in v2)
                patterns = [
                    f"{svc_short} untuk {alias}",
                    f"{svc_short} untuk {alias} murah",
                    f"{svc_short} bagi {alias}",
                    f"rekomendasi {svc_short} untuk {alias}",
                    f"biaya {svc_short} untuk {alias}",
                    f"paket {svc_short} untuk {alias}",
                ]
                for pat in patterns:
                    add(pat, svc_slug, ind_id)
                    for city in CITIES[:15]:
                        add(f"{pat} di {city}", svc_slug, ind_id, city)

    # ────────────────────────────────────────────────
    # REPORT
    # ────────────────────────────────────────────────
    print(f"Existing: {len(queue)}")
    print(f"New generated: {len(new)}")
    print(f"After expansion: {len(queue) + len(new)}")

    if new:
        queue.extend(new)
        json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)
        print(f"Saved to {QUEUE}")

    from collections import Counter
    new_by_svc = Counter(x.get("service") for x in new)
    print("\nNew keywords by service:")
    for s, c in new_by_svc.most_common():
        print(f"  {s}: {c}")

    new_by_ind = Counter(x.get("industry") for x in new if x.get("industry"))
    print("\nNew keywords with industry:")
    for s, c in new_by_ind.most_common():
        print(f"  {s}: {c}")

if __name__ == "__main__":
    generate()
