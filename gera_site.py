"""Site do Estrela Negra (GitHub Pages) · v4 (24/11/2026): segue a referência do site antigo do Bruno (cabeçalho e rodapé escuros, título em caixa alta com palavra em roxo, seções brancas).
Uma página por vídeo PÚBLICO (oEmbed = 200), com vídeo, o número do vídeo, capítulos, grau de certeza, transcrição e fontes.
Dados: motion/reels_NN/05_YOUTUBE/METADADOS_YOUTUBE.md · scripts/motion/tempos/tts/rNN.txt · motion/THUMBS_LUZ/TROCA_YOUTUBE.json (+ ids_extra.json)
· miniaturas THUMB_LUZ_NN_16x9.jpg · número/rótulo da tabela V de scripts/thumbs/thumbs_luz.py · artes do Instagram (FOTO_DO_CEU).
uso: python3 gera_site.py [--todos]   (--todos ignora o filtro de vídeo público: só para prévia/Figma; nunca publicar assim)"""
import json, re, os, sys, html, shutil, unicodedata, urllib.request, datetime, glob
from PIL import Image
B = "/Users/porciuncula/Desktop/BRUNO/estrela-negra"; AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = AQUI + "/docs/"
URL = "https://bruno-porciuncula.github.io/estrelanegra/"; TODOS = "--todos" in sys.argv
IDS = {x["reels"]: x["id"] for x in json.load(open(B + "/motion/THUMBS_LUZ/TROCA_YOUTUBE.json")) if x["versao"] == "16:9"}
IDS.update({"23": "yPL-Up9xJhc"})
if os.path.exists(AQUI + "/ids_extra.json"): IDS.update(json.load(open(AQUI + "/ids_extra.json")))
NUM = {m.group(1): (m.group(2), [x.strip().strip('"') for x in m.group(3).split('",')]) for m in re.finditer(r'\("(\d\d)", "reels_\d\d", "[A-Z]", [^,]+, "([^"]*)", \[([^\]]*)\]', open(B + "/scripts/thumbs/thumbs_luz.py", encoding="utf-8").read())}
def publico(i):
    try: return urllib.request.urlopen("https://www.youtube.com/oembed?url=https://youtu.be/%s&format=json" % i, timeout=15).status == 200
    except Exception: return False
def slug(s): return re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()).strip("-")[:70]
def limpa(t): return re.sub(r"Narração com voz sintetizada[^.\n]*\.?", "", re.sub(r"\bEP\.?\s?\d+\b\s*[·:-]?\s*", "", t)).strip()
def secao(md, ini, ate=("##", "🔎", "📚", "🖼", "Identidade visual", "#")):
    if ini not in md: return ""
    out = []
    for l in md.split(ini, 1)[1].split("\n")[1:]:
        if any(l.startswith(a) for a in ate) and out: break
        out.append(l)
    return "\n".join(out).strip()
def e(s): return html.escape(s)
def seloclasse(t):
    u = t.upper()
    return "c" if ("CONFIRM" in u or "CONSENSO" in u) else "f" if "FORTE" in u else "d" if "DEBATE" in u else "h" if ("HIPÓTESE" in u or "HIPOTESE" in u) else "p"
def nivel(t):
    u = t.upper()
    for k, v in (("EVIDÊNCIA FORTE", "Evidência forte"), ("EM DEBATE", "Em debate"), ("HIPÓTESE", "Hipótese"), ("CONSENSO", "Consenso"), ("CONFIRMAD", "Confirmado"), ("PREVIS", "Previsão"), ("PLANO", "Plano"), ("ESQUEMA", "Esquema"), ("ESTIMATIVA", "Estimativa")):
        if k in u: return v
    return t.split("(")[0].strip().capitalize()[:22]
def certezas(cert):
    out = []
    for parte in [p.strip() for p in re.split(r"\s·\s", cert) if p.strip()]:
        if "=" in parte: o, n = parte.split("=", 1); out.append((n.strip().rstrip("."), o.strip()))
        else: out.append(("", parte))
    return out
