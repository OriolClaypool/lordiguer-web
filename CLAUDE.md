# lordiguer.cat

Web de L’Ordiguer Estudi, publicada amb GitHub Pages des de la branca `main`.

## Com funciona

La web es genera amb `python3 _build/build.py` (només Python, sense dependències).

- **No editis els `.html` de l’arrel ni de les carpetes de pàgina**: es tornen a escriure cada vegada que s’executa el generador.
- Textos de cada pàgina: `_build/pages/<pàgina>.html`. El bloc de dalt (entre `<!--` i `-->`) són les dades SEO: títol, descripció, adreça.
- Articles del Diari: `_build/diari/<article>.html`. Per fer-ne un de nou, copia’n un i canvia’n les dades.
- Blocs compartits (per exemple, «Com treballem»): `_build/parts/`.
- Pàgines «On treballem» (una per comarca): dades a `_build/comarques.json`. Les pàgines per servei de les comarques base (Berguedà, Osona, Vallès Occidental i Barcelonès): textos a `_build/serveis-locals.json`. L’estructura de totes dues és a `build.py` (funcions `comarca_page`, `local_service_page` i `hub_page`).
- Capçalera, peu, menú i dades de contacte: `_build/build.py` (constants `SITE`, `NAV`, `SECTORS`, `SERVICES`).
- Icones: dibuixades a mà a `build.py` (constant `ICONS`). Les dels serveis i sectors es posen soles; en qualsevol pàgina es poden inserir amb `{{icon:nom}}`.
- Diari: cada article porta `tags` (temes del filtre, vegeu `TOPICS` a `build.py`) i, si cal, `"featured": true` per sortir destacat a dalt.
- Portades del Diari: il·lustracions generades amb `_build/portades.py` (cal Playwright). La imatge final és `assets/covers/<article>.jpg`; si no n’hi ha, l’article fa servir la foto del bloc `image`.
- Infografies dins dels articles i de les pàgines de servei: components `.fig` d’`assets/css/site.css` (comparació, formats, mesos, calendari, camí en passos, dia i sol, temes, esquema amb números, una jornada i diverses peces). Copia’n un d’un article i canvia’n els textos.
- Estils: `assets/css/site.css`. Animacions i formulari: `assets/js/site.js`.

## Fotos i vídeos

La llista de fotos pendents és a `_build/FOTOS.md`. Cada foto va a `assets/img/<nom>.jpg`
(2000 px d’ample, qualitat 80) i cada vídeo a `assets/video/<nom>.mp4`. Després, torna a executar el generador.

## Previsualitzar abans de pujar

```
python3 _build/build.py
python3 -m http.server 8000
```

i obre http://localhost:8000

## Normes del projecte

- Canvia només el que s’ha demanat explícitament. Res més: ni textos, ni colors, ni tipografies, ni estructura.
- Colors: paper `#F6F3EE`, sorra `#E7DFD6`, tinta `#1C1C1A`, terracota `#C46A4A`, sàlvia `#7A8A78`. El blau `#2F4A5C` no es fa servir com a fons.
- Tipografies: Libre Caslon (títols) i Source Sans 3 (text). Són a `assets/fonts`, no a Google Fonts.
- Sense cursives. La paraula destacada d’un títol (`<em>`) va en terracota i dreta, mai en cursiva.
- Les animacions han de ser variades, no totes iguals.
- El `git push` el fa l’Oriol manualment, després de revisar la web en local.
- Tots els textos en català, amb el to de la guia de marca: proper, evocador, sense superlatius.
