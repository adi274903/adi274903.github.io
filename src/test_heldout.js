// 22 questions written AFTER the engine was tuned on the 29-question dev set. Run once, report, then fix what is generic.
const fs = require("fs"), path = require("path"), E = require("./engine.js");
const eng = E.build(JSON.parse(fs.readFileSync(path.join(__dirname, "..", "dist", "ask-data.json"), "utf8")));
const T = [
 ["Tell me about the fraud work at Jocata", "get_jocata", "0.86"],
 ["What stack did he use for the safety data sheets?", "get_value_global", "Qdrant"],
 ["How did he cut the reporting time at Tata?", "get_tata_capital", "PySpark"],
 ["Which benchmarks did Med-Qwen beat MedGemma on?", "get_med_qwen", "MedGemma"],
 ["What's the SkyDeck thing?", "get_stealth_startup", "SkyDeck"],
 ["Did he present at AMIA?", "get_recognition", "AMIA"],
 ["what degrees does he hold", "get_education", "Master"],
 ["Does he know SQL?", "get_skills", "SQL"],
 ["How accurate is the pricing agent?", "get_pricing_agent", "91%"],
 ["What was the physician rated improvement for EMMA AI?", "get_emma", "25%"],
 ["How many synthetic queries did the pricing agent use?", "get_pricing_agent", "465"],
 ["What papers has he written about plant phenotyping?", "get_publications", "Phenotyping"],
 ["Tell me about the Sorensen Dice contribution", "get_cmu_paper", "Sorensen"],
 ["What models did NIST AIMSEC use as judge?", "get_cmu_evaluation", "DeepSeek"],
 ["Is he open to moving?", "Contact", "relocat"],
 ["What is Jocata?", "get_jocata", "fraud"],
 ["Give me a recipe for pasta", "decline", "only answer"],
 ["Who is the president of the US?", "decline", "only answer"],
 ["Can you write a SQL query for me?", "decline", "only answer"],
 ["What's the weather like in Houston?", "decline", "only answer"],
 ["How did the Learning Portal compare to Claude?", "get_learning_portal", "0.4201"],
 ["What did he do at Carnegie Mellon research?", "get_cmu_evaluation|get_cmu_paper|get_pricing_agent", "Carnegie|NIST"],
];
let ok = 0; const miss = [];
for (const [q, want, must] of T) {
  const r = eng.answer(q, {});
  const got = r.type === "decline" ? "decline" : r.type === "contact" ? "Contact" : r.sectionId;
  const text = [r.lead || "", ...(r.lines || [])].join(" ") + " " + (r.source || "");
  const a = want.split("|").includes(got), b = must.split("|").some(m => text.toLowerCase().includes(m.toLowerCase()));
  if (a && b) ok++; else miss.push([q, "want " + want, "got " + got, a ? "" : "WRONG SECTION", b ? "" : "FACT MISSING"]);
}
console.log(JSON.stringify({ heldout_questions: T.length, correct_section_and_fact: ok + "/" + T.length }));
miss.forEach(m => console.log("MISS", JSON.stringify(m)));
