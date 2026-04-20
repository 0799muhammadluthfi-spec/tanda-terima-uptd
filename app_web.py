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
st.set_page_config(page_title="UPTD PASAR KANDANGAN", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI PDF (FIX GARIS & POSISI)
# ==========================================
def buat_pdf_full(data, berkas_list):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 12 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    
    # Titik nol kita atur agak naik dari bawah kertas
    x_pos, y_pos = 1 * cm, 1.2 * cm 
    lebar_kertas = 22 * cm
    
    # HALAMAN 1 (DEPAN)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9.5*cm) # Bingkai luar
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 9.2*cm) # Bingkai dalam
    
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(lebar_kertas/2, y_pos + 8.5 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    
    # Baris Berkas
    yy = y_pos + 7.0 * cm
    items = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(items, 1):
        c.setFont("Helvetica-BoldOblique", 10); c.drawString(x_pos + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10); x_status = x_pos + 15 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        # Logika Coret
        if item in berkas_list: 
            c.line(x_status + 1.2 * cm, yy + 0.1 * cm, x_status + 3.5 * cm, yy + 0.1 * cm)
        else: 
            c.line(x_status - 0.1 * cm, yy + 0.1 * cm, x_status + 0.8 * cm, yy + 0.1 * cm)
        yy -= 0.7 * cm
        
    # GARIS TTD (DInaikkan agar tidak hilang)
    c.setLineWidth(1)
    c.line(x_pos + 0.15*cm, y_pos + 2.8 * cm, x_pos + 19.85*cm, y_pos + 2.8 * cm) # Garis horizontal ttd
    c.line(lebar_kertas/2, y_pos + 0.15*cm, lebar_kertas/2, y_pos + 2.8 * cm) # Garis vertikal pembagi
    
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 2.3 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 2.3 * cm, "PETUGAS PENERIMA")
    
    # Nama di bawah (TTD)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 0.6 * cm, f"( {str(data['Nama_Pengantar_Berkas']).upper()} )")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 0.6 * cm, f"( {str(data['Penerima_Berkas']).upper()} )")
    
    c.showPage()
    
    # HALAMAN 2 (BELAKANG)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9.5*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 9.2*cm)
    
    y_tab = y_pos + 9.35 * cm; tinggi_baris = 1.25 * cm
    rows = [("NO. URUT", data['No']), ("TGL TERIMA", data['Tanggal_Pengantaran']),
            ("TGL AMBIL", data['Tanggal_Pengambilan']), ("TOKO", f"{data['Nama_Toko']} - {data['No_Toko']}"),
            ("PEMILIK", data['Nama_Pemilik_Asli']), ("PENGANTAR", data['Nama_Pengantar_Berkas'])]
            
    for label, val in rows:
        c.rect(x_pos + 0.15*cm, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.rect(lebar_kertas/2, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.setFont("Helvetica-Bold", 9); c.drawString(x_pos + 0.6 * cm, y_tab - 0.8 * cm, label)
        c.setFont("Helvetica-Bold", 10); c.drawString(lebar_kertas/2 + 0.6 * cm, y_tab - 0.8 * cm, str(val).upper())
        y_tab -= tinggi_baris
        
    c.save(); buffer.seek(0)
    return buffer

# ==========================================
# 3. INTERFACE UTAMA
# ==========================================
st.sidebar.title("🗂️ UPTD KANDANGAN")
modul = st.sidebar.selectbox("PILIH MODUL:", ["SK MENEMPATI TOKO", "REKAP PARKIR"])

if modul == "SK MENEMPATI TOKO":
    menu = st.sidebar.radio("MENU:", ["PENGANTARAN", "PENGAMBILAN"])
    # Membaca data dengan proteksi nama tab
    try:
        df_sk = conn.read(worksheet="DATA_SK", ttl=0).astype(str).replace("nan", "-")
    except:
        st.error("❌ TAB 'DATA_SK' TIDAK DITEMUKAN DI GOOGLE SHEETS!")
        st.stop()

    if menu == "PENGANTARAN":
        st.header("📝 INPUT BERKAS")
        # Penomoran otomatis
        try:
            val_no = pd.to_numeric(df_sk['No'], errors='coerce').max()
            next_no = int(val_no) + 1 if not pd.isna(val_no) else 1
        except: next_no = 1
        
        no_urut = st.text_input("NO. URUT", value=str(next_no))
        c1, c2 = st.columns(2)
        tgl_t = c1.text_input("TANGGAL (DD-MM-YYYY)", value=datetime.now().strftime("%d-%m-%Y"))
        nama_toko = c1.text_input("NAMA TOKO").upper()
        no_toko = c1.text_input("NOMOR TOKO").upper()
        sk = c2.text_input("NAMA PEMILIK SK").upper()
        pengantar = c2.text_input("PENGANTAR").upper()
        penerima = c2.text_input("PENERIMA").upper()
        
        t_list = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
        sel_berkas = [t for t in t_list if st.checkbox(t)]

        if st.button("💾 SIMPAN & CETAK"):
            if not nama_toko or not sk:
                st.warning("⚠️ Nama Toko & Pemilik harus diisi!")
            else:
                new_row = {"No": no_urut, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", 
                           "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": sk, 
                           "Nama_Pengantar_Berkas": pengantar, "Penerima_Berkas": penerima}
                df_final = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(worksheet="DATA_SK", data=df_final)
                st.success("✅ Tersimpan!")
                st.download_button("📥 DOWNLOAD PDF", buat_pdf_full(new_row, sel_berkas), f"TANDA_{no_urut}.pdf")

    elif menu == "PENGAMBILAN":
        st.header("🏁 PENGAMBILAN")
        no_cari = st.text_input("MASUKKAN NOMOR URUT:").strip()
        
        if no_cari:
            # Cari data dengan strip agar lebih akurat
            hasil = df_sk[df_sk['No'].str.strip() == no_cari]
            
            if not hasil.empty:
                data_lama = hasil.iloc[0]
                st.success(f"📦 DATA DITEMUKAN: {data_lama['Nama_Toko']} (Pemilik: {data_lama['Nama_Pemilik_Asli']})")
                tgl_a = st.text_input("TANGGAL AMBIL", value=datetime.now().strftime("%d-%m-%Y"))
                
                if st.button("✅ UPDATE TANGGAL"):
                    df_sk.loc[df_sk['No'].str.strip() == no_cari, 'Tanggal_Pengambilan'] = tgl_a
                    conn.update(worksheet="DATA_SK", data=df_sk)
                    st.balloons()
                    st.success("Berhasil diupdate!")
            else:
                st.error(f"❓ Nomor Urut {no_cari} tidak ada dalam data. Cek kembali pengetikan Anda.")

elif modul == "REKAP PARKIR":
    st.info("Modul Parkir Siap Dikonfigurasi.")
