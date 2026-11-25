import re
import json
from datetime import datetime, timedelta
from scraper import surinkti_visas_degalines_tiesiogiai
from analyzer import sugeneruoti_santraukas
from seo import generuoti_kuro_seo

def suvienodinti_tinkla(pavadinimas):
    zemas = pavadinimas.strip().lower()
    if "circle" in zemas: return "Circle K"
    if "neste" in zemas: return "Neste"
    if "viada" in zemas or "lukoil" in zemas: return "Viada"
    if "baltic" in zemas: return "Baltic Petroleum"
    if "jozita" in zemas: return "Jozita"
    if "orlen" in zemas: return "Orlen"
    if "emsi" in zemas: return "Emsi"
    if "alau" in zemas: return "Alauša"
    if "saurida" in zemas: return "Saurida"
    if "stateta" in zemas: return "Stateta"
    if "skulas" in zemas: return "Skulas"
    if "ecoil" in zemas: return "Ecoil"
    if "kvistija" in zemas: return "Kvistija"
    return pavadinimas.strip().title()

def sukurti_tinklo_id(pavadinimas):
    p = pavadinimas.lower().strip()
    lt = {'ą': 'a', 'č': 'c', 'ę': 'e', 'ė': 'e', 'į': 'i', 'š': 's', 'ų': 'u', 'ū': 'u', 'ž': 'z'}
    for k, v in lt.items():
        p = p.replace(k, v)
    return re.sub(r'[^a-z0-9]+', '-', p).strip('-')

def normalizuoti_adresa(adr, miest):
    s = f"{adr} {miest}".lower()
    s = re.sub(r'[^a-z0-9ąčęėįšųūž]', '', s)
    return s[:22]

def paleisti_kainu_atnaujinima():
    dabar = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{dabar}] Pradedamas oficialių ENA.lt degalinių kainų surinkimas...")

    with open("prices.json", "r", encoding="utf-8") as f:
        seni_duomenys = json.load(f)

    visos_naujos_degalines = surinkti_visas_degalines_tiesiogiai(dabar)

    tinklai_dict = {}
    for net in seni_duomenys.get("networks", []):
        tinklai_dict[net["id"]] = net

    for st in visos_naujos_degalines:
        raw_name = (st.get("network") or "").strip()
        if not raw_name:
            continue
        net_name = suvienodinti_tinkla(raw_name)
        if not net_name:
            continue
        net_id = sukurti_tinklo_id(net_name)
        
        if net_id not in tinklai_dict:
            tinklai_dict[net_id] = {
                "id": net_id,
                "name": net_name,
                "best_a95": None,
                "best_a98": None,
                "best_diesel": None,
                "diff_a95": 0,
                "diff_a98": 0,
                "diff_diesel": 0,
                "price_time": dabar,
                "source_name": st.get("source") or "Lietuvos energetikos agentūra (ena.lt)",
                "source_url": st.get("source_url") or "https://" + "www.ena" + ".lt",
                "stations": [],
                "logo_url": ""
            }
        
        naujas_miestas = (st.get("city") or "").strip()
        naujas_adresas = (st.get("address") or "").strip()
        if not naujas_adresas:
            continue

        naujas_irasas = {
            "city": naujas_miestas,
            "address": naujas_adresas,
            "a95": st.get("a95"),
            "a98": st.get("a98"),
            "diesel": st.get("diesel"),
            "time": st.get("time") or dabar,
            "source": st.get("source") or "Lietuvos energetikos agentūra (ena.lt)",
            "source_url": st.get("source_url") or "https://" + "www.ena" + ".lt"
        }

        naujas_raktas = normalizuoti_adresa(naujas_adresas, naujas_miestas)
        rasta_sena = False
        for idx, esama in enumerate(tinklai_dict[net_id]["stations"]):
            esamas_raktas = normalizuoti_adresa(esama.get("address") or "", esama.get("city") or "")
            if esamas_raktas == naujas_raktas and esamas_raktas != "":
                tinklai_dict[net_id]["stations"][idx] = naujas_irasas
                rasta_sena = True
                break
        if not rasta_sena:
            tinklai_dict[net_id]["stations"].append(naujas_irasas)

        if st.get("source_url"):
            tinklai_dict[net_id]["source_url"] = st.get("source_url")
        if st.get("source"):
            tinklai_dict[net_id]["source_name"] = st.get("source")
        if st.get("logo_url"):
            tinklai_dict[net_id]["logo_url"] = st.get("logo_url")

    septynios_dienos_atgal = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    atnaujinti_tinklai = []
    for net_id, net in tinklai_dict.items():
        sviezios_stations = []
        for s in net.get("stations", []):
            laikas_str = str(s.get("time") or dabar)
            if laikas_str.startswith("202"):
                if laikas_str[:10] >= septynios_dienos_atgal:
                    sviezios_stations.append(s)
            else:
                sviezios_stations.append(s)
                
        net["stations"] = sviezios_stations
        stations = sviezios_stations

        sena_a95 = net.get("best_a95")
        sena_a98 = net.get("best_a98")
        sena_dz = net.get("best_diesel")

        a95_kainos = [s["a95"] for s in stations if isinstance(s.get("a95"), (int, float)) and s["a95"] > 0]
        a98_kainos = [s["a98"] for s in stations if isinstance(s.get("a98"), (int, float)) and s["a98"] > 0]
        dz_kainos = [s["diesel"] for s in stations if isinstance(s.get("diesel"), (int, float)) and s["diesel"] > 0]

        if a95_kainos:
            nauja_a95 = min(a95_kainos)
            net["diff_a95"] = round(nauja_a95 - sena_a95, 3) if isinstance(sena_a95, (int, float)) else 0
            net["best_a95"] = nauja_a95

        if a98_kainos:
            nauja_a98 = min(a98_kainos)
            net["diff_a98"] = round(nauja_a98 - sena_a98, 3) if isinstance(sena_a98, (int, float)) else 0
            net["best_a98"] = nauja_a98

        if dz_kainos:
            nauja_dz = min(dz_kainos)
            net["diff_diesel"] = round(nauja_dz - sena_dz, 3) if isinstance(sena_dz, (int, float)) else 0
            net["best_diesel"] = nauja_dz
        
        if stations:
            net["price_time"] = stations[0].get("time", dabar)
        atnaujinti_tinklai.append(net)

    try:
        santraukos = sugeneruoti_santraukas(atnaujinti_tinklai, dabar)
    except Exception as e:
        print("Nepavyko sugeneruoti naujos teksto santraukos, paliekama sena:", e)
        santraukos = {}

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

if __name__ == "__main__":
    paleisti_kainu_atnaujinima()
