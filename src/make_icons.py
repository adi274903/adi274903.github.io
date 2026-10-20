#!/usr/bin/env python3
"""One-off: fetch brand icons from Simple Icons (CC0) and write src/assets/icons.svg, a single <symbol> sprite.
Icons are monochrome (currentColor), so they follow the light/dark theme. Brand names are trademarks of their owners."""
import re, urllib.request, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SLUGS = {"qwen": "Qwen", "googlecloud": "Google Cloud", "googlegemini": "Gemini", "huggingface": "Hugging Face",
         "pytorch": "PyTorch", "postgresql": "PostgreSQL", "neo4j": "Neo4j", "qdrant": "Qdrant",
         "databricks": "Databricks", "apachespark": "PySpark", "oracle": "Oracle", "python": "Python",
         "spacy": "spaCy", "fastapi": "FastAPI", "streamlit": "Streamlit", "anthropic": "Claude",
         "mistralai": "Mistral", "deepseek": "DeepSeek", "amazonwebservices": "AWS Bedrock", "vllm": "vLLM",
         "tata": "Tata", "tensorflow": "TensorFlow", "scikitlearn": "scikit-learn"}
out = ['<svg xmlns="http://www.w3.org/2000/svg" style="display:none">']
for slug, name in SLUGS.items():
    svg = urllib.request.urlopen(f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg", timeout=20).read().decode()
    d = re.search(r'<path d="([^"]+)"', svg).group(1)
    out.append(f'<symbol id="i-{slug}" viewBox="0 0 24 24"><title>{name}</title><path d="{d}"/></symbol>')
out.append("</svg>")
(HERE / "assets" / "icons.svg").write_text("\n".join(out))
print(len(SLUGS), "icons,", (HERE / "assets" / "icons.svg").stat().st_size, "bytes")
