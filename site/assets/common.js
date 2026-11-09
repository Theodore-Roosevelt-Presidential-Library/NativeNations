/* Shared helpers for Native Nations pages and widgets */
window.NN = (() => {
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const STATES = {AK:"Alaska",AL:"Alabama",AZ:"Arizona",CA:"California",CO:"Colorado",CT:"Connecticut",FL:"Florida",IA:"Iowa",ID:"Idaho",IN:"Indiana",KS:"Kansas",LA:"Louisiana",MA:"Massachusetts",ME:"Maine",MI:"Michigan",MN:"Minnesota",MO:"Missouri",MS:"Mississippi",MT:"Montana",NC:"North Carolina",ND:"North Dakota",NE:"Nebraska",NM:"New Mexico",NV:"Nevada",NY:"New York",OK:"Oklahoma",OR:"Oregon",RI:"Rhode Island",SC:"South Carolina",SD:"South Dakota",TX:"Texas",UT:"Utah",VA:"Virginia",WA:"Washington",WI:"Wisconsin",WY:"Wyoming"};
  let cache;
  const load = async () => cache ||= (await fetch('/api/v1/index.json')).json();
  const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const filter = (all, f) => {
    const q = norm(f.q).trim(), states = (f.state || '').split(',').filter(Boolean);
    return all.filter(n =>
      (!q || norm([n.name, n.town, ...n.aka, ...n.former, ...n.states.map(s => STATES[s])].join(' ')).includes(q)) &&
      (!states.length || n.states.some(s => states.includes(s))) &&
      (!f.region || n.region === f.region) &&
      (!f.alliance || n.alliances.includes(f.alliance)) &&
      (!f.visit || n.visit));
  };
  const where = n => [n.town, n.states.map(s => STATES[s] || s).join(', ')].filter(Boolean).join(' · ');
  const card = (n, target) => `<article class="card${n.visit ? ' has-links' : ''}">
    <h3><a href="/nations/${n.id}/"${target ? ' target="_blank" rel="noopener"' : ''}>${esc(n.name)}</a></h3>
    <div class="where">${esc(where(n))}</div>
    ${n.visit ? '<div><span class="pill">Tourism links</span></div>' : ''}
    <div class="more"><a href="/nations/${n.id}/"${target ? ' target="_blank" rel="noopener"' : ''}>Plan your visit &rsaquo;</a></div></article>`;
  const params = () => Object.fromEntries(new URLSearchParams(location.search));
  return {esc, STATES, load, filter, card, where, params};
})();
