/* Map page, fact-page mini map and map widget */
(() => {
  const TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  const ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
  const style = n => ({radius: 7, color: '#25282A', weight: 1.5, fillColor: n.visit ? '#E7805D' : '#99ADC5', fillOpacity: .95});
  const base = el => { const m = L.map(el, {scrollWheelZoom: false, worldCopyJump: true}); L.tileLayer(TILES, {attribution: ATTR, maxZoom: 19}).addTo(m); return m; };

  const mini = document.getElementById('minimap');
  if (mini) {
    const ll = [+mini.dataset.lat, +mini.dataset.lon], m = base(mini).setView(ll, 8);
    L.circleMarker(ll, {...style({visit: true}), radius: 9}).addTo(m).bindTooltip(mini.dataset.label + ' — tribal government headquarters');
    return;
  }
  const el = document.getElementById('map'); if (!el) return;
  const form = document.getElementById('filters'), count = document.getElementById('count');
  const widget = document.body.classList.contains('widget'); const p = NN.params();
  if (widget && p.height) el.style.height = (+p.height) + 'px';
  const map = base(el); const layer = L.layerGroup().addTo(map);
  map.fitBounds([[24, -125], [50, -66]]);
  if (form) for (const [k, v] of Object.entries(p)) { const f = form.elements[k]; if (f) f.type === 'checkbox' ? f.checked = v === '1' : f.value = v; }
  NN.load().then(all => {
    const draw = (fit) => {
      const f = form ? {q: form.q.value, state: form.state.value, region: form.region.value, alliance: form.alliance.value, visit: form.visit.checked ? '1' : ''} : p;
      const hits = NN.filter(all, f).filter(n => n.lat != null);
      layer.clearLayers();
      hits.sort((a, b) => a.visit - b.visit).forEach(n => L.circleMarker([n.lat, n.lon], style(n)).addTo(layer)
        .bindPopup(`<b>${NN.esc(n.name)}</b>${NN.esc(NN.where(n))}<br><a href="/nations/${n.id}/"${widget ? ' target="_blank" rel="noopener"' : ''}>Plan your visit &rsaquo;</a>`));
      if (count) count.textContent = `${hits.length} nation${hits.length === 1 ? '' : 's'} shown. Points mark tribal government headquarters.`;
      if (fit && hits.length && (f.state || f.q || f.region || f.alliance)) map.fitBounds(L.latLngBounds(hits.map(n => [n.lat, n.lon])).pad(.2), {maxZoom: 9});
      if (form) { const qs = new URLSearchParams(Object.entries(f).filter(([, v]) => v)).toString(); history.replaceState(null, '', qs ? `?${qs}` : location.pathname); }
    };
    if (form) form.addEventListener('input', () => draw(true));
    draw(true);
  });
})();
