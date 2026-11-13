#!/usr/bin/env python3
"""Publica os artigos agendados do blog. Roda no GitHub Actions do code-phi-site (todo dia, 9h de Brasília).
Fica em code-phi-site/.agenda/ (copiado pelo publicar.py). Um artigo entra no ar quando a data dele chega.
Teste local: BLOG_HOJE=2026-11-20 python3 .agenda/agenda_blog.py"""
import re, sys, shutil, tempfile, pathlib, importlib.util, datetime
A = pathlib.Path(__file__).resolve().parent; ROOT = A.parent
sys.path.insert(0, str(A)); import seo, gtm
spec = importlib.util.spec_from_file_location('blogb', A/'blog'/'build.py'); bm = importlib.util.module_from_spec(spec); spec.loader.exec_module(bm)
home = (ROOT/'index.html').read_text(encoding='utf-8')
csp = re.search(r'<meta http-equiv="Content-Security-Policy"[^>]*>', home).group(0)
pix = re.search(r'<!-- Meta Pixel.*?</noscript>', home, re.S).group(0)
T = pathlib.Path(tempfile.mkdtemp())
bm.build(T/'blog', csp, pix); seo.apply(T); gtm.apply(T)
blog = ROOT/'blog'
for d in blog.iterdir():
    if d.is_dir() and d.name != 'img': shutil.rmtree(d)
shutil.copytree(T/'blog', blog, dirs_exist_ok=True)
# sitemap do site inteiro (mesmo formato do seo.py)
urls = [seo.page_url(str(f.relative_to(ROOT))) for f in sorted(ROOT.rglob('index.html'))
        if '.agenda' not in f.parts and '.git' not in f.parts and not str(f.relative_to(ROOT)).startswith('links/')]
hoje = datetime.date.today().isoformat(); B = seo.BASE
pri = lambda u: '1.0' if u == B + '/' else '0.9' if '/crm/' in u or '/raio-x/' in u else '0.7'
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{u}</loc><lastmod>{hoje}</lastmod><priority>{pri(u)}</priority></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
print('agenda: hoje', bm.HOJE)
