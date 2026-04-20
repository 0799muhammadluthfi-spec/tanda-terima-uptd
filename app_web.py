import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="🏪",
    layout="wide"
)

conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI HELPER
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    """Load data dari Google Sheets dengan error handling."""
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        # FIX PENCARIAN 1.0 -> 1 
        df = df.astype(str).replace(r'\.0$', '', regex=True).replace("nan", "-").replace("None", "-")
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    """Hitung nomor urut berikutnya."""
    try:
        if df.empty or col not in df.columns:
            return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except Exception:
        return 1

def safe_update(worksheet: str, data: pd.DataFrame) -> bool:
    """Update Google Sheets dengan error handling."""
    try:
        conn.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")
        return False

# ==========================================
# 3. FUNGSI PDF (VERSI F4 PORTRAIT - CETAK DI ATAS)
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    # KERTAS FULL F4 PORTRAIT (21.5 cm x 33 cm)
    # Printer setting harus PORTRAIT (Berdiri) & Kertas F4/Folio
    UKURAN_KERTAS = (21.5 * cm, 33 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)
    
    # Koordinat ditaruh di paling atas kertas
    Y_BASE = 21.5 * cm # Jarak dari bawah kertas, menyisakan ruang 11.5cm di atas
    X_POS = 0.75 * cm 
    LEBAR = 21.5 * cm
    TENGAH = LEBAR / 2

    # ------------------------------------------
    # HALAMAN 1 - DEPAN
    # ------------------------------------------
    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, 20 * cm, 10 * cm) # Bingkai Luar
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, 19.7 * cm, 9.7 * cm) # Bingkai Dalam

    # Judul
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(TENGAH, Y_BASE + 8.8 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    
    # Garis Judul (Ketebalan 2)
    c.setLineWidth(2)
    c.line(TENGAH - 5.5*cm, Y_BASE + 8.5*cm, TENGAH + 5.5*cm, Y_BASE + 8.5*cm)

    # Checklist Berkas
    yy = Y_BASE + 7.5 * cm
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    
    for i, item in enumerate(SEMUA_BERKAS, 1):
        c.setFont("Helvetica-BoldOblique", 10)
        c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")
        
        c.setFont("Helvetica-Bold", 10)
        x_status = X_POS + 14 * cm
        c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        
        # Coretan (Ketebalan 1.5) & Panjang disesuaikan
        c.setLineWidth(1.5)
        y_strike = yy + 0.11 * cm 
        if item in berkas_list:
            # Coret TIDAK ADA (Panjang sudah diperpendek)
            c.line(x_status + 1.6 * cm, y_strike, x_status + 3.1 * cm, y_strike)
        else:
            # Coret ADA
            c.line(x_status - 0.1 * cm, y_strike, x_status + 0.8 * cm, y_strike)
        yy -= 0.7 * cm

    # Garis Tanda Tangan (Ketebalan 1.5)
    c.setLineWidth(1.5)
    c.line(X_POS + 0.15 * cm, Y_BASE + 3.0 * cm, X_POS + 19.85 * cm, Y_BASE + 3.0 * cm) 
    c.line(TENGAH, Y_BASE + 0.15 * cm, TENGAH, Y_BASE + 3.0 * cm) 

    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(X_POS + 5 * cm, Y_BASE + 2.5 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 2.5 * cm, "PETUGAS PENERIMA")

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(X_POS + 5 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Nama_Pengantar_Berkas', '')).upper()} )")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Penerima_Berkas', '')).upper()} )")

    c.showPage()

    # ------------------------------------------
    # HALAMAN 2 - BELAKANG
    # ------------------------------------------
    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, 20 * cm, 10 * cm)
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, 19.7 * cm, 9.7 * cm)

    # Memulai tabel PERSIS dari garis kotak dalam bagian atas, agar tidak ada sisa kolom
    y_tab = Y_BASE + 9.85 * cm 
    TINGGI_B = 1.15 * cm
    
    tgl_ambil_pdf = data.get("Tanggal_Pengambilan", "-")
    if tgl_ambil_pdf in ["-", "nan", "NAN", ""]:
        tgl_ambil_pdf = ""

    DETAIL_ROWS = [
        ("NOMOR", data.get("No", "-")),
        ("TGL TERIMA", data.get("Tanggal_Pengantaran", "-")),
        ("TGL AMBIL", tgl_ambil_pdf),
        ("NAMA & NO. TOKO", f"{data.get('Nama_Toko', '-')} - {data.get('No_Toko', '-')}"),
        ("PEMILIK (SK)", data.get("Nama_Pemilik_Asli", "-"))
    ]

    for label, val in DETAIL_ROWS:
        c.setLineWidth(1.5) 
        c.rect(X_POS + 0.15 * cm, y_tab - TINGGI_B, 6 * cm, TINGGI_B)
        c.rect(X_POS + 6.15 * cm, y_tab - TINGGI_B, 13.55 * cm, TINGGI_B)
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(X_POS + 0.5 * cm, y_tab - 0.7 * cm, label)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(X_POS + 6.5 * cm, y_tab - 0.7 * cm, str(val).upper())
        y_tab -= TINGGI_B

    # Teks Perhatian Baru
    c.setFont("Helvetica-Bold", 10)
    c.drawString(X_POS + 0.6 * cm, Y_BASE + 2.8 * cm, "PERHATIAN:")
    c.setFont("Helvetica", 9)
    c.drawString(X_POS + 0.6 * cm, Y_BASE + 2.2 * cm, "1. Simpan tanda terima ini sebagai syarat pengambilan SK asli.")
    c.drawString(X_POS + 0.6 * cm, Y_BASE + 1.6 * cm, "2. Pengambilan SK hanya dapat dilakukan di jam kerja UPTD.")

    c.save()
    buffer.seek(0)
    return buffer

