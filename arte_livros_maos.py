"""Mockup: capa oficial do livro aplicada num livro segurado por mãos (fotos de acervo Freepik em arte/loja/_mock).
Mantém polegares e sombras por cima da capa. Saída arte/loja/<ISBN10>.jpg (720x540). Capas em arte/loja/_capas/(pub_|ol_)<ISBN>.jpg"""
import os, sys
from PIL import Image, ImageChops, ImageFilter, ImageOps
AQUI = os.path.dirname(os.path.abspath(__file__)); D = AQUI + "/arte/loja/"
# retângulo da capa (sem a lombada) em coordenadas da prévia de 900 px de largura
BASES = {"maos1.jpg": (318, 98, 593, 497, 4692 / 900), "maos2.jpg": (298, 61, 609, 501, 3000 / 900)}
def capa_de(isbn):
    for p in ("pub_", "ol_"):
        f = D + "_capas/%s%s.jpg" % (p, isbn)
        if os.path.exists(f) and os.path.getsize(f) > 3000: return f
def compoe(isbn, base):
    x0, y0, x1, y1, s = BASES[base]; im = Image.open(D + "_mock/" + base).convert("RGB")
    box = tuple(int(v * s) for v in (x0, y0, x1, y1)); w, h = box[2] - box[0], box[3] - box[1]
    cv = ImageOps.fit(Image.open(capa_de(isbn)).convert("RGB"), (w, h), Image.LANCZOS)
    reg = im.crop(box)
    # sombreado do papel: luminância normalizada pelo branco da capa
    L = reg.convert("L"); ref = sorted(L.getdata())[int(w * h * .9)] or 255
    sh = L.point(lambda v: min(255, int(v * 255 / ref)))
    mult = ImageChops.multiply(cv, Image.merge("RGB", (sh, sh, sh)))
    # máscara de pele (polegares): tons quentes ou escuros ficam da foto original
    r, g, b = reg.split()
    pele = ImageChops.subtract(r, b).point(lambda v: 255 if v > 22 else 0)
    pele = pele.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.composite(reg, mult, pele); im.paste(out, box)
    # recorte final 4:3 centrado no livro
    cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2 + int(h * .08); H = min(int(h * 1.32), im.height); W = min(int(H * 4 / 3), im.width); H = int(W * 3 / 4)
    l = min(max(0, cx - W // 2), im.width - W); t = min(max(0, cy - H // 2), im.height - H)
    return im.crop((l, t, l + W, t + H)).resize((720, 540), Image.LANCZOS)
def plano(cv):
    """capa quadrada ou deitada: capa plana em fundo claro com sombra suave"""
    cv = cv.convert("RGB"); W, H = 720, 540; im = Image.new("RGB", (W, H), (242, 241, 239)); cv.thumbnail((int(W * .7), int(H * .74)), Image.LANCZOS)
    x, y = (W - cv.width) // 2, (H - cv.height) // 2 - 6
    sh = Image.new("L", (W, H), 0); sh.paste(150, (x + 8, y + 14, x + cv.width + 8, y + cv.height + 14)); sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.paste((170, 168, 164), (0, 0), sh); im.paste(cv, (x, y)); return im
if __name__ == "__main__":
    L = [a for a in sys.argv[1:]] or [f.split("_", 1)[1][:-4] for f in os.listdir(D + "_capas") if f.endswith(".jpg")]
    for k, isbn in enumerate(sorted(set(L))):
        if not capa_de(isbn): print("sem capa", isbn); continue
        cv = Image.open(capa_de(isbn))
        if cv.width / cv.height > .85: plano(cv).save(D + isbn + ".jpg", quality=88); print("plano", isbn); continue
        compoe(isbn, "maos2.jpg").save(D + isbn + ".jpg", quality=88); print("ok", isbn)
