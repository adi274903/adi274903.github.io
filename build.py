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
import charts as CH  # noqa: E402
import content as C  # noqa: E402
import gt  # noqa: E402
import webcontent as S  # noqa: E402

STATIC = "--static" in sys.argv           # published build: no chat button (Pages cannot run the model)
DIST = HERE / ("docs" if STATIC else "dist")
import hashlib
VER = hashlib.md5(b"".join((HERE / "src" / f).read_bytes() for f in ("styles.css", "app.js", "chat.js"))).hexdigest()[:8]
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
    "fintech": "I build and evaluate AI for financial data: credit-bureau reporting cut from 3 days to 2 hours at "
               "Tata Capital, a fraud-identification model at 0.86 F1 at Jocata, and governed agent access to "
               "Oracle E-Business Suite at Value Global.",
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
                ("0.86", "F1 for fraud identification, Jocata"),
                ("30-40", "governed MCP queries on Oracle E-Business Suite"),
                ("82% → 91%", "CPT/HCPCS code selection")],
    "health": [("66.20", "PubMedQA for Med-Qwen, vs 45.60 for its base"),
               ("+25%", "physician-rated accuracy + completeness, EMMA"),
               ("17,167", "schema-bound evaluation records"),
               ("82% → 91%", "CPT/HCPCS code selection")],
}


def _metric_row(value):
    return next(r for r in C.METRICS if r[1] == value)



# ------------------------------------------------------------- logos, bold numbers, links
ICON_RULES = [("qwen", r"qwen", "Qwen"), ("googlecloud", r"\bGCP\b|Google Cloud", "Google Cloud"),
              ("googlegemini", r"\bGemini\b", "Gemini"), ("huggingface", r"hugging ?face", "Hugging Face"),
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


COLOGOS = [("Jocata", "img", "jocata.webp"), ("Carnegie", "img", "cmu.webp"), ("Tata", "icon", "tata")]


def co_logo(org):
    """Left-hand tile for an employer: its logo if we have one, otherwise initials (decorative)."""
    for key, kind, val in COLOGOS:
        if key in org:
            if kind == "img":
                return f'<span class="co"><img src="logos/{val}" alt="" width="32" height="32" loading="lazy" decoding="async"></span>'
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


# ---------------------------------------------------------------------- entries
def _chart_for(n, w=CH.W):
    if n == "01":
        return CH.hbars("Med-Qwen-3.5-4B-Instruct · zero-shot greedy", [
            ("PubMedQA · base", 45.60, "45.60", False),
            ("PubMedQA · Med-Qwen", 66.20, "66.20", True),
            ("MMLU Med", 80.72, "80.72", False), ("MedQA", 67.95, "67.95", False),
            ("AfriMed-QA", 64.80, "64.80", False), ("GPQA Diamond", 50.51, "50.51", False),
            ("MedMCQA", 33.20, "33.20", False)], maxv=100,
            note="base = Qwen3.5-4B-Base", label="Med-Qwen benchmark scores", w=w)
    if n == "02":
        return CH.hbars("EMMA · what the +25% rests on", [
            ("+25% accuracy", 25, "+25%", True), ("contexts", 20, "20", False),
            ("physician surveys", 2, "2", False)],
            maxv=50, note="different units, one shared axis for scale only",
            label="EMMA scale facts", w=w)
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
      "05": "ai health fintech", "06": "ai fintech"}
bul = {"01": C.PROJECTS[0]["bullets"], "02": C.PROJECTS[1]["bullets"], "03": C.PROJECTS[2]["bullets"],
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
    en["chart"] = f'<div class="dw">{_chart_for(en["n"])}</div><div class="mw">{_chart_for(en["n"], 360)}</div>'
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
        "%3Crect width='32' height='32' rx='7' fill='%230b0d12'/%3E%3Ctext x='16' y='22' "
        "text-anchor='middle' font-family='Arial' font-size='15' font-weight='700' fill='%23eceef4'"
        "%3EAS%3C/text%3E%3Ccircle cx='26' cy='7' r='3' fill='%23ffc46b'/%3E%3C/svg%3E")
MAIL = f"mailto:{C.EMAIL}?subject=" + "Let%27s%20talk"


