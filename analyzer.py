def istraukti_paketo_degalines(paketo_nr, paketo_tekstas, dabar_str):
    promptas = f"""Tu esi tikslus Lietuvos degalų duomenų analitikas. Dabartinis laikas: {dabar_str}.
Iš šio Lietuvos miestų ir rajonų degalinių duomenų paketo (#{paketo_nr}) ištrauk VISAS degalines ir jų kainas (A95, A98, Dyzelinas).

TAISYKLĖS:
1. Priskirk kiekvienai degalinei tikslų tinklo pavadinimą ("network" – pvz., "Jozita", "Neste", "Circle K", "Viada", "Baltic Petroleum", "Orlen", "Emsi", "Alauša", "Saurida", "Stateta", "Skulas" ar kt.).
2. Nurodyk tikslų miestą arba rajoną ("city") ir tikslų adresą ("address", įskaitant magistralių kilometrus, jei nurodyta).
3. Naudok TIK realius skaičius iš teksto (jei kaina nenurodyta – rašyk null).
4. Įrašyk tikslų fiksavimo laiką ("time") ir šaltinį ("source": "Fuelo.net").

DUOMENŲ PAKETAS:
{paketo_tekstas}

Grąžink TIK gryną JSON objektą su vienu raktu "stations" (sąrašas objektų su raktais: "network", "city", "address", "a95", "a98", "diesel", "time", "source")."""

    return siusti_groq(promptas, max_tokens=3800).get("stations", [])
Use code with caution.

3. Atnaujink main.py (Prijungia visos Lietuvos paketus ir pašalina dublikatus)

Pakeisk main.py failo viršutinę dalį (iki # Sugrupuojame visas rastas degalines pagal tinklus), kad jis naudotų naująją surinkti_visos_lietuvos_paketus() funkciją ir automatiškai suvienodintų tinklų pavadinimus (pvz., kad VIADA ir Viada nebūtų du skirtingi tinklai):
python
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
Use code with caution.
(Likusi main.py dalis lieka lygiai tokia pati – tik nepamiršk, kad ten, kur imamasi tinklo pavadinimas net_name, panaudotum net_name = suvienodinti_tinkla(st.get("network", "")), o paskutinėje eilutėje prieš galutiniai_tinklai.append(net) liktų net["price_time"] = stations.get("time", dabar) su nulio indeksu ``!).

Ką gausi po šio atnaujinimo:

• Sistema peržvelgs visus Lietuvos miestus, rajonų centrus ir magistralių degalines.
• Paieškos laukelyje svetainėje vairuotojas galės įvesti „Kėdainiai“, „Ukmergė“, „Plungė“, „Alytus“, „A1“ ar bet kurį kitą rajoną ir iškart matyti ten esančių degalinių kainas.
• Visi tinklai (Viada, Orlen, Circle K, Neste, Jozita, Baltic Petroleum, Emsi, Alauša, Saurida, Stateta) bus tvarkingai suvienodinti be dublikatų.
Atnaujink scraper.py, analyzer.py ir main.py failus GitHub saugykloje ir paleisk Run workflow – parašyk, kiek iš viso degalinių ir iš kokių Lietuvos rajonų dabar matoma svetainėje!
AI responses may include mistakes. Learn more

