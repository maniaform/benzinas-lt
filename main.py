import time
import json
from datetime import datetime
from scraper import TINKLAI, surinkti_tinklo_duomenis
from analyzer import analizuoti_viena_tinkla, sugeneruoti_santraukas
from seo import generuoti_kuro_seo

def paleisti_kainu_atnaujinima():
    dabar = datetime.now().strftime("%Y-%m-%d %H:%M")
    siandien = datetime.now().strftime("%Y-%m-%d")
    print(f"[{dabar}] Pradedamas išsamus visų tinklų kuro kainų atnaujinimas...")

    with open("prices.json", "r", encoding="utf-8") as f:
        seni_duomenys = json.load(f)

    seni_pagal_id = {t["id"]: t for t in seni_duomenys.get("networks", [])}
    atnaujinti_tinklai = []

    for tinklas in TINKLAI:
        print(f"Renkami duomenys tinklui: {tinklas['name']}...")
        tekstas = surinkti_tinklo_duomenis(tinklas, siandien)
        senas_tinklas = seni_pagal_id.get(tinklas["id"], {
            "id": tinklas["id"],
            "name": tinklas["name"],
            "best_a95": None,
            "best_a98": None,
            "best_diesel": None,
            "price_time": dabar,
            "source_name": "Fuelo.net",
            "source_url": "https://fuelo.net",
            "stations": []
        })
        
        try:
            rezultatas = analizuoti_viena_tinkla(tinklas, tekstas, senas_tinklas, dabar)
            atnaujinti_tinklai.append(rezultatas)
            print(f"  -> {tinklas['name']}: rasta {len(rezultatas.get('stations', []))} degalinių.")
        except Exception as e:
            print(f"  -> Klaida analizuojant {tinklas['name']}, paliekami seni duomenys: {e}")
            atnaujinti_tinklai.append(senas_tinklas)
            time.sleep(8)

    santraukos = sugeneruoti_santraukas(atnaujinti_tinklai, dabar)

    galutinis = {
        "last_updated": dabar,
        "summary_petrol": santraukos.get("summary_petrol", seni_duomenys.get("summary_petrol", "")),
        "summary_diesel": santraukos.get("summary_diesel", seni_duomenys.get("summary_diesel", "")),
        "networks": atnaujinti_tinklai
    }

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(galutinis, f, ensure_ascii=False, indent=2)

    generuoti_kuro_seo(galutinis)
    print("Visi tinklai ir SEO puslapiai sėkmingai atnaujinti!")

if __name__ == "__main__":
    paleisti_kainu_atnaujinima()
