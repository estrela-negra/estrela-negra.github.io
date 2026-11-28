/* Google Analytics (via Google Tag Manager GTM-MTVFZH8K) com Consent Mode v2 e aviso de cookies (LGPD).
   Padrão: tudo negado; só ativa cookies de análise se a pessoa aceitar. A escolha fica no navegador. */
(function () {
  var K = "en_cookies", esc = null;
  try { esc = localStorage.getItem(K); } catch (e) {}
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: esc === "sim" ? "granted" : "denied", wait_for_update: 500 });
  gtag("js", new Date());
  (function (w, d, s, l, i) { w[l] = w[l] || []; w[l].push({ "gtm.start": new Date().getTime(), event: "gtm.js" }); var f = d.getElementsByTagName(s)[0], j = d.createElement(s); j.async = true; j.src = "https://www.googletagmanager.com/gtm.js?id=" + i; f.parentNode.insertBefore(j, f); })(window, document, "script", "dataLayer", "GTM-MTVFZH8K");
  if (esc) return;
  function aviso() {
    var raiz = (document.currentScript && document.currentScript.getAttribute("data-raiz")) || (document.querySelector("script[data-en-analytics]") || {}).getAttribute && document.querySelector("script[data-en-analytics]").getAttribute("data-raiz") || "/";
    var b = document.createElement("div"); b.className = "en-cookie";
    b.innerHTML = '<p>Usamos cookies de análise (Google Analytics) para saber quantas pessoas visitam o site e o que leem. Nada de anúncios. <a href="' + raiz + 'privacidade/">Saiba mais</a></p><div><button data-c="nao">Recusar</button><button data-c="sim">Aceitar</button></div>';
    b.addEventListener("click", function (e) { var c = e.target.getAttribute && e.target.getAttribute("data-c"); if (!c) return;
      try { localStorage.setItem(K, c); } catch (x) {}
      if (c === "sim") gtag("consent", "update", { analytics_storage: "granted" });
      b.remove(); });
    document.body.appendChild(b);
    var st = document.createElement("style");
    st.textContent = ".en-cookie{position:fixed;left:16px;right:16px;bottom:16px;z-index:999;max-width:560px;margin:0 auto;background:#0A090E;color:#F1EEE9;border:1px solid #25222D;border-radius:16px;padding:16px 18px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;font:14px/1.5 'Space Grotesk',sans-serif;box-shadow:0 10px 40px rgba(0,0,0,.4)}.en-cookie p{margin:0;flex:1 1 260px}.en-cookie a{color:#A88BFF}.en-cookie div{display:flex;gap:8px}.en-cookie button{border:1px solid #6F6B77;background:none;color:#F1EEE9;border-radius:99px;padding:9px 16px;font:600 12px 'Space Grotesk',sans-serif;letter-spacing:.12em;text-transform:uppercase;cursor:pointer}.en-cookie button[data-c=sim]{background:#8762F3;border-color:#8762F3}";
    document.head.appendChild(st);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", aviso); else aviso();
})();
