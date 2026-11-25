import os
import re

BASE_URL = "https://" + "benzinas-lt.vercel.app"

def sukurti_slug(tekstas):
    p = tekstas.lower().strip()
    lt = {'ą': 'a', 'č': 'c', 'ę': 'e', 'ė': 'e', 'į': 'i', 'š': 's', 'ų': 'u', 'ū': 'u', 'ž': 'z'}
    for k, v in lt.items():
        p = p.replace(k, v)
    return re.sub(r'[^a-z0-9]+', '-', p).strip('-')

def generuoti_kuro_seo(duomenys):
    os.makedirs("tinklai", exist_ok=True)
    os.makedirs("miestai", exist_ok=True)
    os.makedirs("keliai", exist_ok=True)
    sitemap_urls = [f"{BASE_URL}/"]

    # 1. TINKLŲ SEO PUSLAPIAI
    for net in duomenys.get("networks", []):
        slug = net["id"]
        failo_kelias = f"tinklai/{slug}.html"
        pilnas_url = f"{BASE_URL}/{failo_kelias}"
        sitemap_urls.append(pilnas_url)

        logo_html = f"<img src='{net['logo_url']}' alt='{net['name']}' style='width:42px; height:42px; object-fit:contain; border-radius:8px; background:white; padding:4px; border:1px solid #e5e7eb;'>" if net.get("logo_url") else ""

        eilutes = ""
        for s in net.get("stations", []):
            a95 = f"{s['a95']:.3f} €" if s.get("a95") else "—"
            a98 = f"{s['a98']:.3f} €" if s.get("a98") else "—"
            dz = f"{s['diesel']:.3f} €" if s.get("diesel") else "—"
            eilutes += f"<tr><td><strong>{s['city']}</strong></td><td>{s['address']}</td><td class='mono' style='color:#059669;'>{a95}</td><td class='mono'>{a98}</td><td class='mono' style='color:#d97706;'>{dz}</td><td style='font-size:0.8rem; color:#6b7280;'>{s['time']}</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{net['name']} degalų kainos šiandien (A95, A98, Dyzelinas) | KuroPulsas.lt</title>
    <meta name="description" content="Naujausios {net['name']} degalinių tinklo benzino ir dyzelino kainos Lietuvoje: A95 nuo {net.get('best_a95', '—')} €, dyzelinas nuo {net.get('best_diesel', '—')} €. Visų {len(net.get('stations', []))} degalinių adresai ir kainos.">
    <link rel="canonical" href="{pilnas_url}">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="../index.html" style="text-decoration:none; color:white;"><div class="logo">Kuro<span>Pulsas.lt</span></div></a>
            <a href="../index.html" class="fuel-btn active" style="text-decoration:none;">← Visi tinklai</a>
        </div>
    </header>
    <main class="container" style="padding-top: 32px; padding-bottom: 60px;">
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:12px;">
            {logo_html}
            <h1 class="section-title" style="font-size: 1.75rem; margin-bottom:0;">{net['name']} — degalinės ir kuro kainos</h1>
        </div>
        <p style="color: var(--text-muted); margin-bottom: 24px;">Atnaujinta: {duomenys['last_updated']} • Šaltinis: Lietuvos energetikos agentūra (ena.lt) • Iš viso degalinių: {len(net.get('stations', []))}</p>
        <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid var(--border-light); overflow-x:auto;">
            <table class="stations-table">
                <thead><tr><th>Miestas / Rajonas</th><th>Adresas</th><th>Benzinas A95</th><th>Benzinas A98</th><th>Dyzelinas</th><th>Laikas</th></tr></thead>
                <tbody>{eilutes}</tbody>
            </table>
        </div>
    </main>
