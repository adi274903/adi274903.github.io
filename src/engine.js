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
  function vec(toks, idf, query) {     // log-scaled tf * idf, L2-normalised sparse vector
    var tf = {}, v = {}, n = 0, k, top = query ? Math.max.apply(null, Object.keys(idf).map(function (x) { return idf[x]; })) : 0;
    toks.forEach(function (t) { tf[t] = (tf[t] || 0) + 1; });
    for (k in tf) {
      if (idf[k] !== undefined) { v[k] = (1 + Math.log(tf[k])) * idf[k]; n += v[k] * v[k]; }
      else if (query) { var u = (1 + Math.log(tf[k])) * top; n += u * u; }      // words the record never uses still count against the match
    }
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

  var ROLEFIT = /\b(fit|fits|fitting|suit|suits|suitable|relevant|best for|good for|right for|which (project|work|experience)|what (project|work|experience))\b/i;
  var LISTQ = /\b(which|any|list|show|every|all)\b.{0,40}\b(projects?|work|experience|roles?|research)\b|\bwhat (projects?|work|experience)\b|\b(fit|fits|relevant|suit|suits|involve|involves|involving|related to|focused on|touch|touches)\b/i;
  var HELP = /\b(how (can|could|would) (he|aditya) (help|fit|contribute|add)|what can (he|aditya) do for|why (hire|should (i|we))|help me|can (he|aditya) help|value (he|aditya) (brings|adds))\b/i;
  var EXPER = /\b(experience|experiences|background|career|work history|track record|what (has|have) (he|aditya) done|where has (he|aditya) worked|resume|cv)\b|\b(roles?|positions?|jobs?)\b.{0,25}\b(held|had|has|have)\b/i;
  var YEARS = /\b(how (many|long)\b.{0,25}\b(years?|months?)|years? of (experience|work)|how (much|long)\b.{0,25}\bexperience|how long (has|have|did) (he|aditya) (worked|been)|how experienced|seniority|statistics|stats|by the numbers|in numbers)\b/i;
  var SUPER = /\b(strongest|best|proudest|most impressive|top|favou?rite|flagship|biggest)\b.{0,25}\b(project|work|result|achievement|win)\b/i;
  var ALLPROJ = /\b(what|which|list|show|give me)\b.{0,25}\b(projects?|work)\b/i;
  var YESNO = /\b(has|have|does|did|is|can) (he|aditya)\b.{0,50}\b(used|worked|built|done|experience|know|with|fine-?tuned|published|led)\b|\bany experience\b|\bexperience (with|in)\b/i;
  var TYPOS = { waht: "what", whta: "what", hwo: "how", hsi: "his", teh: "the", adn: "and", abotu: "about", whn: "when", wat: "what", knwo: "know", hs: "has" };
  var NOLIST = {papers: 1, honors: 1, education: 1, skills: 1, overview: 1};

  function strip(chunk) {              // drop the "Org, Role (dates): " prefix so the answer starts at the substance
    var m = chunk.match(/^[^:]{0,140}?\):\s+/);
    return m ? chunk.slice(m[0].length) : chunk;
  }

  function near(a, b) {                 // edit distance <= 1 (substitution, insertion, deletion, adjacent swap)
    if (a === b) return true;
    var la = a.length, lb = b.length;
    if (Math.abs(la - lb) > 1) return false;
    var i = 0; while (i < la && i < lb && a[i] === b[i]) i++;
    if (la === lb) { if (a.slice(i + 1) === b.slice(i + 1)) return true; return a[i] === b[i + 1] && a[i + 1] === b[i] && a.slice(i + 2) === b.slice(i + 2); }
    return la > lb ? a.slice(i + 1) === b.slice(i) : b.slice(i + 1) === a.slice(i);
  }

  function build(data) {
    var N = 0, df = {}, secs = [], i, j;
    data.sections.forEach(function (s) {
      var sec = { s: s, chunkToks: s.chunks.map(tokens), sectionToks: [] };
      var head = tokens(s.title + " " + s.desc + " " + s.asks.join(" "));
      var al = []; s.aliases.forEach(function (a) { tokens(a).forEach(function (t) { al.push(t, t, t); }); });
      // metadata tokens: project, organisation, kind, year, domains (+ their words), topics (+ their words), tools
      var m = s.meta || {}, F = data.facets || { domain: {}, topic: {} }, mt = [m.project, m.org, m.kind, m.year];
      (m.domains || []).forEach(function (d) { mt.push(d); (F.domain[d] || []).forEach(function (w) { mt.push(w); }); });
      (m.topics || []).forEach(function (t) { mt.push(t); (F.topic[t] || []).forEach(function (w) { mt.push(w); }); });
      (m.tech || []).forEach(function (t) { mt.push(t); });
      sec.metaToks = tokens(mt.join(" "));
      sec.chunkToks = sec.chunkToks.map(function (t) { return t.concat(sec.metaToks); });   // every line knows its project and topics
      sec.sectionToks = head.concat(al, sec.metaToks, sec.metaToks);
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
      sec.av = sec.s.asks.map(function (a) { return vec(expand(tokens(a)), idf); });   // the section's own example questions
      sec.aliasRx = sec.s.aliases.map(function (a) { var rx = new RegExp("(^|[^a-z0-9])" + esc(a.toLowerCase()) + "s?($|[^a-z0-9])"); rx.w = 1 + 0.5 * (a.trim().split(/\s+/).length - 1); return rx; });
    });
    var byId = {}; secs.forEach(function (sec) { byId[sec.s.id] = sec; });
    // typo correction targets a CONTROLLED keyword list only: project titles, tool and skill names, facet words and
    // intent words. Never the free text of the lines, or "president" would become "resident" and "moving" become "mowing".
    var rawVocab = {};
    var INTENT_WORDS = "experience background career projects project education degree university research relocation relocate published papers skills contact resume startup internship interview summary overview achievements awards".split(" ");
    var kw = INTENT_WORDS.slice();
    data.sections.forEach(function (sec) {          // distinctive names only: titles, tools, skill names; not ordinary-word aliases like "resident"
      kw = kw.concat([sec.title, (sec.meta || {}).project || ""], (sec.meta || {}).tech || []);
      if (sec.id === "get_skills") kw = kw.concat(sec.aliases);
    });
    ["domain", "topic", "kind"].forEach(function (g) { Object.keys((data.facets || {})[g] || {}).forEach(function (k) { kw = kw.concat([k], data.facets[g][k]); }); });
    (kw.join(" ").toLowerCase().match(/[a-z]{5,}/g) || []).forEach(function (w) { rawVocab[w] = 1; });
    var rawList = Object.keys(rawVocab).sort();
    function fixTypos(q) {                // "experiance" -> "experience"; only words the record never uses are touched
      q = q.replace(/\b[A-Za-z]{2,4}\b/g, function (w) { return TYPOS[w.toLowerCase()] || w; });
      return q.replace(/[A-Za-z]{5,}/g, function (w) {
        var lw = w.toLowerCase();
        if (rawVocab[lw] || STOP.has(lw)) return w;
        for (var i = 0; i < rawList.length; i++) if (near(lw, rawList[i])) return rawList[i];
        return w;
      });
    }
    var FAC = data.facets || { domain: {}, topic: {}, kind: {} }, facetRx = { domain: {}, topic: {}, kind: {} };
    FAC.kind = FAC.kind || {};
    ["domain", "topic", "kind"].forEach(function (kind) {
      Object.keys(FAC[kind]).forEach(function (key) {
        facetRx[kind][key] = new RegExp("(^|[^a-z0-9])(" + FAC[kind][key].concat([key]).map(esc).join("|") + ")s?($|[^a-z0-9])", "i");
      });
    });
    var DOMAIN_LABEL = { fintech: "Fintech", health: "Healthtech", ai: "AI engineer" };
    function facets(q) {
      var f = { domain: [], topic: [], kind: [] };
      ["domain", "topic", "kind"].forEach(function (kind) { Object.keys(facetRx[kind]).forEach(function (k) { if (facetRx[kind][k].test(q)) f[kind].push(k); }); });
      return f;
    }
    function listByFacets(q, f, qv) {      // sections whose metadata matches every detected facet group, best cosine first
      var rows = secs.filter(function (sec) {
        var m = sec.s.meta || {};
        if (NOLIST[m.kind] && !f.kind.length) return false;
        var okD = !f.domain.length || f.domain.some(function (d) { return (m.domains || []).indexOf(d) > -1; });
        var okT = !f.topic.length || f.topic.some(function (t) { return (m.topics || []).indexOf(t) > -1; });
        var okK = !f.kind.length || f.kind.indexOf(m.kind) > -1;
        return okD && okT && okK;
      }).map(function (sec) { return [cos(qv, sec.sv), sec]; }).sort(function (a, b) { return b[0] - a[0] || (a[1].s.id < b[1].s.id ? -1 : 1); }).slice(0, 10);
      var labels = f.domain.map(function (d) { return DOMAIN_LABEL[d] || d; }).concat(f.topic, f.kind);
      return {
        type: "tracks", section: "Metadata match: " + labels.join(" + "), how: "metadata filter + cosine", score: 1,
        lead: rows.length ? "Projects and roles tagged " + labels.join(" and ") + ":" : "I have nothing tagged " + labels.join(" and ") + ".",
        lines: rows.map(function (r) { var m = r[1].s.meta, h = m.headline; return m.project + ": " + (h ? h.metric + " (" + h.note + ")" : strip(r[1].s.chunks[0]).slice(0, 110)); }),
        links: rows.filter(function (r) { return r[1].s.meta.headline; }).map(function (r) { return { label: r[1].s.meta.project, href: r[1].s.meta.headline.href }; }),
        suggestions: data.starters
      };
    }

    function route(q, qv, state) {
      var ql = q.toLowerCase(), best = null, bs = -1, hits = {};
      secs.forEach(function (sec) {
        var h = 0; sec.aliasRx.forEach(function (rx) { if (rx.test(ql)) h += rx.w; });
        var sc = cos(qv, sec.sv);
        sec.av.forEach(function (a) { var c = cos(qv, a); if (c >= 0.55) sc = Math.max(sc, 0.9 * c); });
        hits[sec.s.id] = h;
        var total = sc + Math.min(h, 3) * 0.35;
        if (total > bs) { bs = total; best = sec; }
      });
      var hasHit = hits[best.s.id] > 0;
      if (hasHit || bs >= 0.30) return { sec: best, score: Math.max(cos(qv, best.sv), best.av.reduce(function (m, a) { var c = cos(qv, a); return c >= 0.55 ? Math.max(m, 0.9 * c) : m; }, 0)), how: hasHit ? "name match + cosine" : "cosine" };
      if (state && state.last && tokens(q).length <= 9) return { sec: byId[state.last], score: cos(qv, byId[state.last].sv), how: "follow-up" };
      return null;
    }

    function answerOne(q, state) {
      state = state || {};
      q = fixTypos((q || "").trim());
      if (!q) return null;
      if (GREET.test(q) && q.length < 40) return { type: "greeting", lines: [data.greeting], suggestions: data.starters };
      if (OFFTOPIC.test(q)) return { type: "decline", lines: [data.decline], suggestions: data.starters, how: "off-topic rule" };

      var fq0 = facets(q), noFacet = !fq0.domain.length && !fq0.topic.length && !(fq0.kind || []).length;
      var namedAny = secs.some(function (sec) { return sec.aliasRx.some(function (rx) { return rx.test(q.toLowerCase()); }); });
      if (HELP.test(q) && data.tracks) {
        var T = data.tracks;
        return { type: "tracks", section: "How Aditya can help", how: "role tags", score: 1,
          lead: "Here is where Aditya can help, by kind of role:",
          lines: ["fintech", "health", "ai"].map(function (k) { return T[k].label + ": " + T[k].items.slice(0, 2).map(function (x) { return x.title + " (" + x.metric + ")"; }).join("; "); }),
          links: [{ label: "Book a chat", href: "contact.html" }, { label: "See all work", href: "index.html#work" }],
          suggestions: ["Which project fits a fintech role?", "Tell me about his healthcare experience", "What is his experience?"] };
      }
      if (SUPER.test(q) || (ALLPROJ.test(q) && noFacet && !namedAny && !ROLEFIT.test(q))) {
        var hl = secs.filter(function (sec) { return sec.s.meta && sec.s.meta.headline; });
        return { type: "tracks", section: "Projects", how: "headline results", score: 1,
          lead: SUPER.test(q) ? "I would let the numbers speak. Here are the headline results:" : "Here are the projects with their headline results:",
          lines: hl.map(function (sec) { var m = sec.s.meta; return m.project + ": " + m.headline.metric + " (" + m.headline.note + ")"; }),
          links: hl.map(function (sec) { return { label: sec.s.meta.project, href: sec.s.meta.headline.href }; }).slice(0, 8),
          suggestions: ["Which project fits a fintech role?", "Tell me about his healthcare experience", "What is his experience?"] };
      }
      if (noFacet && ((EXPER.test(q) && !namedAny) || YEARS.test(q))) {
        var MON = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11 }, now = new Date(), nowM = now.getFullYear() * 12 + now.getMonth();
        var seen = {}, rows = [], spans = [], orgs = {};
        secs.forEach(function (sec) {
          var m = sec.s.meta || {};
          if (m.kind !== "role" && m.kind !== "research") return;
          var h = sec.s.chunks[0].match(/^([^(]+?)\s*\(([A-Z][a-z]{2}) (\d{4}) - (?:([A-Z][a-z]{2}) (\d{4})|Present)\):/);
          var key = h ? h[1] + h[2] + h[3] : sec.s.id;
          if (seen[key]) return; seen[key] = 1;
          if (h) {
            var a0 = +h[3] * 12 + MON[h[2]], b0 = h[4] ? +h[5] * 12 + MON[h[4]] : nowM;
            spans.push([a0, b0]);
            orgs[h[1].split(",")[0].trim()] = 1;
            rows.push([a0, sec.s.id, h[1].trim() + " (" + h[2] + " " + h[3] + " - " + (h[4] ? h[4] + " " + h[5] : "Present") + ")"]);
          } else rows.push([0, sec.s.id, sec.s.title]);
        });
        rows.sort(function (a, b) { return b[0] - a[0] || (a[1] < b[1] ? -1 : 1); });
        spans.sort(function (a, b) { return a[0] - b[0]; });
        var total = 0, cur = null;                      // union of intervals: overlapping roles are counted once
        spans.forEach(function (x) { if (!cur || x[0] > cur[1] + 1) { if (cur) total += cur[1] - cur[0] + 1; cur = [x[0], x[1]]; } else cur[1] = Math.max(cur[1], x[1]); });
        if (cur) total += cur[1] - cur[0] + 1;
        var yrs = Math.floor(total / 12), mos = total % 12, first = spans.length ? spans[0][0] : 0, MN = Object.keys(MON);
        var heads = secs.filter(function (sec) { return sec.s.meta && sec.s.meta.headline; }), dom = { fintech: 0, health: 0, ai: 0 };
        heads.forEach(function (sec) { (sec.s.meta.domains || []).forEach(function (d) { if (dom[d] !== undefined) dom[d]++; }); });
        var pubs = (byId.get_publications ? byId.get_publications.s.chunks.length : 0);
        var span = (yrs ? yrs + (yrs === 1 ? " year " : " years ") : "") + (mos ? mos + (mos === 1 ? " month" : " months") : "");
        return { type: "tracks", section: "By the numbers", how: "dates in the record", score: 1,
          lead: "About " + span.trim() + " of professional and research experience, across " + rows.length + " roles at " + Object.keys(orgs).length + " organisations since " + MN[first % 12] + " " + Math.floor(first / 12) + " (overlapping roles counted once).",
          lines: rows.map(function (r) { return r[2]; }).concat([
            heads.length + " projects and roles with a measured result; " + pubs + " publications.",
            "Tagged by domain: fintech " + dom.fintech + ", healthtech " + dom.health + ", AI engineer " + dom.ai + " (a project can carry more than one tag)."]),
          links: [{ label: "Full experience", href: "index.html#experience" }, { label: "Book a chat", href: "contact.html" }],
          suggestions: ["Which project fits a fintech role?", "Tell me about his healthcare experience", "How can he help me?"] };
      }
      if (CONTACT.test(q)) return { type: "contact", lead: "Here is how to reach Aditya.", lines: [data.contact.reply], links: data.contact.links, suggestions: data.starters, section: "Contact", score: 1, how: "keyword" };
      if (THANKS.test(q) && q.length < 40) return { type: "thanks", lines: ["Happy to help. Ask me about any project, result or role."], suggestions: data.starters };
      var qv = vec(expand(tokens(q)), idf, true), fq = facets(q), hasFacet = fq.domain.length || fq.topic.length || fq.kind.length;
      var named = secs.some(function (sec) { return sec.aliasRx.some(function (rx) { return rx.test(q.toLowerCase()); }); });
      var skillNamed = secs.some(function (sec) { return sec.s.id === "get_skills" && sec.aliasRx.some(function (rx) { return rx.test(q.toLowerCase()); }); });
      if (hasFacet && !skillNamed && (LISTQ.test(q) || YESNO.test(q) || !named)) return listByFacets(q, fq, qv);
      if (ROLEFIT.test(q) && !named) {
        return { type: "tracks", section: "Role fit", how: "metadata", lead: "Which kind of role do you have in mind?", lines: ["Fintech, healthtech, or AI engineer. I will list the projects tagged for it."], suggestions: ["Which project fits a fintech role?", "Which projects fit healthtech?", "Which projects involve retrieval?"], score: 1 };
      }
      var r = route(q, qv, state);
      if (!r) return { type: "decline", lines: [data.decline], suggestions: data.starters, how: "no section matched" };
      var sec = r.sec, s = sec.s, ranked = sec.cv.map(function (v, idx) { return [cos(qv, v), idx]; }).sort(function (a, b) { return b[0] - a[0] || a[1] - b[1]; });
      var out = { type: "answer", meta: s.meta, section: s.title, sectionId: s.id, score: Math.round(r.score * 100) / 100, how: r.how, links: s.links || [], suggestions: s.asks, sourceIdx: ranked[0][1] };
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
    function answer(q, state) {                       // one or several questions in one message
      state = state || {};
      var parts = (q || "").split(/(?<=[?!.])\s+/).map(function (p) { return p.trim(); }).filter(function (p) { return p.replace(/[^a-z]/gi, "").length >= 3; });
      if (parts.length > 1) {
        var rs = parts.slice(0, 3).map(function (p) { var r = answerOne(p, state); if (r && r.sectionId) state.last = r.sectionId; return r; }).filter(Boolean);
        if (rs.length > 1) return { type: "multi", parts: rs };
        if (rs.length === 1) return rs[0];
      }
      return answerOne(q, state);
    }
    return { answer: answer, sections: data.sections.map(function (x) { return x.id; }), tokens: tokens };
  }
  return { build: build, tokens: tokens };
});
