#!/usr/bin/env python3
"""Portades il·lustrades dels articles del Diari.

Cada portada és una il·lustració plana en la paleta de la marca: un paisatge
retallat al fons i un objecte que explica el tema de l'article. El codi SVG de
cada portada queda a _build/portades/<article>.svg i la imatge final, a
assets/covers/<article>.jpg (és la que fa servir la web).

Per tornar-les a generar cal Playwright amb Chromium:
    python3 _build/portades.py            (totes)
    python3 _build/portades.py calendari-xarxes-casa-rural   (una)
"""

import asyncio
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_build" / "portades"
OUT = ROOT / "assets" / "covers"
W, H = 1600, 1000

# Paleta (marca + tons derivats per il·lustrar)
PAPER = "#F6F3EE"
PAPER2 = "#EFE9E1"
SAND = "#E7DFD6"
SAND2 = "#D6CCC0"
KRAFT = "#C9B49B"
INK = "#1C1C1A"
TERRA = "#C46A4A"
TERRA_INK = "#9A4A30"
TERRA_L = "#E7BFAC"
TERRA_BG = "#EDD7CB"
SAGE = "#7A8A78"
SAGE_INK = "#56644F"
SAGE_L = "#B9C2B4"
SAGE_BG = "#D5DACF"


# ---------------------------------------------------------------- pieces

def frame(bg, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <filter id="gra" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" seed="7"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="table" tableValues="0 0.28"/></feComponentTransfer>
  </filter>
</defs>
<rect width="{W}" height="{H}" fill="{bg}"/>
{body}
<rect width="{W}" height="{H}" filter="url(#gra)" style="mix-blend-mode:multiply"/>
</svg>"""


def sun(cx, cy, r, color=TERRA):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'


def hills(top=640, colors=(SAND2, SAGE_L, SAGE), seed=0):
    """Tres capes de turons, de més lluny a més a prop."""
    shapes = [
        f"M0 {top} C 260 {top-80} 520 {top-40} 760 {top+10} S 1260 {top-40} 1600 {top-80} V{H} H0Z",
        f"M0 {top+120} C 300 {top+40} 600 {top+60} 900 {top+120} S 1400 {top+100} 1600 {top+60} V{H} H0Z",
        f"M0 {top+240} C 350 {top+180} 700 {top+200} 1000 {top+240} S 1450 {top+220} 1600 {top+210} V{H} H0Z",
    ]
    if seed % 2:
        shapes = [s.replace("C 260", "C 340").replace("S 1260", "S 1180") for s in shapes]
    return "".join(f'<path d="{d}" fill="{c}"/>' for d, c in zip(shapes, colors))


def ground(y, color):
    return f'<rect x="0" y="{y}" width="{W}" height="{H-y}" fill="{color}"/>'


def cypress(cx, base, h=260, w=74, color=SAGE_INK):
    return (f'<path d="M{cx} {base-h} C {cx+w*0.62} {base-h*0.62} {cx+w*0.55} {base-h*0.12} {cx} {base} '
            f'C {cx-w*0.55} {base-h*0.12} {cx-w*0.62} {base-h*0.62} {cx} {base-h}Z" fill="{color}"/>')


def sprig(x, y, scale=1.0, rot=0, color=SAGE_INK):
    """Branca d'avet: un tronc i agulles a banda i banda."""
    needles = []
    for i in range(9):
        t = i * 30
        L = 70 - i * 5
        needles.append(f'<path d="M{t} 0 l{-L*0.55} {-L*0.75}" />')
        needles.append(f'<path d="M{t} 0 l{-L*0.55} {L*0.75}" />')
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({scale})" stroke="{color}" '
            f'stroke-width="12" stroke-linecap="round" fill="none">'
            f'<path d="M-30 0 H260"/>{"".join(needles)}</g>')


