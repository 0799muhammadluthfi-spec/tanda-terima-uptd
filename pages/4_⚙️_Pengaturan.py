# ==========================================
# pages/4_⚙️_Pengaturan.py
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css
from utils.helpers import (
    WS_SK, WS_PARKIR, WS_KAS,
    load_data, tombol_refresh
)
from utils.auth import wajib_login, get_current_user, logout

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Pengaturan | UPTD Pasar Kandangan",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_css()
wajib_login()

# ==========================================
# KONEKSI
# ==========================================
conn_sk = st.connection("gsheets_sk", type=GSheetsConnection)
conn_parkir = st.connection("gsheets_parkir", type=GSheetsConnection)
conn_kas = st.connection("gsheets_kas", type=GSheetsConnection)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    logo_b64 = st.session_state.get("logo_b64")
    if logo_b64:
        st.markdown(
            f'<div style="text-align:center; padding:18px 0 6px 0;">'
            f'<img src="data:image/png;base64,{logo_b64}" width="78" height="auto" '
            f'style="display:inline-block; filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4));">'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="text-align:center; padding:18px 0 6px 0;">'
            '<div style="font-size:3rem;">🏛️</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("""
    <div style="text-align:center; padding:4px 0 14px 0;
                border-bottom:1px solid rgba(255,255,255,0.08);
                margin-bottom:14px;">
        <p style="font-family:'Inter',sans-serif; font-size:1.05rem; font-weight:800;
                  color:#f1f5f9 !important; margin:0 0 4px 0;">
            UPTD PASAR KANDANGAN</p>
        <p style="font-family:'Inter',sans-serif; font-size:0.78rem; font-weight:600;
                  color:#94a3b8 !important; margin:0;">
            KABUPATEN HULU SUNGAI SELATAN</p>
    </div>
    """, unsafe_allow_html=True)

    st.page_link("Home.py", label="🏠  Beranda", use_container_width=True)

    st.markdown(
        '<div style="padding: 8px 4px 4px 4px;">'
        '<p style="font-family:\'Inter\',sans-serif; font-size:0.7rem; font-weight:600;'
        'color:#64748b !important; text-transform:uppercase; letter-spacing:0.06em;'
        'margin:0 0 6px 0;">MODUL</p></div>',
        unsafe_allow_html=True
    )

    st.page_link("pages/1_📋_SK_Toko.py", label="📋  SK TOKO", use_container_width=True)
    st.page_link("pages/2_🅿️_Parkir.py", label="🅿️  PARKIR", use_container_width=True)
    st.page_link("pages/3_💰_Kas.py", label="💰  KAS UPTD", use_container_width=True)

    st.markdown(
        '<div style="padding: 16px 4px 4px 4px;">'
        '<p style="font-family:\'Inter\',sans-serif; font-size:0.7rem; font-weight:600;'
        'color:#64748b !important; text-transform:uppercase; letter-spacing:0.06em;'
        'margin:0 0 6px 0;">SISTEM</p></div>',
        unsafe_allow_html=True
    )

    st.page_link("pages/4_⚙️_Pengaturan.py", label="⚙️  PENGATURAN", use_container_width=True)

    if st.button("🚪  Logout", use_container_width=True, key="btn_logout_setting"):
        logout()

    st.markdown("""
    <div style="text-align:center; padding:24px 0 8px 0;
                border-top:1px solid rgba(255,255,255,0.06); margin-top:40px;">
        <p style="font-family:'Inter',sans-serif; font-size:0.56rem;
                  color:#64748b !important; margin:0;">Developed by</p>
        <p style="font-family:'Inter',sans-serif; font-size:0.68rem; font-weight:700;
                  color:#94a3b8 !important; margin:2px 0 0 0;">M. Luthfi Renaldi</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================
c_head, c_btn = st.columns([0.88, 0.12])
c_head.title("PENGATURAN")
with c_btn:
    tombol_refresh("ref_pengaturan")

st.caption(f"Login sebagai: **{get_current_user()}**")

# ==========================================
# TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "INFO AKUN",
    "BACKUP DATA",
    "RINGKASAN SHEETS",
    "TENTANG APLIKASI"
])

# ==========================================
# TAB 1 - INFO AKUN
# ==========================================
with tab1:
    st.subheader("Informasi Akun")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Username", get_current_user())
    with c2:
        st.metric("Role", "ADMIN")

    st.divider()

    st.subheader("Ubah Password")
    st.info(
        "Untuk mengubah password, edit langsung di **Streamlit Secrets**:\n\n"
        "```\n"
        "[admin]\n"
        "username = \"admin\"\n"
        "password = \"password_baru\"\n"
        "```\n\n"
        "Buka Manage app → Settings → Secrets di Streamlit Cloud."
    )

    st.divider()

    if st.button("LOGOUT SEKARANG", type="primary", use_container_width=True):
        logout()

