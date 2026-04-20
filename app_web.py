import streamlit as st
import pandas as pd
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="🏪",
    layout="wide"
)
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# CUSTOM CSS - MODERN ELEGANT AESTHETIC
# ==========================================
st.markdown("""
<style>
    /* ===== FONT IMPORT - INTER (MODERN & CLEAN) ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ===== GLOBAL FONT OVERRIDE ===== */
    html, body, [class*="css"], .stApp,
    .stMarkdown, .stText, p, span, label, li, td, th,
    div, input, textarea, select, button,
    [data-testid="stMarkdownContainer"],
    [data-testid="stWidgetLabel"],
    .stSelectbox, .stMultiSelect, .stTextInput,
    .stNumberInput, .stRadio, .stCheckbox {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        letter-spacing: -0.01em;
    }

    /* ===== BACKGROUND ===== */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f0f4f8 50%, #e8eef5 100%);
    }

    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 40%, #0f172a 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        letter-spacing: -0.02em !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 6px 0 !important;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        color: #60a5fa !important;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em !important;
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] .stDivider {
        border-color: rgba(255,255,255,0.08) !important;
    }

    /* ===== HEADINGS ===== */
    h1 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.65rem !important;
        color: #0f172a !important;
        letter-spacing: -0.03em !important;
        line-height: 1.2 !important;
        margin-bottom: 0.4rem !important;
    }
    h2 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        color: #1e293b !important;
        letter-spacing: -0.025em !important;
        line-height: 1.3 !important;
    }
    h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        color: #334155 !important;
        letter-spacing: -0.02em !important;
    }

    /* ===== BODY TEXT & PARAGRAPHS ===== */
    p, .stMarkdown p {
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        line-height: 1.65 !important;
        color: #475569 !important;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
        transition: all 0.25s ease;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.07);
        transform: translateY(-1px);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em !important;
        color: #64748b !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }

    /* ===== INPUT FIELDS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        background: #ffffff !important;
        color: #1e293b !important;
        transition: all 0.2s ease;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    }
    .stTextInput label, .stNumberInput label,
    .stSelectbox label, .stCheckbox label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
        letter-spacing: 0.01em !important;
        margin-bottom: 4px !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1.5px solid #e2e8f0 !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 6px 16px rgba(37,99,235,0.35) !important;
    }
    .stDownloadButton > button {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(5,150,105,0.2) !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 16px rgba(5,150,105,0.3) !important;
        transform: translateY(-1px);
    }

    /* ===== FORM CONTAINER ===== */
    [data-testid="stForm"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 24px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        background: white !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 8px !important;
    }

    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    [data-testid="stDataFrame"] th {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        color: #475569 !important;
        background: #f8fafc !important;
    }
    [data-testid="stDataFrame"] td {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
        font-weight: 400 !important;
        color: #334155 !important;
    }

    /* ===== ALERTS ===== */
    .stAlert, [data-testid="stAlert"] {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        border-radius: 10px !important;
        border-left-width: 4px !important;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none !important;
        border-top: 1px solid #e2e8f0 !important;
        margin: 1.2rem 0 !important;
    }

    /* ===== CHECKBOX STYLING ===== */
    .stCheckbox {
        font-size: 0.84rem !important;
    }
    .stCheckbox label span {
        font-weight: 500 !important;
        color: #374151 !important;
    }

    /* ===== TABS (if used) ===== */
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

    /* ===== SMOOTH TRANSITIONS ===== */
    .main .block-container {
        animation: fadeIn 0.35s ease-out;
        max-width: 1100px;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header [data-testid="stStatusWidget"] {display: none;}
</style>
""", unsafe_allow_html=True)

