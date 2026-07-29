#!/usr/bin/env python3
"""Inject PAASection into all 10 service pages after FaqAccordion."""
import re
from pathlib import Path

# (filename, service_slug, canonical_url)
PAGES = [
    ("digital-marketing-agency.astro", "digital-marketing-agency", "https://beriklan.my/digital-marketing-agency/"),
    ("facebook-ads-management.astro", "facebook-ads-management", "https://beriklan.my/facebook-ads-management/"),
    ("google-ads-management.astro", "google-ads-management", "https://beriklan.my/google-ads-management/"),
    ("instagram-ads-management.astro", "instagram-ads-management", "https://beriklan.my/instagram-ads-management/"),
    ("tiktok-ads-management.astro", "tiktok-ads-management", "https://beriklan.my/tiktok-ads-management/"),
    ("youtube-ads-management.astro", "youtube-ads-management", "https://beriklan.my/youtube-ads-management/"),
    ("instagram-management.astro", "instagram-management", "https://beriklan.my/instagram-management/"),
    ("tiktok-management.astro", "tiktok-management", "https://beriklan.my/tiktok-management/"),
    ("landing-page-design.astro", "landing-page-design", "https://beriklan.my/landing-page-design/"),
    ("website-development.astro", "website-development", "https://beriklan.my/website-development/"),
]

PAGES_DIR = Path("src/pages")

for filename, service_slug, canonical_url in PAGES:
    filepath = PAGES_DIR / filename
    content = filepath.read_text()

    # Skip if already injected
    if "<PAASection" in content:
        print(f"SKIP {filename}: already has PAASection")
        continue

    # 1. Add import after FaqAccordion import
    import_marker = "import FaqAccordion from '../components/FaqAccordion.svelte';"
    if import_marker not in content:
        print(f"SKIP {filename}: FaqAccordion import not found")
        continue

    new_imports = (
        "import FaqAccordion from '../components/FaqAccordion.svelte';\n"
        "import PAASection from '../components/PAASection.astro';"
    )
    content = content.replace(import_marker, new_imports, 1)

    # 2. Insert PAASection after </section> closing FAQ section
    # Pattern: <FaqAccordion items={faqs} client:visible /> </div> </section>
    # Insert PAASection before <RelatedServices
    related_pattern = r"(<RelatedServices)"
    if not re.search(related_pattern, content):
        print(f"SKIP {filename}: RelatedServices not found")
        continue

    paa_block = (
        f"\n    <!-- ====================== PAA (People Also Ask) ====================== -->\n"
        f"    <PAASection service=\"{service_slug}\" pageUrl=\"{canonical_url}\" />\n\n    "
    )
    content = re.sub(related_pattern, paa_block + r"\1", content, count=1)

    filepath.write_text(content)
    print(f"OK {filename} → service={service_slug}")

print("\nDone.")
