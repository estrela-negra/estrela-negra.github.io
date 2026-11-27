/* Estrela Negra · comunidade: comentários por página + Discussões (estilo fórum).
   Login com Google via Firebase Auth; dados no Firestore. Só liga se assets/firebase-config.js tiver apiKey. */
(function () {
  var CFG = window.EN_FIREBASE || {};
  var ADMINS = CFG.admins || [];
  var raiz = document.currentScript ? document.currentScript.getAttribute("data-raiz") || "" : "";
  var alvoC = document.getElementById("en-comentarios"), alvoF = document.getElementById("en-forum");
  if (!alvoC && !alvoF) return;
  if (!CFG.apiKey) { [alvoC, alvoF].forEach(function (a) { if (a) a.innerHTML = '<p class="en-off">Os comentários abrem em breve.</p>'; }); return; }

  var V = "10.12.2", base = "https://www.gstatic.com/firebasejs/" + V + "/";
  function carrega(src) { return new Promise(function (ok, erro) { var s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = erro; document.head.appendChild(s); }); }
  carrega(base + "firebase-app-compat.js").then(function () { return Promise.all([carrega(base + "firebase-auth-compat.js"), carrega(base + "firebase-firestore-compat.js")]); }).then(inicia)
    .catch(function () { [alvoC, alvoF].forEach(function (a) { if (a) a.innerHTML = '<p class="en-off">Não foi possível carregar os comentários agora.</p>'; }); });

  var db, auth, eu = null;
  function esc(s) { return String(s || "").replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function quando(ts) { if (!ts || !ts.toDate) return "agora"; var d = ts.toDate(), s = (Date.now() - d) / 1000;
    if (s < 60) return "agora"; if (s < 3600) return Math.floor(s / 60) + " min"; if (s < 86400) return Math.floor(s / 3600) + " h"; if (s < 86400 * 7) return Math.floor(s / 86400) + " d";
    return d.toLocaleDateString("pt-BR"); }
  function admin() { return eu && ADMINS.indexOf(eu.uid) >= 0; }
  var ultimo = 0; function devagar() { if (Date.now() - ultimo < 20000) { alert("Espere alguns segundos antes de publicar de novo."); return true; } ultimo = Date.now(); return false; }
  var PROIB = /(https?:\/\/\S+){3,}/i;  /* mais de 2 links = provável spam */
  function barraLogin() {
    if (eu) return '<div class="en-eu"><img src="' + esc(eu.photoURL) + '" alt=""><span>' + esc(eu.displayName) + '</span><button class="en-lk" data-a="sair">Sair</button></div>';
    return '<button class="en-google" data-a="entrar"><span>G</span> Entrar com Google para participar</button>';
  }
  function entrar() { auth.signInWithPopup(new firebase.auth.GoogleAuthProvider()).catch(function (e) { if (e.code !== "auth/popup-closed-by-user") alert("Não deu para entrar: " + e.message); }); }
  function denunciar(caminho) { if (!eu) return entrar(); db.collection("denuncias").add({ alvo: caminho, uid: eu.uid, criado: firebase.firestore.FieldValue.serverTimestamp() }).then(function () { alert("Obrigado. A moderação vai olhar."); }); }

  function inicia() {
    firebase.initializeApp(CFG); auth = firebase.auth(); db = firebase.firestore();
    auth.onAuthStateChanged(function (u) { eu = u; if (alvoC) comentarios(alvoC, alvoC.getAttribute("data-pagina") || location.pathname); if (alvoF) forum(); });
    document.addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-a]"); if (!b) return; var a = b.getAttribute("data-a");
      if (a === "entrar") entrar(); else if (a === "sair") auth.signOut();
      else if (a === "denuncia") denunciar(b.getAttribute("data-c"));
      else if (a === "apaga") { if (confirm("Remover este conteúdo?")) db.doc(b.getAttribute("data-c")).update({ removido: true }); }
      else if (a === "responde") { var f = document.getElementById("en-r-" + b.getAttribute("data-id")); if (f) f.hidden = !f.hidden; }
      else if (a === "voto") votar(b.getAttribute("data-id"), +b.getAttribute("data-v"));
    });
  }

  /* ---------------- comentários de uma página ---------------- */
  var desliga = {};
  function comentarios(alvo, pagina, titulo) {
    if (desliga[pagina]) desliga[pagina]();
    alvo.innerHTML = '<section class="en-c"><h2 class="en-h">' + (titulo || 'Comentários') + ' <span class="en-n"></span></h2>' + barraLogin() +
      (eu ? formC("", pagina) : "") + '<div class="en-lista"><p class="en-off">Carregando…</p></div><p class="en-regras">Seja gentil e cite fontes quando falar de dados. <a href="' + raiz + 'privacidade/">Privacidade e regras</a></p></section>';
    ligaForm(alvo, pagina);
    desliga[pagina] = db.collection("comentarios").where("pagina", "==", pagina).orderBy("criado", "asc").limit(500).onSnapshot(function (snap) {
      var todos = []; snap.forEach(function (d) { var x = d.data(); x.id = d.id; if (!x.removido) todos.push(x); });
      alvo.querySelector(".en-n").textContent = todos.length ? "(" + todos.length + ")" : "";
      var raizes = todos.filter(function (x) { return !x.pai; });
      var html = raizes.map(function (c) { return itemC(c, pagina) + '<div class="en-resps">' + todos.filter(function (r) { return r.pai === c.id; }).map(function (r) { return itemC(r, pagina, true); }).join("") + "</div>"; }).join("");
      alvo.querySelector(".en-lista").innerHTML = html || '<p class="en-off">Ainda não tem comentários. Comece a conversa.</p>';
      ligaForm(alvo, pagina);
    }, function (e) { alvo.querySelector(".en-lista").innerHTML = '<p class="en-off">Erro ao carregar (' + esc(e.code) + ').</p>'; });
  }
  function formC(pai, pagina) { return '<form class="en-form" data-pai="' + pai + '" data-pagina="' + esc(pagina) + '"><textarea maxlength="2000" required placeholder="' + (pai ? "Escreva uma resposta" : "Escreva um comentário") + '"></textarea><button class="en-bt">Publicar</button></form>'; }
  function itemC(c, pagina, resp) {
    var dono = eu && eu.uid === c.uid;
    return '<div class="en-item' + (resp ? " en-resp" : "") + '"><img class="en-av" src="' + esc(c.foto) + '" alt=""><div class="en-corpo"><div class="en-meta"><b>' + esc(c.nome) + "</b> · " + quando(c.criado) + "</div><p>" + esc(c.texto).replace(/\n/g, "<br>") + '</p><div class="en-acoes">' +
      (eu && !resp ? '<button class="en-lk" data-a="responde" data-id="' + c.id + '">Responder</button>' : "") +
      '<button class="en-lk" data-a="denuncia" data-c="comentarios/' + c.id + '">Denunciar</button>' + (dono || admin() ? '<button class="en-lk" data-a="apaga" data-c="comentarios/' + c.id + '">Remover</button>' : "") + "</div>" +
      (eu && !resp ? '<div id="en-r-' + c.id + '" hidden>' + formC(c.id, pagina) + "</div>" : "") + "</div></div>";
  }
  function ligaForm(alvo, pagina) {
    alvo.querySelectorAll("form.en-form").forEach(function (f) {
      if (f._ok) return; f._ok = true;
      f.addEventListener("submit", function (ev) {
        ev.preventDefault(); var t = f.querySelector("textarea").value.trim(); if (!t || !eu) return;
        if (PROIB.test(t)) { alert("Muitos links num comentário só."); return; } if (devagar()) return;
        var pg = f.getAttribute("data-pagina");
        db.collection("comentarios").add({ pagina: pg, pai: f.getAttribute("data-pai") || null, texto: t.slice(0, 2000), uid: eu.uid, nome: eu.displayName || "Leitor", foto: eu.photoURL || "", criado: firebase.firestore.FieldValue.serverTimestamp(), removido: false })
          .then(function () { f.querySelector("textarea").value = "";
            if (pg.indexOf("topico/") === 0) db.doc("topicos/" + pg.slice(7)).update({ nresp: firebase.firestore.FieldValue.increment(1), ativo: firebase.firestore.FieldValue.serverTimestamp() }).catch(function () {}); })
          .catch(function (e) { alert("Não publicou: " + e.message); });
      });
    });
  }

  /* ---------------- Discussões ---------------- */
  var ordem = "quente", desligaF = null;
  function forum() {
    var id = new URLSearchParams(location.search).get("t");
    if (id) return topico(id);
    alvoF.innerHTML = '<div class="en-f">' + barraLogin() + (eu ? '<form class="en-novo"><input maxlength="140" required placeholder="Título da discussão"><textarea maxlength="5000" required placeholder="Sobre o que você quer conversar? Pergunta, notícia, foto que fez do céu…"></textarea><button class="en-bt">Abrir discussão</button></form>' : "") +
      '<div class="en-tabs"><button data-o="quente" class="' + (ordem === "quente" ? "on" : "") + '">Em alta</button><button data-o="novo" class="' + (ordem === "novo" ? "on" : "") + '">Novas</button><button data-o="top" class="' + (ordem === "top" ? "on" : "") + '">Mais votadas</button></div><div class="en-topicos"><p class="en-off">Carregando…</p></div></div>';
    alvoF.querySelectorAll(".en-tabs button").forEach(function (b) { b.onclick = function () { ordem = b.getAttribute("data-o"); forum(); }; });
    var nf = alvoF.querySelector(".en-novo");
    if (nf) nf.onsubmit = function (ev) { ev.preventDefault(); var ti = nf.querySelector("input").value.trim(), tx = nf.querySelector("textarea").value.trim(); if (!ti || !tx || devagar()) return; if (PROIB.test(tx)) { alert("Muitos links."); return; }
      db.collection("topicos").add({ titulo: ti.slice(0, 140), texto: tx.slice(0, 5000), uid: eu.uid, nome: eu.displayName || "Leitor", foto: eu.photoURL || "", criado: firebase.firestore.FieldValue.serverTimestamp(), ativo: firebase.firestore.FieldValue.serverTimestamp(), score: 0, nresp: 0, removido: false })
        .then(function (r) { location.search = "?t=" + r.id; }).catch(function (e) { alert("Não abriu: " + e.message); }); };
    if (desligaF) desligaF();
    var q = db.collection("topicos").orderBy(ordem === "novo" ? "criado" : ordem === "top" ? "score" : "ativo", "desc").limit(60);
    desligaF = q.onSnapshot(function (snap) {
      var L = []; snap.forEach(function (d) { var x = d.data(); x.id = d.id; if (!x.removido) L.push(x); });
      if (ordem === "quente") L.sort(function (a, b) { return calor(b) - calor(a); });
      alvoF.querySelector(".en-topicos").innerHTML = L.map(linhaT).join("") || '<p class="en-off">Nenhuma discussão ainda. Abra a primeira.</p>';
    }, function (e) { alvoF.querySelector(".en-topicos").innerHTML = '<p class="en-off">Erro ao carregar (' + esc(e.code) + ").</p>"; });
  }
  function calor(t) { var h = t.criado && t.criado.toDate ? (Date.now() - t.criado.toDate()) / 3600000 : 0; return ((t.score || 0) + (t.nresp || 0) * 0.5 + 1) / Math.pow(h + 2, 1.5); }
  function votos(t) { return '<div class="en-votos"><button data-a="voto" data-id="' + t.id + '" data-v="1" aria-label="Votar a favor">▲</button><b>' + (t.score || 0) + '</b><button data-a="voto" data-id="' + t.id + '" data-v="-1" aria-label="Votar contra">▼</button></div>'; }
  function linhaT(t) { return '<div class="en-top">' + votos(t) + '<a class="en-tl" href="?t=' + t.id + '"><b>' + esc(t.titulo) + '</b><span>' + esc(t.nome) + " · " + quando(t.criado) + " · " + (t.nresp || 0) + " respostas</span></a></div>"; }
  function topico(id) {
    db.doc("topicos/" + id).onSnapshot(function (d) {
      if (!d.exists || d.data().removido) { alvoF.innerHTML = '<p class="en-off">Discussão não encontrada. <a href="./">Voltar</a></p>'; return; }
      var t = d.data(); t.id = d.id; var dono = eu && eu.uid === t.uid;
      var cab = alvoF.querySelector(".en-tcab");
      var html = '<a class="en-lk" href="./">← Todas as discussões</a><div class="en-tcab">' + votos(t) + '<div><h1 class="en-tt">' + esc(t.titulo) + '</h1><div class="en-meta"><img class="en-av" src="' + esc(t.foto) + '" alt=""><b>' + esc(t.nome) + "</b> · " + quando(t.criado) + '</div><p class="en-tx">' + esc(t.texto).replace(/\n/g, "<br>") + '</p><div class="en-acoes"><button class="en-lk" data-a="denuncia" data-c="topicos/' + t.id + '">Denunciar</button>' + (dono || admin() ? '<button class="en-lk" data-a="apaga" data-c="topicos/' + t.id + '">Remover</button>' : "") + "</div></div></div>";
      if (!cab) { alvoF.innerHTML = '<div class="en-f">' + html + '<div id="en-tc"></div></div>'; comentarios(document.getElementById("en-tc"), "topico/" + id, "Respostas"); document.title = t.titulo + " · Discussões · Estrela Negra"; }
      else { cab.outerHTML = html.slice(html.indexOf('<div class="en-tcab">')); }
    });
  }
  function votar(id, v) {
    if (!eu) return entrar();
    var tref = db.doc("topicos/" + id), vref = db.doc("topicos/" + id + "/votos/" + eu.uid);
    db.runTransaction(function (tx) { return tx.get(vref).then(function (vd) { var antes = vd.exists ? vd.data().v : 0, novo = antes === v ? 0 : v;
      tx.set(vref, { v: novo }); tx.update(tref, { score: firebase.firestore.FieldValue.increment(novo - antes) }); }); }).catch(function (e) { alert("Voto não registrado: " + e.message); });
  }
})();