</body>
</html>"""
        with open(failo_kelias, "w", encoding="utf-8") as f:
            f.write(html)

    # 2. VISŲ LIETUVOS SAVIVALDYBIŲ SEO PUSLAPIAI
    miestu_degalines = {}
    for net in duomenys.get("networks", []):
        for s in net.get("stations", []):
            miestas = (s.get("city") or "").strip()
            if miestas:
                miestu_degalines.setdefault(miestas, []).append({**s, "network": net["name"]})

    visu_miestu_nuorodos = []

    for miestas in sorted(miestu_degalines.keys()):
        stotys = miestu_degalines[miestas]
        m_slug = sukurti_slug(miestas)
        if not m_slug:
            continue
        m_kelias = f"miestai/{m_slug}.html"
        m_url = f"{BASE_URL}/{m_kelias}"
        sitemap_urls.append(m_url)
        visu_miestu_nuorodos.append(f'<a href="{m_kelias}" class="filter-chip" style="text-decoration:none; color:var(--text-main);">{miestas} ({len(stotys)})</a>')

        stotys.sort(key=lambda x: x.get("a95") or 99)
        min_a95 = next((s["a95"] for s in stotys if s.get("a95")), "—")
        min_dz = min((s["diesel"] for s in stotys if s.get("diesel")), default="—")

        m_eilutes = ""
        for s in stotys:
            a95 = f"{s['a95']:.3f} €" if s.get("a95") else "—"
            a98 = f"{s['a98']:.3f} €" if s.get("a98") else "—"
            dz = f"{s['diesel']:.3f} €" if s.get("diesel") else "—"
            m_eilutes += f"<tr><td><strong>{s['network']}</strong></td><td>{s['address']}</td><td class='mono' style='color:#059669;'>{a95}</td><td class='mono'>{a98}</td><td class='mono' style='color:#d97706;'>{dz}</td><td style='font-size:0.8rem; color:#6b7280;'>{s['time']}</td></tr>"

        m_html = f"""<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Degalų kainos: {miestas} — A95 nuo {min_a95} €, Dyzelinas nuo {min_dz} € | KuroPulsas.lt</title>
    <meta name="description" content="Naujausios benzino ir dyzelino kainos vietovėje {miestas}. Pigiausias A95 benzinas nuo {min_a95} €, dyzelinas nuo {min_dz} €. Visų {len(stotys)} degalinių adresai.">
    <link rel="canonical" href="{m_url}">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="../index.html" style="text-decoration:none; color:white;"><div class="logo">Kuro<span>Pulsas.lt</span></div></a>
            <a href="../index.html" class="fuel-btn active" style="text-decoration:none;">← Visos vietovės</a>
        </div>
    </header>
    <main class="container" style="padding-top: 32px; padding-bottom: 60px;">
        <h1 class="section-title" style="font-size: 1.75rem;">📍 Degalų kainos — {miestas}</h1>
        <p style="color: var(--text-muted); margin-bottom: 24px;">Atnaujinta: {duomenys['last_updated']} • Šaltinis: Lietuvos energetikos agentūra (ena.lt) • Degalinių skaičius: {len(stotys)}</p>
        <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid var(--border-light); overflow-x:auto;">
            <table class="stations-table">
                <thead><tr><th>Tinklas</th><th>Adresas</th><th>Benzinas A95</th><th>Benzinas A98</th><th>Dyzelinas</th><th>Laikas</th></tr></thead>
                <tbody>{m_eilutes}</tbody>
            </table>
        </div>
    </main>
