(async () => {
  const form = document.getElementById('filters'), out = document.getElementById('results'),
        count = document.getElementById('count'), more = document.getElementById('more');
  const all = await NN.load(); const PAGE = 48; let shown = PAGE, hits = [];
  const p = NN.params();
  for (const [k, v] of Object.entries(p)) { const el = form.elements[k]; if (el) el.type === 'checkbox' ? el.checked = v === '1' : el.value = v; }
  const state = () => ({q: form.q.value, state: form.state.value, region: form.region.value, alliance: form.alliance.value, visit: form.visit.checked ? '1' : ''});
  const render = (reset) => {
    if (reset) shown = PAGE;
    const f = state(); hits = NN.filter(all, f).sort((a, b) => (b.visit - a.visit) || a.name.localeCompare(b.name));
    out.innerHTML = hits.slice(0, shown).map(n => NN.card(n)).join('') || '<p class="empty">No nations match. Try a broader search.</p>';
    count.textContent = `${hits.length} nation${hits.length === 1 ? '' : 's'}`;
    more.hidden = hits.length <= shown;
    const qs = new URLSearchParams(Object.entries(f).filter(([, v]) => v)).toString();
    history.replaceState(null, '', qs ? `?${qs}` : location.pathname);
  };
  form.addEventListener('input', () => render(true));
  more.addEventListener('click', () => { shown += PAGE; render(); });
  render(true);
})();
