/* Keep public navigation context in this tab; never store personal form entries. */
(() => {
  'use strict';
  const key = 'studywawa-navigation-context-v1';
  const allowed = new Set(['place', 'grade', 'subject', 'level', 'availability', 'neighborhood', 'from']);
  const clean = value => {
    const result = new URLSearchParams();
    for (const [name, text] of new URLSearchParams(value)) {
      if (allowed.has(name) && text.length <= 300 && !/[\u0000-\u001f\u007f]/u.test(text)) result.set(name, text);
    }
    return result;
  };
  window.studywawaNavigationContext = () => {
    if (location.search) return clean(location.search); // Existing shared URLs continue to work.
    try {
      const item = JSON.parse(sessionStorage.getItem(key) || 'null');
      if (item && item.path === decodeURIComponent(location.pathname) && Date.now() >= item.at && Date.now() - item.at < 1800000) return clean(item.query);
    } catch { /* A blocked storage API must never block links or the original page. */ }
    return new URLSearchParams();
  };
  const remember = event => {
    const a = event.target.closest?.('a[href]');
    if (!a) return;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin || !/^\/(상담문의|교육정보|학습커리큘럼)\//.test(decodeURIComponent(url.pathname))) return;
    try {
      if (a.dataset.studyContext) sessionStorage.setItem(key, JSON.stringify({path: decodeURIComponent(url.pathname), query: clean(a.dataset.studyContext).toString(), at: Date.now()}));
      else if (!url.search) sessionStorage.removeItem(key);
    } catch { /* The destination's static navigation remains available. */ }
  };
  document.addEventListener('pointerdown', remember, true);
  document.addEventListener('click', remember, true);
  document.addEventListener('auxclick', remember, true);
  document.addEventListener('keydown', event => { if (event.key === 'Enter') remember(event); }, true);
})();
