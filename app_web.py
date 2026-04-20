import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. FUNGSI KHUSUS CETAK PARKIR (PORTRAIT)
# ==========================================
def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    # UKURAN F4 PORTRAIT (21.5cm x 33cm)
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    
    # PENGATURAN DIMENSI MIKRO
    lebar_box = 6.8 * cm
    tinggi_box = 4.6 * cm
    
    # HITUNG POSISI TENGAH (CENTER)
    # Titik X agar box berada di tengah kertas
    x_awal = (lebar_kertas - lebar_box) / 2
    center_x = lebar_kertas / 2
    
    # POSISI VERTIKAL (Margin atas 1cm)
    y_top = 32 * cm 
    y_bottom = y_top - tinggi_box
    
    # 1. BINGKAI LUAR BOX (TENGAH)
    c.setLineWidth(1.2)
    c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    
    # 2. GARIS POTONG DI BAWAH BOX (PUTUS-PUTUS FULL LEBAR)
    y_garis_potong = y_bottom - 1.0 * cm
    c.setDash(1, 3)
    c.setLineWidth(0.5)
    c.line(0, y_garis_potong, lebar_kertas, y_garis_potong)
    c.setDash() 
    
    # 3. LOGIKA OTOMATIS TANGGAL
    tgl_input = data['Tanggal'].replace('/', '-')
    try:
        if len(tgl_input.split('-')[-1]) == 2:
            tgl_obj = datetime.strptime(tgl_input, "%d-%m-%y")
        else:
            tgl_obj = datetime.strptime(tgl_input, "%d-%m-%Y")
            
        hari_indo = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
        nama_hari = hari_indo[tgl_obj.weekday()]
        tgl_final = f"{nama_hari}, {tgl_obj.strftime('%d - %m - %Y')}"
    except:
        tgl_final = data['Tanggal'].upper()

    # 4. HEADER (DI TENGAH BOX)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(center_x, y_top - 0.5 * cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(center_x, y_top - 0.9 * cm, "TANDA TERIMA KARCIS PARKIR (MPP)")
    
    c.setLineWidth(0.8)
    c.line(x_awal + 0.3*cm, y_top - 1.1 * cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1 * cm)
    
    # 5. DATA IDENTITAS
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_awal + 0.3*cm, y_top - 1.5 * cm, f"TGL : {tgl_final}")
    c.drawString(x_awal + 0.3*cm, y_top - 1.9 * cm, f"NAMA : {data['Nama_Petugas'].upper()}")

    # 6. TABEL DATA MINI
    y_tab = y_top - 2.2 * cm
    t_row = 0.6 * cm
    lebar_tabel_mini = lebar_box - 0.6 * cm
    x_tab = x_awal + 0.3 * cm
    
    # Header Tabel
    c.rect(x_tab, y_tab - t_row, lebar_tabel_mini, t_row)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(x_tab + 0.1*cm, y_tab - 0.4*cm, "JENIS")
    c.drawCentredString(center_x, y_tab - 0.4*cm, "JUMLAH")
    c.drawRightString(x_tab + lebar_tabel_mini - 0.1*cm, y_tab - 0.4*cm, "KET")
    
    # Baris RODA 2
    y_r2 = y_tab - (2 * t_row)
    c.rect(x_tab, y_r2, lebar_tabel_mini, t_row)
    c.setFont("Helvetica", 6)
    c.drawString(x_tab + 0.1*cm, y_r2 + 0.2*cm, "RODA 2")
    c.drawCentredString(center_x, y_r2 + 0.2*cm, f"{data['MPP_Roda_R2']} LBR")
    c.drawRightString(x_tab + lebar_tabel_mini - 0.1*cm, y_r2 + 0.2*cm, "MPP")

    # Baris RODA 4
    y_r4 = y_tab - (3 * t_row)
    c.rect(x_tab, y_r4, lebar_tabel_mini, t_row)
    c.drawString(x_tab + 0.1*cm, y_r4 + 0.2*cm, "RODA 4")
    c.drawCentredString(center_x, y_r4 + 0.2*cm, f"{data['MPP_Roda_R4']} LBR")
    c.drawRightString(x_tab + lebar_tabel_mini - 0.1*cm, y_r4 + 0.2*cm, "MPP")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

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
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        # FIX PENCARIAN: Hapus .0 agar nomor 1 tetap 1, bukan 1.0
        df = df.astype(str).replace(r'\.0$', '', regex=True).replace("nan", "-").replace("None", "-")
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns:
            return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except Exception:
        return 1

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
        dt = datetime.strptime(str(tgl_str).strip(), "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()

# ==========================================
# 3. FUNGSI PDF (F4 PORTRAIT + MENTOK)
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    UKURAN_KERTAS = (21.5 * cm, 33 * cm) # Kertas F4 Standar
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

    # HALAMAN 1 - DEPAN
    gambar_garis_potong()
    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX) 
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm) 
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(TENGAH, Y_BASE + 9.3 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    c.setLineWidth(2); c.line(TENGAH - 5.5*cm, Y_BASE + 9.0*cm, TENGAH + 5.5*cm, Y_BASE + 9.0*cm)

    yy = Y_BASE + 8.0 * cm
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(SEMUA_BERKAS, 1):
        c.setFont("Helvetica-BoldOblique", 10); c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10); x_status = X_POS + 14 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        c.setLineWidth(1.5); y_strike = yy + 0.11 * cm 
        if item in berkas_list:
            c.line(x_status + 1.4 * cm, y_strike, x_status + 3.5 * cm, y_strike)
        else:
            c.line(x_status - 0.1 * cm, y_strike, x_status + 0.8 * cm, y_strike)
        yy -= 0.7 * cm

    c.setLineWidth(1.5); c.line(X_POS + 0.15 * cm, Y_BASE + 3.0 * cm, X_POS + LEBAR_BOX - 0.15 * cm, Y_BASE + 3.0 * cm) 
    c.line(TENGAH, Y_BASE + 0.15 * cm, TENGAH, Y_BASE + 3.0 * cm) 
    c.setFont("Helvetica-Bold", 9); c.drawCentredString(X_POS + 5 * cm, Y_BASE + 2.5 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 2.5 * cm, "PETUGAS PENERIMA")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(X_POS + 5 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Nama_Pengantar_Berkas', '')).upper()} )")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Penerima_Berkas', '')).upper()} )")
    c.showPage()

    # HALAMAN 2 - BELAKANG
    gambar_garis_potong()

    # --- KODE WATERMARK TIPIS ---
    c.saveState