def bottle(x, base, h=420, w=120, body=INK, label=PAPER, cap=TERRA):
    neck_w = w * 0.34
    shoulder = base - h * 0.62
    top = base - h
    lx, lw = x - w / 2 + 10, w - 20
    return (f'<path d="M{x-neck_w/2} {top} h{neck_w} v{h*0.2} '
            f'C {x+neck_w/2} {shoulder-h*0.06} {x+w/2} {shoulder-h*0.04} {x+w/2} {shoulder+h*0.06} '
            f'V{base-14} a14 14 0 0 1 -14 14 H{x-w/2+14} a14 14 0 0 1 -14 -14 V{shoulder+h*0.06} '
            f'C {x-w/2} {shoulder-h*0.04} {x-neck_w/2} {shoulder-h*0.06} {x-neck_w/2} {top+h*0.2}Z" fill="{body}"/>'
            f'<rect x="{x-neck_w/2-3}" y="{top}" width="{neck_w+6}" height="{h*0.12}" rx="5" fill="{cap}"/>'
            f'<rect x="{lx}" y="{base-h*0.42}" width="{lw}" height="{h*0.22}" rx="4" fill="{label}"/>'
            f'<rect x="{lx+18}" y="{base-h*0.42+h*0.07}" width="{lw-36}" height="8" fill="{cap}"/>')


def jar(x, base, w=150, h=170, body=PAPER, lid=TERRA, label=SAND2):
    return (f'<rect x="{x-w/2}" y="{base-h}" width="{w}" height="{h}" rx="22" fill="{body}"/>'
            f'<rect x="{x-w/2+8}" y="{base-h-36}" width="{w-16}" height="40" rx="8" fill="{lid}"/>'
            f'<rect x="{x-w/2+18}" y="{base-h*0.62}" width="{w-36}" height="{h*0.34}" rx="4" fill="{label}"/>')


def star(cx, cy, r, color):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr*math.cos(ang):.1f},{cy + rr*math.sin(ang):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}"/>'


def lines(x, y, widths, color=SAND2, gap=26, h=12):
    return "".join(f'<rect x="{x}" y="{y+i*gap}" width="{w}" height="{h}" rx="{h/2}" fill="{color}"/>'
                   for i, w in enumerate(widths))


# ---------------------------------------------------------------- covers

def casa_rural():
    house = []
    house.append(f'<rect x="948" y="300" width="46" height="110" fill="{PAPER2}"/>')            # xemeneia
    house.append(f'<rect x="560" y="430" width="480" height="340" fill="{PAPER}"/>')            # cos
    house.append(f'<polygon points="520,452 800,318 1080,452 1080,474 800,342 520,474" fill="{TERRA}"/>')
    house.append(f'<polygon points="560,452 800,338 1040,452" fill="{PAPER}"/>')               # timpà
    house.append(f'<circle cx="800" cy="410" r="20" fill="{INK}"/>')
    for wx in (612, 928):
        for wy in (500, 625):
            house.append(f'<rect x="{wx}" y="{wy}" width="60" height="78" fill="{INK}"/>')
            house.append(f'<rect x="{wx-20}" y="{wy}" width="16" height="78" fill="{SAGE}"/>')
            house.append(f'<rect x="{wx+64}" y="{wy}" width="16" height="78" fill="{SAGE}"/>')
    house.append(f'<path d="M742 770 V668 A58 58 0 0 1 858 668 V770Z" fill="{INK}"/>')
    house.append(f'<path d="M760 770 V672 A40 40 0 0 1 840 672 V770Z" fill="{TERRA_INK}"/>')
    body = (sun(1210, 250, 112) + hills(620, (SAND2, SAGE_L, SAGE)) + cypress(455, 770, 290) +
            cypress(1150, 770, 250, 66) + "".join(house) + ground(770, SAGE) +
            f'<path d="M0 840 C 400 800 1000 820 1600 790 V1000 H0Z" fill="{SAGE_INK}"/>')
    return frame(SAND, body)


