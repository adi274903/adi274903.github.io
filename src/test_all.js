// One evaluation over BOTH question sets: the 29-question dev set and the 22-question set written afterwards (51 total).
// Note: both sets have now been used to fix the engine, so this is a regression suite, not a blind test.
const fs = require("fs"), path = require("path"), E = require("./engine.js");
const grab = f => eval(fs.readFileSync(path.join(__dirname, f), "utf8").match(/const T = (\[[\s\S]*?\n\]);/)[1]);
const roles = [["Which project fits a fintech role?", "tracks", "Credit-bureau"], ["Which projects are relevant for healthtech?", "tracks", "Med-Qwen"], ["What fits an AI engineer role?", "tracks", "Value Global"], ["Which project suits a banking job?", "tracks", "Credit-bureau"], ["Which project fits a role?", "tracks", "Which kind of role"]];
const facetq = [["Which projects involve retrieval?", "tracks", "Value Global"], ["Which work involves fine-tuning?", "tracks", "Med-Qwen"], ["Any fraud or credit work?", "tracks", "Credit-bureau"], ["Which projects mix healthcare and evaluation?", "tracks", "Med-Qwen|NIST"], ["Show me agent projects for fintech", "tracks", "Value Global|Patient-facing"]];
const phrasing = [["tell me about his healthcare experience?", "tracks", "EMMA"], ["What is his fintech background?", "tracks", "Tata"], ["clinical work he has done", "tracks", "Med-Qwen"], ["tell me about his experience with retrieval", "tracks", "EMMA"], ["anything about banking", "tracks", "Jocata"]];
const intents = [["So how can he help me? whats hsi experience?", "multi", "Fintech|Value Global"], ["how can he help me", "tracks", "Fintech"], ["whats his experience?", "tracks", "Value Global"], ["what is hsi experiance", "tracks", "Tata Capital"], ["tell me about tata capitl", "get_tata_capital", "credit"], ["why should we hire him?", "tracks", "Healthtech"]];
const sets = { intents6: intents, phrasing5: phrasing, facets5: facetq, roles5: roles, dev29: grab("test_engine.js"), second22: grab("test_heldout.js") };
const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, "..", process.argv[2] || "dist", "ask-data.json"), "utf8")); const eng = E.build(DATA);
let ok = 0, n = 0; const miss = [], per = {};
for (const [name, T] of Object.entries(sets)) {
  let k = 0;
  for (const [q, want, must] of T) {
    const r = eng.answer(q, {});
    const got = r.type === "decline" ? "decline" : r.type === "contact" ? "Contact" : r.type === "tracks" ? "tracks" : r.type === "multi" ? "multi" : r.sectionId;
    const all = r.type === "multi" ? r.parts : [r]; const text = all.map(x => [x.lead || "", ...(x.lines || []), ...(x.links || []).map(l => l.label)].join(" ") + " " + (x.source || "")).join(" ");
    const a = want.split("|").includes(got), b = must.split("|").some(m => text.toLowerCase().includes(m.toLowerCase()));
    n++; if (a && b) { ok++; k++; } else miss.push([name, q, "want " + want, "got " + got, a ? "" : "WRONG SECTION", b ? "" : "FACT MISSING"]);
  }
  per[name] = k + "/" + T.length;
}
// every suggested question on the page must be answerable (never a decline)
let starterMiss = []; const asks = [].concat(eng_data_starters(), eng_data_asks());
function eng_data_starters() { return DATA.starters; } function eng_data_asks() { return [].concat.apply([], DATA.sections.map(s => s.asks)); }
asks.forEach(q => { if (eng.answer(q, {}).type === "decline") starterMiss.push(q); });
let askWrong = []; DATA.sections.forEach(s => s.asks.forEach(q => { const r = eng.answer(q, {}); if (r.type === "answer" && r.sectionId !== s.id) askWrong.push([q, s.id, r.sectionId]); }));
const twice = JSON.stringify(eng.answer("How was EMMA measured?", {})) === JSON.stringify(eng.answer("How was EMMA measured?", {}));
console.log(JSON.stringify({ total: n, correct_section_and_fact: ok + "/" + n, per_set: per, deterministic: twice, suggested_questions_checked: asks.length, suggested_that_decline: starterMiss, example_questions_in_wrong_section: askWrong }));
miss.forEach(m => console.log("MISS", JSON.stringify(m)));
