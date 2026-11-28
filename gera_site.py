"""Site do Estrela Negra (GitHub Pages) · v7 (24/11: página /links da bio, uma página por Foto do céu, cartões de compartilhamento LUZ) · v6 (24/11/2026, refinado: ícones, menu no celular, filtros reais, sem carrossel falso) · base v4: segue a referência do site antigo do Bruno (cabeçalho e rodapé escuros, título em caixa alta com palavra em roxo, seções brancas).
Uma página por vídeo PÚBLICO (oEmbed = 200), com vídeo, o número do vídeo, capítulos, grau de certeza, transcrição e fontes.
Dados: motion/reels_NN/05_YOUTUBE/METADADOS_YOUTUBE.md · scripts/motion/tempos/tts/rNN.txt · motion/THUMBS_LUZ/TROCA_YOUTUBE.json (+ ids_extra.json)
· miniaturas THUMB_LUZ_NN_16x9.jpg · número/rótulo da tabela V de scripts/thumbs/thumbs_luz.py · artes do Instagram (FOTO_DO_CEU).
uso: python3 gera_site.py [--todos]   (--todos ignora o filtro de vídeo público: só para prévia/Figma; nunca publicar assim)"""
import json, re, os, sys, html, shutil, unicodedata, urllib.request, datetime, glob
from PIL import Image
B = "/Users/porciuncula/Desktop/BRUNO/estrela-negra"; AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = AQUI + "/docs/"
URL = "https://estrela-negra.github.io/"; TODOS = "--todos" in sys.argv
LOJA = json.load(open(AQUI + "/loja.json", encoding="utf-8")) if os.path.exists(AQUI + "/loja.json") else None
JORNAL = sorted([json.load(open(f, encoding="utf-8")) for f in glob.glob(AQUI + "/jornal/20*.json")], key=lambda x: x["data"], reverse=True)
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
def data_ext(iso, dia_semana=True):
    d = datetime.date.fromisoformat(iso); t = "%d de %s de %d" % (d.day, MESES[d.month - 1], d.year)
    return (DIAS[d.weekday()].capitalize() + ", " + t) if dia_semana else t
def ed_url(n): return "jornal/%s-%s/" % (n["data"], n["slug"])
COM_LOJA = bool(LOJA) and (LOJA.get("aprovado") or "--loja" in sys.argv)  # só publica com aprovação do Bruno
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
def corta(t, n):
    """corta no fim de frase (ou palavra) antes de n caracteres, sem deixar palavra pela metade"""
    if len(t) <= n: return t
    c = t[:n]; k = max(c.rfind(". "), c.rfind("? "), c.rfind("! "))
    return c[:k + 1] if k > n * .5 else c[:c.rfind(" ")].rstrip(",;:") + "…"
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
# ------------------------------------------------------------------ matérias: site/materias/<slug>.md (cabeçalho "chave: valor", linha ---, corpo com "## " intertítulos e "## Fontes" com "- nome: URL")
# endereço ESTÁVEL /materias/<slug>/ (o slug vem do arquivo, não do título; é o endereço do CTA no fim dos vídeos). Só publica se o vídeo da pasta reels_NN estiver público.
def le_materia(p):
    cab, _, corpo = open(p, encoding="utf-8").read().partition("\n---\n")
    m = dict(l.split(": ", 1) for l in cab.strip().split("\n") if ": " in l)
    if "slug" not in m or "reels" not in m: return None
    corpo, _, fon = corpo.partition("\n## Fontes")
    m["blocos"] = [("h2", b[3:].strip()) if b.startswith("## ") else ("p", b.replace("\n", " ")) for b in [x.strip() for x in corpo.split("\n\n") if x.strip()]]
    m["fontes"] = []
    for l in fon.split("\n"):
        l = l.strip()
        if not l.startswith("- "): continue
        u = re.search(r"(https?://\S+)$", l[2:]); m["fontes"].append((l[2:u.start() + 2].strip().rstrip(":").strip() if u else l[2:], u.group(1) if u else ""))
    m["nn"] = int(m["reels"]); return m
MATERIAS = []
for f in sorted(glob.glob(AQUI + "/materias/*.md")):
    m = le_materia(f); d = next((x for x in DADOS if m and x["nn"] == m["nn"]), None)
    if m and d: m["d"] = d; d["mat"] = m; MATERIAS.append(m)
