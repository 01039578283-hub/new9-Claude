(() => {
  'use strict';
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ko').replace(/\s+/g, '');
  const form = document.getElementById('education-filters');
  if (form) {
    const query = document.getElementById('education-query');
    const group = document.getElementById('education-group');
    const kind = document.getElementById('education-kind');
    const cards = [...document.querySelectorAll('[data-education-card]')];
    let composing = false;
    const update = () => {
      const terms = query.value.trim().split(/\s+/).map(normalize).filter(Boolean);
      let count = 0;
      for (const card of cards) {
        const match = (!group.value || card.dataset.group === group.value) && (!kind.value || card.dataset.kind === kind.value) && terms.every(term => normalize(card.dataset.search).includes(term));
        card.hidden = !match;
        if (match) count += 1;
      }
      document.getElementById('education-results').textContent = `${count}편의 글을 찾았습니다.`;
      document.getElementById('education-empty').hidden = count !== 0;
    };
    form.addEventListener('submit', event => event.preventDefault());
    query.addEventListener('compositionstart', () => { composing = true; });
    query.addEventListener('compositionend', () => { composing = false; update(); });
    query.addEventListener('input', () => { if (!composing) update(); });
    group.addEventListener('change', update);
    kind.addEventListener('change', update);
    form.addEventListener('reset', () => { requestAnimationFrame(update); });
    form.hidden = false;
    update();
  }
  const localForm = document.getElementById('education-local-form');
  if (!localForm) return;
  const locations = JSON.parse(document.getElementById('education-locations').textContent);
  const region = document.getElementById('education-region');
  const place = document.getElementById('education-place');
  const subject = document.getElementById('education-subject');
  const actions = document.getElementById('education-local-actions');
  const status = document.getElementById('education-place-status');
  const params = new URLSearchParams(location.search);
  const incoming = params.get('from') || '';
  const origin = /^\/(과목별학원|전국학원)\/[^/]+\/[^/]+\/$/.test(incoming) ? incoming : '';
  let useOrigin = true;
  const link = (href, label, primary) => {
    const element = document.createElement('a');
    element.className = primary ? 'btn btn-primary' : 'btn btn-ghost';
    element.href = href;
    element.textContent = label;
    return element;
  };
  const populate = () => {
    place.replaceChildren(new Option('동네 선택', ''));
    for (const item of locations.filter(item => item.region === region.value)) place.add(new Option(`${item.name} · ${item.center}`, item.slug));
    place.disabled = !region.value;
  };
  const updateLocal = () => {
    const item = locations.find(item => item.slug === place.value && item.region === region.value);
    actions.replaceChildren();
    if (!item) {
      status.textContent = '지역과 동네를 선택하면 해당 동네의 과목 안내와 지점 정보로 이동할 수 있습니다.';
      actions.append(link('/전국학원/와와학습코칭센터/', '동네·지점 찾기', true), link('/교육정보/#region-directory', '지역별 안내 목록', false));
      return;
    }
    status.textContent = `${item.name} · ${item.center} · ${item.address}`;
    const parts = origin.split('/');
    if (useOrigin && parts[3] === item.slug && item.returnPaths.includes(origin)) actions.append(link(origin, `${item.name} 학원 안내로 돌아가기`, true));
    else actions.append(link(subject.value === 'english' ? item.englishUrl : item.mathUrl, `${item.name} ${subject.value === 'english' ? '중등 영어' : '중등 수학'} 안내`, true));
    actions.append(link(item.centerUrl, `${item.center} 지점 안내`, false));
  };
  localForm.addEventListener('submit', event => event.preventDefault());
  region.addEventListener('change', () => { useOrigin = false; populate(); updateLocal(); });
  place.addEventListener('change', () => { useOrigin = false; updateLocal(); });
  subject.addEventListener('change', () => { useOrigin = false; updateLocal(); });
  const initial = locations.find(item => item.slug === params.get('neighborhood'));
  if (initial) { region.value = initial.region; populate(); place.value = initial.slug; }
  updateLocal();
  localForm.hidden = false;
})();