# ==========================================
# TAB 2 - BACKUP DATA
# ==========================================
with tab2:
    st.subheader("Backup Data ke Excel")
    st.caption("Download semua data dari Google Sheets sebagai file Excel untuk backup manual.")

    st.divider()

    # SK TOKO
    st.markdown("### Data SK Toko")
    df_sk = load_data(conn_sk, WS_SK)
    if not df_sk.empty:
        st.caption(f"Total data: **{len(df_sk[df_sk['No'] != '-'])}** baris")
        csv_sk = df_sk[df_sk['No'] != '-'].to_csv(index=False).encode('utf-8')
        st.download_button(
            "DOWNLOAD SK TOKO (CSV)",
            data=csv_sk,
            file_name=f"backup_sk_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_sk"
        )
    else:
        st.info("Data SK kosong.")

    st.divider()

    # PARKIR
    st.markdown("### Data Parkir")
    df_pk = load_data(conn_parkir, WS_PARKIR)
    if not df_pk.empty:
        st.caption(f"Total data: **{len(df_pk)}** baris")
        csv_pk = df_pk.to_csv(index=False).encode('utf-8')
        st.download_button(
            "DOWNLOAD PARKIR (CSV)",
            data=csv_pk,
            file_name=f"backup_parkir_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_pk"
        )
    else:
        st.info("Data Parkir kosong.")

    st.divider()

    # KAS
    st.markdown("### Data Kas UPTD")
    df_ks = load_data(conn_kas, WS_KAS)
    if not df_ks.empty:
        st.caption(f"Total data: **{len(df_ks[df_ks['No'] != '-'])}** baris")
        csv_ks = df_ks[df_ks['No'] != '-'].to_csv(index=False).encode('utf-8')
        st.download_button(
            "DOWNLOAD KAS UPTD (CSV)",
            data=csv_ks,
            file_name=f"backup_kas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_ks"
        )
    else:
        st.info("Data Kas kosong.")

# ==========================================
# TAB 3 - RINGKASAN SHEETS
# ==========================================
with tab3:
    st.subheader("Ringkasan Data Google Sheets")

    df_sk = load_data(conn_sk, WS_SK)
    df_pk = load_data(conn_parkir, WS_PARKIR)
    df_ks = load_data(conn_kas, WS_KAS)

    r1, r2, r3 = st.columns(3)

    with r1:
        total_sk = len(df_sk[df_sk['No'] != '-']) if not df_sk.empty else 0
        st.metric("Total Data SK", total_sk)

    with r2:
        total_pk = len(df_pk) if not df_pk.empty else 0
        st.metric("Total Data Parkir", total_pk)

    with r3:
        total_ks = len(df_ks[df_ks['No'] != '-']) if not df_ks.empty else 0
        st.metric("Total Data Kas", total_ks)

    st.divider()

    st.markdown("### Worksheet yang Terhubung")
    st.dataframe(
        pd.DataFrame({
            "Modul": ["SK Toko", "Parkir", "Kas UPTD"],
            "Worksheet": [WS_SK, WS_PARKIR, WS_KAS],
            "Status": ["Terhubung", "Terhubung", "Terhubung"],
            "Jumlah Data": [total_sk, total_pk, total_ks]
        }),
        hide_index=True,
        use_container_width=True
    )

# ==========================================
# TAB 4 - TENTANG
# ==========================================
with tab4:
    st.subheader("Tentang Aplikasi")

    st.markdown("""
    **UPTD PASAR KANDANGAN**
    Kabupaten Hulu Sungai Selatan

    Aplikasi internal untuk:
    - Manajemen perpanjangan SK Toko
    - Rekap setoran parkir harian
    - Pencatatan Kas UPTD

    ---

    **Versi:** 2.0
    **Developed by:** M. Luthfi Renaldi
    **Stack:** Python, Streamlit, Google Sheets

    ---

    ### Modul Tersedia
    | Modul | Fungsi |
    |---|---|
    | SK Toko | Pengantaran & pengambilan berkas |
    | Parkir | Rekap karcis & konfirmasi setoran |
    | Kas UPTD | Catat transaksi masuk/keluar |
    | Pengaturan | Akun, backup, info aplikasi |
    """)

    st.divider()

    st.caption("© 2025 UPTD Pasar Kandangan. All rights reserved.")
