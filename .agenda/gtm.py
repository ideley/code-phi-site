"""Google Tag Manager (GTM-M968FFMV) em todas as páginas publicadas.
- injeta o contêiner no <head> e o <noscript> após <body>
- libera os domínios do Google na CSP
- empurra eventos para o dataLayer: generate_lead (envio ao Google Forms) e contact_whatsapp (clique em wa.me)
GA4 (G-BQ6QWFL49E), eventos e vinculador de conversões são configurados dentro do contêiner.
"""
import re, pathlib

GTM = 'GTM-M968FFMV'
HEAD = ("<!-- Google Tag Manager --><script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
        "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
        "f.parentNode.insertBefore(j,f)})(window,document,'script','dataLayer','" + GTM + "');</script><!-- End Google Tag Manager -->\n"
        # eventos: lead = qualquer POST para o Google Forms; WhatsApp = clique em link wa.me
        "<script>(function(){var dl=window.dataLayer=window.dataLayer||[];var of=window.fetch;"
        "if(of)window.fetch=function(u,o){try{if(String(u).indexOf('/formResponse')>-1&&o&&o.body){var b=o.body,g=function(k){return b.get?b.get(k):''};"
        "dl.push({event:'generate_lead',form_name:(location.pathname.replace(/\\//g,' ').trim()||'home'),lead_interesse:g('entry.156359449')||''})}}catch(e){}return of.apply(this,arguments)};"
        "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href*=\"wa.me\"]');if(a)dl.push({event:'contact_whatsapp',page_path:location.pathname})},true)})();</script>\n")
BODY = ('<!-- Google Tag Manager (noscript) --><noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM +
        '" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript><!-- End Google Tag Manager (noscript) -->\n')

G_SCRIPT = 'https://www.googletagmanager.com https://*.googletagmanager.com'
G_CONNECT = 'https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://*.g.doubleclick.net https://www.google.com https://www.google.com.br'
G_IMG = 'https://*.google-analytics.com https://*.googletagmanager.com https://*.g.doubleclick.net https://www.google.com https://www.google.com.br'


def _csp(m):
    c = m.group(1)
    def add(directive, extra):
        nonlocal c
        r = re.search(r'(' + directive + r' [^;]*)', c)
        if r and 'googletagmanager' not in r.group(1) and 'google-analytics' not in r.group(1):
            c = c.replace(r.group(1), r.group(1) + ' ' + extra, 1)
    add('script-src', G_SCRIPT)
    add('connect-src', G_CONNECT)
    add('img-src', G_IMG)
    c = c.replace("frame-src 'none'", 'frame-src https://www.googletagmanager.com')
    return '<meta http-equiv="Content-Security-Policy" content="' + c + '">'


def apply(dst):
    dst = pathlib.Path(dst); done = []
    for p in dst.rglob('*.html'):
        if p.name.startswith('google') or '.git' in p.parts:
            continue
        s = p.read_text(encoding='utf-8')
        if '<head' not in s or GTM in s:
            continue
        s = re.sub(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', _csp, s, count=1)
        # depois da CSP (para a política valer também para o GTM); sem CSP, logo após <head>
        if re.search(r'<meta http-equiv="Content-Security-Policy"[^>]*>', s):
            s = re.sub(r'(<meta http-equiv="Content-Security-Policy"[^>]*>\s*)', lambda m: m.group(1) + HEAD, s, count=1)
        else:
            s = re.sub(r'(<head[^>]*>\s*)', lambda m: m.group(1) + HEAD, s, count=1)
        s = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + '\n' + BODY, s, count=1)
        p.write_text(s, encoding='utf-8'); done.append(str(p.relative_to(dst)))
    return done
