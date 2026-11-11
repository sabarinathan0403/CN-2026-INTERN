import re
import numpy as np
import pandas as pd
import streamlit as st
from nltk.stem import PorterStemmer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

st.set_page_config(page_title="Spam Shield", page_icon="👑", layout="centered")

# ------------------------------------------------------------------ THEME
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Source+Sans+3:wght@400;600&display=swap');

:root {
    --night: #120d26;
    --velvet: #1d1540;
    --velvet-2: #271b57;
    --gold: #d4af5f;
    --gold-soft: #f0d99a;
    --ivory: #f5edd9;
    --muted: #b9afd1;
    --spam: #c0344f;
    --ham: #2f9d78;
}

.stApp {
    background:
        radial-gradient(1100px 500px at 50% -10%, #3a2a7a 0%, rgba(58,42,122,0) 60%),
        var(--night);
    color: var(--ivory);
    font-family: 'Source Sans 3', 'Segoe UI', sans-serif;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 860px; padding-top: 2.5rem; }

/* ---- hero ---- */
.hero { text-align: center; padding: 0.5rem 0 1.6rem 0; }
.hero .crown { font-size: 2.6rem; line-height: 1; }
.hero h1 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 700;
    font-size: 3.4rem;
    letter-spacing: 0.02em;
    margin: 0.3rem 0 0.2rem 0;
    color: var(--gold-soft);
    text-shadow: 0 2px 24px rgba(212,175,95,0.25);
}
.hero p { color: var(--muted); font-size: 1.05rem; margin: 0; }
.rule {
    height: 1px; margin: 1.1rem auto 0 auto; width: 55%;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}

/* ---- input ---- */
.stTextArea label p {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.35rem; font-weight: 600; color: var(--gold-soft);
}
.stTextArea textarea {
    background: var(--velvet) !important;
    color: var(--ivory) !important;
    border: 1px solid rgba(212,175,95,0.45) !important;
    border-radius: 10px !important;
    font-size: 1.02rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(212,175,95,0.3) !important;
}

/* ---- button ---- */
.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #e3c378 0%, #b98d33 100%);
    color: #2a1d05;
    font-weight: 600;
    font-size: 1.05rem;
    border: 1px solid #f0d99a;
    border-radius: 10px;
    padding: 0.6rem 2rem;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #f0d28a 0%, #c99c3e 100%);
    color: #1d1403;
    border-color: #fff1c4;
}