def tombol_refresh_pojok(key_btn):
    """Fungsi khusus untuk tombol Refresh di pojok kanan atas"""
    if st.button("🔄 Refresh", key=key_btn, use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 2. FUNGSI HELPER (LOAD, SAVE, FORMAT)
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        
        # BERSILAT LIDAH DENGAN DATA GOOGLE SHEETS AGAR SUPER BERSIH
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip() # Babat habis spasi tersembunyi
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-") # Seragamkan semua data siluman jadi "-"

        if worksheet == "DATA_PARKIR" and not df.empty:
            if "Status_Cetak" not in df.columns:
                df["Status_Cetak"] = "BELUM"
                conn.update(worksheet=worksheet, data=df)
                st.cache_data.clear()
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns: return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except Exception: return 1

def safe_update(worksheet: str, data: pd.DataFrame) -> bool:
    try:
        conn.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")
        return False

def format_tgl_hari_indo(tgl_str):
    if not tgl_str or tgl_str in ["-", "nan", "NAN", ""]: return ""
    try:
        tgl_bersih = str(tgl_str).strip().replace('/', '-')
        if len(tgl_bersih.split('-')[-1]) == 2:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%y")
        else:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()

# ==========================================
# 3. FUNGSI PDF (SK TOKO & PARKIR)
# ==========================================

def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    UKURAN_KERTAS = (21.5 * cm, 33 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)
    M = 0.75 * cm; TINGGI_POTONG = 12 * cm; Y_POTONG = 33 * cm - TINGGI_POTONG
    Y_BASE = Y_POTONG + M; X_POS = M; LEBAR_BOX = 21.5 * cm - (2 * M); TINGGI_BOX = TINGGI_POTONG - (2 * M); TENGAH = 21.5 * cm / 2

    def gambar_garis_potong():
        c.setLineWidth(1); c.setDash(4, 4); c.line(0, Y_POTONG, 21.5 * cm, Y_POTONG)
        c.setFont("Helvetica-Oblique", 8); c.drawString(0.5 * cm, Y_POTONG + 0.15 * cm, "✂ --- Batas potong (Tinggi 12 cm) ---"); c.setDash()

    gambar_garis_potong(); c.setLineWidth(1.5); c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX) 
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm) 
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(TENGAH, Y_BASE + 9.3 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    c.setLineWidth(2); c.line(TENGAH - 5.5*cm, Y_BASE + 9.0*cm, TENGAH + 5.5*cm, Y_BASE + 9.0*cm)
    yy = Y_BASE + 8.0 * cm
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(SEMUA_BERKAS, 1):
        c.setFont("Helvetica-BoldOblique", 10); c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10); x_status = X_POS + 14 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        c.setLineWidth(1.5); y_strike = yy + 0.11 * cm 
        if item in berkas_list: c.line(x_status + 1.4 * cm, y_strike, x_status + 3.5 * cm, y_strike)
        else: c.line(x_status - 0.1 * cm, y_strike, x_status + 0.8 * cm, y_strike)
        yy -= 0.7 * cm
    c.setLineWidth(1.5); c.line(X_POS + 0.15 * cm, Y_BASE + 3.0 * cm, X_POS + LEBAR_BOX - 0.15 * cm, Y_BASE + 3.0 * cm) 
    c.line(TENGAH, Y_BASE + 0.15 * cm, TENGAH, Y_BASE + 3.0 * cm) 
    c.setFont("Helvetica-Bold", 9); c.drawCentredString(X_POS + 5 * cm, Y_BASE + 2.5 * cm, "PENGANTAR BERKAS"); c.drawCentredString(X_POS + 15 * cm, Y_BASE + 2.5 * cm, "PETUGAS PENERIMA")
    c.setFont("Helvetica-Bold", 11); c.drawCentredString(X_POS + 5 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Nama_Pengantar_Berkas', '')).upper()} )"); c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Penerima_Berkas', '')).upper()} )")
    c.showPage()
    gambar_garis_potong(); c.saveState(); c.setFillColorRGB(0.9, 0.9, 0.9); c.setFont("Helvetica-Bold", 35)
    c.translate(TENGAH, Y_BASE + (TINGGI_BOX / 2)); c.rotate(25); c.drawCentredString(0, 0, "UPTD PASAR KANDANGAN"); c.restoreState()
    c.setLineWidth(1.5); c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX); c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm)
    y_tab = Y_BASE + 10.35 * cm; TINGGI_B = 1.05 * cm
    DETAIL_ROWS = [("NOMOR URUT", data.get("No", "-")), ("TANGGAL TERIMA", format_tgl_hari_indo(data.get("Tanggal_Pengantaran", "-"))), ("TANGGAL PENGAMBILAN", format_tgl_hari_indo(data.get("Tanggal_Pengambilan", "-"))), ("NAMA & NOMOR TOKO", f"{data.get('Nama_Toko', '-')} - {data.get('No_Toko', '-')}"), ("NAMA PEMILIK (SK)", data.get("Nama_Pemilik_Asli", "-")), ("NAMA PENGANTAR", data.get("Nama_Pengantar_Berkas", "-"))]
    for label, val in DETAIL_ROWS:
        c.setLineWidth(1.5); c.rect(X_POS + 0.15 * cm, y_tab - TINGGI_B, 6.5 * cm, TINGGI_B); c.rect(X_POS + 6.65 * cm, y_tab - TINGGI_B, 13.2 * cm, TINGGI_B) 
        c.setFont("Helvetica-Bold", 9); c.drawString(X_POS + 0.4 * cm, y_tab - 0.7 * cm, label)
        c.setFont("Helvetica-Bold", 10); c.drawString(X_POS + 7.0 * cm, y_tab - 0.7 * cm, str(val).upper())
        y_tab -= TINGGI_B
    c.setFont("Helvetica-Bold", 10); c.drawString(X_POS + 0.6 * cm, Y_BASE + 2.8 * cm, "PERHATIAN:"); c.setFont("Helvetica", 9)
    c.drawString(X_POS + 0.6 * cm, Y_BASE + 2.2 * cm, "1. Simpan tanda terima ini sebagai syarat pengambilan SK asli."); c.drawString(X_POS + 0.6 * cm, Y_BASE + 1.6 * cm, "2. Pengambilan SK hanya dapat dilakukan di jam kerja UPTD.")
    c.save(); buffer.seek(0); return buffer