CHAT_BTN = "" if STATIC else ("<button class=\"fab\" id=\"chat-open\" type=\"button\" aria-controls=\"chat\" aria-expanded=\"false\"><i></i>Ask my record</button>\n")


def shell(title, desc, body, depth_attr="", page="index"):
    nav = ('<a class="opt" href="index.html#work">Work</a><a class="opt mh" href="index.html#results">Results</a>'
           '<a class="opt mh" href="index.html#stack">Stack</a><a class="opt" href="index.html#contact">Contact</a>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#0b0d12">
<link rel="icon" href="{ICON}"><link rel="stylesheet" href="styles.css?v={VER}">
<script>try{{var t=localStorage.getItem("th");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head><body>
<header class="top"><div class="wrap"><a class="wm" href="index.html"><i></i>{e(NAME)}</a>
<nav>{nav}<button class="tg" id="tg" type="button" aria-label="Toggle light and dark theme">Theme</button></nav></div></header>
<main>{body}</main>
<footer id="contact"><div class="wrap">
<span class="k">Let’s talk</span>
<p style="margin:14px 0 4px"><a class="mail" href="{MAIL}">{e(C.EMAIL)}</a></p>
<div class="l"><a href="{C.LINKEDIN}" rel="noopener">LinkedIn ↗</a><a href="{C.GITHUB}" rel="noopener">GitHub ↗</a><a href="{C.ARXIV}" rel="noopener">arXiv ↗</a></div>
<p>{e(NAME)} · {e(ROLE)} · {e(C.CONTACT_LINE)}</p>
<p>Logos are trademarks of their owners; icons from Simple Icons (CC0).</p>
</div></footer>
{CHAT_BTN}<script src="app.js?v={VER}" defer></script></body></html>"""


def card(en):
    tags = "".join(f"<li>{''.join(ic(s, n) for s, n, in icons_in(t)[:1])}{e(t)}</li>" for t in en["tags"][:4])
    return (f'<a class="card cs" href="{en["slug"]}" data-tr="{en["tracks"]}">'
            f'<div class="m"><span class="mono">{e(en["n"])} · {e(en["kicker"])}</span>'
            f'<span class="mono">{e(en["year"])}</span></div>'
            f'<h3>{e(en["title"])}</h3>'
            f'<div><div class="big">{e(en["metric"])}</div><div class="bn">{e(en["metric_note"])}</div></div>'
            f'{en["chart"]}<ul class="chips">{tags}</ul></a>')


def home():
    ledes = "".join(f'<p class="lede" data-lede="{k}"{"" if k == "ai" else " hidden"}>{fmt(v)}</p>'
                    for k, v in LEDE.items())
    stats = "".join(
        f'<div class="stats" data-stats="{k}"{"" if k == "ai" else " hidden"}>'
        + "".join(f"<div><b>{e(a)}</b><span>{e(b)}</span></div>" for a, b in v) + "</div>"
        for k, v in STATS.items())
    seg = "".join(f'<button type="button" data-track="{k}" aria-pressed="{str(k == "all").lower()}">{e(v)}</button>'
                  for k, v in TRACKS)
    grid = "".join(card(en) for en in ENTRIES)
    panels = "".join(
        f'<figure class="dp"><span class="k">{e(k)}</span><h3>{e(t)}</h3>{svg}</figure>'
        for k, t, svg in [
            ("Latency", "Retrieval cut from ~8 s to 2 s", ENTRIES[5]["chart"]),
            ("Workflow", "Reporting prep cut from 3 days to 2 hours", ENTRIES[6]["chart"]),
            ("Accuracy", "Code selection raised from 82% to 91%", ENTRIES[4]["chart"]),
            ("Benchmarks", "A 4.2B clinical model against its base", ENTRIES[0]["chart"]),
            ("Evaluation", "Why the retrieval layer was the limit", ENTRIES[2]["chart"]),
            ("Scale", "Records from 15,944 papers, zero skew", ENTRIES[3]["chart"])])
    pool = " ".join([" ".join(en["bullets"]) + " " + " ".join(en["tags"]) for en in ENTRIES]
                    + [" ".join(x["bullets"]) for x in C.EXPERIENCE] + [" ".join(p["bullets"]) for p in C.PROJECTS])
    tools = "".join(f"<li>{ic(s, n)}<span>{e(n)}</span></li>" for s, n in icons_in(pool))
    xp = "".join(
        f'<details{" open" if i == 0 else ""}><summary>{co_logo(x["org"])}<b>{e(x["org"])}</b><span>{e(x["period"])}</span>'
        f'<small>{e(x["role"])}{" · " + e(x["meta"]) if x["meta"] else ""}</small>'
        f'<span class="lg">{"".join(ic(s, n) for s, n in icons_in(" ".join(x["bullets"])))}</span></summary>'
        f'<ul>{"".join(f"<li>{fmt(b)}</li>" for b in x["bullets"])}</ul></details>'
        for i, x in enumerate(C.EXPERIENCE))
    pubs = "".join(f'<li><a href="{p["url"]}" rel="noopener"><b>{e(p["title"])}</b>'
                   f'<span>{e(p["venue"])}{"" if p["year"] in p["venue"] else " \u00b7 " + e(p["year"])} \u2197</span></a></li>'
                   for p in C.PUBLICATIONS)
    def _hon(h):
        t, o, d, w = honor(h)
        return (f'<li class="hn"><div><b>{e(t)}</b>' + (f'<span class="org">{e(o)}</span>' if o else "") + "</div>"
                + (f"<p>{fmt(d)}</p>" if d else "") + (f'<time class="wh">{e(w)}</time>' if w else "") + "</li>")
    hon = "".join(_hon(h) for h in C.HONORS)
    edu = "".join(f'<li><b>{e(d["degree"])}</b><span>{e(d["school"])} \u00b7 {e(d["meta"])}</span></li>'
                  for d in C.EDUCATION)
    return f"""<section class="hero"><div class="wrap">
<div class="hg"><div class="hl">
<div class="k"><b>{e(ROLE)}</b><span>{e(C.LOCATION)}</span><span>{e(C.AVAILABILITY)}</span></div>
<h1 class="name"><span>{e(NAME.split()[0])}</span><span>{e(NAME.split()[1])}</span></h1>
{ledes}
<p class="motto">{e(MOTTO)}</p>
<div class="cta"><a class="btn p" href="{MAIL}">Book a chat</a><a class="btn" href="#work">See the work</a>
<a class="btn" href="{C.LINKEDIN}" rel="noopener">LinkedIn \u2197</a></div>
<div class="tracks"><span class="k">View for</span><div class="seg" role="group" aria-label="Role track">{seg}</div></div>
</div><figure class="pt hp"><img src="me.webp" width="320" height="320" alt="Portrait of {e(NAME)}" decoding="async" fetchpriority="high"></figure></div>
{stats}</div></section>

<section id="work"><div class="wrap"><div class="sh"><span class="k">Selected work</span>
<h2>Eight projects, each with the number it produced.</h2>
<p>Pick a role track above and the evidence reorders itself. Open any card for the full case.</p></div>
<div class="grid" id="grid">{grid}</div></div></section>

<section id="results"><div class="wrap"><div class="sh"><span class="k">Measured outcomes</span>
<h2>Results, drawn to scale.</h2><p>Every bar is a number from the record, on one shared scale per chart.</p></div>
<div class="dash">{panels}</div></div></section>

<section id="stack"><div class="wrap"><div class="sh"><span class="k">Where the skills show up</span>
<h2>Skills, counted rather than claimed.</h2>
<p>Each cell is the number of resume bullets in that project or role that mention the area. Computed from the text, not self-rated.</p></div>
<ul class="tools" aria-label="Tools used across the work">{tools}</ul>
<div class="scroll" style="margin-top:22px">{matrix_svg()}</div>
<p class="cap">A darker cell means more bullets. Retrieval and evaluation run through most of the work; fine-tuning is concentrated in one project and the 4.2B model behind it.</p>
<div class="sh" style="margin-top:clamp(40px,5vw,70px)"><span class="k">Timeline</span><h2>August 2023 to now.</h2></div>
<div class="scroll">{CH.timeline(TIMELINE)}</div></div></section>

<section id="experience"><div class="wrap"><div class="sh"><span class="k">Experience</span>
<h2>Roles, every bullet as written.</h2></div>{xp}</div></section>

<section id="more"><div class="wrap two">
<div><div class="sh"><span class="k">Publications</span><h2>{["Zero","One","Two","Three","Four"][len(C.PUBLICATIONS)]} papers.</h2></div><ul class="rows">{pubs}</ul>
<div class="sh" style="margin-top:clamp(32px,4vw,56px)"><span class="k">Education</span><h2>Where I studied.</h2></div><ul class="rows">{edu}</ul></div>
<div><div class="sh"><span class="k">Recognition</span><h2>And a few more.</h2></div><ul class="hons">{hon}</ul></div></div></section>"""


def case(i):
    en = ENTRIES[i]
    prev_ = ENTRIES[i - 1] if i else None
    next_ = ENTRIES[i + 1] if i + 1 < len(ENTRIES) else None
    tmap = dict(TRACKS)
    trk = "".join(f"<li>{e(tmap[t])}</li>" for t in en["tracks"].split())
    tags = "".join(f"<li>{''.join(ic(s, n) for s, n in icons_in(t)[:1])}{e(t)}</li>" for t in en["tags"])
    bl = "".join(f"<li>{fmt(b)}</li>" for b in en["bullets"])
    link = (f'<a class="btn" href="{_linkify(en["url"])}" rel="noopener">View project ↗</a>'
            if en["url"] else "")
    pn = ((f'<a class="btn" href="{prev_["slug"]}">← {e(prev_["title"])}</a>') if prev_ else
          '<a class="btn" href="index.html#work">← All work</a>')
    pn += (f'<a class="btn" href="{next_["slug"]}">{e(next_["title"])} →</a>' if next_ else
           '<a class="btn" href="index.html#contact">Get in touch →</a>')
    body = f"""<section class="case" style="border:0"><div class="wrap">
<div class="crumb mono"><span>Case {e(en["n"])} / 0{len(ENTRIES)} · {e(en["kicker"])}</span><span>{e(en["year"])} · {e(en["source"])}</span></div>
<h1>{e(en["title"])}</h1>
<div class="bigm"><b>{e(en["metric"])}</b><span>{e(en["metric_note"])}</span></div>
<div class="cols"><div><span class="k">What I built</span><ul class="b" style="margin-top:14px">{bl}</ul>
<p class="cap">{fmt(en["line"])}</p><div class="cta">{link}</div></div>
<div><div class="scroll" style="padding:18px">{en["chart"]}</div>
<span class="k" style="display:block;margin-top:22px">Stack</span><ul class="chips" style="margin-top:10px">{tags}</ul>
<span class="k" style="display:block;margin-top:22px">Relevant to</span><ul class="chips" style="margin-top:10px">{trk}</ul></div></div>
<div class="pn">{pn}</div></div></section>"""
    return shell(f'{en["title"]} — {NAME}', en["metric"] + " — " + en["metric_note"], body)


def build():
    DIST.mkdir(exist_ok=True)
    (DIST / "styles.css").write_text((HERE / "src/styles.css").read_text())
    (DIST / "logos").mkdir(exist_ok=True)
    for f in (HERE / "src/assets/logos").iterdir():
        (DIST / "logos" / f.name).write_bytes(f.read_bytes())
    (DIST / "icons.svg").write_text((HERE / "src/assets/icons.svg").read_text())
    (DIST / "me.webp").write_bytes((HERE / "src/assets/me.webp").read_bytes())
    (DIST / "app.js").write_text((HERE / "src/app.js").read_text())
    if not STATIC:
        (DIST / "chat.js").write_text((HERE / "src/chat.js").read_text())
    (DIST / "index.html").write_text(shell(
        f"{NAME} — {ROLE}",
        "AI engineer for clinical and financial data: production RAG, governed agents, "
        "evaluation and fine-tuning, each with the number it produced.", home()))
    for i, en in enumerate(ENTRIES):
        (DIST / en["slug"]).write_text(case(i))


def audit():
    blob = gt.blob(gt.load()).replace(",", "")
    bad_r, bad_n = set(), set()
    for p in sorted(DIST.glob("*.html")):
        h = p.read_text()
        h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S)
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
