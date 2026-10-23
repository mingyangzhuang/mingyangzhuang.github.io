(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Footer year ---------- */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- Starfield canvas in the hero ---------- */
  var canvas = document.getElementById('starfield');
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext('2d');
    var hero = canvas.closest('.hero');
    var stars = [];
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = 0, h = 0;

    function starColor(alpha) {
      return 'rgba(247, 241, 232, ' + alpha + ')';
    }

    function buildStars() {
      var area = w * h;
      var count = Math.max(60, Math.min(220, Math.round(area / 9000)));
      stars = [];
      for (var i = 0; i < count; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: Math.random() * 1.3 + 0.3,
          base: Math.random() * 0.5 + 0.35,
          speed: Math.random() * 0.015 + 0.006,
          phase: Math.random() * Math.PI * 2
        });
      }
    }

    function resize() {
      w = hero.clientWidth;
      h = hero.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      buildStars();
    }

    function drawStatic() {
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        ctx.beginPath();
        ctx.fillStyle = starColor(s.base);
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    var t = 0;
    function tick() {
      t += 1;
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        var alpha = s.base + Math.sin(t * s.speed + s.phase) * 0.35;
        if (alpha < 0.08) alpha = 0.08;
        ctx.beginPath();
        ctx.fillStyle = starColor(alpha);
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      raf = requestAnimationFrame(tick);
    }

    var raf = null;
    var resizeTimer = null;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        resize();
        if (reduceMotion) drawStatic();
      }, 150);
    });

    resize();
    if (reduceMotion) {
      drawStatic();
    } else {
      tick();
    }
  }

  /* ---------- Nav: mobile menu toggle ---------- */
  var navToggle = document.querySelector('.nav-toggle');
  var navLinksEl = document.getElementById('nav-links');
  if (navToggle && navLinksEl) {
    var closeMenu = function () {
      navLinksEl.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    };
    navToggle.addEventListener('click', function () {
      var isOpen = navLinksEl.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
    navLinksEl.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeMenu);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 700) closeMenu();
    });
  }

  /* ---------- Nav: solid background once you scroll past the hero ---------- */
  var nav = document.querySelector('.site-nav');
  var heroEl = document.querySelector('header.hero');
  if (nav && heroEl && 'IntersectionObserver' in window) {
    var navObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        nav.classList.toggle('solid', !entry.isIntersecting);
      });
    }, { rootMargin: '-' + (nav.offsetHeight || 68) + 'px 0px 0px 0px', threshold: 0 });
    navObserver.observe(heroEl);
  }

  /* ---------- Scroll-reveal for sections and cards ---------- */
  var revealTargets = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealTargets.length) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0, rootMargin: '0px 0px -8% 0px' });
    revealTargets.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Back-to-top button ---------- */
  var backToTop = document.getElementById('back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', function () {
      backToTop.classList.toggle('visible', window.scrollY > window.innerHeight * 0.6);
    }, { passive: true });
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------- Compact layout helpers ---------- */

  // 1+2) First-author list: show the newest few papers that are not already a highlight card; expand on demand.
  (function () {
    var list = document.querySelector('#publications .pub-list');
    if (!list) return;
    var items = Array.prototype.slice.call(list.querySelectorAll('.pub-item'));
    var VISIBLE = 6, shown = 0;
    items.forEach(function (it) {
      var isHighlight = !!it.querySelector('a.venue-badge');
      if (isHighlight || shown >= VISIBLE) it.classList.add('is-collapsed');
      else shown++;
    });
    if (!list.querySelector('.is-collapsed')) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pub-toggle';
    var open = false;
    function label() {
      btn.textContent = open ? 'Show fewer' : 'Show all ' + items.length + ' first-author papers';
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    btn.addEventListener('click', function () {
      open = !open;
      if (open) items.forEach(function (it) { it.classList.remove('is-collapsed'); });
      else {
        var n = 0;
        items.forEach(function (it) {
          var isHighlight = !!it.querySelector('a.venue-badge');
          if (isHighlight || n >= VISIBLE) it.classList.add('is-collapsed'); else n++;
        });
      }
      label();
    });
    label();
    list.parentNode.insertBefore(btn, list.nextSibling);
  })();

  // 4) Highlight cards: clamp long summaries with a Read more toggle.
  document.querySelectorAll('.hl-summary').forEach(function (p) {
    p.classList.add('is-clamped');
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'hl-more';
    b.textContent = 'Read more';
    b.setAttribute('aria-expanded', 'false');
    b.addEventListener('click', function () {
      var o = p.classList.toggle('is-open');
      b.textContent = o ? 'Show less' : 'Read more';
      b.setAttribute('aria-expanded', o ? 'true' : 'false');
    });
    p.parentNode.insertBefore(b, p.nextSibling);
  });

})();
