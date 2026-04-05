/* =========================================
   L'ORDIGUER ESTUDI — JavaScript principal
   ========================================= */

/* --- Navegació: hamburguesa mòbil --- */
document.addEventListener('DOMContentLoaded', () => {
  const hamburguesa = document.querySelector('.nav__hamburguesa');
  const links = document.querySelector('.nav__links');

  if (hamburguesa && links) {
    hamburguesa.addEventListener('click', () => {
      hamburguesa.classList.toggle('obert');
      links.classList.toggle('obert');
      // Bloqueja el scroll quan el menú és obert
      document.body.style.overflow = links.classList.contains('obert') ? 'hidden' : '';
    });

    // Tanca el menú quan es clica un link
    links.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburguesa.classList.remove('obert');
        links.classList.remove('obert');
        document.body.style.overflow = '';
      });
    });
  }

  /* --- Marca el link actiu a la nav --- */
  const paginaActual = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav__links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === paginaActual || (paginaActual === '' && href === 'index.html')) {
      link.classList.add('actiu');
    }
  });

  /* --- Inicialitza els mòduls segons la pàgina --- */
  if (document.getElementById('agenda-container')) {
    carregaEsdeveniments();
  }

  if (document.getElementById('mapa')) {
    inicialitzaMapa();
  }

  if (document.getElementById('portfolio-grid')) {
    inicialitzaFiltresPortfolio();
  }

  if (document.getElementById('formulari-contacte')) {
    inicialitzaFormulari();
  }

  if (document.getElementById('client-loading')) {
    carregaClientPage();
  }

  if (document.getElementById('arxiu-grid')) {
    inicialitzaArxiu();
  }

  if (document.getElementById('formulari-newsletter')) {
    inicialitzaNewsletter();
  }

  // Animacions de scroll — sempre actiu a totes les pàgines
  inicialitzaAnimacions();
});

/* =========================================
   DADES INCRUSTADES (evita fetch() amb file://)
   ========================================= */

const DADES_ESDEVENIMENTS = [
  {
    "id": 1,
    "nom": "Mercat de Pagès de Vic",
    "data": "2026-04-04",
    "lloc": "Plaça Major, Vic",
    "comarca": "Osona",
    "descripcio": "El mercat setmanal més antic de Catalunya. Productors locals de l'Osona ofereixen verdures, embotits, formatges artesans i flors de temporada. Un ritual que no ha canviat en segles.",
    "categoria": "mercat"
  },
  {
    "id": 2,
    "nom": "Fira de Sant Isidre de Mollerussa",
    "data": "2026-05-15",
    "lloc": "Recinte Firal, Mollerussa",
    "comarca": "Pla d'Urgell",
    "descripcio": "La gran fira agrícola i ramadera del ple de les terres de ponent. Maquinària, bestiar, productes de l'horta i concursos de races autòctones. El batec del pagès català.",
    "categoria": "fira"
  },
  {
    "id": 3,
    "nom": "Patum de Berga",
    "data": "2026-05-28",
    "lloc": "Plaça de Sant Pere, Berga",
    "comarca": "Berguedà",
    "descripcio": "Festa declarada Patrimoni Immaterial de la Humanitat per la UNESCO. Foc, música i figures ancestrals que surten al carrer des del segle XIV. Una experiència única al món.",
    "categoria": "festa"
  },
  {
    "id": 4,
    "nom": "Festival Temps de Flors de Girona",
    "data": "2026-05-09",
    "lloc": "Barri Vell, Girona",
    "comarca": "Gironès",
    "descripcio": "Durant una setmana, el barri vell de Girona es transforma en una instal·lació floral gegant. Patis, esglésies, escales i racons medievals coberts de flors de temporada. Art efímer i territori.",
    "categoria": "cultura"
  },
  {
    "id": 5,
    "nom": "Mercat Medieval de Montblanc",
    "data": "2026-04-23",
    "lloc": "Muralla Medieval, Montblanc",
    "comarca": "Conca de Barberà",
    "descripcio": "La vila de Montblanc reviu l'edat mitjana durant la Setmana Medieval. Artesans, cavallers, músics i mercat de productes tradicionals dins les millors muralles medievals de Catalunya.",
    "categoria": "mercat"
  }
];

