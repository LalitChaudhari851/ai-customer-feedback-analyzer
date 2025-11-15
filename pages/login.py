import streamlit as st

# DO NOT USE set_page_config here (only in app.py)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------- PREMIUM LOGIN UI ----------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0b1529, #000);
}
.login-box {
    background: rgba(255,255,255,0.05);
    padding: 35px;
    width: 420px;
    margin: 70px auto;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
}
.login-title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    color: white;
}
.stButton > button {
    width: 100%;
    background: linear-gradient(90deg,#00c2b8,#007bff) !important;
    color: white !important;
    padding: 10px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='login-box'>", unsafe_allow_html=True)
st.markdown("<div class='login-title'>🔐 Login to Continue</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#aaa;'>Use <b>demo/demo</b> or any username</p>", unsafe_allow_html=True)

# ---------- LOGIN FORM ----------
with st.form("login_form"):
    user = st.text_input("Username", placeholder="Enter username...")
    pwd = st.text_input("Password", type="password", placeholder="Enter password...")
    submit = st.form_submit_button("Login")

# ---------- LOGIN HANDLER ----------
if submit:
    if (user == "demo" and pwd == "demo") or user.strip() != "":
        st.session_state.logged_in = True
        st.session_state.username = user

        st.success("Login successful! Redirecting...")

        # 🚀 CORRECT REDIRECT
        st.switch_page("pages/dashboard.py")

    else:
        st.error("Invalid username or password ❌")

st.markdown("</div>", unsafe_allow_html=True)
