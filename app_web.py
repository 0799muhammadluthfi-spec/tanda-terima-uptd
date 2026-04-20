import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import time

# ==========================================
# 1. KONFIGURASI & KONEKSI (Paling Atas)
# ==========================================
st.set_page_config(page_title="UPTD PASAR KANDANGAN", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI PEMBUAT PDF (UKURAN 22 x 11 CM)
# ==========================================
def buat_pdf_full(data, berkas_list):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 11 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    x_pos, y_pos = 1 * cm, 1 * cm
    lebar_kertas = 22 * cm
    
    # HALAMAN 1 (DEPAN)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    c.setFont("Helvetica-Bold", 14); c.drawCentredString(lebar_kertas/2, y_pos + 8.1 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    
    # Checkbox Dokumen
    yy = y_pos + 6.3 * cm
    items = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(items, 1):
        c.setFont("Helvetica-BoldOblique", 10.5); c.drawString(x_pos + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 11); x_status = x_pos + 15.2 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        if item in berkas_list: 
            c.line(x_status + 1.5 * cm, yy + 0.12 * cm, x_status + 3.8 * cm, yy + 0.12 * cm)
        else: 
            c.line(x_status - 0.1 * cm, yy + 0.12 * cm, x_status + 0.9 * cm, yy + 0.12 * cm)
        yy -= 0.65 * cm
        
    c.setFont("Helvetica-Bold", 12); c.drawCentredString(x_pos + 5 * cm, y_pos + 0.5 * cm, f"( {data['Nama_Pengantar_Berkas']} )")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 0.5 * cm, f"( {data['Penerima_Berkas']} )")
    c.showPage()
    
    # HALAMAN 2 (BELAKANG)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    y_tab = y_pos + 8.85 * cm; tinggi_baris = 1.15 * cm
    tgl_ambil_pdf = "" if data['Tanggal_Pengambilan'] in ["-", "nan", "NAN"] else data['Tanggal_Pengambilan']
    
    rows = [("NO. URUT PENDAFTARAN", data['No']), ("TANGGAL TERIMA BERKAS", data['Tanggal_Pengantaran']),
            ("TANGGAL PENGAMBILAN", tgl_ambil_pdf), ("NAMA & NOMOR TOKO", f"{data['Nama_Toko']} - {data['No_Toko']}"),
            ("NAMA PEMILIK (SK)", data['Nama_Pemilik_Asli']), ("PENGANTAR BERKAS", data['Nama_Pengantar_Berkas'])]
            
    for label, val in rows:
        c.rect(x_pos + 0.15*cm, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris); c.rect(lebar_kertas/2, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.setFont("Helvetica-Bold", 10); c.drawString(x_pos + 0.6 * cm, y_tab - 0.75 * cm, label)
        c.setFont("Helvetica-Bold", 11); c.drawString(lebar_kertas/2 + 0.6 * cm, y_tab - 0.75 * cm, str(val).upper())
        y_tab -= tinggi_baris
        
    c.save(); buffer.seek(0)
    return buffer

def cetak_overprint(tgl_ambil):
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(22*cm, 11*cm))
    c.setFont("Helvetica-Bold", 12); c.drawString(11.6 * cm, 1 * cm + 8.85 * cm - (1.15 * cm * 3) + 0.4 * cm, tgl_ambil.upper())
    c.save(); buffer.seek(0); return buffer

def format_tgl_indo(tgl_input):
    if not tgl_input or tgl_input == "-": return ""
    try:
        dt = pd.to_datetime(tgl_input, dayfirst=True)
        return f"{dt.day:02d}-{dt.month:02d}-{dt.year}"
    except: return str(tgl_input).upper()

# ==========================================
# 3. NAVIGASI SIDEBAR
# ==========================================
st.sidebar.title("🗂️ DASHBOARD UPTD")
modul = st.sidebar.selectbox("PILIH MODUL:", ["SK MENEMPATI TOKO", "REKAP PARKIR"])

# ==========================================
# 4. MODUL SK MENEMPATI TOKO
# ==========================================
if modul == "SK MENEMPATI TOKO":
    menu_sk = st.sidebar.radio("MENU:", ["PENGANTARAN", "PENGAMBILAN"])
    df_sk = conn.read(worksheet="DATA_SK", ttl=60).astype(str).replace("nan", "-")

    if menu_sk == "PENGANTARAN":
        st.header("📝 INPUT PENGANTARAN BERKAS")
        # Hitung No Urut
        try: nums = pd.to_numeric(df_sk['
