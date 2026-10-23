#!/usr/bin/env python3
"""portfolio_v7 -- build dist/ from the GT3-derived content model.

Content: ../portfolio/content.py (-> design/gt.py -> resume_gt/GT3.md). Nothing numeric is
typed here except chart inputs copied from those bullets; the audit at the end fails the build
if a retired metric, or a number that GT3 does not contain, reaches visible text.

    python3 build.py            -> dist/  (local preview, with the chat popup; serve with serve.py)
    python3 build.py --static   -> docs/  (GitHub Pages build, no chat popup)
"""
import pathlib
import re
import sys
from html import escape as e

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
sys.path.insert(0, str(HERE.parent / "portfolio"))
sys.path.insert(0, str(HERE.parent / "portfolio" / "design"))
sys.path.insert(0, str(HERE.parent / "smollm_chatbot"))
import charts as CH  # noqa: E402
import content as C  # noqa: E402
import gt  # noqa: E402
import webcontent as S  # noqa: E402

STATIC = "--static" in sys.argv           # published build: no chat button (Pages cannot run the model)
DIST = HERE / ("docs" if STATIC else "dist")
import hashlib
VER = hashlib.md5(b"".join((HERE / "src" / f).read_bytes() for f in ("styles.css", "app.js", "engine.js", "ask.js", "contact.js"))).hexdigest()[:8]
NAME, ROLE = C.NAME, C.ROLE

# ------------------------------------------------------------------ authored copy
# Presentation only; every factual clause is a compression of a GT3 bullet.
TRACKS = [("all", "All"), ("ai", "AI engineer"), ("fintech", "Fintech"), ("health", "Healthtech")]
_BODY = C.THESIS.split(" - ", 1)[1].split(" Optimization")[0]
SUMMARY = _BODY[0].upper() + _BODY[1:]          # GT summary without its role title and motto, verbatim
MOTTO = C.THESIS[C.THESIS.index("Optimization"):]
LEDE = {      # one plain-language summary per track; every figure is a GT3 number
    "ai": "I build and evaluate AI systems for clinical and financial data. Recently: a 4.2B clinical model that "
          "beat MedGemma-1.5-4B-it on all six benchmarks, an agentic retrieval prototype cut from ~8 seconds to 2, "
          "and an evaluation pipeline with zero run-to-run skew.",
    "fintech": "Credit-bureau reporting cut from 3 days to 2 hours at Tata Capital and a fraud-identification "
               "model at 0.86 F1 at Jocata, backed by production RAG and LLM evaluation.",
    "health": "I build and evaluate AI for clinical settings: a 4.2B clinical model that beat MedGemma-1.5-4B-it on "
              "all six benchmarks, physician-rated RAG accuracy up 25% in EMMA, and a pricing agent that lifted "
              "CPT/HCPCS code selection from 82% to 91%.",
}
STATS = {
    "ai": [("~8s → 2s", "retrieval time over ~1,000 chemical safety data sheets"),
           ("66.20", "PubMedQA for Med-Qwen, vs 45.60 for its base"),
           ("97/100", "documents with all PII removed"),
           ("82% → 91%", "CPT/HCPCS code selection")],
    "fintech": [("3 days → 2 hours", "credit-bureau submission prep, Tata Capital"),
                ("0.86", "F1 for fraud identification, Jocata")],
    "health": [("66.20", "PubMedQA for Med-Qwen, vs 45.60 for its base"),
               ("+25%", "physician-rated accuracy + completeness, EMMA"),
               ("17,167", "schema-bound evaluation records"),
               ("82% → 91%", "CPT/HCPCS code selection")],
}


def _metric_row(value):
    return next(r for r in C.METRICS if r[1] == value)



# ------------------------------------------------------------- logos, bold numbers, links
ICON_RULES = [("qwen", r"qwen", "Qwen"), ("googlecloud", r"\bGCP\b|Google Cloud", "Google Cloud"),
              ("googlegemini", r"Gemini|Gemma", "Gemini / Gemma"), ("huggingface", r"hugging ?face", "Hugging Face"),
              ("pytorch", r"PyTorch", "PyTorch"), ("postgresql", r"pgvector|PostgreSQL", "PostgreSQL"),
              ("neo4j", r"Neo4j", "Neo4j"), ("qdrant", r"Qdrant", "Qdrant"),
              ("databricks", r"Databricks", "Databricks"), ("apachespark", r"PySpark", "PySpark"),
              ("oracle", r"Oracle", "Oracle"), ("python", r"\bPython\b", "Python"),
              ("spacy", r"SpaCy", "spaCy"), ("fastapi", r"FastAPI", "FastAPI"),
              ("streamlit", r"Streamlit", "Streamlit"), ("anthropic", r"\bClaude\b", "Claude"),
              ("mistralai", r"Mistral", "Mistral"), ("deepseek", r"DeepSeek", "DeepSeek"),
              ("amazonwebservices", r"\bAWS\b|Bedrock", "AWS Bedrock"), ("vllm", r"vLLM", "vLLM"),
              ("tensorflow", r"TensorFlow", "TensorFlow"), ("scikitlearn", r"scikit-learn", "scikit-learn")]


def icons_in(text):
    """Ordered, unique (slug, name) for every known technology mentioned in text."""
    seen, out = set(), []
    for slug, rx, name in ICON_RULES:
        if slug not in seen and re.search(rx, text, re.I if slug in ("qwen", "huggingface") else 0):
            seen.add(slug); out.append((slug, name))
    return out


def ic(slug, name):
    return (f'<span class="lg-i" title="{e(name)}"><svg class="ic" width="16" height="16" aria-hidden="true">'
            f'<use href="icons.svg#i-{slug}"/></svg></span>')


_TOK = re.compile(r"(arXiv:\d{4}\.\d{5})|(https?://[^\s)\]>,;]+)|((?<![\w.\-])~?\d(?:[\d,]*\d)?(?:\.\d+)?(?:-\d+(?:\.\d+)?)?(?:%|[BMK](?![A-Za-z]))?)")


def fmt(text):
    """Escape, bold every metric, and link arXiv ids and URLs. Returns trusted HTML."""
    out, pos = [], 0
    for m in _TOK.finditer(text):
        out.append(e(text[pos:m.start()])); pos = m.end()
        tok = m.group(0)
        if m.group(1):
            out.append(f'<a class="ln" href="https://arxiv.org/abs/{tok[6:]}" rel="noopener">{e(tok)}</a>')
        elif m.group(2):
            out.append(f'<a class="ln" href="{e(tok)}" rel="noopener">{e(tok)}</a>')
        elif re.fullmatch(r"(19|20)\d\d", tok.lstrip("~")):
            out.append(e(tok))
        else:
            out.append(f'<strong class="n">{e(tok)}</strong>')
    out.append(e(text[pos:]))
    return "".join(out)


COLOGOS = [("Value Global", "seal", "valueglobal.png"), ("Jocata", "img", "jocata.png"), ("Carnegie", "seal", "cmu.png"), ("Tata", "full", "tata.png"), ("Stealth", "full", "stealth.png")]


