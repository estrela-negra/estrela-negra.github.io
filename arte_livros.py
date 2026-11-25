"""Mockups de livro (fundo claro isolado, capa tipográfica com título e autor reais) para a página Equipamentos.
Não copia a capa da editora: cor e desenho são próprios. Saída: arte/loja/<ASIN>.jpg (720x540)."""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = AQUI + "/arte/loja/"
F = os.path.expanduser("~/Library/Fonts/SpaceGrotesk-VariableFont_wght.ttf")
def fonte(t, w):
    f = ImageFont.truetype(F, t); f.set_variation_by_axes([w]); return f
LIVROS = [  # asin, título, autor, cor de fundo, cor do texto, motivo
 ("8535929886", "Cosmos", "Carl Sagan", (14, 18, 38), (240, 232, 214), "espiral"),
 ("8535931937", "Pálido ponto azul", "Carl Sagan", (8, 10, 16), (226, 230, 238), "ponto"),
 ("8580576466", "Uma breve história do tempo", "Stephen Hawking", (20, 16, 40), (238, 210, 140), "anel"),
 ("8551010255", "Breves respostas para grandes questões", "Stephen Hawking", (236, 232, 222), (30, 26, 40), "anel_esc"),
 ("8558890765", "A história do universo para quem tem pressa", "Colin Stuart", (32, 54, 92), (250, 246, 236), "estrelas"),
 ("854220753X", "Morte no buraco negro", "Neil deGrasse Tyson", (10, 10, 12), (250, 170, 60), "buraco"),
 ("8578614437", "Aprendendo a ler o céu", "Rodolfo Langhi", (18, 40, 74), (250, 246, 236), "constelacao"),
 ("8542302680", "Planetas e estrelas", "Arjuna C. Panzera", (40, 24, 70), (250, 246, 236), "planetas"),
 ("8576085097", "Astronomia para leigos", "Stephen P. Maran", (250, 214, 40), (20, 20, 20), "planetas_esc"),
 ("8578614852", "Astronomia e Astrofísica", "Kepler de S. Oliveira Filho · Maria de F. O. Saraiva", (230, 228, 222), (20, 34, 70), "orbitas"),
 ("852120745X", "Curso de Física Básica 1 · Mecânica", "H. Moysés Nussenzveig", (150, 30, 34), (250, 246, 236), "pendulo"),
 ("8521637225", "Fundamentos de Física 1 · Mecânica", "Halliday · Resnick · Walker", (12, 70, 110), (250, 246, 236), "orbitas_cl"),
 ("6555651326", "O guia do mochileiro das galáxias", "Douglas Adams", (20, 20, 22), (120, 230, 120), "42"),
 ("8580414482", "Perdido em Marte", "Andy Weir", (150, 60, 30), (250, 240, 220), "marte"),
 ("8535913513", "Contato", "Carl Sagan", (12, 14, 30), (220, 230, 250), "antenas"),
]
def quebra(d, txt, f, larg):
    ls, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= larg: cur = t
        else: ls.append(cur); cur = w
    return ls + [cur]
