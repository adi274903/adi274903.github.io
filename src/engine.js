/* Deterministic Q&A over a chunked record: TF-IDF vectors + cosine similarity. No model, no network after the
   data file loads. Same input -> same output. Works in the browser (window.AskEngine) and in node (module.exports). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AskEngine = factory();
})(typeof self !== "undefined" ? self : this, function () {
  var STOP = new Set(("a an and are as at be been but by can did do does for from had has have he his him how i in is it its me my of on or our so than that the their them then there these they this to was were what when where which who whom why will with would you your about any also into just not out over such very".split(" ")));

  function stem(w) {
    if (/^\d/.test(w)) return w;
    if (w.length > 4 && w.endsWith("ies")) return w.slice(0, -3) + "y";
    if (w.length > 5 && w.endsWith("ing")) return w.slice(0, -3);
    if (w.length > 4 && w.endsWith("ed")) return w.slice(0, -2);
    if (w.length > 4 && w.endsWith("es")) return w.slice(0, -2);
    if (w.length > 3 && w.endsWith("s") && !w.endsWith("ss")) return w.slice(0, -1);
    return w;
  }
  function tokens(t) {
    var m = t.toLowerCase().replace(/[’']/g, "").match(/[a-z0-9]+(?:\.[0-9]+)?/g) || [];
    return m.filter(function (w) { return !STOP.has(w); }).map(stem);
  }
  // authored routing synonyms (question word -> words the record actually uses); metadata only, never shown as facts
  var SYN = { train: ["pretrain", "dora"], built: ["architect", "deliver"], build: ["architect", "deliver"], made: ["architect", "deliver"],
              improve: ["raise", "cut", "reduce", "outscore"], faster: ["cut", "reduce"], speed: ["cut", "second"], accuracy: ["raise", "accurate"],
              studied: ["degree", "university"], job: ["role", "intern"], worked: ["role", "intern"], used: ["pgvector", "qdrant", "pytorch"] };
  function expand(toks) { var out = toks.slice(); toks.forEach(function (t) { if (SYN[t]) out = out.concat(SYN[t]); }); return out; }
  function vec(toks, idf) {            // log-scaled tf * idf, L2-normalised sparse vector
    var tf = {}, v = {}, n = 0, k;
    toks.forEach(function (t) { tf[t] = (tf[t] || 0) + 1; });
    for (k in tf) { if (idf[k] !== undefined) { v[k] = (1 + Math.log(tf[k])) * idf[k]; n += v[k] * v[k]; } }
    n = Math.sqrt(n) || 1;
    for (k in v) v[k] /= n;
    return v;
  }
  function cos(a, b) { var s = 0, k; for (k in a) if (b[k] !== undefined) s += a[k] * b[k]; return s; }
  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  var OFFTOPIC = /\b(write|generate|create|build|debug|fix|implement|explain|translate|draft)\b.{0,40}\b(code|function|script|program|app|class|regex|query|poem|story|essay|joke|song)\b|\b(my code|my script|leetcode|homework|weather|stock price|recipe|tell me a joke|a poem)\b|\b(ignore|forget)\b.{0,30}\b(instructions|rules|prompt)\b|\bsystem prompt\b/i;
  var CONTACT = /\b(contact|e-?mail|linkedin|github|phone number|relocat\w*|hire|hiring|get in touch|portfolio site)\b|\bopen to (moving|relocat\w*|new)\b|\breach (out|him|aditya|you)\b|\bhow (do|can) i reach\b/i;
  var GREET = /^\s*(hi|hello|hey|yo|good (morning|afternoon|evening)|howdy)\b/i;
  var THANKS = /\b(thanks|thank you|cheers|great|awesome|nice)\b\s*[.!]*\s*$/i;
  var HOWMUCH = /\b(how (much|many|fast|accurate|good|well)|what (was|is|were) the .{0,30}(score|result|f1|accuracy|improvement|time|speed|number|rate|metric)|by how much|what (score|f1|accuracy|number|percent)|percent|measured|metric|result)\b/i;
  var DESCRIBE = /\b(what (did|does|has) (he|aditya)\b.{0,25}\b(do|done|build|built|work|contribute|achieve)|tell me about|describe|walk me through|summari[sz]e|overview|exactly|what is .{0,40} about|what did .{0,30} do)\b/i;

  function strip(chunk) {              // drop the "Org, Role (dates): " prefix so the answer starts at the substance
    var m = chunk.match(/^[^:]{0,140}?\):\s+/);
    return m ? chunk.slice(m[0].length) : chunk;
  }

  function build(data) {
    var N = 0, df = {}, secs = [], i, j;
    data.sections.forEach(function (s) {
      var sec = { s: s, chunkToks: s.chunks.map(tokens), sectionToks: [] };
      var head = tokens(s.title + " " + s.desc + " " + s.asks.join(" "));
      var al = []; s.aliases.forEach(function (a) { tokens(a).forEach(function (t) { al.push(t, t, t); }); });
      sec.sectionToks = head.concat(al);
      sec.chunkToks.forEach(function (t) { sec.sectionToks = sec.sectionToks.concat(t); });
      secs.push(sec);
    });
    secs.forEach(function (sec) {       // idf over every chunk and section document
      sec.chunkToks.concat([sec.sectionToks]).forEach(function (toks) {
        N++; var seen = {};
        toks.forEach(function (t) { if (!seen[t]) { seen[t] = 1; df[t] = (df[t] || 0) + 1; } });
      });
    });
    var idf = {}, k;
    for (k in df) idf[k] = Math.log((N + 1) / (df[k] + 1)) + 1;
    secs.forEach(function (sec) {
      sec.sv = vec(sec.sectionToks, idf);
      sec.cv = sec.chunkToks.map(function (t) { return vec(t, idf); });
      sec.aliasRx = sec.s.aliases.map(function (a) { var rx = new RegExp("(^|[^a-z0-9])" + esc(a.toLowerCase()) + "s?($|[^a-z0-9])"); rx.w = 1 + 0.5 * (a.trim().split(/\s+/).length - 1); return rx; });
    });
    var byId = {}; secs.forEach(function (sec) { byId[sec.s.id] = sec; });

    function route(q, qv, state) {
      var ql = q.toLowerCase(), best = null, bs = -1, hits = {};
      secs.forEach(function (sec) {
        var h = 0; sec.aliasRx.forEach(function (rx) { if (rx.test(ql)) h += rx.w; });
        var sc = cos(qv, sec.sv);
        hits[sec.s.id] = h;
        var total = sc + Math.min(h, 3) * 0.35;
        if (total > bs) { bs = total; best = sec; }
      });
      var hasHit = hits[best.s.id] > 0;
      if (hasHit || bs >= 0.30) return { sec: best, score: cos(qv, best.sv), how: hasHit ? "name match + cosine" : "cosine" };
      if (state && state.last && tokens(q).length <= 9) return { sec: byId[state.last], score: cos(qv, byId[state.last].sv), how: "follow-up" };
      return null;
    }

    function answer(q, state) {
      state = state || {};
      q = (q || "").trim();
      if (!q) return null;
      if (GREET.test(q) && q.length < 40) return { type: "greeting", lines: [data.greeting], suggestions: data.starters };
      if (OFFTOPIC.test(q)) return { type: "decline", lines: [data.decline], suggestions: data.starters, how: "off-topic rule" };
      if (CONTACT.test(q)) return { type: "contact", lead: "Here is how to reach Aditya.", lines: [data.contact.reply], links: data.contact.links, suggestions: data.starters, section: "Contact", score: 1, how: "keyword" };
      if (THANKS.test(q) && q.length < 40) return { type: "thanks", lines: ["Happy to help. Ask me about any project, result or role."], suggestions: data.starters };
      var qv = vec(expand(tokens(q)), idf), r = route(q, qv, state);
      if (!r) return { type: "decline", lines: [data.decline], suggestions: data.starters, how: "no section matched" };
      var sec = r.sec, s = sec.s, ranked = sec.cv.map(function (v, idx) { return [cos(qv, v), idx]; }).sort(function (a, b) { return b[0] - a[0] || a[1] - b[1]; });
      var out = { type: "answer", section: s.title, sectionId: s.id, score: Math.round(r.score * 100) / 100, how: r.how, links: s.links || [], suggestions: s.asks, sourceIdx: ranked[0][1] };
      var list = !!s.list, isResult = function (t) { return /^Result - /.test(t); };
      if (!HOWMUCH.test(q) && !list) { var nr = ranked.filter(function (x) { return !isResult(s.chunks[x[1]]); }); if (nr.length) ranked = nr; }
      if (list) {
        out.lead = "Here is " + s.title.toLowerCase() + ":";
        out.lines = s.chunks.map(function (c) { return c.replace(/^(Recognition|Publication|Education|Skills - )[: ]*/, ""); });
        out.source = null;
      } else if (HOWMUCH.test(q) && s.chunks.some(isResult)) {
        var res = ranked.filter(function (x) { return isResult(s.chunks[x[1]]); })[0];
        out.lead = "Here is the number for " + s.title + ":";
        out.lines = [s.chunks[res[1]].replace(/^Result - /, "")];
        out.source = s.chunks[res[1]];
      } else if (DESCRIBE.test(q) || r.how === "follow-up") {
        var pick = ranked.filter(function (x) { return !isResult(s.chunks[x[1]]); }).slice(0, 2);
        out.lead = "Here is what Aditya did in " + s.title + ":";
        out.lines = pick.map(function (x) { return strip(s.chunks[x[1]]); });
        out.source = s.chunks[pick[0][1]];
      } else {
        var top = ranked[0][1];
        out.lead = "From " + s.title + ":";
        out.lines = [strip(s.chunks[top])];
        out.source = s.chunks[top];
      }
      return out;
    }
    return { answer: answer, sections: data.sections.map(function (x) { return x.id; }), tokens: tokens };
  }
  return { build: build, tokens: tokens };
});
