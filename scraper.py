import os
import re
import requests

def isvalyti_html(html_tekstas):
    # Pašaliname script ir style blokus bei HTML žymes
    tekstas = re.sub(r'<(script|style).*?>.*?</\1>', ' ', html_tekstas, flags=re.DOTALL)
    tekstas = re.sub(r'<[^>]+>', ' ', tekstas)
    tekstas = re.sub(r'\s+', ' ', tekstas).strip()
    return tekstas[:12000]

def gauti_tiesioginius_puslapius():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    saltiniai = [
        ("Fuelo.net Lietuva", "https://" + "lt.fuelo" + ".net/?lang=lt"),
        ("Fuelo.net Vilnius", "https://" + "lt.fuelo" + ".net/city/Vilnius?lang=lt"),
        ("Fuelo.net Kaunas", "https://" + "lt.fuelo" + ".net/city/Kaunas?lang=lt")
    ]
    surinkta = []
    for pavadinimas, url in saltiniai:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.ok:
                svarus = isvalyti_html(res.text)
                surinkta.append(f"=== ŠALTINIS: {pavadinimas} ({url}) ===\n{svarus}\n")
        except Exception as e:
            print(f"Nepavyko nuskaityti {pavadinimas}: {e}")
    return "\n".join(surinkta)

def ieskoti_per_tavily(siandien_str):
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_key:
        return ""
    
    url = "https://" + "api.tavily" + ".com/search"
    payload = {
        "api_key": tavily_key,
        "query": f"degalu kainos benzinas 95 dyzelinas Lietuvoje Circle K Neste Viada Jozita {siandien_str}",
        "search_depth": "advanced",
        "max_results": 6
    }
    try:
        res = requests.post(url, json=payload, timeout=20)
        res.raise_for_status()
        rezultatai = res.json().get("results", [])
        return "\n".join([f"- {r['title']} (URL: {r['url']}): {r['content']}" for r in rezultatai])
    except Exception as e:
        print("Tavily paieškos klaida:", e)
        return ""

def surinkti_kainu_duomenis(siandien_str):
    tiesioginiai = gauti_tiesioginius_puslapius()
    paieska = ieskoti_per_tavily(siandien_str)
    return f"{tiesioginiai}\n\n=== NAUJAUSIOS APŽVALGOS IŠ PAIEŠKOS ===\n{paieska}"
