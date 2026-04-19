import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UPTD Pasar Kandangan - Dashboard", layout="wide")

# --- KONEKSI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def buat_pdf_full(data):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 11 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    x_pos, y_pos = 1 * cm, 1 * cm
    lebar_kertas = 22 * cm

    # --- HALAMAN 1: DEPAN ---
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(lebar_kertas/2, y_pos + 8.1 * cm, "TANDA TERIMA BERKAS PERMOHONAN PERPANJANGAN IZIN TOKO")
    c.setLineWidth(1); c.line(x_pos + 0.4*cm, y_pos + 7.85*cm, x_pos + 19.6*cm, y_pos + 7.85*cm)
    c.line(x_pos + 0.4*cm, y_pos + 7.75*cm, x_pos + 19.6*cm, y_pos + 7.75*cm)
    
    c.setFont("Helvetica-Bold", 11); c.drawString(x_pos + 0.8 * cm, y_pos + 7.1 * cm, "Daftar kelengkapan dokumen permohonan:")
    
    yy = y_pos + 6.3 * cm
    items = ["SK Asli Menempati", "Pas Foto 3x4 (2 lbr)", "FC KTP Pemilik", "FC Kartu Sewa", "Surat Kuasa", "Surat Kehilangan"]
    
    # Ambil data ceklis dari kolom Keterangan
    berkas_terpilih = data['Keterangan'].split(", ") if data['Keterangan'] else []
    
    for i, item in enumerate(items, 1):
        c.setFont("Helvetica-BoldOblique", 10.5); c.drawString(x_pos + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 11); x_status = x_pos + 15.2 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        c.setLineWidth(1.5)
        
        # --- LOGIKA GARIS YANG SUDAH BAPAK SESUAIKAN ---
        if item in berkas_terpilih:
            # CORET "TIDAK ADA"
            c.line(x_status + 1.5 * cm, yy + 0.12 * cm, x_status + 3.8 * cm, yy + 0.12 * cm)
        else:
            # CORET "ADA"
            c.line(x_status - 0.1 * cm, yy + 0.12 * cm, x_status + 0.9 * cm, yy + 0.12 * cm)
        yy -= 0.65 * cm

    c.setLineWidth(1.5)
    c.line(x_pos + 0.15*cm, y_pos + 2.8 * cm, x_pos + 19.85*cm, y_pos + 2.8 * cm)
    c.line(lebar_kertas/2, y_pos + 0.15*cm, lebar_kertas/2, y_pos + 2.8 * cm)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 2.3 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 2.3 * cm, "PETUGAS PENERIMA BERKAS")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 0.5 * cm, f"( {data['Nama_Pengantar_Berkas']} )")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 0.5 * cm, f"( {data['Penerima_Berkas']} )")
    c.showPage()

    # --- HALAMAN 2: BELAKANG ---
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    y_tab = y_pos + 8.85 * cm; tinggi_baris = 1.15 * cm
    rows = [
        ("NO. URUT PENDAFTARAN", data['No']), 
        ("TANGGAL TERIMA BERKAS", data['Tanggal_Pengantaran']),
        ("TANGGAL PENGAMBILAN", data['Tanggal_Pengambilan']), 
        ("NAMA & NOMOR TOKO / LAPAK", f"{data['Nama_Toko']} - {data['No_Toko']}"),
        ("NAMA PEMILIK (SESUAI SK)", data['Nama_Pemilik_Asli']), 
        ("NAMA PENGANTAR BERKAS", data['Nama_Pengantar_Berkas'])
    ]
    for label, val in rows:
        c.setLineWidth(1.5)
        c.rect(x_pos + 0.15*cm, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.rect(lebar_kertas/2, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.setFont("Helvetica-Bold", 10); c.drawString(x_pos + 0.6 * cm, y_tab - 0.75 * cm, label)
        c.setFont("Helvetica-Bold", 11); c.drawString(lebar_kertas/2 + 0.6 * cm, y_tab - 0.75 * cm, str(val).upper())
        y_tab -= tinggi_baris
    c.save(); buffer.seek(0)
    return buffer

def cetak_overprint(tgl_ambil):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 11 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    c.showPage() # Halaman 1 Kosong
    # Halaman 2: Cetak Tanggal Pengambilan saja
    y_pos_tgl = 1 * cm + 8.85 * cm - (1.15 * cm * 3) + 0.4 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(11 * cm + 0.6 * cm, y_pos_tgl, tgl_ambil.upper())
    c.save(); buffer.seek(0)
    return buffer

# --- INTERFACE UTAMA ---
st.sidebar.title("MENU UPTD PASAR")
menu = st.sidebar.radio("Pilih Kegiatan:", ["Input Berkas Baru", "Dashboard Pengambilan (Overprint)"])

# Baca Database dari Google Sheets
df = conn.read()

if menu == "Input Berkas Baru":
    st.header("📝 Penerimaan Berkas Baru")
    
    # Logika Auto-Number
    last_no = 0 if df.empty else pd.to_numeric(df['No'], errors='coerce').max()
    no_urut = st.text_input("No. Urut Pendaftaran", value=str(int(last_no) + 1))
    
    col1, col2 = st.columns(2)
    with col1:
        tgl_t = st.text_input("Tanggal Pengantaran", value=datetime.now().strftime("%A, %d %B %Y").upper())
        nama_toko = st.text_input("Nama Toko/Usaha").upper()
        no_toko = st.text_input("Nomor Toko/Lapak").upper()
    with col2:
        sk = st.text_input("Nama Pemilik Sesuai SK").upper()
        pengantar = st.text_input("Nama Pengantar Berkas").upper()
        penerima = st.text_input("Petugas Penerima").upper()
    
    t_list = ["SK Asli Menempati", "Pas Foto 3x4 (2 lbr)", "FC KTP Pemilik", "FC Kartu Sewa", "Surat Kuasa", "Surat Kehilangan"]
    st.write("Ceklis Kelengkapan Berkas:")
    sel_berkas = [t for t in t_list if st.checkbox(t)]

    if st.button("SIMPAN & CETAK FULL"):
        ket_gabung = ", ".join(sel_berkas)
        new_row = {
            "No": no_urut, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", 
            "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": sk, 
            "Nama_Pengantar_Berkas": pengantar, "Penerima_Berkas": penerima, "Keterangan": ket_gabung
        }
        # Update ke Google Sheets
        df_updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        conn.update(data=df_updated)
        
        st.success("Data Berhasil Disimpan ke Google Sheets!")
        pdf = buat_pdf_full(new_row)
        st.download_button("📥 Download PDF Tanda Terima", pdf, f"Tanda_Terima_{no_urut}.pdf", "application/pdf")

elif menu == "Dashboard Pengambilan (Overprint)":
    st.header("🏁 Mode Pengambilan (Overprint)")
    no_cari = st.text_input("Cari No. Urut Pendaftaran")
    
    if no_cari:
        hasil = df[df['No'].astype(str) == no_cari]
        if not hasil.empty:
            data_lama = hasil.iloc[0]
            st.info(f"Data Ditemukan: {data_lama['Nama_Toko']} (Pemilik: {data_lama['Nama_Pemilik_Asli']})")
            tgl_ambil = st.text_input("Input Tanggal Pengambilan", value=datetime.now().strftime("%A, %d %B %Y").upper())
            
            if st.button("UPDATE DATA & CETAK TANGGAL"):
                # Update kolom tanggal di DataFrame
                df.loc[df['No'].astype(str) == no_cari, 'Tanggal_Pengambilan'] = tgl_ambil
                conn.update(data=df)
                
                st.success("Tanggal Pengambilan Berhasil Dicatat!")
                pdf_over = cetak_overprint(tgl_ambil)
                st.download_button("📥 Download PDF Overprint (Hanya Tanggal)", pdf_over, f"Update_Tgl_{no_cari}.pdf", "application/pdf")
        else:
            st.error("Nomor Urut tidak ditemukan di Database.")
