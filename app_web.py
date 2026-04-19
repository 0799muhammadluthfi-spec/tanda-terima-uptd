import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UPTD Kandangan - Online", layout="centered")

# --- FUNGSI GENERATE PDF (DESAIN v3.1 FIXED) ---
def buat_pdf_web(data, dokumen):
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
    
    c.setLineWidth(1)
    c.line(x_pos + 0.4*cm, y_pos + 7.85*cm, x_pos + 19.6*cm, y_pos + 7.85*cm)
    c.line(x_pos + 0.4*cm, y_pos + 7.75*cm, x_pos + 19.6*cm, y_pos + 7.75*cm)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_pos + 0.8 * cm, y_pos + 7.1 * cm, "Daftar kelengkapan dokumen permohonan:")

    yy = y_pos + 6.3 * cm
    # BARIS 34 (MULAI DI SINI)
    for i, (item, status) in enumerate(dokumen.items(), 1):
        c.setFont("Helvetica-BoldOblique", 10.5)
        c.drawString(x_pos + 1 * cm, yy, f"{i}. {item}")
        
        c.setFont("Helvetica-Bold", 11)
        x_status = x_pos + 15.2 * cm 
        c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        
        c.setLineWidth(1.5) 
        if status == "Ada":
            # CORET "TIDAK ADA"
            c.line(x_status + 1.5 * cm, yy + 0.12 * cm, x_status + 3.8 * cm, yy + 0.12 * cm)
        else:
            # CORET "ADA"
            c.line(x_status - 0.1 * cm, yy + 0.12 * cm, x_status + 1.1 * cm, yy + 0.12 * cm)
        yy -= 0.65 * cm

    # BARIS 54 (TTD)
    c.setLineWidth(1.5)
    c.line(x_pos + 0.15*cm, y_pos + 2.8 * cm, x_pos + 19.85*cm, y_pos + 2.8 * cm)
    c.line(lebar_kertas/2, y_pos + 0.15*cm, lebar_kertas/2, y_pos + 2.8 * cm)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 2.3 * cm, data['ket_ttd'].upper())
    c.drawCentredString(x_pos + 15 * cm, y_pos + 2.3 * cm, "PETUGAS PENERIMA BERKAS")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 0.5 * cm, f"( {data['peng'].upper()} )")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 0.5 * cm, f"( {data['ptg'].upper()} )")

    c.showPage()

    # --- HALAMAN 2: BELAKANG ---
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)

    y_tab = y_pos + 8.85 * cm
    tinggi_baris = 1.15 * cm
    toko_gabung = f"{data['toko']} - NO. {data['no_t']}"

    rows = [
        ("NO. URUT PENDAFTARAN", data['no']),
        ("TANGGAL TERIMA BERKAS", data['tgl_t']),
        ("TANGGAL PENGAMBILAN", data['tgl_a']),
        ("NAMA & NOMOR TOKO / LAPAK", toko_gabung),
        ("NAMA PEMILIK (SESUAI SK)", data['sk']),
        ("NAMA PENGANTAR BERKAS", data['peng'])
    ]

    for label, value in rows:
        c.setLineWidth(1.5)
        c.rect(x_pos + 0.15*cm, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.rect(lebar_kertas/2, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_pos + 0.6 * cm, y_tab - 0.75 * cm, label)
        c.setFont("Helvetica-Bold", 11)
        teks_isi = str(value).upper()
        if len(teks_isi) > 30: c.setFont("Helvetica-Bold", 9.5)
        c.drawString(lebar_kertas/2 + 0.6 * cm, y_tab - 0.75 * cm, teks_isi)
        y_tab -= tinggi_baris

    y_perhatian = y_tab - 0.6 * cm
    c.setFont("Helvetica-Bold", 10); c.drawString(x_pos + 0.8 * cm, y_perhatian, "PERHATIAN:")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x_pos + 1.2 * cm, y_perhatian - 0.5 * cm, "- Harap bawa tanda terima ini saat pengambilan berkas/SK.")
    c.drawString(x_pos + 1.2 * cm, y_perhatian - 0.9 * cm, "- Pelayanan dilakukan pada hari dan jam kerja UPTD.")

    c.save()
    buffer.seek(0)
    return buffer

# --- TAMPILAN WEB (STREAMLIT) ---
st.title("🏛️ UPTD Pasar Kandangan")
st.write("Sistem Online Tanda Terima Berkas")

# Input Data
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        no = st.text_input("No. Urut Pendaftaran").upper()
        hari = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
        bln = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]
        s = datetime.now()
        tgl_t = st.text_input("Tanggal Terima", value=f"{hari[s.weekday()]}, {s.day} {bln[s.month-1]} {s.year}").upper()
        tgl_a = st.text_input("Tanggal Pengambilan").upper()
    with col2:
        toko = st.text_input("Nama Toko/Usaha").upper()
        no_t = st.text_input("Nomor Toko/Lapak").upper()
        sk = st.text_input("Nama Pemilik (Sesuai SK)").upper()

    peng = st.text_input("Nama Pengantar Berkas").upper()
    ptg = st.text_input("Nama Petugas Penerima").upper()
    ket_ttd = st.text_input("Keterangan TTD Kiri", value="PENGANTAR BERKAS").upper()

st.write("---")
st.write("**Kelengkapan Berkas:**")
t_list = ["SK Asli Menempati", "Pas Foto 3x4 (2 lbr)", "FC KTP Pemilik", "FC Kartu Sewa", "Surat Kuasa", "Surat Kehilangan"]
docs_val = {}
c1, c2 = st.columns(2)
for i, t in enumerate(t_list):
    with (c1 if i % 2 == 0 else c2):
        docs_val[t] = st.checkbox(t)

if st.button("PROSES & BUAT PDF"):
    if not sk or not ptg:
        st.error("Nama Pemilik dan Petugas wajib diisi!")
    else:
        input_data = {
            "no": no, "tgl_t": tgl_t, "tgl_a": tgl_a, "toko": toko, 
            "no_t": no_t, "sk": sk, "peng": peng, "ptg": ptg, "ket_ttd": ket_ttd
        }
        dokumen = {k: ("Ada" if v else "Tidak Ada") for k, v in docs_val.items()}
        
        pdf_out = buat_pdf_web(input_data, dokumen)
        
        st.success("✅ Berhasil! Silakan klik tombol download di bawah:")
        st.download_button(
            label="📥 DOWNLOAD TANDA TERIMA",
            data=pdf_out,
            file_name=f"Tanda_Terima_{sk}.pdf",
            mime="application/pdf"
        )