def co_logo(org):
    """Left-hand tile for an employer: its logo if we have one, otherwise initials (decorative)."""
    for key, kind, val in COLOGOS:
        if key in org:
            if kind in ("img", "full", "seal"):
                sz = 44 if kind == "full" else 40 if kind == "seal" else 32
                return (f'<span class="co{" fb" if kind == "full" else ""}{" ink" if val == "jocata.png" else ""}"><img src="logos/{val}" alt="" width="{sz}" height="{sz}" '
                        f'loading="lazy" decoding="async"></span>')
            return f'<span class="co">{ic(val, org)}</span>'
    ini = "ST" if org.startswith("Stealth") else "".join(w[0] for w in re.sub(r"[^A-Za-z ]", "", org).split()[:2]).upper()
    return f'<span class="co mn" aria-hidden="true">{e(ini)}</span>'


def honor(h):
    """'Title, Org - detail (when)' -> structured row, same words, split for scanning."""
    m = re.search(r"\(([^)]*)\)\s*$", h)
    when, h = (m.group(1), h[:m.start()].strip()) if m else ("", h)
    head, _, detail = h.partition(" - ")
    title, _, org = head.partition(", ")
    if not detail and when and "," in when:      # '(Kaggle competition, Spring 2025)' -> note + date
        note, _, when = when.rpartition(", ")
        detail = (org + " " if False else "") + note
    if detail and not when and re.match(r"^[A-Z][a-z]{2} \d{4}", detail):    # 'Nov 2025, Atlanta' is a date line
        when, detail = detail, ""
    return title, org, detail, when


# ------------------------------------------------------------ Med-Qwen comparison (GT3, model card)
MQ_HEAD, MQ_ROWS = gt.medqwen_table()
_NAMES = {"Qwen3.5-4B-Base": "its base", "MedGemma-1.5-4B-it": "MedGemma-1.5-4B-it", "Gemma-4-E4B-it": "Gemma-4-E4B-it"}


def mq_wins():
    """Out of the six benchmarks, how many does Med-Qwen beat each other model on? Derived from the table."""
    out = []
    for col, name in ((3, "MedGemma-1.5-4B-it"), (4, "Gemma-4-E4B-it"), (1, "its base, Qwen3.5-4B-Base")):
        won = [float(r[2]) > float(r[col]) for r in MQ_ROWS]
        out.append((name, won))
    return out


_W = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_T = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy"}


def mq_score():
    rows = "".join(
        f'<div class="vr"><span class="vn">{e(n)}</span><span class="cells" aria-hidden="true">'
        + "".join(f'<i class="{"w" if w else "l"}"></i>' for w in won)
        + f'</span><b>{sum(won)}/{len(won)}</b></div>' for n, won in mq_wins())
    return (f'<div class="vs" role="group" aria-label="Med-Qwen wins out of six benchmarks, per comparison model">'
            f'<span class="k">Wins out of {len(MQ_ROWS)} benchmarks</span>{rows}</div>')