def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    lebar_box, tinggi_box = 6.8 * cm, 4.6 * cm
    x_awal = (lebar_kertas - lebar_box) / 2; center_x = lebar_kertas / 2; y_top = 32 * cm; y_bottom = y_top - tinggi_box
    c.setLineWidth(1.2); c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    y_gp = y_bottom - 1.0 * cm; c.setDash(1, 3); c.setLineWidth(0.5); c.line(0, y_gp, lebar_kertas, y_gp); c.setDash() 
    tgl_dis = format_tgl_hari_indo(data['Tanggal'])
    c.setFont("Helvetica-Bold", 7); c.drawCentredString(center_x, y_top - 0.5*cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6); c.drawCentredString(center_x, y_top - 0.9*cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.line(x_awal + 0.3*cm, y_top - 1.1*cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1*cm)
    c.setFont("Helvetica-Bold", 6); c.drawString(x_awal + 0.3*cm, y_top - 1.5*cm, f"TGL : {tgl_dis}"); c.drawString(x_awal + 0.3*cm, y_top - 1.9*cm, f"NAMA : {str(data['Nama_Petugas']).upper()}")
    y_tab, t_row = y_top - 2.2*cm, 0.6*cm; x_tab, l_tab = x_awal + 0.3*cm, lebar_box - 0.6*cm
    for i, (jns, jml) in enumerate([("RODA 2", data.get('MPP_Roda_R2', 0)), ("RODA 4", data.get('MPP_Roda_R4', 0))]):
        y_r = y_tab - ((i+1) * t_row); c.rect(x_tab, y_r, l_tab, t_row)
        c.setFont("Helvetica", 6); c.drawString(x_tab + 0.1*cm, y_r + 0.2*cm, jns); c.drawCentredString(center_x, y_r + 0.2*cm, f"{jml} LBR"); c.drawRightString(x_tab + l_tab - 0.1*cm, y_r + 0.2*cm, "MPP")
    c.showPage(); c.save(); buffer.seek(0); return buffer

def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm)); c.setFont("Helvetica-Bold", 10); X_POS = 0.75 * cm
    y_target = 21.5 * cm + 0.75 * cm + 10.35 * cm - (1.05 * cm * 2) - 0.7 * cm
    c.drawString(X_POS + 7.0 * cm, y_target, format_tgl_hari_indo(tgl_ambil).upper()); c.save(); buffer.seek(0); return buffer

