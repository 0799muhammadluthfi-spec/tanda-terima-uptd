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
    UKURAN_CUSTOM = (22 * cm, 11 *
