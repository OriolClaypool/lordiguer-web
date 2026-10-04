#!/usr/bin/env python3
"""Genera la web de L'Ordiguer.

Executa des de l'arrel del projecte:  python3 _build/build.py

Llegeix les pàgines de _build/pages, els articles de _build/diari i els blocs
compartits de _build/parts, i escriu els .html finals a l'arrel, a més del
mapa del lloc (sitemap.xml), robots.txt i la llista de fotos pendents.
Només fa servir la biblioteca estàndard de Python.
"""

import datetime
import hashlib
import html
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_build"

SITE = {
    "name": "L’Ordiguer Estudi",
    "base": "https://lordiguer.cat",
    "email": "agenciaordiguer@gmail.com",
    "instagram": "https://www.instagram.com/lordiguer/",
    "instagram_handle": "@lordiguer",
    "description": (
        "Estudi creatiu i agència de contingut en català. Fotografia, vídeo, "
        "xarxes i web per a turisme rural, productors, cooperatives, restaurants "
        "i comerç de proximitat de Catalunya."
    ),
}

NAV = [
    ("serveis", "Serveis", "/serveis/"),
    ("portfolio", "Portfolio", "/portfolio/"),
    ("comunitat", "Comunitat", "/comunitat/"),
    ("diari", "Diari", "/diari/"),
]

SECTORS = [
    ("Turisme rural", "/turisme-rural/", "Cases rurals, masies i petits hotels."),
    ("Productors i cellers", "/productors/", "Cellers, formatgeries, obradors i finques."),
    ("Cooperatives", "/cooperatives/", "Cooperatives agràries i agrupacions de productors."),
    ("Restaurants", "/restaurants/", "Cuina de territori i de km 0."),
    ("Comerç de proximitat", "/comerc-proximitat/", "Botigues de producte local i obradors."),
]

SERVICES = [
    ("Fotografia", "/fotografia/", "Espais, producte, retrat i reportatge."),
    ("Vídeo", "/video/", "Reportatge, marca i peces per a xarxes."),
    ("Xarxes socials", "/xarxes-socials/", "Estratègia, contingut i publicació."),
    ("Disseny web", "/disseny-web/", "Webs a mida, ràpides i ben posicionades."),
]

# Pàgines de temporada que surten al peu, a la columna de serveis. Treu-les quan acabi la campanya.
SEASONAL = [
    ("Campanya de Nadal", "/campanya-de-nadal/", ""),
]

# Adreces de la web anterior que ara redirigeixen a la pàgina nova.
REDIRECTS = {
    "serveis.html": "/serveis/",
    "portfolio.html": "/portfolio/",
    "comunitat.html": "/comunitat/",
    "contacte.html": "/contacte/",
    "arxiu.html": "/diari/",
    "mapa.html": "/comunitat/",
    "client.html": "/portfolio/",
}

ARROW = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="1.5" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>')

# Icones de línia pròpies (48 × 48). La classe "acc" és l'accent terracota.
ICONS = {
    "fotografia": '<path d="M7 17.5h7.5l3-5.5h13l3 5.5H41a2 2 0 0 1 2 2V37a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V19.5a2 2 0 0 1 2-2z"/><circle cx="24" cy="28" r="7.5"/><circle class="acc" cx="24" cy="28" r="3.5"/><circle class="dot" cx="37" cy="22.5" r="1.3"/>',
    "video": '<rect x="5" y="14" width="29" height="21" rx="2.5"/><path d="M34 21.5l9-5.5v17l-9-5.5z"/><circle class="acc" cx="11" cy="20" r="2.2"/><path d="M11 29.5h17"/>',
    "xarxes-socials": '<rect x="13" y="4.5" width="22" height="39" rx="4"/><path d="M21.5 8.5h5"/><rect class="acc" x="17" y="14" width="6.5" height="6.5"/><rect x="24.5" y="14" width="6.5" height="6.5"/><rect x="17" y="21.5" width="6.5" height="6.5"/><rect x="24.5" y="21.5" width="6.5" height="6.5"/><path d="M17 33h14"/><circle class="dot" cx="24" cy="38.5" r="1.3"/>',
    "disseny-web": '<rect x="4.5" y="9" width="39" height="30" rx="3"/><path d="M4.5 16h39"/><circle class="dot" cx="9" cy="12.5" r="1"/><circle class="dot" cx="12.5" cy="12.5" r="1"/><circle class="dot" cx="16" cy="12.5" r="1"/><rect class="acc" x="9.5" y="20.5" width="14" height="10"/><path d="M28 21.5h10.5M28 25.5h10.5M28 29.5h7M9.5 34.5h29"/>',
    "turisme-rural": '<path d="M5 22.5L24 8l19 14.5"/><path d="M9.5 19.5V40h29V19.5"/><path d="M31.5 13.7V8.5h4.5v8.6"/><path class="acc" d="M20 40v-7.5a4 4 0 0 1 8 0V40z"/><rect x="13.5" y="24" width="5" height="5"/><rect x="29.5" y="24" width="5" height="5"/>',
    "productors": '<path d="M15.5 5.5h4v7.5c2.8 1.6 4 4 4 7v20.5a1.5 1.5 0 0 1-1.5 1.5h-9a1.5 1.5 0 0 1-1.5-1.5V20c0-3 1.2-5.4 4-7z"/><rect class="acc" x="11.5" y="25" width="12" height="8"/><rect x="27" y="22" width="15" height="20" rx="2.5"/><rect x="28" y="17.5" width="13" height="4.5" rx="1"/><path d="M30.5 30h8"/>',
    "cooperatives": '<circle cx="13" cy="17" r="4"/><circle cx="35" cy="17" r="4"/><circle class="acc" cx="24" cy="14.5" r="4.8"/><path d="M5 36v-2.5A7.5 7.5 0 0 1 12.5 26H14a7.5 7.5 0 0 1 4.6 1.6"/><path d="M43 36v-2.5A7.5 7.5 0 0 0 35.5 26H34a7.5 7.5 0 0 0-4.6 1.6"/><path d="M14.5 40v-3.5a9.5 9.5 0 0 1 19 0V40"/>',
    "restaurants": '<circle cx="24" cy="25" r="11.5"/><circle class="acc" cx="24" cy="25" r="5.5"/><path d="M6 9v8.5a3 3 0 0 0 3 3V41M9 9v8M12 9v8.5a3 3 0 0 1-3 3"/><path d="M42 9c-3 2.5-4.5 7-4.5 12H42v20"/>',
    "comerc-proximitat": '<path d="M6.5 18.5L10 10h28l3.5 8.5z"/><path d="M16.5 10l-1.2 8.5M24 10v8.5M31.5 10l1.2 8.5"/><path d="M6.5 18.5a4.375 4.375 0 0 0 8.75 0a4.375 4.375 0 0 0 8.75 0a4.375 4.375 0 0 0 8.75 0a4.375 4.375 0 0 0 8.75 0"/><path d="M9 23v17h30V23"/><rect class="acc" x="13" y="27" width="10" height="7.5"/><path d="M28 40V28h7v12"/>',
    "parlar": '<path d="M8 9h32a3 3 0 0 1 3 3v17a3 3 0 0 1-3 3H21l-8 7v-7H8a3 3 0 0 1-3-3V12a3 3 0 0 1 3-3z"/><circle class="acc" cx="16" cy="20.5" r="2"/><circle class="acc" cx="24" cy="20.5" r="2"/><circle class="acc" cx="32" cy="20.5" r="2"/>',
    "escoltar": '<circle class="acc" cx="11" cy="24" r="3.2"/><path d="M18.5 16.5a10.5 10.5 0 0 1 0 15"/><path d="M25 11a18 18 0 0 1 0 26"/><path d="M31.5 5.5a25.5 25.5 0 0 1 0 37"/>',
    "entendre": '<path d="M4 24c5-8.5 12-13 20-13s15 4.5 20 13c-5 8.5-12 13-20 13S9 32.5 4 24z"/><circle cx="24" cy="24" r="7"/><circle class="acc" cx="24" cy="24" r="3"/>',
    "pin": '<path d="M24 43s-13-12.6-13-23a13 13 0 0 1 26 0c0 10.4-13 23-13 23z"/><circle class="acc" cx="24" cy="20" r="5"/>',
    "temps": '<path d="M14 6h20M14 42h20"/><path d="M16 6c0 10 8 12 8 18s-8 8-8 18M32 6c0 10-8 12-8 18s8 8 8 18"/><path class="acc" d="M19 39c1.5-4 4-6 5-6s3.5 2 5 6z"/><circle class="dot" cx="24" cy="27" r="1"/>',
    "calendari": '<rect x="6" y="9" width="36" height="32" rx="3"/><path d="M6 17h36M15 5v8M33 5v8"/><rect class="acc" x="27" y="27" width="8" height="7"/><path d="M13 24h4M22 24h4M31 24h4M13 31h4M22 31h4"/>',
}
ICON_FOR_HREF = {
    "/fotografia/": "fotografia", "/video/": "video", "/xarxes-socials/": "xarxes-socials",
    "/disseny-web/": "disseny-web", "/turisme-rural/": "turisme-rural", "/productors/": "productors",
    "/cooperatives/": "cooperatives", "/restaurants/": "restaurants", "/comerc-proximitat/": "comerc-proximitat",
}