def words_of(n):
    return _W[n] if n < 20 else _T[n // 10] + ("" if n % 10 == 0 else "-" + _W[n % 10])


# ------------------------------------------------------------ deterministic Q&A data (TF-IDF built in the browser)
ENTRY_OF = {"get_med_qwen": "01", "get_emma": "02", "get_learning_portal": "03", "get_cmu_evaluation": "04",
            "get_pricing_agent": "05", "get_value_global": "06", "get_tata_capital": "07", "get_jocata": "08"}
KIND_OF = {"get_value_global": "role", "get_cmu_evaluation": "research", "get_cmu_paper": "research", "get_pricing_agent": "research",
           "get_stealth_startup": "role", "get_tata_capital": "role", "get_jocata": "role", "get_med_qwen": "project", "get_emma": "project",
           "get_learning_portal": "project", "get_publications": "papers", "get_recognition": "honors", "get_education": "education",
           "get_skills": "skills", "get_summary": "overview"}
ORG_OF = {"get_value_global": "Value Global LLC", "get_cmu_evaluation": "Carnegie Mellon University, NIST-AIMSEC", "get_cmu_paper": "Carnegie Mellon University",
          "get_pricing_agent": "Carnegie Mellon University, NIST-AIMSEC", "get_stealth_startup": "Stealth Startup", "get_tata_capital": "Tata Capital",
          "get_jocata": "Jocata Financial Advisory", "get_emma": "Allegheny Health Network", "get_education": "Carnegie Mellon University, REVA University"}
YEAR_OF = {"get_value_global": "2026", "get_cmu_evaluation": "2025", "get_cmu_paper": "2025", "get_pricing_agent": "2025", "get_stealth_startup": "2025",
           "get_tata_capital": "2024", "get_jocata": "2023", "get_med_qwen": "2026", "get_emma": "2025", "get_learning_portal": "2025"}
DOMAINS_EXTRA = {"get_stealth_startup": ["ai"], "get_cmu_paper": ["health", "ai"], "get_publications": [], "get_summary": ["ai"]}
FACETS = {   # question words -> facet; authored routing vocabulary, never shown as facts
    "domain": {"fintech": ["fintech", "finance", "financial", "bank", "banking", "credit", "fraud", "payments", "lending", "loan"],
               "health": ["health", "healthcare", "healthtech", "clinical", "medical", "hospital", "physician", "patient", "pricing transparency"],
               "ai": ["ai engineer", "ml engineer", "machine learning engineer", "genai", "llm", "ai role"]},
    "kind": {"research": ["research", "researcher", "researchers"]},
    "topic": {"Retrieval & RAG": ["retrieval", "rag", "vector search", "search", "vector database", "vector databases", "vector store", "vector db", "embeddings"], "Fine-tuning & training": ["fine-tuning", "finetuning", "fine tuning", "fine-tuned", "fine tuned", "finetuned", "tuned", "training", "pretraining", "dora"],
              "Evaluation & benchmarks": ["evaluation", "evaluating", "benchmark", "benchmarks", "metrics"], "Agents & tool use": ["agent", "agents", "agentic", "mcp", "tool use"],
              "Data engineering": ["data engineering", "pipeline", "pipelines", "sql", "spark", "etl"], "Classical ML & NLP": ["nlp", "classical ml", "xgboost", "machine learning model"]}}


def ask_data():
    """The record, chunked into 15 sections (verbatim GT3 lines) plus routing metadata, as one small JSON file."""
    import sections as SEC
    LIST = {"get_publications", "get_recognition", "get_education", "get_skills", "get_summary"}
    LINKS = {
        "get_med_qwen": [{"label": "Latest model (with RLVR) on Hugging Face", "href": "https://huggingface.co/adi274903/Med-Qwen-3.5-4B-it"},
                         {"label": "Earlier release (Instruct) on Hugging Face", "href": "https://huggingface.co/adi274903/Med-Qwen-3.5-4B-Instruct"}],
        "get_learning_portal": [{"label": "Project on GitHub", "href": "https://github.com/adi274903/NLX_Assignment3"}],
        "get_publications": [{"label": p["venue"], "href": p["url"]} for p in C.PUBLICATIONS],
        "get_recognition": [{"label": "11-785 leaderboard", "href": "https://www.kaggle.com/competitions/11785-hw-2-p-2-face-verification-spring-2025/leaderboard"},
                            {"label": "AMIA poster (PDF)", "href": "https://workshopamia2025.github.io/AMIA-KDDM-2025/posters/KDDM_Poster%5BCMU%5D.pdf"}],
        "get_cmu_paper": [{"label": "arXiv:2503.22954", "href": C.ARXIV}],
    }
    secs = []
    for tool, title, desc, asks, aliases, chunks in SEC.SECTIONS:
        chunks = [C.EMMA_PRINT if (tool == "get_emma" and c.startswith("Project EMMA")) else c for c in chunks]
        if tool == "get_skills":
            aliases = aliases + [t.strip().lower() for g, items in C.SKILLS for t in items.split(",") if t.strip()]
        ent = next((en for en in ENTRIES if en["n"] == ENTRY_OF.get(tool)), None)
        body = " ".join(chunks)
        meta = dict(
            project=title, kind=KIND_OF.get(tool, "record"), org=ORG_OF.get(tool, ""), year=YEAR_OF.get(tool, ""),
            domains=(ent["tracks"].split() if ent else DOMAINS_EXTRA.get(tool, [])),       # fintech / health / ai (the site's role tags)
            topics=[name for name, rx in CONCEPTS if re.search(rx, body, re.I)],           # derived: which areas the lines actually mention
            tech=[n for _, n in icons_in(body)],                                         # derived: tools named in the lines
            headline=(dict(metric=ent["metric"], note=ent["metric_note"], href=ent["slug"]) if ent else None))
        secs.append(dict(id=tool, title=title, desc=desc, asks=asks, aliases=aliases, chunks=chunks, meta=meta,
                         links=LINKS.get(tool, []), list=tool in LIST))
    starters = ["What did he do at EMMA AI?", "How fast is the retrieval at Value Global?", "What PubMedQA score did Med-Qwen get?",
                "Which project fits a fintech role?"]
    tracks = {}
    for key, label, lead in (("fintech", "Fintech", "Projects most relevant to a fintech role:"),
                             ("health", "Healthtech", "Projects most relevant to a healthtech role:"),
                             ("ai", "AI engineer", "Projects most relevant to an AI engineer role:")):
        items = [dict(title=en["title"], metric=en["metric"], note=en["metric_note"], href=en["slug"])
                 for en in ENTRIES if key in en["tracks"].split()]
        tracks[key] = dict(label=label, lead=lead, items=items)
    return dict(
        sections=secs, starters=starters, tracks=tracks, facets=FACETS,
        greeting="Hi. I answer questions about Aditya's projects, results, roles, papers and education, using only his record. Try one of these.",
        decline="I only answer questions about Aditya's record: his projects, results, experience, papers and education. I can't help with that.",
        contact=dict(reply=f"You can reach Aditya at {C.EMAIL}. He is based in {C.LOCATION} ({C.AVAILABILITY.lower()}).",
                     links=[{"label": "Email", "href": "mailto:" + C.EMAIL}, {"label": "LinkedIn", "href": C.LINKEDIN},
                            {"label": "GitHub", "href": C.GITHUB}, {"label": "Portfolio", "href": "https://adi274903.github.io/"}]))

# ---------------------------------------------------------------------- entries
def _chart_for(n, w=CH.W):
    if n == "01":
        return mq_score() + '<div class="rl">' + CH.delta("reasoning tokens per answer (MedQA)", 456, 66, "456 (SFT)", "66 (RLVR)",
                                     note="same MedQA accuracy: 73.2% SFT, 73.5% RLVR; my own evaluation harness", w=w) + "</div>"
    if n == "__old01":
        return CH.hbars("Med-Qwen-3.5-4B-Instruct · zero-shot greedy", [
            ("PubMedQA · base", 45.60, "45.60", False),
            ("PubMedQA · Med-Qwen", 66.20, "66.20", True),
            ("MMLU Med", 80.72, "80.72", False), ("MedQA", 67.95, "67.95", False),
            ("AfriMed-QA", 64.80, "64.80", False), ("GPQA Diamond", 50.51, "50.51", False),
            ("MedMCQA", 33.20, "33.20", False)], maxv=100,
            note="base = Qwen3.5-4B-Base", label="Med-Qwen benchmark scores", w=w)
    if n == "02":
        return CH.hbars("EMMA \u00b7 evidence base", [
            ("students surveyed", 48, "48", True), ("20 contexts", 20, "20", False),
            ("physician surveys", 2, "2", False)],
            maxv=50, note="+25% comes from the two physician surveys",
            label="EMMA evidence base", w=w)
    if n == "03":
        return CH.hbars("RACE · 15 Deep Research Bench queries", [
            ("Mistral-7B + BART", 0.0668, "0.0668", False),
            ("Claude Sonnet 3.7", 0.4201, "0.4201", True)],
            note="abstract-only retrieval limited the pipeline", w=w)
    if n == "04":
        return CH.hbars("NIST-AIMSEC evaluation corpus", [
            ("inclusion list", 28023, "28,023", False), ("records", 17167, "17,167", True),
            ("full-text papers", 15944, "15,944", False)],
            note="zero run-to-run skew over 10 repeats", w=w)
    if n == "05":
        return CH.delta("CPT/HCPCS code selection (%)", 82, 91, "82%", "91%", maxv=100,
                        note="465 synthetic queries", w=w)
    if n == "06":
        return CH.delta("retrieval time (seconds)", 8, 2, "~8 s", "2 s",
                        note="~1,000 chemical safety data sheets", w=w)
    if n == "07":
        return CH.delta("credit-bureau submission prep (hours)", 72, 2, "3 days", "2 hours",
                        note="3 days drawn as 72 hours, to scale", w=w)
    if n == "08":
        return CH.hbars("fraud identification · F1", [("F1", 0.86, "0.86", True)],
                        maxv=1, note="scale 0 to 1", w=w)


def _linkify(u):
    return u if not u or u.startswith("http") else "https://" + u


ENTRIES = []
for c in S.CARDS:
    ENTRIES.append(dict(c, label={"01": "Med-Qwen", "02": "EMMA", "03": "PLP", "04": "NIST eval",
                                  "05": "Pricing", "06": "Value Global"}[c["n"]]))
tr = {"01": "ai health", "02": "ai health", "03": "ai", "04": "ai health",
      "05": "ai health", "06": "ai"}
bul = {"01": C.PROJECTS[0]["bullets"] + ["Cut medical reasoning length about 7x (456 to 66 tokens) at matching MedQA accuracy by training a GRPO RLVR adapter on Qwen3.5-4B with rule-based accuracy, format and length rewards."], "02": [C.EMMA_PRINT], "03": C.PROJECTS[2]["bullets"],
       "04": C.EXPERIENCE[1]["bullets"][:2], "05": C.EXPERIENCE[1]["bullets"][3:4],
       "06": C.EXPERIENCE[0]["bullets"]}
src = {"01": (C.PROJECTS[0]["meta"], C.PROJECTS[0]["url"]), "02": (C.PROJECTS[1]["meta"], ""),
       "03": (C.PROJECTS[2]["meta"], C.PROJECTS[2]["url"]),
       "04": ("Carnegie Mellon University, NIST-AIMSEC", ""),
       "05": ("Carnegie Mellon University, NIST-AIMSEC", ""),
       "06": ("Value Global LLC", "")}
for en in ENTRIES:
    n = en["n"]
    en.update(tracks=tr[n], bullets=bul[n], source=src[n][0], url=src[n][1])
    if n == "01":
        en["url"] = "https://huggingface.co/adi274903/Med-Qwen-3.5-4B-it"      # latest release, trained with RLVR
    if n == "02":   # the physician surveys measured the answers (source of +25%); the student survey is app feedback
        en["line"] = ("Rebuilt retrieval over a 20-context corpus on GCP with Gemini and pgvector. Two physician "
                      "surveys measured the answers, and 48 students surveyed the app.")
for n, ex, key, kick in (("07", C.TATA, "3 days → 2 hours", "Credit reporting"),
                         ("08", C.JOCATA, "0.86", "Fraud NLP")):
    row = _metric_row(key.replace("→", "→")) if key in [r[1] for r in C.METRICS] else None
    ENTRIES.append(dict(
        n=n, label="Tata" if n == "07" else "Jocata", year=ex["year"], kicker=kick,
        title="Credit-bureau submission automation" if n == "07" else "Fraud-identification NLP",
        metric=key, metric_note=row[0] if row else "",
        line=(row[2] if row else ""), tags=["SAS", "Databricks PySpark", "automated tests"] if n == "07"
        else ["XGBoost", "SpaCy NER", "REST APIs"],
        tracks="fintech ai" if n == "08" else "fintech", bullets=ex["bullets"],
        source=f'{ex["org"]} · {ex["meta"]}', url=""))
for en in ENTRIES:
    en["chart"] = (_chart_for(en["n"]) if en["n"] == "01" else
                   f'<div class="dw">{_chart_for(en["n"])}</div><div class="mw">{_chart_for(en["n"], 360)}</div>')
    en["slug"] = f'case-{en["n"]}.html'

# ------------------------------------------------------------------ evidence matrix
CONCEPTS = [
    ("Retrieval & RAG", r"retriev|\bRAG\b|Qdrant|pgvector|vector"),
    ("Fine-tuning & training", r"fine-tun|pretrain|DoRA|SFT"),
    ("Evaluation & benchmarks", r"evaluat|benchmark|judge|skew|\bF1\b|survey|RACE|validated|queries|tests"),
    ("Agents & tool use", r"agent|MCP|tool"),
    ("Data engineering", r"SQL|PySpark|Databricks|SAS|pipeline|preprocess"),
    ("Classical ML & NLP", r"XGBoost|SpaCy|\bNER\b|NLP"),
]
MCOLS = [(en["label"], en["bullets"]) for en in ENTRIES] + [("Stealth", C.STEALTH["bullets"])]


def matrix_svg():
    hits = [[sum(1 for b in bl if re.search(rx, b, re.I)) for _, bl in MCOLS] for _, rx in CONCEPTS]
    return CH.matrix([c for c, _ in CONCEPTS], [l for l, _ in MCOLS], hits,
                     "resume bullets mentioning each area")


TIMELINE = [    # newest first: top row is now, bottom row is where it started
    ("Med-Qwen \u00b7 clinical SLM", 2026.78, 2026.95, True),
    ("Value Global \u00b7 AI engineer", 2026.5, 2026.95, True),
    ("NIST-AIMSEC \u00b7 research", 2025.25, 2026.37, True),
    ("EMMA \u00b7 capstone", 2025.58, 2025.92, False),
    ("Stealth startup \u00b7 co-founder", 2025.42, 2025.75, False),
    ("CMU \u00b7 MISM", 2024.58, 2025.92, False),
    ("Tata Capital \u00b7 credit report", 2024.08, 2024.5, False),
    ("Jocata \u00b7 fraud NLP", 2023.58, 2023.92, False),
]

# ------------------------------------------------------------------------ pieces
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
        "%3Crect width='32' height='32' fill='%230c0a08'/%3E%3Ctext x='16' y='22' "
        "text-anchor='middle' font-family='Georgia,serif' font-size='15' fill='%23d2ac5f'"
        "%3EAS%3C/text%3E%3C/svg%3E")
