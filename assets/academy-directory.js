/* All destination links and center facts are rendered in HTML. */
(() => {
  const root = document.querySelector('[data-academy-directory]');
  if (!root) return;
  const form = root.querySelector('form');
  const search = root.querySelector('#center-search');
  const region = root.querySelector('#center-region');
  const grade = root.querySelector('#center-grade');
  const status = root.querySelector('#center-status');
  const empty = root.querySelector('#center-empty');
  const groups = [...root.querySelectorAll('[data-center-group]')];
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase('ko-KR').replace(/\s+/g, '');
  const cards = [...root.querySelectorAll('[data-center-card]')].map(element => ({
    element, text: normalize(element.dataset.search), region: element.dataset.centerRegion,
    status: element.dataset.gradeStatus, center: element.dataset.centerKey
  }));
  const update = () => {
    const terms = search.value.trim().split(/[\s,]+/).filter(Boolean).map(normalize);
    let shown = 0;
    const centers = new Set();
    cards.forEach(card => {
      const matchesGrade = !grade || grade.value === 'all' ||
        (grade.value === 'listed' ? card.status === 'listed' : card.status !== 'listed');
      const matches = terms.every(term => card.text.includes(term)) &&
        (region.value === 'all' || region.value === card.region) && matchesGrade;
      card.element.hidden = !matches;
      if (matches) { shown++; centers.add(card.center); }
    });
    groups.forEach(group => {
      const count = group.querySelectorAll('[data-center-card]:not([hidden])').length;
      group.hidden = count === 0;
      group.querySelector('[data-group-count]').textContent = `${count}개 지역 안내`;
    });
    status.textContent = `${shown}개 지역 안내 · 센터명·주소 기준 ${centers.size}개 센터`;
    empty.hidden = shown > 0;
  };
  form.addEventListener('submit', event => { event.preventDefault(); update(); });
  search.addEventListener('input', update);
  region.addEventListener('change', update);
  grade?.addEventListener('change', update);
  root.querySelectorAll('[data-reset-directory]').forEach(button => button.addEventListener('click', () => {
    form.reset(); update(); search.focus();
  }));
  form.hidden = false;
  update();
})();
