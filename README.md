# Aditya Sannabhadti: portfolio

Live site: https://adi274903.github.io

Static, dependency-free portfolio (about 112 KB, no third-party requests): role-track views for AI engineer,
fintech and healthtech, a chart for every project result, a skills grid counted from the resume bullets,
and a case-study page per project.

    docs/        the published site (GitHub Pages serves this folder)
    src/         styles.css, app.js, chat.js, charts.py
    build.py     renders the site from the portfolio content model
    serve.py     local preview server with the optional SmolLM2 chat popup (needs the harness, not included here)

`python3 build.py --static` writes `docs/`. The content model and its ground-truth source are kept private, so
the site cannot be rebuilt from this repository alone; `docs/` is the deliverable.
