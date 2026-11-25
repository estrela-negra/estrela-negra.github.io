"""Artes de luz do site (mesmo sistema dos posts LUZ): anel da abertura, retrato do Bruno com anel, feixe, grão.
uso: python3 arte_site.py  → site/arte/*.png|jpg (o gera_site.py copia para docs/img)"""
import sys, os, math, numpy as np
sys.path.insert(0, "/Users/porciuncula/Desktop/BRUNO/estrela-negra/scripts/behance")
from _base_luz import Luz, ESC
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.dirname(os.path.abspath(__file__)) + "/arte/"
# 1) abertura: anel grande nascendo + ponto
L = Luz(1400, 1000); L.anel(760, 520, 330, ang0=math.radians(200), pot=2.6, f=1.15, fino=3.6, halo=46); L.apaga(760, 520, 330)
L.ponto(760, 520, r=9, f=1.0, halo=90); L.ponto(1088, 420, r=5, f=1.0, halo=30); L.img(grao=7, seed=3).save(OUT + "hero_anel.jpg", quality=90)
# 2) anel pequeno para cabeçalhos de página
L = Luz(900, 700); L.anel(470, 350, 200, f=1.0, fino=3.0, halo=30); L.ponto(470, 350, r=6, f=0.9, halo=40); L.img(grao=7, seed=4).save(OUT + "anel_pag.jpg", quality=90)
# 3) feixe horizontal (divisor) e feixe vertical
L = Luz(1400, 120); L.feixe(40, 60, 1360, 60, larg=2.2, f=0.75, halo=26, cresce=False); L.ponto(700, 60, r=5, halo=40); L.img(grao=6, seed=5).save(OUT + "feixe.jpg", quality=90)
# 4) retrato com anel de luz (fundo escuro)
S = 1100; L = Luz(S, S)
foto = Image.open("/Users/porciuncula/Desktop/BRUNO/estrela-negra/assets/fotos/bruno_2026_editada.jpg").convert("RGB")
w, h = foto.size; c = foto.crop((int(w * 0.24), 0, int(w * 0.24) + int(h * 0.95), int(h * 0.95))).resize((760, 760), Image.LANCZOS)
L.anel(S / 2, S / 2, 410, f=1.05, fino=3.2, halo=40); L.ponto(S / 2 + 410 * math.cos(-0.6), S / 2 + 410 * math.sin(-0.6), r=9, f=1.0, halo=50)
base = L.img(grao=6, seed=6)
m = Image.new("L", (760, 760), 0); ImageDraw.Draw(m).ellipse((0, 0, 759, 759), fill=255); m = m.filter(ImageFilter.GaussianBlur(1.2))
base.paste(c, ((S - 760) // 2, (S - 760) // 2), m); base.save(OUT + "bruno_anel.jpg", quality=92)
# 5) grão em tile transparente (textura)
rng = np.random.default_rng(9); n = rng.normal(128, 40, (256, 256)).clip(0, 255).astype(np.uint8)
g = Image.fromarray(np.dstack([n, n, n, np.full((256, 256), 22, np.uint8)]), "RGBA"); g.save(OUT + "grao.png")
print("ok", sorted(os.listdir(OUT)))
# 6) retrato SEM moldura (pedido do Bruno em 24/11): foto em cor natural se dissolvendo no fundo escuro, com grão
foto = Image.open("/Users/porciuncula/Desktop/BRUNO/estrela-negra/assets/fotos/bruno_2026_editada.jpg").convert("RGB")
w, h = foto.size; c = foto.crop((int(w * 0.17), 0, int(w * 0.83), h)).resize((1000, 1000), Image.LANCZOS)
a = np.asarray(c, np.float32); Y, X = np.mgrid[0:1000, 0:1000].astype(np.float32)
sm = lambda v: np.clip(v, 0, 1) ** 2 * (3 - 2 * np.clip(v, 0, 1))
k = 1 - sm(X / 380) * sm((999 - X) / 380) * sm((999 - Y) / 460) * sm(Y / 260)
fundo = np.array(ESC, np.float32); a = a * (1 - k[..., None]) + fundo * k[..., None]
a += np.random.default_rng(11).normal(0, 4, (1000, 1000, 1)); Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(OUT + "bruno_foto.jpg", quality=92)
print("ok retrato sem moldura")