def producte_xarxes():
    phone = (f'<g transform="rotate(-7 800 500)">'
             f'<rect x="610" y="140" width="380" height="720" rx="52" fill="{INK}"/>'
             f'<rect x="630" y="160" width="340" height="680" rx="36" fill="{PAPER}"/>'
             f'<circle cx="676" cy="214" r="22" fill="{TERRA}"/>'
             + lines(712, 202, [150], SAND2, 26, 14) +
             f'<rect x="650" y="258" width="300" height="300" fill="{TERRA_L}"/>'
             + jar(800, 520, 130, 150, PAPER, INK, TERRA)
             + lines(660, 590, [240, 200, 120], SAND2, 32, 14) +
             f'<rect x="660" y="700" width="130" height="44" rx="22" fill="{SAGE}"/>'
             f'</g>')
    wheat = []
    for i, (x, y) in enumerate(((1120, 760), (1165, 770), (1080, 775))):
        wheat.append(f'<path d="M{x} {y} C {x+6} {y-140} {x+18} {y-230} {x+40} {y-330}" stroke="{TERRA_INK}" stroke-width="8" fill="none" stroke-linecap="round"/>')
        for k in range(6):
            yy = y - 220 - k * 22
            xx = x + 26 + k * 3
            wheat.append(f'<ellipse cx="{xx-12}" cy="{yy}" rx="9" ry="20" transform="rotate(-25 {xx-12} {yy})" fill="{TERRA}"/>')
            wheat.append(f'<ellipse cx="{xx+12}" cy="{yy-6}" rx="9" ry="20" transform="rotate(25 {xx+12} {yy-6})" fill="{TERRA}"/>')
    body = (sun(380, 250, 120, PAPER) + hills(660, (SAGE_L, SAGE, SAGE_INK), 1) + phone + "".join(wheat))
    return frame(SAGE_BG, body)


def restaurant_mobil():
    plate = (f'<circle cx="760" cy="520" r="280" fill="{PAPER}"/>'
             f'<circle cx="760" cy="520" r="212" fill="none" stroke="{SAND2}" stroke-width="8"/>'
             f'<circle cx="760" cy="520" r="128" fill="{TERRA}"/>'
             f'<circle cx="725" cy="490" r="34" fill="{TERRA_INK}"/>'
             f'<circle cx="806" cy="560" r="26" fill="{TERRA_INK}"/>'
             f'<ellipse cx="790" cy="470" rx="22" ry="44" transform="rotate(35 790 470)" fill="{SAGE}"/>'
             f'<ellipse cx="700" cy="570" rx="20" ry="40" transform="rotate(-40 700 570)" fill="{SAGE_INK}"/>'
             f'<ellipse cx="830" cy="520" rx="16" ry="32" transform="rotate(80 830 520)" fill="{SAGE}"/>'
             f'<circle cx="760" cy="600" r="9" fill="{PAPER}"/><circle cx="690" cy="470" r="7" fill="{PAPER}"/>')
    fork = (f'<g fill="{INK}"><rect x="386" y="330" width="14" height="110" rx="7"/><rect x="418" y="330" width="14" height="110" rx="7"/>'
            f'<rect x="450" y="330" width="14" height="110" rx="7"/><path d="M386 430 h78 v20 c0 30 -18 44 -30 50 v230 a9 9 0 0 1 -18 0 v-230 c-12 -6 -30 -20 -30 -50z"/></g>')
    knife = f'<path d="M1250 320 c-50 40 -64 120 -64 220 h40 v210 a12 12 0 0 0 24 0z" fill="{INK}"/>'
    phone = (f'<g transform="rotate(14 980 470)">'
             f'<rect x="830" y="190" width="300" height="560" rx="44" fill="none" stroke="{INK}" stroke-width="26"/>'
             f'<g stroke="{PAPER}" stroke-width="8" fill="none" stroke-linecap="round">'
             f'<path d="M870 260 v-30 h30"/><path d="M1090 260 v-30 h-30"/><path d="M870 680 v30 h30"/><path d="M1090 680 v30 h-30"/></g>'
             f'</g>')
    body = plate + fork + phone + knife
    return frame(TERRA_BG, body)


