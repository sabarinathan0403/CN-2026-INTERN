"""PhishShift dashboard (Streamlit).  Run locally:  streamlit run app.py

Safety (NFR-01/02): inputs are treated as inert text. Nothing is fetched, opened or
executed, and no real credentials or personal data should be pasted in.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from core import ABSTAIN_HIGH, ABSTAIN_LOW, DISCLAIMER, perturb_variants, scan_message  # noqa: E402

MODEL_PATH = ROOT / "models" / "phishshift_logreg_v1.joblib"
RF_PATH = ROOT / "models" / "phishshift_rf_v1.joblib"
REPORTS = ROOT / "reports"

st.set_page_config(page_title="PhishShift Message Risk Scanner", page_icon="🛡️", layout="wide")


@st.cache_resource(show_spinner="Training models (first run only)...")
def load_models():
    if not MODEL_PATH.exists():
        subprocess.run([sys.executable, str(ROOT / "src" / "train.py")], check=True, cwd=ROOT)
    return joblib.load(MODEL_PATH), joblib.load(RF_PATH)


@st.cache_data
def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(REPORTS / name)


@st.cache_data
def read_json(path: str) -> dict:
    return json.loads(Path(path).read_text())


lr, rf = load_models()

# ------------------------------------------------------------------ style
st.markdown(
    """
