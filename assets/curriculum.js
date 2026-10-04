(() => {
  'use strict';
  const form = document.getElementById('curriculum-filters');
  if (form) {
    const query = document.getElementById('curriculum-query');
    const grade = document.getElementById('curriculum-grade');
    const subject = document.getElementById('curriculum-subject');
    const cards = [...document.querySelectorAll('[data-curriculum-card]')];
    const normalize = value => value.toLowerCase().replace(/\s+/g, '');
    const update = () => {
      const q = normalize(query.value); let count = 0;
      for (const card of cards) {
        const visible = (!grade.value || card.dataset.grade === grade.value)
          && (!subject.value || card.dataset.subject === subject.value)
          && (!q || normalize(card.textContent + card.dataset.grade).includes(q));
        card.hidden = !visible; if (visible) count++;
      }
      document.getElementById('curriculum-results').textContent = count + '개 안내를 볼 수 있습니다.';
      document.getElementById('curriculum-empty').hidden = count !== 0;
    };
    form.hidden = false;
    form.addEventListener('input', update); form.addEventListener('change', update);
    form.addEventListener('submit', event => event.preventDefault());
    form.addEventListener('reset', () => setTimeout(update, 0));
    update();
  }
  const params = new URLSearchParams(location.search);
  const place = params.get('neighborhood'); const from = params.get('from');
  if (!place || !from || !document.getElementById('curriculum-context')) return;
  fetch('/assets/curriculum-localities.json')
    .then(response => { if (!response.ok) throw new Error('Missing directory'); return response.json(); })
    .then(items => {
      const item = items.find(x => x.slug === place && x.returnPaths.includes(from));
      if (!item) return;
      const status = document.getElementById('curriculum-context');
      status.textContent = item.name + ' · ' + item.center + ' 안내에서 이어서 보고 있습니다. 현재 학년·과목의 수업 가능 여부는 지점에 확인하세요.';
      const actions = document.getElementById('curriculum-local-actions');
      const group = document.createElement('div'); group.className = 'curriculum-actions';
      for (const [href, text] of [[from, item.name + ' 이전 학원 안내로 돌아가기'], [item.centerUrl, item.center + ' 지점 안내 보기']]) {
        const a = document.createElement('a'); a.className = 'btn btn-ghost'; a.href = href; a.textContent = text; group.append(a);
      }
      actions.prepend(group);
    }).catch(() => { /* The static directory and consultation links remain usable. */ });
})();
