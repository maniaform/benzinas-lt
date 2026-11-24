import os

BASE_URL = "https://" + "benzinas-lt.vercel.app"

def generuoti_kuro_seo(duomenys):
    os.makedirs("tinklai", exist_ok=True)
    sitemap_urls = [f"{BASE_URL}/"]

    for net in duomenys.get("networks", []):
        slug = net["id"]
        failo_kelias = f"tinklai/{slug}.html"
        pilnas_url = f"{BASE_URL}/{failo_kelias}"
        sitemap_urls.append(pilnas_url)

        eilutes = ""
        for s in net.get("stations", []):
            a95 = f"{s['a95']:.3f} €" if s.get("a95") else "—"
            a98 = f"{s['a98']:.3f} €" if s.get("a98") else "—"
            dz = f"{s['diesel']:.3f} €" if s.get("diesel") else "—"
            eilutes += f"<tr><td><strong>{s['city']}</strong></td><td>{s['address']}</td><td class='mono'>{a95}</td><td class='mono'>{a98}</td><td class='mono'>{dz}</td><td>{s['time']}</td><td>{s['source']}</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{net['name']} degalų kainos (A95, A98, Dyzelinas) | KuroPulsas.lt</title>
    <meta name="description" content="Naujausios {net['name']} degalinių tinklo benzino ir dyzelino kainos Lietuvoje: A95 nuo {net.get('best_a95', '—')} €, dyzelinas nuo {net.get('best_diesel', '—')} €.">
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
        <h1 class="section-title" style="font-size: 1.8rem;">⛽ {net['name']} — degalinės ir kuro kainos</h1>
        <p style="color: var(--text-muted); margin-bottom: 24px;">Paskutinis atnaujinimas: {duomenys['last_updated']} • Pagrindinis šaltinis: <a href="{net['source_url']}" target="_blank">{net['source_name']}</a></p>
        <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid var(--border-light);">
            <table class="stations-table">
                <thead><tr><th>Miestas</th><th>Adresas</th><th>A95</th><th>A98</th><th>Dyzelinas</th><th>Laikas</th><th>Šaltinis</th></tr></thead>
                <tbody>{eilutes}</tbody>
            </table>
        </div>
    </main>
</body>
</html>"""
        with open(failo_kelias, "w", encoding="utf-8") as f:
            f.write(html)

    ns = "http://" + "www.sitemaps.org/schemas/sitemap/0.9"
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', f'<urlset xmlns="{ns}">']
    for u in sitemap_urls:
        xml.append(f"  <url><loc>{u}</loc></url>")
    xml.append("</urlset>")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))

    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
