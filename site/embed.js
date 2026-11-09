/* Native Nations embed loader. Usage:
   <div data-nativenations="list" data-state="ND"></div>
   <script src="https://nativenations.labs.trlibrary.com/embed.js" async></script> */
(() => {
  const ORIGIN = new URL(document.currentScript ? document.currentScript.src : 'https://nativenations.labs.trlibrary.com/embed.js').origin;
  const KEYS = ['id', 'state', 'region', 'alliance', 'visit', 'limit', 'height', 'q'];
  const frames = {};
  document.querySelectorAll('[data-nativenations]:not([data-nn-ready])').forEach((el, i) => {
    el.dataset.nnReady = '1';
    const kind = ['card', 'list', 'map'].includes(el.dataset.nativenations) ? el.dataset.nativenations : 'list';
    const id = 'nn' + Date.now().toString(36) + i, qs = new URLSearchParams({frame: id});
    KEYS.forEach(k => el.dataset[k] && qs.set(k, el.dataset[k]));
    const f = document.createElement('iframe');
    f.src = `${ORIGIN}/widgets/${kind}.html?${qs}`; f.title = 'Native Nations';
    f.loading = 'lazy'; f.style.cssText = `width:100%;border:0;display:block;height:${kind === 'map' ? (+el.dataset.height || 480) + 20 : 200}px`;
    el.append(f); frames[id] = f;
  });
  addEventListener('message', ev => {
    if (ev.origin !== ORIGIN || !ev.data || !ev.data.nativenations) return;
    const f = frames[ev.data.id]; if (f) f.style.height = Math.ceil(ev.data.height) + 'px';
  });
})();
