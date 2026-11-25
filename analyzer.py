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
    modeliai = ["qwen/qwen3.8-27b", "llama-3.1-8b-instant", "openai/gpt-oss-120b"]
    
    for modelis in modeliai:
        payload = {
            "model": modelis,
            "messages": [{"role": "user", "content": promptas}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens
        }
        atsakas = requests.post(GROQ_URL, headers=headers, json=payload, timeout=45)
        if atsakas.status_code == 429:
            print(f"  -> Modelis {modelis} pasiekė limitą, bandomas kitas modelis...")
            time.sleep(3)
            continue
        if not atsakas.ok:
            print(f"Groq klaida ({modelis}):", atsakas.text)
            continue
        return json.loads(atsakas.json()["choices"][0]["message"]["content"])
        
    raise Exception("Visi Groq modeliai laikinai pasiekė limitus.")

def istraukti_paketo_degalines(paketo_nr, paketo_tekstas, dabar_str):
    promptas = f"""Tu esi tikslus Lietuvos degalų duomenų analitikas. Dabartinis laikas: {dabar_str}.
Iš šio Lietuvos degalinių duomenų paketo (#{paketo_nr}) ištrauk VISAS minimas degalines ir jų kainas (A95, A98, Dyzelinas).

TAISYKLĖS:
1. Priskirk kiekvienai degalinei tikslų tinklo pavadinimą ("network" – pvz., "Jozita", "Neste", "Circle K", "Viada", "Baltic Petroleum", "Orlen", "Emsi", "Alauša", "Saurida", "Stateta").
2. Nurodyk tikslų miestą arba rajoną ("city") ir tikslų adresą ("address").
3. Naudok TIK realius skaičius iš teksto (jei kaina nenurodyta – rašyk null).
4. KRITIŠKAI SVARBU DĖL ŠALTINIŲ: Kiekvienai degalinei įrašyk TIKSLŲ šaltinio puslapio URL adresą ("source_url") iš antraštės "=== TIKSLUS ŠALTINIO URL: ... ===" (pvz., tikslų miesto puslapio arba straipsnio adresą su keliu po domeno), o ne bendrą titulinį puslapį! Taip pat įrašyk trumpą šaltinio pavadinimą ("source", pvz., "Fuelo.net (Vilnius)", "Pricer.lt apžvalga", "15min.lt").

DUOMENŲ PAKETAS:
{paketo_tekstas}

Grąžink TIK gryną JSON objektą su vienu raktu "stations" (sąrašas objektų su raktais: "network", "city", "address", "a95", "a98", "diesel", "time", "source", "source_url")."""

    return siusti_groq(promptas, max_tokens=3800).get("stations", [])

def sugeneruoti_santraukas(tinklai_sarasas, dabar_str):
    trumpas_vaizdas = [
        {"name": t["name"], "a95": t.get("best_a95"), "a98": t.get("best_a98"), "diesel": t.get("best_diesel")}
        for t in tinklai_sarasas
        if t.get("best_a95") or t.get("best_diesel")
    ]
    promptas = f"""Remdamasis šiais šiandienos ({dabar_str}) degalų kainų duomenimis Lietuvoje:
{json.dumps(trumpas_vaizdas, ensure_ascii=False)}

Parašyk dvi trumpas (1–2 sakinių), aiškias apžvalgas vairuotojams lietuvių kalba:
1. "summary_petrol" – apie benzino mažiausias kainas ir kur jos fiksuojamos.
2. "summary_diesel" – apie dyzelino mažiausias kainas ir bendrą situaciją.

GRIEŽTA TAISYKLĖ: Niekada nerašyk programavimo terminų („null“, „None“, „duomenyse nenurodyta“). Jei kurios nors kuro rūšies (pvz., A98) skaičiaus nėra, tiesiog jos neminėk ir rašyk tik apie A95 benziną!

Grąžink TIK gryną JSON objektą su raktais "summary_petrol" ir "summary_diesel"."""
    return siusti_groq(promptas, max_tokens=1200)
