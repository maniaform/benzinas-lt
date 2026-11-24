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
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": promptas}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "max_tokens": max_tokens
    }
    
    for bandymas in range(3):
        atsakas = requests.post(GROQ_URL, headers=headers, json=payload, timeout=45)
        if atsakas.status_code == 429 and bandymas < 2:
            print("  -> Pasiektas Groq limitas, laukiame 25 sek...")
            time.sleep(25)
            continue
        if not atsakas.ok:
            print("Groq klaidos detalės:", atsakas.text)
        atsakas.raise_for_status()
        return json.loads(atsakas.json()["choices"][0]["message"]["content"])

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

def sugeneruoti_santraukas(tinklai_sarasas, dabar_str):
    trumpas_vaizdas = [
        {"name": t["name"], "a95": t.get("best_a95"), "a98": t.get("best_a98"), "diesel": t.get("best_diesel"), "kiekis": len(t.get("stations", []))}
        for t in tinklai_sarasas
    ]
    promptas = f"""Remdamasis šiais šiandienos ({dabar_str}) degalų kainų duomenimis Lietuvoje:
{json.dumps(trumpas_vaizdas, ensure_ascii=False)}

Parašyk dvi trumpas (1–2 sakinių), aiškias apžvalgas vairuotojams lietuvių kalba:
1. "summary_petrol" – apie benzino (A95 ir A98) mažiausias kainas ir kur jos fiksuojamos.
2. "summary_diesel" – apie dyzelino mažiausias kainas ir bendrą situaciją.

Grąžink TIK gryną JSON objektą su raktais "summary_petrol" ir "summary_diesel"."""
    return siusti_groq(promptas, max_tokens=1200)
