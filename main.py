import re
import json
import time
from datetime import datetime
from scraper import surinkti_visos_lietuvos_paketus
from analyzer import istraukti_paketo_degalines, sugeneruoti_santraukas
from seo import generuoti_kuro_seo

def suvienodinti_tinkla(pavadinimas):
    p = pavadinimas.strip()
    zemas = p.lower()
    if "circle" in zemas: return "Circle K"
    if "neste" in zemas: return "Neste"
    if "viada" in zemas: return "Viada"
    if "baltic" in zemas: return "Baltic Petroleum"
    if "jozita" in zemas: return "Jozita"
    if "orlen" in zemas: return "Orlen"
    if "emsi" in zemas: return "Emsi"
    if "alau" in zemas: return "Alauša"
    if "saurida" in zemas: return "Saurida"
    if "stateta" in zemas: return "Stateta"
    return p.title()

def sukurti_tinklo_id(pavadinimas):
    p = pavadinimas.lower().strip()
    lt = {'ą': 'a', 'č': 'c', 'ę': 'e', 'ė': 'e', 'į': 'i', 'š': 's', 'ų': 'u', 'ū': 'u', 'ž': 'z'}
    for k, v in lt.items():
        p = p.replace(k, v)
    return re.sub(r'[^a-z0-9]+', '-', p).strip('-')

def paleisti_kainu_atnaujinima():
    dabar = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{dabar}] Pradedamas visos Lietuvos (miestų ir rajonų) degalinių kainų surinkimas...")

    with open("prices.json", "r", encoding="utf-8") as f:
        seni_duomenys = json.load(f)

    paketai = surinkti_visos_lietuvos_paketus()
    print(f"Suformuoti {len(paketai)} duomenų paketai iš visos Lietuvos.")

    visos_naujos_degalines = []
    for i, paketas in enumerate(paketai, 1):
        print(f"Analizuojamas paketas {i}/{len(paketai)}...")
        try:
            rastos = istraukti_paketo_degalines(i, paketas, dabar)
            visos_naujos_degalines.extend(rastos)
            print(f"  -> Pakete #{i} rasta {len(rastos)} degalinių.")
        except Exception as e:
            print(f"  -> Klaida pakete #{i}: {e}")
        time.sleep(15)

    # Sugrupuojame visas rastas degalines pagal suvienodintus tinklus
    tinklai_dict = {}
    for net in seni_duomenys.get("networks", []):
        tinklai_dict[net["id"]] = net

    atnaujinti_tinklu_id = set()
    for st in visos_naujos_degalines:
        raw_name = st.get("network", "").strip()
        if not raw_name:
            continue
        net_name = suvienodinti_tinkla(raw_name)
        net_id = sukurti_tinklo_id(net_name)
        
        if net_id not in atnaujinti_tinklu_id:
            tinklai_dict[net_id] = {
                "id": net_id,
                "name": net_name,
                "best_a95": None,
                "best_a98": None,
                "best_diesel": None,
                "price_time": dabar,
                "source_name": "Fuelo.net",
                "source_url": "https://" + "lt.fuelo" + ".net/?lang=lt",
                "stations": []
            }
            atnaujinti_tinklu_id.add(net_id)
        
        tinklai_dict[net_id]["stations"].append({
            "city": st.get("city", ""),
            "address": st.get("address", ""),
            "a95": st.get("a95"),
            "a98": st.get("a98"),
            "diesel": st.get("diesel"),
            "time": st.get("time", dabar),
            "source": st.get("source", "Fuelo.net")
        })

    # Apskaičiuojame mažiausias kainas kiekvienam tinklui
    atnaujinti_tinklai = []
    for net_id, net in tinklai_dict.items():
        stations = net.get("stations", [])
        a95_kainos = [s["a95"] for s in stations if isinstance(s.get("a95"), (int, float)) and s["a95"] > 0]
        a98_kainos = [s["a98"] for s in stations if isinstance(s.get("a98"), (int, float)) and s["a98"] > 0]
        dz_kainos = [s["diesel"] for s in stations if isinstance(s.get("diesel"), (int, float)) and s["diesel"] > 0]

        if a95_kainos:
            net["best_a95"] = min(a95_kainos)
        if a98_kainos:
            net["best_a98"] = min(a98_kainos)
        if dz_kainos:
            net["best_diesel"] = min(dz_kainos)
        
        if stations:
            net["price_time"] = stations[0].get("time", dabar)
        atnaujinti_tinklai.append(net)

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
    print(f"Visi tinklai ({len(atnaujinti_tinklai)}) ir SEO puslapiai sėkmingai atnaujinti!")

if __name__ == "__main__":
    paleisti_kainu_atnaujinima()