MAIL = f"mailto:{C.EMAIL}?subject=" + "Let%27s%20talk"

# photographs of the places in the record (Wikimedia Commons, credited in the footer); never presented as his own pictures
PLACES = {   # key -> (file, what the caption says, alt)
    "houston": ("houston.webp", "Houston, the nearest big city to Tomball, TX, where Value Global is based.", "Skyline of downtown Houston under a blue sky"),
    "pittsburgh": ("pittsburgh.webp", "Pittsburgh, where Carnegie Mellon University is.", "Carnegie Mellon University campus buildings in Pittsburgh"),
    "mumbai": ("mumbai.webp", "Mumbai, where Tata Capital is based.", "Mumbai skyline seen across the water with sailing boats"),
    "hyderabad": ("hyderabad.webp", "Hyderabad, where Jocata is based.", "The Charminar monument in Hyderabad at night"),
}
CITY_OF = {"Value Global": "houston", "Carnegie": "pittsburgh", "Tata": "mumbai", "Jocata": "hyderabad"}


def _credits():
    import json
    rows = json.loads((HERE / "src/assets/places/credits.json").read_text())
    by = {}
    for r in rows:
        key = next((k for k, (f, _, _) in PLACES.items() if r["file"].split("/")[-1].startswith(
            {"houston": "buildings-city-houston", "pittsburgh": "carnegie-mellon", "mumbai": "mumbai-skyline",
             "hyderabad": "charminar-hyderabad"}[k])), None)
        if key:
            by[key] = r
    return by


def credits_html():
    by = _credits()
    parts = []
    for k in ("houston", "pittsburgh", "mumbai", "hyderabad"):
        r = by[k]
        parts.append(f'<a href="{e(r["page"])}" rel="noopener">{e(r["title"])}</a> by {e(r["creator"])}, {e(r["license"])}')
    return "Photographs of cities, via Wikimedia Commons: " + "; ".join(parts) + "."


CHAT_BTN = ""


def shell(title, desc, body, depth_attr="", page="index", extra_js="", fab=True, credits=False, bodycls=""):
    cur = lambda n: ' aria-current="page"' if page == n else ""
    nav = (f'<a class="wk" href="index.html#work">Work</a><a class="mh" href="index.html#experience">Experience</a>'
           f'<a class="mh" href="index.html#results">Results</a><a href="ask.html"{cur("ask.html")}>Ask</a>'
           f'<button class="thm" id="tg" type="button" aria-label="Switch between dark and light">Theme</button>'
           f'<a class="btn p" href="contact.html"{cur("contact.html")}>Book a chat</a>')
    cr = f'<p class="cr" id="credits">{credits_html()}</p>' if credits else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta name="color-scheme" content="dark light"><meta name="theme-color" content="#0c0a08">