def icon(name, extra=""):
    return (f'<svg class="icon{extra}" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
            f'{ICONS[name]}</svg>')


def icon_for(href):
    """Icona d’un enllaç de servei o sector (també els de les pàgines locals)."""
    for key, name in ICON_FOR_HREF.items():
        if href == key or (href.startswith("/on-treballem/") and href.endswith(key)):
            return name
    return None


def add_icons(body):
    """Posa la icona que toca a les files de serveis i a les targetes de sector."""
    def svc(m):
        name = icon_for(m.group(2))
        if not name:
            return m.group(0)
        return f'{m.group(1)}<span class="svc__name"><span class="svc__icon">{icon(name)}</span>'
    body = re.sub(r'(<a class="svc__link" href="([^"]+)">)\s*<span class="svc__name">', svc, body)

    def card(m):
        name = icon_for(m.group(2))
        if not name:
            return m.group(0)
        return (f'<a class="link-card link-card--icon" href="{m.group(2)}">'
                f'<span class="link-card__icon">{icon(name)}</span>')
    body = re.sub(r'(<a class="link-card" href="([^"]+)">)', card, body)
    return re.sub(r"\{\{icon:([a-z-]+)\}\}", lambda m: icon(m.group(1)), body)

TODAY = datetime.date.today()
SLOTS = {}  # slot -> {ratio, label, pages, status}


# ---------------------------------------------------------------- utilities

def esc(text):
    return html.escape(str(text), quote=True)


