import os
import requests

ENA_API_URL = "https://" + "api-degalukainos.ena" + ".lt/api/v1/read/prices/latest"
ENA_WEB_URL = "https://" + "www.ena" + ".lt"

def isvalyti_savivaldybe(sav_pavadinimas, adresas):
    # Jei adresas prasideda miesto pavadinimu (pvz. "Alytus, Kauno g. 73"), paimame jį
    if adresas and "," in adresas:
        pirmas_zodis = adresas.split(",")[0].strip()
        if len(pirmas_zodis) > 2 and not any(c.isdigit() for c in pirmas_zodis):
            return pirmas_zodis
    # Kitu atveju sutvarkome savivaldybės pavadinimą
    s = (sav_pavadinimas or "").replace(" m. sav.", "").replace(" r. sav.", " r.").strip()
    return s

def surinkti_visas_degalines_tiesiogiai(dabar_str):
    token = os.environ.get("ENA_API_TOKEN")
    if not token:
        print("KLAIDA: Nerastas ENA_API_TOKEN raktas!")
        return []

    headers = {
        "Authorization": token if token.startswith("Bearer ") else f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(ENA_API_URL, headers=headers, timeout=25)
        res.raise_for_status()
        visi_irasai = res.json().get("data", [])
        print(f"Gauta {len(visi_irasai)} oficialių kainų įrašų iš ENA.lt API.")
    except Exception as e:
        print("Klaida jungiantis prie ENA.lt API:", e)
        return []

    # Sugrupuojame atskirus kuro įrašus (95, 98, dyzelinas) į vieną konkrečią degalinę
    degalines_map = {}

    for item in visi_irasai:
        tinklas = (item.get("gas_station_name") or item.get("company_name") or "").strip()
        adresas = (item.get("address") or "").strip()
        savivaldybe = item.get("municipality") or ""
        kuro_rusis = (item.get("fuel_type") or "").lower()
        laikas = item.get("submitted_at") or dabar_str
        
        try:
            kaina = round(float(item.get("price")), 3)
        except (TypeError, ValueError):
            continue

        if not tinklas or not adresas or kaina <= 0:
            continue

        raktas = f"{tinklas.lower()}_{adresas.lower()}"
        if raktas not in degalines_map:
            degalines_map[raktas] = {
                "network": tinklas,
                "logo_url": item.get("logo_url") or "",
                "city": isvalyti_savivaldybe(savivaldybe, adresas),
                "address": adresas,
                "a95": None,
                "a98": None,
                "diesel": None,
                "time": laikas,
                "source": "Lietuvos energetikos agentūra (ena.lt)",
                "source_url": ENA_WEB_URL
            }

        if "95" in kuro_rusis:
            degalines_map[raktas]["a95"] = kaina
        elif "98" in kuro_rusis:
            degalines_map[raktas]["a98"] = kaina
        elif "dyzel" in kuro_rusis:
            degalines_map[raktas]["diesel"] = kaina

        # Išsaugome naujausią pateikimo laiką
        if laikas > degalines_map[raktas]["time"]:
            degalines_map[raktas]["time"] = laikas

    rezultatas = list(degalines_map.values())
    print(f"Sugrupuota į {len(rezultatas)} unikalių Lietuvos degalinių!")
    return rezultatas
