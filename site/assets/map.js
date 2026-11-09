/* Map page, fact-page mini map and map widget */
(() => {
  const TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  const ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
  const style = n => ({radius: 7, color: '#25282A', weight: 1.5, fillColor: n.visit ? '#E7805D' : '#99ADC5', fillOpacity: .95});
  const AREA_STYLE = {color: '#092A4D', weight: 1.5, fillColor: '#99ADC5', fillOpacity: .35};
  const drawAreas = async (m, codes, fit) => {
    codes = (codes || '').split(',').filter(Boolean); if (!codes.length) return null;
    const g = L.featureGroup().addTo(m);
    await Promise.all(codes.map(c => fetch(`/api/v1/boundaries/${c}.geojson`).then(r => r.ok ? r.json() : null).then(fc => {
      if (fc) L.geoJSON(fc, {style: AREA_STYLE, onEachFeature: (f, l) => l.bindTooltip(`${f.properties.name} (${f.properties.kind})`)}).addTo(g);
    }).catch(() => null)));
    g.bringToBack();
    if (fit && g.getLayers().length && g.getBounds().isValid()) m.fitBounds(g.getBounds().pad(.1), {maxZoom: 10});
    return g;
  };
  const base = el => { const m = L.map(el, {scrollWheelZoom: false, worldCopyJump: true}); L.tileLayer(TILES, {attribution: ATTR, maxZoom: 19}).addTo(m); return m; };

  const mini = document.getElementById('minimap');
  if (mini) {
    const ll = [+mini.dataset.lat, +mini.dataset.lon], m = base(mini).setView(ll, 8);
    L.circleMarker(ll, {...style({visit: true}), radius: 9}).addTo(m).bindTooltip(mini.dataset.label + ' — tribal government headquarters');
    drawAreas(m, mini.dataset.areas, true).then(g => { if (g && g.getLayers().length) m.fitBounds(g.getBounds().extend(ll).pad(.1), {maxZoom: 10}); });
    return;
  }
  const pm = document.getElementById('peoplemap');
  if (pm) {
    const m = base(pm).setView([39, -98], 4), ids = new Set(pm.dataset.ids.split(','));
    drawAreas(m, pm.dataset.areas, false);
    NN.load().then(all => {
      const hits = all.filter(n => ids.has(n.id) && n.lat != null);
      hits.forEach(n => L.circleMarker([n.lat, n.lon], style(n)).addTo(m)
        .bindPopup(`<b>${NN.esc(n.name)}</b>${NN.esc(NN.where(n))}<br><a href="/nations/${n.id}/">Plan your visit &rsaquo;</a>`));
      if (hits.length) m.fitBounds(L.latLngBounds(hits.map(n => [n.lat, n.lon])).pad(.25), {maxZoom: 8}); else m.setView([39, -98], 4);
    });
    return;
  }
  const sm = document.getElementById('statemap');
  if (sm) {
    const m = base(sm).setView([39, -98], 4), code = sm.dataset.state;
    drawAreas(m, sm.dataset.areas, false);
    NN.load().then(all => {
      const hits = all.filter(n => n.states.includes(code) && n.lat != null);
      hits.forEach(n => L.circleMarker([n.lat, n.lon], style(n)).addTo(m)
        .bindPopup(`<b>${NN.esc(n.name)}</b>${NN.esc(NN.where(n))}<br><a href="/nations/${n.id}/">Plan your visit &rsaquo;</a>`));
      if (hits.length) m.fitBounds(L.latLngBounds(hits.map(n => [n.lat, n.lon])).pad(.25), {maxZoom: 8}); else m.setView([39, -98], 4);
    });
    return;
  }
  const el = document.getElementById('map'); if (!el) return;
  const form = document.getElementById('filters'), count = document.getElementById('count');
  const widget = document.body.classList.contains('widget'); const p = NN.params();
  if (widget && p.height) el.style.height = (+p.height) + 'px';
  const map = base(el); const layer = L.layerGroup().addTo(map);
  let bndLayer = null;
  const bndBox = document.getElementById('bnd');
  const wantBnd = bndBox ? bndBox.checked : p.boundaries === '1';
  const loadBnd = () => fetch('/api/v1/boundaries/overview.geojson').then(r => r.json()).then(fc => {
    bndLayer = L.geoJSON(fc, {style: {...AREA_STYLE, weight: 1}, onEachFeature: (f, l) => l.bindTooltip(f.properties.name)}).addTo(map); bndLayer.bringToBack();
  });
  if (wantBnd) loadBnd();
  if (bndBox) bndBox.addEventListener('change', () => { if (bndBox.checked) { bndLayer ? bndLayer.addTo(map) : loadBnd(); } else if (bndLayer) map.removeLayer(bndLayer); });
  let cesLayer = null;
  const cesBox = document.getElementById('ces');
  const CES_STYLE = {color: '#E7805D', weight: 1, fillColor: '#E7805D', fillOpacity: .12, dashArray: '3 3'};
  const loadCes = () => fetch('/api/v1/cessions.geojson').then(r => r.json()).then(fc => {
    cesLayer = L.geoJSON(fc, {style: CES_STYLE, onEachFeature: (f, l) => { const q = f.properties;
      l.bindPopup(`<b>Royce cession ${NN.esc(q.cession)}</b>${q.date ? ' · ' + NN.esc(q.date.slice(0, 4)) : ''}<br>${NN.esc(q.royce_tribes || '')}${q.treaty_url ? `<br><a href="${NN.esc(q.treaty_url)}" target="_blank" rel="noopener">Treaty or act</a>` : ''}<br><span style="font-size:12px">USDA Forest Service, CC BY 4.0. Not legal boundaries or homelands.</span>`); }}).addTo(map);
    cesLayer.bringToBack();
  });
  if (cesBox ? cesBox.checked : p.cessions === '1') loadCes();
  if (cesBox) cesBox.addEventListener('change', () => { if (cesBox.checked) { cesLayer ? cesLayer.addTo(map) : loadCes(); } else if (cesLayer) map.removeLayer(cesLayer); });
  map.fitBounds([[24, -125], [50, -66]]);
  if (form) for (const [k, v] of Object.entries(p)) { const f = form.elements[k]; if (f) f.type === 'checkbox' ? f.checked = v === '1' : f.value = v; }
  NN.load().then(all => {
    const draw = (fit) => {
      const f = form ? {q: form.q.value, state: form.state.value, region: form.region.value, alliance: form.alliance.value, people: form.people ? form.people.value : '', visit: form.visit.checked ? '1' : ''} : p;
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
