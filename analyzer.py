import os
import json
import requests

GROQ_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://" + "api.groq" + ".com/openai/v1/chat/completions"

def analizuoti_kainas(surinkti_duomenys, seni_duomenys, dabar_str):
    promptas = f"""Tu esi tikslus Lietuvos degalų rinkos duomenų analitikas. Dabartinis laikas: {dabar_str}.

Tavo užduotis – iš šių surinktų interneto šaltinių ištraukti naujausias žinomas A95, A98 benzino ir Dyzelino kainas pagrindiniuose Lietuvos degalinių tinkluose (Jozita, Neste, Baltic Petroleum, Circle K, Viada, Orlen).

GRIEŽTOS TAISYKLĖS:
1. JOKIŲ HALIUCINACIJŲ: Niekada neišsigalvok kainų ar adresų! Naudok TIK tai, kas parašyta žemiau pateiktuose šaltiniuose.
2. JEI TINKLUI NERADAI NAUJESNĖS KAINOS: Palik tiksliai tokią pačią kainą, laiką ("price_time") ir degalinių sąrašą, koks buvo senuose duomenyse!
3. JEI RADAI NAUJĄ KAINĄ: Atnaujink tinklo "best_a95", "best_a98" arba "best_diesel" (skaičius su 3 skaitmenimis po kablelio, pvz., 1.389), įrašyk tikslų fiksavimo laiką ("price_time") bei tikslų šaltinio pavadinimą ("source_name") ir jo nuorodą ("source_url").
4. Jei šaltiniuose yra konkrečių degalinių adresų su kainomis, įtrauk jas į to tinklo "stations" sąrašą.
5. Parašyk trumpą (1–2 sakinių) dienos apžvalgą benzinui ("summary_petrol") ir dyzelinui ("summary_diesel").

SENI DUOMENYS (atskaitos taškas):
{json.dumps(seni_duomenys, ensure_ascii=False)}

NAUJI SURINKTI ŠALTINIAI:
{surinkti_duomenys}

Grąžink TIK gryną JSON objektą su tokia pačia struktūra kaip SENI DUOMENYS ("last_updated", "summary_petrol", "summary_diesel", "networks")."""

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": promptas}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "max_tokens": 4000
    }

    atsakas = requests.post(GROQ_URL, headers=headers, json=payload, timeout=45)
    if not atsakas.ok:
        print("Groq klaidos detalės:", atsakas.text)
    atsakas.raise_for_status()
    return json.loads(atsakas.json()["choices"][0]["message"]["content"])
