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
    sitemap_urls = [f"{BASE_URL}/"]

    # 1. TINKLŲ SEO PUSLAPIAI (/tinklai/...)
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

    # 2. MIESTŲ SEO PUSLAPIAI (/miestai/vilnius.html ir t.t.)
    miestu_degalines = {}
    for net in duomenys.get("networks", []):
        for s in net.get("stations", []):
            miestas = (s.get("city") or "").strip()
            if miestas:
                miestu_degalines.setdefault(miestas, []).append({**s, "network": net["name"]})

    for miestas, stotys in miestu_degalines.items():
        if len(stotys) < 2:
            continue
        m_slug = sukurti_slug(miestas)
        if not m_slug:
            continue
        m_kelias = f"miestai/{m_slug}.html"
        m_url = f"{BASE_URL}/{m_kelias}"
        sitemap_urls.append(m_url)

        stotys.sort(key=lambda x: x.get("a95") or 99)
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
    <title>Degalų kainos: {miestas} (Benzinas A95, Dyzelinas) | KuroPulsas.lt</title>
    <meta name="description" content="Mažiausios benzino ir dyzelino kainos vietovėje {miestas}. Palyginkite visų degalinių kainas vienoje vietoje.">
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
        <p style="color: var(--text-muted); margin-bottom: 24px;">Atnaujinta: {duomenys['last_updated']} • Šaltinis: Lietuvos energetikos agentūra (ena.lt)</p>
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

    # 3. SITEMAP.XML IR ROBOTS.TXT
    ns = "http://" + "www.sitemaps.org/schemas/sitemap/0.9"
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', f'<urlset xmlns="{ns}">']
    for u in sitemap_urls:
        xml.append(f"  <url><loc>{u}</loc></url>")
    xml.append("</urlset>")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))

    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