/* ---- verdict banner ---- */
.verdict {
    margin: 1.6rem 0 1rem 0;
    padding: 1.3rem 1.5rem;
    border-radius: 14px;
    text-align: center;
    background: var(--velvet);
    border: 2px solid var(--gold);
    box-shadow: 0 0 0 5px rgba(212,175,95,0.10), 0 14px 40px rgba(0,0,0,0.45);
}
.verdict .title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 2.3rem; font-weight: 700; margin: 0;
}
.verdict .sub { color: var(--muted); margin-top: 0.25rem; }
.verdict.spam .title { color: #ff8da1; }
.verdict.ham  .title { color: #7fe0bb; }

/* ---- model cards ---- */
.mcard {
    background: var(--velvet);
    border: 1px solid rgba(212,175,95,0.35);
    border-top: 4px solid var(--ham);
    border-radius: 12px;
    padding: 1rem 1rem 1.1rem 1rem;
    height: 100%;
}
.mcard.spam { border-top-color: var(--spam); }
.mcard .name {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.3rem; font-weight: 600; color: var(--gold-soft);
}
.mcard .res { font-size: 1.5rem; font-weight: 600; margin: 0.35rem 0 0.1rem 0; }
.mcard.spam .res { color: #ff8da1; }
.mcard.ham  .res { color: #7fe0bb; }
.mcard .conf { color: var(--muted); font-size: 0.92rem; }
.track {
    height: 8px; border-radius: 6px; margin-top: 0.7rem;
    background: rgba(255,255,255,0.10); overflow: hidden;
}
.fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, var(--ham), var(--spam)); }

/* ---- expanders / table ---- */
div[data-testid="stExpander"] {
    background: var(--velvet);
    border: 1px solid rgba(212,175,95,0.30);
    border-radius: 12px;
}
div[data-testid="stExpander"] summary p { color: var(--gold-soft); font-weight: 600; }

.footer { text-align: center; color: var(--muted); font-size: 0.9rem; margin-top: 2rem; }

@media (max-width: 640px) {
    .hero h1 { font-size: 2.4rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------ ML
stemmer = PorterStemmer()


def clean(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\.\S+", " url ", text)
    text = re.sub(r"\d+", " num ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    words = [stemmer.stem(w) for w in text.split()
             if w not in ENGLISH_STOP_WORDS and len(w) > 1]
    return " ".join(words)


@st.cache_resource(show_spinner="Training the models... (first run only)")
def train():
    df = pd.read_csv("spam.csv", encoding="latin-1")[["v1", "v2"]].dropna().drop_duplicates()
    df.columns = ["label", "text"]
    df["y"] = (df["label"].str.lower().str.strip() == "spam").astype(int)
    df["clean"] = df["text"].apply(clean)

    X_tr, X_te, y_tr, y_te = train_test_split(
        df["clean"], df["y"], test_size=0.2, random_state=42, stratify=df["y"])
    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
    Xtr, Xte = vec.fit_transform(X_tr), vec.transform(X_te)

    models = {
        "Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "SVM": CalibratedClassifierCV(LinearSVC(class_weight="balanced"), cv=5),
    }
    rows = []
    for name, m in models.items():
        m.fit(Xtr, y_tr)
        p = m.predict(Xte)
        rows.append({"Model": name,
                     "Accuracy": accuracy_score(y_te, p),
                     "Precision": precision_score(y_te, p),
                     "Recall": recall_score(y_te, p),
                     "F1": f1_score(y_te, p)})
    metrics = pd.DataFrame(rows).set_index("Model").round(4)

    lr = models["Logistic Regression"]
    feats = np.array(vec.get_feature_names_out())
    top = np.argsort(lr.coef_[0])[-15:]
    keywords = pd.Series(lr.coef_[0][top], index=feats[top])
    return vec, models, metrics, keywords, len(df)


vec, models, metrics, keywords, n_rows = train()


def model_card(name, spam_p):
    is_spam = spam_p >= 0.5
    cls = "spam" if is_spam else "ham"
    result = "Spam" if is_spam else "Not spam"
    conf = spam_p if is_spam else 1 - spam_p
    return (
        f'<div class="mcard {cls}">'
        f'<div class="name">{name}</div>'
        f'<div class="res">{result}</div>'
        f'<div class="conf">{conf:.1%} confident</div>'
        f'<div class="track"><div class="fill" style="width:{spam_p * 100:.1f}%"></div></div>'
        f'<div class="conf" style="margin-top:0.35rem">Spam probability: {spam_p:.1%}</div>'
        f'</div>'
    )


# ------------------------------------------------------------------ UI
st.markdown(
    f"""
    <div class="hero">
        <div class="crown">👑</div>
        <h1>Spam Shield</h1>
        <p>Three machine learning models inspect every message before it reaches the court.</p>
        <div class="rule"></div>
        <p style="margin-top:0.8rem; font-size:0.92rem;">Trained on {n_rows:,} real messages</p>
    </div>
    """,
    unsafe_allow_html=True,
)

msg = st.text_area("Paste an email or SMS to inspect", height=160,
                   placeholder="Type or paste the message here...")

if st.button("Check message", type="primary"):
    if not msg.strip():
        st.warning("Please enter a message first.")
    else:
        X = vec.transform([clean(msg)])
        probs = {name: float(m.predict_proba(X)[0][1]) for name, m in models.items()}
        spam_votes = sum(p >= 0.5 for p in probs.values())
        total = len(probs)
        final_spam = spam_votes > total / 2
        avg_p = sum(probs.values()) / total

        if final_spam:
            title, cls = "This message is spam", "spam"
        else:
            title, cls = "This message looks safe", "ham"

        st.markdown(
            f"""
            <div class="verdict {cls}">
                <p class="title">{title}</p>
                <div class="sub">{spam_votes} of {total} models flagged it as spam
                &nbsp;|&nbsp; Average spam probability {avg_p:.1%}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cols = st.columns(total)
        for col, (name, p) in zip(cols, probs.items()):
            col.markdown(model_card(name, p), unsafe_allow_html=True)

st.write("")
with st.expander("Model comparison"):
    st.dataframe(metrics, use_container_width=True)
with st.expander("Top spam-indicating keywords"):
    st.bar_chart(keywords)

st.markdown('<div class="footer">Naive Bayes, Logistic Regression and SVM with TF-IDF features</div>',
            unsafe_allow_html=True)