<style>
.block-container {padding-top: 1.6rem; max-width: 1200px;}
.hero {background: linear-gradient(120deg,#0b1220 0%,#14325c 60%,#0e7490 100%);
       border-radius: 16px; padding: 26px 30px; margin-bottom: 18px; color: #fff;}
.hero h1 {margin: 0; font-size: 2rem; color: #fff;}
.hero p {margin: 6px 0 0 0; color: #cbd5e1; font-size: .95rem;}
.pill {display:inline-block; padding:3px 12px; margin:10px 6px 0 0; border-radius:999px;
       background: rgba(255,255,255,.14); font-size:.78rem; color:#e2e8f0;}
.verdict {border-radius: 14px; padding: 18px 22px; margin-bottom: 12px; border: 1px solid;}
.verdict h2 {margin: 0; font-size: 1.5rem;}
.verdict small {opacity:.85;}
.v-phishing {background:#fef2f2; border-color:#fca5a5; color:#7f1d1d;}
.v-legitimate {background:#f0fdf4; border-color:#86efac; color:#14532d;}
.v-abstain {background:#fffbeb; border-color:#fcd34d; color:#78350f;}
.cue {background:#f1f5f9; border-left:4px solid #0e7490; border-radius:6px;
      padding:8px 12px; margin:6px 0; color:#0f172a; font-size:.92rem;}
.foot {color:#64748b; font-size:.8rem; margin-top:18px;}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ header
st.markdown(
    """
<div class="hero">
  <h1>🛡️ PhishShift</h1>
  <p>Message risk scanner · spots suspicious emails and SMS, explains why, and says "not sure" when it should.</p>
  <span class="pill">Simulated messages only</span><span class="pill">Defanged links</span>
  <span class="pill">Never opens URLs</span><span class="pill">Decision support</span>
</div>
""",
    unsafe_allow_html=True,
)

tab_scan, tab_data, tab_models, tab_holdout, tab_robust, tab_accept, tab_safety = st.tabs(
    ["🔍 Scanner", "🗂️ Data & dedup", "📊 Model comparison", "🧪 Campaign holdout",
     "🌪️ Robustness", "✅ Acceptance tests", "🔒 Safety & limits"]
)

# ------------------------------------------------------------------ scanner
SENDERS = {
    "Corporate / internal": "corporate", "Bank / service short code": "shortcode",
    "Free webmail": "free_webmail", "Look-alike domain": "lookalike",
    "Unknown number": "unknown_number", "Link shortener": "shortener", "Unknown": "unknown",
}
VERDICT = {
    "phishing": ("🚨", "Likely phishing", "v-phishing"),
    "legitimate": ("✅", "Likely legitimate", "v-legitimate"),
    "abstain": ("🤔", "Not sure: send to human review", "v-abstain"),
}

with tab_scan:
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown("##### Paste a message")
        with st.form("scan_form", border=True):
            subject = st.text_input("Subject / title", placeholder="e.g. Action required: verify your account")
            body = st.text_area("Message body", height=170,
                                placeholder="Paste the message text. Write links defanged: hxxp://site[.]test")
            c1, c2 = st.columns(2)
            channel = c1.radio("Channel", ["email", "sms"], horizontal=True)
            sender_label = c2.selectbox("Sender type", list(SENDERS))
            url_feats = st.text_input("Link features (optional)", value="no_url",
                                      help="Inert descriptors only, e.g. 'defanged shortener'. Never paste a live link.")
            model_name = st.radio("Model", ["TF-IDF Logistic Regression", "Random Forest"], horizontal=True)
            go = st.form_submit_button("Scan message", type="primary", use_container_width=True)
    with right:
        st.markdown("##### Result")
        if not go:
            st.info("Fill in the message and press **Scan message**.")
        elif "http://" in body.lower() or "https://" in body.lower():
            st.error("Live URL detected. Please defang it (hxxp://… and [.]). Nothing was scanned or fetched.")
        elif not (subject.strip() or body.strip()):
            st.info("Enter a subject or body to scan.")
        else:
            pipe = lr if model_name.startswith("TF-IDF") else rf
            v = scan_message(pipe, subject, body, channel, SENDERS[sender_label], url_feats)
            icon, label, css = VERDICT[v.decision]
            st.markdown(
                f'<div class="verdict {css}"><h2>{icon} {label}</h2>'
                f"<small>Phishing probability {v.p_phish:.0%}</small></div>",
                unsafe_allow_html=True,
            )
            st.progress(min(max(v.p_phish, 0.0), 1.0))
            st.caption(f"Abstain band {ABSTAIN_LOW:.2f}–{ABSTAIN_HIGH:.2f}: inside it the tool refuses to decide.")
            st.markdown("**Why**")
            if v.cues:
                for _, d in v.cues:
                    st.markdown(f'<div class="cue">{d}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="cue">No standard risk cues detected.</div>', unsafe_allow_html=True)
            if v.top_terms:
                st.markdown("**Words pushing toward phishing:** " + ", ".join(f"`{t}`" for t in v.top_terms))
    st.markdown(f'<div class="foot">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ data
with tab_data:
    summ = read_json(str(REPORTS / "summary.json"))
    d, sn = summ["dedup"], summ["sanitization"]
    a, b, c, e = st.columns(4)
    a.metric("Raw messages", d["raw_rows"])
    b.metric("After dedup", d["after_dedup"])
    c.metric("Near-duplicates removed", d["removed"])
    e.metric("Train/test template overlap", d["train_test_template_overlap_campaign_split"])
    st.caption(f"Dedup method: {d['method']} (threshold {d['threshold']}).")
    st.subheader("Sanitization audit (CP-1)")
    st.json(sn)
    ded = pd.read_csv(ROOT / "data" / "deduped_messages.csv")
    st.subheader("Corpus preview")
    st.dataframe(ded.head(50), use_container_width=True)
    cc = st.columns(3)
    for col, f in zip(cc, ["eda_campaigns.png", "eda_channel.png", "eda_length.png"]):
        col.image(str(REPORTS / f))

# ------------------------------------------------------------------ models
with tab_models:
    res = read_csv("results_table.csv")
    st.subheader("Rules vs TF-IDF linear vs Random Forest")
    st.dataframe(res.round(3), use_container_width=True)
    piv = res.pivot(index="model", columns="split", values="f1")
    st.bar_chart(piv)
    gap = res.pivot(index="model", columns="split", values="f1")
    gap["gap (random − campaign)"] = gap["random_split"] - gap["campaign_holdout"]
    st.markdown("**Generalisation gap** — a random split looks near-perfect because templates leak between train and test. The campaign-separated holdout is the honest number.")
    st.dataframe(gap.round(3))
    st.subheader("Reject / abstain option")
    st.dataframe(read_csv("abstain_results.csv").round(3), use_container_width=True)

# ------------------------------------------------------------------ holdout
with tab_holdout:
    st.subheader("Per-campaign results on campaigns excluded from training")
    pc = read_csv("per_campaign_holdout.csv")
    sel = st.selectbox("Model", pc["model"].unique(), index=1)
    st.dataframe(pc[pc.model == sel].round(3), use_container_width=True)
    st.bar_chart(pc[pc.model == sel].set_index("campaign")["accuracy"])
    st.subheader("Error examples (TF-IDF logistic regression)")
    st.dataframe(read_csv("error_examples.csv").head(10), use_container_width=True)

# ------------------------------------------------------------------ robustness
with tab_robust:
    st.subheader("Probability drift under harmless text perturbations (AT-03)")
    rob = read_csv("robustness_drift.csv")
    st.dataframe(rob.round(3), use_container_width=True)
    st.markdown("**Try it live**")
    txt = st.text_input("Message body to perturb", "Your parcel could not be delivered. Choose a new slot: hxxp://pkg-slot[.]example-sim[.]test/r")
    rows = []
    for k, vtxt in perturb_variants(txt).items():
        v = scan_message(lr, "Parcel", vtxt, "sms", "shortener", "defanged http")
        rows.append(dict(perturbation=k, p_phish=round(v.p_phish, 3), decision=v.decision))
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.subheader("CP-5: 8 new harmless simulated messages")
    st.dataframe(read_csv("cp5_perturbation_results.csv"), use_container_width=True, height=300)

# ------------------------------------------------------------------ acceptance
with tab_accept:
    st.subheader("AT-01 · Legitimate urgent / password / payroll messages")
    fp = read_csv("legit_urgent_fpr.csv")
    st.dataframe(fp.round(3), use_container_width=True)
    st.caption("False-positive impact: legitimate messages flagged as phishing or sent to human review.")
    st.subheader("AT-02 · Phishing with unfamiliar phrasing (campaigns excluded from training)")
    pc = read_csv("per_campaign_holdout.csv")
    st.dataframe(pc[pc.label == 1].round(3), use_container_width=True)
    st.subheader("AT-03 · Defanged URL / punctuation pattern changes")
    st.dataframe(read_csv("robustness_drift.csv").round(3), use_container_width=True)

# ------------------------------------------------------------------ safety
with tab_safety:
    st.markdown(
        """
**What this tool is:** an educational triage / decision-support tool for *controlled, simulated* messages.

**What it never does (NFR-01, NFR-02):** click, fetch or execute URLs; store attachments; collect real credentials or personal data.

**Known limitations**
- Trained on a small, locally authored synthetic corpus; real-world phishing is far more varied.
- Unseen tactics (e.g. polite, link-light or vague requests) are the weakest area. See the campaign-holdout tab.
- Probabilities can shift under small formatting changes. See the robustness tab.
- Outputs are *not* a guarantee of safety. Always follow your organisation's reporting process.
        """
    )
    if (ROOT / "models" / "model_card.json").exists():
        st.json(read_json(str(ROOT / "models" / "model_card.json")))