/* Widgets: card, list, map. Reports height to the parent page for embed.js. */
(async () => {
  const s = document.createElement('script'); s.src = '/assets/common.js'; document.head.append(s);
  await new Promise(r => s.onload = r);
  const w = document.getElementById('w'), kind = w.dataset.widget, p = NN.params();
  const post = () => parent.postMessage({nativenations: true, id: p.frame, height: document.documentElement.scrollHeight}, '*');
  new ResizeObserver(post).observe(document.body);
  if (kind === 'map') {
    const m = document.createElement('script'); m.src = '/assets/map.js'; document.body.append(m); return;
  }
  const all = await NN.load();
  if (kind === 'card') {
    const n = all.find(x => x.id === p.id);
    w.innerHTML = n ? NN.card(n, true) : '<p class="empty">Nation not found.</p>';
  } else {
    const hits = NN.filter(all, p).sort((a, b) => (b.visit - a.visit) || a.name.localeCompare(b.name)).slice(0, +p.limit || ((p.state || p.alliance || p.region || p.q) ? 600 : 24));
    w.innerHTML = `<div class="grid">${hits.map(n => NN.card(n, true)).join('')}</div>
      <p class="caption" style="margin-top:10px">From <a href="https://nativenations.labs.trlibrary.com/" target="_blank" rel="noopener">Native Nations</a>, Theodore Roosevelt Presidential Library</p>`;
  }
  post();
})();
