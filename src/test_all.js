// One evaluation over BOTH question sets: the 29-question dev set and the 22-question set written afterwards (51 total).
// Note: both sets have now been used to fix the engine, so this is a regression suite, not a blind test.
const fs = require("fs"), path = require("path"), E = require("./engine.js");
const grab = f => eval(fs.readFileSync(path.join(__dirname, f), "utf8").match(/const T = (\[[\s\S]*?\n\]);/)[1]);
const sets = { dev29: grab("test_engine.js"), second22: grab("test_heldout.js") };
const eng = E.build(JSON.parse(fs.readFileSync(path.join(__dirname, "..", process.argv[2] || "dist", "ask-data.json"), "utf8")));
let ok = 0, n = 0; const miss = [], per = {};
for (const [name, T] of Object.entries(sets)) {
  let k = 0;
  for (const [q, want, must] of T) {
    const r = eng.answer(q, {});
    const got = r.type === "decline" ? "decline" : r.type === "contact" ? "Contact" : r.sectionId;
    const text = [r.lead || "", ...(r.lines || [])].join(" ") + " " + (r.source || "");
    const a = want.split("|").includes(got), b = must.split("|").some(m => text.toLowerCase().includes(m.toLowerCase()));
    n++; if (a && b) { ok++; k++; } else miss.push([name, q, "want " + want, "got " + got, a ? "" : "WRONG SECTION", b ? "" : "FACT MISSING"]);
  }
  per[name] = k + "/" + T.length;
}
const twice = JSON.stringify(eng.answer("How was EMMA measured?", {})) === JSON.stringify(eng.answer("How was EMMA measured?", {}));
console.log(JSON.stringify({ total: n, correct_section_and_fact: ok + "/" + n, per_set: per, deterministic: twice }));
miss.forEach(m => console.log("MISS", JSON.stringify(m)));
