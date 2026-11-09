(async () => {
  const list = document.getElementById('list'), q = document.getElementById('q');
  const nations = await (await fetch('api/v1/nations.json')).json();
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const card = n => `<article class="card"><h2>${esc(n.name)}</h2>
    <p class="meta">${esc([n.nearest_town, n.states.join(', ')].filter(Boolean).join(' · '))}</p>
    ${n.blurb ? `<p>${esc(n.blurb)}</p>` : ''}
    <ul>${n.links.map(l => `<li><a href="${esc(l.go)}" target="_blank" rel="noopener">${esc(l.label)}</a><span class="pub">${esc(l.type_label)}</span></li>`).join('')}</ul></article>`;
  const render = () => {
    const t = q.value.trim().toLowerCase();
    const hit = nations.filter(n => !t || [n.name, n.fr_name, n.nearest_town, ...n.states, ...n.aka].join(' ').toLowerCase().includes(t));
    list.innerHTML = hit.map(card).join('') || '<p>No matches.</p>';
  };
  q.addEventListener('input', render); render();
})();
