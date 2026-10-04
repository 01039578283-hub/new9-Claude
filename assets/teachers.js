(() => {
  'use strict';
  const form = document.getElementById('teacher-filters');
  if (!form) return;
  const query = document.getElementById('teacher-query');
  const region = document.getElementById('teacher-region');
  const status = document.getElementById('teacher-results');
  const empty = document.getElementById('teacher-empty');
  const cards = [...document.querySelectorAll('[data-teacher-branch]')];
  const sections = [...document.querySelectorAll('[data-teacher-region]')];
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ko').replace(/[\s*·]/g, '');
  const entries = cards.map(card => ({
    card, region: card.dataset.region, search: normalize(card.dataset.search),
    names: [...card.querySelectorAll('[data-teacher-name]')].map(element => ({element, search: normalize(element.dataset.search)}))
  }));
  let composing = false;
  function update() {
    const terms = query.value.trim().split(/\s+/).map(normalize).filter(Boolean);
    let branchCount = 0;
    let teacherCount = 0;
    for (const entry of entries) {
      const inRegion = !region.value || entry.region === region.value;
      let matches = 0;
      for (const teacher of entry.names) {
        const haystack = entry.search + teacher.search;
        const visible = inRegion && terms.every(term => haystack.includes(term));
        teacher.element.hidden = !visible;
        if (visible) matches++;
      }
      entry.card.hidden = !matches;
      if (matches) { branchCount++; teacherCount += matches; }
    }
    for (const section of sections) {
      const visible = [...section.querySelectorAll('[data-teacher-branch]')].filter(card => !card.hidden);
      section.hidden = visible.length === 0;
      section.querySelector('.teacher-section-heading > p').textContent = `${visible.length}개 지점`;
    }
    for (const link of document.querySelectorAll('.teacher-region-nav a')) {
      link.hidden = document.getElementById(link.getAttribute('href').slice(1)).hidden;
    }
    status.textContent = terms.length || region.value
      ? `${branchCount}개 지점에서 ${teacherCount}개의 교사 소개를 찾았습니다.`
      : '205개 지점의 교사 소개를 볼 수 있습니다.';
    empty.hidden = branchCount > 0;
  }
  form.addEventListener('submit', event => { event.preventDefault(); update(); });
  form.addEventListener('input', () => { if (!composing) update(); });
  form.addEventListener('change', update);
  query.addEventListener('compositionstart', () => { composing = true; });
  query.addEventListener('compositionend', () => { composing = false; update(); });
  form.addEventListener('reset', () => { query.value = ''; region.value = ''; update(); });
  form.hidden = false;
  update();
})();