def reserva_directa():
    win = [f'<rect x="400" y="200" width="800" height="560" rx="18" fill="{PAPER}"/>',
           f'<path d="M400 218 a18 18 0 0 1 18 -18 h764 a18 18 0 0 1 18 18 v42 h-800z" fill="{INK}"/>']
    for i, c in enumerate((TERRA, SAND2, SAND2)):
        win.append(f'<circle cx="{440+i*34}" cy="230" r="10" fill="{c}"/>')
    win.append(lines(452, 292, [260], SAND2, 0, 18))
    booked = {(1, 1), (2, 1), (3, 1), (4, 3), (5, 3), (0, 4), (1, 4)}
    mine = {(3, 2), (4, 2)}
    for r in range(5):
        for c in range(7):
            x = 452 + c * 100
            y = 340 + r * 76
            fill = TERRA if (c, r) in booked else (SAGE if (c, r) in mine else SAND)
            win.append(f'<rect x="{x}" y="{y}" width="84" height="60" rx="6" fill="{fill}"/>')
    key = (f'<g transform="rotate(-32 1180 720)">'
           f'<circle cx="1060" cy="720" r="96" fill="{TERRA_INK}"/><circle cx="1060" cy="720" r="40" fill="{SAND}"/>'
           f'<rect x="1140" y="698" width="300" height="44" rx="10" fill="{TERRA_INK}"/>'
           f'<rect x="1350" y="742" width="34" height="56" fill="{TERRA_INK}"/><rect x="1400" y="742" width="34" height="38" fill="{TERRA_INK}"/></g>')
    body = sun(1230, 210, 100, TERRA_L) + "".join(win) + key
    return frame(SAND, body)


def fitxa_google():
    shop = [f'<rect x="560" y="430" width="480" height="370" fill="{PAPER}"/>',
            f'<rect x="590" y="300" width="420" height="70" fill="{INK}"/>',
            lines(700, 326, [200], PAPER, 0, 18)]
    # tendal a ratlles
    for i in range(8):
        x = 540 + i * 65
        fill = TERRA if i % 2 == 0 else PAPER2
        shop.append(f'<path d="M{x} 370 h65 v70 a32.5 32.5 0 0 1 -65 0z" fill="{fill}"/>')
    shop.append(f'<rect x="600" y="520" width="230" height="200" fill="{INK}"/>')
    shop.append(f'<path d="M630 690 l60 -140 M680 690 l40 -90" stroke="{SAGE_L}" stroke-width="10" stroke-linecap="round"/>')
    shop.append(f'<rect x="870" y="520" width="130" height="280" fill="{SAGE_INK}"/>')
    shop.append(f'<circle cx="980" cy="660" r="9" fill="{PAPER}"/>')
    pin = (f'<path d="M800 300 c-60 -70 -110 -120 -110 -180 a110 110 0 0 1 220 0 c0 60 -50 110 -110 180z" fill="{TERRA}"/>'
           f'<circle cx="800" cy="120" r="44" fill="{PAPER}"/>')
    card = [f'<rect x="1080" y="560" width="330" height="150" rx="14" fill="{PAPER}"/>']
    for i in range(5):
        card.append(star(1130 + i * 56, 610, 22, TERRA if i < 4 else SAND2))
    card.append(lines(1110, 652, [240, 170], SAND2, 26, 12))
    body = (hills(700, (SAGE_L, SAGE, SAGE_INK)) + "".join(shop) + ground(800, SAGE_INK) + pin + "".join(card))
    return frame(SAGE_BG, body)


def calendari_xarxes():
    board = [f'<rect x="420" y="190" width="760" height="620" rx="16" fill="{PAPER}"/>',
             f'<rect x="420" y="190" width="760" height="80" rx="16" fill="{INK}"/>',
             f'<rect x="420" y="240" width="760" height="30" fill="{INK}"/>']
    for i in range(6):
        board.append(f'<circle cx="{500+i*120}" cy="180" r="16" fill="{TERRA_INK}"/>')
    season = [SAND2, SAND2, SAGE_L, SAGE_L, SAGE, TERRA_L, TERRA_L, TERRA, KRAFT, KRAFT, TERRA_INK, SAND2]
    for k, col in enumerate(season):
        r, c = divmod(k, 4)
        x = 460 + c * 175
        y = 300 + r * 165
        board.append(f'<rect x="{x}" y="{y}" width="155" height="145" rx="8" fill="{col}"/>')
        board.append(f'<rect x="{x+18}" y="{y+18}" width="56" height="12" rx="6" fill="{PAPER}" opacity="0.85"/>')
    board.append(f'<rect x="1000" y="465" width="155" height="145" rx="8" fill="none" stroke="{INK}" stroke-width="8"/>')
    phone = (f'<g transform="rotate(10 1240 700)"><rect x="1150" y="520" width="190" height="350" rx="30" fill="{INK}"/>'
             f'<rect x="1163" y="533" width="164" height="324" rx="20" fill="{PAPER}"/>'
             f'<rect x="1178" y="580" width="134" height="134" fill="{TERRA}"/>'
             f'<circle cx="1245" cy="647" r="30" fill="{TERRA_L}"/>' + lines(1178, 730, [134, 100], SAND2, 26, 12) + '</g>')
    body = "".join(board) + phone
    return frame(PAPER2, body)


