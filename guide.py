from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
import json
import os
from utils import normalize_for_url

URL = "https://www.plonkit.net/guide"

countries_data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)

    page.wait_for_selector("tr")

    rows = page.query_selector_all("tr")

    for row in rows:
        cells = row.query_selector_all("td")

        if len(cells) >= 4:
            name = cells[1].inner_text().strip()
            code = cells[2].inner_text().strip()
            date = cells[3].inner_text().strip()

            countries_data.append({
                "name": name,
                "code": code,
                "date": date,
                "url": f"https://www.plonkit.net/{normalize_for_url(name)}"
            })

    browser.close()

all_countries = {
    "source": "https://www.plonkit.net",
    "schema_version": "1.0",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "total_countries": len(countries_data),
    "countries": countries_data
}

os.makedirs("data", exist_ok=True)

with open("data/all_countries.json", "w", encoding="utf-8") as f:
    json.dump(all_countries, f, indent=2, ensure_ascii=False)

print(f"✅ {len(countries_data)} countries saved to data/all_countries.json")