def plain(text):
    """Text sense etiquetes HTML, per a metadades i dades estructurades."""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def asset_version(rel):
    path = ROOT / rel
    if not path.exists():
        return "0"
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def read_source(path):
    """Separa el bloc de metadades (JSON dins d'un comentari) del cos HTML."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*", text, re.S)
    if not m:
        raise SystemExit(f"Falten les metadades a {path}")
    try:
        meta = json.loads(m.group(1))
    except json.JSONDecodeError as err:
        raise SystemExit(f"Metadades mal escrites a {path}: {err}")
    meta["_src"] = path
    return meta, text[m.end():]


def out_path(url_path):
    if url_path.endswith(".html"):
        return ROOT / url_path.lstrip("/")
    return ROOT / url_path.strip("/") / "index.html" if url_path != "/" else ROOT / "index.html"


def lastmod(meta):
    if meta.get("updated"):
        return meta["updated"]
    if meta.get("date"):
        src_date = datetime.date.fromtimestamp(meta["_src"].stat().st_mtime).isoformat()
        return max(meta["date"], src_date)
    return datetime.date.fromtimestamp(meta["_src"].stat().st_mtime).isoformat()


# ---------------------------------------------------------------- image slots

def parse_attrs(raw):
    attrs = {}
    for m in re.finditer(r'([a-z-]+)(?:="([^"]*)")?', raw):
        attrs[m.group(1)] = m.group(2) if m.group(2) is not None else True
    return attrs


def find_media(slot):
    img = None
    for ext in ("webp", "jpg", "jpeg", "png"):
        p = ROOT / "assets" / "img" / f"{slot}.{ext}"
        if p.exists():
            img = f"/assets/img/{slot}.{ext}"
            break
    video = None
    p = ROOT / "assets" / "video" / f"{slot}.mp4"
    if p.exists():
        video = f"/assets/video/{slot}.mp4"
    return img, video


def render_slot(attrs, page_path):
    slot = attrs["slot"]
    ratio = attrs.get("ratio", "4/5")
    alt = attrs.get("alt", "")
    label = attrs.get("label", alt)
    eager = "eager" in attrs
    wants_video = "video" in attrs
    img, video = find_media(slot)

    info = SLOTS.setdefault(slot, {"ratio": ratio, "label": label, "pages": set(),
                                   "video": wants_video})
    info["pages"].add(page_path)

    if wants_video and video:
        info["status"] = "vídeo"
        poster = f' poster="{img}"' if img else ""
        return (f'<video class="fill" autoplay muted loop playsinline preload="metadata"{poster} '
                f'aria-label="{esc(alt)}"><source src="{video}" type="video/mp4"></video>')
    if img:
        info["status"] = "foto"
        try:
            w, h = (float(x) for x in ratio.split("/"))
        except ValueError:
            w, h = 4.0, 5.0
        width = 2000
        height = round(width * h / w)
        loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
        return (f'<img class="fill" src="{img}" alt="{esc(alt)}" width="{width}" height="{height}" '
                f'{loading} decoding="async">')
    info.setdefault("status", "pendent")
    variant = int(hashlib.md5(slot.encode()).hexdigest(), 16) % 4
    return (f'<div class="ph ph--v{variant} fill" role="img" aria-label="{esc(alt)}">'
            f'<span class="ph__label">{esc(label)}</span></div>')


def expand_slots(body, page_path):
    return re.sub(r"<x-img\s+([^>]*)></x-img>",
                  lambda m: render_slot(parse_attrs(m.group(1)), page_path), body)


# ---------------------------------------------------------------- shared blocks

def link_cards(items, current=None, extra_class="", places=False):
    cards = []
    for title, href, text in items:
        if href == current:
            continue
        cards.append(
            f'<li><a class="link-card" href="{href}">'
            f'<span class="link-card__title">{esc(title)} {ARROW}</span>'
            f'<span class="link-card__text">{esc(text)}</span></a></li>')
    if places:
        return '<ul class="link-grid link-grid--places">' + "".join(cards) + "</ul>"
    cols = len(cards)
    return f'<ul class="link-grid link-grid--n{cols} {extra_class}" style="--cols: {cols}">' + "".join(cards) + "</ul>"


def format_date(iso):
    months = ["gener", "febrer", "març", "abril", "maig", "juny", "juliol", "agost",
              "setembre", "octubre", "novembre", "desembre"]
    d = datetime.date.fromisoformat(iso)
    month = months[d.month - 1]
    prep = "d’" if month[0] in "aeiou" else "de "
    return f"{d.day} {prep}{month} de {d.year}"


def reading_minutes(body):
    words = len(plain(body).split())
    return max(1, round(words / 200))


TOPICS = {
    "turisme-rural": "Turisme rural",
    "restaurants": "Restaurants",
    "productors": "Productors",
    "comerc": "Comerç",
    "fotografia": "Fotografia",
    "xarxes": "Xarxes",
    "web": "Web",
    "nadal": "Nadal",
}


def cover_url(a):
    """Portada il·lustrada de l’article, si n’hi ha (assets/covers/<id>.jpg)."""
    p = ROOT / "assets" / "covers" / f"{a['id']}.jpg"
    return f"/assets/covers/{a['id']}.jpg" if p.exists() else None


def cover_html(a, eager=False, cls="fill"):
    url = cover_url(a)
    if url:
        loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
        return (f'<img class="{cls}" src="{url}" alt="" width="1600" height="1000" {loading} decoding="async">')
    extra = " eager" if eager else ""
    return (f'<x-img slot="{a["image"]}" ratio="16/10" alt="{esc(a["image_alt"])}" '
            f'label="{esc(a["image_alt"])}"{extra}></x-img>')


def topics_html(a):
    names = [TOPICS[t] for t in a.get("tags", []) if t in TOPICS]
    if not names:
        return ""
    return '<p class="topics">' + "".join(f"<span>{esc(n)}</span>" for n in names) + "</p>"


def post_meta(a):
    return (f'<p class="post-meta"><span class="post-meta__cat">{esc(a["category"])}</span>'
            f'<span>{a["minutes"]} min de lectura</span></p>')


def post_card(a, heading="h3"):
    tags = " ".join(a.get("tags", []))
    return (f'<article class="post-card" data-tags="{tags}"><a class="post-card__link" href="{a["path"]}">'
            f'<div class="post-card__cover">{cover_html(a)}</div>'
            f'<div class="post-card__body">{post_meta(a)}'
            f'<{heading} class="post-card__title">{esc(a["title"])}</{heading}>'
            f'<p class="post-card__excerpt">{esc(a["description"])}</p>'
            f'{topics_html(a)}</div></a></article>')


def post_grid(articles, cols=3):
    return (f'<div class="post-grid post-grid--{cols}">' + "".join(post_card(a) for a in articles) + "</div>")


def featured_article(articles):
    return next((a for a in articles if a.get("featured")), articles[0])


def diari_index(articles):
    top = featured_article(articles)
    rest = [a for a in articles if a is not top]
    counts = {k: sum(1 for a in rest if k in a.get("tags", [])) for k in TOPICS}
    chips = ['<button class="filter" type="button" data-filter="*" aria-pressed="true">Tot '
             f'<span class="filter__n">{len(rest)}</span></button>']
    for key, label in TOPICS.items():
        if counts[key]:
            chips.append(f'<button class="filter" type="button" data-filter="{key}" aria-pressed="false">'
                         f'{esc(label)} <span class="filter__n">{counts[key]}</span></button>')
    feature = (f'<article class="post-feature">'
               f'<a class="post-feature__cover" href="{top["path"]}" tabindex="-1" aria-hidden="true">{cover_html(top, eager=True)}</a>'
               f'<div class="post-feature__body">{post_meta(top)}'
               f'<h2 class="post-feature__title"><a href="{top["path"]}">{esc(top["title"])}</a></h2>'
               f'<p class="post-feature__excerpt">{esc(top["description"])}</p>{topics_html(top)}'
               f'<a class="text-link" href="{top["path"]}">Llegir la guia {ARROW}</a></div></article>')
    return f"""{feature}
<div class="filters-bar">
  <h2 class="eyebrow" id="tots-els-articles">Tots els articles</h2>
  <div class="filters" role="group" aria-label="Filtra els articles per tema">{''.join(chips)}</div>
