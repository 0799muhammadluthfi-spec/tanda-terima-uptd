import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import time

# ==========================================
# 1. KONFIGURASI & KONEKSI
# ==========================================
st.set_page_config(page_title="UPTD PASAR KANDANGAN", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI PEMBUAT PDF (UPDATE UKURAN 22 x 12 CM)
# ==========================================
def buat_pdf_full(data, berkas_list):
    buffer = BytesIO()
    # UPDATE: Ukuran sekarang 22cm x 12cm sesuai permintaan Bapak
    UKURAN_CUSTOM = (22 * cm, 12 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    
    # x_pos tetap 1cm, y_pos kita naikkan dikit biar tidak terlalu mepet bawah
    x_pos, y_pos = 1 * cm, 1.5 * cm 
    lebar_kertas = 22 * cm
    
    # HALAMAN 1 (DEPAN) - Bingkai dipermanis
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    
    # Judul (Posisinya disesuaikan dengan tinggi 12cm)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(lebar_kertas/2, y_pos + 8.1 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    
    # Checkbox Dokumen
    yy = y_pos + 6.3 * cm
    items = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(items, 1):
        c.setFont("Helvetica-BoldOblique", 10); c.drawString(x_pos + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10); x_status = x_pos + 15 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        if item in berkas_list: 
            c.line(x_status + 1.2 * cm, yy + 0.1 * cm, x_status + 3.5 * cm, yy + 0.1 * cm) # Coret TIDAK ADA
        else: 
            c.line(x_status - 0.1 * cm, yy + 0.1 * cm, x_status + 0.8 * cm, yy + 0.1 * cm) # Coret ADA
        yy -= 0.6 * cm
        
    # Nama Pengantar & Penerima
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 0.5 * cm, f"( {data['Nama_Pengantar_Berkas']} )")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 0.5 * cm, f"( {data['Penerima_Berkas']} )")
    c.showPage()
    
    # HALAMAN 2 (BELAKANG) - Ukuran tetap sama
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    
    y_tab = y_pos + 8.85 * cm; tinggi_baris = 1.15 * cm
    tgl_ambil_pdf = "" if data['Tanggal_Pengambilan'] in ["-", "nan", "NAN"] else data['Tanggal_Pengambilan']
    
    rows = [("NO. URUT PENDAFTARAN", data['No']), ("TANGGAL TERIMA BERKAS", data['Tanggal_Pengantaran']),
            ("TANGGAL PENGAMBILAN", tgl_ambil_pdf), ("NAMA & NOMOR TOKO", f"{data['Nama_Toko']} - {data['No_Toko']}"),
            ("NAMA PEMILIK (SK)", data['Nama_Pemilik_Asli']), ("PENGANTAR BERKAS", data['Nama_Pengantar_Berkas'])]
            
    for label, val in rows:
        c.rect(x_pos + 0.15*cm, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.rect(lebar_kertas/2, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.setFont("Helvetica-Bold", 9); c.drawString(x_pos + 0.6 * cm, y_tab - 0.75 * cm, label)
        c.setFont("Helvetica-Bold", 10); c.drawString(lebar_kertas/2 + 0.6 * cm, y_tab - 0.75 * cm, str(val).upper())
        y_tab -= tinggi_baris
        
    c.save(); buffer.seek(0)
    return buffer

def cetak_overprint(tgl_ambil):
    # Overprint juga disesuaikan ukurannya 22x12
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(22*cm, 12*cm))
    c.setFont("Helvetica-Bold", 12)
    # Koordinat x=11.6cm dan y=6.5cm biar pas di kotak Tanggal Pengambilan
    c.drawString(11.6 * cm, 6.5 * cm, tgl_ambil.upper())
    c.save(); buffer.seek(0); return buffer

# ==========================================
# 3. INTERFACE (KODE LANJUTAN TETAP SAMA)
# ==========================================
st.sidebar.title("🗂️ DASHBOARD UPTD")
modul = st.sidebar.selectbox("PILIH MODUL:", ["SK MENEMPATI TOKO", "REKAP PARKIR"])

if modul == "SK MENEMPATI TOKO":
    menu_sk = st.sidebar.radio("MENU:", ["PENGANTARAN", "PENGAMBILAN"])
    df_sk = conn.read(worksheet="DATA_SK", ttl=60).astype(str).replace("nan", "-")

    if menu_sk == "PENGANTARAN":
        st.header("📝 INPUT PENGANTARAN BERKAS")
        try: 
            nums = pd.to_numeric(df_sk['No'], errors='coerce').dropna()
            last_no = int(nums.max())
        except: last_no = 0
        
        no_urut = st.text_input("NO. URUT", value=str(last_no + 1))
        c1, c2 = st.columns(2)
        tgl_t = c1.text_input("TANGGAL TERIMA (DD-MM-YYYY)", value=datetime.now().strftime("%d-%m-%Y"))
        nama_toko = c1.text_input("NAMA TOKO").upper()
        no_toko = c1.text_input("NOMOR TOKO").upper()
        sk = c2.text_input("NAMA PEMILIK SK").upper()
        pengantar = c2.text_input("PENGANTAR").upper()
        penerima = c2.text_input("PENERIMA").upper()
        
        t_list = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
        sel_berkas = [t for t in t_list if st.checkbox(t)]

        if st.button("💾 SIMPAN & CETAK"):
            if not nama_toko or not sk:
                st.error("NAMA TOKO & PEMILIK HARUS DIISI!")
            else:
                new_row = {"No": no_urut, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", 
                           "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": sk, 
                           "Nama_Pengantar_Berkas": pengantar, "Penerima_Berkas": penerima}
                df_final = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(worksheet="DATA_SK", data=df_final)
                st.cache_data.clear()
                st.success("✅ DATA DISIMPAN!")
                st.download_button("📥 DOWNLOAD PDF", buat_pdf_full(new_row, sel_berkas), f"TANDA_{no_urut}.pdf")

    elif menu_sk == "PENGAMBILAN":
        st.header("🏁 PENGAMBILAN (OVERPRINT)")
        no_cari = st.text_input("CARI NOMOR URUT").strip()
        if no_cari:
            hasil = df_sk[df_sk['No'] == no_cari]
            if not hasil.empty:
                data_lama = hasil.iloc[0]
                st.info(f"DATA: {data_lama['Nama_Toko']} - {data_lama['Nama_Pemilik_Asli']}")
                tgl_a = st.text_input("TANGGAL AMBIL", value=datetime.now().strftime("%d-%m-%Y"))
                if st.button("✅ UPDATE & CETAK"):
                    df_sk.loc[df_sk['No'] == no_cari, 'Tanggal_Pengambilan'] = tgl_a
                    conn.update(worksheet="DATA_SK", data=df_sk)
                    st.cache_data.clear()
                    st.success("TANGGAL UPDATE!")
                    st.download_button("📥 DOWNLOAD OVERPRINT", cetak_overprint(tgl_a), f"UP_{no_cari}.pdf")
            else: st.error("TIDAK DITEMUKAN")

elif modul == "REKAP PARKIR":
    st.header("🅿️ MODUL REKAP PARKIR")
    st.info("Silakan siapkan tab LOG_PARKIR di Google Sheets Anda besok.")