const DADES_LLOCS = [
  {
    "id": 1,
    "nom": "Can Bonastre Wine Resort",
    "categoria": "allotjament",
    "lat": 41.5247,
    "lng": 1.8312,
    "comarca": "Anoia",
    "descripcio": "Masia del segle XVIII envoltada de vinyes al cor del Penedès. Allotjament de luxe discret amb celler propi, piscina entre ceps i cuina de territori.",
    "client": true
  },
  {
    "id": 2,
    "nom": "Restaurant Les Cols",
    "categoria": "restaurant",
    "lat": 42.1724,
    "lng": 2.4884,
    "comarca": "Garrotxa",
    "descripcio": "Cuina volcànica d'avantguarda de Fina Puigdevall. Dues estrelles Michelin al cor de la Garrotxa. El producte local com a filosofia de vida.",
    "client": false
  },
  {
    "id": 3,
    "nom": "Formatgeria La Bauma",
    "categoria": "productor",
    "lat": 41.9583,
    "lng": 2.1421,
    "comarca": "Osona",
    "descripcio": "Formatges artesans elaborats amb llet crua de vaques de raça bruna dels Pirineus. Producció familiar a la plana de Vic. Madurats en cava de pedra.",
    "client": true
  },
  {
    "id": 4,
    "nom": "Casa Amatller",
    "categoria": "espai_cultural",
    "lat": 41.3919,
    "lng": 2.1650,
    "comarca": "Barcelonès",
    "descripcio": "Obra mestre del modernisme català de Puig i Cadafalch al passeig de Gràcia. Museu, xocolateria artesana i espai d'exposicions. El gust modernista en estat pur.",
    "client": false
  },
  {
    "id": 5,
    "nom": "Mercat del Lleó de Girona",
    "categoria": "mercat",
    "lat": 41.9832,
    "lng": 2.8235,
    "comarca": "Gironès",
    "descripcio": "El mercat municipal de Girona és un dels millors de Catalunya. Peix fresc de l'Empordà, verdures de l'Horta, embotits de la Garrotxa i formatges de les comarques gironines.",
    "client": false
  },
  {
    "id": 6,
    "nom": "Hotel El Cingle",
    "categoria": "allotjament",
    "lat": 41.8341,
    "lng": 2.0123,
    "comarca": "Moianès",
    "descripcio": "Petit hotel rural de 8 habitacions enclavat al Moianès. Vista a la plana de Vic, cuina de proximitat i silenci absolut. Per a qui vol desconnectar de veritat.",
    "client": true
  },
  {
    "id": 7,
    "nom": "Oli Núria — Cooperativa Siurana",
    "categoria": "productor",
    "lat": 41.2284,
    "lng": 0.9312,
    "comarca": "Priorat",
    "descripcio": "Cooperativa centenària de la DOP Siurana al Priorat. Producció d'oli verge extra de varietats arbequina i royal. Visites a l'oliverar i tast guiat.",
    "client": false
  },
  {
    "id": 8,
    "nom": "Centre d'Art i Natura de Farrera",
    "categoria": "espai_cultural",
    "lat": 42.4102,
    "lng": 1.1924,
    "comarca": "Pallars Sobirà",
    "descripcio": "Residència d'artistes en un poble recuperat del Pallars Sobirà. Exposicions d'art contemporani, tallers i residències creatives al mig del Pirineu. On l'art i el territori es troben.",
    "client": true
  }
];

/* =========================================
   AGENDA D'ESDEVENIMENTS (comunitat.html)
   ========================================= */

function carregaEsdeveniments() {
  const contenidor = document.getElementById('agenda-container');
  if (!contenidor) return;

  const esdeveniments = DADES_ESDEVENIMENTS;

  // Ordena per data
  esdeveniments.sort((a, b) => new Date(a.data) - new Date(b.data));

  contenidor.innerHTML = '';

  esdeveniments.forEach(event => {
    const data = new Date(event.data + 'T12:00:00');
    const dia = data.getDate().toString().padStart(2, '0');
    const mes = data.toLocaleDateString('ca-ES', { month: 'short' }).toUpperCase();

    const card = document.createElement('article');
    card.classList.add('event-card');
    card.innerHTML = `
      <div class="event-card__data">
        <div class="event-card__dia">${dia}</div>
        <div class="event-card__mes">${mes}</div>
      </div>
      <div class="event-card__info">
        <h3>${event.nom}</h3>
        <div class="event-card__lloc">
          <span>${event.lloc}</span>
          <span>·</span>
          <span>${event.comarca}</span>
        </div>
        <p>${event.descripcio}</p>
      </div>
      <div class="event-card__badge-wrap">
        <span class="event-card__badge badge--${event.categoria}">${event.categoria}</span>
      </div>
    `;
    contenidor.appendChild(card);
  });
}

/* =========================================
   MAPA INTERACTIU (mapa.html)
   Leaflet.js + data/llocs.json
   ========================================= */

