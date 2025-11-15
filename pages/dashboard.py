import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from datetime import datetime

# -------------------------
# LOGIN PROTECTION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.warning("You must sign in to view the dashboard.")
    st.info("Click below to open the login page.")
    st.markdown(
        "<a href='/?page=Login' style='color:#00c2b8;text-decoration:none;font-weight:600'>➡️ Open Login Page</a>",
        unsafe_allow_html=True,
    )
    st.stop()


username = st.session_state.get("username", "User")

# ===========================================================
# PREMIUM HEADER (NO INDENTATION — FIXED)
# ===========================================================
header_html = f"""
<div style='background:linear-gradient(90deg,#00c2b8,#007bff);
            padding:22px;border-radius:12px;color:white;margin-bottom:18px'>
  <div style='display:flex;justify-content:space-between;align-items:center'>
    <div>
      <h2 style='margin:0'>🧠 AI Customer Feedback Analyzer — Dashboard</h2>
      <div style='opacity:0.85;font-size:13px'>
        Hybrid BERT + RoBERTa • LIME Explainability • SaaS Premium UI
      </div>
    </div>
    <div style='text-align:right;font-size:13px;opacity:0.9'>
      Logged in as: <strong>{username}</strong>
    </div>
  </div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

# ===========================================================
# SIDEBAR
# ===========================================================
with st.sidebar:
    st.markdown("## ⚙️ Navigation")
    st.write(f"Welcome, **{username}** 👋")
    st.markdown("---")
    st.write("👨‍💻 **Built by:** Lalit Chaudhari")
    st.markdown("[LinkedIn](https://www.linkedin.com/in/lalit-chaudhari-9a62b8190/)")
    st.markdown("[GitHub](https://github.com/LalitChaudhari851)")
    st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out successfully.")
        st.markdown("<a href='/?page=login'>Open Login Page</a>", unsafe_allow_html=True)

# ===========================================================
# LOAD MODELS FROM app.py
# ===========================================================
BERT_MODEL = None
ROBERTA_MODEL = None
HAS_LIME = False
HAS_WORDCLOUD = False

try:
    from app import get_shared_resources
    resources = get_shared_resources()
    BERT_MODEL = resources["bert"]
    ROBERTA_MODEL = resources["roberta"]
    HAS_WORDCLOUD = resources["has_wordcloud"]
    HAS_LIME = resources["has_lime"]
except:
    BERT_MODEL = ROBERTA_MODEL = None
    HAS_WORDCLOUD = HAS_LIME = False

# ===========================================================
# HELPERS
# ===========================================================
def simple_rule_predict(text: str):
    t = text.lower()
    pos = sum(t.count(w) for w in ["good", "great", "excellent", "love", "amazing", "satisfied"])
    neg = sum(t.count(w) for w in ["bad", "poor", "terrible", "hate", "late", "delay", "worst", "disappointed"])
    if pos - neg >= 2: return "Positive 😊", 0.90
    if neg - pos >= 2: return "Negative 😡", 0.90
    return "Neutral 😐", 0.75


def safe_predict(text: str):
    if BERT_MODEL and ROBERTA_MODEL:
        try:
            b = BERT_MODEL(text)[0]
            r = ROBERTA_MODEL(text)[0]

            stars = int(b["label"].split()[0])
            tone = r["label"].lower()
            conf = r["score"]

            if tone == "neutral": return "Neutral 😐", b, r, conf
            if stars <= 2: return "Negative 😡", b, r, conf
            if stars >= 4: return "Positive 😊", b, r, conf
            return "Neutral 😐", b, r, conf
        except:
            pass

    lbl, conf = simple_rule_predict(text)
    return lbl, None, None, conf


def highlight_text_html(text: str):
    mapping = {
        "good": "#4ade80", "excellent": "#4ade80", "great": "#4ade80",
        "love": "#4ade80", "amazing": "#4ade80",
        "bad": "#f87171", "poor": "#f87171", "terrible": "#f87171",
        "late": "#facc15", "delay": "#facc15"
    }
    out = text
    for w, col in mapping.items():
        out = re.sub(rf"(?i)\b{w}\b", f"<mark style='background:{col};padding:3px;border-radius:4px'>{w}</mark>", out)
    return out

# ===========================================================
# TABS
# ===========================================================
tab1, tab2, tab3 = st.tabs(["🔎 Single Review", "📊 Bulk Upload", "📈 Insights"])

# ------------------------------------------------------
# TAB 1 — SINGLE REVIEW
# ------------------------------------------------------
with tab1:
    st.subheader("Analyze a Single Review")
    txt = st.text_area("Enter review text:", height=150)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Analyze"):
            if txt.strip():
                sentiment, b, r, conf = safe_predict(txt)
                st.success(f"{sentiment} — {conf*100:.1f}%")

                if b: st.write(f"BERT → {b['label']} | {b['score']}")
                if r: st.write(f"RoBERTa → {r['label']} | {r['score']}")

                st.markdown("### 🔍 Keyword Highlight")
                st.markdown(highlight_text_html(txt), unsafe_allow_html=True)
            else:
                st.warning("Enter a review first.")

    with col2:
        if st.button("Explain (LIME)"):
            if not HAS_LIME or ROBERTA_MODEL is None:
                st.warning("LIME is not available.")
            else:
                from lime.lime_text import LimeTextExplainer
                explainer = LimeTextExplainer(class_names=["negative","neutral","positive"])

                def predict_proba(texts):
                    res = ROBERTA_MODEL(texts, return_all_scores=True)
                    prob_list = []
                    for item in res:
                        d = {e["label"].lower(): e["score"] for e in item}
                        prob_list.append([
                            d.get("negative", 0.0),
                            d.get("neutral", 0.0),
                            d.get("positive", 0.0)
                        ])
                    return np.array(prob_list)

                exp = explainer.explain_instance(txt, predict_proba, num_features=6)
                st.write("### LIME Important Tokens")
                for w, score in exp.as_list():
                    st.write(f"{'🔺' if score>0 else '🔻'} `{w}` → {score:.3f}")

                st.components.v1.html(exp.as_html(), height=350, scrolling=True)

    with col3:
        if st.button("Clear"):
            st.rerun()

# ------------------------------------------------------
# TAB 2 — BULK CSV
# ------------------------------------------------------
with tab2:
    st.subheader("Bulk Upload CSV (column: review_text)")
    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)

        if "review_text" not in df.columns:
            st.error("CSV must contain a column named `review_text`.")
        else:
            df["review_text"] = df["review_text"].astype(str)

            results = []
            for review in df["review_text"]:
                s, b, r, c = safe_predict(review)
                results.append({"Sentiment": s, "Confidence": c})

            df_out = pd.concat([df, pd.DataFrame(results)], axis=1)

            st.dataframe(df_out.head(), use_container_width=True)

            st.download_button(
                "Download Results",
                df_out.to_csv(index=False),
                file_name="sentiment_results.csv"
            )

# ------------------------------------------------------
# TAB 3 — INSIGHTS
# ------------------------------------------------------
with tab3:
    st.subheader("Insights")
    st.info("Upload data in Bulk Upload to generate insights.")

st.markdown("---")
st.caption("🚀 Hybrid AI • Built by Lalit Chaudhari")
