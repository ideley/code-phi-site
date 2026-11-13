"""SEO técnico aplicado depois de gerar o site público: canonical, Open Graph, JSON-LD, sitemap e robots."""
import re, json, html, datetime, pathlib
BASE = 'https://codephi.com.br'
SAME = ['https://www.instagram.com/codevitruvian/', 'https://www.linkedin.com/company/code-phi/',
        'https://www.youtube.com/@code.vitruvian', 'https://www.facebook.com/profile.php?id=61596306214869']
ORG = {"@type": "ProfessionalService", "@id": BASE + "/#org", "name": "Code ϕ", "alternateName": ["Code Phi", "Code Vitruvian"],
       "legalName": "CODE VITRUVIAN COMUNICACAO E MIDIA LTDA", "taxID": "48.418.062/0001-44", "foundingDate": "2022-10-26",
       "url": BASE + "/", "logo": BASE + "/apple-touch-icon.png", "image": BASE + "/poster-lima.jpg", "slogan": "Cresça com método.",
       "description": "Marketing e dados para e-commerce, negócios locais e serviços: mídia paga, site e conversão, CRM e recompra.",
       "email": "codevitruvian@gmail.com", "areaServed": {"@type": "Country", "name": "Brasil"},
       "address": {"@type": "PostalAddress", "streetAddress": "Rua Pedro Martins, 330 - Térreo", "addressLocality": "Nova Serrana", "addressRegion": "MG", "postalCode": "35523-014", "addressCountry": "BR"},
       "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "09:00", "closes": "18:00"}],
       "sameAs": SAME, "knowsAbout": ["CRM", "Recompra", "Tráfego pago", "Conversão de e-commerce", "E-mail marketing", "WhatsApp marketing"]}
TITLES = {'/': 'Code ϕ · Marketing, CRM e tráfego para e-commerce | Cresça com método'}
def page_url(rel):
    rel = rel.replace('index.html', '')
    return BASE + '/' + rel
def ld(obj): return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", **obj} if "@graph" not in obj else {"@context": "https://schema.org", **obj}, ensure_ascii=False) + '</script>'
def text(s): return html.unescape(re.sub(r'<[^>]+>', ' ', s)).strip()
def apply(DST):
    DST = pathlib.Path(DST); urls = []
    for f in sorted(DST.rglob('index.html')):
        rel = str(f.relative_to(DST)); url = page_url(rel); path = url[len(BASE):]
        s = f.read_text(encoding='utf-8')
        if path in TITLES: s = re.sub(r'<title>.*?</title>', '<title>' + TITLES[path] + '</title>', s, count=1)
        title = text(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
        dm = re.search(r'<meta name="description" content="([^"]*)"', s); desc = html.unescape(dm.group(1)) if dm else ''
        head = []
        if 'rel="canonical"' not in s: head.append(f'<link rel="canonical" href="{url}">')
        if 'og:title' not in s: head.append(f'<meta property="og:title" content="{html.escape(title)}">')
        if 'og:description' not in s and desc: head.append(f'<meta property="og:description" content="{html.escape(desc)}">')
        if 'og:image' not in s: head.append(f'<meta property="og:image" content="{BASE}/poster-lima.jpg">')
        if 'og:url' not in s: head.append(f'<meta property="og:url" content="{url}">')
        head += ['<meta property="og:site_name" content="Code ϕ">', '<meta property="og:locale" content="pt_BR">', '<meta name="twitter:card" content="summary_large_image">']
        noindex = path.startswith('/links/')
        if noindex: head.append('<meta name="robots" content="noindex,follow">')
        # dados estruturados
        crumbs = [{"@type": "ListItem", "position": 1, "name": "Início", "item": BASE + "/"}]
        if path != '/':
            parts = [p for p in path.strip('/').split('/') if p]
            acc = ''
            for i, p in enumerate(parts):
                acc += '/' + p
                nm = {'crm': 'CRM e recompra', 'blog': 'Blog', 'raio-x': 'Raio-X', 'links': 'Links'}.get(p, title.split(' · ')[0])
                crumbs.append({"@type": "ListItem", "position": i + 2, "name": nm, "item": BASE + acc + '/'})
        graph = []
        if path == '/':
            graph += [ORG, {"@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": "Code ϕ", "inLanguage": "pt-BR", "publisher": {"@id": BASE + "/#org"}}]
        else:
            graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
        if path == '/crm/':
            graph.append({"@type": "Service", "name": "CRM e recompra para e-commerce", "serviceType": "CRM, automação de e-mail e WhatsApp, cashback e recompra",
                          "provider": {"@id": BASE + "/#org"}, "areaServed": "BR", "url": url, "description": desc})
        qas = re.findall(r'<div class="qa[^"]*"><button>(.*?)<span class="pl">\+</span></button><div class="ans"><div>(.*?)</div></div></div>', s, re.S)
        if qas:
            graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": text(q), "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in qas]})
        if path.startswith('/blog/') and path != '/blog/':
            h1 = text(re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1))
            dt = re.search(r'(\d{1,2}) (jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez) (\d{4})', s)
            graph.append({"@type": "BlogPosting", "headline": h1, "description": desc, "url": url, "inLanguage": "pt-BR",
                          "author": {"@type": "Person", "name": "Vinícius Duarte", "url": "https://www.linkedin.com/in/viniciusduarteb/"},
                          "publisher": {"@id": BASE + "/#org"}, "image": BASE + (re.search(r'og:image" content="https://codephi.com.br([^"]+)"', s) or re.search(r'()', '')).group(1)})
        if graph: head.append(ld({"@graph": graph}))
        s = s.replace('</head>', '\n'.join(head) + '\n</head>', 1)
        f.write_text(s, encoding='utf-8')
        if not noindex: urls.append(url)
    today = datetime.date.today().isoformat()
    pri = lambda u: '1.0' if u == BASE + '/' else '0.9' if '/crm/' in u or '/raio-x/' in u else '0.7'
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{pri(u)}</priority></url>\n' for u in urls) + '</urlset>\n'
    (DST / 'sitemap.xml').write_text(sm, encoding='utf-8')
    (DST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n', encoding='utf-8')
    return urls