function inicialitzaMapa() {
  // Icones per categoria (colors diferenciats)
  const iconesCategoria = {
    restaurant:     { color: '#c87a6a', etiqueta: 'Restaurant' },
    allotjament:    { color: '#8aad7a', etiqueta: 'Allotjament' },
    productor:      { color: '#c8a45a', etiqueta: 'Productor' },
    espai_cultural: { color: '#7a8aad', etiqueta: 'Espai Cultural' },
    mercat:         { color: '#ad8a7a', etiqueta: 'Mercat' },
  };

  // Crea icona personalitzada amb SVG
  function creaIcona(categoria) {
    const config = iconesCategoria[categoria] || { color: '#8b6f47' };
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36">
      <path d="M14 0C6.268 0 0 6.268 0 14c0 9.333 14 22 14 22S28 23.333 28 14C28 6.268 21.732 0 14 0z" fill="${config.color}"/>
      <circle cx="14" cy="14" r="5" fill="white" opacity="0.9"/>
    </svg>`;
    return L.divIcon({
      html: svg,
      iconSize: [28, 36],
      iconAnchor: [14, 36],
      popupAnchor: [0, -36],
      className: ''
    });
  }

  // Centra a Catalunya
  const mapa = L.map('mapa', {
    center: [41.7, 1.5],
    zoom: 8,
    zoomControl: true
  });

  // Tiles neutres i elegants (OpenStreetMap)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
    maxZoom: 18
  }).addTo(mapa);

  const llocs = DADES_LLOCS;
  const marcadors = {};

  // Crea tots els marcadors
  llocs.forEach(lloc => {
      const config = iconesCategoria[lloc.categoria] || { color: '#8b6f47', etiqueta: lloc.categoria };
      const badgeText = lloc.client ? 'Treballem junts' : 'Recomanat per L\'Ordiguer';
      const badgeClass = lloc.client ? 'popup-badge--client' : 'popup-badge--editorial';

      const popupContingut = `
        <div style="min-width:220px; padding: 0.5rem;">
          <div class="popup-nom">${lloc.nom}</div>
          <div class="popup-comarca">${config.etiqueta} · ${lloc.comarca}</div>
          <div class="popup-desc">${lloc.descripcio}</div>
          <span class="popup-badge ${badgeClass}">${badgeText}</span>
        </div>
      `;

      const marcador = L.marker([lloc.lat, lloc.lng], {
        icon: creaIcona(lloc.categoria)
      })
        .addTo(mapa)
        .bindPopup(popupContingut, { maxWidth: 300 });

      if (!marcadors[lloc.categoria]) marcadors[lloc.categoria] = [];
      marcadors[lloc.categoria].push({ marcador, dades: lloc });
    });

  // Filtre per categories
  document.querySelectorAll('.filtre-mapa').forEach(boto => {
    boto.addEventListener('click', () => {
      document.querySelectorAll('.filtre-mapa').forEach(b => b.classList.remove('actiu'));
      boto.classList.add('actiu');

      const categoria = boto.dataset.categoria;

      // Mostra/amaga marcadors per categoria
      Object.entries(marcadors).forEach(([cat, items]) => {
        items.forEach(({ marcador }) => {
          if (categoria === 'tots' || cat === categoria) {
            if (!mapa.hasLayer(marcador)) mapa.addLayer(marcador);
          } else {
            if (mapa.hasLayer(marcador)) mapa.removeLayer(marcador);
          }
        });
      });
    });
  });
}

/* =========================================
   FILTRES PORTFOLIO (portfolio.html)
   ========================================= */

function inicialitzaFiltresPortfolio() {
  const botons = document.querySelectorAll('.filtre-boto');
  const items = document.querySelectorAll('.portfolio-item[data-categoria]');

  botons.forEach(boto => {
    boto.addEventListener('click', () => {
      botons.forEach(b => b.classList.remove('actiu'));
      boto.classList.add('actiu');

      const categoria = boto.dataset.filtre;

      items.forEach(item => {
        const mostrar = categoria === 'tot' || item.dataset.categoria === categoria;
        item.style.display = mostrar ? '' : 'none';

        // Animació suau
        if (mostrar) {
          item.style.opacity = '0';
          requestAnimationFrame(() => {
            item.style.transition = 'opacity 0.3s ease';
            item.style.opacity = '1';
          });
        }
      });
    });
  });
}

/* =========================================
   FORMULARI DE CONTACTE (contacte.html)
   ========================================= */

function inicialitzaFormulari() {
  const formulari = document.getElementById('formulari-contacte');
  const missatgeExit = document.getElementById('missatge-exit');

  formulari.addEventListener('submit', (e) => {
    e.preventDefault();

    // Validació bàsica
    const nom = formulari.nom.value.trim();
    const missatge = formulari.missatge.value.trim();

    if (!nom || !missatge) {
      alert('Si us plau, omple els camps obligatoris.');
      return;
    }

    // Simula enviament (en producció, aquí aniria la crida a l'API)
    const boto = formulari.querySelector('button[type="submit"]');
    boto.textContent = 'Enviant...';
    boto.disabled = true;

    setTimeout(() => {
      formulari.reset();
      boto.textContent = 'Enviar missatge';
      boto.disabled = false;

      if (missatgeExit) {
        missatgeExit.style.display = 'block';
        setTimeout(() => { missatgeExit.style.display = 'none'; }, 5000);
      }
    }, 1200);
  });
}

/* =========================================
   ANIMACIÓ D'ENTRADA (IntersectionObserver)
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
  // Afegeix classe per animar elements quan entren a la vista
  const observat = document.querySelectorAll('.seccio, .servei-bloc, .portfolio-item, .pilar, .event-card');

  if ('IntersectionObserver' in window && observat.length) {
    const observer = new IntersectionObserver((entrades) => {
      entrades.forEach(entrada => {
        if (entrada.isIntersecting) {
          entrada.target.style.opacity = '1';
          entrada.target.style.transform = 'translateY(0)';
          observer.unobserve(entrada.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    observat.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      observer.observe(el);
    });
  }
});