def reduz(src, dst, w):
    im = Image.open(src).convert("RGB"); im.thumbnail((w, w * 2)); im.save(dst, quality=84, optimize=True)
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT + "img")
# ------------------------------------------------------------------ dados
DADOS = []
for nn in sorted(IDS, key=int):
    md_p = B + "/motion/reels_%s/05_YOUTUBE/METADADOS_YOUTUBE.md" % nn
    if not os.path.exists(md_p) or not (TODOS or publico(IDS[nn])): continue
    md = open(md_p, encoding="utf-8").read(); vid = IDS[nn]
    m = re.search(r"^- 16:9: (.+)$", md, re.M) or re.search(r"## Título[^\n]*\n(?:[^\n]*\n)*?- (.+)$", md, re.M); titulo = limpa(m.group(1)) if m else "Estrela Negra"
    desc_bloco = secao(md, "## Descrição (16:9 e vertical)", ("⏱", "##")) or secao(md, "## Descrição\n", ("⏱", "##", "#"))
    resumo = [limpa(p) for p in desc_bloco.split("\n\n") if p.strip() and not p.startswith("Gravado") and not p.startswith("⏱")]
    caps = re.findall(r"^(\d+:\d\d) (.+)$", secao(md, "⏱ Capítulos", ("🔎", "📚", "##")), re.M)
    cert = limpa(md.split("🔎", 1)[1].split("\n", 1)[0].split(":", 1)[-1]) if "🔎" in md else ""
    fontes = [limpa(re.sub(r"^\d+\.\s*", "", l)) for l in secao(md, "📚 Fontes", ("🖼", "Identidade", "#", "##")).split("\n") if l.strip()]
    imgs = limpa(md.split("🖼", 1)[1].split("\n", 1)[0].split(":", 1)[-1]) if "🖼" in md else ""
    tts = B + "/scripts/motion/tempos/tts/r%s.txt" % nn; transc = []
    if os.path.exists(tts): transc = [re.sub(r"\[[^\]]*\]\s*", "", p).strip() for p in open(tts, encoding="utf-8").read().split("\n\n") if p.strip()]
    sl = slug(titulo); th = B + "/motion/THUMBS_LUZ/THUMB_LUZ_%s_16x9.jpg" % nn
    if os.path.exists(th): reduz(th, OUT + "img/%s.jpg" % sl, 1280)
    num, rot = NUM.get(nn, ("", []))
    DADOS.append(dict(nn=int(nn), vid=vid, titulo=titulo, resumo=resumo, caps=caps, cert=cert, fontes=fontes, imgs=imgs, transc=transc, sl=sl, img="img/%s.jpg" % sl, num=num, rot=" ".join(rot).capitalize()))
