import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME (VITE STYLE)
# ==========================================
st.set_page_config(
    page_title="UPTD Pasar Kandangan",
    page_icon="🏪",
    layout="wide"
)

# CSS CUSTOM UNTUK MENIRU INTERFACE REACT
st.markdown("""
    <style>
    /* Latar Belakang Utama */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1e3a5f;
        border-right: 1px solid #d0d7e2;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Card Container */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #d0d7e2;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }

    /* Typography */
    h1, h2, h3 {
        color: #1e3a5f !important;
        font-weight: 700 !important;
    }
    p {
        color: #64748b;
    }

    /* Button Styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* Animasi Pindah Menu */
    .main .block-container {
        animation: fadeIn 0.5s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI HELPER
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip()
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

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
        dt = datetime.strptime(tgl_bersih, "%d-%m-%y") if len(tgl_bersih.split('-')[-1]) == 2 else datetime.strptime(tgl_bersih, "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except: return str(tgl_str).upper()

# ==========================================
# 3. FUNGSI PDF (SK & PARKIR)
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    UKURAN_KERTAS = (21.5 * cm, 33 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)
    M = 0.75 * cm; TINGGI_POTONG = 12 * cm; Y_POTONG = 33 * cm - TINGGI_POTONG
    Y_BASE = Y_POTONG + M; X_POS = M; LEBAR_BOX = 21.5 * cm - (2 * M); TINGGI_BOX = TINGGI_POTONG - (2 * M); TENGAH = 21.5 * cm / 2
    c.setLineWidth(1.5); c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX) 
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm) 
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(TENGAH, Y_BASE + 9.3 * cm, "TANDA TERIMA BERKAS TOKO")
    c.setFont("Helvetica-Bold", 10); c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Penerima_Berkas', '')).upper()} )")
    c.save(); buffer.seek(0); return buffer

def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm))
    c.setFont("Helvetica-Bold", 7); c.drawCentredString(10.75 * cm, 31.5 * cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.save(); buffer.seek(0); return buffer

# ==========================================
# 4. MODUL SK TOKO
# ==========================================
def halaman_sk(menu):
    st.title(f"{'📦' if menu == 'PENGANTARAN' else '📤'} {menu}")
    df_sk = load_data("DATA_SK")
    
    with st.container():
        if menu == "PENGANTARAN":
            with st.form("form_sk"):
                c1, c2 = st.columns(2)
                with c1:
                    no_urut = st.text_input("NOMOR URUT")
                    nama_toko = st.text_input("NAMA TOKO")
                with c2:
                    pemilik = st.text_input("NAMA PEMILIK SK")
                    penerima = st.text_input("PENERIMA")
                if st.form_submit_button("💾 SIMPAN DATA", type="primary"):
                    st.success("Data berhasil diproses (Mode Tampilan Baru)")
        else:
            st.write("Silakan cari nomor urut berkas yang akan diambil.")
            st.text_input("🔍 Cari Nomor Urut...")

    st.subheader("📊 Data Terbaru")
    st.dataframe(df_sk.head(10), use_container_width=True, hide_index=True)

# ==========================================
# 5. MODUL PARKIR
# ==========================================
def halaman_parkir(menu):
    st.title(f"🚗 PARKIR - {menu}")
    df_p = load_data("DATA_PARKIR")

    if menu == "KONFIRMASI":
        # Tampilan List seperti Framer Motion
        st.info("Menampilkan 10 antrian setoran terakhir.")
        for i in range(3):
            with st.expander(f"📦 [BELUM SELESAI] - Petugas: Anshar - 20/04/2026"):
                st.write("Klik tombol di bawah jika dana sudah diterima.")
                st.button(f"Konfirmasi Setoran {i}", key=f"btn_{i}")
    else:
        with st.container():
            st.date_input("Pilih Tanggal")
            st.button("Tampilkan Form", type="primary")

# ==========================================
# 6. MAIN RUNNER (DESAIN SIDEBAR VITE)
# ==========================================
def main():
    # Logo & Nama di Sidebar
    st.sidebar.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: white; font-size: 1.2rem; margin-bottom: 0;">UPTD PASAR</h1>
            <p style="color: #94a3b8; font-size: 0.8rem;">Hulu Sungai Selatan</p>
        </div>
        <hr style="border-color: #334155;">
    """, unsafe_allow_html=True)

    with st.sidebar:
        modul = st.selectbox("PILIH MODUL:", ["SK TOKO", "PARKIR"], key="pilih_modul")
        st.divider()
        if modul == "SK TOKO":
            menu = st.radio("MENU SK:", ["PENGANTARAN", "PENGAMBILAN"], key="sk_sub")
        else:
            menu = st.radio("MENU PARKIR:", ["INPUT REKAP", "INPUT STOK", "KONFIRMASI"], key="parkir_sub")

    # Tombol Refresh Pojok Kanan Atas
    cols = st.columns([0.9, 0.1])
    if cols[1].button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

    if modul == "SK TOKO":
        halaman_sk(menu)
    else:
        halaman_parkir(menu)

if __name__ == "__main__":
    main()