MATERIAS.sort(key=lambda m: -m["nn"])
IG = []
for k, f in enumerate(sorted(glob.glob(B + "/motion/INSTAGRAM/FOTO_DO_CEU/img/f*.jpg"))[:10]):
    im = Image.open(f).convert("RGB"); s_ = min(im.size); im = im.crop(((im.width - s_) // 2, (im.height - s_) // 2, (im.width + s_) // 2, (im.height + s_) // 2)); im.thumbnail((900, 900), Image.LANCZOS); im.save(OUT + "img/ceu_%d.jpg" % k, quality=90); IG.append("img/ceu_%d.jpg" % k)
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
_sim = lg.copy(); _w, _h = _sim.size; _k = _w / 520.0
from PIL import ImageDraw as _ID
_m = Image.new("L", _sim.size, 255); _d = _ID.Draw(_m); _d.rectangle((int(258 * _k), int(78 * _k), _w, _h), fill=0); _d.rectangle((int(302 * _k), 0, _w, _h), fill=0)
_sim.putalpha(Image.composite(_sim.getchannel("A"), Image.new("L", _sim.size, 0), _m)); _sim = _sim.crop(_sim.getbbox()); _sim.save(OUT + "img/logo_simbolo.png")
shutil.copy(AQUI + "/arte/bruno_foto_recorte.webp", OUT + "img/bruno_foto_recorte.webp")
ic = Image.open(B + "/assets/marca/original_2020/logo_estrela_negra_transparente.png").convert("RGBA"); ic = ic.crop(ic.getbbox()); q = max(ic.size); fu = Image.new("RGBA", (q, q), (10, 9, 14, 255)); fu.alpha_composite(ic, ((q - ic.width) // 2, (q - ic.height) // 2)); fu.resize((180, 180), Image.LANCZOS).save(OUT + "img/icone.png")
import numpy as np
a_ = np.array(lg); br = (a_[..., 0] > 200) & (a_[..., 1] > 200) & (a_[..., 2] > 200); a_[br, 0:3] = (18, 16, 22); Image.fromarray(a_).save(OUT + "img/logo_escuro.png")
FILT_JS = '<script>document.querySelectorAll(".filtros").forEach(function(f){var bs=f.querySelectorAll("button"),its=document.querySelectorAll(f.dataset.alvo);bs.forEach(function(b){b.onclick=function(){bs.forEach(function(x){x.classList.toggle("on",x===b)});var v=b.dataset.f,n=0;its.forEach(function(i){var ok=!v||(i.dataset.c||"").indexOf(v)>-1;i.style.display=ok?"":"none";if(ok)n++});var z=document.querySelector(".vazio");if(z)z.style.display=n?"none":"block"}})})</script>'
# ------------------------------------------------------------------ cartões de compartilhamento (1200x630, identidade LUZ)
from PIL import ImageDraw, ImageFont, ImageFilter
FONTE = os.path.expanduser("~/Library/Fonts/SpaceGrotesk-VariableFont_wght.ttf")
def fonte(tam, peso):
    f = ImageFont.truetype(FONTE, tam); f.set_variation_by_axes([peso]); return f
os.makedirs(OUT + "img/og", exist_ok=True)
GR = Image.open(AQUI + "/arte/grao_esc.jpg").convert("RGB")
LOGO_OG = Image.open(B + "/assets/marca/original_2020/logo_estrela_negra_transparente.png").convert("RGBA"); LOGO_OG.thumbnail((150, 150))
def quebra(dr, txt, f, larg):
    ls, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if dr.textlength(t, font=f) <= larg: cur = t
        else: ls.append(cur); cur = w
    return ls + [cur]
def cartao(nome, rot, titulo, foto=None, fx=.5, fy=.5):
    """cartão 1200x630: fundo escuro com grão, foto à direita dissolvendo no escuro, rótulo roxo, título Light, logo e endereço"""
    W, H = 1200, 630
    im = GR.resize((max(W, GR.width), max(H, GR.height))).crop((0, 0, W, H))
    if foto and os.path.exists(foto):
        ft = Image.open(foto).convert("RGB"); s_ = min(ft.size); cx, cy = int(fx * ft.width), int(fy * ft.height)
        l_ = min(max(0, cx - s_ // 2), ft.width - s_); t_ = min(max(0, cy - s_ // 2), ft.height - s_)
        ft = ft.crop((l_, t_, l_ + s_, t_ + s_)).resize((H, H), Image.LANCZOS)
        m = Image.new("L", (H, H), 0); ImageDraw.Draw(m).ellipse((110, 90, H - 20, H - 90), fill=255); m = m.filter(ImageFilter.GaussianBlur(85))
        im.paste(ft, (W - H + 60, 0), m)
    dr = ImageDraw.Draw(im)
    f_rot = fonte(19, 700); x = 72
    dr.text((x, 92), "  ".join(rot.upper()), font=f_rot, fill=(168, 139, 255))
    tam = 66 if len(titulo) < 40 else 54 if len(titulo) < 70 else 46
    f_t = fonte(tam, 300); ls = quebra(dr, titulo, f_t, 640 if foto else 1040)[:4]
    y = 150; brilho = Image.new("RGBA", (W, H), (0, 0, 0, 0)); db = ImageDraw.Draw(brilho)
    for i, l in enumerate(ls):
        ult = i == len(ls) - 1
        if ult:
            p_ = l.split(); a, b = " ".join(p_[:-1]), p_[-1]
            dr.text((x, y), a, font=f_t, fill=(241, 238, 233)); xb = x + (dr.textlength(a + " ", font=f_t) if a else 0)
            db.text((xb, y), b, font=f_t, fill=(168, 139, 255, 255)); dr.text((xb, y), b, font=f_t, fill=(168, 139, 255))
        else: dr.text((x, y), l, font=f_t, fill=(241, 238, 233))
        y += int(tam * 1.12)
    im = Image.alpha_composite(im.convert("RGBA"), brilho.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .55))); im.alpha_composite(brilho); dr = ImageDraw.Draw(im)
    im.alpha_composite(LOGO_OG, (x - 8, H - 40 - LOGO_OG.height))
    dr.text((x + LOGO_OG.width + 6, H - 40 - 30), "ESTRELA-NEGRA.GITHUB.IO", font=fonte(17, 700), fill=(156, 152, 165))
    im.convert("RGB").save(OUT + "img/og/%s.jpg" % nome, quality=86); return URL + "img/og/%s.jpg" % nome
def cartao_video(d):
    th = B + "/motion/THUMBS_LUZ/THUMB_LUZ_%02d_16x9.jpg" % d["nn"]
    if not os.path.exists(th): return URL + d["img"]
    im = Image.open(th).convert("RGB"); im = im.resize((1200, int(1200 * im.height / im.width)), Image.LANCZOS); t_ = (im.height - 630) // 2
    im.crop((0, t_, 1200, t_ + 630)).save(OUT + "img/og/v_%s.jpg" % d["sl"], quality=86); return URL + "img/og/v_%s.jpg" % d["sl"]
L5 = B + "/motion/INSTAGRAM/LOTE5/fotos/"
OG = {"inicio": cartao("inicio", "Canal de astronomia", "Astronomia com fonte: o que é certo, o que é debate", L5 + "T1412_saturno_aneis_cassini.jpg"),
      "episodios": cartao("episodios", "Todos os episódios", "Vídeos de astronomia com transcrição e fontes", B + "/motion/INSTAGRAM/FOTO_DO_CEU/img/f05_jupiter_webb.jpg"),
      "fotos": cartao("fotos", "James Webb · Hubble · ESO", "Uma foto do céu por dia, explicada", B + "/motion/INSTAGRAM/FOTO_DO_CEU/img/f01_pilares_webb.jpg", .55, .36),
      "sobre": cartao("sobre", "Sobre o canal", "Um canal sobre o universo que diz o que é certo", B + "/motion/reels_23/00_IMAGENS/c01_lua_cruzando_terra_dscovr.jpg"),
      "contato": cartao("contato", "Contato", "Fale com a gente: dúvidas, temas e parcerias", L5 + "T2012_webb_espelho.jpg")}
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

CSS += """
/* ---------- jornal ---------- */
.serif{font-family:'Newsreader',Georgia,serif}
.jn{padding:96px 0 104px}
.mast{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px double var(--tx);padding-bottom:14px;margin-bottom:34px;gap:20px}
.mast .nome{font-family:'Newsreader',Georgia,serif;font-weight:500;font-size:44px;letter-spacing:-.01em;line-height:1}
.mast .nome em{font-style:italic;color:var(--rx)}
.mast .ed{font-size:11px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--mu);text-align:right;line-height:1.8}
.manchete{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:48px;align-items:start}
.chapeu{font-size:11px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:var(--rx)}
.manchete h2,.art h1{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:46px;line-height:1.08;letter-spacing:-.015em;margin:14px 0 16px}
.manchete h2 a:hover{color:var(--rx)}
.fina{font-family:'Newsreader',Georgia,serif;font-style:italic;font-size:21px;line-height:1.45;color:#4A4652;margin:0 0 20px}
.manchete .lide{font-size:16px;line-height:1.75;color:#3D3A44;margin:0 0 22px}
.manchete figure,.art figure{margin:0}.manchete img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:4px}
figcaption.cr{font-size:11px;color:var(--mu);margin-top:8px;line-height:1.5}
.lermais{font-size:12px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--rx);border-bottom:1px solid var(--rx);padding-bottom:3px}
.anteriores{margin-top:44px;border-top:1px solid var(--ln);display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 32px}
.anteriores a{display:block;padding:18px 0;border-bottom:1px solid var(--ln)}.anteriores a:hover b{color:var(--rx)}
.anteriores span{display:block;font-size:10px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--mu);margin-bottom:6px}
.anteriores b{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:19px;line-height:1.3}
.art{max-width:760px;margin:0 auto;padding:72px 0 40px}
.art .meta2{font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--mu);border-top:1px solid var(--ln);border-bottom:1px solid var(--ln);padding:12px 0;margin:8px 0 32px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.art figure img{width:100%;max-height:520px;object-fit:cover;border-radius:4px}
.art .corpo2 p{font-family:'Newsreader',Georgia,serif;font-size:21px;line-height:1.65;color:#25222B;margin:0 0 22px}
.art .corpo2 p:first-child:first-letter{float:left;font-size:72px;line-height:.86;padding:6px 10px 0 0;color:var(--rx)}
.certeza{border-left:3px solid var(--rx);padding:4px 0 4px 18px;margin:30px 0;font-size:15px;color:#3D3A44}
.certeza b{display:block;font-size:10px;letter-spacing:.24em;text-transform:uppercase;color:var(--rx);margin-bottom:4px}
.acervo{max-width:860px;margin:0 auto;padding:72px 0 100px}.acervo h3{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:28px;margin:44px 0 6px;border-bottom:3px double var(--tx);padding-bottom:8px}
.acervo a{display:grid;grid-template-columns:120px minmax(0,1fr);gap:20px;padding:18px 0;border-bottom:1px solid var(--ln)}.acervo a:hover b{color:var(--rx)}
.acervo time{font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--mu);padding-top:5px}
.acervo b{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:22px;line-height:1.3;display:block}.acervo i{font-style:normal;display:block;font-size:14px;color:var(--mu);margin-top:4px}
""" + """
/* ---------- v6 ---------- */
::selection{background:var(--rx);color:#fff}
a,.bt,.it img,.ep,.foto img,.fotos img,.soc a{transition:all .25s ease}
a:focus-visible{outline:2px solid var(--rxl);outline-offset:3px}
.topo{position:relative}
.nav{position:relative;z-index:5}
.nav .logo img{height:44px}
.menu a:hover{color:var(--off)}
.soc a{width:36px;height:36px}.soc a svg{width:15px;height:15px;fill:currentColor}
.soc a:hover{border-color:var(--rxl);color:var(--rxl);box-shadow:0 0 18px rgba(168,139,255,.45)}
.bt:hover{background:var(--rxl);box-shadow:0 0 36px rgba(168,139,255,.7);transform:translateY(-1px)}
.bt.esc:hover{background:var(--tx);color:var(--off)}.escuro .bt.esc:hover,.lado .bt.esc:hover{background:var(--off);color:var(--esc)}
.bt.lin{background:transparent;border:1px solid var(--lnd);color:var(--off);box-shadow:none;margin-left:12px}.bt.lin:hover{border-color:var(--rxl);color:var(--rxl);background:transparent}
.hero{position:relative;padding:56px 0 72px}
.rod{border-top:1px solid var(--lnd)}
.hero .img{-webkit-mask-image:radial-gradient(ellipse 62% 70% at 60% 50%,#000 42%,transparent 72%);mask-image:radial-gradient(ellipse 62% 70% at 60% 50%,#000 42%,transparent 72%);min-height:420px}
.hero .lead{max-width:470px}
.numeros{display:flex;gap:44px;margin-top:48px;padding-top:26px;border-top:1px solid var(--lnd)}
.numeros b{display:block;font-weight:300;font-size:40px;line-height:1;letter-spacing:-.02em;color:var(--off)}.numeros span{display:block;margin-top:8px;font-size:10px;font-weight:700;letter-spacing:.26em;text-transform:uppercase;color:var(--mu2)}
.ultimo .fig{position:relative;display:block}.ultimo .fig:after{content:"";position:absolute;left:50%;top:50%;width:76px;height:76px;margin:-38px 0 0 -38px;border-radius:50%;background:rgba(135,98,243,.92) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='M8 5v14l11-7z'/%3E%3C/svg%3E") center/30px no-repeat;box-shadow:var(--glow);opacity:0;transform:scale(.85);transition:all .25s}
.ultimo .fig:hover:after{opacity:1;transform:none}.ultimo .fig:hover img{box-shadow:0 0 0 1px var(--rxl),0 0 80px rgba(135,98,243,.5)}
.trio{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px;text-align:left}
.ep{opacity:1}.ep:hover{border-color:var(--rxl);box-shadow:var(--glow);transform:translateY(-4px)}
.ep .s{font-size:10px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--rxl);margin:0 6px 6px}
.it{display:block}.it:hover img{box-shadow:0 0 0 1px var(--rxl),0 0 40px rgba(135,98,243,.45);transform:translateY(-4px)}.it:hover .n{color:var(--rx)}.escuro .it:hover .n{color:var(--rxl)}
.metodo{padding:110px 0}.metodo .passos{margin-top:56px}.metodo .passos div{border-color:var(--lnd);color:var(--mu2)}.metodo .passos i{color:var(--rxl);text-shadow:0 0 24px rgba(168,139,255,.5)}.metodo .passos b{color:var(--off)}
.fotos a{display:block;overflow:hidden;border-radius:8px}.fotos a:hover img{transform:scale(1.05)}.fotos img:nth-child(3){box-shadow:none}
.filtros button{font:inherit;font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--mu);background:transparent;border:1px solid var(--ln);border-radius:99px;padding:8px 16px;cursor:pointer;transition:all .2s}
.filtros button:hover{border-color:var(--rx);color:var(--rx)}.filtros button.on{color:#fff;background:var(--rx);border-color:var(--rx);box-shadow:var(--glow)}
.vazio{display:none;color:var(--mu);padding:40px 0}
.foto img{transition:all .25s}.foto:hover img{opacity:.9}
.lado{position:sticky;top:24px}
.lado li a:hover{color:var(--off)}
.texto .cap{scroll-margin-top:24px}
.fontes a{text-decoration:underline;text-decoration-color:rgba(135,98,243,.35);text-underline-offset:3px}
.navv{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:56px}.navv a{border:1px solid var(--ln);border-radius:10px;padding:20px 22px}.navv a:hover{border-color:var(--rx)}.navv span{display:block;font-size:10px;font-weight:700;letter-spacing:.26em;text-transform:uppercase;color:var(--rx);margin-bottom:6px}.navv b{font-weight:500;font-size:15px;line-height:1.35}.navv a.d{text-align:right}
.v-hero.so{grid-template-columns:minmax(0,1fr)}.v-hero.so>div{max-width:820px}
.rod .w1 img{height:48px}.rod .plat a:hover{color:var(--rxl)}
.rod .w2 .w{gap:24px}
.mm{display:none}
.ctaeq{display:flex;align-items:center;justify-content:space-between;gap:32px;background:var(--esc) url(img/grao.png) repeat;color:var(--off);border-radius:14px;padding:36px 40px;margin:0 0 90px;box-shadow:0 0 0 1px rgba(168,139,255,.25)}
.ctaeq h3{font-weight:300;font-size:30px;letter-spacing:-.015em;margin:10px 0 8px}.ctaeq h3 span{color:var(--rxl);text-shadow:0 0 24px rgba(168,139,255,.5)}.ctaeq p{color:var(--mu2);margin:0;font-size:14px;max-width:560px}.ctaeq .bt{flex:none}
.aviso{border:1px solid var(--ln);border-radius:10px;padding:14px 18px;font-size:13px;color:var(--mu);margin:0 0 8px}
.chips{display:flex;gap:10px;flex-wrap:wrap;margin:28px 0 8px}.chips a{font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--mu);border:1px solid var(--ln);border-radius:99px;padding:8px 16px}.chips a:hover{border-color:var(--rx);color:var(--rx)}
.lj{padding:72px 0 8px;scroll-margin-top:16px}.lj .intro{color:var(--mu);max-width:720px;margin:14px 0 36px;font-size:16px}
.g3l{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.cx{display:flex;flex-direction:column;border:1px solid var(--ln);border-radius:14px;overflow:hidden;background:rgba(255,255,255,.35);transition:all .25s}.cx:hover{border-color:var(--rx);box-shadow:0 0 0 1px var(--rx);transform:translateY(-3px)}
.pi{display:block;position:relative;aspect-ratio:4/3;overflow:hidden;background:#111}.pi img{width:100%;height:100%;object-fit:cover;transition:transform .4s}.cx:hover .pi img{transform:scale(1.04)}
.pi i{position:absolute;right:10px;bottom:8px;font-style:normal;font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.75);background:rgba(10,9,14,.55);padding:3px 7px;border-radius:99px}
.pr{display:flex;flex-direction:column;flex:1;padding:22px 24px 24px}
#nerd .tit2 span{color:var(--rx)}#nerd{border-top:1px solid var(--ln);margin-top:40px}
.pr .sl{align-self:flex-start;font-size:9.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:#fff;background:var(--rx);border-radius:99px;padding:5px 10px;margin-bottom:14px;box-shadow:var(--glow)}
.pr h3{font-weight:500;font-size:19px;line-height:1.3;margin:0 0 16px}
.pr dl{margin:0 0 22px;font-size:14px;line-height:1.55;color:#3D3A44;flex:1}.pr dt{font-size:10px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--rx);margin:12px 0 3px}.pr dt.l{color:var(--mu)}.pr dd{margin:0}
.pr .bt{text-align:center}
.grande{margin:0;padding:0 0 64px;position:relative}.grande a{display:block;text-align:center}.grande img{display:inline-block;width:auto;max-width:100%;max-height:78vh;border-radius:10px;}
.grande figcaption{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--mu2);margin-top:14px;text-align:center}.grande img{max-height:86vh;border-radius:4px}
a.foto{display:block}a.foto:hover b{color:var(--rx)}
.ficha li b{display:block;margin:0 0 2px}
"""
CSS += """
/* ---------- refino elegante (25/11) ---------- */
body{font-size:16px;line-height:1.7;letter-spacing:.005em}
.rot{font-size:11px;letter-spacing:.3em}
.menu{gap:34px;font-size:11px;letter-spacing:.2em}
.nav{height:78px}
.bt{font-size:11px;letter-spacing:.22em;padding:15px 28px;box-shadow:0 6px 24px -8px rgba(135,98,243,.55)}
.bt:hover{box-shadow:0 10px 30px -8px rgba(168,139,255,.7)}
.marca-h span,.tit span,.bruno h2 span,.v-hero h1 span,.parceria h2 span,.ctaeq h3 span{text-shadow:0 0 18px rgba(168,139,255,.28)}
.tit,.tit2{font-weight:300;letter-spacing:-.025em}
.secao,.metodo,.cinza{padding-top:120px;padding-bottom:120px}
.ultimo{padding:120px 0}
.ultimo .nome{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:26px;line-height:1.3}
.ultimo .fig img,.ep.on,.ep:hover{box-shadow:0 20px 50px -20px rgba(10,9,14,.55)}
.ep{border-color:rgba(255,255,255,.06);background:rgba(255,255,255,.02)}
.ep:hover{border-color:rgba(168,139,255,.45)}
.it .n,.ep p{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:18px;line-height:1.35}
.foto .tl b{font-family:'Newsreader',Georgia,serif;font-weight:400}
.texto p{font-family:'Newsreader',Georgia,serif;font-size:20px;line-height:1.7;color:#25222B}
.lado{border-radius:6px}
.cx,.pr{border-radius:8px}.cx{border-color:rgba(22,20,28,.1)}
.pr h3{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:21px}
.passos i{font-family:'Newsreader',Georgia,serif;font-weight:300}
.ctaeq{border-radius:8px}
.chips a,.filtros button{letter-spacing:.18em}
"""
CSS += """
/* ---------- matérias (26/11) ---------- */
.art .corpo2 h2{font-family:'Newsreader',Georgia,serif;font-weight:500;font-size:29px;line-height:1.2;letter-spacing:-.01em;margin:46px 0 16px;color:var(--tx)}
.art .corpo2 em{font-style:italic}
.art .tit2.m{font-size:26px;margin:44px 0 16px}
.art .player{margin-top:0}
.art .bts{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0 0}
.lermat{display:flex;align-items:center;justify-content:space-between;gap:20px;border:1px solid var(--ln);border-left:3px solid var(--rx);border-radius:8px;padding:20px 24px;margin:0 0 44px}
.lermat span{display:block;font-size:10px;font-weight:700;letter-spacing:.26em;text-transform:uppercase;color:var(--rx);margin-bottom:4px}.lermat b{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:20px;line-height:1.3}
.lermat:hover{border-color:var(--rx)}.lermat i{font-style:normal;color:var(--rx);font-size:22px}
.menu a{white-space:nowrap}
@media (min-width:821px) and (max-width:1180px){.menu{gap:18px;letter-spacing:.12em}.nav>.soc{display:none}}
"""
MOB = """
.w{padding:0 20px}.nav{height:64px}.nav .logo img{height:28px}.menu{display:none}
.hero{grid-template-columns:minmax(0,1fr);min-height:0;padding:40px 0 0}.hero .img{height:260px}.marca-h{font-size:58px}
.ultimo,.bruno,.porque,.contato,.parceria,.v-hero{grid-template-columns:minmax(0,1fr);gap:36px}.ultimo{padding:64px 0}
.carro{grid-template-columns:minmax(0,1fr)}.carro .ep:not(.on){display:none}
.g4,.g3{grid-template-columns:repeat(2,minmax(0,1fr));gap:28px 14px}.fotos{grid-template-columns:repeat(2,1fr)}.fotos img:nth-child(n+5){display:none}
.tit,.tit2{font-size:34px}.bruno h2{font-size:44px}.contato .form{padding:44px 20px}.contato h2{font-size:38px}.parceria h2{font-size:40px}.circ{width:260px;height:260px}
.v-hero{padding:40px 0 80px}.v-hero h1{font-size:34px}.v-hero .num b{font-size:72px}.corpo{grid-template-columns:minmax(0,1fr);gap:40px}.passos{grid-template-columns:minmax(0,1fr)}
.rod .w1{grid-template-columns:minmax(0,1fr);gap:24px}
.soc{display:none}.mm{display:block;position:relative}.mm summary{list-style:none;cursor:pointer;width:42px;height:42px;border:1px solid var(--lnd);border-radius:50%;display:flex;align-items:center;justify-content:center}.mm summary::-webkit-details-marker{display:none}
.mm summary i,.mm summary i:before,.mm summary i:after{display:block;width:16px;height:1.5px;background:var(--off);position:relative}.mm summary i:before,.mm summary i:after{content:"";position:absolute;left:0}.mm summary i:before{top:-5px}.mm summary i:after{top:5px}
.mm[open] summary{border-color:var(--rxl)}.mm .gav{position:absolute;right:0;top:52px;width:240px;background:var(--esc);border:1px solid var(--lnd);border-radius:12px;padding:10px;box-shadow:0 20px 60px rgba(0,0,0,.6)}
.mm .gav a{display:block;padding:13px 14px;font-size:12px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--mu2);border-radius:8px}.mm .gav a.on{color:var(--off);background:var(--gr)}
.mm .gav .soc{display:flex;padding:12px 14px 6px}
.hero .img{min-height:260px;-webkit-mask-image:radial-gradient(ellipse 60% 70% at 50% 50%,#000 45%,transparent 80%);mask-image:radial-gradient(ellipse 60% 70% at 50% 50%,#000 45%,transparent 80%)}
.hero{padding:32px 0 48px}.numeros{gap:22px;flex-wrap:wrap}.numeros b{font-size:30px}
.bt.lin{margin:12px 0 0}
.trio{grid-template-columns:minmax(0,1fr)}.manchete,.anteriores{grid-template-columns:minmax(0,1fr)}.mast{flex-direction:column;align-items:flex-start}.mast .ed{text-align:left}.mast .nome{font-size:34px}.manchete h2,.art h1{font-size:32px}.art .corpo2 p{font-size:19px}.acervo a{grid-template-columns:minmax(0,1fr);gap:4px}.ctaeq{flex-direction:column;align-items:flex-start;padding:28px 22px}.g3l{grid-template-columns:minmax(0,1fr)}.navv{grid-template-columns:minmax(0,1fr)}.lado{position:static}.rod .w2 .w{height:auto;padding:16px 20px;flex-direction:column;gap:10px}
"""
for f_ in ("hero_anel.jpg", "anel_pag.jpg", "feixe.jpg", "bruno_anel.jpg", "bruno_foto.jpg", "grao.png"): shutil.copy(AQUI + "/arte/" + f_, OUT + "img/" + f_)
# ---- refinamento LUZ (27/11/2026): aproxima o site da identidade dos posts (Space Grotesk fina, rótulos espaçados, grão, luz roxa)
CSS += """
body{font-family:'Space Grotesk',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:60;background:url(GRAO);opacity:.07;mix-blend-mode:overlay}
.art h1,.art h2,.mast .nome,.manchete h2,.manchete h3,.lide h2,.jn h2,.jn h3{font-family:'Space Grotesk',system-ui,sans-serif!important;font-weight:300!important;letter-spacing:-.025em!important}
.art h1{font-size:52px;line-height:1.04}.art h2{font-size:30px;margin-top:42px}
.art p,.art li{font-size:17px;line-height:1.75}
.mast .nome{font-size:40px}.mast .nome em{font-style:normal;font-weight:500}
.rot,.chapeu,.it .s,.ed,.meta2 span{font-weight:700!important;font-size:11px!important;letter-spacing:.42em!important;text-transform:uppercase}
.tit,.tit2,.v-hero h1{font-weight:300;letter-spacing:-.035em}
.tit span,.tit2 span{font-weight:500}
.menu a{font-size:11px;font-weight:700;letter-spacing:.32em;text-transform:uppercase}
.cinza,section.secao,.claro{background-image:radial-gradient(ellipse 70% 60% at 50% 40%,rgba(255,255,255,.55),rgba(255,255,255,0) 70%)}
.escuro{background-image:radial-gradient(ellipse 55% 50% at 50% 0%,rgba(135,98,243,.16),rgba(135,98,243,0) 70%)}
.it img,.ep,.foto img,.fotos img{border-radius:6px}
.it:hover img,.ep:hover,.foto:hover img{box-shadow:0 0 0 1px rgba(168,139,255,.55),0 18px 50px -18px rgba(135,98,243,.65);transform:translateY(-3px)}
.numeros b,.numeros strong{font-weight:300;letter-spacing:-.04em}
.bt{letter-spacing:.32em;box-shadow:0 0 22px rgba(135,98,243,.45)}
.bt:hover{box-shadow:0 0 34px rgba(135,98,243,.75)}
::selection{background:var(--rx);color:#fff}
"""
MOB += ".art h1{font-size:34px!important}.art h2{font-size:24px}.mast .nome{font-size:30px}"
open(OUT + "estilo.css", "w").write((CSS + "@media (max-width:820px){" + MOB + "}").replace("url(GRAO)", "url(img/grao.png)").replace("url(FEIXE)", "url(img/feixe.jpg)"))
YT = "https://www.youtube.com/@estrelanegra_p"; INSTA = "https://www.instagram.com/estrelanegra_p/"; TT = "https://www.tiktok.com/@estrelanegra_p"
IC = {"yt": '<svg viewBox="0 0 24 24"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8zM9.6 15.6V8.4l6.2 3.6z"/></svg>',
      "ig": '<svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 3.9 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 1 0 0 12.4 6.2 6.2 0 0 0 0-12.4zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.8a1.4 1.4 0 1 0 0 2.9 1.4 1.4 0 0 0 0-2.9z"/></svg>',
      "tt": '<svg viewBox="0 0 24 24"><path d="M19.6 6.7a4.8 4.8 0 0 1-3.8-4.2V2h-3.4v13.7a2.9 2.9 0 1 1-2-2.8V9.5a6.3 6.3 0 1 0 5.4 6.2V8.8a8.2 8.2 0 0 0 4.8 1.5V6.9a4.8 4.8 0 0 1-1-.2z"/></svg>'}
SOC = '<div class="soc"><a href="%s" title="YouTube" aria-label="YouTube">%s</a><a href="%s" title="Instagram" aria-label="Instagram">%s</a><a href="%s" title="TikTok" aria-label="TikTok">%s</a></div>' % (YT, IC["yt"], INSTA, IC["ig"], TT, IC["tt"])
def cabeca(t, d, u, img, tipo, raiz, ativo, ld=""):
    m = [("", "Início")] + ([("jornal/", "Jornal")] if JORNAL else []) + [("episodios/", "Episódios")] + ([("materias/", "Matérias")] if MATERIAS else []) + [("fotos/", "Fotos do céu")] + ([("equipamentos/", "Equipamentos")] if COM_LOJA else []) + [("discussoes/", "Discussões"), ("sobre/", "Sobre"), ("contato/", "Contato")]
    menu = "".join('<a class="%s" href="%s%s">%s</a>' % ("on" if k == ativo else "", raiz, k, n) for k, n in m)
    return ("""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:image" content="%s"><meta property="og:type" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:site_name" content="Estrela Negra"><meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400&family=Space+Grotesk:wght@300;400;500;700&display=swap" rel="stylesheet"><link rel="icon" href="%simg/icone.png"><link rel="stylesheet" href="%sestilo.css"><script src="%sassets/analytics.js" data-en-analytics data-raiz="%s"></script>%s</head><body>
<div class="topo"><div class="w"><nav class="nav"><a class="logo" href="%s"><img src="%simg/logo_simbolo.png" alt="Estrela Negra"></a><div class="menu">%s</div>%s<details class="mm"><summary aria-label="Menu"><i></i></summary><div class="gav">%s%s</div></details></nav></div>""" % (t, d, u, t, d, img, tipo, raiz, raiz, raiz, raiz, ld, raiz, raiz, menu, SOC, menu, SOC))
def rodape(raiz):
    return """<footer class="rod"><div class="w"><div class="w1"><div><img src="%simg/logo.png" alt="Estrela Negra"><div>Astronomia com fonte: o que é certo, o que é debate<br>e de onde vem cada número.</div>%s</div><div class="plat"><a href="%s">YouTube</a><a href="%s">Instagram</a><a href="%s">TikTok</a></div><a class="bt" href="%scontato/">Entre em contato</a></div></div>
<div class="w2"><div class="w"><span>Estrela Negra © 2026 · feito por Bruno Porciúncula</span><span>Imagens: NASA · ESA · ESO e créditos em cada página</span><span class="sim"></span></div></div></footer></body></html>""" % (raiz, SOC, YT, INSTA, TT, raiz)
def com(raiz, pagina):
    """bloco de comentários (Firebase); pagina = caminho estável da página, ex. /materias/slug/"""
    return ('<div class="w"><div id="en-comentarios" data-pagina="%s"></div></div><link rel="stylesheet" href="%sassets/comunidade.css">'
            '<script src="%sassets/firebase-config.js"></script><script src="%sassets/comunidade.js" data-raiz="%s" defer></script>' % (e(pagina), raiz, raiz, raiz, raiz))
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
    return '<a class="it" data-c="%s" href="%s%s/"><img src="%s%s" alt="%s" loading="lazy"><p class="n">%s</p><p class="s">%s · %d fontes</p></a>' % (cat(d["titulo"]), raiz, d["sl"], raiz, d["img"], e(d["titulo"]), e(d["titulo"]), cat(d["titulo"]), len(d["fontes"]))
def cta_eq(raiz, txt="Binóculos, telescópios e livros que o canal indica, com o que cada um mostra e o limite de cada um."):
    if not COM_LOJA: return ""
    return '<div class="w"><aside class="ctaeq"><div><span class="rot">Equipamentos</span><h3>Quer ver o céu <span>com os próprios olhos?</span></h3><p>%s</p></div><a class="bt" href="%sequipamentos/">Ver indicações</a></aside></div>' % (txt, raiz)
def topo_hero(rot, titulo, texto, arte, extra="", alt="420px"):
    return '<div class="w"><section class="hero" style="min-height:%s"><div><span class="rot">%s</span><h1 class="marca-h">%s</h1>%s%s</div><div class="img" style="background-image:url(%s)"></div></section></div></div>' % (alt, rot, titulo, '<p class="lead">%s</p>' % texto if texto else "", extra, arte)
# ------------------------------------------------------------------ início
desc0 = "Vídeos de astronomia com fonte: o que se sabe, o que está em debate e de onde vem cada número."
h = [cabeca("Estrela Negra · astronomia com fonte", desc0, URL, OG["inicio"], "website", "", "")]
h.append(topo_hero("Canal de astronomia", "Estrela<br><span>Negra</span>", "Buracos negros, estrelas, missões e descobertas. <b>O que já é certo, o que ainda está em debate e de onde vem cada número.</b>", "img/hero_anel.jpg", '<a class="bt" href="%s?sub_confirmation=1">Inscreva-se no canal</a><a class="bt lin" href="episodios/">Ver episódios</a><div class="numeros"><div><b>%d</b><span>Episódios</span></div><div><b>%d</b><span>Fontes citadas</span></div><div><b>1</b><span>Foto do céu por dia</span></div></div>' % (YT, len(DADOS), NFONTES), "620px"))
if JORNAL:
    n = JORNAL[0]; nimg = "jornal/img/%s.jpg" % n["data"]
    ant = "".join('<a href="%s"><span>%s · %s</span><b>%s</b></a>' % (ed_url(x), data_ext(x["data"], False), e(x["chapeu"]), e(x["titulo"])) for x in JORNAL[1:4])
    h.append('<div class="w"><section class="jn"><div class="mast"><div class="nome">O Estrela <em>Negra</em></div><div class="ed">%s<br>Edição nº %d · <a href="jornal/">Acervo</a></div></div><div class="manchete"><div><span class="chapeu">%s</span><h2><a href="%s">%s</a></h2><p class="fina">%s</p><p class="lide">%s</p><a class="lermais" href="%s">Ler a notícia completa</a></div><figure><a href="%s"><img src="%s" alt="%s"></a><figcaption class="cr">%s · %s</figcaption></figure></div>%s</section></div>' % (data_ext(n["data"]), len(JORNAL), e(n["chapeu"]), ed_url(n), e(n["titulo"]), e(n["linha_fina"]), e(corta(n["texto"][0], 320)), ed_url(n), ed_url(n), nimg, e(n["imagem"]["legenda"]), e(n["imagem"]["legenda"]), e(n["imagem"]["credito"]), '<div class="anteriores">%s</div>' % ant if ant else ""))
if DADOS:
    d = DADOS[0]
    h.append('<div class="w"><section class="ultimo"><a class="fig" href="%s/"><img src="%s" alt="%s"></a><div><span class="rot">Último episódio</span><h2 class="tit">Confira o<br><span>último episódio</span></h2><p class="nome">%s</p><p>%s</p><div class="meta" style="margin-bottom:28px"><span class="tag" style="color:var(--rx)">%s</span><span>%d fontes conferidas</span></div><a class="bt" href="%s/">Assistir agora</a></div></section></div>' % (d["sl"], d["img"], e(d["titulo"]), e(d["titulo"]), e(corta(d["resumo"][0] if d["resumo"] else "", 260)), cat(d["titulo"]), len(d["fontes"]), d["sl"]))
if len(DADOS) > 3:
    tres = DADOS[1:4]
    h.append('<section class="cinza escuro"><div class="w"><span class="rot">Episódios</span><h2 class="tit c">Últimos <span>episódios</span></h2><a class="bt esc" href="episodios/">Ver todos</a><div class="trio">%s</div></div></section>' % "".join('<a class="ep" href="%s/"><img src="%s" alt="%s" loading="lazy"><p>%s</p><p class="s">%s · %d fontes</p></a>' % (x["sl"], x["img"], e(x["titulo"]), e(x["titulo"]), cat(x["titulo"]), len(x["fontes"])) for x in tres))
h.append('<div class="w"><section class="secao c"><span class="rot">Instagram</span><h2 class="tit c">Uma foto do céu <span>por dia</span></h2><p style="color:var(--mu);margin:16px 0 0">Imagens dos telescópios James Webb, Hubble e ESO, explicadas.</p><div class="fotos">%s</div><p style="margin-top:44px"><a class="bt" href="%s">Seguir @estrelanegra_p</a><a class="bt esc" style="margin-left:12px" href="fotos/">Ver as explicações</a></p></section></div>' % ("".join('<a href="fotos/"><img src="%s" alt="Foto de telescópio" loading="lazy"></a>' % x for x in IG[:5]), INSTA))
h.append(cta_eq(""))
h.append('<section class="escuro"><div class="w"><div class="metodo"><span class="rot">Como a gente checa</span><h2 class="tit">Toda frase <span>tem fonte</span></h2><div class="passos"><div><i>01</i><b>Fonte primária</b>Agências espaciais, observatórios e artigos científicos, com link em cada episódio.</div><div><i>02</i><b>Revisão independente</b>Um segundo revisor confere o roteiro frase a frase antes da gravação.</div><div><i>03</i><b>Grau de certeza</b>Consenso, evidência forte, debate ou hipótese: cada vídeo diz qual é.</div></div></div></div></section>')
h.append(rodape("")); open(OUT + "index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ episódios
os.makedirs(OUT + "episodios")
h = [cabeca("Episódios · Estrela Negra", desc0, URL + "episodios/", OG["episodios"], "website", "../", "episodios/")]
h.append(topo_hero("%d vídeos · %d fontes" % (len(DADOS), NFONTES), "Todos os<br><span>episódios</span>", "Cada vídeo com transcrição, grau de certeza e fontes.", "../img/anel_pag.jpg"))
h.append('<div class="w"><section class="lista"><span class="rot">Lista</span><h2 class="tit2">Lista de <span style="color:var(--rx)">episódios</span></h2><div class="filtros" data-alvo=".g4 .it"><button class="on" data-f="">Todos</button>%s</div><div class="g4">%s</div><p class="vazio">Ainda não tem episódio público neste tema. Em breve.</p></section></div>' % ("".join('<button data-f="%s">%s</button>' % (n, n) for n, _ in CAT), "".join(it(d, "../") for d in DADOS)) + FILT_JS)
h.append(rodape("../")); open(OUT + "episodios/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ fotos do céu
FC = json.load(open(B + "/motion/INSTAGRAM/FOTO_DO_CEU/foto_do_ceu.json", encoding="utf-8"))
os.makedirs(OUT + "fotos")
cards = []; FOTOS = []
for k, x in enumerate(FC):
    if not os.path.exists(x["foto"]): continue
    im = Image.open(x["foto"]).convert("RGB"); W_, H_ = im.size; s_ = int(min(W_, H_) / max(1.0, x.get("zoom", 1.0)))
    cx, cy = int(x.get("fx", .5) * W_), int(x.get("fy", .5) * H_); l_ = min(max(0, cx - s_ // 2), W_ - s_); t_ = min(max(0, cy - s_ // 2), H_ - s_)
    im = im.crop((l_, t_, l_ + s_, t_ + s_)); im.thumbnail((1000, 1000), Image.LANCZOS); im.save(OUT + "img/fc_%02d.jpg" % k, quality=90)
    tel = x["tag"].split("·")[-1].strip().title()
    x["sl"] = slug(x["titulo"].split("(")[0]); x["k"] = k
    im_b = Image.open(x["foto"]).convert("RGB"); im_b.thumbnail((2400, 2400), Image.LANCZOS); im_b.save(OUT + "img/fc_g_%02d.jpg" % k, quality=92)
    shutil.copy(x["foto"], OUT + "img/fc_orig_%02d.jpg" % k)  # resolução original, sem recompressão
    FOTOS.append(x)
    cards.append('<a class="foto" href="%s/" data-c="%s"><img src="../img/fc_%02d.jpg" alt="%s" loading="lazy"><div class="tl"><b>%s</b><span class="tag" style="color:var(--rx)">%s</span></div><p>%s %s</p><p class="cr">Imagem: %s</p></a>' % (x["sl"], e(x["tag"].upper()), k, e(x["titulo"]), e(x["num"]), e(tel), e(x["l1"].rstrip('.') + '.'), e(x["l2"].rstrip('.') + '.'), e(x["cred"])))
h = [cabeca("Fotos do céu · Estrela Negra", "Fotos dos telescópios James Webb, Hubble, ESO e outros, explicadas.", URL + "fotos/", OG["fotos"], "website", "../", "fotos/")]
h.append('<div class="w"><section class="hero" style="min-height:420px"><div><span class="rot">James Webb · Hubble · ESO</span><h1 class="marca-h" style="font-size:84px">Fotos<br><span>do céu</span></h1><p>As imagens mais bonitas dos telescópios, explicadas: o que é cada parte, a que distância está e o que as cores querem dizer.</p></div><div class="img" style="background-image:url(../img/fc_00.jpg)"></div></section></div></div>')
h.append('<div class="w"><section class="lista"><span class="rot">Galeria</span><h2 class="tit2">Uma foto por dia, <span style="color:var(--rx)">explicada</span></h2><div class="filtros" data-alvo=".g3 .foto"><button class="on" data-f="">Todas</button><button data-f="WEBB">James Webb</button><button data-f="HUBBLE">Hubble</button><button data-f="ESO">ESO</button><button data-f="CHANDRA">Chandra</button></div><div class="g3">%s</div></section></div>' % "".join(cards) + FILT_JS)
h.append(rodape("../")); open(OUT + "fotos/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ sobre
os.makedirs(OUT + "sobre")
h = [cabeca("Sobre · Estrela Negra", desc0, URL + "sobre/", OG["sobre"], "website", "../", "sobre/")]
h.append(topo_hero("Sobre o canal", "Astronomia<br><span>com fonte</span>", "Um canal sobre o universo que diz o que é certo, o que é debate e o que é hipótese.", "../img/sobre.jpg"))
h.append('<div class="w"><section class="secao c"><span class="rot">Galeria</span><h2 class="tit c">O céu visto pelos <span>telescópios</span></h2><div class="fotos">%s</div></section></div>' % "".join('<img src="../%s" alt="Foto de telescópio" loading="lazy">' % x for x in IG[:5]))
h.append('<div class="w"><section class="secao c en-numeros-sec"><span class="rot">Em números</span><h2 class="tit c">O Estrela Negra <span>até agora</span></h2><div id="en-numeros" class="en-nums" data-raiz="../"></div><p class="en-nota">Os números do YouTube se atualizam sozinhos.</p></section></div>'
         '<style>.en-nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:28px;margin-top:44px;text-align:center}.en-num b{display:block;font-family:Newsreader,serif;font-weight:300;font-size:clamp(46px,7vw,84px);line-height:1;color:var(--tx)}.en-num span{display:block;margin-top:12px;font:700 11px "Space Grotesk",sans-serif;letter-spacing:.28em;text-transform:uppercase;color:var(--rx)}.en-num i{display:block;margin-top:6px;font-style:normal;font-size:12px;color:var(--mu)}.en-nota{margin-top:28px;font-size:12px;color:var(--mu);text-align:center}</style><script src="../assets/numeros.js" defer></script>')
h.append('<section class="escuro"><div class="w"><div class="secao bruno"><div><span class="rot">Quem faz</span><h2>Bruno<br><span>Porciúncula.</span></h2><p>Designer e editor de vídeo, estudou Física na UFSCar e é apaixonado por astronomia desde criança, quando maratonava documentários sobre o espaço na TV.</p><p>O Estrela Negra nasceu como podcast e hoje é um canal de vídeo sobre o universo, com identidade visual, animação e locução feitas por ele.</p><p style="margin-top:28px"><a class="bt" href="%s?sub_confirmation=1">Assista o canal</a></p></div><div class="ft"><img src="../img/bruno_foto_recorte.webp" alt="Bruno Porciúncula"></div></div></div></section>' % YT)
h.append('<div class="w"><section class="secao porque"><div><span class="rot">Por que assistir</span><h2 class="tit">Por que assistir o<br><span>Estrela Negra?</span></h2><p style="margin-top:28px"><a class="bt" href="../episodios/">Ver episódios</a></p></div><div><p>Cada vídeo explica um assunto do universo do jeito que se conta para um amigo, sem deixar de lado o rigor: toda afirmação tem fonte, e o vídeo diz com que grau de certeza a ciência sabe o que está sendo contado.</p><div class="passos"><div><i>01</i><b>Fonte primária</b>Agências, observatórios e artigos científicos, com link.</div><div><i>02</i><b>Revisão independente</b>Um segundo revisor confere o roteiro frase a frase.</div><div><i>03</i><b>Grau de certeza</b>Hipótese é dita como hipótese; previsão, como previsão.</div></div></div></section></div>')
h.append(rodape("../")); open(OUT + "sobre/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ contato
os.makedirs(OUT + "contato")
h = [cabeca("Contato · Estrela Negra", desc0, URL + "contato/", OG["contato"], "website", "../", "contato/"), "</div>"]
h.append('<section class="contato"><div class="roxo"><img src="../img/webb.jpg" alt="Espelho do telescópio James Webb"></div><div class="form"><span class="rot">Contato</span><h2>Fale com<br><span style="color:var(--rx)">a gente!</span></h2><p style="color:var(--mu);font-size:15px;margin:0">Dúvidas, sugestões de tema, correções e parcerias. A gente lê tudo.</p><div class="caixa"><a class="campo" style="display:block;color:var(--off)" href="%s">Mensagem direta no Instagram →</a><a class="campo" style="display:block;color:var(--off)" href="%s">Comentários no YouTube →</a><a class="campo" style="display:block;color:var(--off);border:0" href="%s">TikTok →</a></div><a class="bt" href="%s">Mandar mensagem</a></div></section>' % (INSTA, YT, TT, INSTA))
h.append('<section class="escuro"><div class="w"><div class="parceria"><div><span class="rot">Parcerias</span><h2>Quer fazer<br><span>uma parceria?</span></h2><p>Planetários, escolas, clubes de astronomia e divulgadores de ciência: vamos conversar.</p><a class="bt" href="%s">Falar no Instagram</a></div><div class="circ"><img src="../img/parceria.jpg" alt="Júpiter visto pelo James Webb"></div></div></div></section>' % INSTA)
h.append(rodape("../")); open(OUT + "contato/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ páginas de vídeo
for d in DADOS:
    desc = (d["resumo"][0] if d["resumo"] else d["titulo"])[:155]
    ld = '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@type": "VideoObject", "name": d["titulo"], "description": desc, "thumbnailUrl": URL + d["img"], "embedUrl": "https://www.youtube.com/embed/" + d["vid"], "contentUrl": "https://youtu.be/" + d["vid"], "inLanguage": "pt-BR"}, ensure_ascii=False)
    h = [cabeca(e(d["titulo"]) + " · Estrela Negra", e(desc), URL + d["sl"] + "/", cartao_video(d), "article", "../", "episodios/", ld)]
    num = '<div class="num"><b>%s</b><span class="rot">%s</span></div>' % (e(d["num"]), e(d["rot"])) if d["num"] else ""
    h.append('<div class="w"><section class="v-hero%s">' % ("" if num else " so") + '<div><span class="rot">%s · %d fontes</span><h1>%s</h1>%s</div>%s</section></div></div>' % (cat(d["titulo"]), len(d["fontes"]), destaca(d["titulo"]), '<p>%s</p>' % e(corta(d["resumo"][0], 340)) if d["resumo"] else "", num))
    h.append('<div class="w"><div class="player"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s" loading="lazy" allowfullscreen></iframe></div><div class="corpo"><article class="texto">' % (d["vid"], e(d["titulo"])))
    if d.get("mat"): h.append('<a class="lermat" href="../materias/%s/"><div><span>Leia a matéria completa</span><b>%s</b></div><i>→</i></a>' % (d["mat"]["slug"], e(d["mat"]["titulo"])))
    if len(d["resumo"]) > 1: h += ["<p>%s</p>" % e(p) for p in d["resumo"][1:]]
    if d["transc"]:
        h.append('<h2>Transcrição</h2>'); nomes = [n for _, n in d["caps"]] if len(d["caps"]) == len(d["transc"]) else []
        for k, p in enumerate(d["transc"]):
            if nomes: h.append('<p class="cap">%s</p>' % e(nomes[k]))
            h.append("<p>%s</p>" % e(p))
    if d["fontes"]: h.append('<h2>Fontes</h2><ol class="fontes">' + "".join("<li>%s</li>" % re.sub(r"(https?://\S+)", r'<a href="\1" rel="nofollow">\1</a>', e(f)) for f in d["fontes"]) + "</ol>")
    if d["imgs"]: h.append('<p style="font-size:12px;color:var(--mu);margin-top:24px">Imagens: %s</p>' % e(d["imgs"]))
    i_ = DADOS.index(d); ant = DADOS[i_ + 1] if i_ + 1 < len(DADOS) else None; prox = DADOS[i_ - 1] if i_ > 0 else None
    if ant or prox: h.append('<nav class="navv">%s%s</nav>' % ('<a href="../%s/"><span>← Episódio anterior</span><b>%s</b></a>' % (ant["sl"], e(ant["titulo"])) if ant else "<div></div>", '<a class="d" href="../%s/"><span>Próximo episódio →</span><b>%s</b></a>' % (prox["sl"], e(prox["titulo"])) if prox else ""))
    h.append('</article><aside class="lado">')
    if d["caps"]: h.append("<h4>Capítulos</h4><ul>" + "".join('<li><a href="https://youtu.be/%s?t=%d"><b>%s</b>%s</a></li>' % (d["vid"], ytseg(t), e(t), e(n)) for t, n in d["caps"]) + "</ul>")
    cs = certezas(d["cert"])
    if cs: h.append("<h4>Grau de certeza</h4><ul>" + "".join("<li>%s<br>%s</li>" % ('<span class="selo %s">%s</span>' % (seloclasse(n), e(nivel(n))) if n else "", e(o)) for n, o in cs) + "</ul>")
    if d.get("mat"): h.append('<a class="bt" style="display:block;text-align:center;margin-bottom:10px" href="../materias/%s/">Leia a matéria completa</a>' % d["mat"]["slug"])
    h.append('<a class="bt" style="display:block;text-align:center" href="https://youtu.be/%s">Assistir no YouTube</a><a class="bt esc" style="display:block;text-align:center;margin-top:10px;color:var(--off);border-color:var(--off)" href="%s?sub_confirmation=1">Inscrever-se</a></aside></div></div>' % (d["vid"], YT))
    h.append(cta_eq("../"))
    outros = [x for x in DADOS if x is not d][:4]
    if outros: h.append('<section class="cinza escuro" style="text-align:left"><div class="w"><span class="rot">Continue</span><h2 class="tit">Mais <span>episódios</span></h2><div class="g4" style="margin-top:40px">%s</div></div></section>' % "".join(it(x, "../") for x in outros))
    h.append(com("../", "/" + d["sl"] + "/")); h.append(rodape("../")); os.makedirs(OUT + d["sl"]); open(OUT + d["sl"] + "/index.html", "w", encoding="utf-8").write("\n".join(h))

# ------------------------------------------------------------------ uma página por foto do céu
def legenda_partes(t):
    corpo, _, fon = t.partition("\nFontes:")
    pars = [p.strip() for p in corpo.split("\n\n") if p.strip()]
    fl = [l.strip() for l in fon.split("\n") if l.strip()]
    return pars, fl
def linka(t): return re.sub(r"(https?://[^\s<]+)", r'<a href="\1" rel="nofollow">\1</a>', e(t))
for i_, x in enumerate(FOTOS):
    pars, fl = legenda_partes(x.get("legenda", ""))
    if not pars: pars = [x["l1"].rstrip(".") + ". " + x["l2"].rstrip(".") + "."]
    desc = corta(pars[0], 155); tel = x["tag"].split("·")[-1].strip().title()
    og = cartao("f_" + x["sl"], x["rot"], x["titulo"].split("(")[0].strip(), x["foto"], x.get("fx", .5), x.get("fy", .5))
    ld = '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": x["titulo"], "description": desc, "image": URL + "img/fc_g_%02d.jpg" % x["k"], "inLanguage": "pt-BR", "publisher": {"@type": "Organization", "name": "Estrela Negra"}}, ensure_ascii=False)
    h = [cabeca(e(x["titulo"]) + " · Foto do céu · Estrela Negra", e(desc), URL + "fotos/%s/" % x["sl"], og, "article", "../../", "fotos/", ld)]
    h.append('<div class="w"><section class="v-hero so" style="padding-bottom:48px"><div><span class="rot">Foto do céu · %s</span><h1>%s</h1><p>%s %s</p></div></section></div>' % (e(tel), destaca(x["titulo"]), e(x["l1"].rstrip(".") + "."), e(x["l2"].rstrip(".") + ".")))
    h.append('<div class="w"><figure class="grande"><a href="../../img/fc_orig_%02d.jpg"><img src="../../img/fc_g_%02d.jpg" alt="%s"></a><figcaption>Imagem: %s · toque na foto para ver na resolução original</figcaption></figure></div></div><div class="w"><div class="corpo"><article class="texto"><h2>O que a foto mostra</h2>' % (x["k"], x["k"], e(x["titulo"]), e(x["cred"])))
    h += ["<p>%s</p>" % linka(p) for p in pars]
    fontes_ = [f for f in fl if not f.lower().startswith("imagem")]
    if fontes_: h.append('<h2>Fontes</h2><ol class="fontes">' + "".join("<li>%s</li>" % linka(f) for f in fontes_) + "</ol>")
    ant = FOTOS[i_ - 1] if i_ > 0 else None; prox = FOTOS[i_ + 1] if i_ + 1 < len(FOTOS) else None
    h.append('<nav class="navv">%s%s</nav>' % ('<a href="../%s/"><span>← Foto anterior</span><b>%s</b></a>' % (ant["sl"], e(ant["titulo"])) if ant else "<div></div>", '<a class="d" href="../%s/"><span>Próxima foto →</span><b>%s</b></a>' % (prox["sl"], e(prox["titulo"])) if prox else ""))
    h.append('</article><aside class="lado ficha"><h4>Ficha</h4><ul><li><b>Objeto</b>%s</li><li><b>Telescópio</b>%s</li><li><b>Imagem</b>%s</li></ul><a class="bt" style="display:block;text-align:center" href="%s">Uma foto por dia no Instagram</a><a class="bt esc" style="display:block;text-align:center;margin-top:10px;color:var(--off);border-color:var(--off)" href="../">Ver todas as fotos</a></aside></div></div>' % (e(x["titulo"].split("(")[0].strip()), e(tel), e(x["cred"]), INSTA))
    h.append(cta_eq("../../", "Muito do que aparece nas fotos de telescópio dá para começar a ver com um bom binóculo: a Lua, aglomerados e nebulosas brilhantes. Veja o que o canal indica."))
    outras = [y for y in FOTOS if y is not x][i_ % max(1, len(FOTOS) - 4):][:4] or FOTOS[:4]
    h.append('<section class="cinza escuro" style="text-align:left"><div class="w"><span class="rot">Continue</span><h2 class="tit">Mais fotos <span>do céu</span></h2><div class="g4" style="margin-top:40px">%s</div></div></section>' % "".join('<a class="it" href="../%s/"><img src="../../img/fc_%02d.jpg" alt="%s" loading="lazy" style="aspect-ratio:1"><p class="n">%s</p><p class="s">%s</p></a>' % (y["sl"], y["k"], e(y["titulo"]), e(y["titulo"]), e(y["tag"].split("·")[-1].strip().title())) for y in outras))
    h.append(rodape("../../")); os.makedirs(OUT + "fotos/" + x["sl"], exist_ok=True); open(OUT + "fotos/%s/index.html" % x["sl"], "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ equipamentos (Amazon Associados; só com aprovação)
if COM_LOJA:
    LIVROS_ = {"8535929886","8535931937","8580576466","8551010255","8558890765","854220753X","8578614437","8542302680","8576085097","8578614852","852120745X","8521637225","6555651326","8580414482","8535913513"}
    JOGOS_ = {"B0B4KN54RQ","B0CWS6WD53","B0GT2GZFHV","B0H6KT2RWH","B0D6HPB6SF"}
    OFICIAIS_ = {'B00DV6SI3Q', 'B003AM87Q4', 'B0HKYBZRN1', 'B07ZYJ9R1N', 'B0CLD7TFNL', 'B0FPGF9J2J', 'B0HGP399RF', 'B0FMS8BW3K', 'B0HGP7LYM4'}
    SELO_IMG = {**{a: "Capa oficial" for a in LIVROS_}, **{a: "Arte oficial do jogo" for a in JOGOS_}, **{a: "Foto oficial do fabricante" for a in OFICIAIS_}}
    TAG = LOJA["tag"]; AV = "Como associado da Amazon, o Estrela Negra ganha com compras qualificadas. O preço para você é o mesmo."
    og_e = cartao("equipamentos", "Equipamentos", "O que usar para olhar o céu, e o que ler", L5 + "T1412_saturno_aneis_cassini.jpg")
    h = [cabeca("Equipamentos · Estrela Negra", "Binóculos, telescópios, livros e acessórios de astronomia indicados pelo Estrela Negra, com o que cada um mostra e o limite de cada um.", URL + "equipamentos/", og_e, "website", "../", "equipamentos/")]
    h.append(topo_hero("Indicações do canal", "Para olhar<br><span>o céu</span>", "Binóculos, telescópios, livros e acessórios. Cada indicação diz para quem é, o que dá para ver e qual é o limite.", "../img/anel_pag.jpg"))
    h.append('<div class="w"><div style="padding-top:56px"><p class="aviso">%s</p><div class="chips">%s</div></div>' % (AV + " Fotos oficiais de Celestron, LEGO, Sony, Nintendo e SVBONY; demais fotos de produto ilustrativas (Freepik). Capas dos livros: divulgação das editoras (Companhia das Letras, Intrínseca, Planeta, Valentina, Livraria da Física, Editora UFMG, Alta Books, Blucher, LTC, Arqueiro), aplicadas em foto ilustrativa. Artes dos jogos: divulgação oficial de Rockstar Games, Sony Interactive Entertainment, Hello Games, Mobius Digital e Bethesda.", "".join('<a href="#%s">%s</a>' % (sc["id"], e(sc["titulo"])) for sc in LOJA["secoes"])))
    for sc in LOJA["secoes"]:
        cards_ = []
        for it in sc["itens"]:
            u = "https://www.amazon.com.br/dp/%s?tag=%s" % (it["asin"], TAG)
            fimg = AQUI + "/arte/loja/%s.jpg" % it["asin"]; im_html = ""
            if os.path.exists(fimg):
                os.makedirs(OUT + "img/loja", exist_ok=True); shutil.copy(fimg, OUT + "img/loja/%s.jpg" % it["asin"])
                im_html = '<a class="pi" href="%s" rel="sponsored nofollow noopener" target="_blank"><img src="../img/loja/%s.jpg" alt="" loading="lazy"><i>%s</i></a>' % (u, it["asin"], SELO_IMG.get(it["asin"], "Foto ilustrativa"))
            cards_.append(im_html + '<div class="pr">%s<h3>%s</h3><dl><dt>Para quem</dt><dd>%s</dd><dt>O que dá para ver</dt><dd>%s</dd><dt class="l">Limite</dt><dd>%s</dd></dl><a class="bt" href="%s" rel="sponsored nofollow noopener" target="_blank">Ver na Amazon</a></div>' % ('<span class="sl">%s</span>' % e(it["selo"]) if it.get("selo") else "", e(it["nome"]), e(it["para"]), e(it["ve"]), e(it["limite"]), u))
        h.append('<section class="lj" id="%s"><span class="rot">%s</span><h2 class="tit2">%s</h2><p class="intro">%s</p><div class="g3l">%s</div></section>' % (sc["id"], "Equipamentos", destaca(sc["titulo"]), e(sc["intro"]), "".join('<div class="cx">%s</div>' % c for c in cards_)))
    h.append('<p class="aviso" style="margin:64px 0 100px">%s Os preços e a disponibilidade mudam na Amazon; confira na página do produto.</p></div>' % AV)
    h.append(rodape("../")); os.makedirs(OUT + "equipamentos", exist_ok=True); open(OUT + "equipamentos/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ jornal: uma página por edição + acervo
if JORNAL:
    os.makedirs(OUT + "jornal/img", exist_ok=True)
    for i_, n in enumerate(JORNAL):
        src = AQUI + "/jornal/img/%s.jpg" % n["data"]
        if os.path.exists(src): shutil.copy(src, OUT + "jornal/img/%s.jpg" % n["data"])
        og = cartao("j_" + n["data"], "O Estrela Negra · " + data_ext(n["data"], False), n["titulo"], src)
        ld = '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@type": "NewsArticle", "headline": n["titulo"], "description": n["linha_fina"], "datePublished": n["data"], "image": URL + "jornal/img/%s.jpg" % n["data"], "inLanguage": "pt-BR", "publisher": {"@type": "Organization", "name": "Estrela Negra"}, "author": {"@type": "Organization", "name": "Redação Estrela Negra"}}, ensure_ascii=False)
        h = [cabeca(e(n["titulo"]) + " · O Estrela Negra", e(n["linha_fina"]), URL + ed_url(n), og, "article", "../../", "jornal/", ld), "</div>"]
        fontes = "".join('<li><a href="%s" rel="nofollow">%s</a></li>' % (e(f["url"]), e(f["nome"])) for f in n["fontes"])
        mais = JORNAL[i_ + 1] if i_ + 1 < len(JORNAL) else None; menos = JORNAL[i_ - 1] if i_ > 0 else None
        nav = '<nav class="navv">%s%s</nav>' % ('<a href="../../%s"><span>← Edição anterior</span><b>%s</b></a>' % (ed_url(mais), e(mais["titulo"])) if mais else "<div></div>", '<a class="d" href="../../%s"><span>Próxima edição →</span><b>%s</b></a>' % (ed_url(menos), e(menos["titulo"])) if menos else "")
        h.append('<div class="w"><article class="art"><div class="mast"><div class="nome">O Estrela <em>Negra</em></div><div class="ed">%s<br><a href="../">Acervo de edições</a></div></div><span class="chapeu">%s</span><h1>%s</h1><p class="fina">%s</p><div class="meta2"><span>Redação Estrela Negra</span><span>Fatos conferidos por revisão independente</span></div><figure><img src="../img/%s.jpg" alt="%s"><figcaption class="cr">%s · Imagem: %s (%s)</figcaption></figure><div class="corpo2" style="margin-top:34px">%s</div><p class="certeza"><b>Grau de certeza</b>%s</p><h2 class="tit2" style="font-size:26px;margin-top:40px">Fontes</h2><ol class="fontes">%s</ol>%s</article></div>' % (data_ext(n["data"]), e(n["chapeu"]), e(n["titulo"]), e(n["linha_fina"]), n["data"], e(n["imagem"]["legenda"]), e(n["imagem"]["legenda"]), e(n["imagem"]["credito"]), e(n["imagem"]["licenca"]), "".join("<p>%s</p>" % e(p) for p in n["texto"]), e(n["certeza"]), fontes, nav))
        h.append(com("../../", "/" + ed_url(n))); h.append(cta_eq("../../")); h.append(rodape("../../"))
        os.makedirs(OUT + ed_url(n), exist_ok=True); open(OUT + ed_url(n) + "index.html", "w", encoding="utf-8").write("\n".join(h))
    h = [cabeca("Acervo · O Estrela Negra", "Todas as edições do jornal diário de astronomia do Estrela Negra.", URL + "jornal/", cartao("jornal", "O Estrela Negra", "Uma notícia de astronomia por dia, com fonte", JORNAL[0] and AQUI + "/jornal/img/%s.jpg" % JORNAL[0]["data"]), "website", "../", "jornal/"), "</div>"]
    blocos, mes = [], None
    for n in JORNAL:
        d_ = datetime.date.fromisoformat(n["data"]); m_ = "%s de %d" % (MESES[d_.month - 1].capitalize(), d_.year)
        if m_ != mes: blocos.append("<h3>%s</h3>" % m_); mes = m_
        blocos.append('<a href="../%s"><time>%d %s</time><span><b>%s</b><i>%s · %s</i></span></a>' % (ed_url(n), d_.day, MESES[d_.month - 1][:3], e(n["titulo"]), e(n["chapeu"]), e(n["linha_fina"])))
    h.append('<div class="w"><section class="acervo"><div class="mast"><div class="nome">O Estrela <em>Negra</em></div><div class="ed">Acervo · %d edições<br>Uma notícia de astronomia por dia</div></div>%s</section></div>' % (len(JORNAL), "".join(blocos)))
    h.append(rodape("../")); open(OUT + "jornal/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ matérias: uma página por vídeo público + índice /materias/
def md_inline(t): return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", e(t))
if MATERIAS:
    for i_, m in enumerate(MATERIAS):
        d = m["d"]; u = URL + "materias/%s/" % m["slug"]
        ld = '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": m["titulo"], "description": m["linha_fina"], "datePublished": m.get("data", ""), "dateModified": m.get("data", ""), "image": URL + d["img"], "inLanguage": "pt-BR", "mainEntityOfPage": u, "isBasedOn": "https://youtu.be/" + d["vid"], "author": {"@type": "Organization", "name": "Redação Estrela Negra"}, "publisher": {"@type": "Organization", "name": "Estrela Negra", "logo": {"@type": "ImageObject", "url": URL + "img/icone.png"}}}, ensure_ascii=False)
        h = [cabeca(e(m["titulo"]) + " · Estrela Negra", e(corta(m["linha_fina"], 160)), u, cartao_video(d), "article", "../../", "materias/", ld), "</div>"]
        corpo = "".join(("<h2>%s</h2>" if k == "h2" else "<p>%s</p>") % md_inline(t) for k, t in m["blocos"])
        fontes = "".join('<li>%s: <a href="%s" rel="nofollow">%s</a></li>' % (e(n), e(l), e(l)) if l else "<li>%s</li>" % e(n) for n, l in m["fontes"])
        mais = MATERIAS[i_ + 1] if i_ + 1 < len(MATERIAS) else None; menos = MATERIAS[i_ - 1] if i_ > 0 else None
        nav = '<nav class="navv">%s%s</nav>' % ('<a href="../%s/"><span>← Matéria anterior</span><b>%s</b></a>' % (mais["slug"], e(mais["titulo"])) if mais else "<div></div>", '<a class="d" href="../%s/"><span>Próxima matéria →</span><b>%s</b></a>' % (menos["slug"], e(menos["titulo"])) if menos else "")
        h.append('<div class="w"><article class="art"><span class="chapeu">%s</span><h1>%s</h1><p class="fina">%s</p><div class="meta2"><span>Redação Estrela Negra · %s</span><span>Matéria do vídeo do canal</span></div><figure><img src="../../%s" alt="%s"><figcaption class="cr">Capa do vídeo no canal Estrela Negra</figcaption></figure><div class="corpo2" style="margin-top:34px">%s</div><p class="certeza"><b>Grau de certeza</b>%s</p><h2 class="tit2 m">Fontes</h2><ol class="fontes">%s</ol><h2 class="tit2 m">Assista ao vídeo</h2><div class="player"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s" loading="lazy" allowfullscreen></iframe></div><div class="bts"><a class="bt" href="https://youtu.be/%s">Assistir no YouTube</a><a class="bt esc" href="../../%s/">Episódio com transcrição</a></div>%s</article></div>' % (e(m["chapeu"]), e(m["titulo"]), e(m["linha_fina"]), data_ext(m["data"], False) if m.get("data") else "", d["img"], e(d["titulo"]), corpo, e(m["certeza"]), fontes, d["vid"], e(d["titulo"]), d["vid"], d["sl"], nav))
        h.append(com("../../", "/materias/%s/" % m["slug"])); h.append(cta_eq("../../")); h.append(rodape("../../"))
        os.makedirs(OUT + "materias/" + m["slug"], exist_ok=True); open(OUT + "materias/%s/index.html" % m["slug"], "w", encoding="utf-8").write("\n".join(h))
    h = [cabeca("Matérias · Estrela Negra", "Uma matéria para cada vídeo do canal: o tema aprofundado, com grau de certeza e fontes.", URL + "materias/", cartao("materias", "Matérias", "O tema de cada vídeo, aprofundado e com fonte", L5 + "T2012_webb_espelho.jpg"), "website", "../", "materias/")]
    h.append(topo_hero("%d matérias" % len(MATERIAS), "As<br><span>matérias</span>", "O tema de cada vídeo, aprofundado: o que foi medido, o que está em debate e de onde vem cada número.", "../img/anel_pag.jpg"))
    h.append('<div class="w"><section class="lista"><span class="rot">Lista</span><h2 class="tit2">Todas as <span style="color:var(--rx)">matérias</span></h2><div class="g4" style="margin-top:40px">%s</div></section></div>' % "".join('<a class="it" href="%s/"><img src="../%s" alt="%s" loading="lazy"><p class="n">%s</p><p class="s">%s</p></a>' % (m["slug"], m["d"]["img"], e(m["titulo"]), e(m["titulo"]), e(m["chapeu"])) for m in MATERIAS))
    h.append(rodape("../")); open(OUT + "materias/index.html", "w", encoding="utf-8").write("\n".join(h))
# ------------------------------------------------------------------ /links (página do link da bio)
dm = datetime.date.today().strftime("%d/%m")
hojef = next((x for x in FOTOS if x.get("data") == dm), None) or (FOTOS[0] if FOTOS else None)
og_l = cartao("links", "Estrela Negra", "Vídeos, fotos do céu e fontes num lugar só", L5 + "T1412_saturno_aneis_cassini.jpg")
btn = []
if DADOS: btn.append(('../%s/' % DADOS[0]["sl"], "Vídeo novo", DADOS[0]["titulo"], True))
if JORNAL: btn.append(("../" + ed_url(JORNAL[0]), "Notícia do dia", JORNAL[0]["titulo"], False))
if hojef: btn.append(('../fotos/%s/' % hojef["sl"], "Foto do céu de hoje", hojef["titulo"].split("(")[0].strip(), False))
btn += [(YT + "?sub_confirmation=1", "YouTube", "Inscreva-se no canal", False), (TT, "TikTok", "@estrelanegra_p", False), (INSTA, "Instagram", "@estrelanegra_p", False),
        ("../episodios/", "Episódios", "Todos os vídeos, com transcrição e fontes", False), ("../fotos/", "Fotos do céu", "James Webb, Hubble e ESO, explicadas", False)] + ([("../equipamentos/", "Equipamentos", "Binóculos, telescópios e livros indicados", False)] if COM_LOJA else []) + [("../contato/", "Contato", "Dúvidas, temas e parcerias", False)]
os.makedirs(OUT + "links")
open(OUT + "links/index.html", "w", encoding="utf-8").write("""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Estrela Negra · links</title><meta name="description" content="Vídeos, fotos do céu e fontes do canal de astronomia Estrela Negra."><link rel="canonical" href="%slinks/"><meta property="og:title" content="Estrela Negra"><meta property="og:description" content="Vídeos, fotos do céu e fontes num lugar só."><meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="../img/icone.png"><link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="../estilo.css">
<style>body{background:var(--esc) url(../img/grao.png) repeat;color:var(--off);min-height:100vh}.lk{max-width:520px;margin:0 auto;padding:56px 20px 64px;text-align:center;position:relative}
.lk:before{content:"";position:absolute;left:50%%;top:-120px;width:520px;height:520px;margin-left:-260px;background:radial-gradient(circle,rgba(135,98,243,.28),transparent 65%%);pointer-events:none}
.lk .av{width:112px;height:112px;border-radius:50%%;margin:0 auto;object-fit:cover;box-shadow:0 0 0 2px var(--rxl),0 0 40px rgba(135,98,243,.6);position:relative}
.lk h1{font-weight:300;font-size:40px;letter-spacing:-.02em;margin:22px 0 6px;position:relative}.lk h1 span{color:var(--rxl);text-shadow:0 0 26px rgba(168,139,255,.5)}
.lk .bio{color:var(--mu2);font-size:15px;margin:0 0 32px;position:relative}
.lk a.b{display:block;text-align:left;border:1px solid var(--lnd);background:rgba(22,20,28,.75);border-radius:16px;padding:16px 20px;margin-bottom:12px;position:relative;transition:all .2s}
.lk a.b:hover{border-color:var(--rxl);box-shadow:0 0 26px rgba(135,98,243,.35);transform:translateY(-2px)}
.lk a.b span{display:block;font-size:10px;font-weight:700;letter-spacing:.26em;text-transform:uppercase;color:var(--rxl);margin-bottom:4px}.lk a.b b{font-weight:500;font-size:16px;line-height:1.35}
.lk a.b.d{background:var(--rx);border-color:var(--rx);box-shadow:var(--glow)}.lk a.b.d span{color:#E9E2FF}
.lk a.b:after{content:"→";position:absolute;right:20px;top:50%%;transform:translateY(-50%%);color:var(--mu2)}
.lk .soc{justify-content:center;margin:28px 0 18px;display:flex}.lk small{font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--mu2)}</style></head><body><main class="lk">
<img class="av" src="../img/icone.png" alt="Estrela Negra"><h1>Estrela <span>Negra</span></h1><p class="bio">Astronomia com fonte: o que é certo, o que é debate e de onde vem cada número.</p>%s%s<small><a href="../">estrela-negra.github.io</a></small></main></body></html>""" % (URL, og_l, "".join('<a class="b%s" href="%s"><span>%s</span><b>%s</b></a>' % (" d" if dd else "", u, e(r), e(t)) for u, r, t, dd in btn), SOC))
hoje = datetime.date.today().isoformat()
urls = [URL, URL + "discussoes/", URL + "episodios/", URL + "fotos/", URL + "sobre/", URL + "contato/", URL + "links/"] + ([URL + "jornal/"] + [URL + ed_url(n) for n in JORNAL] if JORNAL else []) + ([URL + "equipamentos/"] if COM_LOJA else []) + [URL + d["sl"] + "/" for d in DADOS] + ([URL + "materias/"] + [URL + "materias/%s/" % m["slug"] for m in MATERIAS] if MATERIAS else []) + [URL + "fotos/%s/" % x["sl"] for x in FOTOS]
open(OUT + "sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, hoje) for u in urls) + "</urlset>")
# ---- comunidade: Discussões + privacidade + assets
import shutil
shutil.copytree(AQUI + "/dados", OUT + "dados", dirs_exist_ok=True)
os.makedirs(OUT + "assets", exist_ok=True)
for _f in ("comunidade.js", "comunidade.css", "firebase-config.js", "analytics.js", "numeros.js"): shutil.copy(AQUI + "/comunidade/" + _f, OUT + "assets/" + _f)
os.makedirs(OUT + "discussoes", exist_ok=True)
h = [cabeca("Discussões · Estrela Negra", "Converse sobre astronomia com quem acompanha o Estrela Negra: perguntas, notícias e fotos do céu.", URL + "discussoes/", URL + "img/og/inicio.jpg", "website", "../", "discussoes/"), "</div>",
     '<div class="w"><span class="rot">Comunidade</span><h1 class="tit" style="margin-top:12px">Discussões</h1><p style="max-width:640px;color:var(--mu)">Perguntas, notícias, fotos que você fez do céu. Entre com o Google, abra um tópico e vote nos que valem a pena.</p>'
     '<div id="en-forum"></div></div><link rel="stylesheet" href="../assets/comunidade.css"><script src="../assets/firebase-config.js"></script><script src="../assets/comunidade.js" data-raiz="../" defer></script>', rodape("../")]
open(OUT + "discussoes/index.html", "w", encoding="utf-8").write("\n".join(h))
os.makedirs(OUT + "privacidade", exist_ok=True)
PRIV = [("Quem somos", "O Estrela Negra é um canal de divulgação de astronomia feito por Bruno Porciúncula. Este site é estático; os comentários e as Discussões usam o Firebase (Google) para login e para guardar as mensagens."),
        ("O que guardamos", "Quando você entra com o Google, guardamos o seu nome público, a sua foto de perfil e um identificador da conta, junto com o texto que você publica e a data. Não guardamos o seu e-mail no site e não vendemos nem compartilhamos dados."),
        ("Para que usamos", "Só para mostrar quem escreveu cada comentário ou tópico, permitir que você remova o que publicou e moderar abusos (base legal: legítimo interesse e o seu consentimento ao publicar, conforme a LGPD)."),
        ("Estatísticas de visita", "Se você aceitar no aviso de cookies, o site usa o Google Analytics para contar visitas e páginas lidas, de forma agregada. Não usamos cookies de publicidade. Se recusar, nenhum cookie de análise é gravado; para mudar a escolha, limpe os dados do site no seu navegador."),
        ("Seus direitos", "Você pode remover o que publicou pelo botão Remover. Para apagar todos os seus dados ou tirar dúvidas, use a página de contato do site."),
        ("Regras da conversa", "Sem ofensas, preconceito, spam ou propaganda. Discorde do argumento, não da pessoa. Ao falar de dados, cite a fonte. Conteúdo denunciado pode ser removido pela moderação.")]
h = [cabeca("Privacidade e regras · Estrela Negra", "Como o Estrela Negra trata os dados de quem comenta e as regras das Discussões.", URL + "privacidade/", URL + "img/og/inicio.jpg", "website", "../", ""), "</div>",
     '<div class="w"><article class="art"><h1>Privacidade e regras</h1>' + "".join("<h2>%s</h2><p>%s</p>" % (e(a), e(b)) for a, b in PRIV) + "</article></div>", rodape("../")]
open(OUT + "privacidade/index.html", "w", encoding="utf-8").write("\n".join(h))
open(OUT + "robots.txt", "w").write("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % URL); open(OUT + ".nojekyll", "w").write("")
open(OUT + "google019414cc94055bb3.html", "w").write("google-site-verification: google019414cc94055bb3.html")  # Search Console (não apagar)
print("ok", len(DADOS), "vídeos +", len(MATERIAS), "matérias +", len(FOTOS), "fotos + 5 páginas", "(PRÉVIA COM TODOS)" if TODOS else "")

