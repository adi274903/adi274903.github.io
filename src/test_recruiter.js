// Recruiter-style questions, written BEFORE adding help / experience / multi-question / typo handling, so the first run is blind.
// [question, acceptable outcomes (section id | tracks | Contact | decline | multi), substring(s) the answer must contain ("" = any)]
const fs = require("fs"), path = require("path"), E = require("./engine.js");
const eng = E.build(JSON.parse(fs.readFileSync(path.join(__dirname, "..", process.argv[2] || "dist", "ask-data.json"), "utf8")));
const T = [
 ["Can you give me a quick summary of his background?", "get_summary|tracks", ""],
 ["What roles has he held?", "tracks", "Value Global"],
 ["What's his current role?", "get_value_global", "Value Global"],
 ["Where is he based and is he open to relocation?", "Contact", "relocate"],
 ["Does he need visa sponsorship?", "decline|Contact", "only answer|reach Aditya"],
 ["What is his salary expectation?", "decline|Contact", "only answer|reach Aditya"],
 ["When can he start?", "decline|Contact", "only answer|reach Aditya"],
 ["Is he available for an interview next week?", "decline|Contact", "only answer|reach Aditya"],
 ["Who are his references?", "decline|Contact", "only answer|reach Aditya"],
 ["Does he have experience with LLMs in production?", "get_value_global|get_emma|tracks", "Value Global|EMMA"],
 ["Has he worked with RAG?", "tracks|get_emma|get_value_global", "EMMA|Value Global"],
 ["Does he know Python?", "get_skills", "Python"],
 ["Any experience with AWS or GCP?", "get_value_global|get_emma|get_skills|tracks", "Bedrock|GCP|AWS"],
 ["Has he fine-tuned models?", "get_med_qwen|tracks", "Med-Qwen|DoRA"],
 ["Does he have healthcare domain experience?", "tracks", "EMMA|Med-Qwen"],
 ["Any finance or banking experience?", "tracks", "Tata|Jocata"],
 ["What's his strongest project?", "get_med_qwen|tracks|get_summary", ""],
 ["Tell me about his research", "get_cmu_evaluation|get_cmu_paper|tracks", "NIST|Carnegie|imputation"],
 ["Has he published any papers?", "get_publications", "arXiv"],
 ["What did he build at his current job?", "get_value_global", "Qdrant|retrieval"],
 ["Can he lead a team?", "get_stealth_startup|decline|Contact", ""],
 ["What is his education?", "get_education", "Master"],
 ["Where did he go to school?", "get_education", "Carnegie Mellon"],
 ["How many years of experience does he have?", "tracks|decline|Contact", ""],
 ["Has he worked in a startup?", "get_stealth_startup", "SkyDeck|Stealth"],
 ["Any open source or Hugging Face work?", "get_med_qwen", "Hugging Face|Med-Qwen"],
 ["What metrics did he improve?", "tracks|get_value_global|get_summary", ""],
 ["How can I contact him?", "Contact", "asannabh@alumni.cmu.edu"],
 ["Does he have a LinkedIn?", "Contact", "LinkedIn|linkedin"],
 ["What makes him a good fit for an AI engineer role?", "tracks", "Value Global|Med-Qwen"],
 ["Compare his fintech and healthcare experience", "tracks", "Tata|Med-Qwen"],
 ["Has he used agents or MCP?", "tracks|get_value_global", "Value Global"],
 ["tell me about his time at Tata", "get_tata_capital", "credit"],
 ["What did he do at CMU?", "get_cmu_evaluation|get_cmu_paper|get_pricing_agent|get_education|tracks", "Carnegie|NIST|CPT|imputation"],
 ["Does he have experience with vector databases?", "get_value_global|get_emma|tracks|get_skills", "Qdrant|pgvector"],
 ["whats his expirience", "tracks", "Value Global"],
 ["waht projects has he done", "tracks|get_summary", ""],
 ["So how can he help me? whats hsi experience?", "multi", "Fintech|Value Global"],
];
let ok = 0; const rows = [];
for (const [q, want, must] of T) {
  const r = eng.answer(q, {});
  const got = r.type === "decline" ? "decline" : r.type === "contact" ? "Contact" : r.type === "tracks" ? "tracks" : r.type === "multi" ? "multi" : r.sectionId;
  const all = r.type === "multi" ? r.parts : [r];
  const text = all.map(x => [x.lead || "", ...(x.lines || []), ...(x.links || []).map(l => l.label)].join(" ") + " " + (x.source || "")).join(" ");
  const a = want.split("|").includes(got), b = !must || must.split("|").some(m => text.toLowerCase().includes(m.toLowerCase()));
  if (a && b) ok++; else rows.push([q, "want " + want, "got " + got, a ? "" : "WRONG", b ? "" : "FACT?", (all[0].lines || [""])[0].slice(0, 60)]);
}
console.log(JSON.stringify({ recruiter_questions: T.length, correct: ok + "/" + T.length }));
rows.forEach(r => console.log("MISS", JSON.stringify(r)));
