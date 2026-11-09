/* Native Nations embed loader.
   <div data-nativenations="list" data-state="ND" data-filters="1"></div>
   <script src="https://nativenations.labs.trlibrary.com/embed.js" async></script>

   Deep linking: the host page's own address can carry nn- query strings, e.g.
     https://example.org/plan-your-trip?nn-state=SD&nn-q=lakota
     https://example.org/plan-your-trip?nn-nation=oglala-sioux-tribe
   They override the widget's data- settings. As people search or open a nation inside
   the widget, the host address updates (nn-*), so the current view can be bookmarked or shared.
   With several widgets on one page, name them: data-name="plains" → nn-plains-state=SD.
   Turn off with data-deeplink="off". */
(() => {
  const ORIGIN = new URL(document.currentScript ? document.currentScript.src : 'https://nativenations.labs.trlibrary.com/embed.js').origin;
  const KEYS = ['id', 'state', 'region', 'alliance', 'people', 'visit', 'limit', 'height', 'q', 'filters', 'nation', 'boundaries', 'cessions'];
  const frames = {};
  const prefix = el => el.dataset.name ? `nn-${el.dataset.name}-` : 'nn-';
  document.querySelectorAll('[data-nativenations]:not([data-nn-ready])').forEach((el, i) => {
    el.dataset.nnReady = '1';
    const kind = ['card', 'list', 'map'].includes(el.dataset.nativenations) ? el.dataset.nativenations : 'list';
    const id = 'nn' + Date.now().toString(36) + i, qs = new URLSearchParams({frame: id});
    KEYS.forEach(k => el.dataset[k] && qs.set(k, el.dataset[k]));
    const deep = el.dataset.deeplink !== 'off';
    if (deep) {
      const host = new URLSearchParams(location.search), pre = prefix(el);
      KEYS.forEach(k => { if (host.has(pre + k)) qs.set(k, host.get(pre + k)); });
      qs.set('deeplink', '1');
    }
    const f = document.createElement('iframe');
    f.src = `${ORIGIN}/widgets/${kind}.html?${qs}`; f.title = 'Native Nations';
    f.loading = 'lazy'; f.style.cssText = `width:100%;border:0;display:block;height:${kind === 'map' ? (+el.dataset.height || 480) + 20 : 200}px`;
    el.append(f); frames[id] = {f, el, deep};
  });
  addEventListener('message', ev => {
    if (ev.origin !== ORIGIN || !ev.data || !ev.data.nativenations) return;
    const w = frames[ev.data.id]; if (!w) return;
    if (ev.data.height) w.f.style.height = Math.ceil(ev.data.height) + 'px';
    if (ev.data.view && w.deep) {
      const url = new URL(location.href), pre = prefix(w.el);
      KEYS.forEach(k => url.searchParams.delete(pre + k));
      Object.entries(ev.data.view).forEach(([k, v]) => { if (v && KEYS.includes(k)) url.searchParams.set(pre + k, v); });
      const next = url.pathname + (url.searchParams.toString() ? '?' + url.searchParams : '') + url.hash;
      if (next !== location.pathname + location.search + location.hash)
        history[ev.data.push ? 'pushState' : 'replaceState'](history.state, '', next);
    }
    if (ev.data.scrollTop) w.f.scrollIntoView({block: 'start', behavior: 'smooth'});
  });
  addEventListener('popstate', () => {
    Object.entries(frames).forEach(([id, w]) => {
      if (!w.deep) return;
      const host = new URLSearchParams(location.search), pre = prefix(w.el), view = {};
      KEYS.forEach(k => { if (host.has(pre + k)) view[k] = host.get(pre + k); });
      w.f.contentWindow.postMessage({nativenations: true, restore: view}, ORIGIN);
    });
  });
})();