def celler():
    dx = -90
    barrel = (f'<g transform="translate({dx} 0)">'
              f'<path d="M520 330 C 470 420 470 700 520 790 H860 C 910 700 910 420 860 330Z" fill="{TERRA_INK}"/>'
              f'<path d="M690 330 V790" stroke="{TERRA}" stroke-width="6"/>'
              f'<path d="M600 330 C 585 450 585 670 600 790 M780 330 C 795 450 795 670 780 790" stroke="{TERRA}" stroke-width="6" fill="none"/>'
              f'<path d="M500 410 H880 M490 560 H890 M500 710 H880" stroke="{INK}" stroke-width="22"/>'
              f'<ellipse cx="690" cy="330" rx="172" ry="34" fill="{KRAFT}"/></g>')
    grapes = []
    ox, oy = 1150, 600
    for (gx, gy) in ((0, 0), (42, 0), (84, 0), (21, 36), (63, 36), (-21, 36), (105, 36), (0, 72), (42, 72), (84, 72), (21, 108), (63, 108), (42, 144)):
        grapes.append(f'<circle cx="{ox+gx}" cy="{oy+gy}" r="25" fill="{SAGE_INK}"/>')
    grapes.append(f'<path d="M{ox+42} {oy-28} C {ox+37} {oy-60} {ox+52} {oy-80} {ox+72} {oy-92}" stroke="{INK}" stroke-width="8" fill="none" stroke-linecap="round"/>')
    grapes.append(f'<path d="M{ox+72} {oy-92} c40 -40 110 -30 120 10 c-50 25 -100 25 -120 -10z" fill="{SAGE}"/>')
    body = (sun(1180, 260, 120, PAPER) + ground(790, SAND2) + barrel +
            bottle(960, 790, 430, 120, INK, PAPER, TERRA) + "".join(grapes) +
            f'<rect x="0" y="830" width="{W}" height="170" fill="{KRAFT}"/>')
    return frame(SAND, body)


def campanya_nadal():
    cal = [f'<g transform="rotate(-6 620 420)">',
           f'<rect x="400" y="200" width="440" height="460" rx="12" fill="{PAPER}"/>',
           f'<rect x="400" y="200" width="440" height="90" rx="12" fill="{TERRA}"/>',
           f'<rect x="400" y="260" width="440" height="30" fill="{TERRA}"/>']
    for r in range(5):
        for c in range(6):
            cal.append(f'<rect x="{430+c*66}" y="{320+r*62}" width="50" height="44" rx="4" fill="{SAND}"/>')
    cal.append(f'<circle cx="{430+3*66+25}" cy="{320+3*62+22}" r="40" fill="none" stroke="{INK}" stroke-width="8"/>')
    cal.append('</g>')
    boxes = (f'<rect x="760" y="520" width="380" height="290" fill="{KRAFT}"/>'
             f'<rect x="938" y="520" width="24" height="290" fill="{INK}"/><rect x="760" y="652" width="380" height="24" fill="{INK}"/>'
             f'<rect x="1010" y="380" width="240" height="190" fill="{TERRA}"/>'
             f'<rect x="1118" y="380" width="24" height="190" fill="{PAPER}"/><rect x="1010" y="462" width="240" height="24" fill="{PAPER}"/>'
             f'<path d="M1130 380 c-40 -60 -100 -40 -80 -10 c14 20 50 14 80 10z M1130 380 c40 -60 100 -40 80 -10 c-14 20 -50 14 -80 10z" fill="{PAPER}"/>'
             f'<rect x="1150" y="570" width="200" height="240" fill="{PAPER}"/>'
             f'<rect x="1238" y="570" width="24" height="240" fill="{SAGE}"/>')
    body = (ground(810, SAND2) + "".join(cal) + boxes + sprig(470, 800, 1.0, -8))
    return frame(TERRA_BG, body)


