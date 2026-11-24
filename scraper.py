import re
import time
import requests

BASE_FUELO = "https://" + "lt.fuelo" + ".net"

def isvalyti_html(html_tekstas):
    tekstas = re.sub(r'<(script|style).*?>.*?</\1>', ' ', html_tekstas, flags=re.DOTALL)
    tekstas = re.sub(r'<[^>]+>', ' ', tekstas)
    tekstas = re.sub(r'\s+', ' ', tekstas).strip()
    return tekstas

def surinkti_visos_lietuvos_paketus():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    nuorodos = set()
    
    # 1. Paimame pagrindinius Lietuvos puslapius ir ištraukiame visas tikras vietovių nuorodas
    pradiniai = [
        f"{BASE_FUELO}/?lang=lt",
        f"{BASE_FUELO}/fuel/gasoline?lang=lt",
        f"{BASE_FUELO}/fuel/diesel?lang=lt"
    ]
    
    visi_tekstai = []
    for p_url in pradiniai:
        try:
            res = requests.get(p_url, headers=headers, timeout=15)
            if res.ok:
                # Ištraukiame visas vidines miestų/rajonų nuorodas (/city/...)
                rasti_keliai = re.findall(r'href=["\'](/city/[^"\'\?]+)', res.text)
                for k in rasti_keliai:
                    nuorodos.add(f"{BASE_FUELO}{k}?lang=lt")
                
                svarus = isvalyti_html(res.text)
                visi_tekstai.append(f"[Lietuvos suvestinė]: {svarus[:6000]}")
        except Exception as e:
            print("Pradinės paieškos klaida:", e)

    print(f"Rastos {len(nuorodos)} tikros Lietuvos miestų ir rajonų nuorodos.")

    # 2. Nuskaitome visas atrastas miestų ir rajonų nuorodas
    for url in sorted(list(nuorodos)):
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.ok and ("95" in res.text or "Dyzelinas" in res.text):
                svarus = isvalyti_html(res.text)
                # Paimame tik duomenų lentelės dalį (be puslapio meniu)
                pradzia = svarus.find("Degalinė") if "Degalinė" in svarus else 300
                fragmentas = svarus[pradzia:pradzia + 2500]
                if len(fragmentas) > 100:
                    visi_tekstai.append(f"[{url}]: {fragmentas}")
        except Exception:
            continue
        time.sleep(0.25)

    # 3. Sugrupuojame į kompaktiškus paketus po ~8500 simbolių
    paketai = []
    dabartinis_paketas = ""
    for t in visi_tekstai:
        if len(dabartinis_paketas) + len(t) > 8500:
            paketai.append(dabartinis_paketas)
            dabartinis_paketas = t + "\n"
        else:
            dabartinis_paketas += t + "\n"
    if dabartinis_paketas:
        paketai.append(dabartinis_paketas)

    return paketai
    return paketai
    