def capa(tit, aut, bg, fg, mot, W=330, H=480, seed=0):
    c = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(c); rnd = random.Random(seed)
    acc = tuple(int(fg[i] * .55 + bg[i] * .45) for i in range(3))
    cx, cy = W // 2, int(H * .62)
    if mot in ("estrelas", "espiral", "constelacao", "contato", "antenas", "ponto", "anel", "buraco", "planetas", "marte", "orbitas", "42"):
        for _ in range(70 if mot != "ponto" else 120): x, y = rnd.randrange(W), rnd.randrange(H); r = rnd.choice([0, 0, 1]); d.ellipse((x - r, y - r, x + r, y + r), fill=acc)
    if mot == "espiral":
        import math
        for k in range(900):
            a = k * .045; r = 4 + k * .11; x = cx + r * math.cos(a); y = cy + r * math.sin(a) * .55
            d.ellipse((x - 1.4, y - 1.4, x + 1.4, y + 1.4), fill=fg)
    elif mot == "ponto": d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(120, 170, 255)); d.line((cx - 120, cy - 40, cx + 120, cy + 30), fill=acc, width=1)
    elif mot in ("anel", "anel_esc"): d.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), outline=fg, width=3); d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=fg)
    elif mot == "buraco": 
        for k in range(14): d.ellipse((cx - 60 - k * 3, cy - 60 - k * 3, cx + 60 + k * 3, cy + 60 + k * 3), outline=tuple(int(fg[i] * (1 - k / 14) + bg[i] * k / 14) for i in range(3)), width=2)
        d.ellipse((cx - 58, cy - 58, cx + 58, cy + 58), fill=(0, 0, 0))
    elif mot == "estrelas":
        for _ in range(5): x, y = rnd.randrange(40, W - 40), rnd.randrange(int(H * .45), H - 60); d.regular_polygon((x, y, 7), 4, fill=fg)
    elif mot == "constelacao":
        pts = [(70, 300), (130, 270), (180, 300), (230, 260), (270, 330), (200, 380)]
        d.line(pts, fill=acc, width=2); [d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=fg) for x, y in pts]
    elif mot in ("planetas", "planetas_esc"):
        for k, (r, col) in enumerate([(46, fg), (22, acc), (14, fg)]): x = 90 + k * 85; d.ellipse((x - r, cy - r, x + r, cy + r), fill=col)
    elif mot in ("orbitas", "orbitas_cl"):
        for r in (40, 75, 110): d.ellipse((cx - r, cy - r * .55, cx + r, cy + r * .55), outline=fg, width=2)
        d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=fg)
    elif mot == "pendulo": d.line((cx, int(H * .45), cx + 60, cy + 70), fill=fg, width=3); d.ellipse((cx + 44, cy + 54, cx + 76, cy + 86), fill=fg)
    elif mot == "42": d.text((cx, cy), "42", font=fonte(130, 700), fill=fg, anchor="mm")
    elif mot == "marte": d.ellipse((cx - 85, cy - 85, cx + 85, cy + 85), fill=(196, 92, 52)); d.ellipse((cx - 85, cy - 85, cx + 85, cy + 85), outline=fg, width=2)
    elif mot == "antenas":
        for k in range(3): x = 80 + k * 85; d.arc((x - 34, cy - 10, x + 34, cy + 50), 180, 360, fill=fg, width=3); d.line((x, cy + 20, x, cy + 80), fill=fg, width=3)
    ft = fonte(34 if len(tit) < 22 else 28 if len(tit) < 36 else 24, 500); y = 34
    for l in quebra(d, tit, ft, W - 48): d.text((24, y), l, font=ft, fill=fg); y += int(ft.size * 1.12)
    fa = fonte(13, 700); y2 = H - 28
    for l in reversed(quebra(d, aut.upper(), fa, W - 48)): d.text((24, y2), l, font=fa, fill=fg, anchor="ls"); y2 -= 18
    return c
def mockup(cv, bg_spine):
    W, H = 720, 540; im = Image.new("RGB", (W, H), (244, 242, 238))
    s = 0.92; cv = cv.resize((int(cv.width * s), int(cv.height * s)), Image.LANCZOS); cw, ch = cv.size
    x0, y0 = (W - cw) // 2 + 10, (H - ch) // 2 - 6
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle((x0 + 10, y0 + 18, x0 + cw + 14, y0 + ch + 12), fill=120); sh = sh.filter(ImageFilter.GaussianBlur(16))
    im.paste((180, 176, 170), (0, 0), sh)
    d = ImageDraw.Draw(im); esp = 22
    d.polygon([(x0 - esp, y0 + 6), (x0, y0), (x0, y0 + ch), (x0 - esp, y0 + ch - 6)], fill=tuple(int(c * .62) for c in bg_spine))
    d.rectangle((x0 + cw - 2, y0 + 3, x0 + cw + 6, y0 + ch - 3), fill=(236, 230, 214))
    for k in range(0, ch - 8, 3): d.line((x0 + cw - 1, y0 + 4 + k, x0 + cw + 5, y0 + 4 + k), fill=(220, 212, 194))
    im.paste(cv, (x0, y0))
    gl = Image.new("L", (cw, ch), 0); ImageDraw.Draw(gl).rectangle((0, 0, 10, ch), fill=60); im.paste((255, 255, 255), (x0, y0), gl.filter(ImageFilter.GaussianBlur(4)))
    return im
os.makedirs(OUT, exist_ok=True)
for k, (asin, tit, aut, bg, fg, mot) in enumerate(LIVROS):
    mockup(capa(tit, aut, bg, fg, mot, seed=k), bg).save(OUT + asin + ".jpg", quality=88)
print("ok", len(LIVROS))
