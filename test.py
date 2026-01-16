from playwright.sync_api import sync_playwright, TimeoutError
import json
import os
from utils import normalize_for_url, safe_filename
from datetime import datetime, timezone

DATA_FILE = "data/all_countries.json"
OUTPUT_DIR = "data/countries"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    all_countries = json.load(f)

countries = all_countries["countries"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for country in countries:
        name = country["name"]
        url = country["url"]

        print(f"\n🌍 Processando {name}...")

        try:
            page.goto(url, timeout=60000)
            page.wait_for_selector("h3", timeout=15000)

            steps = page.query_selector_all("h3")

            data = {
                "country": name,
                "url": url,
                "schema_version": "1.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "steps": []
            }

            for step in steps:
                step_id = step.get_attribute("id")
                title = step.inner_text().strip()

                container = step.evaluate_handle("el => el.nextElementSibling")
                container = container.as_element()

                if not container:
                    continue

                items = container.query_selector_all("div[id]")

                step_data = {
                    "id": step_id,
                    "title": title,
                    "items": []
                }

                for item in items:
                    item_id = item.get_attribute("id")

                    img = item.query_selector("img")
                    image = img.get_attribute("src") if img else None

                    paragraphs = item.query_selector_all("p")

                    text = ""
                    note = None

                    for p in paragraphs:
                        cls = p.get_attribute("class") or ""
                        if "note" in cls:
                            note = p.inner_text().replace("NOTE:", "").strip()
                        else:
                            text += p.inner_text().strip() + " "

                    step_data["items"].append({
                        "id": item_id,
                        "image": image,
                        "text": text.strip(),
                        "note": note
                    })

                data["steps"].append(step_data)

            file_name = safe_filename(normalize_for_url(name))
            file_path = f"{OUTPUT_DIR}/{file_name}.json"

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✅ Salvo em {file_path}")

        except TimeoutError:
            print(f"⏭️ Pulando {name} (conteúdo não encontrado)")
        except Exception as e:
            print(f"❌ Erro ao processar {name}: {e}")

    browser.close()
print(f"\n🎉 Processo concluído. Dados salvos em {OUTPUT_DIR}/")