def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO()
    # Overprint juga disesuaikan dengan F4 Portrait
    c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm))
    c.setFont("Helvetica-Bold", 10)
    
    Y_BASE = 21.5 * cm
    X_POS = 0.75 * cm
    # Koordinat presisi di dalam kotak TGL AMBIL
    y_target = Y_BASE + 6.8 * cm 
    c.drawString(X_POS + 6.5 * cm, y_target, tgl_ambil.upper())
    
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 4. MODUL SK TOKO - PENGANTARAN
# ==========================================
def halaman_pengantaran():
    st.header("📝 INPUT PENGANTARAN BERKAS")

    df_sk = load_data("DATA_SK")

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(df_sk) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    belum_ambil = total - sudah_ambil

    col_stat1.metric("📦 Total Berkas", total)
    col_stat2.metric("✅ Sudah Diambil", sudah_ambil)
    col_stat3.metric("⏳ Belum Diambil", belum_ambil)

    st.divider()

    SEMUA_BERKAS = [
        "SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", 
        "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"
    ]

    if "sel_berkas" not in st.session_state:
        st.session_state["sel_berkas"] = []

    st.subheader("☑️ Pilih Berkas yang Dibawa:")
    cols_berkas = st.columns(3)
    sel_berkas = []
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
            no_urut = st.text_input("NO. URUT *", value=str(next_no), help="Nomor urut otomatis")
            tgl_terima = st.text_input("TANGGAL TERIMA *", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = st.text_input("NAMA TOKO *").strip().upper()
            no_toko = st.text_input("NOMOR TOKO *").strip().upper()

        with col2:
            nama_pemilik = st.text_input("NAMA PEMILIK SK *").strip().upper()
            nama_pengantar = st.text_input("NAMA PENGANTAR *").strip().upper()
            nama_penerima = st.text_input("NAMA PENERIMA *").strip().upper()

        submitted = st.form_submit_button("💾 SIMPAN DATA", type="primary")

        if submitted:
            errors = []
            if not no_urut.strip(): errors.append("No. Urut wajib diisi")
            if not nama_toko: errors.append("Nama Toko wajib diisi")
            if not nama_pemilik: errors.append("Nama Pemilik wajib diisi")

            if not df_sk.empty and no_urut.strip() in df_sk["No"].str.strip().values:
                errors.append(f"No. Urut {no_urut} sudah ada!")

            if errors:
                for err in errors: st.error(f"❌ {err}")
            else:
                new_row = {
                    "No": no_urut.strip(), "Tanggal_Pengantaran":
