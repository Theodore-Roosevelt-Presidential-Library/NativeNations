(async () => {
  const form = document.getElementById('filters'), out = document.getElementById('results'),
        count = document.getElementById('count'), more = document.getElementById('more');
  const all = await NN.load(); const PAGE = 36; let shown = 0, hits = [];
  const p = NN.params();
  for (const [k, v] of Object.entries(p)) { const el = form.elements[k]; if (el) el.type === 'checkbox' ? el.checked = v === '1' : el.value = v; }
  const state = () => ({q: form.q.value, state: form.state.value, region: form.region.value, alliance: form.alliance.value,
                        people: form.people ? form.people.value : '', visit: form.visit.checked ? '1' : ''});
  const sentinel = document.createElement('div'); sentinel.setAttribute('aria-hidden', 'true'); sentinel.style.height = '1px';
  out.after(sentinel);
  const appendPage = () => {
    if (shown >= hits.length) return;
    out.insertAdjacentHTML('beforeend', hits.slice(shown, shown + PAGE).map(n => NN.card(n)).join(''));
    shown = Math.min(shown + PAGE, hits.length);
    more.hidden = 'IntersectionObserver' in window || shown >= hits.length;
    count.textContent = `${hits.length} nation${hits.length === 1 ? '' : 's'}${shown < hits.length ? ` · showing ${shown}` : ''}`;
  };
  const render = () => {
    const f = state(); hits = NN.filter(all, f).sort((a, b) => (b.visit - a.visit) || a.name.localeCompare(b.name));
    out.innerHTML = hits.length ? '' : '<p class="empty">No nations match. Try a broader search.</p>';
    shown = 0; appendPage();
    if (!hits.length) count.textContent = '0 nations';
    const qs = new URLSearchParams(Object.entries(f).filter(([, v]) => v)).toString();
    history.replaceState(null, '', qs ? `?${qs}` : location.pathname);
  };
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) appendPage(); }, {rootMargin: '600px'}).observe(sentinel);
  }
  form.addEventListener('input', render);
  more.addEventListener('click', appendPage);
  render();
})();