<link rel="icon" href="{ICON}">
<link rel="preload" href="fonts/YoungSerif-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/SourceSerif4-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="styles.css?v={VER}">
<script>document.documentElement.classList.add("js");try{{var t=localStorage.getItem("th");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head><body{bodycls}>
<header class="topbar"><a class="wm" href="index.html">{e(NAME)}</a><nav aria-label="Main">{nav}</nav></header>
<main>{body}</main>
<footer class="foot"><div class="row"><span>{e(ROLE)}, {e(C.LOCATION)}</span>
<nav aria-label="Elsewhere"><a href="{MAIL}">Email</a><a href="{C.LINKEDIN}" rel="noopener">LinkedIn</a><a href="{C.GITHUB}" rel="noopener">GitHub</a><a href="{C.ARXIV}" rel="noopener">arXiv</a><button class="thm tgf" type="button" aria-label="Switch between dark and light">Theme</button></nav>
<span>{e(NAME)}</span></div>
<p class="cr">Logos are trademarks of their owners; technology icons from Simple Icons (CC0).</p>{cr}</footer>
{extra_js}<script src="app.js?v={VER}" defer></script></body></html>"""


BLURB = {
    "01": "A small clinical reasoning model that beats MedGemma on every clinical benchmark I tested. I continued pretraining Qwen3.5 on medical text, then fine-tuned it with DoRA on a mix of clinical reasoning data, and published it on Hugging Face. A later stage trained it with reinforcement learning on rule-based rewards (GRPO), which cut its reasoning about sevenfold at the same MedQA accuracy.",
    "02": "I rebuilt the retrieval behind a clinical education podcast platform so residents get more accurate, more complete answers, using Gemini and pgvector on GCP. Physicians rated the answers, and students surveyed the app.",
    "03": "A research assistant that pulls from six scholarly sources. I benchmarked open models against Claude on Deep Research Bench and showed that abstract-only retrieval is what limits it.",
    "04": "At CMU I built an evaluation pipeline that turns thousands of full-text papers into schema-bound records. Two extractor models, a DeepSeek judge and a human verifier keep the results consistent from run to run.",
    "05": "A patient-facing agent that turns a plain-language question into the right billing code. MedGemma works out the intent and deterministic SQL does the pricing across hospital price files, so the answer is reproducible.",
    "06": "At Value Global I built an agentic proof of concept for chemical safety data sheets, combining vector search with graph traversal. I also built governed MCP tool access to Oracle ERP.",
    "07": "I moved legacy SAS credit-bureau reporting onto Databricks PySpark with automated tests, turning a multi-day manual prep into a short automated run.",
    "08": "An NLP pipeline that flags fraud in text messages and cost data, using XGBoost and SpaCy entity recognition, served through REST APIs.",
}


def work_row(en):
    tags = "".join(f"<li>{''.join(ic(s, n) for s, n in icons_in(t)[:1])}{e(t)}</li>" for t in en["tags"][:4])
    n = en["n"]
    return (f'<li data-n="{n}" data-tr="{en["tracks"]}" data-reveal>'
            f'<button class="wn" type="button" aria-controls="wf-{n}" aria-expanded="false">'
            f'<span class="wt">{e(en["title"])}</span><span class="wm">{e(en["kicker"])}, {e(en["year"])}</span></button>'
            f'<p class="wb">{e(BLURB[n])}</p><ul class="chips">{tags}</ul>'
            f'<div class="wf" id="wf-{n}"><div class="big">{e(en["metric"])}</div><p class="note">{e(en["metric_note"])}</p>{en["chart"]}</div>'
            f'<div class="wa"><button class="show" type="button">Show numbers</button><a href="{en["slug"]}">Case study</a></div></li>')


def stage_panes():
    out = ['<div class="pane me on" data-pane="me"><figure><img src="me.webp" width="640" height="640" '
           f'alt="Portrait of {e(NAME)}" decoding="async" fetchpriority="high">'
           f'<figcaption>{e(NAME)}, {e(C.LOCATION)}. {e(C.AVAILABILITY)}.</figcaption></figure></div>']
    for en in ENTRIES:
        chart = _chart_for(en["n"])
        out.append(f'<div class="pane" data-pane="w{en["n"]}" aria-hidden="true"><div class="fill">'
                   f'<span class="ttl">{e(en["title"])}</span><div class="big">{e(en["metric"])}</div>'
                   f'<p class="note">{e(en["metric_note"])}</p>{chart}</div></div>')
    for k, (f, cap, alt) in PLACES.items():
        out.append(f'<div class="pane" data-pane="{k}" aria-hidden="true"><figure><img src="places/{f}" width="1500" height="1000" '
                   f'alt="{e(alt)}" loading="lazy" decoding="async"><figcaption>{e(cap)} <a href="#credits">Photo credit</a></figcaption></figure></div>')
    return "".join(out)


def mq_table():
    order = [2, 1, 3, 4]          # Med-Qwen first, then its base, then the two comparison models (left to right)
    head = "".join(f'<th class="c{i}{" us" if i == 2 else ""}" scope="col">{e("Med-Qwen" if i == 2 else MQ_HEAD[i])}</th>' for i in order)
    head = '<th scope="col">Benchmark</th>' + head
    body = ""
    for r in MQ_ROWS:
        tds = "".join(f'<td class="c{i}{" us" if i == 2 else ""}" data-v="{e(r[i])}">{e(r[i])}</td>' for i in order)
        body += f'<tr><th scope="row">{e(r[0])}</th>{tds}</tr>'
    return (f'<div class="tblw"><table class="cmp" id="cmp" data-sel="all">'
            f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
            f'<p class="cap">PubMedQA, MedQA (USMLE 4-option), GPQA Diamond, MedMCQA, MMLU Med aggregate and AfriMed-QA. '
            f'Zero-shot, greedy inference with normalized choice log-probabilities. '
            f'Source: <a class="ln" href="https://huggingface.co/adi274903/Med-Qwen-3.5-4B-Instruct" rel="noopener">model card of the Med-Qwen-3.5-4B-Instruct release</a>. The latest model, trained further with RLVR, is <a class="ln" href="https://huggingface.co/adi274903/Med-Qwen-3.5-4B-it" rel="noopener">Med-Qwen-3.5-4B-it</a>.</p>')


def mq_verdict():
    w = {n: sum(won) for n, won in mq_wins()}
    k = list(w.items())
    return (f"Med-Qwen beats MedGemma-1.5-4B-it on <em>{words_of(k[0][1])} of six</em> benchmarks and Gemma-4-E4B-it on "
            f"<em>{words_of(k[1][1])} of six</em>. It trails its own base model on three.")


def skills_list():
    hits = [(c, [lab for lab, bl in MCOLS if any(re.search(rx, b, re.I) for b in bl)],
             sum(1 for _, bl in MCOLS for b in bl if re.search(rx, b, re.I))) for c, rx in CONCEPTS]
    mx = max(t for _, _, t in hits)
    return "".join(
        f'<li data-reveal><span class="a">{e(c)}</span><div class="m"><div class="bar2" role="img" aria-label="{e(c)}: {t} resume bullets">'
        f'<i style="--w:{100 * t / mx:.0f}%"></i></div><span class="who">{t} {'bullet' if t == 1 else 'bullets'} across {e(", ".join(who))}</span></div></li>'
        for c, who, t in hits)


def home():
    ledes = "".join(f'<p class="lede" data-lede="{k}"{"" if k == "ai" else " hidden"}>{fmt(v)}</p>' for k, v in LEDE.items())
    seg = "".join(f'<button type="button" data-track="{k}" aria-pressed="{str(k == "all").lower()}">{e(v)}</button>'
                  for k, v in TRACKS)
    works = "".join(work_row(en) for en in ENTRIES)
    pool = " ".join([" ".join(en["bullets"]) + " " + " ".join(en["tags"]) for en in ENTRIES]
                    + [" ".join(x["bullets"]) for x in C.EXPERIENCE] + [" ".join(p["bullets"]) for p in C.PROJECTS])
    tools = "".join(f"<li>{ic(s, n)}<span>{e(n)}</span></li>" for s, n in icons_in(pool))

    def _city(org):
        return next((v for k, v in CITY_OF.items() if k in org), "")
    xp = "".join(
        f'<details{" open" if i == 0 else ""} data-city="{_city(x["org"])}" data-reveal><summary>{co_logo(x["org"])}'
        f'<span class="org">{e(x["org"])}</span><span class="when">{e(x["period"])}</span>'
        f'<span class="role">{e(x["role"])}{", " + e(x["meta"]) if x["meta"] else ""}</span>'
        f'<span class="lgs">{"".join(ic(s, n) for s, n in icons_in(" ".join(x["bullets"])))}</span></summary>'
        f'<ul>{"".join(f"<li>{fmt(b)}</li>" for b in x["bullets"])}</ul></details>'
        for i, x in enumerate(C.EXPERIENCE))
    pubs = "".join(f'<li><a href="{p["url"]}" rel="noopener">{e(p["title"])}</a>'
                   f'<span>{e(p["venue"])}{"" if p["year"] in p["venue"] else ", " + e(p["year"])}</span></li>' for p in C.PUBLICATIONS)
    HONOR_LINKS = {"Kaggle": "https://www.kaggle.com/competitions/11785-hw-2-p-2-face-verification-spring-2025/leaderboard",
                   "AMIA": "https://workshopamia2025.github.io/AMIA-KDDM-2025/posters/KDDM_Poster%5BCMU%5D.pdf"}

    def _hon(h):
        t, o, d, w = honor(h)
        url = next((u for k, u in HONOR_LINKS.items() if k in h), "")
        title = f'<a href="{url}" target="_blank" rel="noopener">{e(t)}</a>' if url else e(t)
        sub = ", ".join(x for x in (d, w) if x)
        return f'<li>{title}{(", " + e(o)) if o else ""}<span>{e(sub)}</span></li>'
    _SEASON = {"winter": 0.0, "spring": 0.25, "summer": 0.5, "fall": 0.75}
    _MONTH = {m: i / 12 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}

    def _when(h):
        w = honor(h)[3].lower()
        y = re.search(r"(20\d\d)", w)
        if not y:
            return 0.0
        word = re.match(r"[a-z]+", w)
        frac = _SEASON.get(word.group(0), _MONTH.get(word.group(0)[:3], 0.4)) if word else 0.4
        return int(y.group(1)) + frac

    hon = "".join(_hon(h) for h in sorted(C.HONORS, key=_when, reverse=True))
    edu = "".join(f'<li>{e(d["degree"])}<span>{e(d["school"])}, {e(d["meta"].replace(" | ", ", "))}</span></li>' for d in C.EDUCATION)
    first, last = NAME.split()[0], NAME.split()[1]
    return f"""<div class="split">
<aside class="stage" aria-label="Portrait, and the figure or place for whatever you are reading">{stage_panes()}</aside>
<div class="read">
<section class="hero" id="top">
<h1 data-rise style="--i:0">{e(first)} {e(last)}</h1>
<p class="role" data-rise style="--i:1">{e(ROLE)} for clinical and financial data.</p>
<p class="where" data-rise style="--i:2">{e(C.LOCATION)}. {e(C.AVAILABILITY)}.</p>
<div data-rise style="--i:3">{ledes}</div>
<p class="motto" data-rise style="--i:4">{e(MOTTO)}</p>
<div class="cta" data-rise style="--i:5"><a class="btn p" href="contact.html">Book a chat</a><a class="btn" href="ask.html">Ask my record</a><a class="btn" href="{C.LINKEDIN}" rel="noopener">LinkedIn</a></div>
<div class="tracks" data-rise style="--i:6"><span>See the work for</span><div class="seg" role="group" aria-label="Role track">{seg}</div></div>
</section>

<section id="work"><h2 class="sh w" data-reveal>Eight projects, each with its number.</h2>
<p data-reveal>Choose a role track above and the projects reorder. Pick any project to see its numbers.</p>
<ol class="works" id="grid">{works}</ol></section>

<section id="experience"><h2 class="sh" data-reveal>Roles, as written.</h2>
<div class="xp">{xp}</div></section>
</div></div>

<section class="full" id="results"><div class="in sb">
<div><h2 class="sh w" data-reveal>Where Med-Qwen wins and loses.</h2>
<p class="mut" data-reveal>Pick a model to compare it with. Same six benchmarks, same zero-shot setup.</p>
<div class="pick" id="pick" role="group" aria-label="Compare Med-Qwen with" hidden></div>
<p class="verdict" id="verdict" aria-live="polite">{mq_verdict()}</p></div>
<div data-reveal>{mq_table()}</div></div></section>

<section class="full" id="stack"><div class="in">
<h2 class="sh w" data-reveal>Skills, counted rather than claimed.</h2>
<p class="mut" data-reveal style="margin-bottom:30px">Each bar is the number of resume bullets that mention the area, computed from the text and not self-rated.</p>
<ul class="tools" aria-label="Tools used across the work">{tools}</ul>
<ul class="sk">{skills_list()}</ul></div></section>

<section class="full" id="more"><div class="in names">
<div data-reveal><h3>Papers</h3><ul>{pubs}</ul></div>
<div data-reveal><h3>Education</h3><ul>{edu}</ul></div>
<div data-reveal><h3>Recognition</h3><ul>{hon}</ul></div></div></section>

<section class="visit" id="contact"><img src="places/houston.webp" width="1500" height="502" alt="{e(PLACES['houston'][2])}" loading="lazy" decoding="async">
<div class="card" data-reveal><h2>Let’s talk.</h2>
<p>I am based in {e(C.LOCATION)} and {e(C.AVAILABILITY.lower())}. Tell me about the role or the project and I will reply.</p>
<a class="mail" href="{MAIL}">{e(C.EMAIL)}</a>
<div class="links"><a href="{C.LINKEDIN}" rel="noopener">LinkedIn</a><a href="{C.GITHUB}" rel="noopener">GitHub</a><a href="{C.ARXIV}" rel="noopener">arXiv</a></div>
<a class="btn p" href="contact.html">Book a chat</a></div></section>"""


def case(i):
    en = ENTRIES[i]
    prev_ = ENTRIES[i - 1] if i else None
    next_ = ENTRIES[i + 1] if i + 1 < len(ENTRIES) else None
    tmap = dict(TRACKS)
    trk = "".join(f"<li>{e(tmap[t])}</li>" for t in en["tracks"].split())
    tags = "".join(f"<li>{''.join(ic(s, n) for s, n in icons_in(t)[:1])}{e(t)}</li>" for t in en["tags"])
    bl = "".join(f"<li>{fmt(b)}</li>" for b in en["bullets"])
    link = (f'<a class="btn p" href="{_linkify(en["url"])}" rel="noopener">View project</a>' if en["url"] else "")
    pn = ((f'<a class="btn" href="{prev_["slug"]}">Previous: {e(prev_["title"])}</a>') if prev_ else
          '<a class="btn" href="index.html#work">All work</a>')
    pn += (f'<a class="btn" href="{next_["slug"]}">Next: {e(next_["title"])}</a>' if next_ else
           '<a class="btn p" href="contact.html">Get in touch</a>')
    src = f'{e(en["year"])}' + (f', {e(en["source"])}' if en["source"] else "")
    body = f"""<div class="page">
<div class="top">
<div><h1 data-rise>{e(en["title"])}</h1>
<p class="sub" data-rise style="--i:1">{e(en["kicker"])}, {src}</p>
<div class="bigm" data-rise style="--i:2"><b>{e(en["metric"])}</b><span>{e(en["metric_note"])}</span></div></div>
<div class="fig" data-rise style="--i:3">{en["chart"]}</div></div>
<div class="cols"><div><h3 data-reveal>What I built</h3><ul class="b">{"".join(f'<li data-reveal>{fmt(b)}</li>' for b in en["bullets"])}</ul>
<p class="cap" data-reveal>{fmt(en["line"])}</p><div class="cta" data-reveal>{link}</div></div>
<div><h3 data-reveal>Stack</h3><ul class="chips" data-reveal>{tags}</ul>
<h3 data-reveal>Relevant to</h3><ul class="chips" data-reveal>{trk}</ul></div></div>
{('<div style="margin-top:clamp(48px,6vw,88px)" data-reveal><h2 class="sh w">The full comparison.</h2>' + mq_table() + '</div>') if en["n"] == "01" else ""}
<div class="pn" data-reveal>{pn}</div></div>"""
    return shell(f'{en["title"]} — {NAME}', en["metric"] + " — " + en["metric_note"], body, bodycls=' class="sub"')


HOW_STEPS = [   # (title, lines) for the example question "What did he do at EMMA AI?"
    ("Question", ["What did he do", "at EMMA AI?"]),
    ("Read it", ["tokens: emma, ai", "intent: describe", "typos fixed"]),
    ("Find section", ["match: EMMA", "metadata: project", "health \u00b7 AI \u00b7 2025"]),
    ("Rank lines", None),
    ("Quote", ["best line,", "numbers in bold,", "+ source line"]),
]


def how_svg(vertical=False):
    """Animated pipeline diagram (SMIL packet + CSS highlight loop). Static for prefers-reduced-motion."""
    bw, bh, gap = (300, 100, 28) if vertical else (142, 132, 16)
    n = len(HOW_STEPS)
    W, H = (330, 24 + n * (bh + gap) - gap + 24) if vertical else (24 + n * (bw + gap) - gap + 24, 190)
    out = []
    pos = []
    for i, (title, lines) in enumerate(HOW_STEPS):
        x, y = (15, 24 + i * (bh + gap)) if vertical else (24 + i * (bw + gap), 28)
        pos.append((x, y))
        g = [f'<g class="hs" opacity=".35"><animate attributeName="opacity" values=".35;1;1;.35;.35" keyTimes="0;0.04;0.14;0.19;1" dur="7.5s" begin="{1.5 * i - 0.3:.1f}s" repeatCount="indefinite"/>',
             f'<rect class="hb" x="{x}" y="{y}" width="{bw}" height="{bh}" />',
             f'<text class="ht" x="{x + 14}" y="{y + 24}">{i + 1}. {e(title)}</text>']
        if not lines:
            g.append(f'<text class="hl sm" x="{x + 14}" y="{y + bh - 10}">similarity</text>')
        if lines:
            for k, t in enumerate(lines):
                tl = f' textLength="{bw - 28}" lengthAdjust="spacingAndGlyphs"' if len(t) * 6.9 > bw - 28 else ""   # never wider than the box
                g.append(f'<text class="hl" x="{x + 14}" y="{y + 46 + k * 19}"{tl}>{e(t)}</text>')
        else:                                   # cosine bars: the winner is the accent colour
            for k, (sc, win) in enumerate(((0.57, True), (0.21, False), (0.11, False))):
                yy = y + 40 + k * 26
                g.append(f'<rect class="hbt" x="{x + 14}" y="{yy}" width="{bw - 28}" height="10"/>'
                         f'<rect class="hbar{" win" if win else ""}" x="{x + 14}" y="{yy}" width="{(bw - 28) * sc / 0.62:.1f}" height="10"/>'
                         )
        g.append("</g>")
        out.append("".join(g))
    arrows = []
    for i in range(n - 1):
        (x0, y0), (x1, y1) = pos[i], pos[i + 1]
        if vertical:
            arrows.append(f'<path class="ha" d="M{x0 + bw / 2} {y0 + bh + 4} L{x1 + bw / 2} {y1 - 6}" marker-end="url(#ah)"/>')
        else:
            arrows.append(f'<path class="ha" d="M{x0 + bw + 3} {y0 + bh / 2} L{x1 - 5} {y1 + bh / 2}" marker-end="url(#ah)"/>')
    if vertical:
        tx = 7
        path = f"M{tx} {pos[0][1] + bh / 2} L{tx} {pos[-1][1] + bh / 2}"
        track = f'<path class="ha" d="{path}"/>'
    else:
        ty = pos[0][1] + bh + 16
        path = f"M{pos[0][0] + bw / 2} {ty} L{pos[-1][0] + bw / 2} {ty}"
        track = f'<path class="ha" d="{path}"/>'
    packet = (f'<circle class="hp" r="6"><animateMotion dur="7.5s" repeatCount="indefinite" path="{path}" keyPoints="0;1;1" keyTimes="0;0.8;1" calcMode="linear"/></circle>')
    defs = '<defs><marker id="ah" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L8 4 L0 8 z" class="hah"/></marker></defs>'
    label = "How the Ask page works: question, read it, find the section, rank the lines, quote the best match"
    return f'<svg class="hws" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">{defs}{"".join(arrows)}{track}{"".join(out)}{packet}</svg>'


def page_ask():
    data = ask_data()
    n_sec = len(data["sections"]); n_lines = sum(len(s["chunks"]) for s in data["sections"])
    return f"""<div class="page"><div class="askn">
<h1 data-rise>Ask about my work.</h1>
<p class="intro s" data-rise style="--i:1">Ask about my projects, results, roles or papers, or which of my work fits a role.</p>
<div class="hwbar"><button class="hwb" id="hwb" type="button" aria-expanded="false" aria-controls="hwp">How it works <i aria-hidden="true">▾</i></button></div>
<div class="hwp" id="hwp" hidden><div class="hwd" aria-hidden="false"><div class="dw">{how_svg(False)}</div><div class="mw">{how_svg(True)}</div></div>
<ol>
<li><b>Chunk.</b> My record is cut into {words_of(n_sec)} sections, one per project, role or topic, split into {words_of(n_lines)} short lines. Each section carries metadata: project, organisation, year, domain, topics and tools.</li>
<li><b>Match.</b> No AI model runs here. Each question and each line becomes a TF-IDF vector; names such as EMMA or Tata pick the section, metadata filters pick projects by topic or role, and cosine similarity picks the best lines.</li>
<li><b>Quote.</b> A fixed template writes the reply around those lines. Same question, same answer, every time.</li></ol>
<p class="cap">It refuses anything outside my record, such as coding help or general questions. It was checked on fifty-six questions I wrote; every set was used to tune it, so treat that as a regression check, not a blind test. With this panel open, each answer also shows its similarity score and metadata tags. <a class="ln" href="how-it-works.gif" download>Download this diagram as a GIF</a>.</p></div>
<div class="askp" id="askp"><div class="thread" id="thread" aria-live="polite"></div>
<div class="starts" id="starts" aria-label="Suggested questions"></div>
<form id="askf" class="askf"><input id="askq" type="text" maxlength="300" autocomplete="off" placeholder="Ask about EMMA AI, Med-Qwen, Value Global, fintech work…" aria-label="Your question"><button type="submit">Ask</button></form></div>
</div></div>"""


FORM_ENDPOINT = "https://formsubmit.co/ajax/" + C.EMAIL      # FormSubmit: free, no account; first message needs a one-time confirmation


def page_contact():
    return f"""<div class="page">
<h1 data-rise>Let’s talk.</h1>
<p class="intro s" data-rise style="--i:1">Tell me who you are and what you have in mind: a role, a project, a question about my work. Your message goes straight to my inbox and I reply to the email you give.</p>
<div class="askw" style="margin-top:clamp(34px,5vw,64px)">
<div class="cfw"><form id="cf" action="{FORM_ENDPOINT}" method="post" novalidate>
<div class="fr"><label for="cn">Your name</label><input id="cn" name="name" type="text" autocomplete="name" maxlength="120" required></div>
<div class="fr"><label for="ce">Your email</label><input id="ce" name="email" type="email" autocomplete="email" maxlength="200" required></div>
<div class="fr"><label for="cs">Subject</label><input id="cs" name="subject" type="text" maxlength="160" placeholder="e.g. AI engineer role at your company" required></div>
<div class="fr"><label for="cm">Message</label><textarea id="cm" name="message" rows="7" maxlength="4000" required></textarea></div>
<input type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;opacity:0;height:0;width:0">
<input type="hidden" name="_subject" value="Portfolio message"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false">
<button class="btn p" type="submit">Send message</button>
<p id="cmsg" class="cmsg" role="status" aria-live="polite"></p></form>
<div id="cdone" class="cdone" tabindex="-1" hidden><h2>Message sent.</h2><p>Thank you. I will reply to the email you gave.</p>
<p style="margin-top:18px"><a class="btn" href="index.html">Back to the portfolio</a></p></div></div>
<aside class="how"><h3>Or reach me directly</h3>
<div class="direct"><a href="{MAIL}">{e(C.EMAIL)}</a><a href="{C.LINKEDIN}" rel="noopener">LinkedIn</a><a href="{C.GITHUB}" rel="noopener">GitHub</a></div>
<p class="cap">The form sends your message by email through FormSubmit. Nothing is stored on this site. Based in {e(C.LOCATION)}; {e(C.AVAILABILITY.lower())}.</p></aside></div></div>"""


def build():
    DIST.mkdir(exist_ok=True)
    (DIST / "styles.css").write_text((HERE / "src/styles.css").read_text())
    import shutil
    shutil.rmtree(DIST / "logos", ignore_errors=True)
    (DIST / "logos").mkdir(exist_ok=True)
    for f in (HERE / "src/assets/logos").iterdir():
        (DIST / "logos" / f.name).write_bytes(f.read_bytes())
    import json
    (DIST / "ask-data.json").write_text(json.dumps(ask_data(), ensure_ascii=False, separators=(",", ":")))
    (DIST / "engine.js").write_text((HERE / "src/engine.js").read_text())
    (DIST / "how-it-works.gif").write_bytes((HERE / "src/assets/how-it-works.gif").read_bytes()) if (HERE / "src/assets/how-it-works.gif").exists() else None
    (DIST / "icons.svg").write_text((HERE / "src/assets/icons.svg").read_text())
    (DIST / "me.webp").write_bytes((HERE / "src/assets/me.webp").read_bytes())
    for sub in ("fonts", "places"):
        shutil.rmtree(DIST / sub, ignore_errors=True)
        (DIST / sub).mkdir(exist_ok=True)
        for f in (HERE / "src/assets" / sub).iterdir():
            if f.suffix in (".woff2", ".webp"):
                (DIST / sub / f.name).write_bytes(f.read_bytes())
    (DIST / "app.js").write_text((HERE / "src/app.js").read_text())
    (DIST / "ask.js").write_text((HERE / "src/ask.js").read_text())
    (DIST / "contact.js").write_text((HERE / "src/contact.js").read_text())
    (DIST / "contact.html").write_text(shell(f"Book a chat \u2014 {NAME}", "Send Aditya a message: name, email, subject and message.", page_contact(), page="contact.html", bodycls=' class="sub"', extra_js=f'<script src="contact.js?v={VER}" defer></script>'))
    (DIST / "ask.html").write_text(shell(f"Ask my record \u2014 {NAME}", "Ask about Aditya\u2019s projects, results and experience. Answers are quoted from his record by cosine similarity, with no AI model.", page_ask(), page="ask.html", fab=False, bodycls=' class="sub"', extra_js=f'<script src="engine.js?v={VER}" defer></script><script src="ask.js?v={VER}" defer></script>'))
    (DIST / "index.html").write_text(shell(
        f"{NAME} — {ROLE}",
        "AI engineer for clinical and financial data: production RAG, governed agents, "
        "evaluation and fine-tuning, each with the number it produced.", home(), credits=True, bodycls=' class="home"'))
    for i, en in enumerate(ENTRIES):
        (DIST / en["slug"]).write_text(case(i))


def audit():
    blob = gt.blob(gt.load()).replace(",", "")
    bad_r, bad_n = set(), set()
    for p in sorted(DIST.glob("*.html")):
        h = p.read_text()
        h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S)
        h = re.sub(r'<p class="cr"[^>]*>.*?</p>', " ", h, flags=re.S)       # third-party photo credits
        text = re.sub(r"<[^>]+>", " ", h)
        for t in C.RETIRED:
            if t in text:
                bad_r.add((p.name, t))
        for num in re.findall(r"\b\d[\d,]*(?:\.\d+)?", text):
            k = num.replace(",", "")
            if re.match(r"^0?\d$", k):      # ordinals and one-digit counts
                continue
            if not re.search(r"(?<!\d)" + re.escape(k) + r"(?!\d)", blob):
                bad_n.add((p.name, num))
    return bad_r, bad_n


if __name__ == "__main__":
    build()
    r, n = audit()
    sz = {p.name: p.stat().st_size for p in DIST.iterdir()}
    print(f"built {len(sz)} files; index {sz['index.html']:,} B, css {sz['styles.css']:,} B, js {sz['app.js']:,} B")
    print("retired metrics:", sorted(r) or "none")
    print("numerals not in GT3:", sorted(n) or "none")
    sys.exit(1 if (r or n) else 0)
