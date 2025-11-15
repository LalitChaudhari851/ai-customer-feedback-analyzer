# ----------------------------
# FILE: app.py (FINAL CLEAN VERSION)
# ----------------------------
import os
import streamlit as st

# Avoid TensorFlow warnings
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"   # Required for HuggingFace Spaces

# ----------------------------------------------------
# MAIN PAGE CONFIG (ONLY HERE) — required by Streamlit
# ----------------------------------------------------
st.set_page_config(
    page_title="AI Customer Feedback Analyzer — SaaS Pro",
    page_icon="🧠",
    layout="wide"
)

# ----------------------------------------------------
# GLOBAL SESSION STATE
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ----------------------------------------------------
# PREMIUM SAAS LANDING HEADER  ✔ FIXED HTML, NO RAW TEXT
# ----------------------------------------------------
st.markdown(
    """
<div style='background:linear-gradient(90deg,#00c2b8,#007bff);
            padding:22px;border-radius:12px;margin-bottom:15px; color:white;'>

  <h1 style='margin:0;'>🧠 AI Customer Feedback Analyzer</h1>
  <p style='opacity:0.9;'>Hybrid BERT + RoBERTa • Explainable AI (LIME) • Premium SaaS UI</p>

  <div style='text-align:right; margin-top:-40px;'>
      <strong>Built by Lalit Chaudhari</strong><br>
      <a href='https://github.com/LalitChaudhari851' style='color:white;text-decoration:none;'>GitHub</a> •
      <a href='https://www.linkedin.com/in/lalit-chaudhari-9a62b8190/'
         style='color:white;text-decoration:none;'>LinkedIn</a>
  </div>

</div>
""",
    unsafe_allow_html=True
)

# ----------------------------------------------------
# CTA — open login page
# ----------------------------------------------------
st.markdown("### 👇 Start using the app")

if st.button("🔐 Open Login Page"):
    st.switch_page("pages/login.py")

st.markdown("---")

# ----------------------------------------------------
# SHARE MODELS WITH PAGES (CACHE = FAST)
# ----------------------------------------------------
@st.cache_resource(show_spinner=True)
def get_shared_resources():
    """Load ML models only once, share across pages."""
    resources = {
        "bert": None,
        "roberta": None,
        "has_transformers": False,
        "has_wordcloud": False,
        "has_lime": False
    }

    try:
        from transformers import pipeline

        resources["bert"] = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )

        resources["roberta"] = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment"
        )

        resources["has_transformers"] = True

    except Exception as e:
        print("Transformer load issue:", e)

    try:
        import wordcloud
        resources["has_wordcloud"] = True
    except:
        pass

    try:
        import lime
        resources["has_lime"] = True
    except:
        pass

    return resources

# ----------------------------------------------------
# PRELOAD MODELS BUTTON
# ----------------------------------------------------
if st.button("⚡ Preload ML Models (Optional)"):

    _ = get_shared_resources()
    st.success("Models preloaded (if available)!")

# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------
st.markdown("---")
st.caption("🚀 AI Customer Feedback Analyzer • Hybrid BERT + RoBERTa • Premium SaaS UI")
