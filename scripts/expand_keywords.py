#!/usr/bin/env python3
"""
expand_keywords.py — Mass-expand keyword queue via intent matrix.

Current: 2763 keywords (suggest + miner). Target: 7000+ via:
  service × city × intent_modifier × year × action_verb explosion

Combinations generated:
- service × city (x26) × modifier (x6)  = 11 × 26 × 6 = 1.716 base
- + question prefixes ("cara", "apa itu", "bagaimana")  = +~600
- + year ("2026", "2027")  = +~700
- + vs comparisons (Beriklan vs X)  = +~50
- + pain point ("gagal", "tidak closing")  = +~150

Dedupe against existing keywords (slug-based).
"""
import json
import os
import re
from itertools import product

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')
QUEUE = os.path.join(WEB, "src", "data", "keyword-queue.json")

SERVICES = [
    ("digital-marketing-agency", "Jasa Digital Marketing", ["jasa digital marketing"]),
    ("facebook-ads-management", "Jasa Iklan Facebook", ["jasa iklan facebook", "iklan facebook"]),
    ("instagram-ads-management", "Jasa Iklan Instagram", ["jasa iklan instagram", "iklan instagram"]),
    ("tiktok-ads-management", "Jasa Iklan TikTok", ["jasa iklan tiktok", "iklan tiktok"]),
    ("google-ads-management", "Jasa Iklan Google", ["jasa iklan google", "iklan google"]),
    ("youtube-ads-management", "Jasa Iklan YouTube", ["jasa iklan youtube", "iklan youtube"]),
    ("instagram-management", "Jasa Kelola Instagram", ["jasa kelola instagram", "kelola instagram"]),
    ("tiktok-management", "Jasa Kelola TikTok", ["jasa kelola tiktok", "kelola tiktok"]),
    ("website-development", "Jasa Pembuatan Website", ["jasa pembuatan website", "pembuatan website"]),
    ("landing-page-design", "Jasa Pembuatan Landing Page", ["jasa landing page", "landing page"]),
    ("live-stream-viewers", "Jasa View Live", ["view live", "viewers live"]),
]

CITIES = ["jakarta", "bandung", "surabaya", "yogyakarta", "semarang", "medan", "makassar",
          "denpasar", "bekasi", "depok", "tangerang", "bogor", "malang", "batam",
          "palembang", "pekanbaru", "sidoarjo", "solo", "padang", "manado",
          "pontianak", "banjarmasin", "lampung", "jambi", "cimahi", "balikpapan"]

# Intent modifiers — prepend/append to base keyword
COMMERCIAL = ["murah", "harga", "biaya", "tarif", "paket", "promo"]
QUALITY = ["terbaik", "profesional", "berpengalaman", "terpercaya"]
ACTION = ["cara", "tips", "tutorial", "langkah", "strategi"]
QUESTION = ["apa itu", "bagaimana", "kenapa", "berapa biaya"]
YEAR = ["2026", "2027"]
PAINPOINT = ["gagal", "tidak closing", "roas rendah", "boncos"]

# Service-specific modifier patterns
SERVICE_MODIFIERS = {
    "digital-marketing-agency": ["umkm", "toko online", "skala kecil", "bisnis menengah", "startup", "b2b"],
    "facebook-ads-management": ["meta ads", "fb ads", "untuk toko online", "untuk umkm", "leadgen"],
    "instagram-ads-management": ["ig ads", "reels ads", "untuk fashion", "untuk beauty", "untuk fnb"],
    "tiktok-ads-management": ["tiktok ads", "spark ads", "untuk produk", "live shopping"],
    "google-ads-management": ["google ads", "search ads", "pmax", "performance max", "untuk jasa", "untuk toko"],
    "youtube-ads-management": ["youtube ads", "video ads", "bumper ads", "trueview"],
    "instagram-management": ["konten harian", "feed aesthetic", "story aktif", "engagement naik"],
    "tiktok-management": ["konten video", "fyp strategy", "live streaming"],
    "website-development": ["company profile", "toko online", "landing page", "wordpress", "custom", "murah", "umkm"],
    "landing-page-design": ["high converting", "untuk google ads", "a/b testing"],
    "live-stream-viewers": ["tiktok live", "instagram live", "shopee live", "youtube live"],
}

VIEW_LIVE_PLATFORMS = ["tiktok", "instagram", "shopee", "youtube", "twitch"]

# ─── LAYER INDUSTRI BARU (Phase 1) — Updated per user table ───
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

