/* Big numbers da página Sobre. YouTube: ao vivo pela YouTube Data API (chave restrita ao domínio do site e só a essa API),
   com cache de 6 h no navegador. Instagram/TikTok: dados/redes.json (manual). */
(function () {
  var KEY = "AIzaSyC1ev_Js3YZKMuZqpwT_fv1DYek2vs5PzY", CANAL = "UCECuIRqWbwWHO8vNaTPQAfQ";
  var alvo = document.getElementById("en-numeros"); if (!alvo) return;
  var raiz = alvo.getAttribute("data-raiz") || "../";
  function fmt(n) { n = +n; if (n >= 1e6) return (n / 1e6).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " mi"; if (n >= 1e4) return (n / 1e3).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " mil"; return n.toLocaleString("pt-BR"); }
  function conta(el, fim) { var t0 = null; function p(t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / 1400); k = 1 - Math.pow(1 - k, 3); el.textContent = fmt(Math.round(fim * k)); if (k < 1) requestAnimationFrame(p); } requestAnimationFrame(p); }
  function card(rotulo, valor, sub) { return '<div class="en-num"><b data-v="' + valor + '">0</b><span>' + rotulo + "</span>" + (sub ? "<i>" + sub + "</i>" : "") + "</div>"; }
  function youtube() {
    try { var c = JSON.parse(localStorage.getItem("en_yt") || "null"); if (c && Date.now() - c.t < 6 * 3600e3) return Promise.resolve(c.s); } catch (e) {}
    return fetch("https://www.googleapis.com/youtube/v3/channels?part=statistics&id=" + CANAL + "&key=" + KEY).then(function (r) { return r.json(); })
      .then(function (j) { var s = j.items && j.items[0] && j.items[0].statistics; if (!s) throw 0; try { localStorage.setItem("en_yt", JSON.stringify({ t: Date.now(), s: s })); } catch (e) {} return s; });
  }
  Promise.all([youtube().catch(function () { return null; }), fetch(raiz + "dados/redes.json", { cache: "no-store" }).then(function (r) { return r.json(); }).catch(function () { return {}; })]).then(function (r) {
    var yt = r[0], rd = r[1] || {}, h = "";
    if (yt) { h += card("visualizações no YouTube", yt.viewCount) + card("inscritos no YouTube", yt.subscriberCount) + card("vídeos publicados", yt.videoCount); }
    [["instagram", "Instagram"], ["tiktok", "TikTok"]].forEach(function (p) { var d = rd[p[0]]; if (!d) return;
      if (d.visualizacoes) h += card("visualizações no " + p[1], d.visualizacoes, d.data ? "em " + d.data : "");
      if (d.seguidores) h += card("seguidores no " + p[1], d.seguidores, d.data ? "em " + d.data : ""); });
    if (!h) { alvo.parentNode.style.display = "none"; return; }
    alvo.innerHTML = h;
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { conta(e.target, +e.target.getAttribute("data-v")); io.unobserve(e.target); } }); }, { threshold: 0.4 });
    alvo.querySelectorAll("b[data-v]").forEach(function (b) { io.observe(b); });
  });
})();
