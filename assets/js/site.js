/* L'Ordiguer Estudi — interacció i animacions de la web.
   Tot el contingut es veu igualment sense aquest fitxer; aquí només hi ha
   el menú mòbil, el formulari, el botó de copiar i les animacions (GSAP + Lenis). */
(function () {
  'use strict';
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function reveal() { root.classList.remove('js-anim'); }

  /* ---------- Paper grain, generated once ---------- */
  try {
    var c = document.createElement('canvas');
    c.width = c.height = 160;
    var ctx = c.getContext('2d');
    var img = ctx.createImageData(160, 160);
    for (var i = 0; i < img.data.length; i += 4) {
      var v = (Math.random() * 255) | 0;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    root.style.setProperty('--grain', 'url(' + c.toDataURL() + ')');
  } catch (e) {}

  /* ---------- Copy e-mail buttons ---------- */
  $$('[data-copy]').forEach(function (btn) {
    var box = btn.parentElement;
    var addr = box && box.querySelector('[data-email]');
    if (!addr) return;
    btn.addEventListener('click', function () {
      var text = addr.textContent.trim();
      function selectText() {
        var range = document.createRange();
        range.selectNodeContents(addr);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        btn.textContent = 'Seleccionat';
      }
      function done() {
        btn.textContent = 'Copiat';
        setTimeout(function () { btn.textContent = 'Copia'; }, 2200);
      }
      try {
        navigator.clipboard.writeText(text).then(done, selectText);
      } catch (e) { selectText(); }
    });
  });

  /* ---------- Mobile menu ---------- */
  var menu = $('#menu-mobil');
  var openBtn = $('#obre-menu');
  var closeBtn = $('#tanca-menu');
  if (menu && openBtn && closeBtn) {
    var setMenu = function (open) {
      menu.hidden = !open;
      openBtn.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
      if (window.__lenis) { open ? window.__lenis.stop() : window.__lenis.start(); }
      (open ? closeBtn : openBtn).focus();
    };
    openBtn.addEventListener('click', function () { setMenu(true); });
    closeBtn.addEventListener('click', function () { setMenu(false); });
    menu.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
    $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  }

  /* ---------- Header hide/show + reading progress ---------- */
  var header = $('#capcalera');
  var bar = $('#progres');
  var lastY = window.scrollY;
  function onScroll() {
    var y = window.scrollY;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
    if (header) {
      if (y > lastY + 4 && y > 240) header.classList.add('is-hidden');
      else if (y < lastY - 4 || y < 240) header.classList.remove('is-hidden');
    }
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (header) header.addEventListener('focusin', function () { header.classList.remove('is-hidden'); });

  /* ---------- Contact form (sent through FormSubmit) ---------- */
  var form = $('#formulari-contacte');
  if (form) {
    var status = $('#estat-formulari');
    var submit = $('button[type="submit"]', form);
    var endpoint = form.getAttribute('data-endpoint');
    var setStatus = function (text, kind) {
      status.textContent = text;
      status.className = 'form__status' + (kind ? ' is-' + kind : '');
    };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var fd = new FormData(form);
      if (fd.get('_honey')) return;
      var data = {};
      fd.forEach(function (value, key) {
        if (key === 'serveis') return;
        data[key] = value;
      });
      data.serveis = fd.getAll('serveis').join(', ') || 'No indicat';
      data._subject = 'Nou missatge des de lordiguer.cat';
      data._template = 'table';
      submit.disabled = true;
      setStatus('Enviant…');
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data)
      })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (String(res.success) === 'true') {
            form.reset();
            setStatus('Missatge enviat. Gràcies, et respondrem aviat.', 'ok');
          } else {
            throw new Error(res.message || 'error');
          }
        })
        .catch(function () {
          setStatus('No s’ha pogut enviar. Escriu-nos directament a ' + form.getAttribute('data-email') + '.', 'err');
        })
        .then(function () { submit.disabled = false; });
    });
  }

  /* ================= Motion ================= */
  if (reduce || !window.gsap || !window.ScrollTrigger) { reveal(); return; }
  gsap.registerPlugin(ScrollTrigger);
  var css = getComputedStyle(root);
  var INK = css.getPropertyValue('--ink').trim();
  var TERRA = css.getPropertyValue('--terra').trim();
  var GHOST = css.getPropertyValue('--ghost').trim();
  function gutter() { return parseFloat(getComputedStyle(document.body).paddingLeft) || 16; }

  /* Smooth scrolling */
  if (window.Lenis) {
    var lenis = new Lenis({ lerp: 0.09, smoothWheel: true });
    window.__lenis = lenis;
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
    $$('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href');
        var target = id.length > 1 ? document.querySelector(id) : null;
        if (!target) return;
        e.preventDefault();
        lenis.scrollTo(target, { offset: -24, duration: 1.4 });
      });
    });
  }

  /* Split titles into words that rise into place */
  function splitWords(node) {
    Array.prototype.slice.call(node.childNodes).forEach(function (child) {
      if (child.nodeType === 3) {
        var frag = document.createDocumentFragment();
        child.textContent.split(/(\s+)/).forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          var outer = document.createElement('span');
          outer.className = 'w';
          var inner = document.createElement('span');
          inner.textContent = part;
          outer.appendChild(inner);
          frag.appendChild(outer);
        });
        child.parentNode.replaceChild(frag, child);
      } else if (child.nodeType === 1 && !child.classList.contains('w')) {
        splitWords(child);
      }
    });
  }
  $$('[data-split]').forEach(splitWords);

  /* 1 — Opening sequence */
  var intro = gsap.timeline({ defaults: { ease: 'expo.out' } });
  intro.from('.site-header > *', { y: -16, opacity: 0, duration: 0.9, stagger: 0.06 });
  if ($('.dateline')) intro.from('.dateline > *', { y: 10, opacity: 0, duration: 0.8, stagger: 0.08 }, '<0.1');
  var words = $$('.hero__title .w > span, [data-split] .w > span');
  if (words.length) intro.from(words, { yPercent: 112, duration: 1.3, stagger: 0.045 }, '<0.05');
  var introItems = $$('[data-intro]');
  if (introItems.length) intro.from(introItems, { y: 26, opacity: 0, duration: 1.1, stagger: 0.1 }, '-=1.05');
  var paths = $$('.hero__underline path');
  if (paths.length) {
    paths.forEach(function (p) {
      var len = p.getTotalLength();
      p.style.strokeDasharray = len;
      p.style.strokeDashoffset = len;
    });
    intro.to(paths, { strokeDashoffset: 0, duration: 1.1, stagger: 0.18, ease: 'power2.inOut' }, '-=0.8');
  }
  var heroMedia = $('.hero-media');
  var frame = heroMedia && $('.hero-media__frame', heroMedia);
  if (frame) {
    intro.fromTo(frame,
      { clipPath: function () { var g = gutter(); return 'inset(38% ' + g + 'px 0% ' + g + 'px)'; } },
      { clipPath: function () { var g = gutter(); return 'inset(0% ' + g + 'px 0% ' + g + 'px)'; }, duration: 1.5, ease: 'expo.inOut' },
      '-=1.3');
    intro.from($('.hero-media__img', frame), { scale: 1.2, duration: 1.9 }, '<');
    if ($('.badge', heroMedia)) intro.from($('.badge', heroMedia), { scale: 0.4, rotate: -90, opacity: 0, duration: 1.3 }, '-=1.1');
    var caption = $$('figcaption > *', heroMedia);
    if (caption.length) intro.from(caption, { y: 12, opacity: 0, duration: 0.9, stagger: 0.08 }, '-=1');

    /* 2 — The image widens to full bleed as you scroll */
    intro.eventCallback('onComplete', function () {
      gsap.fromTo(frame,
        { clipPath: function () { var g = gutter(); return 'inset(0% ' + g + 'px 0% ' + g + 'px)'; } },
        {
          clipPath: 'inset(0% 0px 0% 0px)',
          ease: 'none',
          immediateRender: false,
          scrollTrigger: { trigger: heroMedia, start: 'top 80%', end: 'top 12%', scrub: 0.6, invalidateOnRefresh: true }
        });
    });
    gsap.fromTo($('.hero-media__img', frame), { yPercent: -5 }, {
      yPercent: 5, ease: 'none',
      scrollTrigger: { trigger: heroMedia, start: 'top bottom', end: 'bottom top', scrub: true }
    });
  }
  reveal();

  /* Magnetic buttons in the hero */
  if (finePointer) {
    $$('.hero__side .btn, .page-hero .btn').forEach(function (btn) {
      var bx = gsap.quickTo(btn, 'x', { duration: 0.6, ease: 'power3' });
      var by = gsap.quickTo(btn, 'y', { duration: 0.6, ease: 'power3' });
      btn.addEventListener('pointermove', function (e) {
        var r = btn.getBoundingClientRect();
        bx((e.clientX - (r.left + r.width / 2)) * 0.22);
        by((e.clientY - (r.top + r.height / 2)) * 0.3);
      });
      btn.addEventListener('pointerleave', function () { bx(0); by(0); });
    });
  }

  /* 3 — Index rows: rule draws, name slides in */
  $$('.svc').forEach(function (row) {
    var tl = gsap.timeline({ scrollTrigger: { trigger: row, start: 'top 88%' } });
    tl.from($('.svc__rule', row), { scaleX: 0.15, duration: 1.2, ease: 'expo.out' })
      .from($('.svc__name', row), { x: -48, opacity: 0.3, duration: 1.2, ease: 'expo.out', clearProps: 'transform,opacity' }, '<0.05')
      .from($$('.svc__desc, .svc__arrow', row), { y: 16, opacity: 0.3, duration: 1, ease: 'expo.out', stagger: 0.06, clearProps: 'transform,opacity' }, '<0.15');
  });

  /* 4 — Statements ink in word by word as they scroll past */
  $$('[data-ink]').forEach(function (block) {
    splitInk(block);
    var inked = $$('.ink', block);
    gsap.fromTo(inked, { color: GHOST }, {
      color: function (i, el) { return el.closest('em') ? TERRA : INK; },
      ease: 'none',
      stagger: 0.1,
      scrollTrigger: { trigger: block, start: 'top 82%', end: 'bottom 50%', scrub: true }
    });
  });
  function splitInk(node) {
    Array.prototype.slice.call(node.childNodes).forEach(function (child) {
      if (child.nodeType === 3) {
        var frag = document.createDocumentFragment();
        child.textContent.split(/(\s+)/).forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          var s = document.createElement('span');
          s.className = 'ink';
          s.textContent = part;
          frag.appendChild(s);
        });
        child.parentNode.replaceChild(frag, child);
      } else if (child.nodeType === 1) {
        splitInk(child);
      }
    });
  }

  /* Gentle reveals: content is readable before it moves */
  $$('[data-reveal]').forEach(function (el) {
    gsap.from(el, { y: 44, opacity: 0.3, duration: 1.2, ease: 'expo.out', clearProps: 'transform,opacity', scrollTrigger: { trigger: el, start: 'top 90%' } });
  });
  ScrollTrigger.batch('.link-card, .faq__item, .post-row, .value, .facts > div', {
    start: 'top 92%',
    once: true,
    onEnter: function (batch) { gsap.from(batch, { y: 30, opacity: 0.3, duration: 1, ease: 'expo.out', stagger: 0.08, clearProps: 'transform,opacity' }); }
  });

  ScrollTrigger.batch('.place-row', {
    start: 'top 94%',
    once: true,
    onEnter: function (batch) { gsap.from(batch, { x: -32, opacity: 0, duration: 0.9, ease: 'power3.out', stagger: 0.06, clearProps: 'transform,opacity' }); }
  });
  $$('.moments--places').forEach(function (list) {
    gsap.from(list.children, { yPercent: 60, opacity: 0, duration: 0.8, ease: 'power2.out', stagger: 0.07, clearProps: 'transform,opacity', scrollTrigger: { trigger: list, start: 'top 88%' } });
  });

  /* 5 — Photographs uncover and drift at their own pace */
  $$('.frame, .feature, .person').forEach(function (fig) {
    var media = $('.frame__media, .feature__media, .person__media', fig);
    if (!media) return;
    var fill = $('.fill', media);
    gsap.fromTo(media, { clipPath: 'inset(14% 0% 14% 0%)' }, {
      clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4, ease: 'expo.out',
      scrollTrigger: { trigger: fig, start: 'top 88%' }
    });
    if (fill) gsap.fromTo(fill, { scale: 1.18 }, { scale: 1, duration: 1.8, ease: 'expo.out', scrollTrigger: { trigger: fig, start: 'top 88%' } });
    var speed = parseFloat(fig.getAttribute('data-speed') || 0);
    if (speed) {
      gsap.to(fig, {
        yPercent: speed * -10, ease: 'none',
        scrollTrigger: { trigger: fig.parentElement, start: 'top bottom', end: 'bottom top', scrub: true }
      });
    }
  });

  /* Cursor label over photographs */
  var viewer = $('#cursor-veure');
  if (finePointer && viewer) {
    gsap.set(viewer, { xPercent: -50, yPercent: -50, scale: 0.4 });
    var vX = gsap.quickTo(viewer, 'x', { duration: 0.45, ease: 'power3' });
    var vY = gsap.quickTo(viewer, 'y', { duration: 0.45, ease: 'power3' });
    window.addEventListener('pointermove', function (e) { vX(e.clientX); vY(e.clientY); }, { passive: true });
    $$('.frame__media, .feature__media').forEach(function (m) {
      m.addEventListener('pointerenter', function () { gsap.to(viewer, { autoAlpha: 1, scale: 1, duration: 0.45, ease: 'expo.out' }); });
      m.addEventListener('pointerleave', function () { gsap.to(viewer, { autoAlpha: 0, scale: 0.4, duration: 0.3 }); });
    });
  }

  /* 6 — Marquee: steady drift that speeds up and leans with scroll velocity */
  var track = $('#marquee');
  if (track) {
    var loop = gsap.to(track, { xPercent: -50, duration: 46, ease: 'none', repeat: -1 });
    var skewTo = gsap.quickTo(track, 'skewX', { duration: 0.5, ease: 'power3' });
    var settle;
    ScrollTrigger.create({
      trigger: track,
      start: 'top bottom',
      end: 'bottom top',
      onUpdate: function (self) {
        var v = self.getVelocity();
        gsap.to(loop, { timeScale: Math.min(5, 1 + Math.abs(v) / 500), duration: 0.25, overwrite: true });
        skewTo(gsap.utils.clamp(-7, 7, v / -220));
        clearTimeout(settle);
        settle = setTimeout(function () {
          gsap.to(loop, { timeScale: 1, duration: 1.2, ease: 'power2.out', overwrite: true });
          skewTo(0);
        }, 140);
      }
    });
  }

  /* 7 — Cards stagger in */
  ScrollTrigger.batch('.card', {
    start: 'top 90%',
    once: true,
    onEnter: function (batch) { gsap.from(batch, { y: 60, opacity: 0.3, duration: 1.3, ease: 'expo.out', stagger: 0.12, clearProps: 'transform,opacity' }); }
  });

  /* 8 — Closing: the big call rises, the wordmark lifts into place */
  gsap.from('.big-cta span', {
    yPercent: 60, opacity: 0.3, duration: 1.3, ease: 'expo.out', stagger: 0.05, clearProps: 'transform,opacity',
    scrollTrigger: { trigger: '.site-footer', start: 'top 80%' }
  });
  gsap.fromTo('.marca-gran', { yPercent: 45 }, {
    yPercent: 0, ease: 'none',
    scrollTrigger: { trigger: '.wordmark', start: 'top bottom', end: 'bottom bottom', scrub: true }
  });

  window.addEventListener('load', function () { ScrollTrigger.refresh(); });
})();
