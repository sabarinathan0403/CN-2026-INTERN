# PhishShift Message Risk Scanner (ML-07)

Educational triage tool: classifies **simulated** emails/SMS as phishing / legitimate / *abstain*,
explains risk cues safely, and measures generalisation to **unseen campaigns**.
It never opens, fetches or executes links (URLs are defanged, inert text).

## Quick start (VS Code terminal)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/train.py          # builds data, trains 3 models, writes reports/ + models/
streamlit run app.py         # dashboard at http://localhost:8501
python -m unittest discover -s tests -v
python src/cli.py --subject "Quick favour" --body "Are you free? details hxxp://sho[.]rt/aB3x" --channel sms --sender shortener --url-features "defanged shortener"
```

## What is where
| Path | Purpose |
|---|---|
| `src/generate_data.py` | synthetic, defanged, locally authored corpus (provenance column) |
| `src/core.py` | dedup, rules model, TF-IDF LR, Random Forest, abstain, explanations, perturbations |
| `src/train.py` | full pipeline + all evidence in `reports/` |
| `app.py` | Streamlit dashboard (Scanner, Data, Models, Holdout, Robustness, Acceptance, Safety) |
| `docs/traceability.md` | FR/NFR -> code -> evidence, plus short threat model |

## Method summary
1. **FR-01** Near-duplicate removal (cosine >= 0.85 on normalised templates) before any split.
2. **FR-02** Rules baseline vs TF-IDF + Logistic Regression vs Random Forest.
3. **FR-03** Campaign-separated holdout (5 template families never seen in training) compared with a random split.
4. **FR-04** Abstain band 0.35-0.65 and cue-based explanations.
5. **FR-05** False-positive rate on a separate legitimate urgent/password/payroll set; perturbation drift.

## Deploy on Render
1. Push this folder to a GitHub repo (commands below).
2. Render dashboard -> **New + -> Blueprint** -> pick the repo (it reads `render.yaml`).
   Or **New Web Service** with: Build `pip install -r requirements.txt && python src/train.py`,
   Start `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`.
3. Wait for the build; open the `onrender.com` URL. (Free plan sleeps when idle; first load is slow.)

## Push to GitHub
```bash
git init && git add . && git commit -m "PhishShift ML-07"
git branch -M main
git remote add origin https://github.com/<your-username>/phishshift.git
git push -u origin main
```

## Limitations / disclosure
Synthetic corpus only; decision support, not a guarantee of safety. AI tools assisted drafting;
you must be able to explain and reproduce every part (see SRS section 14) - add your own AI-usage note here.
