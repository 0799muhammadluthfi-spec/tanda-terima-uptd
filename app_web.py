# ==========================================
# app_web.py
# ==========================================
import streamlit as st
import os
import base64
import urllib.request

from utils.css_styles import inject_css, inject_welcome_css

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="logo_hss.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# FUNGSI LOGO
# ==========================================
def get_logo_base64():
    for nama_file in ["logo_hss.png", "logo.png", "Logo_HSS.png"]:
        if os.path.exists(nama_file):
            with open(nama_file, "rb") as f:
                return base64.b64encode(f.read()).decode()

    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/3/3e/Lambang_Kabupaten_Hulu_Sungai_Selatan.png",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                img_data = response.read()
                if len(img_data) > 100:
                    return base64.b64encode(img_data).decode()
        except Exception:
            continue
    return None

if "logo_b64" not in st.session_state:
    st.session_state["logo_b64"] = get_logo_base64()

# ==========================================
# INJECT CSS
# ==========================================
inject_css()
inject_welcome_css()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    logo_b64 = st.session_state.get("logo_b64")

    if logo_b64:
        st.markdown(
            f"""
            <div style="text-align:center; padding:18px 0 6px 0;">
                <img src="data:image/png;base64,{logo_b64}"
                     width="78" height="auto"
                     style="display:inline-block;
                            filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4));">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="text-align:center; padding:18px 0 6px 0;">
                <div style="font-size:3rem; line-height:1;">🏛️</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div style="text-align:center; padding:4px 0 14px 0;
                    border-bottom:1px solid rgba(255,255,255,0.08);
                    margin-bottom:14px;">
            <p style="font-family:'Inter',sans-serif;
                      font-size:1.05rem; font-weight:800;
                      color:#f1f5f9 !important;
                      letter-spacing:-0.02em;
                      margin:0 0 4px 0; line-height:1.3;">
                UPTD PASAR KANDANGAN
            </p>
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.78rem; font-weight:600;
                      color:#94a3b8 !important;
                      letter-spacing:0.04em;
                      margin:0; line-height:1.4;">
                KABUPATEN HULU SUNGAI SELATAN
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="padding: 8px 4px;">
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.7rem; font-weight:600;
                      color:#64748b !important;
                      text-transform:uppercase;
                      letter-spacing:0.06em;
                      margin:0 0 8px 0;">
                MENU UTAMA
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.page_link("app_web.py", label="🏠  Beranda", use_container_width=True)

    st.markdown(
        """
        <div style="padding: 8px 4px 4px 4px;">
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.7rem; font-weight:600;
                      color:#64748b !important;
                      text-transform:uppercase;
                      letter-spacing:0.06em;
                      margin:0 0 6px 0;">
                MODUL
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.page_link(
        "pages/1_📋_SK_Toko.py",
        label="📋  SK Toko",
        use_container_width=True
    )
    st.page_link(
        "pages/2_🅿️_Parkir.py",
        label="🅿️  Parkir",
        use_container_width=True
    )
    st.page_link(
        "pages/3_💰_Kas.py",
        label="💰  Kas UPTD",
        use_container_width=True
    )

    st.markdown(
        """
        <div style="text-align:center; padding:24px 0 8px 0;
                    border-top:1px solid rgba(255,255,255,0.06);
                    margin-top:40px;">
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.56rem; font-weight:400;
                      color:#64748b !important;
                      margin:0; line-height:1.7;
                      letter-spacing:0.02em;">
                Developed by
            </p>
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.68rem; font-weight:700;
                      color:#94a3b8 !important;
                      margin:2px 0 0 0;
                      letter-spacing:0.01em;">
                M. Luthfi Renaldi
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# HALAMAN WELCOME
# ==========================================
logo_b64 = st.session_state.get("logo_b64")
logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" '
    f'width="140" height="auto" style="display:inline-block;">'
    if logo_b64
    else '<div style="font-size:6rem; line-height:1;">🏛️</div>'
)

st.markdown(
    f"""
    <div class="welcome-wrapper">
        <div class="welcome-logo">{logo_html}</div>
        <p class="welcome-title">
            UPTD PENGELOLAAN<br>PASAR KANDANGAN
        </p>
        <p class="welcome-subtitle">
            Kabupaten Hulu Sungai Selatan
        </p>
        <div class="welcome-line"></div>
        <p class="welcome-hint">
            Silakan pilih modul pada menu di sebelah kiri untuk memulai
        </p>
        <div class="welcome-credit">
            <p class="welcome-credit-label">Developed by</p>
            <p class="welcome-credit-name">M. Luthfi Renaldi</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
