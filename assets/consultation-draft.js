// Draft preparation only; no network request, persistence, or automatic sending.
(() => {
  const panel = document.querySelector('[data-message-builder]');
  if (!panel) return;
  const form = document.getElementById('consultation-draft');
  const result = document.getElementById('draft-result');
  const message = document.getElementById('draft-message');
  const copy = document.getElementById('draft-copy');
  const status = document.getElementById('draft-status');
  const review = document.getElementById('draft-review');
  const value = name => form.elements.namedItem(name).value.trim();
  let reviewContext = null;
  function needsReview() {
    if (!review || !reviewContext) return false;
    const {place, grade, subject, level} = reviewContext;
    const levelMatches = !level || !value('grade') || value('grade').startsWith(level === 'middle' ? '중' : '고');
    return value('place') === place && (!grade || value('grade') === grade) && value('subject') === subject && levelMatches;
  }
  function updateReview() {
    if (!review) return;
    const show = needsReview();
    review.hidden = !show;
    review.textContent = show ? (reviewContext.availability === 'unknown'
      ? '안내 자료에 해당 과목의 가능 학년이 기재되어 있지 않습니다. 현재 수강 가능 여부를 먼저 확인해 주세요.'
      : '이 안내의 학년은 자료상 가능 학년 목록에 없습니다. 현재 수강 가능 여부를 먼저 확인해 주세요.') : '';
  }
  function clearDraft() {
    result.hidden = true;
    message.value = '';
    status.textContent = '';
    updateReview();
  }
  form.addEventListener('input', clearDraft);
  form.addEventListener('change', clearDraft);
  form.addEventListener('reset', () => {
    reviewContext = null;
    clearDraft();
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const place = form.elements.namedItem('place');
    place.value = place.value.trim();
    if (!form.reportValidity()) return;
    const lines = ['안녕하세요. 수강 상담을 문의드립니다.',
      `센터 또는 동네: ${value('place')}`,
      `학생 학년: ${value('grade')}`,
      `희망 과목: ${value('subject')}`];
    if (value('time')) lines.push(`희망 요일·시간: ${value('time')}`);
    if (value('concern')) lines.push(`궁금한 내용: ${value('concern')}`);
    if (needsReview()) lines.push('확인 요청: 안내 자료에서 확인이 필요한 학년·과목입니다. 현재 수강 가능한 반이 있는지 먼저 확인해 주세요.');
    lines.push('현재 수강 가능 여부와 시간표, 교습비·별도 비용, 방문 가능한 일정을 알려 주세요.');
    message.value = lines.join('\n');
    result.hidden = false;
    status.textContent = '문의 문안이 준비되었습니다. 내용을 확인하고 복사해 주세요.';
    message.focus();
  });
  copy.addEventListener('click', async () => {
    if (!message.value) return;
    const draft = message.value;
    copy.disabled = true;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(draft);
      if (message.value === draft) status.textContent = '문안을 복사했습니다. 문자나 상담 신청서에 붙여넣어 주세요.';
    } catch {
      if (message.value === draft) {
        message.focus();
        message.select();
        status.textContent = '자동 복사를 사용할 수 없습니다. 선택된 문안을 직접 복사해 주세요.';
      }
    } finally {
      copy.disabled = false;
    }
  });
  // Only public center/grade/subject context is accepted; personal fields stay blank.
  const context = new URLSearchParams(window.location.search);
  let prefilled = false;
  for (const name of ['place', 'grade', 'subject']) {
    const field = form.elements.namedItem(name);
    const seed = context.get(name)?.trim();
    if (!seed || field.value || /[\u0000-\u001f\u007f]/u.test(seed)) continue;
    if (name === 'place') {
      if (seed.length > field.maxLength) continue;
    } else if (![...field.options].some(option => option.value === seed)) continue;
    field.value = seed;
    prefilled = true;
  }
  const availability = context.get('availability');
  const place = context.get('place')?.trim();
  const grade = context.get('grade')?.trim() || '';
  const subject = context.get('subject')?.trim();
  const level = context.get('level') || '';
  if (['unknown', 'not_listed'].includes(availability) && place && subject
      && value('place') === place && value('subject') === subject && (!grade || value('grade') === grade)
      && (!level || ['middle', 'high'].includes(level))) {
    reviewContext = {place, grade, subject, level, availability};
  }
  updateReview();
  if (prefilled) status.textContent = '선택한 안내의 센터·학년·과목을 미리 넣었습니다. 내용을 확인하고 필요한 항목을 수정해 주세요.';
  panel.hidden = false;
})();