</div>
{post_grid(rest)}
<p class="filters__empty" hidden>No hi ha cap article d’aquest tema.</p>"""


def article_cards(articles, limit, with_community):
    cards = [post_card(a) for a in articles[:limit]]
    if with_community:
        cards.append(
            '<article class="post-card"><a class="post-card__link" href="/comunitat/">'
            '<div class="post-card__cover"><x-img slot="comunitat-portada" ratio="16/10" '
            'alt="Un mercat de pagès a primera hora" label="Un mercat de pagès a primera hora"></x-img></div>'
            '<div class="post-card__body"><p class="post-meta"><span class="post-meta__cat">L’Ordiguer Comunitat</span></p>'
            '<h3 class="post-card__title">Mercats, festes, oficis i paisatges, des de dins</h3>'
            f'<p class="post-card__excerpt">El nostre canal editorial sobre el territori. Segueix-nos a Instagram, {SITE["instagram_handle"]}.</p>'
            '</div></a></article>')
    return f'<div class="post-grid post-grid--{len(cards)}">' + "".join(cards) + "</div>"


def article_rows(articles):
    return post_grid(articles)


def expand_parts(body, ctx):
    def part(m):
        attrs = parse_attrs(m.group(1))
        name = attrs["name"]
        if name == "sectors":
            return link_cards(SECTORS, ctx.get("path"))
        if name == "services":
            return link_cards(SERVICES, ctx.get("path"))
        if name == "diari-cards":
            return article_cards(ctx["articles"], int(attrs.get("limit", 2)), "community" in attrs)
        if name == "diari-index":
            return diari_index(ctx["articles"])
        if name == "diari-list":
            arts = ctx["articles"]
            if attrs.get("tag"):
                arts = [a for a in arts if attrs["tag"] in a.get("tags", [])]
            return article_rows(arts)
        if name == "email":
            return SITE["email"]
        if name == "comarca-options":
            return comarca_options()
        path = SRC / "parts" / f"{name}.html"
        if not path.exists():
            raise SystemExit(f"No trobo el bloc {name} ({path})")
        return path.read_text(encoding="utf-8")
    for _ in range(3):  # blocs dins de blocs
        body = re.sub(r"<x-part\s+([^>]*)></x-part>", part, body)
    return body.replace("{{email}}", SITE["email"]).replace("{{arrow}}", ARROW)


# ---------------------------------------------------------------- layout

def header_html(current):
    links = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == current else ""
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    cta_cur = ' aria-current="page"' if current == "contacte" else ""
    mobile = "".join(f'<a href="{href}">{label}</a>' for _, label, href in NAV)
    return f"""<header class="site-header" id="capcalera">
  <a class="logo" href="/" aria-label="L’Ordiguer Estudi, inici">
    <span class="logo__name">L’Ordiguer</span>
    <span class="logo__bar" aria-hidden="true"></span>
    <span class="logo__sub">Estudi</span>
  </a>
  <nav class="nav" aria-label="Principal">
    {''.join(links)}
  </nav>
  <a class="cta-link" href="/contacte/"{cta_cur}>Parlem</a>
  <button class="menu-btn" id="obre-menu" type="button" aria-expanded="false" aria-controls="menu-mobil">
    Menú
    <span class="menu-btn__lines" aria-hidden="true"><span></span><span></span></span>
  </button>
</header>
<div class="menu" id="menu-mobil" hidden>
  <div class="menu__top">
    <span class="logo">
      <span class="logo__name">L’Ordiguer</span>
      <span class="logo__bar" aria-hidden="true"></span>
      <span class="logo__sub">Estudi</span>
    </span>
    <button class="menu__close" id="tanca-menu" type="button">Tanca</button>
  </div>
  <nav class="menu__links" aria-label="Menú mòbil">
    <a href="/">Inici</a>
    {mobile}
    <a href="/qui-som/">Qui som</a>
    <a class="is-cta" href="/contacte/">Parlem</a>
  </nav>
</div>"""


def footer_html():
    def col(title, items):
        lis = "".join(f'<li><a href="{href}">{esc(label)}</a></li>' for label, href, _ in items)
        return f'<div><p class="footer__h">{title}</p><ul>{lis}</ul></div>'
    studio = [("Portfolio", "/portfolio/", ""), ("Comunitat", "/comunitat/", ""),
              ("Diari", "/diari/", ""), ("On treballem", "/on-treballem/", ""),
              ("Qui som", "/qui-som/", ""), ("Contacte", "/contacte/", ""),
              ("Configura el projecte", "/configura/", "")]
    letters = "".join(f'<span aria-hidden="true">{c}</span>' for c in "Parlem")
    return f"""<footer class="site-footer">
  <div class="footer__grid">
    <a class="big-cta" href="/contacte/" aria-label="Parlem?">{letters}<span class="q" aria-hidden="true">?</span></a>
    <div class="footer__contact">
      <p class="footer__lead">Si el teu projecte comparteix aquesta mirada, ens agradarà conèixer-ne la història.</p>
      <div class="email">
        <span class="email__addr" data-email>{SITE['email']}</span>
        <button class="copy" type="button" data-copy>Copia</button>
      </div>
      <p class="footer__small"><a href="{SITE['instagram']}" rel="noopener">Instagram · {SITE['instagram_handle']}</a></p>
    </div>
  </div>
  <nav class="footer__cols" aria-label="Peu de pàgina">
    {col('Sectors', SECTORS)}
    {col('Serveis', SERVICES + SEASONAL)}
    {col('L’Ordiguer', studio)}
  </nav>
  <div class="footer__bar">
    <span>© {TODAY.year} L’Ordiguer Estudi</span>
    <a href="/privacitat/">Avís legal i privacitat</a>
    <span>Fet amb cura al territori català.</span>
  </div>
  <div class="wordmark" aria-hidden="true"><span class="marca-gran">L’Ordiguer</span></div>
