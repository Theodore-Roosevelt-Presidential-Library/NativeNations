/* Widgets: card, list, map. Reports height (and, for deep linking, the current view) to embed.js. */
(async () => {
  const s = document.createElement('script'); s.src = '/assets/common.js'; document.head.append(s);
  await new Promise(r => s.onload = r);
  const w = document.getElementById('w'), kind = w.dataset.widget, p = NN.params();
  const msg = extra => parent.postMessage({nativenations: true, id: p.frame, height: document.documentElement.scrollHeight, ...extra}, '*');
  const post = () => msg({});
  new ResizeObserver(post).observe(document.body);
  if (kind === 'map') { const m = document.createElement('script'); m.src = '/assets/map.js'; document.body.append(m); return; }
  const all = await NN.load();
  const esc = NN.esc, deep = p.deeplink === '1';
  const SITE = 'https://nativenations.labs.trlibrary.com';

  // In-widget nation detail (deep-linkable as nn-nation=<id>)
  const detail = async (id, push) => {
    const n = await (await fetch(`/api/v1/nations/${id}.json`)).json().catch(() => null);
    if (!n) { w.innerHTML = '<p class="empty">Nation not found.</p>'; return post(); }
    const links = n.links.filter(l => !['official', 'history', 'reference'].includes(l.type));
    w.innerHTML = `<article class="card has-links" style="max-width:none">
      ${kind === 'list' ? '<p class="caption"><a href="#" id="back">&lsaquo; All nations</a></p>' : ''}
      <h3>${esc(n.name)}</h3>
      <div class="where">${esc([n.nearest_town || (n.hq || {}).city, n.states.map(x => NN.STATES[x] || x).join(', ')].filter(Boolean).join(' · '))}</div>
      ${n.peoples && n.peoples.length ? `<div class="caption">${n.peoples.map(pp => esc(pp.name)).join(' · ')}</div>` : ''}
      ${n.official_website ? `<p class="caption"><a href="${esc(n.official_website)}" target="_blank" rel="noopener">Official website</a></p>` : ''}
      <ul class="linklist">${links.map(l => `<li><a href="${esc(l.go)}" target="_blank" rel="noopener">${esc(l.label)}</a><span class="caption">${esc(l.type_label)}</span></li>`).join('') || '<li class="caption">Tourism links for this nation haven’t been added yet.</li>'}</ul>
      <p class="more"><a href="${SITE}/nations/${n.id}/" target="_blank" rel="noopener">Full page on Native Nations &rsaquo;</a></p></article>`;
    const b = document.getElementById('back');
    if (b) b.addEventListener('click', e => { e.preventDefault(); list(view(), true); });
    msg({view: {...view(), nation: id}, push, scrollTop: push});
  };

  if (kind === 'card') {
    const n = all.find(x => x.id === (p.nation || p.id));
    if (!n) { w.innerHTML = '<p class="empty">Nation not found.</p>'; return post(); }
    return detail(n.id, false);
  }

  // List with optional filter bar (data-filters="1")
  let state = {q: p.q || '', state: p.state || '', region: p.region || '', alliance: p.alliance || '', people: p.people || '', visit: p.visit || ''};
  const view = () => Object.fromEntries(Object.entries(state).filter(([, v]) => v));
  const list = (v, push) => {
    state = {...state, ...Object.fromEntries(Object.keys(state).map(k => [k, v[k] || '']))};
    const hits = NN.filter(all, state).sort((a, b) => (b.visit - a.visit) || a.name.localeCompare(b.name)).slice(0, +p.limit || 600);
    const bar = p.filters === '1' ? `<form class="controls" id="f" onsubmit="return false" style="grid-template-columns:2fr 1fr auto;margin:0 0 12px">
      <label><span class="label">Search</span><input type="search" name="q" value="${esc(state.q)}" placeholder="Nation, town or people"></label>
      <label><span class="label">State</span><select name="state"><option value="">All states</option>${Object.entries(NN.STATES).sort((a, b) => a[1].localeCompare(b[1])).map(([k, n]) => `<option value="${k}"${state.state === k ? ' selected' : ''}>${n}</option>`).join('')}</select></label>
      <label class="check"><input type="checkbox" name="visit" value="1"${state.visit ? ' checked' : ''}> Tourism links</label></form>` : '';
    w.innerHTML = `${bar}<p class="count" id="c">${hits.length} nation${hits.length === 1 ? '' : 's'}</p><div class="grid" id="g"></div>
      <p style="text-align:center;margin:14px 0"><button class="btn ghost" id="m" hidden>Show more</button></p>
      <p class="caption" style="margin-top:10px">From <a href="${SITE}/" target="_blank" rel="noopener">Native Nations</a>, Theodore Roosevelt Presidential Library</p>`;
    const g = document.getElementById('g'), m = document.getElementById('m'), PAGE = 24; let shown = 0;
    const cardHTML = n => NN.card(n, !deep).replace(/href="\/nations\/([^/]+)\/"/g, deep ? 'href="#$1" data-nation="$1"' : `href="${SITE}/nations/$1/"`);
    const more = () => { g.insertAdjacentHTML('beforeend', hits.slice(shown, shown + PAGE).map(cardHTML).join('')); shown += PAGE; m.hidden = shown >= hits.length; post(); };
    m.addEventListener('click', more); more();
    if (deep) g.addEventListener('click', e => { const a = e.target.closest('[data-nation]'); if (a) { e.preventDefault(); detail(a.dataset.nation, true); } });
    const f = document.getElementById('f');
    if (f) f.addEventListener('input', () => { list({q: f.q.value, state: f.state.value, visit: f.visit.checked ? '1' : '', region: state.region, alliance: state.alliance, people: state.people}, false); const nf = document.getElementById('f'); nf.q.focus(); nf.q.setSelectionRange(nf.q.value.length, nf.q.value.length); });
    msg({view: view(), push});
  };

  addEventListener('message', ev => {
    if (!ev.data || !ev.data.nativenations || !ev.data.restore) return;
    const r = ev.data.restore;
    r.nation ? detail(r.nation, false) : list(r, false);
  });

  p.nation ? detail(p.nation, false) : list(view(), false);
})();