# ==========================================
# 4. MODUL SK TOKO
# ==========================================
def halaman_pengantaran():
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.header("📝 INPUT PENGANTARAN BERKAS")
    with c_btn: tombol_refresh_pojok("ref_pengantaran")
    
    df_sk = load_data("DATA_SK")
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(df_sk) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    col_stat1.metric("📦 Total Berkas", total); col_stat2.metric("✅ Sudah Diambil", sudah_ambil); col_stat3.metric("⏳ Belum Diambil", total - sudah_ambil)
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    if "sel_berkas" not in st.session_state: st.session_state["sel_berkas"] = []
    st.subheader("☑️ Pilih Berkas yang Dibawa:"); cols_berkas = st.columns(3); sel_berkas = []
    for i, item in enumerate(SEMUA_BERKAS):
        with cols_berkas[i % 3]:
            if st.checkbox(item, key=f"cb_{item}"): sel_berkas.append(item)
    st.divider()
    with st.form("form_pengantaran", clear_on_submit=False):
        st.subheader("📋 Data Pengantaran")
        next_no = get_next_no(df_sk); col1, col2 = st.columns(2)
        with col1:
            no_urut = st.text_input("NOMOR URUT *", value=str(next_no))
            tgl_terima = st.text_input("TANGGAL TERIMA *", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = st.text_input("NAMA TOKO *").strip().upper(); no_toko = st.text_input("NOMOR TOKO *").strip().upper()
        with col2:
            nama_pemilik = st.text_input("NAMA PEMILIK SK *").strip().upper(); nama_pengantar = st.text_input("NAMA PENGANTAR *").strip().upper(); nama_penerima = st.text_input("NAMA PENERIMA *").strip().upper()
        if st.form_submit_button("💾 SIMPAN DATA", type="primary"):
            if not no_urut.strip() or not nama_toko or not nama_pemilik: st.error("❌ Data Wajib Diisi!")
            else:
                is_exist = not df_sk.empty and no_urut.strip() in df_sk["No"].str.strip().values
                new_row = {"No": no_urut.strip(), "Tanggal_Pengantaran": tgl_terima, "Tanggal_Pengambilan": "-", "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": nama_pemilik, "Nama_Pengantar_Berkas": nama_pengantar, "Penerima_Berkas": nama_penerima}
                if is_exist: st.session_state["pending_sk"] = new_row; st.session_state["show_confirm_sk"] = True
                else:
                    df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                    if safe_update("DATA_SK", df_baru): st.session_state["last_sk"] = new_row; st.session_state["last_berkas"] = sel_berkas; st.success("✅ Berhasil!"); st.rerun()
    if st.session_state.get("show_confirm_sk"):
        st.warning(f"⚠️ Nomor {no_urut} sudah ada!"); col_c1, col_c2 = st.columns(2)
        if col_c1.button("✅ YA, TIMPA DATA", type="primary"):
            d = st.session_state["pending_sk"]; df_sk = df_sk[df_sk["No"] != d["No"]]; df_final = pd.concat([df_sk, pd.DataFrame([d])], ignore_index=True)
            if safe_update("DATA_SK", df_final): st.session_state["last_sk"] = d; st.session_state["last_berkas"] = sel_berkas; st.session_state["show_confirm_sk"] = False; st.rerun()
        if col_c2.button("❌ BATAL"): st.session_state["show_confirm_sk"] = False; st.rerun()
    if "last_sk" in st.session_state:
        st.divider(); l = st.session_state["last_sk"]
        st.download_button("📥 DOWNLOAD PDF TANDA TERIMA", data=buat_pdf_full(l, st.session_state["last_berkas"]), file_name=f"TANDA_{l['No']}.pdf", mime="application/pdf")
    st.divider(); st.subheader("📊 DATA GOOGLE SHEETS")
    if not df_sk.empty:
        df_tampil = df_sk[df_sk["No"] != "-"].copy()
        st.dataframe(df_tampil.sort_values(by="No", ascending=False), use_container_width=True, hide_index=True)

def halaman_pengambilan_sk():
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.header("PENGAMBILAN BERKAS SK")
    with c_btn: tombol_refresh_pojok("ref_ambil")
    
    df_m = load_data("DATA_SK")
    if df_m.empty: return
    df_b = df_m[(df_m["Tanggal_Pengambilan"] == "-") & (df_m["No"] != "-")]
    no_cari = st.text_input("🔍 CARI NOMOR URUT:").strip()
    if no_cari:
        hasil = df_m[df_m["No"].str.strip() == no_cari]
        if not hasil.empty:
            data = hasil.iloc[0]; sudah = data["Tanggal_Pengambilan"] != "-"
            if sudah:
                st.success(f"✅ Sudah diambil pada: {format_tgl_hari_indo(data['Tanggal_Pengambilan'])}")
                st.download_button("🖨️ PRINT ULANG", data=cetak_overprint(data['Tanggal_Pengambilan']), file_name=f"AMBIL_{no_cari}.pdf")
            else:
                st.warning(f"🏪 Toko: {data['Nama_Toko']}"); tgl_a = st.text_input("📅 TANGGAL AMBIL:", value=datetime.now().strftime("%d-%m-%Y"))
                if st.button("✅ KONFIRMASI PENGAMBILAN"):
                    df_m.loc[df_m["No"].str.strip() == no_cari, "Tanggal_Pengambilan"] = tgl_a
                    if safe_update("DATA_SK", df_m): st.success("Berhasil!"); st.rerun()
        else: st.error("❌ Nomor Urut tidak terdaftar.")
    st.divider(); st.subheader(f"📊 BELUM DIAMBIL ({len(df_b)})"); st.dataframe(df_b.sort_values(by="No", ascending=True), use_container_width=True, hide_index=True)

# ==========================================
# 5. MODUL PARKIR
# ==========================================
def halaman_parkir(menu):
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.header(f"🚗 {menu}")
    with c_btn: tombol_refresh_pojok("ref_parkir")

    df_p = load_data("DATA_PARKIR")
    hari_ini = datetime.now().date()

    tgl_input_user = st.text_input("🔍 MASUKKAN TANGGAL", value=datetime.now().strftime("%d-%m-%Y"))
    try:
        tgl_bersih = str(tgl_input_user).strip().replace('/', '-')
        if len(tgl_bersih.split('-')[-1]) == 2: dt_user = datetime.strptime(tgl_bersih, "%d-%m-%y").date()
        else: dt_user = datetime.strptime(tgl_bersih, "%d-%m-%Y").date()
        df_p['Tgl_Temp'] = pd.to_datetime(df_p['Tanggal'], dayfirst=True, errors='coerce').dt.date
        baris = df_p[df_p['Tgl_Temp'] == dt_user]
    except: baris = pd.DataFrame()

    if baris.empty and menu != "KONFIRMASI":
        st.warning("⚠️ Tanggal belum ada di jadwal Sheet. Silakan isi jadwal dulu.")
        return

    if not baris.empty:
        idx = baris.index[0]; nama_p = baris.iloc[0]["Nama_Petugas"]
        
        df_petugas_sama = df_p[(df_p["Nama_Petugas"] == nama_p) & (df_p.index < idx)]
        if not df_petugas_sama.empty:
            idx_terakhir_petugas = df_petugas_sama.index[-1]
            sisa_r2 = pd.to_numeric(df_petugas_sama.loc[idx_terakhir_petugas].get("Sisa_Stok_R2", 0), errors='coerce')
            sisa_r4 = pd.to_numeric(df_petugas_sama.loc[idx_terakhir_petugas].get("Sisa_Stok_R4", 0), errors='coerce')
        else:
            sisa_r2 = 0; sisa_r4 = 0

        sisa_r2 = 0 if pd.isna(sisa_r2) else sisa_r2
        sisa_r4 = 0 if pd.isna(sisa_r4) else sisa_r4

    if menu == "INPUT REKAP":
        st.success(f"👤 PETUGAS: **{nama_p}** | 📅 **{format_tgl_hari_indo(tgl_input_user)}**")
        col_s1, col_s2 = st.columns(2)
        col_s1.metric(f"📊 Sisa Karcis R2 ({nama_p})", int(sisa_r2))
        col_s2.metric(f"📊 Sisa Karcis R4 ({nama_p})", int(sisa_r4))

        with st.form("form_rekap_harian", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1: 
                tr2 = st.number_input("TOTAL TERJUAL R2", min_value=0)
                mr2 = st.number_input("MPP RODA R2", min_value=0)
            with c2: 
                tr4 = st.number_input("TOTAL TERJUAL R4", min_value=0)
                mr4 = st.number_input("MPP RODA R4", min_value=0)
            
            cb1, cb2 = st.columns(2)
            with cb1: subm = st.form_submit_button("💾 SIMPAN REKAP", type="primary", use_container_width=True)
            with cb2: reset = st.form_submit_button("🔄 RESET FORM", use_container_width=True)
            
            if reset: st.rerun()

            if subm:
                pk2_lama = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R2"], errors='coerce')
                pk4_lama = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R4"], errors='coerce')
                pk2_lama = 0 if pd.isna(pk2_lama) else pk2_lama
                pk4_lama = 0 if pd.isna(pk4_lama) else pk4_lama

                sn2 = (pk2_lama + sisa_r2) - tr2
                sn4 = (pk4_lama + sisa_r4) - tr4
                
                tr2_str = str(tr2) if tr2 > 0 else "0"
                tr4_str = str(tr4) if tr4 > 0 else "0"

                # --- CEK APAKAH DATA SUDAH PERNAH DIISI ---
                karcis_r2_sekarang = str(df_p.loc[idx, "Total_Karcis_R2"]).strip()
                sudah_diisi = karcis_r2_sekarang not in ["-", "nan", ""]

                data_baru = {
                    "tr2_str": tr2_str, "mr2_str": str(mr2), "sn2_str": str(sn2), "kh2_str": str(tr2-mr2),
                    "tr4_str": tr4_str, "mr4_str": str(mr4), "sn4_str": str(sn4), "kh4_str": str(tr4-mr4)
                }

                if sudah_diisi:
                    # Tahan proses dan munculkan peringatan
                    st.session_state["pending_parkir"] = data_baru
                    st.session_state["pending_idx"] = idx
                    st.session_state["show_confirm_parkir"] = True
                else:
                    # Proses langsung simpan
                    df_p.loc[idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [data_baru["tr2_str"], data_baru["mr2_str"], data_baru["sn2_str"], data_baru["kh2_str"]]
                    df_p.loc[idx, ["Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [data_baru["tr4_str"], data_baru["mr4_str"], data_baru["sn4_str"], data_baru["kh4_str"]]
                    df_p.loc[idx, ["Status_Khusus", "Status_MPP", "Status_Cetak"]] = ["BELUM", "BELUM", "BELUM"]
                    
                    if 'Tgl_Temp' in df_p.columns: df_p = df_p.drop(columns=['Tgl_Temp'])
                    if safe_update("DATA_PARKIR", df_p): st.success("✅ Berhasil Diupdate!"); st.rerun()

        # --- BLOK PERINGATAN TIMPA DATA (Muncul di bawah form) ---
        if st.session_state.get("show_confirm_parkir"):
            st.warning(f"⚠️ Data setoran untuk tanggal **{tgl_input_user}** sudah pernah diisi! Yakin ingin menimpanya?")
            col_c1, col_c2 = st.columns(2)
            if col_c1.button("✅ YA, TIMPA DATA", type="primary", key="btn_timpa_parkir"):
                d = st.session_state["pending_parkir"]
                p_idx = st.session_state["pending_idx"]
                
                df_p.loc[p_idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [d["tr2_str"], d["mr2_str"], d["sn2_str"], d["kh2_str"]]
                df_p.loc[p_idx, ["Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [d["tr4_str"], d["mr4_str"], d["sn4_str"], d["kh4_str"]]
                
                # Reset status konfirmasi jika ditimpa
                if str(df_p.loc[p_idx, "Status_Cetak"]).strip() != "SUDAH":
                    df_p.loc[p_idx, ["Status_Khusus", "Status_MPP", "Status_Cetak"]] = ["BELUM", "BELUM", "BELUM"]
                
                if 'Tgl_Temp' in df_p.columns: df_p = df_p.drop(columns=['Tgl_Temp'])
                if safe_update("DATA_PARKIR", df_p): 
                    st.session_state["show_confirm_parkir"] = False
                    st.success("✅ Berhasil Ditimpa!")
                    st.rerun()
            
            if col_c2.button("❌ BATAL", key="btn_batal_parkir"):
                st.session_state["show_confirm_parkir"] = False
                st.rerun()

    elif menu == "INPUT STOK":
        st.subheader("📦 UPDATE PENGAMBILAN KARCIS BARU")
        st.info(f"Mengisi stok baru untuk petugas: **{nama_p}**")
        with st.form("form_stok_baru", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1: pk2 = st.number_input("PENGAMBILAN BARU R2", min_value=0)
            with c2: pk4 = st.number_input("PENGAMBILAN BARU R4", min_value=0)
            
            # --- PENAMBAHAN TOMBOL RESET DI SINI ---
            cb1, cb2 = st.columns(2)
            with cb1: 
                subm_stok = st.form_submit_button("➕ TAMBAH STOK", type="primary", use_container_width=True)
            with cb2: 
                reset_stok = st.form_submit_button("🔄 RESET FORM", use_container_width=True)
            
            if reset_stok:
                st.rerun()

            if subm_stok:
                df_p.loc[idx, ["Pengambilan_Karcis_R2", "Pengambilan_Karcis_R4"]] = [str(pk2), str(pk4)]
                if 'Tgl_Temp' in df_p.columns: df_p = df_p.drop(columns=['Tgl_Temp'])
                if safe_update("DATA_PARKIR", df_p): st.success("✅ Stok Berhasil Ditambahkan!"); st.rerun()

    elif menu == "KONFIRMASI":
        # FILTER ANTI HANTU: Hanya tampilkan jika Total Karcis terdeteksi sebagai ANGKA
        kondisi_angka_r2 = df_p["Total_Karcis_R2"].str.isnumeric()
        kondisi_angka_r4 = df_p["Total_Karcis_R4"].str.isnumeric()
        df_pen = df_p[kondisi_angka_r2 | kondisi_angka_r4].copy()
        
        if df_pen.empty: 
            st.info("TIDAK ADA DATA KONFIRMASI.")
        else:
            df_pen['Tgl_Temp'] = pd.to_datetime(df_pen['Tanggal'], dayfirst=True, errors='coerce').dt.date
            
            df_terfilter = df_pen[
                (df_pen["Status_Khusus"] != "SUDAH") |
                (df_pen["Status_MPP"] != "SUDAH") |
                (df_pen["Status_Cetak"] != "SUDAH") |
                (df_pen['Tgl_Temp'] == hari_ini)
            ].copy()

            if df_terfilter.empty:
                st.info("TIDAK ADA DATA KONFIRMASI (Semua data lama sudah Lunas).")
            else:
                df_terfilter = df_terfilter.sort_index(ascending=False).head(10)
                
                for i, row in df_terfilter.iterrows():
                    stat_k = str(row.get("Status_Khusus", "BELUM")).strip()
                    stat_m = str(row.get("Status_MPP", "BELUM")).strip()
                    stat_c = str(row.get("Status_Cetak", "BELUM")).strip()
                    
                    lunas = (stat_k == "SUDAH") and (stat_m == "SUDAH") and (stat_c == "SUDAH")
                    ikon = "✅ [SELESAI]" if lunas else "📦 [BELUM SELESAI]"
                    
                    with st.expander(f"{ikon} {row['Tanggal']} - {row['Nama_Petugas']}", expanded=not lunas):
                        if lunas:
                            st.success("✨ PROSES SELESAI: Data ini akan otomatis hilang besok.")
                            
                        ck, cm = st.columns(2)
                        with ck:
                            st.write(f"**KHUSUS**\nR2: {row['Khusus_Roda_R2']} | R4: {row['Khusus_Roda_R4']}")
                            if stat_k != "SUDAH":
                                if st.button("TERIMA KHUSUS", key=f"k{i}", use_container_width=True):
                                    df_p.loc[i, "Status_Khusus"] = "SUDAH"
                                    safe_update("DATA_PARKIR", df_p); st.rerun()
                            else: 
                                st.success("✅ Khusus Diterima")
                        
                        with cm:
                            st.write(f"**MPP**\nR2: {row['MPP_Roda_R2']} | R4: {row['MPP_Roda_R4']}")
                            if stat_m != "SUDAH":
                                if st.button("TERIMA MPP", key=f"m{i}", type="primary", use_container_width=True):
                                    df_p.loc[i, "Status_MPP"] = "SUDAH"
                                    safe_update("DATA_PARKIR", df_p); st.rerun()
                            else: 
                                st.download_button("🖨️ CETAK PDF MPP", data=cetak_tanda_terima_parkir(row), file_name=f"MPP_{row['Tanggal']}.pdf", key=f"p{i}", use_container_width=True)
                                if stat_c != "SUDAH":
                                    if st.button("✅ SUDAH CETAK", key=f"c{i}", use_container_width=True):
                                        df_p.loc[i, "Status_Cetak"] = "SUDAH"
                                        safe_update("DATA_PARKIR", df_p); st.rerun()
                                else:
                                    st.success("✅ Telah Dicetak")
                                    
    st.divider(); st.subheader("📊 LOG DATA TERAKHIR")
    if 'Tgl_Temp' in df_p.columns: df_p = df_p.drop(columns=['Tgl_Temp'])
    st.dataframe(df_p.sort_values(by="Tanggal", ascending=False).head(15), hide_index=True)

# ==========================================
# 6. MAIN RUNNER
# ==========================================
def main():
    with st.sidebar:
        # ===== LOGO KABUPATEN HSS =====
        st.markdown("""
        <div style="text-align:center; padding: 16px 0 8px 0;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Lambang_Kabupaten_Hulu_Sungai_Selatan.png/220px-Lambang_Kabupaten_Hulu_Sungai_Selatan.png" 
                 width="80" style="filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3)); margin-bottom: 8px;">
            <p style="font-size: 0.65rem; font-weight: 600; color: #94a3b8 !important; 
                      letter-spacing: 0.08em; text-transform: uppercase; margin: 0; line-height: 1.4;">
                Kabupaten<br>Hulu Sungai Selatan
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align:center; padding: 4px 0 12px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px;">
            <h2 style="font-size: 1.05rem !important; font-weight: 800 !important; 
                       color: #f1f5f9 !important; letter-spacing: -0.02em; margin: 0;
                       line-height: 1.3;">
                🏪 UPTD PASAR<br>KANDANGAN
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        modul = st.selectbox("PILIH MODUL:", ["SK TOKO", "PARKIR"], key="pilih_modul")
        
        st.divider()
        if modul == "SK TOKO": 
            menu = st.radio("MENU SK:", ["PENGANTARAN", "PENGAMBILAN"], key="pilih_menu_sk")
        else: 
            menu = st.radio("MENU PARKIR:", ["INPUT REKAP", "INPUT STOK", "KONFIRMASI"], key="pilih_menu_parkir")
        
        # ===== FOOTER SIDEBAR =====
        st.markdown("""
        <div style="position: fixed; bottom: 12px; left: 12px; right: 12px; text-align: center;">
            <p style="font-size: 0.6rem; color: #475569 !important; margin: 0; 
                      letter-spacing: 0.03em; line-height: 1.5;">
                © 2025 UPTD Pengelolaan Pasar<br>Kab. Hulu Sungai Selatan
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    if modul == "SK TOKO":
        if menu == "PENGANTARAN": halaman_pengantaran()
        else: halaman_pengambilan_sk()
    else: halaman_parkir(menu)

if __name__ == "__main__":
    main()