</footer>"""


def crumbs_html(crumbs):
    if not crumbs:
        return ""
    items = ['<li><a href="/">Inici</a></li>']
    for label, href in crumbs:
        if href:
            items.append(f'<li><a href="{href}">{esc(label)}</a></li>')
        else:
            items.append(f'<li aria-current="page">{esc(label)}</li>')
    return f'<nav class="crumbs" aria-label="Ruta"><ol>{"".join(items)}</ol></nav>'


def faq_entities(body):
    items = re.findall(r'<details class="faq__item">\s*<summary>(.*?)</summary>\s*<div class="faq__answer">(.*?)</div>\s*</details>', body, re.S)
    return [{"@type": "Question", "name": plain(q),
             "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in items]


def structured_data(meta, url, body):
    base = SITE["base"]
    org_id = base + "/#organitzacio"
    graph = [
        {
            "@type": "Organization",
            "@id": org_id,
            "name": SITE["name"],
            "alternateName": "L’Ordiguer",
            "url": base + "/",
            "logo": {"@type": "ImageObject", "url": base + "/assets/icons/icon-512.png",
                     "width": 512, "height": 512},
            "email": SITE["email"],
            "description": SITE["description"],
            "areaServed": {"@type": "AdministrativeArea", "name": "Catalunya"},
            "knowsLanguage": ["ca", "es"],
            "sameAs": [SITE["instagram"]],
        },
        {
            "@type": "WebSite",
            "@id": base + "/#web",
            "url": base + "/",
            "name": SITE["name"],
            "inLanguage": "ca",
            "publisher": {"@id": org_id},
        },
    ]
    page = {
        "@type": meta.get("page_type", "WebPage"),
        "@id": url + "#pagina",
        "url": url,
        "name": plain(meta["title"]),
        "description": meta["description"],
        "inLanguage": "ca",
        "isPartOf": {"@id": base + "/#web"},
        "about": {"@id": org_id},
    }
    crumbs = meta.get("crumbs")
    if crumbs:
        page["breadcrumb"] = {"@id": url + "#ruta"}
        elements = [{"@type": "ListItem", "position": 1, "name": "Inici", "item": base + "/"}]
        for i, (label, href) in enumerate(crumbs, start=2):
            item = {"@type": "ListItem", "position": i, "name": label}
            item["item"] = base + href if href else url
            elements.append(item)
        graph.append({"@type": "BreadcrumbList", "@id": url + "#ruta", "itemListElement": elements})
    graph.append(page)

    service = meta.get("service")
    if service:
        entry = {
            "@type": "Service",
            "@id": url + "#servei",
            "name": service["name"],
            "serviceType": service.get("type", service["name"]),
            "description": meta["description"],
            "url": url,
            "provider": {"@id": org_id},
            "areaServed": service.get("area", {"@type": "AdministrativeArea", "name": "Catalunya"}),
            "availableLanguage": ["ca", "es"],
        }
        if service.get("audience"):
            entry["audience"] = {"@type": "BusinessAudience", "audienceType": service["audience"]}
        graph.append(entry)

    if meta.get("kind") == "article":
        graph.append({
            "@type": "BlogPosting",
            "@id": url + "#article",
            "headline": meta["title"],
            "description": meta["description"],
            "datePublished": meta["date"],
            "dateModified": lastmod(meta),
            "inLanguage": "ca",
            "articleSection": meta["category"],
            "wordCount": len(plain(body).split()),
            "mainEntityOfPage": {"@id": url + "#pagina"},
            "author": {"@id": org_id},
            "publisher": {"@id": org_id},
            "image": SITE["base"] + (cover_url(meta) or og_image(meta)),
        })

    faqs = faq_entities(body)
    if faqs:
        graph.append({"@type": "FAQPage", "@id": url + "#preguntes", "mainEntity": faqs,
                      "inLanguage": "ca"})

    data = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


def og_image(meta):
    specific = ROOT / "assets" / "og" / f"{meta['id']}.png"
    if specific.exists():
        return f"/assets/og/{meta['id']}.png"
    return "/assets/og/default.png"


def layout(meta, body):
    base = SITE["base"]
    url = base + meta["path"]
    css_v = asset_version("assets/css/site.css")
    js_v = asset_version("assets/js/site.js")
    robots = '<meta name="robots" content="noindex, follow">\n' if meta.get("noindex") else ""
    og_type = "article" if meta.get("kind") == "article" else "website"
    og_title = meta.get("og_title", meta["title"])
    article_meta = ""
    if meta.get("kind") == "article":
        article_meta = (f'<meta property="article:published_time" content="{meta["date"]}">\n'
                        f'<meta property="article:section" content="{esc(meta["category"])}">\n')
    ld = structured_data(meta, url, body)
    body_class = f'page-{meta["id"]}'
    return f"""<!doctype html>
