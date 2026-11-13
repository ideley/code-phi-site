#!/usr/bin/env python3
"""Gera o blog estático: blog/index.html e blog/<slug>/index.html a partir de posts/*.md.
Uso: build.py <pasta_destino> <csp_meta> <pixel_html>  (chamado pelo publicar.py)"""
import re, sys, html, pathlib, shutil, json
SRC = pathlib.Path(__file__).parent
import datetime, os
from zoneinfo import ZoneInfo
HOJE = os.environ.get('BLOG_HOJE') or datetime.datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat()
MES = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
def fm(t):
    m = re.match(r'---\n(.*?)\n---\n(.*)', t, re.S); meta = {}
    for l in m.group(1).splitlines():
        k, v = l.split(':', 1); meta[k.strip()] = v.strip()
    return meta, m.group(2).strip()
def inl(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', s)
    return s
def md(t):
    out, lst = [], None
    for b in re.split(r'\n\s*\n', t):
        b = b.strip()
        if b.startswith('## '): out.append(f'<h2>{inl(b[3:])}</h2>'); continue
        lines = b.splitlines()
        if all(re.match(r'\d+\. ', l) for l in lines):
            out.append('<ol>' + ''.join(f'<li>{inl(re.sub(r"^\d+\. ", "", l))}</li>' for l in lines) + '</ol>'); continue
        if all(l.startswith('- ') for l in lines):
            out.append('<ul>' + ''.join(f'<li>{inl(l[2:])}</li>' for l in lines) + '</ul>'); continue
        out.append(f'<p>{inl(" ".join(lines))}</p>')
    return '\n'.join(out)
def data_br(d):
    y, m, dd = d.split('-'); return f'{int(dd)} {MES[int(m)-1]} {y}'
CSS = (SRC/'blog.css').read_text()
HEAD = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">%(csp)s
<meta name="viewport" content="width=device-width,initial-scale=1"><title>%(t)s</title><meta name="description" content="%(d)s">
<meta property="og:title" content="%(t)s"><meta property="og:description" content="%(d)s"><meta property="og:image" content="https://codephi.com.br%(img)s"><meta property="og:type" content="%(og)s">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta name="theme-color" content="#08080a"><meta name="referrer" content="strict-origin-when-cross-origin">
%(pix)s<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@500&display=swap" rel="stylesheet"><style>%(css)s</style></head><body>
<svg width="0" height="0" style="position:absolute"><symbol id="phi" viewBox="0 0 46 62"><circle cx="23" cy="34" r="15" fill="none" stroke-width="5"/><line x1="23" y1="6" x2="23" y2="60" stroke-width="5"/></symbol></svg>
<div class="gr"></div><div class="prog" id="prog"></div>
<header class="nav"><a class="logo" href="/">code<svg width="14" height="19"><use href="#phi"/></svg></a><nav><a href="/servicos/">Serviços</a><a href="/crm/">CRM</a><a href="/sobre/">Sobre</a><a href="/blog/" class="%(blogon)s">Blog</a><a class="cta" href="/raio-x/?utm_source=blog">Raio-X grátis</a></nav></header>'''
AUTOR = '''<div class="autor"><div class="av"><svg width="22" height="30"><use href="#phi"/></svg></div><div><b>Vinícius Duarte</b><span>Fundador da Code ϕ · estratégia de crescimento, mídia e CRM</span></div><a href="https://www.linkedin.com/in/viniciusduarteb/" target="_blank" rel="noopener">LinkedIn ↗</a></div>'''
CTA = '''<div class="ctab"><div class="eb"><i></i>Raio-X gratuito</div><h3>Onde o seu negócio <em>perde cliente?</em></h3><p>8 perguntas, 2 minutos. Você vê o seu ponto de atenção na hora.</p><a class="btn" href="/raio-x/?utm_source=blog&utm_campaign=%s">Fazer meu Raio-X →</a></div>'''
FOOT = '''<footer><span>Code ϕ · Cresça com método</span><span><a href="/servicos/">serviços</a> · <a href="/crm/">crm</a> · <a href="/sobre/">sobre</a> · <a href="/">codephi.com.br</a></span></footer>
<script>const pr=document.getElementById('prog');addEventListener('scroll',()=>{const h=document.documentElement;pr.style.width=(h.scrollTop/(h.scrollHeight-h.clientHeight)*100)+'%'},{passive:true});
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px'});document.querySelectorAll('.rv').forEach(el=>io.observe(el));
document.querySelectorAll('a[href^="/raio-x"]').forEach(a=>a.addEventListener('click',()=>{try{fbq('track','ViewContent',{content_name:'Raio-X via blog'})}catch(e){}}));</script></body></html>'''
def build(dst, csp, pix):
    dst = pathlib.Path(dst); (dst/'img').mkdir(parents=True, exist_ok=True)
    for f in (SRC/'img').iterdir(): shutil.copy2(f, dst/'img'/f.name)
    posts = []
    for f in sorted((SRC/'posts').glob('*.md'), reverse=True):
        meta, body = fm(f.read_text(encoding='utf-8')); meta['body'] = body
        if meta['data'] > HOJE: continue  # agendado: só entra no dia (horário de Brasília)
        posts.append(meta)
    for i, p in enumerate(posts):
        rel = [q for q in posts if q is not p][:2]
        relh = ''.join(f'<a class="card rv" href="/blog/{q["slug"]}/"><img src="/blog/img/{q["capa"]}" alt="" loading="lazy"><div><small>{q["categoria"]} · {q["leitura"]}</small><b>{html.escape(q["titulo"])}</b></div></a>' for q in rel)
        h = HEAD % dict(csp=csp, pix=pix, css=CSS, t=html.escape(p['titulo'])+' · Code ϕ', d=html.escape(p['resumo']), img='/blog/img/'+p['capa'], og='article', blogon='on')
        h += f'''<main class="art"><a class="back" href="/blog/">← Blog</a><div class="meta rv"><span>{p["categoria"]}</span><span>{data_br(p["data"])}</span><span>{p["leitura"]} de leitura</span></div>
<h1 class="rv">{html.escape(p["titulo"])}</h1><p class="lede rv">{html.escape(p["resumo"])}</p>{AUTOR}
<figure class="hero rv"><img src="/blog/img/{p["capa"]}" alt="{html.escape(p["titulo"])}"></figure>
<article class="txt">{md(p["body"])}</article>{CTA % p["slug"]}
{'<div class="rel"><div class="eb"><i></i>Continue lendo</div><div class="cards">'+relh+'</div></div>' if relh else ''}</main>''' + FOOT
        (dst/p['slug']).mkdir(exist_ok=True); (dst/p['slug']/'index.html').write_text(h, encoding='utf-8')
    cards = ''.join(f'<a class="card rv{" big" if i==0 else ""}" href="/blog/{p["slug"]}/"><img src="/blog/img/{p["capa"]}" alt="" loading="lazy"><div><small>{p["categoria"]} · {data_br(p["data"])} · {p["leitura"]}</small><b>{html.escape(p["titulo"])}</b><span>{html.escape(p["resumo"])}</span></div></a>' for i, p in enumerate(posts))
    h = HEAD % dict(csp=csp, pix=pix, css=CSS, t='Blog · Code ϕ', d='Marketing e dados para quem quer crescer com método: mídia, conversão, CRM e recompra, sem enrolação.', img='/blog/img/'+posts[0]['capa'], og='website', blogon='on')
    h += f'''<main class="idx"><div class="eb rv"><i></i>Blog da Code ϕ</div><h1 class="rv">Crescer com <em>método</em>, um tema por vez.</h1>
<p class="lede rv">Mídia, conversão, CRM e recompra explicados sem enrolação, para quem toca o próprio negócio.</p>
<div class="cards list">{cards}</div>{CTA % "blog-index"}</main>''' + FOOT
    (dst/'index.html').write_text(h, encoding='utf-8')
    (dst/'posts.json').write_text(json.dumps([{k:p[k] for k in ('titulo','slug','data','categoria','resumo','capa','leitura')} for p in posts],ensure_ascii=False),encoding='utf-8')
    print('blog:', len(posts), 'posts')
if __name__ == '__main__': build(*sys.argv[1:4])
