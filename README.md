# Aditya Sannabhadti: portfolio

Live site: https://adi274903.github.io

Static, dependency-free portfolio (no third-party requests): role-track views for AI engineer, fintech and
healthtech, a chart or table for every project result, a skills grid counted from the resume bullets, a case study
per project, and an **Ask page** (`ask.html`) that answers questions about the record with no AI model.

    docs/        the published site (GitHub Pages serves this folder)
    src/         styles.css, app.js, engine.js (Q&A engine), ask.js (Ask page UI), charts.py, test_all.js
    build.py     renders the site from the portfolio content model; `--static` writes docs/

## Ask page: deterministic, model-free
The record is chunked into fifteen sections of short quoted lines (`ask-data.json`). In the browser, `engine.js`
builds TF-IDF vectors for every line and section, turns a question into a vector, picks the section (name matches
plus cosine similarity), then the best lines inside it, and writes the reply from fixed templates. Off-topic and
coding questions are refused. Same question, same answer.

    node src/test_all.js        # 51-question regression suite (29 dev + 22 written afterwards)

The content model and its ground-truth source are kept private, so the site cannot be rebuilt from this repository
alone; `docs/` is the deliverable.
