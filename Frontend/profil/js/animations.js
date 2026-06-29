/* animations.js — VISUAL ONLY.
   Tidak menyentuh logika data/API/form. Hanya menambahkan efek interaksi visual:
   - efek navbar saat scroll
   - scroll-reveal section (Intersection Observer)
   - tombol scroll-to-top
*/
(function () {
  const nav = document.getElementById('navbar') || document.querySelector('nav');

  const onScroll = () => {
    if (!nav) return;
    if (window.scrollY > 10) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Scroll reveal
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach(el => observer.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add('in-view'));
  }

  // Scroll to top button
  const scrollBtn = document.getElementById('scrollTopBtn');
  if (scrollBtn) {
    const toggleScrollBtn = () => {
      if (window.scrollY > 400) scrollBtn.classList.add('visible');
      else scrollBtn.classList.remove('visible');
    };
    window.addEventListener('scroll', toggleScrollBtn, { passive: true });
    toggleScrollBtn();
    scrollBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();

/* --- Depth Gauge — highlights current section as a "dive depth" marker.
   Decorative only; the page works perfectly without it. --- */
(function () {
  const marks = document.querySelectorAll('.depth-gauge__marks li');
  if (!marks.length || !('IntersectionObserver' in window)) return;

  const map = {};
  marks.forEach(li => { map[li.dataset.target] = li; });

  const sectionIds = Object.keys(map);
  const sections = sectionIds
    .map(id => document.getElementById(id))
    .filter(Boolean);

  if (!sections.length) return;

  const setActive = (id) => {
    marks.forEach(li => li.classList.remove('active'));
    if (map[id]) map[id].classList.add('active');
  };

  // Gunakan scroll position untuk menentukan section aktif,
  // lebih andal daripada threshold tinggi yang gagal pada section pendek
  const getActiveSection = () => {
    const scrollMid = window.scrollY + window.innerHeight * 0.35;
    let active = sections[0];
    for (const sec of sections) {
      if (sec.offsetTop <= scrollMid) active = sec;
    }
    return active ? active.id : null;
  };

  const navLinks = document.querySelectorAll('#navMenu .nav-link');

  const setNavActive = (id) => {
    navLinks.forEach(a => {
      const href = a.getAttribute('href');
      if (href === '#' + id) a.classList.add('active');
      else a.classList.remove('active');
    });
  };

  const onScrollGauge = () => {
    const id = getActiveSection();
    if (id) {
      setActive(id);
      setNavActive(id);
    }
  };

  window.addEventListener('scroll', onScrollGauge, { passive: true });
  onScrollGauge();

  // Tetap pakai observer ringan sebagai backup saat load awal
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) onScrollGauge();
    });
  }, { threshold: 0.05, rootMargin: '0px' });

  sections.forEach(el => observer.observe(el));

  marks.forEach(li => {
    li.style.cursor = 'pointer';
    li.addEventListener('click', () => {
      const target = document.getElementById(li.dataset.target);
      if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
  });
})();

/* --- Profile panel tilt — subtle pointer-following tilt on the about photo.
   Skipped on touch devices and when reduced motion is preferred. --- */
(function () {
  const frame = document.getElementById('aboutPanelFrame');
  if (!frame) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (window.matchMedia('(pointer: coarse)').matches) return;

  frame.addEventListener('mousemove', (e) => {
    const rect = frame.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width - 0.5;
    const py = (e.clientY - rect.top) / rect.height - 0.5;
    frame.style.setProperty('--rx', (px * 14).toFixed(2) + 'deg');
    frame.style.setProperty('--ry', (py * -14).toFixed(2) + 'deg');
  });

  frame.addEventListener('mouseleave', () => {
    frame.style.setProperty('--rx', '0deg');
    frame.style.setProperty('--ry', '0deg');
  });
})();

/* --- Bubbles follow click — wherever the user clicks on the page,
   the floating bubbles drift toward that horizontal position. --- */
(function () {
  const bubbles = document.querySelectorAll('.bubble');
  if (!bubbles.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.addEventListener('click', (e) => {
    const xPercent = (e.clientX / window.innerWidth) * 100;

    bubbles.forEach((bubble, i) => {
      // Spread each bubble around the click point so they don't overlap
      const offset = (i - (bubbles.length - 1) / 2) * 9;
      let left = xPercent + offset;
      left = Math.max(2, Math.min(96, left));
      bubble.style.left = left + '%';
    });
  });
})();
