/* Unwritten Health: site chrome behaviour (menu, dropdown, header shadow, sticky call to action). */
(function () {
  var header = document.querySelector('.uh-header');
  var burger = document.querySelector('.uh-burger');
  var panel = document.getElementById('uh-mobile');

  function setMenu(open) {
    if (!burger || !panel) return;
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    panel.classList.toggle('is-open', open);
    document.body.classList.toggle('uh-menu-open', open);
  }
  if (burger) burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
  if (panel) panel.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });

  // "Who it's for" dropdown: hover/focus open it in CSS; the toggle button also opens it for touch and keyboard users.
  document.querySelectorAll('.uh-dd').forEach(function (dd) {
    var btn = dd.querySelector('.uh-dd-toggle');
    if (!btn) return;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var open = !dd.classList.contains('is-open');
      dd.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!dd.contains(e.target)) { dd.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false'); }
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    setMenu(false);
    document.querySelectorAll('.uh-dd.is-open').forEach(function (dd) {
      dd.classList.remove('is-open');
      var b = dd.querySelector('.uh-dd-toggle'); if (b) b.setAttribute('aria-expanded', 'false');
    });
  });

  function onScroll() { if (header) header.classList.toggle('is-scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Hide the sticky mobile button while the page's own call to action or the footer is on screen.
  var sticky = document.querySelector('.uh-sticky');
  if (sticky && 'IntersectionObserver' in window) {
    var targets = document.querySelectorAll('.uh-cta, .uh-footer, [data-hide-sticky]');
    var visible = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) visible.add(en.target); else visible.delete(en.target); });
      sticky.classList.toggle('is-hidden', visible.size > 0);
    }, { threshold: 0.01 });
    targets.forEach(function (t) { io.observe(t); });
  }
})();
