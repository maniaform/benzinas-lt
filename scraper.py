import os
import re
import time
import requests

TINKLAI = [
    {"id": "jozita", "name": "Jozita", "fuelo_slug": "Jozita"},
    {"id": "neste", "name": "Neste", "fuelo_slug": "Neste"},
    {"id": "circle-k", "name": "Circle K", "fuelo_slug": "Circle-K"},
    {"id": "viada", "name": "Viada", "fuelo_slug": "Viada"},
    {"id": "baltic-petroleum", "name": "Baltic Petroleum", "fuelo_slug": "Baltic-Petroleum"},
    {"id": "orlen", "name": "Orlen", "fuelo_slug": "Orlen"},
    {"id": "emsi", "name": "Emsi", "fuelo_slug": "Emsi"},
    {"id": "alausa", "name": "Alauša", "fuelo_slug": "Alausa"}
]

def isvalyti_html(html_tekstas):
    tekstas = re.sub(r'<(script|style).*?>.*?</\1>', ' ', html_tekstas, flags=re.DOTALL)
    tekstas = re.sub(r'<[^>]+>', ' ', tekstas)
    tekstas = re.sub(r'\s+', ' ', tekstas).strip()
    return tekstas[:9000]

def surinkti_tinklo_duomenis(tinklas, siandien_str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    saltiniai_tekstas = []
    
    # 1. Tiesioginis tinklo puslapis Fuelo.net (apima visus Lietuvos miestus!)
    fuelo_url = "https://" + "lt.fuelo" + f".net/brand/{tinklas['fuelo_slug']}?lang=lt"
    try:
        res = requests.get(fuelo_url, headers=headers, timeout=15)
        if res.ok and len(res.text) > 1000:
            svarus = isvalyti_html(res.text)
            saltiniai_tekstas.append(f"=== TIESIOGINIS ŠALTINIS: Fuelo.net ({fuelo_url}) ===\n{svarus}\n")
    except Exception as e:
        print(f"Fuelo klaida tinklui {tinklas['name']}: {e}")

    # 2. Tikslinė Tavily paieška būtent šiam tinklui
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if tavily_key:
        tavily_url = "https://" + "api.tavily" + ".com/search"
        payload = {
            "api_key": tavily_key,
            "query": f"{tinklas['name']} degalines kuro kainos benzinas dyzelinas Lietuvoje {siandien_str}",
            "search_depth": "basic",
            "max_results": 4
        }
        try:
            res = requests.post(tavily_url, json=payload, timeout=15)
            if res.ok:
                rezultatai = res.json().get("results", [])
                paieskos_str = "\n".join([f"- {r['title']} (URL: {r['url']}): {r['content']}" for r in rezultatai])
                saltiniai_tekstas.append(f"=== PAIEŠKOS REZULTATAI ===\n{paieskos_str}")
        except Exception:
            pass

    time.sleep(1)
    return "\n".join(saltiniai_tekstas)
    
