(function () {
  var d = document, state = { last: null }, eng = null, busy = false;
  var thread = d.getElementById("thread"), form = d.getElementById("askf"), input = d.getElementById("askq"), starts = d.getElementById("starts");
  function el(t, c, x) { var e = d.createElement(t); if (c) e.className = c; if (x) e.textContent = x; return e; }
  var RX = /(arXiv:\d{4}\.\d{5})|(https?:\/\/[^\s)\]>,;]+)|([\w.+-]+@[\w-]+(?:\.[\w-]+)+)|((?<![\w.\-])~?\d(?:[\d,]*\d)?(?:\.\d+)?(?:-\d+(?:\.\d+)?)?(?:%|[BMK](?![A-Za-z]))?)/g;
  function rich(p, text) {             // bold every metric, link arXiv ids / URLs / emails; text nodes only, no innerHTML
    var pos = 0, m;
    RX.lastIndex = 0;
    while ((m = RX.exec(text))) {
      if (m.index > pos) p.appendChild(d.createTextNode(text.slice(pos, m.index)));
      var tok = m[0], node;
      if (m[1]) { node = el("a", "ln", tok); node.href = "https://arxiv.org/abs/" + tok.slice(6); }
      else if (m[2]) { node = el("a", "ln", tok); node.href = tok; }
      else if (m[3]) { node = el("a", "ln", tok); node.href = "mailto:" + tok; }
      else if (/^(19|20)\d\d$/.test(tok.replace("~", ""))) node = d.createTextNode(tok);
      else node = el("strong", "n", tok);
      if (node.tagName === "A") { node.target = "_blank"; node.rel = "noopener noreferrer"; }
      p.appendChild(node); pos = m.index + tok.length;
    }
    if (pos < text.length) p.appendChild(d.createTextNode(text.slice(pos)));
    return p;
  }
  function scroll() { thread.scrollTop = thread.scrollHeight; }
  function say(role, node) { var m = el("div", "am " + role); m.appendChild(node); thread.appendChild(m); scroll(); return m; }
  function chips(list, into) {
    var w = el("div", "chs");
    list.slice(0, 4).forEach(function (q) { var b = el("button", "", q); b.type = "button"; b.onclick = function () { ask(q); }; w.appendChild(b); });
    into.appendChild(w);
  }
  function render(r) {
    var box = el("div", "abx");
    if (r.section) {
      var meta = el("div", "mt"); meta.appendChild(el("b", "", r.section));
      meta.appendChild(el("span", "", r.type === "answer" ? "cosine " + r.score.toFixed(2) + " · " + r.how : r.how || "keyword"));
      box.appendChild(meta);
    } else if (r.how) { box.appendChild(el("div", "mt")).appendChild(el("span", "", r.how)); }
    if (r.meta) {      // the section metadata the match used: organisation, year, topics, tools
      var tg = el("div", "tg2"), bits = [r.meta.org, r.meta.year].concat((r.meta.domains || []).map(function (x) { return "domain: " + x; }), (r.meta.topics || []).slice(0, 3), (r.meta.tech || []).slice(0, 3));
      bits.filter(Boolean).forEach(function (t) { tg.appendChild(el("span", "", t)); });
      box.appendChild(tg);
    }
    if (r.lead) box.appendChild(rich(el("p", "ld"), r.lead));
    var ul = el("ul", "ls");
    (r.lines || []).forEach(function (t, i) { var li = el("li"); rich(li, t); li.style.setProperty("--i", i); ul.appendChild(li); });
    box.appendChild(ul);
    if (r.links && r.links.length) {
      var lk = el("div", "lks");
      r.links.forEach(function (x) { var a = el("a", "", x.label + " ↗"); a.href = x.href; a.target = "_blank"; a.rel = "noopener noreferrer"; lk.appendChild(a); });
      box.appendChild(lk);
    }
    if (r.source) { var dt = el("details", "src"); dt.appendChild(el("summary", "", "Source line, quoted from my record")); rich(dt.appendChild(el("p")), r.source); box.appendChild(dt); }
    if (r.suggestions) chips(r.suggestions, box);
    return box;
  }
  function ask(q) {
    q = (q || "").trim();
    if (!q || !eng || busy) return;
    busy = true; input.value = "";
    say("u", el("p", "", q));
    var r = eng.answer(q, state);
    var m = say("b", render(r));
    if (r.sectionId) state.last = r.sectionId;
    busy = false; scroll(); input.focus();
  }
  form.onsubmit = function (e) { e.preventDefault(); ask(input.value); };
  fetch("ask-data.json").then(function (r) { return r.json(); }).then(function (data) {
    eng = AskEngine.build(data);
    chips(data.starters.concat(["What awards has he won?"]), starts);
    say("b", render({ type: "greeting", lines: [data.greeting], suggestions: null }));
    var q = new URLSearchParams(location.search).get("q"); if (q) ask(q);
  }).catch(function () { say("b", el("p", "", "I couldn’t load the record. Please refresh the page.")); });
})();