def vals_regal():
    env_back = f'<rect x="500" y="430" width="600" height="380" rx="10" fill="{SAND2}"/>'
    flap = f'<polygon points="500,440 800,250 1100,440" fill="{SAND2}"/>'
    card = (f'<g transform="rotate(-8 800 420)">'
            f'<rect x="560" y="250" width="480" height="300" rx="10" fill="{TERRA}"/>'
            f'<rect x="586" y="276" width="428" height="248" rx="6" fill="none" stroke="{PAPER}" stroke-width="5" stroke-dasharray="14 10"/>'
            f'<rect x="660" y="250" width="34" height="300" fill="{INK}"/>'
            f'<path d="M677 330 c-70 -70 -130 -20 -100 20 c20 26 70 10 100 -20z M677 330 c50 -80 120 -50 100 -10 c-14 26 -60 30 -100 10z" fill="{INK}"/>'
            + lines(760, 330, [200, 150], PAPER, 34, 16) +
            f'<rect x="760" y="430" width="120" height="56" rx="8" fill="{PAPER}"/>'
            f'</g>')
    front = (f'<path d="M500 470 L800 650 L1100 470 V800 a10 10 0 0 1 -10 10 H510 a10 10 0 0 1 -10 -10Z" fill="{PAPER}"/>'
             f'<path d="M500 800 L760 620 M1100 800 L840 620" stroke="{SAND2}" stroke-width="6"/>')
    body = (sun(1220, 260, 110, PAPER) + hills(700, (SAGE_L, SAGE, SAGE_INK), 1) + env_back + flap + card + front)
    return frame(SAGE_BG, body)


def lots_nadal():
    items = (bottle(640, 640, 440, 120, INK, PAPER, TERRA) +
             jar(800, 640, 150, 170, PAPER, TERRA, SAND2) +
             f'<polygon points="880,640 1060,640 1060,520" fill="{SAND2}"/>'
             f'<polygon points="880,640 1060,520 1000,505" fill="{PAPER2}"/>'
             f'<circle cx="1010" cy="600" r="12" fill="{KRAFT}"/><circle cx="975" cy="618" r="8" fill="{KRAFT}"/>')
    crate = (f'<rect x="500" y="600" width="600" height="230" fill="{KRAFT}"/>'
             f'<path d="M500 676 H1100 M500 752 H1100" stroke="{TERRA_INK}" stroke-width="10"/>'
             f'<rect x="500" y="600" width="600" height="18" fill="{TERRA_INK}"/>')
    corners = (f'<g stroke="{INK}" stroke-width="12" fill="none" stroke-linecap="square">'
               f'<path d="M420 260 V200 H480"/><path d="M1180 260 V200 H1120"/>'
               f'<path d="M420 840 V900 H480"/><path d="M1180 840 V900 H1120"/></g>')
    body = (ground(830, SAND2) + items + crate + sprig(1040, 610, 0.9, -28) + corners)
    return frame(PAPER2, body)


COVERS = {
    "preparar-casa-rural-sessio-fotos": casa_rural,
    "que-explicar-producte-local-xarxes": producte_xarxes,
    "fotos-restaurant-amb-el-mobil": restaurant_mobil,
    "web-propia-o-booking-reserva-directa": reserva_directa,
    "fitxa-de-google-del-teu-negoci": fitxa_google,
    "calendari-xarxes-casa-rural": calendari_xarxes,
    "preparar-celler-sessio-fotos-video": celler,
    "campanya-de-nadal-petit-negoci": campanya_nadal,
    "vals-regal-web": vals_regal,
    "fotografiar-lots-de-nadal": lots_nadal,
}


async def render(names):
    from playwright.async_api import async_playwright
    SRC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": W, "height": H})
        for name in names:
            svg = COVERS[name]()
            (SRC / f"{name}.svg").write_text(svg, encoding="utf-8")
            await page.set_content(f'<html><body style="margin:0">{svg}</body></html>')
            png = OUT / f"{name}.png"
            await page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": W, "height": H})
            try:
                from PIL import Image
                Image.open(png).convert("RGB").save(OUT / f"{name}.jpg", quality=84, optimize=True, progressive=True)
                png.unlink()
            except ImportError:
                pass
            print("portada:", name)
        await browser.close()


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(COVERS)
    asyncio.run(render(wanted))
