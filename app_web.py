import streamlit as st
import pandas as pd
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os
import base64
import urllib.request

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="logo_hss.png",
    layout="wide"
)

# ==========================================
# KONEKSI
# ==========================================
conn_sk     = st.connection("gsheets_sk",     type=GSheetsConnection)
conn_parkir = st.connection("gsheets_parkir", type=GSheetsConnection)
conn_kas    = st.connection("gsheets_kas",    type=GSheetsConnection)

# ==========================================
# KOLOM WAJIB
# ==========================================
KOLOM_PARKIR = [
    "No", "Tanggal", "Nama_Petugas",
    "Pengambilan_Karcis_R2", "Pengambilan_Karcis_R4",
    "Khusus_Roda_R2", "Khusus_Roda_R4",
    "MPP_Roda_R2", "MPP_Roda_R4",
    "Total_Karcis_R2", "Total_Karcis_R4",
    "Status_Khusus", "Status_MPP",
    "Sisa_Stok_R2", "Sisa_Stok_R4",
    "Status_Cetak",
]

KOLOM_SK = [
    "No", "Tanggal_Pengantaran", "Tanggal_Pengambilan",
    "Nama_Toko", "No_Toko", "Nama_Pemilik_Asli",
    "Nama_Pengantar_Berkas", "Penerima_Berkas",
]

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
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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
# CUSTOM CSS + ANIMASI
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main {
        background: linear-gradient(160deg, #f8fafc 0%, #f1f5f9 100%) !important;
        color-scheme: light !important;
    }

    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .stAppDeployButton { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    button[title="View fullscreen"] { display: none !important; }

    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] button[aria-label*="sidebar"],
    [data-testid="stSidebar"] button[title*="sidebar"] {
        color: #ffffff !important;
        background: rgba(255,255,255,0.16) !important;
        border: 1.5px solid rgba(255,255,255,0.35) !important;
        border-radius: 8px !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stSidebar"] button[kind="header"]:hover,
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover {
        background: rgba(255,255,255,0.28) !important;
    }
    [data-testid="stSidebar"] button[kind="header"] svg,
    [data-testid="stSidebar"] button[kind="header"] svg *,
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg * {
        color: #ffffff !important; fill: #ffffff !important;
        stroke: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    }
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] > button,
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] > button {
        color: #111827 !important; background: #ffffff !important;
        border: 1.5px solid #d1d5db !important; border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12) !important;
        opacity: 1 !important; visibility: visible !important;
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="collapsedControl"] svg *,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg * {
        color: #111827 !important; fill: #111827 !important;
        stroke: #111827 !important; -webkit-text-fill-color: #111827 !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    [data-testid="stSidebar"] > div { background: transparent !important; }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        font-family: 'Inter', sans-serif !important; color: #e2e8f0 !important;
    }

    [data-testid="stSidebar"] .stButton { margin-bottom: 0 !important; margin-top: 0 !important; }
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important; font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important; font-weight: 600 !important;
        padding: 8px 12px !important; margin: 1px 0 !important;
        border-radius: 8px !important; text-align: left !important;
        justify-content: flex-start !important; white-space: nowrap !important;
        overflow: hidden !important; text-overflow: ellipsis !important;
        transition: background 0.2s ease, color 0.2s ease,
                    transform 0.15s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.06) !important; color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.08) !important; color: #e2e8f0 !important;
        border-color: rgba(255,255,255,0.14) !important; transform: translateX(3px) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(96,165,250,0.14) !important;
        border: 1px solid rgba(96,165,250,0.28) !important; color: #93c5fd !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: rgba(96,165,250,0.22) !important;
        color: #bfdbfe !important; transform: translateX(3px) !important;
    }

    .submenu-container {
        overflow: hidden;
        animation: submenuSlide 0.38s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transform-origin: top center;
    }
    @keyframes submenuSlide {
        from { max-height: 0; opacity: 0; transform: translateY(-8px) scaleY(0.92); }
        to   { max-height: 400px; opacity: 1; transform: translateY(0) scaleY(1); }
    }

    .main h1 { font-size: 1.55rem !important; font-weight: 800 !important;
               color: #0f172a !important; letter-spacing: -0.03em !important; }
    .main h2 { font-size: 1.15rem !important; font-weight: 700 !important;
               color: #1e293b !important; letter-spacing: -0.02em !important; }
    .main h3 { font-size: 0.98rem !important; font-weight: 600 !important;
               color: #334155 !important; }
    .main p, .main [data-testid="stMarkdownContainer"] p {
        font-size: 0.88rem !important; font-weight: 400 !important;
        line-height: 1.6 !important; color: #374151 !important;
    }
    .main strong { font-weight: 700 !important; color: #1e293b !important; }

    .main .stTextInput label, .main .stNumberInput label,
    .main .stSelectbox label, .main .stCheckbox label {
        font-size: 0.78rem !important; font-weight: 600 !important; color: #374151 !important;
    }
    .main .stTextInput input, .main .stNumberInput input {
        font-size: 0.88rem !important; font-weight: 500 !important;
        color: #1e293b !important; background: #ffffff !important;
        border: 1.5px solid #d1d5db !important; border-radius: 8px !important;
        padding: 10px 14px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    .main .stTextInput input:focus, .main .stNumberInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    }

    [data-testid="stMetric"] {
        background: #ffffff !important; border: 1px solid #e5e7eb;
        border-radius: 10px; padding: 14px 18px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        transition: box-shadow 0.25s ease, transform 0.25s ease !important;
        animation: metricPop 0.5s cubic-bezier(0.34,1.4,0.64,1) both;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.09) !important;
        transform: translateY(-2px) !important;
    }
    @keyframes metricPop {
        from { opacity: 0; transform: scale(0.92) translateY(10px); }
        to   { opacity: 1; transform: scale(1) translateY(0); }
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important; font-weight: 600 !important;
        text-transform: uppercase !important; letter-spacing: 0.03em !important;
        color: #6b7280 !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.5rem !important; font-weight: 700 !important; color: #111827 !important;
    }

    .main .stButton > button {
        font-size: 0.82rem !important; font-weight: 600 !important;
        border-radius: 8px !important; color: #374151 !important;
        border: 1.5px solid #d1d5db !important; background: #ffffff !important;
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease !important;
    }
    .main .stButton > button:hover {
        background: #f3f4f6 !important; color: #111827 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important; transform: translateY(-1px) !important;
    }
    .main .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        border: none !important; color: #ffffff !important;
    }
    .main .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
        transform: translateY(-1px) !important;
    }
    .main .stDownloadButton > button {
        font-size: 0.82rem !important; font-weight: 600 !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: #ffffff !important; border: none !important;
        padding: 8px 16px !important; min-height: 40px !important;
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease !important;
        animation: btnPop 0.45s cubic-bezier(0.34,1.4,0.64,1) 0.15s both;
    }
    .main .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
        box-shadow: 0 4px 14px rgba(5,150,105,0.35) !important;
        transform: translateY(-1px) !important;
    }
    .main .stDownloadButton > button p,
    .main .stDownloadButton > button span {
        color: #ffffff !important; font-size: 0.82rem !important;
    }
    @keyframes btnPop {
        from { opacity: 0; transform: scale(0.88); }
        to   { opacity: 1; transform: scale(1); }
    }

    [data-testid="stForm"] {
        background: #ffffff !important; border: 1px solid #e5e7eb;
        border-radius: 12px; padding: 20px !important;
        animation: formFade 0.5s cubic-bezier(0.22,1,0.36,1) 0.1s both;
    }
    @keyframes formFade {
        from { opacity: 0; transform: translateY(10px) scale(0.99); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }

    [data-testid="stExpander"] {
        border: 1px solid #e5e7eb !important; border-radius: 10px !important;
        background: #ffffff !important; margin-bottom: 6px !important;
        transition: box-shadow 0.25s ease !important;
        animation: expanderSlide 0.42s cubic-bezier(0.22,1,0.36,1) both;
    }
    [data-testid="stExpander"]:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.06) !important; }
    @keyframes expanderSlide {
        from { opacity: 0; transform: translateX(-10px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    [data-testid="stAlert"] {
        animation: alertIn 0.4s cubic-bezier(0.22,1,0.36,1) both;
    }
    @keyframes alertIn {
        from { opacity: 0; transform: translateY(-6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stDataFrame"] {
        border-radius: 10px; border: 1px solid #e5e7eb;
        animation: tableIn 0.5s cubic-bezier(0.22,1,0.36,1) 0.1s both;
    }
    @keyframes tableIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stDataFrame"] th {
        font-family: 'Inter', sans-serif !important; font-size: 0.7rem !important;
        font-weight: 700 !important; text-transform: uppercase !important;
        color: #4b5563 !important; background: #f9fafb !important;
    }
    [data-testid="stDataFrame"] td {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important; color: #374151 !important;
    }

    .main [data-testid="stAlert"] p { font-size: 0.84rem !important; font-weight: 500 !important; }
    .main hr {
        border: none !important; border-top: 1px solid #e5e7eb !important;
        animation: hrExpand 0.6s cubic-bezier(0.22,1,0.36,1) both;
        transform-origin: left center;
    }
    @keyframes hrExpand {
        from { opacity: 0; transform: scaleX(0); }
        to   { opacity: 1; transform: scaleX(1); }
    }

    .main .block-container {
        animation: pageEnter 0.55s cubic-bezier(0.22,1,0.36,1) both;
        max-width: 80%; margin: 0 auto;
    }
    @keyframes pageEnter {
        from { opacity: 0; transform: translateY(16px); filter: blur(3px); }
        to   { opacity: 1; transform: translateY(0);    filter: blur(0px); }
    }
    @media (max-width: 768px) {
        .main .block-container { max-width: 100%; padding-left: 1rem; padding-right: 1rem; }
    }

    .main > div > div > div > div > div:nth-child(1)  { animation: itemFadeUp 0.45s 0.04s cubic-bezier(0.22,1,0.36,1) both; }
    .main > div > div > div > div > div:nth-child(2)  { animation: itemFadeUp 0.45s 0.08s cubic-bezier(0.22,1,0.36,1) both; }
    .main > div > div > div > div > div:nth-child(3)  { animation: itemFadeUp 0.45s 0.12s cubic-bezier(0.22,1,0.36,1) both; }
    .main > div > div > div > div > div:nth-child(4)  { animation: itemFadeUp 0.45s 0.16s cubic-bezier(0.22,1,0.36,1) both; }
    .main > div > div > div > div > div:nth-child(5)  { animation: itemFadeUp 0.45s 0.20s cubic-bezier(0.22,1,0.36,1) both; }
    .main > div > div > div > div > div:nth-child(6)  { animation: itemFadeUp 0.45s 0.24s cubic-bezier(0.22,1,0.36,1) both; }
    .main > div > div > div > div > div:nth-child(7)  { animation: itemFadeUp 0.45s 0.28s cubic-bezier(0.22,1,0.36,1) both; }
    .main > div > div > div > div > div:nth-child(8)  { animation: itemFadeUp 0.45s 0.32s cubic-bezier(0.22,1,0.36,1) both; }
    .main > div > div > div > div > div:nth-child(n+9){ animation: itemFadeUp 0.45s 0.36s cubic-bezier(0.22,1,0.36,1) both; }
    @keyframes itemFadeUp {
        from { opacity: 0; transform: translateY(14px); filter: blur(2px); }
        to   { opacity: 1; transform: translateY(0);    filter: blur(0px); }
    }

    .petugas-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #bfdbfe; border-radius: 10px;
        padding: 12px 18px; margin-bottom: 12px;
        font-family: 'Inter', sans-serif; font-size: 0.88rem;
        font-weight: 600; color: #1e40af;
        animation: petugasIn 0.45s cubic-bezier(0.22,1,0.36,1) 0.05s both;
    }
    @keyframes petugasIn {
        from { opacity: 0; transform: translateX(-12px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    .badge-sudah {
        display: inline-block;
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46; font-family: 'Inter', sans-serif;
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.04em;
        padding: 3px 10px; border-radius: 20px; border: 1px solid #6ee7b7;
        animation: badgePop 0.35s cubic-bezier(0.34,1.4,0.64,1) both;
    }
    .badge-belum {
        display: inline-block;
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e; font-family: 'Inter', sans-serif;
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.04em;
        padding: 3px 10px; border-radius: 20px; border: 1px solid #fcd34d;
        animation: badgePop 0.35s cubic-bezier(0.34,1.4,0.64,1) both;
    }
    @keyframes badgePop {
        from { opacity: 0; transform: scale(0.7); }
        to   { opacity: 1; transform: scale(1); }
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


def tombol_refresh_pojok(key_btn):
    if st.button("🔄 Refresh", key=key_btn, use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ==========================================
# 2. FUNGSI HELPER
# ==========================================
def pastikan_kolom(df: pd.DataFrame, kolom_wajib: list) -> pd.DataFrame:
    """Tambahkan kolom yang tidak ada dengan nilai '-'"""
    for k in kolom_wajib:
        if k not in df.columns:
            df[k] = "-"
    return df


def load_data(conn_obj, worksheet: str) -> pd.DataFrame:
    try:
        df = conn_obj.read(worksheet=worksheet, ttl=0)
        if df is None or df.empty:
            # Kembalikan DataFrame kosong tapi dengan kolom yang benar
            if worksheet == "DATA_PARKIR":
                return pd.DataFrame(columns=KOLOM_PARKIR)
            elif worksheet == "DATA_PERPANJANGAN_SK":
                return pd.DataFrame(columns=KOLOM_SK)
            return pd.DataFrame()

        df = df.astype(str).replace(r'\.0$', '', regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip()
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")

        # Pastikan semua kolom wajib ada
        if worksheet == "DATA_PARKIR":
            df = pastikan_kolom(df, KOLOM_PARKIR)
        elif worksheet == "DATA_PERPANJANGAN_SK":
            df = pastikan_kolom(df, KOLOM_SK)

        return df

    except Exception as e:
        st.error(f"❌ Gagal membaca worksheet **{worksheet}**: {e}")
        if worksheet == "DATA_PARKIR":
            return pd.DataFrame(columns=KOLOM_PARKIR)
        elif worksheet == "DATA_PERPANJANGAN_SK":
            return pd.DataFrame(columns=KOLOM_SK)
        return pd.DataFrame()


def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns:
            return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except Exception:
        return 1


def safe_update(conn_obj, worksheet: str, data: pd.DataFrame) -> bool:
    try:
        conn_obj.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"❌ Gagal menyimpan ke **{worksheet}**: {e}")
        return False


def format_tgl_hari_indo(tgl_str):
    if not tgl_str or str(tgl_str).strip() in ["-", "nan", "NAN", "", "None"]:
        return ""
    try:
        tgl_bersih = str(tgl_str).strip().replace('/', '-')
        if len(tgl_bersih.split('-')[-1]) == 2:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%y")
        else:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%Y")
        hari = ["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU","MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except Exception:
        return str(tgl_str).upper()


def normalisasi_no(val):
    try:
        txt = str(val).replace("\u00a0", "").replace("'", "").strip()
        try:
            return str(int(float(txt)))
        except Exception:
            return txt
    except Exception:
        return ""


def safe_int(val) -> int:
    try:
        s = str(val).strip()
        if s in ['-', 'nan', '', 'None', 'null']:
            return 0
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def cari_tanggal_belum_input_parkir(df_p: pd.DataFrame):
    try:
        if df_p.empty or "Tanggal" not in df_p.columns:
            return None, pd.DataFrame()
        df = df_p.copy()
        df["Tgl_Cek"] = pd.to_datetime(df["Tanggal"], dayfirst=True, errors="coerce").dt.date
        hari_ini = datetime.now().date()
        kondisi_belum = (
            df["Total_Karcis_R2"].astype(str).str.strip().isin(["-","nan","","None","null"]) &
            df["Total_Karcis_R4"].astype(str).str.strip().isin(["-","nan","","None","null"])
        )
        df_belum = df[
            df["Tgl_Cek"].notna() &
            (df["Tgl_Cek"] <= hari_ini) &
            kondisi_belum
        ].copy()
        if df_belum.empty:
            return None, df_belum
        tanggal_awal = df_belum.sort_values("Tgl_Cek").iloc[0]["Tgl_Cek"]
        return tanggal_awal, df_belum
    except Exception:
        return None, pd.DataFrame()


# ==========================================
# 3. FUNGSI PDF — TIDAK DIUBAH
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    UKURAN_KERTAS = (21.5 * cm, 33 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)
    M = 0.75 * cm
    TINGGI_POTONG = 12 * cm
    Y_POTONG = 33 * cm - TINGGI_POTONG
    Y_BASE = Y_POTONG + M
    X_POS = M
    LEBAR_BOX = 21.5 * cm - (2 * M)
    TINGGI_BOX = TINGGI_POTONG - (2 * M)
    TENGAH = 21.5 * cm / 2

    def gambar_garis_potong():
        c.setLineWidth(1); c.setDash(4, 4)
        c.line(0, Y_POTONG, 21.5 * cm, Y_POTONG)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(0.5 * cm, Y_POTONG + 0.15 * cm, "✂ --- Batas potong (Tinggi 12 cm) ---")
        c.setDash()

    gambar_garis_potong()
    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX)
    c.rect(X_POS + 0.15*cm, Y_BASE + 0.15*cm, LEBAR_BOX - 0.3*cm, TINGGI_BOX - 0.3*cm)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(TENGAH, Y_BASE + 9.3*cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    c.setLineWidth(2)
    c.line(TENGAH - 5.5*cm, Y_BASE + 9.0*cm, TENGAH + 5.5*cm, Y_BASE + 9.0*cm)
    yy = Y_BASE + 8.0*cm
    SEMUA_BERKAS = [
        "SK ASLI MENEMPATI","PAS FOTO 3X4 (2 LBR)","FC KTP PEMILIK",
        "FC KARTU SEWA","SURAT KUASA","SURAT KEHILANGAN",
    ]
    for i, item in enumerate(SEMUA_BERKAS, 1):
        c.setFont("Helvetica-BoldOblique", 10)
        c.drawString(X_POS + 1*cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10)
        x_status = X_POS + 14*cm
        c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        c.setLineWidth(1.5)
        y_strike = yy + 0.11*cm
        if item in berkas_list:
            c.line(x_status + 1.4*cm, y_strike, x_status + 3.5*cm, y_strike)
        else:
            c.line(x_status - 0.1*cm, y_strike, x_status + 0.8*cm, y_strike)
        yy -= 0.7*cm
    c.setLineWidth(1.5)
    c.line(X_POS + 0.15*cm, Y_BASE + 3.0*cm, X_POS + LEBAR_BOX - 0.15*cm, Y_BASE + 3.0*cm)
    c.line(TENGAH, Y_BASE + 0.15*cm, TENGAH, Y_BASE + 3.0*cm)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(X_POS + 5*cm, Y_BASE + 2.5*cm, "PENGANTAR BERKAS")
    c.drawCentredString(X_POS + 15*cm, Y_BASE + 2.5*cm, "PETUGAS PENERIMA")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(X_POS + 5*cm,  Y_BASE + 0.6*cm, f"( {str(data.get('Nama_Pengantar_Berkas','')).upper()} )")
    c.drawCentredString(X_POS + 15*cm, Y_BASE + 0.6*cm, f"( {str(data.get('Penerima_Berkas','')).upper()} )")
    c.showPage()

    gambar_garis_potong()
    c.saveState()
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.setFont("Helvetica-Bold", 35)
    c.translate(TENGAH, Y_BASE + (TINGGI_BOX / 2))
    c.rotate(25)
    c.drawCentredString(0, 0, "UPTD PASAR KANDANGAN")
    c.restoreState()
    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX)
    c.rect(X_POS + 0.15*cm, Y_BASE + 0.15*cm, LEBAR_BOX - 0.3*cm, TINGGI_BOX - 0.3*cm)
    y_tab = Y_BASE + 10.35*cm
    TINGGI_B = 1.05*cm
    DETAIL_ROWS = [
        ("NOMOR URUT",          data.get("No", "-")),
        ("TANGGAL TERIMA",      format_tgl_hari_indo(data.get("Tanggal_Pengantaran", "-"))),
        ("TANGGAL PENGAMBILAN", format_tgl_hari_indo(data.get("Tanggal_Pengambilan", "-"))),
        ("NAMA & NOMOR TOKO",   f"{data.get('Nama_Toko','-')} - {data.get('No_Toko','-')}"),
        ("NAMA PEMILIK (SK)",   data.get("Nama_Pemilik_Asli", "-")),
        ("NAMA PENGANTAR",      data.get("Nama_Pengantar_Berkas", "-")),
    ]
    for label, val in DETAIL_ROWS:
        c.setLineWidth(1.5)
        c.rect(X_POS + 0.15*cm, y_tab - TINGGI_B, 6.5*cm, TINGGI_B)
        c.rect(X_POS + 6.65*cm, y_tab - TINGGI_B, 13.2*cm, TINGGI_B)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(X_POS + 0.4*cm, y_tab - 0.7*cm, label)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(X_POS + 7.0*cm, y_tab - 0.7*cm, str(val).upper())
        y_tab -= TINGGI_B
    c.setFont("Helvetica-Bold", 10)
    c.drawString(X_POS + 0.6*cm, Y_BASE + 2.8*cm, "PERHATIAN:")
    c.setFont("Helvetica", 9)
    c.drawString(X_POS + 0.6*cm, Y_BASE + 2.2*cm,
                 "1. Simpan tanda terima ini sebagai syarat pengambilan SK asli.")
    c.drawString(X_POS + 0.6*cm, Y_BASE + 1.6*cm,
                 "2. Pengambilan SK hanya dapat dilakukan di jam kerja UPTD.")
    c.save()
    buffer.seek(0)
    return buffer


def cetak_tanda_terima_parkir(data) -> BytesIO:
    if isinstance(data, pd.Series):
        data = data.to_dict()
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    lebar_box, tinggi_box = 6.8*cm, 4.6*cm
    x_awal   = (lebar_kertas - lebar_box) / 2
    center_x = lebar_kertas / 2
    y_top    = 32*cm
    y_bottom = y_top - tinggi_box
    c.setLineWidth(1.2)
    c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    y_gp = y_bottom - 1.0*cm
    c.setDash(1, 3); c.setLineWidth(0.5)
    c.line(0, y_gp, lebar_kertas, y_gp)
    c.setDash()
    tgl_dis      = format_tgl_hari_indo(data.get('Tanggal', '-'))
    nama_petugas = str(data.get('Nama_Petugas', '-'))
    mpp_r2 = safe_int(data.get('MPP_Roda_R2', 0))
    mpp_r4 = safe_int(data.get('MPP_Roda_R4', 0))
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(center_x, y_top - 0.5*cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(center_x, y_top - 0.9*cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.line(x_awal + 0.3*cm, y_top - 1.1*cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1*cm)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_awal + 0.3*cm, y_top - 1.5*cm, f"TGL : {tgl_dis}")
    c.drawString(x_awal + 0.3*cm, y_top - 1.9*cm, f"NAMA : {nama_petugas.upper()}")
    y_tab = y_top - 2.2*cm
    t_row = 0.6*cm
    x_tab = x_awal + 0.3*cm
    l_tab = lebar_box - 0.6*cm
    for i, (jns, jml) in enumerate([("RODA 2", mpp_r2), ("RODA 4", mpp_r4)]):
        y_r = y_tab - ((i + 1) * t_row)
        c.rect(x_tab, y_r, l_tab, t_row)
        c.setFont("Helvetica", 6)
        c.drawString(x_tab + 0.1*cm, y_r + 0.2*cm, jns)
        c.drawCentredString(center_x, y_r + 0.2*cm, f"{jml} LBR")
        c.drawRightString(x_tab + l_tab - 0.1*cm, y_r + 0.2*cm, "MPP")
    c.showPage(); c.save()
    buffer.seek(0)
    return buffer


def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm))
    c.setFont("Helvetica-Bold", 10)
    X_POS = 0.75 * cm
    y_target = 21.5*cm + 0.75*cm + 10.35*cm - (1.05*cm * 2) - 0.7*cm
    c.drawString(X_POS + 7.0*cm, y_target, format_tgl_hari_indo(tgl_ambil).upper())
    c.save()
    buffer.seek(0)
    return buffer


# ==========================================
# 4. MODUL SK TOKO
# ==========================================
def halaman_pengantaran():
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.header("📝 INPUT PENGANTARAN BERKAS")
    with c_btn:
        tombol_refresh_pojok("ref_pengantaran")

    df_sk = load_data(conn_sk, "DATA_PERPANJANGAN_SK")

    # Debug info jika kosong
    if df_sk.empty:
        st.warning("⚠️ Data SK kosong atau gagal dimuat. Pastikan nama worksheet **DATA_PERPANJANGAN_SK** benar.")

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total       = len(df_sk[df_sk["No"] != "-"]) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    col_stat1.metric("📦 Total Berkas", total)
    col_stat2.metric("✅ Sudah Diambil", sudah_ambil)
    col_stat3.metric("⏳ Belum Diambil", total - sudah_ambil)

    SEMUA_BERKAS = [
        "SK ASLI MENEMPATI","PAS FOTO 3X4 (2 LBR)","FC KTP PEMILIK",
        "FC KARTU SEWA","SURAT KUASA","SURAT KEHILANGAN",
    ]
    if "sel_berkas" not in st.session_state:
        st.session_state["sel_berkas"] = []

    st.subheader("☑️ Pilih Berkas yang Dibawa:")
    cols_berkas = st.columns(3)
    sel_berkas  = []
    for i, item in enumerate(SEMUA_BERKAS):
        with cols_berkas[i % 3]:
            if st.checkbox(item, key=f"cb_{item}"):
                sel_berkas.append(item)

    st.divider()

    with st.form("form_pengantaran", clear_on_submit=False):
        st.subheader("📋 Data Pengantaran")
        next_no = get_next_no(df_sk)
        col1, col2 = st.columns(2)
        with col1:
            no_urut    = st.text_input("NOMOR URUT *", value=str(next_no))
            tgl_terima = st.text_input("TANGGAL TERIMA *", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko  = st.text_input("NAMA TOKO *").strip().upper()
            no_toko    = st.text_input("NOMOR TOKO *").strip().upper()
        with col2:
            nama_pemilik   = st.text_input("NAMA PEMILIK SK *").strip().upper()
            nama_pengantar = st.text_input("NAMA PENGANTAR *").strip().upper()
            nama_penerima  = st.text_input("NAMA PENERIMA *").strip().upper()

        if st.form_submit_button("💾 SIMPAN DATA", type="primary"):
            if not no_urut.strip() or not nama_toko or not nama_pemilik:
                st.error("❌ Data Wajib Diisi!")
            else:
                is_exist = (not df_sk.empty and
                            normalisasi_no(no_urut) in df_sk["No"].apply(normalisasi_no).values)
                new_row = {
                    "No": no_urut.strip(),
                    "Tanggal_Pengantaran":  tgl_terima,
                    "Tanggal_Pengambilan":  "-",
                    "Nama_Toko":            nama_toko,
                    "No_Toko":              no_toko,
                    "Nama_Pemilik_Asli":    nama_pemilik,
                    "Nama_Pengantar_Berkas":nama_pengantar,
                    "Penerima_Berkas":      nama_penerima,
                }
                if is_exist:
                    st.session_state["pending_sk"]      = new_row
                    st.session_state["show_confirm_sk"] = True
                else:
                    df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                    if safe_update(conn_sk, "DATA_PERPANJANGAN_SK", df_baru):
                        st.session_state["last_sk"]     = new_row
                        st.session_state["last_berkas"] = sel_berkas
                        st.success("✅ Berhasil!")
                        st.rerun()

    if st.session_state.get("show_confirm_sk"):
        st.warning("⚠️ Nomor sudah ada!")
        col_c1, col_c2 = st.columns(2)
        if col_c1.button("✅ YA, TIMPA DATA", type="primary"):
            d = st.session_state["pending_sk"]
            df_sk  = df_sk[df_sk["No"] != d["No"]]
            df_final = pd.concat([df_sk, pd.DataFrame([d])], ignore_index=True)
            if safe_update(conn_sk, "DATA_PERPANJANGAN_SK", df_final):
                st.session_state["last_sk"]         = d
                st.session_state["last_berkas"]     = sel_berkas
                st.session_state["show_confirm_sk"] = False
                st.rerun()
        if col_c2.button("❌ BATAL"):
            st.session_state["show_confirm_sk"] = False
            st.rerun()

    if "last_sk" in st.session_state:
        st.divider()
        l = st.session_state["last_sk"]
        st.download_button(
            "📥 DOWNLOAD PDF TANDA TERIMA",
            data=buat_pdf_full(l, st.session_state["last_berkas"]),
            file_name=f"TANDA_{l['No']}.pdf",
            mime="application/pdf",
        )

    st.divider()
    st.subheader("📊 DATA GOOGLE SHEETS")
    if not df_sk.empty:
        df_tampil = df_sk[df_sk["No"] != "-"].copy()
        if not df_tampil.empty:
            st.dataframe(df_tampil.sort_values(by="No", ascending=False),
                         use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data.")
    else:
        st.info("Belum ada data atau worksheet kosong.")


def halaman_pengambilan_sk():
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.header("PENGAMBILAN BERKAS SK")
    with c_btn:
        tombol_refresh_pojok("ref_ambil")

    df_m = load_data(conn_sk, "DATA_PERPANJANGAN_SK")

    if df_m.empty:
        st.warning("⚠️ Data SK kosong atau gagal dimuat. Pastikan worksheet **DATA_PERPANJANGAN_SK** ada.")
        return

    df_b = df_m[(df_m["Tanggal_Pengambilan"] == "-") & (df_m["No"] != "-")]

    no_cari = st.text_input(
        "🔍 CARI NOMOR URUT:",
        key="cari_no_sk_pengambilan",
        placeholder="Masukkan nomor urut, misal 1"
    ).strip()

    if no_cari:
        no_cari_norm = normalisasi_no(no_cari)
        mask_no = df_m["No"].apply(normalisasi_no) == no_cari_norm
        hasil   = df_m[mask_no]

        if not hasil.empty:
            data  = hasil.iloc[0]
            sudah = data["Tanggal_Pengambilan"] != "-"
            if sudah:
                st.success(f"✅ Sudah diambil pada: {format_tgl_hari_indo(data['Tanggal_Pengambilan'])}")
                st.download_button(
                    "🖨️ PRINT ULANG",
                    data=cetak_overprint(data["Tanggal_Pengambilan"]),
                    file_name=f"AMBIL_{no_cari_norm}.pdf",
                )
            else:
                st.warning(f"{data['Nama_Pemilik_Asli']}")
                tgl_a = st.text_input(
                    "📅 TANGGAL AMBIL:",
                    value=datetime.now().strftime("%d-%m-%Y"),
                    key="tgl_ambil_sk_pengambilan",
                )
                if st.button("✅ KONFIRMASI PENGAMBILAN"):
                    df_m.loc[mask_no, "Tanggal_Pengambilan"] = tgl_a
                    if safe_update(conn_sk, "DATA_PERPANJANGAN_SK", df_m):
                        st.success("Berhasil!")
                        st.rerun()
        else:
            st.error("❌ Nomor Urut tidak terdaftar.")

    st.divider()
    st.subheader(f"📊 BELUM DIAMBIL ({len(df_b)})")
    if not df_b.empty:
        st.dataframe(df_b.sort_values(by="No", ascending=True),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Semua berkas sudah diambil.")


# ==========================================
# 5. MODUL PARKIR
# ==========================================
def halaman_parkir(menu):
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.header(f"🅿️ {menu}")
    with c_btn:
        tombol_refresh_pojok("ref_parkir")

    df_p     = load_data(conn_parkir, "DATA_PARKIR")
    hari_ini = datetime.now().date()

    # ── GUARD: pastikan kolom wajib ada ──────────────────────────
    kolom_kurang = [k for k in KOLOM_PARKIR if k not in df_p.columns]
    if kolom_kurang:
        st.error(
            f"❌ Worksheet **DATA_PARKIR** tidak memiliki kolom: `{'`, `'.join(kolom_kurang)}`\n\n"
            f"Pastikan nama kolom di Google Sheets **persis** sama (case-sensitive)."
        )
        st.info("Kolom yang ditemukan: " + ", ".join(df_p.columns.tolist()) if not df_p.empty else "DataFrame kosong.")
        return

    if df_p.empty:
        st.warning("⚠️ Data PARKIR kosong atau worksheet belum ada isinya.")
        if menu != "KONFIRMASI":
            return

    # ── CEK BELUM INPUT ──────────────────────────────────────────
    if menu in ["INPUT REKAP", "INPUT STOK"]:
        tgl_belum, df_belum = cari_tanggal_belum_input_parkir(df_p)
        if tgl_belum:
            st.warning(f"⚠️ Input parkir belum terisi mulai: **{tgl_belum.strftime('%d-%m-%Y')}**")
            with st.expander("📅 Lihat daftar tanggal yang belum diinput", expanded=False):
                if not df_belum.empty:
                    tampil = df_belum[["Tanggal", "Nama_Petugas"]].copy()
                    st.dataframe(tampil, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Semua data parkir sampai hari ini sudah terinput.")

    # ── INPUT TANGGAL ─────────────────────────────────────────────
    tgl_input_user = st.text_input(
        "🔍 MASUKKAN TANGGAL",
        value=datetime.now().strftime("%d-%m-%Y"),
        key="tgl_input_parkir",
    )

    # Inisialisasi default
    dt_user = None
    baris   = pd.DataFrame()
    idx     = None
    nama_p  = "-"
    sisa_r2 = 0
    sisa_r4 = 0

    try:
        tgl_bersih = str(tgl_input_user).strip().replace('/', '-')
        if len(tgl_bersih.split('-')[-1]) == 2:
            dt_user = datetime.strptime(tgl_bersih, "%d-%m-%y").date()
        else:
            dt_user = datetime.strptime(tgl_bersih, "%d-%m-%Y").date()

        if not df_p.empty:
            df_p['Tgl_Temp'] = pd.to_datetime(
                df_p['Tanggal'], dayfirst=True, errors='coerce').dt.date
            baris = df_p[df_p['Tgl_Temp'] == dt_user]
    except Exception:
        baris = pd.DataFrame()

    if baris.empty and menu != "KONFIRMASI":
        st.warning("⚠️ Tanggal belum ada di jadwal Sheet. Silakan isi jadwal dulu.")
        if 'Tgl_Temp' in df_p.columns:
            df_p = df_p.drop(columns=['Tgl_Temp'])
        return

    if not baris.empty:
        idx    = baris.index[0]
        nama_p = str(baris.iloc[0]["Nama_Petugas"])
        df_petugas_sama = df_p[
            (df_p["Nama_Petugas"] == nama_p) & (df_p.index < idx)
        ]
        if not df_petugas_sama.empty:
            idx_terakhir = df_petugas_sama.index[-1]
            sisa_r2 = pd.to_numeric(
                df_petugas_sama.loc[idx_terakhir, "Sisa_Stok_R2"], errors='coerce')
            sisa_r4 = pd.to_numeric(
                df_petugas_sama.loc[idx_terakhir, "Sisa_Stok_R4"], errors='coerce')
        sisa_r2 = 0 if pd.isna(sisa_r2) else int(sisa_r2)
        sisa_r4 = 0 if pd.isna(sisa_r4) else int(sisa_r4)

    # ══════════════════════════════════════════
    # INPUT REKAP
    # ══════════════════════════════════════════
    if menu == "INPUT REKAP":
        if baris.empty or idx is None:
            st.warning("⚠️ Data tidak ditemukan untuk tanggal tersebut.")
            return

        st.markdown(
            f'<div class="petugas-box">👤 PETUGAS: <b>{nama_p}</b> &nbsp;|&nbsp; '
            f'📅 <b>{format_tgl_hari_indo(tgl_input_user)}</b></div>',
            unsafe_allow_html=True,
        )
        col_s1, col_s2 = st.columns(2)
        col_s1.metric(f"📊 Sisa Karcis R2 ({nama_p})", sisa_r2)
        col_s2.metric(f"📊 Sisa Karcis R4 ({nama_p})", sisa_r4)

        with st.form("form_rekap_harian", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                tr2 = st.number_input("TOTAL KARCIS R2", min_value=0)
                mr2 = st.number_input("MPP RODA R2",     min_value=0)
            with c2:
                tr4 = st.number_input("TOTAL KARCIS R4", min_value=0)
                mr4 = st.number_input("MPP RODA R4",     min_value=0)

            cb1, cb2 = st.columns(2)
            with cb1:
                subm  = st.form_submit_button("💾 SIMPAN REKAP", type="primary", use_container_width=True)
            with cb2:
                reset = st.form_submit_button("🔄 RESET FORM", use_container_width=True)

            if reset:
                st.rerun()

            if subm:
                pk2_lama = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R2"], errors='coerce')
                pk4_lama = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R4"], errors='coerce')
                pk2_lama = 0 if pd.isna(pk2_lama) else pk2_lama
                pk4_lama = 0 if pd.isna(pk4_lama) else pk4_lama

                sn2 = (pk2_lama + sisa_r2) - tr2
                sn4 = (pk4_lama + sisa_r4) - tr4

                data_baru = {
                    "tr2_str": str(tr2), "mr2_str": str(mr2),
                    "sn2_str": str(sn2), "kh2_str": str(tr2 - mr2),
                    "tr4_str": str(tr4), "mr4_str": str(mr4),
                    "sn4_str": str(sn4), "kh4_str": str(tr4 - mr4),
                }

                karcis_r2_skrg = str(df_p.loc[idx, "Total_Karcis_R2"]).strip()
                sudah_diisi    = karcis_r2_skrg not in ["-", "nan", ""]

                if sudah_diisi:
                    st.session_state["pending_parkir"]      = data_baru
                    st.session_state["pending_idx"]         = idx
                    st.session_state["show_confirm_parkir"] = True
                else:
                    df_p.loc[idx, ["Total_Karcis_R2","MPP_Roda_R2",
                                   "Sisa_Stok_R2","Khusus_Roda_R2"]] = [
                        data_baru["tr2_str"], data_baru["mr2_str"],
                        data_baru["sn2_str"], data_baru["kh2_str"],
                    ]
                    df_p.loc[idx, ["Total_Karcis_R4","MPP_Roda_R4",
                                   "Sisa_Stok_R4","Khusus_Roda_R4"]] = [
                        data_baru["tr4_str"], data_baru["mr4_str"],
                        data_baru["sn4_str"], data_baru["kh4_str"],
                    ]
                    df_p.loc[idx, ["Status_Khusus","Status_MPP","Status_Cetak"]] = [
                        "BELUM","BELUM","BELUM"
                    ]
                    if 'Tgl_Temp' in df_p.columns:
                        df_p = df_p.drop(columns=['Tgl_Temp'])
                    if safe_update(conn_parkir, "DATA_PARKIR", df_p):
                        st.success("✅ Berhasil Diupdate!")
                        st.rerun()

        if st.session_state.get("show_confirm_parkir"):
            st.warning(
                f"⚠️ Data **{tgl_input_user}** sudah diisi! Yakin ingin menimpa?"
            )
            col_c1, col_c2 = st.columns(2)
            if col_c1.button("✅ YA, TIMPA DATA", type="primary", key="btn_timpa_parkir"):
                d     = st.session_state["pending_parkir"]
                p_idx = st.session_state["pending_idx"]
                df_p.loc[p_idx, ["Total_Karcis_R2","MPP_Roda_R2",
                                  "Sisa_Stok_R2","Khusus_Roda_R2"]] = [
                    d["tr2_str"], d["mr2_str"], d["sn2_str"], d["kh2_str"]
                ]
                df_p.loc[p_idx, ["Total_Karcis_R4","MPP_Roda_R4",
                                  "Sisa_Stok_R4","Khusus_Roda_R4"]] = [
                    d["tr4_str"], d["mr4_str"], d["sn4_str"], d["kh4_str"]
                ]
                if str(df_p.loc[p_idx, "Status_Cetak"]).strip() != "SUDAH":
                    df_p.loc[p_idx, ["Status_Khusus","Status_MPP","Status_Cetak"]] = [
                        "BELUM","BELUM","BELUM"
                    ]
                if 'Tgl_Temp' in df_p.columns:
                    df_p = df_p.drop(columns=['Tgl_Temp'])
                if safe_update(conn_parkir, "DATA_PARKIR", df_p):
                    st.session_state["show_confirm_parkir"] = False
                    st.success("✅ Berhasil Ditimpa!")
                    st.rerun()
            if col_c2.button("❌ BATAL", key="btn_batal_parkir"):
                st.session_state["show_confirm_parkir"] = False
                st.rerun()

    # ══════════════════════════════════════════
    # INPUT STOK
    # ══════════════════════════════════════════
    elif menu == "INPUT STOK":
        if baris.empty or idx is None:
            st.warning("⚠️ Data tidak ditemukan untuk tanggal tersebut.")
            return

        st.subheader("📦 UPDATE PENGAMBILAN KARCIS BARU")
        st.markdown(
            f'<div class="petugas-box">Mengisi stok baru untuk petugas: <b>{nama_p}</b></div>',
            unsafe_allow_html=True,
        )

        with st.form("form_stok_baru", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                pk2 = st.number_input("PENGAMBILAN KARCIS R2", min_value=0)
            with c2:
                pk4 = st.number_input("PENGAMBILAN KARCIS R4", min_value=0)

            cb1, cb2 = st.columns(2)
            with cb1:
                subm_stok  = st.form_submit_button("➕ TAMBAH STOK", type="primary", use_container_width=True)
            with cb2:
                reset_stok = st.form_submit_button("🔄 RESET FORM", use_container_width=True)

            if reset_stok:
                st.rerun()

            if subm_stok:
                df_p.loc[idx, ["Pengambilan_Karcis_R2","Pengambilan_Karcis_R4"]] = [
                    str(pk2), str(pk4)
                ]
                if 'Tgl_Temp' in df_p.columns:
                    df_p = df_p.drop(columns=['Tgl_Temp'])
                if safe_update(conn_parkir, "DATA_PARKIR", df_p):
                    st.success("✅ Stok Berhasil Ditambahkan!")
                    st.rerun()

    # ══════════════════════════════════════════
    # KONFIRMASI
    # ══════════════════════════════════════════
    elif menu == "KONFIRMASI":
        if df_p.empty:
            st.info("Tidak ada data parkir.")
            return

        # Guard kolom sebelum filter
        if "Total_Karcis_R2" not in df_p.columns or "Total_Karcis_R4" not in df_p.columns:
            st.error("❌ Kolom Total_Karcis_R2 / Total_Karcis_R4 tidak ditemukan.")
            return

        kondisi_angka_r2 = df_p["Total_Karcis_R2"].astype(str).str.strip().str.isnumeric()
        kondisi_angka_r4 = df_p["Total_Karcis_R4"].astype(str).str.strip().str.isnumeric()
        df_pen = df_p[kondisi_angka_r2 | kondisi_angka_r4].copy()

        if df_pen.empty:
            st.info("TIDAK ADA DATA KONFIRMASI.")
        else:
            df_pen['Tgl_Temp'] = pd.to_datetime(
                df_pen['Tanggal'], dayfirst=True, errors='coerce').dt.date

            # Pastikan kolom status ada
            for kol_stat in ["Status_Khusus", "Status_MPP", "Status_Cetak"]:
                if kol_stat not in df_pen.columns:
                    df_pen[kol_stat] = "BELUM"

            df_terfilter = df_pen[
                (df_pen["Status_Khusus"] != "SUDAH") |
                (df_pen["Status_MPP"]    != "SUDAH") |
                (df_pen["Status_Cetak"]  != "SUDAH") |
                (df_pen['Tgl_Temp']      == hari_ini)
            ].copy()

            if df_terfilter.empty:
                st.info("TIDAK ADA DATA KONFIRMASI (Semua sudah Lunas).")
            else:
                df_terfilter = df_terfilter.sort_index(ascending=False).head(10)

                for i, row in df_terfilter.iterrows():
                    stat_k = str(row.get("Status_Khusus", "BELUM")).strip()
                    stat_m = str(row.get("Status_MPP",    "BELUM")).strip()
                    stat_c = str(row.get("Status_Cetak",  "BELUM")).strip()
                    lunas  = (stat_k == "SUDAH") and (stat_m == "SUDAH") and (stat_c == "SUDAH")
                    ikon   = "✅ [SELESAI]" if lunas else "📦 [BELUM SELESAI]"

                    with st.expander(
                        f"{ikon} {row['Tanggal']} - {row['Nama_Petugas']}",
                        expanded=not lunas,
                    ):
                        if lunas:
                            st.success("✨ PROSES SELESAI: Data ini akan otomatis hilang besok.")

                        ck, cm_col = st.columns(2)

                        with ck:
                            badge_k = (
                                '<span class="badge-sudah">✅ SUDAH</span>'
                                if stat_k == "SUDAH"
                                else '<span class="badge-belum">⏳ BELUM</span>'
                            )
                            st.markdown(
                                f"**KHUSUS** {badge_k}<br>"
                                f"R2: {row.get('Khusus_Roda_R2','-')} &nbsp;|&nbsp; "
                                f"R4: {row.get('Khusus_Roda_R4','-')}",
                                unsafe_allow_html=True,
                            )
                            if stat_k != "SUDAH":
                                if st.button("TERIMA KHUSUS", key=f"k{i}", use_container_width=True):
                                    df_p.loc[i, "Status_Khusus"] = "SUDAH"
                                    safe_update(conn_parkir, "DATA_PARKIR", df_p)
                                    st.rerun()
                            else:
                                st.success("✅ Khusus Diterima")

                        with cm_col:
                            badge_m = (
                                '<span class="badge-sudah">✅ SUDAH</span>'
                                if stat_m == "SUDAH"
                                else '<span class="badge-belum">⏳ BELUM</span>'
                            )
                            st.markdown(
                                f"**MPP** {badge_m}<br>"
                                f"R2: {row.get('MPP_Roda_R2','-')} &nbsp;|&nbsp; "
                                f"R4: {row.get('MPP_Roda_R4','-')}",
                                unsafe_allow_html=True,
                            )
                            if stat_m != "SUDAH":
                                if st.button("TERIMA MPP", key=f"m{i}",
                                             type="primary", use_container_width=True):
                                    df_p.loc[i, "Status_MPP"] = "SUDAH"
                                    safe_update(conn_parkir, "DATA_PARKIR", df_p)
                                    st.rerun()
                            else:
                                st.download_button(
                                    "🖨️ CETAK PDF MPP",
                                    data=cetak_tanda_terima_parkir(row.to_dict()),
                                    file_name=f"MPP_{row['Tanggal']}.pdf",
                                    key=f"p{i}",
                                    use_container_width=True,
                                )
                                if stat_c != "SUDAH":
                                    if st.button("✅ SUDAH CETAK", key=f"c{i}",
                                                 use_container_width=True):
                                        df_p.loc[i, "Status_Cetak"] = "SUDAH"
                                        safe_update(conn_parkir, "DATA_PARKIR", df_p)
                                        st.rerun()
                                else:
                                    st.success("✅ Telah Dicetak")

    # Bersihkan kolom sementara
    if 'Tgl_Temp' in df_p.columns:
        df_p = df_p.drop(columns=['Tgl_Temp'])

    # ── LOG INPUT TERAKHIR ────────────────────────────────────────
    with st.expander("📊 LOG INPUT TERAKHIR", expanded=False):
        if menu == "INPUT REKAP":
            df_isi = df_p[
                df_p["Total_Karcis_R2"].astype(str).str.strip().apply(
                    lambda x: x not in ["-","nan",""]) |
                df_p["Total_Karcis_R4"].astype(str).str.strip().apply(
                    lambda x: x not in ["-","nan",""])
            ].copy()
            if not df_isi.empty:
                df_isi["Tgl_Sort"] = pd.to_datetime(
                    df_isi["Tanggal"], dayfirst=True, errors="coerce").dt.date
                last = df_isi[df_isi["Tgl_Sort"] == dt_user] if dt_user else pd.DataFrame()
                if last.empty:
                    last = df_isi.sort_values("Tgl_Sort", ascending=False).head(1)
                else:
                    last = last.head(1)
                kolom     = ["Tanggal","Nama_Petugas","Total_Karcis_R2",
                             "Total_Karcis_R4","MPP_Roda_R2","MPP_Roda_R4"]
                kolom_ada = [k for k in kolom if k in last.columns]
                st.dataframe(last[kolom_ada], hide_index=True, use_container_width=True)
            else:
                st.info("Belum ada data yang diinput.")

        elif menu == "INPUT STOK":
            df_isi = df_p[
                df_p["Pengambilan_Karcis_R2"].astype(str).str.strip().apply(
                    lambda x: x not in ["-","nan",""]) |
                df_p["Pengambilan_Karcis_R4"].astype(str).str.strip().apply(
                    lambda x: x not in ["-","nan",""])
            ].copy()
            if not df_isi.empty:
                df_isi["Tgl_Sort"] = pd.to_datetime(
                    df_isi["Tanggal"], dayfirst=True, errors="coerce").dt.date
                last = df_isi[df_isi["Tgl_Sort"] == dt_user] if dt_user else pd.DataFrame()
                if last.empty:
                    last = df_isi.sort_values("Tgl_Sort", ascending=False).head(1)
                else:
                    last = last.head(1)
                kolom     = ["Tanggal","Nama_Petugas",
                             "Pengambilan_Karcis_R2","Pengambilan_Karcis_R4"]
                kolom_ada = [k for k in kolom if k in last.columns]
                st.dataframe(last[kolom_ada], hide_index=True, use_container_width=True)
            else:
                st.info("Belum ada data yang diinput.")

        elif menu == "KONFIRMASI":
            df_isi = df_p[
                df_p["Status_Khusus"].astype(str).str.strip().apply(
                    lambda x: x not in ["-","nan",""]) |
                df_p["Status_MPP"].astype(str).str.strip().apply(
                    lambda x: x not in ["-","nan",""]) |
                df_p["Status_Cetak"].astype(str).str.strip().apply(
                    lambda x: x not in ["-","nan",""])
            ].copy()
            if not df_isi.empty:
                df_isi["Tgl_Sort"] = pd.to_datetime(
                    df_isi["Tanggal"], dayfirst=True, errors="coerce")
                last = df_isi.sort_values("Tgl_Sort", ascending=False).head(1)
                kolom     = ["Tanggal","Nama_Petugas",
                             "Status_Khusus","Status_MPP","Status_Cetak"]
                kolom_ada = [k for k in kolom if k in last.columns]
                st.dataframe(last[kolom_ada], hide_index=True, use_container_width=True)
            else:
                st.info("Belum ada data yang diinput.")


# ==========================================
# 6. HALAMAN WELCOME
# ==========================================
def halaman_welcome():
    logo_b64  = st.session_state.get("logo_b64")
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" width="140" height="auto" '
        f'style="display:inline-block;">'
        if logo_b64
        else '<div style="font-size:6rem; line-height:1;">🏛️</div>'
    )
    st.markdown(f"""
    <style>
        .welcome-wrapper {{
            display:flex; flex-direction:column; align-items:center;
            justify-content:center; min-height:70vh; text-align:center; padding:20px;
        }}
        .welcome-logo {{
            animation: logoEntry 1s cubic-bezier(0.34,1.56,0.64,1) forwards,
                       logoPulse 3.5s ease-in-out 2s infinite;
            opacity:0; filter:drop-shadow(0 8px 24px rgba(0,0,0,0.12)); will-change:transform,opacity;
        }}
        @keyframes logoEntry {{
            0%   {{ opacity:0; transform:scale(0.3) translateY(30px); filter:blur(10px); }}
            50%  {{ opacity:1; filter:blur(0); }}
            70%  {{ transform:scale(1.06) translateY(-4px); }}
            100% {{ opacity:1; transform:scale(1) translateY(0); filter:blur(0); }}
        }}
        @keyframes logoPulse {{
            0%,100% {{ transform:scale(1); }}
            50%     {{ transform:scale(1.04); filter:drop-shadow(0 12px 32px rgba(59,130,246,0.18)); }}
        }}
        .welcome-title {{
            animation:textSlideUp 0.7s cubic-bezier(0.22,1,0.36,1) 0.35s forwards; opacity:0;
            font-family:'Inter',sans-serif; font-size:2.2rem; font-weight:800;
            color:#0f172a; letter-spacing:-0.03em; margin:24px 0 0; line-height:1.2;
        }}
        .welcome-subtitle {{
            animation:textSlideUp 0.7s cubic-bezier(0.22,1,0.36,1) 0.55s forwards; opacity:0;
            font-family:'Inter',sans-serif; font-size:1.05rem; font-weight:500; color:#64748b; margin:8px 0 0;
        }}
        .welcome-line {{
            animation:lineExpand 0.65s cubic-bezier(0.22,1,0.36,1) 0.75s forwards; opacity:0;
            width:0; height:3px; background:linear-gradient(90deg,#3b82f6,#60a5fa,#93c5fd);
            margin:20px auto; border-radius:2px;
        }}
        @keyframes lineExpand {{ from{{opacity:0;width:0}} to{{opacity:1;width:100px}} }}
        .welcome-hint {{
            animation:textSlideUp 0.7s cubic-bezier(0.22,1,0.36,1) 0.95s forwards; opacity:0;
            font-family:'Inter',sans-serif; font-size:0.88rem; color:#94a3b8; margin:8px 0 0;
        }}
        .welcome-credit {{
            animation:creditFloat 0.7s cubic-bezier(0.22,1,0.36,1) 1.2s forwards; opacity:0;
            margin-top:60px; padding-top:20px; border-top:1px solid #e5e7eb;
        }}
        .welcome-credit-label {{
            font-family:'Inter',sans-serif; font-size:0.65rem; color:#94a3b8;
            letter-spacing:0.05em; text-transform:uppercase; margin:0 0 4px;
        }}
        .welcome-credit-name {{
            font-family:'Inter',sans-serif; font-size:0.9rem; font-weight:700; color:#475569; margin:0;
        }}
        @keyframes textSlideUp {{
            from {{ opacity:0; transform:translateY(18px); filter:blur(3px); }}
            to   {{ opacity:1; transform:translateY(0);    filter:blur(0); }}
        }}
        @keyframes creditFloat {{
            from {{ opacity:0; transform:translateY(14px); }}
            to   {{ opacity:1; transform:translateY(0); }}
        }}
    </style>
    <div class="welcome-wrapper">
        <div class="welcome-logo">{logo_html}</div>
        <p class="welcome-title">UPTD PENGELOLAAN<br>PASAR KANDANGAN</p>
        <p class="welcome-subtitle">Kabupaten Hulu Sungai Selatan</p>
        <div class="welcome-line"></div>
        <p class="welcome-hint">Silakan pilih modul pada menu di sebelah kiri untuk memulai</p>
        <div class="welcome-credit">
            <p class="welcome-credit-label">Developed by</p>
            <p class="welcome-credit-name">M. Luthfi Renaldi</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 7. MAIN RUNNER
# ==========================================
def main():
    if "modul_aktif" not in st.session_state:
        st.session_state["modul_aktif"] = None
    if "menu_aktif" not in st.session_state:
        st.session_state["menu_aktif"] = None

    with st.sidebar:
        logo_b64 = st.session_state.get("logo_b64")
        if logo_b64:
            st.markdown(
                f'<div style="text-align:center; padding:18px 0 6px 0;">'
                f'<img src="data:image/png;base64,{logo_b64}" width="78" height="auto" '
                f'style="display:inline-block; filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4));"></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align:center;padding:18px 0 6px 0;">'
                '<div style="font-size:3rem;line-height:1;">🏛️</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("""
        <div style="text-align:center;padding:4px 0 14px 0;
                    border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:14px;">
            <p style="font-family:'Inter',sans-serif;font-size:1.05rem;font-weight:800;
                      color:#f1f5f9 !important;letter-spacing:-0.02em;margin:0 0 4px;line-height:1.3;">
                UPTD PASAR KANDANGAN</p>
            <p style="font-family:'Inter',sans-serif;font-size:0.78rem;font-weight:600;
                      color:#94a3b8 !important;letter-spacing:0.04em;margin:0;line-height:1.4;">
                KABUPATEN HULU SUNGAI SELATAN</p>
        </div>""", unsafe_allow_html=True)

        is_sk = st.session_state["modul_aktif"] == "SK TOKO"
        if st.button(
            "📋  SK TOKO  ▾" if is_sk else "📋  SK TOKO",
            key="btn_modul_sk",
            type="primary" if is_sk else "secondary",
            use_container_width=True,
        ):
            if is_sk:
                st.session_state["modul_aktif"] = None
                st.session_state["menu_aktif"]  = None
            else:
                st.session_state["modul_aktif"] = "SK TOKO"
                st.session_state["menu_aktif"]  = "PENGANTARAN"
            st.rerun()

        if is_sk:
            st.markdown('<div class="submenu-container">', unsafe_allow_html=True)
            for m in ["PENGANTARAN", "PENGAMBILAN"]:
                aktif = st.session_state["menu_aktif"] == m
                if st.button(
                    f"   ▹ {m}" if aktif else f"   ▸ {m}",
                    key=f"btn_sk_{m}",
                    type="primary" if aktif else "secondary",
                    use_container_width=True,
                ):
                    if not aktif:
                        st.session_state["menu_aktif"] = m
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        is_parkir = st.session_state["modul_aktif"] == "PARKIR"
        if st.button(
            "🅿️  PARKIR  ▾" if is_parkir else "🅿️  PARKIR",
            key="btn_modul_parkir",
            type="primary" if is_parkir else "secondary",
            use_container_width=True,
        ):
            if is_parkir:
                st.session_state["modul_aktif"] = None
                st.session_state["menu_aktif"]  = None
            else:
                st.session_state["modul_aktif"] = "PARKIR"
                st.session_state["menu_aktif"]  = "INPUT REKAP"
            st.rerun()

        if is_parkir:
            st.markdown('<div class="submenu-container">', unsafe_allow_html=True)
            for m in ["INPUT REKAP", "INPUT STOK", "KONFIRMASI"]:
                aktif = st.session_state["menu_aktif"] == m
                if st.button(
                    f"   ▹ {m}" if aktif else f"   ▸ {m}",
                    key=f"btn_parkir_{m}",
                    type="primary" if aktif else "secondary",
                    use_container_width=True,
                ):
                    if not aktif:
                        st.session_state["menu_aktif"] = m
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;padding:24px 0 8px;
                    border-top:1px solid rgba(255,255,255,0.06);margin-top:40px;">
            <p style="font-family:'Inter',sans-serif;font-size:0.56rem;
                      color:#64748b !important;margin:0;line-height:1.7;">Developed by</p>
            <p style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:700;
                      color:#94a3b8 !important;margin:2px 0 0;">M. Luthfi Renaldi</p>
        </div>""", unsafe_allow_html=True)

    modul = st.session_state["modul_aktif"]
    menu  = st.session_state["menu_aktif"]

    if modul is None:
        halaman_welcome()
    elif modul == "SK TOKO":
        if menu == "PENGANTARAN":
            halaman_pengantaran()
        else:
            halaman_pengambilan_sk()
    else:
        halaman_parkir(menu)


if __name__ == "__main__":
    main()
