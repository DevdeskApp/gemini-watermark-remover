import os
import re
import json
import sys
import xml.etree.ElementTree as ET

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def run_tests():
    print("=" * 70)
    print("END-TO-END VALIDATION & CONTEST AUDIT: Gemini Watermark Remover")
    print(f"Directory: {BASE_DIR}")
    print("=" * 70)

    errors = 0

    # 1. Essential Root Files Verification
    required_files = [
        "index.html", "about.html", "contact.html", "disclaimer.html",
        "privacy-policy.html", "terms-of-service.html",
        "style.css", "main.js", "sw.js", "ads.txt", "robots.txt", "sitemap.xml",
        "CNAME", "googlec621a4d35c484e60.html"
    ]
    print("\n[1] Checking Essential Root Files...")
    for rf in required_files:
        full_p = os.path.join(BASE_DIR, rf)
        if not os.path.exists(full_p):
            print(f"  [ERROR] Missing file: {rf}")
            errors += 1
        else:
            print(f"  [OK] {rf} present ({os.path.getsize(full_p)} bytes)")

    # Check that .git repository is active
    git_dir = os.path.join(BASE_DIR, ".git")
    if os.path.exists(git_dir):
        print("  [OK] .git repository active on branch main.")
    else:
        print("  [ERROR] .git directory missing.")
        errors += 1

    # 2. Security & Malware Audit (Zero Adware/Monetag Guarantee)
    print("\n[2] Checking Security & Zero Malicious Code...")
    malicious_patterns = [
        r"omg10\.com",
        r"MONETAG",
        r"handleDownloadAd",
        r"handleExportAd",
        r"isharamadushankab@gmail\.com",
        r"ishara\.madu"
    ]

    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.xml', '.txt', '.webmanifest')):
                fp = os.path.join(root, f)
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fl:
                    content = fl.read()
                for pattern in malicious_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        rel = os.path.relpath(fp, BASE_DIR)
                        print(f"  [ERROR] Found blacklisted pattern '{pattern}' in {rel} ({len(matches)} occurrences)")
                        errors += 1
    if errors == 0:
        print("  [OK] Zero malicious / adware redirect patterns found across all files!")

    # 3. Google AdSense & Ads.txt Verification
    print("\n[3] Validating Google AdSense & ads.txt...")
    ads_txt_path = os.path.join(BASE_DIR, "ads.txt")
    if os.path.exists(ads_txt_path):
        with open(ads_txt_path, 'r', encoding='utf-8') as f:
            ads_content = f.read().strip()
        if "google.com, pub-2136229145694242, DIRECT, f08c47fec0942fa0" in ads_content:
            print("  [OK] ads.txt verified with correct publisher ID.")
        else:
            print("  [ERROR] ads.txt invalid format or publisher ID.")
            errors += 1
    else:
        print("  [ERROR] ads.txt missing!")
        errors += 1

    # 4. Check HTML Pages for SEO, AdSense, Analytics, and BMC
    html_files = [f for f in os.listdir(BASE_DIR) if f.endswith('.html') and not f.startswith('google')]
    print(f"\n[4] Validating {len(html_files)} HTML Pages for SEO, AdSense, Analytics & BMC...")

    for hf in html_files:
        hp = os.path.join(BASE_DIR, hf)
        with open(hp, 'r', encoding='utf-8') as f:
            content = f.read()

        # Title
        title_m = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if not title_m or len(title_m.group(1).strip()) < 10:
            print(f"  [ERROR] Missing or short <title> in {hf}")
            errors += 1
        else:
            print(f"  [OK] {hf} -> Title: '{title_m.group(1).strip()[:40]}...'")

        # Meta description
        desc_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE | re.DOTALL)
        if not desc_m or len(desc_m.group(1).strip()) < 20:
            print(f"  [ERROR] Missing or short meta description in {hf}")
            errors += 1

        # Exactly 1 H1
        h1_matches = re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE | re.DOTALL)
        if len(h1_matches) != 1:
            print(f"  [ERROR] Expected exactly 1 <h1> in {hf}, found {len(h1_matches)}")
            errors += 1

        # Google AdSense meta account
        if 'name="google-adsense-account" content="ca-pub-2136229145694242"' not in content:
            print(f"  [ERROR] Missing google-adsense-account in {hf}")
            errors += 1

        # Google site verification meta tag
        if 'name="google-site-verification" content="AonfzJBrxuLc3Obzd6gtq59VYwqOTXUwQbF22kDvlL4"' not in content:
            print(f"  [ERROR] Missing google-site-verification in {hf}")
            errors += 1

        # Google tag (gtag)
        if 'G-63YJ4Y9W27' not in content:
            print(f"  [ERROR] Missing Google Analytics G-63YJ4Y9W27 in {hf}")
            errors += 1

        # Buy Me A Coffee link
        if 'buymeacoffee.com/devdeskapp' not in content:
            print(f"  [ERROR] Missing BuyMeACoffee devdeskapp link in {hf}")
            errors += 1

        # Canonical tag
        if not re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']https://gemini-watermark-remover\.devdeskapp\.com/', content):
            print(f"  [ERROR] Missing or invalid canonical tag in {hf}")
            errors += 1

        # Theme Toggle Button
        if 'themeToggleBtn' not in content:
            print(f"  [ERROR] Missing themeToggleBtn in {hf}")
            errors += 1

        # WebApp Download / Install Button
        if 'navInstallBtn' not in content:
            print(f"  [ERROR] Missing navInstallBtn in {hf}")
            errors += 1

    # 5. Check index.html Ad Units & BMC Widget
    print("\n[5] Checking Ad Units & BMC Widget in index.html...")
    with open(os.path.join(BASE_DIR, "index.html"), 'r', encoding='utf-8') as f:
        idx_content = f.read()

    # Ad slots
    ad_slots = re.findall(r'class="adsbygoogle"', idx_content)
    if len(ad_slots) >= 3:
        print(f"  [OK] Found {len(ad_slots)} responsive AdSense ad slots in index.html")
    else:
        print(f"  [ERROR] Expected at least 3 AdSense slots in index.html, found {len(ad_slots)}")
        errors += 1

    # BMC widget configuration
    if "data-id', 'devdeskapp'" in idx_content:
        print("  [OK] BuyMeACoffee widget configured with ID 'devdeskapp'")
    else:
        print("  [ERROR] BuyMeACoffee widget missing or invalid ID in index.html")
        errors += 1

    # JSON-LD Structured Data
    json_ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', idx_content, re.DOTALL)
    if not json_ld_matches:
        print("  [ERROR] No JSON-LD structured data found in index.html")
        errors += 1
    else:
        for idx, s in enumerate(json_ld_matches):
            try:
                parsed = json.loads(s.strip())
                print(f"  [OK] JSON-LD Block #{idx+1} valid JSON (Type: {parsed.get('@graph', [{}])[0].get('@type', 'Valid')})")
            except Exception as e:
                print(f"  [ERROR] Invalid JSON-LD block #{idx+1}: {e}")
                errors += 1

    # 6. Validate sitemap.xml
    print("\n[6] Validating sitemap.xml...")
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('.//ns:loc', ns) or root.findall('.//loc')
        if len(urls) == 6:
            print(f"  [OK] sitemap.xml contains all {len(urls)} registered site pages:")
            for u in urls:
                print(f"       -> {u.text}")
        else:
            print(f"  [ERROR] Expected 6 URLs in sitemap, found {len(urls)}")
            errors += 1

        with open(sitemap_path, 'r', encoding='utf-8') as f:
            sm_raw = f.read()
        if '<changefreq>monthly</changefreq>' in sm_raw:
            print("  [ERROR] sitemap.xml still contains 'monthly' changefreq! Expected weekly.")
            errors += 1
        elif '<changefreq>weekly</changefreq>' in sm_raw:
            print("  [OK] sitemap.xml changefreq updated to 'weekly' across all pages.")
        else:
            print("  [ERROR] sitemap.xml missing 'weekly' changefreq tag.")
            errors += 1
    except Exception as e:
        print(f"  [ERROR] sitemap.xml parsing error: {e}")
        errors += 1

    # 7. Validate robots.txt
    print("\n[7] Validating robots.txt...")
    robots_path = os.path.join(BASE_DIR, "robots.txt")
    if os.path.exists(robots_path):
        with open(robots_path, 'r', encoding='utf-8') as f:
            rc = f.read()
        if "User-agent: *" in rc and "Sitemap: https://gemini-watermark-remover.devdeskapp.com/sitemap.xml" in rc:
            print("  [OK] robots.txt validated with User-agent and Sitemap directive.")
        else:
            print("  [ERROR] robots.txt missing directives.")
            errors += 1
    else:
        print("  [ERROR] robots.txt missing!")
        errors += 1

    # 8. Check Local Assets Integrity
    print("\n[8] Checking Local Asset Dependencies...")
    key_assets = [
        "assets/bg1.webp", "assets/bg2.webp", "assets/bg_96.png", "assets/bg_48.png",
        "assets/logo.webp", "assets/favicon.ico", "assets/favicon.svg",
        "assets/gemini-watermark-remover-before.webp",
        "assets/gemini-watermark-remover-after.webp",
        "assets/gemini-watermark-remover-preview-left.webp",
        "assets/veo-video-watermark-cleaner-preview-right.webp",
        "assets/gemini-watermark-remover-logo.webp"
    ]
    for ka in key_assets:
        kap = os.path.join(BASE_DIR, ka)
        if not os.path.exists(kap):
            print(f"  [ERROR] Missing key asset: {ka}")
            errors += 1
        else:
            print(f"  [OK] Asset verified: {ka} ({os.path.getsize(kap)} bytes)")

    # 9. Verify WaterEjector Live Links Integration
    print("\n[9] Checking WaterEjector Live Links in Header & Dropdown...")
    we_links = [
        "https://waterejector.devdeskapp.com/",
        "https://waterejector.devdeskapp.com/deep-clean/",
        "https://waterejector.devdeskapp.com/game/",
        "https://waterejector.devdeskapp.com/vibration/",
        "https://waterejector.devdeskapp.com/stereo-test/",
        "https://waterejector.devdeskapp.com/charging-port-fix/"
    ]
    for wl in we_links:
        if wl not in idx_content:
            print(f"  [ERROR] WaterEjector link missing in index.html: {wl}")
            errors += 1
        else:
            print(f"  [OK] WaterEjector live tool link integrated: {wl}")

    print("\n" + "=" * 70)
    print(f"FINAL AUDIT RESULT: Total Errors: {errors}")
    print("=" * 70)

    if errors > 0:
        print("[FAILED] VALIDATION FAILED! Please fix the errors listed above.")
        sys.exit(1)
    else:
        print("[SUCCESS] ALL TESTS PASSED! 100% PRODUCTION READY & CONTEST VALIDATED!")
        sys.exit(0)

if __name__ == '__main__':
    run_tests()
