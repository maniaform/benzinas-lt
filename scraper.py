import re
import time
import requests

BASE_FUELO = "https://" + "lt.fuelo" + ".net"

def isvalyti_html(html_tekstas):
    tekstas = re.sub(r'<(script|style).*?>.*?</\1>', ' ', html_tekstas, flags=re.DOTALL)
    tekstas = re.sub(r'<[^>]+>', ' ', tekstas)
    tekstas = re.sub(r'\s+', ' ', tekstas).strip()
    return tekstas

def gauti_visas_lietuvos_vietoves():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    vietoves = set()
    try:
        res = requests.get(f"{BASE_FUELO}/?lang=lt", headers=headers, timeout=15)
        if res.ok:
            # Ištraukiame visas nuorodas į miestus ir rajonus (/city/...)
            rastos = re.findall(r'/city/([a-zA-Z0-9_-]+)', res.text)
            for v in rastos:
                vietoves.add(v)
    except Exception as e:
        print("Klaida renkant vietovių sąrašą:", e)

    # Pridedame ir svarbiausius rajonų centrus, jei jų nebuvo pagrindiniame sąraše
    papildomi_rajonai = [
        "Vilnius", "Kaunas", "Klaipeda", "Siauliai", "Panevezys", "Alytus", "Marijampole",
        "Mazeikiai", "Jonava", "Utena", "Kedainiai", "Telsiai", "Visaginas", "Taurage",
        "Ukmerge", "Plunge", "Silute", "Kretinga", "Radviliskis", "Druskininkai", "Palanga",
        "Raseiniai", "Elektrenai", "Jurbarkas", "Garliava", "Kursenai", "Birzai", "Vilkaviskis",
        "Garzdzai", "Rokiskis", "Anyksciai", "Prienu", "Varena", "Kaisiadorys", "Pasvalys",
        "Kupiskis", "Zarasai", "Siauliu-rajonas", "Kauno-rajonas", "Vilniaus-rajonas", "Klaipedos-rajonas"
    ]
    for r in papildomi_rajonai:
        vietoves.add(r)

    return sorted(list(vietoves))

def surinkti_visos_lietuvos_paketus():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    vietoves = gauti_visas_lietuvos_vietoves()
    print(f"Iš viso rasta {len(vietoves)} Lietuvos miestų ir rajonų patikrai.")

    visi_tekstai = []
    for v in vietoves:
        url = f"{BASE_FUELO}/city/{v}?lang=lt"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.ok and "A95" in res.text:
                svarus = isvalyti_html(res.text)
                # Paimame tik aktualią lentelės dalį (be puslapio meniu ir poraštės)
                pradzia = svarus.find("Degalinė") if "Degalinė" in svarus else 0
                fragmentas = svarus[pradzia:pradzia + 2200]
                visi_tekstai.append(f"[{v}]: {fragmentas}")
        except Exception:
            continue
        time.sleep(0.3)

    # Sugrupuojame surinktus rajonus į paketus po ~8500 simbolių, kad tilptų į DI langą
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
    
