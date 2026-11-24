import os
import json
import time
import requests

GROQ_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://" + "api.groq" + ".com/openai/v1/chat/completions"

def siusti_groq(promptas, max_tokens=3000):
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": promptas}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "max_tokens": max_tokens
    }
    
    for bandymas in range(2):
        atsakas = requests.post(GROQ_URL, headers=headers, json=payload, timeout=45)
        if atsakas.status_code == 429 and bandymas == 0:
            print("  -> Pasiektas Groq limitas, laukiame 25 sek. ir kartojame...")
            time.sleep(25)
            continue
        if not atsakas.ok:
            print("Groq klaidos detalės:", atsakas.text)
        atsakas.raise_for_status()
        return json.loads(atsakas.json()["choices"]["message"]["content"])

def analizuoti_viena_tinkla(tinklas_info, surinktas_tekstas, senas_tinklas, dabar_str):
    promptas = f"""Tu esi tikslus Lietuvos degalų rinkos duomenų analitikas. Dabartinis laikas: {dabar_str}.
Analizuoji TIK VIENĄ degalinių tinklą: **{tinklas_info['name']}** (id: "{tinklas_info['id']}").

UŽDUOTIS:
Iš pateiktų šaltinių ištrauk VISAS minimas **{tinklas_info['name']}** degalines visoje Lietuvoje (Vilnius, Kaunas, Klaipėda, Šiauliai, Panevėžys, Alytus, Marijampolė, Utena, Telšiai, Tauragė, rajonai) ir jų A95, A98 benzino bei Dyzelino kainas.

GRIEŽTOS TAISYKLĖS:
1. JOKIŲ HALIUCINACIJŲ: Naudok TIK realius skaičius ir adresus iš šaltinių. Jei kuriai nors degalinei kaina nenurodyta, įrašyk null.
2. Nustatyk mažiausią rastą tinklo kainą ("best_a95", "best_a98", "best_diesel"). Jei naujų kainų šaltiniuose neradai – palik senus skaičius iš SENŲ TINKLO DUOMENŲ.
3. Įrašyk tikslų kainos fiksavimo laiką ("price_time") ir šaltinio nuorodą ("source_url", "source_name").
4. Į sąrašą "stations" sudėk VISAS rastas šio tinklo degalines (iki 40 degalinių), sujungdamas naujas su senomis, kad sąrašas būtų kuo išsamesnis.

SENI TINKLO DUOMENYS:
{json.dumps(senas_tinklas, ensure_ascii=False)}

NAUJI SURINKTI ŠALTINIAI ŠIAM TINKLUI:
{surinktas_tekstas}

Grąžink TIK gryną JSON objektą su raktais: "id", "name", "best_a95", "best_a98", "best_diesel", "price_time", "source_name", "source_url", "stations" (kiekvienas elementas: "city", "address", "a95", "a98", "diesel", "time", "source")."""

    return siusti_groq(promptas, max_tokens=3200)

def sugeneruoti_santraukas(tinklai_sarasas, dabar_str):
    trumpas_vaizdas = [
        {"name": t["name"], "a95": t.get("best_a95"), "a98": t.get("best_a98"), "diesel": t.get("best_diesel")}
        for t in tinklai_sarasas
    ]
    promptas = f"""Remdamasis šiais šiandienos ({dabar_str}) degalų kainų duomenimis Lietuvoje:
{json.dumps(trumpas_vaizdas, ensure_ascii=False)}

Parašyk dvi trumpas (1–2 sakinių), aiškias apžvalgas vairuotojams lietuvių kalba:
1. "summary_petrol" – apie benzino (A95 ir A98) mažiausias kainas ir kur jos fiksuojamos.
2. "summary_diesel" – apie dyzelino mažiausias kainas ir bendrą situaciją.

Grąžink TIK gryną JSON objektą be jokio papildomo teksto su raktais "summary_petrol" ir "summary_diesel"."""
    return siusti_groq(promptas, max_tokens=350)
