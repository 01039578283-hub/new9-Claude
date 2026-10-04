(() => {
  'use strict';
  const filters = document.querySelector('#library-filters');
  if (filters) {
    const cards = [...document.querySelectorAll('[data-guide-card]')];
    const groups = [...document.querySelectorAll('[data-guide-group]')];
    const status = document.querySelector('#library-status');
    const empty = document.querySelector('#library-empty');
    const normalize = value => value.normalize('NFKC').toLocaleLowerCase().trim();
    const update = () => {
      const terms = normalize(filters.elements.query.value).split(/\s+/).filter(Boolean);
      const { group, stage, audience } = filters.elements;
      let count = 0;
      cards.forEach(card => {
        const text = normalize(card.dataset.search);
        const matched = terms.every(term => text.includes(term)) &&
          (!group.value || card.dataset.group === group.value) &&
          (!stage.value || card.dataset.stages.split(' ').includes(stage.value)) &&
          (!audience.value || card.dataset.audience === audience.value || card.dataset.audience === 'both');
        card.hidden = !matched;
        count += Number(matched);
      });
      groups.forEach(section => {
        const visible = [...section.querySelectorAll('[data-guide-card]')].filter(card => !card.hidden).length;
        section.hidden = visible === 0;
        section.querySelector('.library-group-heading span').textContent = `${visible}편`;
      });
      status.textContent = `전체 ${cards.length}편 중 ${count}편이 표시됩니다.`;
      empty.hidden = count > 0;
    };
    filters.addEventListener('submit', event => event.preventDefault());
    filters.addEventListener('input', update);
    filters.addEventListener('change', update);
    filters.addEventListener('reset', () => setTimeout(update, 0));
    document.querySelector('.library-topic-nav').addEventListener('click', event => {
      const link = event.target.closest('a[href^="#topic-"]');
      if (!link) return;
      filters.elements.query.value = '';
      filters.elements.group.value = link.getAttribute('href').slice('#topic-'.length);
      filters.elements.stage.value = '';
      filters.elements.audience.value = '';
      update();
    });
    filters.hidden = false;
    update();
  }
  const record = document.querySelector('#guide-record-form');
  if (!record) return;
  const status = document.querySelector('#record-status');
  const fields = [...record.querySelectorAll('textarea')];
  const fieldName = field => field.parentElement.firstChild.textContent.trim();
  const title = record.dataset.title;
  record.addEventListener('submit', event => event.preventDefault());
  record.addEventListener('input', () => { status.textContent = ''; });
  record.addEventListener('reset', () => { status.textContent = '입력 내용을 지웠습니다.'; });
  // Plain text only. Input never becomes markup, a URL, or a server request.
  document.querySelector('#record-download').addEventListener('click', () => {
    const lines = [title, '학습 기록', '', ...fields.flatMap(field => [fieldName(field), field.value.trim() || '____________________________', ''])];
    const blob = new Blob(['\ufeff', lines.join('\r\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = '스터디와와-학습기록.txt';
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    status.textContent = fields.some(field => field.value.trim()) ? '현재 입력한 기록을 TXT로 내려받습니다.' : '빈 기록 양식을 TXT로 내려받습니다.';
  });
  const preparePrint = () => {
    fields.forEach(field => {
      let value = field.parentElement.querySelector('.library-print-value');
      if (!value) {
        value = document.createElement('span');
        value.className = 'library-print-value';
        field.parentElement.append(value);
      }
      value.textContent = field.value || ' ';
    });
    document.body.classList.add('library-printing');
  };
  const finishPrint = () => { document.body.classList.remove('library-printing'); };
  window.addEventListener('beforeprint', preparePrint);
  window.addEventListener('afterprint', finishPrint);
  document.querySelector('#record-print').addEventListener('click', () => { preparePrint(); window.print(); });
  record.querySelector('.library-record-actions').hidden = false;
})();