</body>
</html>"""
        with open(m_kelias, "w", encoding="utf-8") as f:
            f.write(m_html)

    # 2B. MAGISTRALINIŲ KELIŲ SEO PUSLAPIAI (/keliai/...)
    magistrales = [
        {"slug": "a1-vilnius-kaunas-klaipeda", "name": "Magistralė A1 (Vilnius – Kaunas – Klaipėda)", "raktazodziai": ["a1", "vilniaus pl", "kauno pl", "klaipėdos pl", "savanorių pr", "islandijos pl", "jakų"]},
        {"slug": "a2-vilnius-panevezys", "name": "Magistralė A2 (Vilnius – Ukmergė – Panevėžys)", "raktazodziai": ["a2", "ukmergės", "vilniaus g.", "širvint"]},
        {"slug": "via-baltica-a5-a8-a10", "name": "Via Baltica (A5 / A8 / A10: Kaunas – Marijampolė – Panevėžys)", "raktazodziai": ["a5", "a8", "a10", "via baltica", "marijampol", "pasval", "kedain"]},
        {"slug": "a6-kaunas-zarasai", "name": "Kelias A6 (Kaunas – Jonava – Ukmergė – Utena – Zarasai)", "raktazodziai": ["a6", "jonav", "uten", "zaras"]},
        {"slug": "a11-siauliai-palanga", "name": "Kelias A11 (Šiauliai – Telšiai – Plungė – Palanga)", "raktazodziai": ["a11", "telš", "plung", "kreting", "palang"]}
    ]

    keliu_nuorodos_html = []

    for kelias in magistrales:
        k_stotys = []
        for net in duomenys.get("networks", []):
            for s in net.get("stations", []):
                pilnas_adr = f"{s.get('city', '')} {s.get('address', '')}".lower()
                if any(rz in pilnas_adr for rz in kelias["raktazodziai"]):
                    k_stotys.append({**s, "network": net["name"]})

        if not k_stotys:
            continue

        k_kelias = f"keliai/{kelias['slug']}.html"
        k_url = f"{BASE_URL}/{k_kelias}"
        sitemap_urls.append(k_url)
        keliu_nuorodos_html.append(f'<a href="{k_kelias}" class="filter-chip" style="text-decoration:none; color:var(--text-main);">{kelias["name"]} ({len(k_stotys)})</a>')

        k_stotys.sort(key=lambda x: x.get("a95") or 99)
        min_a95 = next((s["a95"] for s in k_stotys if s.get("a95")), "—")
        min_dz = min((s["diesel"] for s in k_stotys if s.get("diesel")), default="—")

        k_eilutes = ""
        for s in k_stotys:
            a95 = f"{s['a95']:.3f} €" if s.get("a95") else "—"
            a98 = f"{s['a98']:.3f} €" if s.get("a98") else "—"
            dz = f"{s['diesel']:.3f} €" if s.get("diesel") else "—"
            k_eilutes += f"<tr><td><strong>{s['network']}</strong></td><td>{s['city']}</td><td>{s['address']}</td><td class='mono' style='color:#059669;'>{a95}</td><td class='mono'>{a98}</td><td class='mono' style='color:#d97706;'>{dz}</td></tr>"

        k_html = f"""<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Degalų kainos kelyje: {kelias['name']} | KuroPulsas.lt</title>
    <meta name="description" content="Mažiausios benzino ir dyzelino kainos kelyje {kelias['name']}. Pigiausias A95 nuo {min_a95} €, dyzelinas nuo {min_dz} €. Palyginkite pakeliui esančias degalines.">
    <link rel="canonical" href="{k_url}">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="../index.html" style="text-decoration:none; color:white;"><div class="logo">Kuro<span>Pulsas.lt</span></div></a>
            <a href="../index.html" class="fuel-btn active" style="text-decoration:none;">← Pagrindinis puslapis</a>
        </div>
    </header>
    <main class="container" style="padding-top: 32px; padding-bottom: 60px;">
        <h1 class="section-title" style="font-size: 1.75rem;">🛣️ Degalų kainos: {kelias['name']}</h1>
        <p style="color: var(--text-muted); margin-bottom: 24px;">Atnaujinta: {duomenys['last_updated']} • Šaltinis: Lietuvos energetikos agentūra (ena.lt) • Rasta degalinių: {len(k_stotys)}</p>
        <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid var(--border-light); overflow-x:auto;">
            <table class="stations-table">
                <thead><tr><th>Tinklas</th><th>Miestas / Rajonas</th><th>Adresas</th><th>Benzinas A95</th><th>Benzinas A98</th><th>Dyzelinas</th></tr></thead>
                <tbody>{k_eilutes}</tbody>
            </table>
        </div>
    </main>
</body>
</html>"""
        with open(k_kelias, "w", encoding="utf-8") as f:
            f.write(k_html)

    # 3. ATNAUJINAME VISŲ MIESTŲ NUORODAS PAGRINDINIAME INDEX.HTML
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            idx_html = f.read()
        start_tag = "<!-- SEO_MIESTAI_START -->"
        end_tag = "<!-- SEO_MIESTAI_END -->"
        if start_tag in idx_html and end_tag in idx_html:
            naujas_blokas = f"{start_tag}\n" + "\n".join(visu_miestu_nuorodos) + f"\n{end_tag}"
            idx_html = re.sub(f"{start_tag}.*?{end_tag}", naujas_blokas, idx_html, flags=re.DOTALL)
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(idx_html)

    # 4. SITEMAP.XML IR ROBOTS.TXT
    ns = "http://" + "www.sitemaps.org/schemas/sitemap/0.9"
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', f'<urlset xmlns="{ns}">']
    for u in sitemap_urls:
        xml.append(f"  <url><loc>{u}</loc></url>")
    xml.append("</urlset>")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))

    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