# Service → industri match — persis tabel user
SERVICE_INDUSTRY_MATCH = {
    "digital-marketing-agency": None,       # ALL 10 industri
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


def slugify(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s


def score_keyword(kw):
    """Priority score: commercial intent > informational > generic."""
    base = 30
    if any(m in kw for m in ["murah", "harga", "biaya", "tarif", "paket"]):
        base += 25
    if any(m in kw for m in ["2026", "2027", "terbaru"]):
        base += 15
    if any(m in kw for m in ["cara", "tips", "tutorial", "bagaimana"]):
        base += 15
    if any(m in kw for m in ["terbaik", "profesional", "berpengalaman"]):
        base += 10
    if "di " in kw and any(c in kw for c in CITIES):
        base += 10  # local intent
    if "untuk " in kw:
        base += 5  # target audience
    return min(base, 100)


def expand():
    queue = json.load(open(QUEUE))
    existing_slugs = {q["slug"] for q in queue}
    existing_keywords_normalized = {q["keyword_normalized"] for q in queue}
    new_added = []
    seen_slugs = set(existing_slugs)
    seen_kw = set(existing_keywords_normalized)

    # 1) service × city × intent_modifier explosion
    for svc_slug, svc_name, base_names in SERVICES:
        service_modifiers = SERVICE_MODIFIERS.get(svc_slug, [])
        for city in CITIES:
            for base_name in base_names:
                # Base: "{base_name} di {city}"
                kws = [f"{base_name} di {city}"]
                # With each modifier (commercial + quality + service-specific)
                for mod in (COMMERCIAL + QUALITY + service_modifiers):
                    kws.append(f"{base_name} {mod} di {city}")
                    kws.append(f"{base_name} di {city} {mod}")
                # With action verbs
                for act in ACTION:
                    kws.append(f"{act} {base_name} di {city}")
                # With question
                for q in QUESTION:
                    kws.append(f"{q} {base_name} di {city}")
                # With year
                for y in YEAR:
                    kws.append(f"{base_name} di {city} {y}")
                    kws.append(f"harga {base_name} di {city} {y}")
                # Without city (broader coverage)
                for mod in COMMERCIAL + QUALITY:
                    kws.append(f"{base_name} {mod}")

                for kw in kws:
                    kw_norm = re.sub(r"\s+", " ", kw.lower().strip())
                    slug = slugify(kw)
                    if not slug or slug in seen_slugs or kw_norm in seen_kw:
                        continue
                    seen_slugs.add(slug)
                    seen_kw.add(kw_norm)
                    new_added.append({
                        "keyword": kw.title() if kw[0].islower() else kw,
                        "keyword_normalized": kw_norm,
                        "slug": slug,
                        "has_post": False,
                        "priority_score": score_keyword(kw_norm),
                        "source": "expansion_v1",
                        "status": "pending",
                        "rank": 0,
                        "created_at": "2026-07-20T12:00:00+00:00",
                        "service": svc_slug,
                        "city": city,
                    })

    # 2) View-live platform explosion
    for platform in VIEW_LIVE_PLATFORMS:
        for city in CITIES:
            for mod in COMMERCIAL + QUALITY:
                kw = f"view live {platform} {mod} di {city}"
                kw_norm = kw.lower()
                slug = slugify(kw)
                if slug in seen_slugs or kw_norm in seen_kw:
                    continue
                seen_slugs.add(slug)
                seen_kw.add(kw_norm)
                new_added.append({
                    "keyword": kw.title(),
                    "keyword_normalized": kw_norm,
                    "slug": slug,
                    "has_post": False,
                    "priority_score": score_keyword(kw_norm),
                    "source": "expansion_v1",
                    "status": "pending",
                    "rank": 0,
                    "created_at": "2026-07-20T12:00:00+00:00",
                    "service": "live-stream-viewers",
                    "city": city,
                })

    # 2.5) LAYER INDUSTRI BARU — 9 industri × layanan × kota
    for svc_slug, svc_name, base_names in SERVICES:
        matched_industries = SERVICE_INDUSTRY_MATCH.get(svc_slug)
        for ind_id, ind_name, ind_aliases in INDUSTRIES:
            # Skip if service doesn't match this industry
            if matched_industries is not None and ind_id not in matched_industries:
                continue

            for alias in ind_aliases[:1]:  # use first alias as canonical
                # Pattern 1: "jasa {service} untuk {industri}"
                kw = f"{base_names[0]} untuk {alias}"
                kw_norm = kw.lower()
                slug = slugify(kw)
                if slug not in seen_slugs and kw_norm not in seen_kw:
                    seen_slugs.add(slug); seen_kw.add(kw_norm)
                    new_added.append({
                        "keyword": kw.title(), "keyword_normalized": kw_norm,
                        "slug": slug, "has_post": False,
                        "priority_score": 70 if matched_industries is None or ind_id in matched_industries else 50,
                        "source": "industri_v1", "status": "pending", "rank": 0,
                        "created_at": "2026-07-24T12:00:00+00:00",
                        "service": svc_slug, "city": None, "industry": ind_id,
                    })

                # Pattern 2: "jasa {service} untuk {industri} di {kota}"
                for city in CITIES:
                    kw = f"{base_names[0]} untuk {alias} di {city}"
                    kw_norm = kw.lower()
                    slug = slugify(kw)
                    if slug not in seen_slugs and kw_norm not in seen_kw:
                        seen_slugs.add(slug); seen_kw.add(kw_norm)
                        new_added.append({
                            "keyword": kw.title(), "keyword_normalized": kw_norm,
                            "slug": slug, "has_post": False,
                            "priority_score": 65 if matched_industries is None or ind_id in matched_industries else 45,
                            "source": "industri_v1", "status": "pending", "rank": 0,
                            "created_at": "2026-07-24T12:00:00+00:00",
                            "service": svc_slug, "city": city, "industry": ind_id,
                        })

                # Pattern 3: "{industri} {service}" (e.g. "e-commerce facebook ads")
                kw = f"{alias} {base_names[0]}"
                kw_norm = kw.lower()
                slug = slugify(kw)
                if slug not in seen_slugs and kw_norm not in seen_kw:
                    seen_slugs.add(slug); seen_kw.add(kw_norm)
                    new_added.append({
                        "keyword": kw.title(), "keyword_normalized": kw_norm,
                        "slug": slug, "has_post": False,
                        "priority_score": 55,
                        "source": "industri_v1", "status": "pending", "rank": 0,
                        "created_at": "2026-07-24T12:00:00+00:00",
                        "service": svc_slug, "city": None, "industry": ind_id,
                    })

                # Pattern 4: "harga/biaya {service} untuk {industri}"
                for modifier in ["harga", "biaya", "paket"]:
                    kw = f"{modifier} {base_names[0]} untuk {alias}"
                    kw_norm = kw.lower()
                    slug = slugify(kw)
                    if slug not in seen_slugs and kw_norm not in seen_kw:
                        seen_slugs.add(slug); seen_kw.add(kw_norm)
                        new_added.append({
                            "keyword": kw.title(), "keyword_normalized": kw_norm,
                            "slug": slug, "has_post": False,
                            "priority_score": 75,
                            "source": "industri_v1", "status": "pending", "rank": 0,
                            "created_at": "2026-07-24T12:00:00+00:00",
                            "service": svc_slug, "city": None, "industry": ind_id,
                        })

    # 3) A vs B comparisons (service vs service AND service vs competitor)
    # 3a) Service vs service per kota
    compare_pairs = [
        ("facebook ads", "google ads", "facebook-ads-management", "google-ads-management"),
        ("instagram ads", "tiktok ads", "instagram-ads-management", "tiktok-ads-management"),
        ("facebook ads", "tiktok ads", "facebook-ads-management", "tiktok-ads-management"),
        ("google ads", "youtube ads", "google-ads-management", "youtube-ads-management"),
        ("kelola instagram", "kelola tiktok", "instagram-management", "tiktok-management"),
        ("facebook ads", "instagram ads", "facebook-ads-management", "instagram-ads-management"),
        ("google ads", "facebook ads", "google-ads-management", "facebook-ads-management"),
        ("tiktok ads", "youtube ads", "tiktok-ads-management", "youtube-ads-management"),
        ("website", "landing page", "website-development", "landing-page-design"),
        ("iklan facebook", "iklan google", "facebook-ads-management", "google-ads-management"),
    ]
    for a, b, svc_a, svc_b in compare_pairs:
        for fmt in ["{a} vs {b}", "{a} atau {b}", "perbedaan {a} dan {b}", "mana lebih baik {a} atau {b}"]:
            kw = fmt.replace("{a}", a).replace("{b}", b)
            kw_norm = kw.lower()
            slug = slugify(kw)
            if slug not in seen_slugs and kw_norm not in seen_kw:
                seen_slugs.add(slug); seen_kw.add(kw_norm)
                new_added.append({
                    "keyword": kw.title() if kw[0].islower() else kw,
                    "keyword_normalized": kw_norm, "slug": slug, "has_post": False,
                    "priority_score": 65, "source": "expansion_v1",
                    "status": "pending", "rank": 0,
                    "created_at": "2026-07-24T12:00:00+00:00",
                    "service": svc_a, "city": None,
                })
            for city in CITIES[:10]:
                for fmt2 in ["{a} vs {b} di {city}", "{a} atau {b} di {city}"]:
                    kw2 = fmt2.replace("{a}", a).replace("{b}", b).replace("{city}", city)
                    kw2_norm = kw2.lower()
                    slug2 = slugify(kw2)
                    if slug2 not in seen_slugs and kw2_norm not in seen_kw:
                        seen_slugs.add(slug2); seen_kw.add(kw2_norm)
                        new_added.append({
                            "keyword": kw2.title() if kw2[0].islower() else kw2,
                            "keyword_normalized": kw2_norm, "slug": slug2, "has_post": False,
                            "priority_score": 60, "source": "expansion_v1",
                            "status": "pending", "rank": 0,
                            "created_at": "2026-07-24T12:00:00+00:00",
                            "service": svc_a, "city": city,
                        })

    # 3b) Service vs platform competitors
    competitors = ["lazada", "shopee", "lazada", "blibli", "tiktok shop"]
    for svc_slug, svc_name, _ in SERVICES[:6]:
        for comp in competitors:
            kw = f"{svc_name} vs {comp}"
            kw_norm = kw.lower()
            slug = slugify(kw)
            if slug not in seen_slugs and kw_norm not in seen_kw:
                seen_slugs.add(slug); seen_kw.add(kw_norm)
                new_added.append({
                    "keyword": kw, "keyword_normalized": kw_norm,
                    "slug": slug, "has_post": False,
                    "priority_score": 65, "source": "expansion_v1",
                    "status": "pending", "rank": 0,
                    "created_at": "2026-07-24T12:00:00+00:00",
                    "service": svc_slug, "city": None,
                })

    # 4) Pain-point queries — expanded to ALL cities
    pain_templates = [
        "{svc} boncos", "iklan {svc} tidak closing", "budget {svc} terbuang",
        "roas rendah {svc}", "{svc} sepi viewers", "{svc} gagal",
        "{svc} tidak efektif", "rugi pakai {svc}",
    ]
    for svc_slug, svc_name, base_names in SERVICES:
        for base_name in base_names[:1]:
            for pain in pain_templates:
                kw = pain.replace("{svc}", base_name)
                kw_norm = kw.lower()
                slug = slugify(kw)
                if slug not in seen_slugs and kw_norm not in seen_kw:
                    seen_slugs.add(slug); seen_kw.add(kw_norm)
                    new_added.append({
                        "keyword": kw.title() if kw[0].islower() else kw,
                        "keyword_normalized": kw_norm, "slug": slug, "has_post": False,
                        "priority_score": 70, "source": "expansion_v1",
                        "status": "pending", "rank": 0,
                        "created_at": "2026-07-24T12:00:00+00:00",
                        "service": svc_slug, "city": None,
                    })
                # + ALL cities for top pain templates
                if pain in ["{svc} boncos", "iklan {svc} tidak closing"]:
                    for city in CITIES[:15]:
                        kw2 = f"{pain.replace('{svc}', base_name)} di {city}"
                        kw2_norm = kw2.lower()
                        slug2 = slugify(kw2)
                        if slug2 not in seen_slugs and kw2_norm not in seen_kw:
                            seen_slugs.add(slug2); seen_kw.add(kw2_norm)
                            new_added.append({
                                "keyword": kw2.title() if kw2[0].islower() else kw2,
                                "keyword_normalized": kw2_norm, "slug": slug2, "has_post": False,
                                "priority_score": 75, "source": "expansion_v1",
                                "status": "pending", "rank": 0,
                                "created_at": "2026-07-24T12:00:00+00:00",
                                "service": svc_slug, "city": city,
                            })
                    
    print(f"Existing: {len(queue)}")
    print(f"New generated: {len(new_added)}")
    print(f"After expansion: {len(queue) + len(new_added)}")

    if new_added:
        queue.extend(new_added)
        json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)
        print(f"Saved to {QUEUE}")

    # Stats per service
    from collections import Counter
    new_by_svc = Counter(x.get("service") for x in new_added)
    print("\nNew keywords by service:")
    for s, c in new_by_svc.most_common():
        print(f"  {s}: {c}")


if __name__ == "__main__":
    expand()