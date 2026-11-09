(() => {
  const form = document.getElementById('builder'), code = document.getElementById('code'), prev = document.getElementById('preview');
  const render = () => {
    const t = form.type.value, attrs = [`data-nativenations="${t}"`];
    if (t === 'card') { if (form.id.value) attrs.push(`data-id="${form.id.value}"`); }
    else { if (form.state.value) attrs.push(`data-state="${form.state.value}"`); if (form.alliance.value) attrs.push(`data-alliance="${form.alliance.value}"`); if (t === 'list' && form.limit.value) attrs.push(`data-limit="${form.limit.value}"`); }
    const html = `<div ${attrs.join(' ')}></div>\n<script src="https://nativenations.labs.trlibrary.com/embed.js" async><\/script>`;
    code.textContent = html;
    prev.innerHTML = `<div ${attrs.join(' ')}></div>`;
    const s = document.createElement('script'); s.src = '/embed.js'; prev.append(s);
  };
  form.addEventListener('input', render);
  document.getElementById('copy').addEventListener('click', e => { navigator.clipboard.writeText(code.textContent); e.target.textContent = 'Copied'; setTimeout(() => e.target.textContent = 'Copy code', 1500); });
  render();
})();
