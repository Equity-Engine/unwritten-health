/* Unwritten Health — Google Analytics 4 with consent gate
 * GA only loads after the visitor clicks "Accept". The choice is remembered for 12 months.
 * Visitors can change their choice any time via the "Cookie settings" link in the footer
 * (which calls window.openCookieSettings()).
 * --------------------------------------------------------------------------
 * Measurement ID is set in GA_ID below (GA Admin → Data Streams).
 */
(function () {
  var GA_ID = 'G-89G9T9L19P';                  // Unwritten Health GA4 Measurement ID
  var STORAGE_KEY = 'uh_analytics_consent';     // stores { v: 'granted'|'denied', t: <timestamp> }
  var TTL = 365 * 24 * 60 * 60 * 1000;          // 12 months — re-prompt after this

  // --- Consent Mode v2: default everything denied until the user opts in ---
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied'
  });

  function loadGA() {
    if (window.__uhGALoaded || GA_ID.indexOf('XXXX') !== -1) return;
    window.__uhGALoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', GA_ID);
  }

  function grant() {
    gtag('consent', 'update', { analytics_storage: 'granted' });
    loadGA();
  }

  function deny() {
    gtag('consent', 'update', { analytics_storage: 'denied' });
  }

  function readConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var obj = JSON.parse(raw);
      if (!obj || !obj.v || !obj.t) return null;
      if (Date.now() - obj.t > TTL) { localStorage.removeItem(STORAGE_KEY); return null; }
      return obj.v;
    } catch (e) { return null; }
  }

  function writeConsent(v) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ v: v, t: Date.now() })); } catch (e) {}
  }

  // Expose a way for the footer "Cookie settings" link to re-open the banner.
  window.openCookieSettings = function () { showBanner(); };

  // Apply any previously saved choice.
  var choice = readConsent();
  if (choice === 'granted') { grant(); }

  // Show the banner on first visit (or after a previous choice has expired).
  if (choice === null) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }

  function showBanner() {
    if (document.getElementById('uh-cookie-banner')) return; // already open
    if (!document.body) { document.addEventListener('DOMContentLoaded', showBanner); return; }

    var bar = document.createElement('div');
    bar.id = 'uh-cookie-banner';
    bar.setAttribute('role', 'dialog');
    bar.setAttribute('aria-label', 'Cookie consent');
    // Compact horizontal bar. Sits bottom-left on desktop (out of hero right column),
    // above the sticky-mobile-cta on narrow screens.
    var isNarrow = window.matchMedia && window.matchMedia('(max-width: 900px)').matches;
    var bottomOffset = isNarrow ? 84 : 16;
    bar.style.cssText = [
      'position:fixed',
      'left:' + (isNarrow ? '12px' : '16px'),
      isNarrow ? 'right:12px' : 'right:auto',
      'bottom:' + bottomOffset + 'px',
      'z-index:99999',
      'max-width:' + (isNarrow ? 'none' : '480px'),
      'background:#37373B', 'color:#ffffff', 'border-radius:100px',
      'box-shadow:0 8px 24px rgba(0,0,0,0.22)',
      'padding:8px 8px 8px 20px',
      'display:flex', 'align-items:center', 'gap:12px',
      'flex-wrap:nowrap',
      "font-family:'Manrope',system-ui,sans-serif", 'line-height:1.4'
    ].join(';');

    var text = document.createElement('span');
    text.style.cssText = 'margin:0;font-size:0.82rem;color:rgba(255,255,255,0.85);flex:1 1 auto;min-width:0;';
    text.innerHTML = 'Analytics cookies? <a href="privacy.html" style="color:#b8d0c6;text-decoration:underline;">Privacy</a>';

    var btns = document.createElement('div');
    btns.style.cssText = 'display:flex;gap:6px;flex:0 0 auto;';

    var decline = document.createElement('button');
    decline.type = 'button';
    decline.textContent = 'Decline';
    decline.style.cssText = 'cursor:pointer;padding:8px 14px;border-radius:100px;border:1px solid rgba(255,255,255,0.3);' +
      'background:transparent;color:#ffffff;font-weight:600;font-size:0.78rem;font-family:inherit;';

    var accept = document.createElement('button');
    accept.type = 'button';
    accept.textContent = 'Accept';
    accept.style.cssText = 'cursor:pointer;padding:8px 16px;border-radius:100px;border:none;' +
      'background:#5B8170;color:#ffffff;font-weight:700;font-size:0.78rem;font-family:inherit;';

    function close() { if (bar.parentNode) bar.parentNode.removeChild(bar); }

    accept.addEventListener('click', function () { writeConsent('granted'); grant(); close(); });
    decline.addEventListener('click', function () { writeConsent('denied'); deny(); close(); });

    btns.appendChild(decline);
    btns.appendChild(accept);
    bar.appendChild(text);
    bar.appendChild(btns);
    document.body.appendChild(bar);
  }
})();