DADOS.sort(key=lambda d: -d["nn"])
IG = []
for k, f in enumerate(sorted(glob.glob(B + "/motion/INSTAGRAM/FOTO_DO_CEU/img/f*.jpg"))[:10]):
    im = Image.open(f).convert("RGB"); s_ = min(im.size); im = im.crop(((im.width - s_) // 2, (im.height - s_) // 2, (im.width + s_) // 2, (im.height + s_) // 2)); im.thumbnail((520, 520)); im.save(OUT + "img/ceu_%d.jpg" % k, quality=84); IG.append("img/ceu_%d.jpg" % k)
def recorte(src, dst, box=None, w=1400):
    im = Image.open(src).convert("RGB")
    if box: im = im.crop(box)
    im.thumbnail((w, w)); im.save(dst, quality=86)
L = B + "/motion/INSTAGRAM/LOTE5/fotos/"
recorte(L + "T1412_saturno_aneis_cassini.jpg", OUT + "img/hero.jpg")
recorte(L + "T2012_webb_espelho.jpg", OUT + "img/webb.jpg")
recorte(B + "/motion/reels_23/00_IMAGENS/c01_lua_cruzando_terra_dscovr.jpg", OUT + "img/sobre.jpg")
recorte(B + "/motion/INSTAGRAM/FOTO_DO_CEU/img/f05_jupiter_webb.jpg", OUT + "img/parceria.jpg", w=700)
recorte(B + "/motion/apresentacao_2026/00_IMAGENS/bruno_1.png", OUT + "img/bruno.jpg", box=(70, 40, 578, 548), w=640)
lg = Image.open(B + "/assets/marca/original_2020/logo_estrela_negra_transparente.png").convert("RGBA"); lg.thumbnail((520, 520)); lg.save(OUT + "img/logo.png")
import numpy as np
a_ = np.array(lg); br = (a_[..., 0] > 200) & (a_[..., 1] > 200) & (a_[..., 2] > 200); a_[br, 0:3] = (18, 16, 22); Image.fromarray(a_).save(OUT + "img/logo_escuro.png")
NFONTES = sum(len(d["fontes"]) for d in DADOS)
# ------------------------------------------------------------------ estilo
CSS = """:root{--esc:#0A090E;--esc2:#060509;--gr:#16141C;--pp:#EEEBE6;--off:#F1EEE9;--tx:#16141C;--mu:#6F6B77;--mu2:#9C98A5;--ln:#DCD8D2;--lnd:#25222D;--rx:#8762F3;--rxl:#A88BFF;--glow:0 0 28px rgba(135,98,243,.55)}
*{box-sizing:border-box}html{-webkit-font-smoothing:antialiased}
body{margin:0;background:var(--pp) url(GRAO) repeat;color:var(--tx);font:16px/1.7 'Space Grotesk',system-ui,sans-serif}
a{color:inherit;text-decoration:none}img{display:block;max-width:100%}
.w{max-width:1200px;margin:0 auto;padding:0 48px}
.escuro{background:var(--esc) url(GRAO) repeat;color:var(--off)}
.rot{font-weight:700;font-size:12px;letter-spacing:.42em;text-transform:uppercase;color:var(--rx)}.escuro .rot{color:var(--rxl)}
.rot.g{color:var(--mu)}.escuro .rot.g{color:var(--mu2)}
/* cabeçalho */
.topo{background:var(--esc) url(GRAO) repeat;color:var(--off)}
.nav{display:flex;align-items:center;justify-content:space-between;height:84px;border-bottom:1px solid var(--lnd)}
.nav .logo img{height:38px;width:auto}
.menu{display:flex;gap:40px;font-size:12px;font-weight:700;letter-spacing:.26em;text-transform:uppercase}.menu a{color:var(--mu2);padding:32px 0;border-bottom:1.5px solid transparent}.menu a.on{color:var(--off);border-color:var(--rxl)}
.soc{display:flex;gap:10px}.soc a{width:32px;height:32px;border-radius:50%;border:1px solid var(--lnd);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;letter-spacing:.06em;color:var(--off)}
.hero{display:grid;grid-template-columns:1fr 1.05fr;align-items:center;min-height:520px}
.hero .img{align-self:stretch;background-size:cover;background-position:center}
.marca-h{font-weight:300;font-size:104px;line-height:.96;letter-spacing:-.03em;margin:22px 0 0;color:var(--off)}
.marca-h span{color:var(--rxl);text-shadow:0 0 34px rgba(168,139,255,.55)}
.hero p{color:var(--mu2);font-size:18px;line-height:1.55;max-width:440px;margin:30px 0 38px}.hero p b{color:var(--off);font-weight:500}
.hero .lg{height:64px;width:auto;margin-bottom:24px}
.faixa{height:120px;background:url(FEIXE) center/cover no-repeat}
.bt{display:inline-block;background:var(--rx);color:#fff;font-weight:700;font-size:12px;letter-spacing:.3em;text-transform:uppercase;padding:16px 30px;border-radius:99px;box-shadow:var(--glow)}
.bt.esc{background:transparent;color:var(--tx);border:1px solid var(--tx);box-shadow:none}.escuro .bt.esc{color:var(--off);border-color:var(--off)}
.tit{font-weight:300;font-size:48px;line-height:1.08;letter-spacing:-.02em;margin:14px 0 0}
.tit span{color:var(--rx)}.escuro .tit span{color:var(--rxl);text-shadow:0 0 28px rgba(168,139,255,.45)}
.tit.c,.c{text-align:center}
.tit2{font-weight:300;font-size:48px;letter-spacing:-.02em;margin:14px 0 0}
.tag{display:inline-block;border:1px solid currentColor;font-size:10px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;padding:6px 10px;border-radius:99px}
/* último episódio */
.ultimo{display:grid;grid-template-columns:1.15fr 1fr;gap:72px;align-items:center;padding:110px 0}
.ultimo .fig img{border-radius:8px;box-shadow:0 0 0 1px rgba(168,139,255,.25),0 0 60px rgba(135,98,243,.28)}
.meta{display:flex;gap:16px;align-items:center;font-size:12px;color:var(--mu);margin-bottom:6px}
.ultimo .nome{font-size:22px;line-height:1.35;font-weight:500;margin:22px 0 14px}
.ultimo p{color:var(--mu);font-size:15px;margin:0 0 32px}
/* carrossel */
.cinza{padding:110px 0 96px;text-align:center}
.cinza .bt{margin:28px 0 56px}
.carro{display:grid;grid-template-columns:1fr 1.15fr 1fr;gap:32px;align-items:center}
.ep{background:var(--gr);border:1px solid var(--lnd);border-radius:10px;padding:10px;text-align:left;opacity:.7}
.ep img{border-radius:6px;aspect-ratio:16/9;object-fit:cover;width:100%}
.ep p{font-size:14px;font-weight:500;margin:14px 6px 8px;line-height:1.4;color:var(--off)}
.ep.on{opacity:1;border-color:var(--rxl);box-shadow:var(--glow)}
.pontos{display:flex;gap:10px;justify-content:center;margin-top:48px}.pontos i{width:8px;height:8px;border-radius:50%;background:var(--mu2);opacity:.5}.pontos i.r{background:var(--rxl);opacity:1;box-shadow:0 0 10px var(--rxl)}
/* lista */
.lista{padding:90px 0 100px}
.filtros{display:flex;gap:10px;margin:28px 0 48px;flex-wrap:wrap}.filtros span{font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--mu);border:1px solid var(--ln);border-radius:99px;padding:8px 16px}.filtros span.on{color:#fff;background:var(--rx);border-color:var(--rx);box-shadow:var(--glow)}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:48px 28px}
.it img{aspect-ratio:16/10;object-fit:cover;border-radius:8px;width:100%}
.it .n{font-size:15px;font-weight:500;margin:16px 0 4px;line-height:1.35}.it .s{font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--rx)}
.escuro .it .n{color:var(--off)}.escuro .it .s{color:var(--rxl)}
/* fotos */
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:52px 32px}
.foto img{aspect-ratio:4/5;object-fit:cover;border-radius:8px;width:100%}
.foto .tl{display:flex;justify-content:space-between;align-items:center;margin:18px 0 6px}.foto .tl b{font-weight:300;font-size:30px;letter-spacing:-.01em}
.foto p{font-size:14px;color:var(--mu);margin:0;line-height:1.55}.foto .cr{font-size:11px;color:var(--mu2);margin-top:8px}
/* sobre */
.secao{padding:110px 0}
.fotos{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-top:48px}.fotos img{aspect-ratio:4/5;object-fit:cover;border-radius:8px}
.fotos img:nth-child(3){box-shadow:0 0 0 1px var(--rxl),var(--glow)}
.bruno{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center}
.bruno h2{font-weight:300;font-size:64px;line-height:1;letter-spacing:-.03em;margin:18px 0 26px;color:var(--off)}.bruno h2 span{color:var(--rxl);text-shadow:0 0 30px rgba(168,139,255,.5)}
.bruno p{color:var(--mu2);font-size:16px;margin:0 0 14px;max-width:480px}
.bruno .ft img{width:100%;max-width:540px;margin:0 auto}
.porque{display:grid;grid-template-columns:1fr 1.6fr;gap:72px}
.porque p{color:var(--mu);font-size:16px;margin:0 0 16px}
.passos{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:40px}.passos div{border-top:1px solid var(--ln);padding-top:18px;font-size:14px;color:var(--mu)}.passos i{font-style:normal;display:block;font-weight:300;font-size:46px;line-height:1;color:var(--tx);margin-bottom:12px}.passos b{display:block;color:var(--tx);font-weight:500;margin-bottom:4px}
/* contato */
.contato{display:grid;grid-template-columns:1fr 1fr;min-height:600px}
.contato .roxo{background:var(--rx);position:relative;overflow:hidden}
.contato .roxo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;mix-blend-mode:luminosity;opacity:.8}
.contato .form{padding:80px 72px}
.contato h2{font-weight:300;font-size:52px;letter-spacing:-.02em;margin:16px 0 14px}
.caixa{background:var(--esc) url(GRAO) repeat;border-radius:10px;padding:30px;margin:32px 0 24px;color:var(--mu2);font-size:12px;font-weight:700;letter-spacing:.2em;text-transform:uppercase}
.campo{border-bottom:1px solid var(--lnd);padding:16px 0 10px;margin-bottom:18px}.campo.g{height:120px}
.parceria{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center;padding:110px 0}
.parceria h2{font-weight:300;font-size:56px;line-height:1.02;letter-spacing:-.025em;margin:16px 0 20px}.parceria h2 span{color:var(--rxl);text-shadow:0 0 30px rgba(168,139,255,.5)}
.parceria p{color:var(--mu2);margin:0 0 32px;max-width:420px}
.circ{width:380px;height:380px;border-radius:50%;margin:0 auto;overflow:hidden;box-shadow:0 0 0 2px var(--rxl),0 0 60px rgba(135,98,243,.6)}.circ img{width:100%;height:100%;object-fit:cover}
/* vídeo */
.v-hero{display:grid;grid-template-columns:1.3fr 1fr;gap:48px;align-items:center;padding:70px 0 110px}
.v-hero h1{font-weight:300;font-size:58px;line-height:1.04;letter-spacing:-.025em;margin:18px 0 24px;color:var(--off)}
.v-hero h1 span{color:var(--rxl);text-shadow:0 0 30px rgba(168,139,255,.5)}
.v-hero p{color:var(--mu2);font-size:17px;margin:0}
.v-hero .num{text-align:center}.v-hero .num b{display:block;font-weight:300;font-size:110px;line-height:1;letter-spacing:-.03em;color:var(--off)}.v-hero .num span{display:block;margin-top:14px}
.player{position:relative;aspect-ratio:16/9;border-radius:10px;overflow:hidden;background:#000;margin-top:-60px;box-shadow:0 0 0 1px rgba(168,139,255,.3),0 0 80px rgba(135,98,243,.35)}
.player iframe,.player img{position:absolute;inset:0;width:100%;height:100%;border:0;object-fit:cover}
.play{position:absolute;left:50%;top:50%;width:92px;height:92px;margin:-46px 0 0 -46px;border-radius:50%;background:var(--rx);box-shadow:var(--glow);display:flex;align-items:center;justify-content:center}.play:after{content:"";border-left:22px solid #fff;border-top:13px solid transparent;border-bottom:13px solid transparent;margin-left:7px}
.corpo{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:72px;padding:90px 0 100px}
.texto h2{font-weight:300;font-size:40px;letter-spacing:-.02em;margin:48px 0 16px}.texto h2:first-child{margin-top:0}
.texto p{color:#3D3A44;font-size:17px;line-height:1.75;margin:0 0 20px}
.texto .cap{font-weight:700;font-size:11px;letter-spacing:.34em;text-transform:uppercase;color:var(--rx);margin:36px 0 8px}
.lado{background:var(--esc) url(GRAO) repeat;color:var(--off);border-radius:10px;padding:30px;align-self:start}
.lado h4{font-weight:700;font-size:11px;letter-spacing:.34em;text-transform:uppercase;color:var(--rxl);margin:0 0 12px}
.lado ul{list-style:none;padding:0;margin:0 0 30px}.lado li{padding:10px 0;border-bottom:1px solid var(--lnd);font-size:13px;line-height:1.45;color:#D6D2DC}
.lado li b{color:var(--rxl);margin-right:10px;font-weight:500}
.selo{display:inline-block;font-size:9.5px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;padding:4px 9px;border-radius:99px;margin-bottom:6px;color:#fff;background:#4A4654}
.selo.c{background:#2E9A5B}.selo.f{background:#3A6FC4}.selo.d{background:#C9861F}.selo.h{background:var(--rx)}
.fontes{counter-reset:f;list-style:none;padding:0;margin:0}.fontes li{counter-increment:f;padding:12px 0 12px 44px;position:relative;border-bottom:1px solid var(--ln);font-size:14px;color:#3D3A44}
.fontes li:before{content:counter(f,decimal-leading-zero);position:absolute;left:0;font-weight:700;font-size:12px;letter-spacing:.2em;color:var(--rx)}.fontes a{color:var(--rx);word-break:break-word}
/* rodapé */
.rod{background:var(--esc) url(GRAO) repeat;color:var(--mu2);font-size:12px}
.rod .w1{display:grid;grid-template-columns:1fr 1fr auto;gap:40px;align-items:center;padding:64px 0}
.rod .w1 img{height:42px;width:auto;margin-bottom:14px}.rod .w1 .soc{margin-top:16px}
.rod .plat{display:flex;gap:22px;font-size:11px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--off)}
.rod .w2{border-top:1px solid var(--lnd)}.rod .w2 .w{display:flex;justify-content:space-between;align-items:center;height:64px;font-size:10px;letter-spacing:.2em;text-transform:uppercase}
.rod .w2 .sim{width:10px;height:10px;border-radius:50%;background:var(--rxl);box-shadow:0 0 12px var(--rxl)}
"""

MOB = """
.w{padding:0 20px}.nav{height:64px}.nav .logo img{height:28px}.menu{display:none}
.hero{grid-template-columns:minmax(0,1fr);min-height:0;padding:40px 0 0}.hero .img{height:260px}.marca-h{font-size:58px}
.ultimo,.bruno,.porque,.contato,.parceria,.v-hero{grid-template-columns:minmax(0,1fr);gap:36px}.ultimo{padding:64px 0}
.carro{grid-template-columns:minmax(0,1fr)}.carro .ep:not(.on){display:none}
.g4,.g3{grid-template-columns:repeat(2,minmax(0,1fr));gap:28px 14px}.fotos{grid-template-columns:repeat(2,1fr)}.fotos img:nth-child(n+5){display:none}
.tit,.tit2{font-size:34px}.bruno h2{font-size:44px}.contato .form{padding:44px 20px}.contato h2{font-size:38px}.parceria h2{font-size:40px}.circ{width:260px;height:260px}
.v-hero{padding:40px 0 80px}.v-hero h1{font-size:34px}.v-hero .num b{font-size:72px}.corpo{grid-template-columns:minmax(0,1fr);gap:40px}.passos{grid-template-columns:minmax(0,1fr)}
.rod .w1{grid-template-columns:minmax(0,1fr);gap:24px}.rod .w2 .w{height:auto;padding:16px 20px;flex-direction:column;gap:10px}
"""
for f_ in ("hero_anel.jpg", "anel_pag.jpg", "feixe.jpg", "bruno_anel.jpg", "bruno_foto.jpg", "grao.png"): shutil.copy(AQUI + "/arte/" + f_, OUT + "img/" + f_)
open(OUT + "estilo.css", "w").write((CSS + "@media (max-width:820px){" + MOB + "}").replace("url(GRAO)", "url(img/grao.png)").replace("url(FEIXE)", "url(img/feixe.jpg)"))
YT = "https://www.youtube.com/@estrelanegra_p"; INSTA = "https://www.instagram.com/estrelanegra_p/"; TT = "https://www.tiktok.com/@estrelanegra_p"
SOC = '<div class="soc"><a href="%s" title="YouTube">YT</a><a href="%s" title="Instagram">IG</a><a href="%s" title="TikTok">TT</a></div>' % (YT, INSTA, TT)
def cabeca(t, d, u, img, tipo, raiz, ativo, ld=""):
    m = [("", "Início"), ("episodios/", "Episódios"), ("fotos/", "Fotos do céu"), ("sobre/", "Sobre"), ("contato/", "Contato")]
    menu = "".join('<a class="%s" href="%s%s">%s</a>' % ("on" if k == ativo else "", raiz, k, n) for k, n in m)
    return ("""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:image" content="%s"><meta property="og:type" content="%s">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="%sestilo.css">%s</head><body>
<div class="topo"><div class="w"><nav class="nav"><a class="logo" href="%s"><img src="%simg/logo.png" alt="Estrela Negra"></a><div class="menu">%s</div>%s</nav></div>""" % (t, d, u, t, d, img, tipo, raiz, ld, raiz, raiz, menu, SOC))
def rodape(raiz):
    return """<footer class="rod"><div class="w"><div class="w1"><div><img src="%simg/logo.png" alt="Estrela Negra"><div>Estrela Negra · astronomia com fonte</div>%s</div><div class="plat"><a href="%s">YouTube</a><a href="%s">Instagram</a><a href="%s">TikTok</a></div><a class="bt" href="%scontato/">Entre em contato</a></div></div>
<div class="w2"><div class="w"><span>Estrela Negra © 2026 · todos os direitos reservados · identidade visual, animação e locução: Bruno Porciúncula (com auxílio da Inteligência da Anthropic)</span><span class="sim"></span></div></div></footer></body></html>""" % (raiz, SOC, YT, INSTA, TT, raiz)
def destaca(t):
    p = t.split(); k = 2 if len(p) > 3 and len(p[-1]) < 5 else 1
    return e(" ".join(p[:-k])) + ' <span>%s</span>' % e(" ".join(p[-k:]))
CAT = [("Buracos negros e estrelas", r"buraco|estrela|betelgeuse|pulsar|supernova|T Coronae|Siwarha"), ("Sistema Solar", r"Merc|Lua|Mars|asteroide|cometa|ATLAS|Voyager|Artemis|eclipse|quase"),
       ("Universo", r"universo|energia escura|Hubble|ondas|gravidade|Webb|Rubin|DESI|rádio|TRAPPIST")]
def cat(t):
    for n, r in CAT:
        if re.search(r, t, re.I): return n
    return "Universo"
def ytseg(t): a, b = t.split(":"); return int(a) * 60 + int(b)
def it(d, raiz):
    return '<a class="it" href="%s%s/"><img src="%s%s" alt="%s" loading="lazy"><p class="n">%s</p><p class="s">%s · %d fontes</p></a>' % (raiz, d["sl"], raiz, d["img"], e(d["titulo"]), e(d["titulo"]), cat(d["titulo"]), len(d["fontes"]))
def topo_hero(rot, titulo, texto, arte, extra="", alt="420px"):
    return '<div class="w"><section class="hero" style="min-height:%s"><div><span class="rot">%s</span><h1 class="marca-h">%s</h1>%s%s</div><div class="img" style="background-image:url(%s)"></div></section></div></div>' % (alt, rot, titulo, '<p>%s</p>' % texto if texto else "", extra, arte)
# ------------------------------------------------------------------ início
desc0 = "Vídeos de astronomia com fonte: o que se sabe, o que está em debate e de onde vem cada número."
h = [cabeca("Estrela Negra · astronomia com fonte", desc0, URL, URL + "img/hero_anel.jpg", "website", "", "")]
h.append(topo_hero("Canal de astronomia", "Estrela<br><span>Negra</span>", "Buracos negros, estrelas, missões e descobertas. <b>O que já é certo, o que ainda está em debate e de onde vem cada número.</b>", "img/hero_anel.jpg", '<a class="bt" href="%s?sub_confirmation=1">Inscreva-se no canal</a>' % YT, "560px"))
if DADOS:
    d = DADOS[0]
    h.append('<div class="w"><section class="ultimo"><div class="fig"><img src="%s" alt="%s"></div><div><span class="rot">Último episódio</span><h2 class="tit">Confira o<br><span>último episódio</span></h2><p class="nome">%s</p><p>%s</p><div class="meta" style="margin-bottom:28px"><span class="tag" style="color:var(--rx)">%s</span><span>%d fontes conferidas</span></div><a class="bt" href="%s/">Assistir agora</a></div></section></div>' % (d["img"], e(d["titulo"]), e(d["titulo"]), e((d["resumo"][0] if d["resumo"] else "")[:240]), cat(d["titulo"]), len(d["fontes"]), d["sl"]))
if len(DADOS) > 3:
    tres = DADOS[1:4]
    h.append('<section class="cinza escuro"><div class="w"><span class="rot">Episódios</span><h2 class="tit c">Últimos <span>episódios</span></h2><a class="bt esc" href="episodios/">Ver todos</a><div class="carro">%s</div><div class="pontos"><i></i><i class="r"></i><i></i></div></div></section>' % "".join('<a class="ep%s" href="%s/"><img src="%s" alt="%s"><p>%s</p></a>' % (" on" if k == 1 else "", x["sl"], x["img"], e(x["titulo"]), e(x["titulo"])) for k, x in enumerate(tres)))
h.append('<div class="w"><section class="secao c"><span class="rot">Instagram</span><h2 class="tit c">Uma foto do céu <span>por dia</span></h2><p style="color:var(--mu);margin:16px 0 0">Imagens dos telescópios James Webb, Hubble e ESO, explicadas.</p><div class="fotos">%s</div><p style="margin-top:44px"><a class="bt" href="%s">Seguir @estrelanegra_p</a></p></section></div>' % ("".join('<img src="%s" alt="Foto de telescópio" loading="lazy">' % x for x in IG[:5]), INSTA))
h.append(rodape("")); open(OUT + "index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ episódios
os.makedirs(OUT + "episodios")
h = [cabeca("Episódios · Estrela Negra", desc0, URL + "episodios/", URL + "img/anel_pag.jpg", "website", "../", "episodios/")]
h.append(topo_hero("%d vídeos · %d fontes" % (len(DADOS), NFONTES), "Todos os<br><span>episódios</span>", "Cada vídeo com transcrição, grau de certeza e fontes.", "../img/anel_pag.jpg"))
h.append('<div class="w"><section class="lista"><span class="rot">Lista</span><h2 class="tit2">Lista de <span style="color:var(--rx)">episódios</span></h2><div class="filtros"><span class="on">Todos</span>%s</div><div class="g4">%s</div><div class="pontos"><i></i><i class="r"></i></div></section></div>' % ("".join("<span>%s</span>" % n for n, _ in CAT), "".join(it(d, "../") for d in DADOS)))
h.append(rodape("../")); open(OUT + "episodios/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ fotos do céu
FC = json.load(open(B + "/motion/INSTAGRAM/FOTO_DO_CEU/foto_do_ceu.json", encoding="utf-8"))
os.makedirs(OUT + "fotos")
cards = []
for k, x in enumerate(FC):
    if not os.path.exists(x["foto"]): continue
    im = Image.open(x["foto"]).convert("RGB"); W_, H_ = im.size; s_ = int(min(W_, H_) / max(1.0, x.get("zoom", 1.0)))
    cx, cy = int(x.get("fx", .5) * W_), int(x.get("fy", .5) * H_); l_ = min(max(0, cx - s_ // 2), W_ - s_); t_ = min(max(0, cy - s_ // 2), H_ - s_)
    im = im.crop((l_, t_, l_ + s_, t_ + s_)); im.thumbnail((560, 560)); im.save(OUT + "img/fc_%02d.jpg" % k, quality=84)
    tel = x["tag"].split("·")[-1].strip().title()
    cards.append('<div class="foto"><img src="../img/fc_%02d.jpg" alt="%s" loading="lazy"><div class="tl"><b>%s</b><span class="tag" style="color:var(--rx)">%s</span></div><p>%s %s</p><p class="cr">Imagem: %s</p></div>' % (k, e(x["titulo"]), e(x["num"]), e(tel), e(x["l1"].rstrip('.') + '.'), e(x["l2"].rstrip('.') + '.'), e(x["cred"])))
h = [cabeca("Fotos do céu · Estrela Negra", "Fotos dos telescópios James Webb, Hubble, ESO e outros, explicadas.", URL + "fotos/", URL + "img/fc_00.jpg", "website", "../", "fotos/")]
h.append('<div class="w"><section class="hero" style="min-height:420px"><div><span class="rot">James Webb · Hubble · ESO</span><h1 class="marca-h" style="font-size:84px">Fotos<br><span>do céu</span></h1><p>As imagens mais bonitas dos telescópios, explicadas: o que é cada parte, a que distância está e o que as cores querem dizer.</p></div><div class="img" style="background-image:url(../img/fc_00.jpg)"></div></section></div></div>')
h.append('<div class="w"><section class="lista"><span class="rot">Galeria</span><h2 class="tit2">Uma foto por dia, <span style="color:var(--rx)">explicada</span></h2><div class="filtros"><span class="on">Todas</span><span>James Webb</span><span>Hubble</span><span>ESO</span><span>Outros</span></div><div class="g3">%s</div></section></div>' % "".join(cards))
h.append(rodape("../")); open(OUT + "fotos/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ sobre
os.makedirs(OUT + "sobre")
h = [cabeca("Sobre · Estrela Negra", desc0, URL + "sobre/", URL + "img/bruno_foto.jpg", "website", "../", "sobre/")]
h.append(topo_hero("Sobre o canal", "Astronomia<br><span>com fonte</span>", "Um canal sobre o universo que diz o que é certo, o que é debate e o que é hipótese.", "../img/sobre.jpg"))
h.append('<div class="w"><section class="secao c"><span class="rot">Galeria</span><h2 class="tit c">O céu visto pelos <span>telescópios</span></h2><div class="fotos">%s</div><div class="pontos"><i></i><i class="r"></i></div></section></div>' % "".join('<img src="../%s" alt="Foto de telescópio" loading="lazy">' % x for x in IG[:5]))
h.append('<section class="escuro"><div class="w"><div class="secao bruno"><div><span class="rot">Quem faz</span><h2>Bruno<br><span>Porciúncula.</span></h2><p>Designer e editor de vídeo, estudou Física na UFSCar e é apaixonado por astronomia desde criança, quando maratonava documentários sobre o espaço na TV.</p><p>O Estrela Negra nasceu como podcast e hoje é um canal de vídeo sobre o universo, com identidade visual, animação e locução feitas por ele.</p><p style="margin-top:28px"><a class="bt" href="%s?sub_confirmation=1">Assista o canal</a></p></div><div class="ft"><img src="../img/bruno_foto.jpg" alt="Bruno Porciúncula"></div></div></div></section>' % YT)
h.append('<div class="w"><section class="secao porque"><div><span class="rot">Por que assistir</span><h2 class="tit">Por que assistir o<br><span>Estrela Negra?</span></h2><p style="margin-top:28px"><a class="bt" href="../episodios/">Ver episódios</a></p></div><div><p>Cada vídeo explica um assunto do universo do jeito que se conta para um amigo, sem deixar de lado o rigor: toda afirmação tem fonte, e o vídeo diz com que grau de certeza a ciência sabe o que está sendo contado.</p><div class="passos"><div><i>01</i><b>Fonte primária</b>Agências, observatórios e artigos científicos, com link.</div><div><i>02</i><b>Revisão independente</b>Um segundo revisor confere o roteiro frase a frase.</div><div><i>03</i><b>Grau de certeza</b>Hipótese é dita como hipótese; previsão, como previsão.</div></div></div></section></div>')
h.append(rodape("../")); open(OUT + "sobre/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ contato
os.makedirs(OUT + "contato")
h = [cabeca("Contato · Estrela Negra", desc0, URL + "contato/", URL + "img/webb.jpg", "website", "../", "contato/"), "</div>"]
h.append('<section class="contato"><div class="roxo"><img src="../img/webb.jpg" alt="Espelho do telescópio James Webb"></div><div class="form"><span class="rot">Contato</span><h2>Fale com<br><span style="color:var(--rx)">a gente!</span></h2><p style="color:var(--mu);font-size:15px;margin:0">Dúvidas, sugestões de tema, correções e parcerias. A gente lê tudo.</p><div class="caixa"><a class="campo" style="display:block;color:var(--off)" href="%s">Mensagem direta no Instagram →</a><a class="campo" style="display:block;color:var(--off)" href="%s">Comentários no YouTube →</a><a class="campo" style="display:block;color:var(--off);border:0" href="%s">TikTok →</a></div><a class="bt" href="%s">Mandar mensagem</a></div></section>' % (INSTA, YT, TT, INSTA))
h.append('<section class="escuro"><div class="w"><div class="parceria"><div><span class="rot">Parcerias</span><h2>Quer fazer<br><span>uma parceria?</span></h2><p>Planetários, escolas, clubes de astronomia e divulgadores de ciência: vamos conversar.</p><a class="bt" href="%s">Falar no Instagram</a></div><div class="circ"><img src="../img/parceria.jpg" alt="Júpiter visto pelo James Webb"></div></div></div></section>' % INSTA)
h.append(rodape("../")); open(OUT + "contato/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ páginas de vídeo
for d in DADOS:
    desc = (d["resumo"][0] if d["resumo"] else d["titulo"])[:155]
    ld = '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@type": "VideoObject", "name": d["titulo"], "description": desc, "thumbnailUrl": URL + d["img"], "embedUrl": "https://www.youtube.com/embed/" + d["vid"], "contentUrl": "https://youtu.be/" + d["vid"], "inLanguage": "pt-BR"}, ensure_ascii=False)
    h = [cabeca(e(d["titulo"]) + " · Estrela Negra", e(desc), URL + d["sl"] + "/", URL + d["img"], "article", "../", "episodios/", ld)]
    num = '<div class="num"><b>%s</b><span class="rot">%s</span></div>' % (e(d["num"]), e(d["rot"])) if d["num"] else "<div></div>"
    h.append('<div class="w"><section class="v-hero"><div><span class="rot">%s · %d fontes</span><h1>%s</h1>%s</div>%s</section></div></div>' % (cat(d["titulo"]), len(d["fontes"]), destaca(d["titulo"]), '<p>%s</p>' % e(d["resumo"][0][:300]) if d["resumo"] else "", num))
    h.append('<div class="w"><div class="player"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s" loading="lazy" allowfullscreen></iframe></div><div class="corpo"><article class="texto">' % (d["vid"], e(d["titulo"])))
    if len(d["resumo"]) > 1: h += ["<p>%s</p>" % e(p) for p in d["resumo"][1:]]
    if d["transc"]:
        h.append('<h2>Transcrição</h2>'); nomes = [n for _, n in d["caps"]] if len(d["caps"]) == len(d["transc"]) else []
        for k, p in enumerate(d["transc"]):
            if nomes: h.append('<p class="cap">%s</p>' % e(nomes[k]))
            h.append("<p>%s</p>" % e(p))
    if d["fontes"]: h.append('<h2>Fontes</h2><ol class="fontes">' + "".join("<li>%s</li>" % re.sub(r"(https?://\S+)", r'<a href="\1" rel="nofollow">\1</a>', e(f)) for f in d["fontes"]) + "</ol>")
    if d["imgs"]: h.append('<p style="font-size:12px;color:var(--mu);margin-top:24px">Imagens: %s</p>' % e(d["imgs"]))
    h.append('</article><aside class="lado">')
    if d["caps"]: h.append("<h4>Capítulos</h4><ul>" + "".join('<li><a href="https://youtu.be/%s?t=%d"><b>%s</b>%s</a></li>' % (d["vid"], ytseg(t), e(t), e(n)) for t, n in d["caps"]) + "</ul>")
    cs = certezas(d["cert"])
    if cs: h.append("<h4>Grau de certeza</h4><ul>" + "".join("<li>%s<br>%s</li>" % ('<span class="selo %s">%s</span>' % (seloclasse(n), e(nivel(n))) if n else "", e(o)) for n, o in cs) + "</ul>")
    h.append('<a class="bt" style="display:block;text-align:center" href="https://youtu.be/%s">Assistir no YouTube</a><a class="bt esc" style="display:block;text-align:center;margin-top:10px;color:var(--off);border-color:var(--off)" href="%s?sub_confirmation=1">Inscrever-se</a></aside></div></div>' % (d["vid"], YT))
    outros = [x for x in DADOS if x is not d][:4]
    if outros: h.append('<section class="cinza escuro" style="text-align:left"><div class="w"><span class="rot">Continue</span><h2 class="tit">Mais <span>episódios</span></h2><div class="g4" style="margin-top:40px">%s</div></div></section>' % "".join(it(x, "../") for x in outros))
    h.append(rodape("../")); os.makedirs(OUT + d["sl"]); open(OUT + d["sl"] + "/index.html", "w", encoding="utf-8").write("\n".join(h))

hoje = datetime.date.today().isoformat()
urls = [URL, URL + "episodios/", URL + "fotos/", URL + "sobre/", URL + "contato/"] + [URL + d["sl"] + "/" for d in DADOS]
open(OUT + "sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, hoje) for u in urls) + "</urlset>")
open(OUT + "robots.txt", "w").write("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % URL); open(OUT + ".nojekyll", "w").write("")
print("ok", len(DADOS), "vídeos + 4 páginas", "(PRÉVIA COM TODOS)" if TODOS else "")