<html lang="ca">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(meta['title'])}</title>
<meta name="description" content="{esc(meta['description'])}">
<meta name="google-site-verification" content="oEAVnYSO-CpscZ7BsTSx1ffOWHXM_ok3HwmSdKp7LBQ">
<link rel="canonical" href="{url}">
{robots}<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="L’Ordiguer Estudi">
<meta property="og:locale" content="ca_ES">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(meta['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}{og_image(meta)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
{article_meta}<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F6F3EE">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/libre-caslon-display-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/source-sans-3-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css?v={css_v}">
<script>(function(d){{if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){{d.classList.add('js-anim');setTimeout(function(){{d.classList.remove('js-anim')}},2500)}}}})(document.documentElement)</script>
<script type="application/ld+json">
{ld}
</script>
</head>
<body class="{body_class}">
<a class="skip" href="#contingut">Salta al contingut</a>
<div class="progress" aria-hidden="true"><span id="progres"></span></div>
{header_html(meta.get('nav'))}
<main id="contingut">
{crumbs_html(meta.get('crumbs'))}
{body}
</main>
{footer_html()}
<div class="cursor-view" id="cursor-veure" aria-hidden="true">Veure</div>
<script src="/assets/vendor/gsap.min.js" defer></script>
<script src="/assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="/assets/vendor/lenis.min.js" defer></script>
<script src="/assets/js/site.js?v={js_v}" defer></script>
</body>
</html>
"""


def slugify(text):
    text = unicodedata.normalize("NFD", plain(text).lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def add_heading_ids(body):
    """Dona un id a cada h2 de l’article i en retorna la llista per a l’índex."""
    toc = []

    def h2(m):
        attrs, text = m.group(1), m.group(2)
        if "id=" in attrs:
            return m.group(0)
        slug = slugify(text)
        toc.append((slug, plain(text)))
        return f'<h2{attrs} id="{slug}">{text}</h2>'
    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", h2, body)
    return body, toc


def related(meta, articles, n=3):
    mine = set(meta.get("tags", []))
    others = [a for a in articles if a["path"] != meta["path"]]
    others.sort(key=lambda a: -len(mine & set(a.get("tags", []))))
    return others[:n]


def article_body(meta, body, articles):
    body, toc = add_heading_ids(body)
    more = ""
    rel = related(meta, articles)
    if rel:
        more = f"""<section class="section" aria-labelledby="mes-diari">
  <div class="section-head">
    <h2 class="eyebrow" id="mes-diari">Per seguir llegint</h2>
    <a class="text-link" href="/diari/">Tot el Diari {ARROW}</a>
  </div>
  {post_grid(rel)}
</section>"""
    toc_html = ""
    if len(toc) > 2:
        items = "".join(f'<li><a href="#{slug}">{esc(text)}</a></li>' for slug, text in toc)
        toc_html = (f'<nav class="toc" aria-label="En aquest article"><p class="toc__h">En aquest article</p>'
                    f'<ol>{items}</ol></nav>')
    return f"""<article class="article">
  <header class="article-head">
    {post_meta(meta).replace('<p class="post-meta">', '<p class="post-meta" data-intro>')}
    <h1 class="article-title" data-split>{meta['title']}</h1>
    <p class="article-lead" data-intro>{meta['description']}</p>
    {topics_html(meta)}
  </header>
  <figure class="article-cover">{cover_html(meta, eager=True)}</figure>
  <div class="article-body">
    <aside class="article-aside">
      <p class="article-date">Publicat el {format_date(meta['date'])}</p>
      {toc_html}
    </aside>
    <div class="prose">
{body}
    </div>
  </div>
</article>
{more}"""


def redirect_stub(target):
    url = SITE["base"] + target
    return f"""<!doctype html>
<html lang="ca">
<head>
<meta charset="utf-8">
<title>L’Ordiguer Estudi</title>
<link rel="canonical" href="{url}">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={target}">
</head>
<body>
<p>Aquesta pàgina s’ha traslladat a <a href="{target}">{url}</a>.</p>
</body>
</html>
"""


# ---------------------------------------------------------------- local pages
# Pàgines «On treballem»: una per comarca (dades a _build/comarques.json) i,
# per a les comarques base, una per servei (textos a _build/serveis-locals.json).

SERVICE_KEYS = ["fotografia", "video", "xarxes-socials", "disseny-web"]
SERVICE_NAMES = {"fotografia": "Fotografia", "video": "Vídeo",
                 "xarxes-socials": "Xarxes socials", "disseny-web": "Disseny web"}
SECTOR_BY_KEY = {href.strip("/"): (title, href) for title, href, _ in SECTORS}
HUB = "/on-treballem/"


def a_place(name):
    """«a» davant d’un nom de lloc: a Berga, al Vendrell, a la Seu d’Urgell."""
    if name.startswith("el "):
        return "al " + name[3:]
    if name.startswith("els "):
        return "als " + name[4:]
    return "a " + name


def de_place(name):
    """«de» davant d’un nom de lloc: de Berga, del Vendrell, d’Igualada."""
    if name.startswith("el "):
        return "del " + name[3:]
    if name.startswith("els "):
        return "dels " + name[4:]
    if unicodedata.normalize("NFD", name[0]).lower()[0] in "aeiou" or name[0] in "Hh":
        return "d’" + name
    return "de " + name


def join_ca(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " i " + items[-1]


def sort_key(name):
    return unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode().lower()


def fit_title(*candidates):
    for title in candidates:
        if len(title) <= 65:
            return title
    return candidates[-1]


def capitals(c):
    return c.get("capitals", [c["capital"]])


def comarca_area(c):
    return {"@type": "AdministrativeArea", "name": c["name"],
            "containedInPlace": {"@type": "AdministrativeArea", "name": "Catalunya"}}


def svc_row(name, desc, href=None):
    head = f'<li class="svc"><span class="svc__rule" aria-hidden="true"></span>'
    inner = f'<span class="svc__name">{esc(name)}</span><span class="svc__desc">{desc}</span>'
    if href:
        return (f'{head}<a class="svc__link" href="{href}">{inner}'
                f'<span class="svc__arrow" aria-hidden="true">{ARROW}</span></a></li>')
    return f'{head}<div class="svc__link">{inner}</div></li>'


def faq_block(items):
    rows = "".join(
        f'\n        <details class="faq__item">\n          <summary>{q}</summary>\n'
        f'          <div class="faq__answer">{a}</div>\n        </details>' for q, a in items)
    return f"""<section class="section" aria-labelledby="preguntes">
  <div class="split">
    <h2 class="eyebrow split__label" id="preguntes">Preguntes freqüents</h2>
    <div class="split__body">
      <div class="faq">{rows}
      </div>
    </div>
  </div>
</section>"""


def towns_block(c, label="Pobles on treballem"):
    towns = "".join(f"<li>{esc(t)}</li>" for t in c["towns"])
    return f"""<section class="section section--tight" aria-labelledby="pobles">
  <div class="split">
    <h2 class="eyebrow split__label" id="pobles">{label}</h2>
    <div class="split__body">
      <ul class="moments moments--places">{towns}</ul>
      <p class="split__intro">I a la resta {c['de']}{esc(c['name'])}.</p>
    </div>
  </div>
</section>"""


def closing_block(c):
    return f"""<section class="closing" aria-labelledby="tancament">
  <p class="eyebrow">{esc(c['name'])}</p>
  <h2 class="closing__title" id="tancament">Tens un projecte {c['a']}<em>{esc(c['name'])}</em>?</h2>
  <a class="btn" href="/contacte/">Parlem {ARROW}</a>
</section>"""


def comarca_page(c, by_slug, local):
    name, slug = c["name"], c["slug"]
    url = f"{HUB}{slug}/"
    caps = capitals(c)
    has_local = slug in local

    if has_local:
        title = fit_title(f"Fotografia, vídeo i xarxes {c['a']}{name} | L’Ordiguer Estudi",
                          f"Fotografia, vídeo i xarxes {c['a']}{name} | L’Ordiguer")
    else:
        cap = " i ".join(caps)
        title = fit_title(f"Fotografia i vídeo {a_place(cap)} i {c['a']}{name} | L’Ordiguer Estudi",
                          f"Fotografia i vídeo {a_place(cap)} i {c['a']}{name} | L’Ordiguer",
                          f"Fotografia, vídeo i xarxes {c['a']}{name} | L’Ordiguer Estudi",
                          f"Fotografia, vídeo i xarxes {c['a']}{name} | L’Ordiguer")
    towns = c["towns"]
    description = ""
    for n in (4, 3, 2):
        description = (f"Fotografia, vídeo, xarxes socials i web per a negocis {c['de']}{name}. "
                       f"Treballem {a_place(towns[0])}, {', '.join(towns[1:n])} i a tota la comarca.")
        if len(description) <= 160:
            break

    meta = {
        "id": f"on-treballem-{slug}", "path": url, "title": title,
        "og_title": f"Fotografia, vídeo i xarxes {c['a']}{name}",
        "description": description,
        "crumbs": [["On treballem", HUB], [name, None]],
        "service": {"name": f"Fotografia, vídeo, xarxes socials i web {c['a']}{name}",
                    "type": "Fotografia, vídeo, xarxes socials i disseny web",
                    "area": comarca_area(c)},
        "priority": 0.6,
        "_src": SRC / "comarques.json",
    }

    cap_label = "Capitals" if len(caps) > 1 else "Capital"
    def dd_list(items):
        return "".join(f"<span>{esc(i)}</span>" for i in items)

    rows = []
    for key in SERVICE_KEYS:
        href = f"{url}{key}/" if has_local else f"/{key}/"
        rows.append(svc_row(SERVICE_NAMES[key], esc(c["focus"][key]), href))

    sectors = [(SECTOR_BY_KEY[k][0], SECTOR_BY_KEY[k][1], note) for k, note in c["sectors"].items()]
    neighbours = sorted((by_slug[n] for n in c["neighbours"]), key=lambda x: sort_key(x["name"]))
    neighbour_cards = [(n["name"], f"{HUB}{n['slug']}/", n["capital"]) for n in neighbours]

    where = join_ca([a_place(x) for x in caps] + [f"a la resta {c['de']}{name}"])
    faq = [[f"Treballeu {esc(where)}?",
            f"Sí. Treballem {a_place(towns[0])}, {esc(join_ca(towns[1:]))}, i ens desplacem a qualsevol punt de la comarca."]]
    faq += c["faq"]

    body = f"""<section class="page-hero">
  <div class="page-hero__text">
    <p class="eyebrow" data-intro>{esc(name)} · {esc(c['capital'])}</p>
    <h1 class="page-title" data-split>Fotografia, vídeo i xarxes {c['a']}<em>{esc(name)}</em>.</h1>
  </div>
  <div class="page-hero__side">
    <p data-intro>{esc(c['lead'])}</p>
    <a class="btn" href="/contacte/" data-intro>Parlem del teu projecte {ARROW}</a>
  </div>
</section>

<section class="section manifest" aria-labelledby="territori">
  <h2 class="eyebrow manifest__label" id="territori">El territori</h2>
  <p class="manifest__text manifest__text--sm" data-ink>{c['territory']}</p>
</section>

<section class="section section--tight" aria-label="La comarca">
  <dl class="facts facts--list">
    <div><dt>{cap_label}</dt><dd>{dd_list(caps)}</dd></div>
    <div><dt>Paisatge i patrimoni</dt><dd>{dd_list(c['landscape'])}</dd></div>
    <div><dt>Producte</dt><dd>{dd_list(c['products'])}</dd></div>
  </dl>
</section>

<section class="section section--tight" aria-labelledby="que-fem">
  <div class="section-head">
    <h2 class="eyebrow" id="que-fem">Què fem {c['a']}{esc(name)}</h2>
    <p class="section-head__note">{esc(c['character'])}.</p>
  </div>
  <ul class="svc-list svc-list--sm">{''.join(rows)}</ul>
</section>

{towns_block(c)}

<section class="section section--tight" aria-labelledby="per-a-qui">
  <div class="section-head">
    <h2 class="eyebrow" id="per-a-qui">Per a qui</h2>
    <a class="text-link" href="/serveis/">Tots els serveis {ARROW}</a>
  </div>
  {link_cards(sectors)}
</section>

{faq_block(faq)}

<section class="section section--tight" aria-labelledby="veines">
  <div class="section-head">
    <h2 class="eyebrow" id="veines">Comarques veïnes</h2>
    <a class="text-link" href="{HUB}">Totes les comarques {ARROW}</a>
  </div>
  {link_cards(neighbour_cards, places=True)}
</section>

{closing_block(c)}"""
    return meta, body


def local_service_page(c, key, texts, services, by_slug):
    name, slug = c["name"], c["slug"]
    svc = services[key]
    url = f"{HUB}{slug}/{key}/"
    caps = capitals(c)

    meta = {
        "id": f"on-treballem-{slug}-{key}", "path": url, "title": texts["title"],
        "og_title": plain(texts["h1"]).rstrip("."),
        "description": texts["description"],
        "crumbs": [["On treballem", HUB], [name, f"{HUB}{slug}/"], [svc["name"], None]],
        "service": {"name": plain(texts["h1"]).rstrip("."), "type": svc["type"],
                    "area": [{"@type": "City", "name": x} for x in caps] + [comarca_area(c)]},
        "priority": 0.6,
        "_src": SRC / "serveis-locals.json",
    }

    items = "".join(svc_row(n, esc(d)) for n, d in svc["items"])
    others = [(SERVICE_NAMES[k], f"{HUB}{slug}/{k}/", c["focus"][k]) for k in SERVICE_KEYS if k != key]

    out_caps = " i ".join(de_place(x) for x in caps)
    rest = [t for t in c["towns"] if t not in caps]
    near = join_ca(by_slug[n]["el"] + by_slug[n]["name"] for n in c["neighbours"])
    faq = list(texts["faq"]) + [[
        f"Treballeu fora {out_caps}?",
        f"Sí. Treballem {a_place(rest[0])}, {esc(join_ca(rest[1:]))}, i també a les comarques veïnes: {esc(near)}."]]

    body = f"""<section class="page-hero">
  <div class="page-hero__text">
    <p class="eyebrow" data-intro>{esc(svc['name'])} · {esc(name)}</p>
    <h1 class="page-title" data-split>{texts['h1']}</h1>
  </div>
  <div class="page-hero__side">
    <p data-intro>{esc(texts['lead'])}</p>
    <a class="btn" href="/contacte/" data-intro>Demana pressupost {ARROW}</a>
  </div>
</section>

<section class="section manifest" aria-labelledby="context">
  <h2 class="eyebrow manifest__label" id="context">{esc(name)}</h2>
  <p class="manifest__text manifest__text--sm" data-ink>{texts['statement']}</p>
</section>

<section class="section section--tight" aria-labelledby="que-inclou">
  <div class="section-head">
    <h2 class="eyebrow" id="que-inclou">Què inclou</h2>
    <a class="text-link" href="{svc['general']}">Més sobre {esc(svc['name'].lower())} {ARROW}</a>
  </div>
  <ul class="svc-list svc-list--sm svc-list--static">{items}</ul>
</section>

{towns_block(c, "On treballem")}

{faq_block(faq)}

<section class="section section--tight" aria-labelledby="altres-serveis">
  <div class="section-head">
    <h2 class="eyebrow" id="altres-serveis">Altres serveis {c['a']}{esc(name)}</h2>
    <a class="text-link" href="{HUB}{slug}/">{esc(name)}, tots els serveis {ARROW}</a>
  </div>
  {link_cards(others)}
</section>

{closing_block(c)}"""
    return meta, body


def hub_page(comarques):
    def rows(group):
        items = sorted((c for c in comarques if c["group"] == group), key=lambda c: sort_key(c["name"]))
        return "".join(
            f'<li><a class="place-row" href="{HUB}{c["slug"]}/">'
            f'<span class="place-row__name">{esc(c["name"])}</span>'
            f'<span class="place-row__capital">{esc(c["capital"])}</span>'
            f'<span class="place-row__text">{esc(c["character"])}</span>'
            f'<span class="place-row__arrow" aria-hidden="true">{ARROW}</span></a></li>'
            for c in items), len(items)

    bcn, n_bcn = rows("barcelona")
    near, n_near = rows("veines")
    meta = {
        "id": "on-treballem", "path": HUB, "page_type": "CollectionPage",
        "title": "On treballem: comarques de Catalunya | L’Ordiguer Estudi",
        "og_title": "On treballem, comarca a comarca",
        "description": ("Fotografia, vídeo, xarxes socials i web per a negocis de la província de "
                        "Barcelona i de les comarques veïnes. Tria la teva comarca."),
        "crumbs": [["On treballem", None]],
        "priority": 0.6,
        "_src": SRC / "comarques.json",
    }
    body = f"""<section class="page-hero">
  <div class="page-hero__text">
    <p class="eyebrow" data-intro>Comarca a comarca</p>
    <h1 class="page-title" data-split>On <em>treballem</em>.</h1>
  </div>
  <div class="page-hero__side">
    <p data-intro>Treballem a tota Catalunya, i sobretot a la província de Barcelona i a les comarques veïnes. Cada comarca té el seu paisatge, el seu producte i el seu ritme.</p>
  </div>
</section>

<section class="section section--tight" aria-labelledby="provincia">
  <div class="section-head">
    <h2 class="eyebrow" id="provincia">Província de Barcelona</h2>
    <p class="section-head__note">{n_bcn} comarques</p>
  </div>
  <ul class="place-list">{bcn}</ul>
</section>

<section class="section section--tight" aria-labelledby="comarques-veines">
  <div class="section-head">
    <h2 class="eyebrow" id="comarques-veines">Comarques veïnes</h2>
    <p class="section-head__note">{n_near} comarques</p>
  </div>
  <ul class="place-list">{near}</ul>
</section>

<section class="closing" aria-labelledby="tancament">
  <p class="eyebrow">A tota Catalunya</p>
  <h2 class="closing__title" id="tancament">La teva comarca no <em>hi és</em>?</h2>
  <p class="lead">Ens desplacem a qualsevol punt de Catalunya. Explica’ns el projecte.</p>
  <a class="btn" href="/contacte/">Parlem {ARROW}</a>
</section>"""
    return meta, body


def comarca_options():
    """Opcions del desplegable de comarques del configurador."""
    comarques = json.loads((SRC / "comarques.json").read_text(encoding="utf-8"))
    groups = []
    for group, label in (("barcelona", "Província de Barcelona"), ("veines", "Comarques veïnes")):
        items = sorted((c for c in comarques if c["group"] == group), key=lambda c: sort_key(c["name"]))
        opts = "".join(f'<option value="{esc(c["name"])}" data-slug="{c["slug"]}">{esc(c["name"])}</option>'
                       for c in items)
        groups.append(f'<optgroup label="{label}">{opts}</optgroup>')
    groups.append('<optgroup label="Altres"><option>Una altra comarca de Catalunya</option>'
                  '<option>Fora de Catalunya</option></optgroup>')
    return "".join(groups)


def local_pages():
    path = SRC / "comarques.json"
    if not path.exists():
        return []
    comarques = json.loads(path.read_text(encoding="utf-8"))
    local = json.loads((SRC / "serveis-locals.json").read_text(encoding="utf-8"))
    services = local.pop("_serveis")
    by_slug = {c["slug"]: c for c in comarques}
    pages = [hub_page(comarques)]
    for c in comarques:
        pages.append(comarca_page(c, by_slug, local))
        for key in SERVICE_KEYS:
            if c["slug"] in local and key in local[c["slug"]]:
                pages.append(local_service_page(c, key, local[c["slug"]][key], services, by_slug))
    return pages


# ---------------------------------------------------------------- build

def build():
    written = []

    articles = []
    for path in sorted((SRC / "diari").glob("*.html")):
        meta, body = read_source(path)
        meta["kind"] = "article"
        meta["minutes"] = reading_minutes(body)
        articles.append((meta, body))
    articles.sort(key=lambda mb: mb[0]["date"], reverse=True)
    article_index = [m for m, _ in articles]

    pages = [read_source(p) for p in sorted((SRC / "pages").glob("*.html"))]
    pages += local_pages()
    sitemap = []

    for meta, body in pages:
        ctx = {"path": meta["path"], "articles": article_index}
        html_body = add_icons(expand_parts(body, ctx))
        html_body = expand_slots(html_body, meta["path"])
        doc = layout(meta, html_body)
        target = out_path(meta["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc, encoding="utf-8")
        written.append(target)
        if not meta.get("noindex"):
            sitemap.append((meta["path"], lastmod(meta), meta.get("priority", 0.6)))

    for meta, body in articles:
        meta.setdefault("nav", "diari")
        meta.setdefault("crumbs", [["Diari", "/diari/"], [meta["title"], None]])
        ctx = {"path": meta["path"], "articles": article_index}
        inner = add_icons(expand_parts(body, ctx))
        html_body = add_icons(article_body(meta, inner, article_index))
        html_body = expand_slots(html_body, meta["path"])
        doc = layout(meta, html_body)
        target = out_path(meta["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc, encoding="utf-8")
        written.append(target)
        sitemap.append((meta["path"], lastmod(meta), 0.5))

    for old, new in REDIRECTS.items():
        (ROOT / old).write_text(redirect_stub(new), encoding="utf-8")

    urls = "\n".join(
        f"  <url><loc>{SITE['base']}{path}</loc><lastmod>{mod}</lastmod>"
        f"<priority>{prio}</priority></url>"
        for path, mod, prio in sorted(sitemap, key=lambda s: (-s[2], s[0])))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n", encoding="utf-8")

    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['base']}/sitemap.xml\n", encoding="utf-8")

    lines = ["# Fotos i vídeos de la web", "",
             "Generat automàticament per `_build/build.py`. No l’editis a mà.", "",
             "Desa cada foto a `assets/img/<nom>.jpg` (2000 px d’ample, qualitat 80) i cada vídeo a",
             "`assets/video/<nom>.mp4`. Després torna a executar `python3 _build/build.py`.", "",
             "| Nom | Proporció | Què hi va | On surt | Estat |", "|---|---|---|---|---|"]
    for slot in sorted(SLOTS):
        info = SLOTS[slot]
        kind = " (accepta vídeo)" if info.get("video") else ""
        pages_list = ", ".join(sorted(info["pages"]))
        lines.append(f"| `{slot}`{kind} | {info['ratio']} | {info['label']} | {pages_list} | {info.get('status', 'pendent')} |")
    (SRC / "FOTOS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    pending = sum(1 for s in SLOTS.values() if s.get("status", "pendent") == "pendent")
    print(f"Fet: {len(written)} pàgines, {len(REDIRECTS)} redireccions, "
          f"{len(sitemap)} adreces al sitemap, {pending} fotos pendents (vegeu _build/FOTOS.md).")


if __name__ == "__main__":
    build()
