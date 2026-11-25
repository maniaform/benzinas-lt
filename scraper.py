import os
import time
import requests

def surinkti_visos_lietuvos_paketus():
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_key:
        print("KLAIDA: Nerastas TAVILY_API_KEY!")
        return []

    url = "https://" + "api.tavily" + ".com/search"
    
    uzklausos = [
        "site:lt.fuelo.net/city/ benzinas dyzelinas kainos Vilnius Kaunas Klaipeda",
        "site:lt.fuelo.net/city/ benzinas dyzelinas kainos Siauliai Panevezys Alytus Marijampole Utena",
        "site:lt.fuelo.net/gasstation/ Viada Neste Circle K Jozita Orlen Baltic Petroleum",
        "site:pricer.lt degalu kainos Lietuvoje apzvalga benzinas dyzelinas",
        "degalu kainos Lietuvoje 15min delfi lrt benzinas dyzelinas Circle K Neste Viada Jozita"
    ]

    visi_tekstai = []
    for q in uzklausos:
        print(f"Ieškoma per Tavily: {q}...")
        payload = {
            "api_key": tavily_key,
            "query": q,
            "search_depth": "advanced",
            "include_raw_content": True,
            "max_results": 6
        }
        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.ok:
                rezultatai = res.json().get("results", [])
                for r in rezultatai:
                    puslapio_url = r.get("url", "")
                    # Atmetame tuščius titulinius puslapius, jei yra gilesnių nuorodų
                    if puslapio_url.rstrip("/") in ["https://fuelo.net", "https://pricer.lt"]:
                        continue
                    turinys = r.get("raw_content") or r.get("content") or ""
                    if turinys:
                        svarus = " ".join(turinys.split())[:3500]
                        visi_tekstai.append(f"=== ŠALTINIO PAVADINIMAS: {r.get('title')} ===\n=== TIKSLUS ŠALTINIO URL: {puslapio_url} ===\n{svarus}")
        except Exception as e:
            print("Tavily paieškos klaida:", e)
        time.sleep(1)

    print(f"Surinkta {len(visi_tekstai)} giliųjų šaltinių puslapių.")

    paketai = []
    dabartinis_paketas = ""
    for t in visi_tekstai:
        if len(dabartinis_paketas) + len(t) > 8500:
            paketai.append(dabartinis_paketas)
            dabartinis_paketas = t + "\n\n"
        else:
            dabartinis_paketas += t + "\n\n"
    if dabartinis_paketas:
        paketai.append(dabartinis_paketas)

    return paketai
