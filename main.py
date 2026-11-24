import json
from datetime import datetime
from scraper import surinkti_kainu_duomenis
from analyzer import analizuoti_kainas
from seo import generuoti_kuro_seo

def paleisti_kainu_atnaujinima():
    dabar = datetime.now().strftime("%Y-%m-%d %H:%M")
    siandien = datetime.now().strftime("%Y-%m-%d")
    print(f"[{dabar}] Pradedamas kuro kainų atnaujinimas...")

    with open("prices.json", "r", encoding="utf-8") as f:
        seni_duomenys = json.load(f)

    surinkti_duomenys = surinkti_kainu_duomenis(siandien)
    print(f"Surinkta {len(surinkti_duomenys)} simbolių iš šaltinių.")

    atnaujinti_duomenys = analizuoti_kainas(surinkti_duomenys, seni_duomenys, dabar)
    atnaujinti_duomenys["last_updated"] = dabar

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(atnaujinti_duomenys, f, ensure_ascii=False, indent=2)

    generuoti_kuro_seo(atnaujinti_duomenys)
    print("Sėkmingai atnaujintas prices.json ir sugeneruoti SEO puslapiai!")

if __name__ == "__main__":
    paleisti_kainu_atnaujinima()
