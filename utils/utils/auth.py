# ==========================================
# utils/auth.py
# ==========================================
import streamlit as st


def get_admin_credentials():
    """Ambil credentials admin dari secrets.toml"""
    try:
        username = st.secrets["admin"]["username"]
        password = st.secrets["admin"]["password"]
        return username, password
    except Exception:
        # Fallback default kalau secrets belum di-set
        return "admin", "admin123"


def is_logged_in():
    """Cek apakah user sudah login"""
    return st.session_state.get("logged_in", False)


def get_current_user():
    """Ambil username user yang sedang login"""
    return st.session_state.get("username", "Tamu")


def login_form():
    """Tampilkan form login"""
    logo_b64 = st.session_state.get("logo_b64")
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" '
        f'width="90" height="auto" style="display:inline-block;">'
        if logo_b64
        else '<div style="font-size:4rem; line-height:1;">🏛️</div>'
    )

    # Tampilkan card login di tengah
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown(
            f"""
            <div class="login-wrapper">
                <div class="login-card">
                    <div class="login-logo">{logo_html}</div>
                    <p class="login-title">UPTD PASAR KANDANGAN</p>
                    <p class="login-subtitle">Silakan login untuk melanjutkan</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("form_login", clear_on_submit=False):
            username_input = st.text_input(
                "USERNAME",
                placeholder="Masukkan username",
                key="login_user"
            )
            password_input = st.text_input(
                "PASSWORD",
                type="password",
                placeholder="Masukkan password",
                key="login_pass"
            )

            submit = st.form_submit_button(
                "LOGIN",
                type="primary",
                use_container_width=True
            )

            if submit:
                admin_user, admin_pass = get_admin_credentials()
                if username_input.strip() == admin_user and password_input.strip() == admin_pass:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username_input.strip().upper()
                    st.success("Login berhasil! Mengalihkan...")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")


def logout():
    """Logout user"""
    for key in ["logged_in", "username"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def wajib_login():
    """Proteksi halaman — kalau belum login redirect ke Home"""
    if not is_logged_in():
        st.warning("Silakan login terlebih dahulu di halaman Beranda.")
        st.page_link("Home.py", label="Kembali ke Beranda", use_container_width=True)
        st.stop()
