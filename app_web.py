import streamlit as st
import pandas as pd
from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. FUNGSI PENUNJANG (LOGIKA & PDF)
# ==========================================

def format_tgl_indo(tgl_str):
    try:
        tgl_input = str(tgl_str).replace('/', '-')
        if len(tgl_input.split('-')[-1]) == 2:
            tgl_obj = datetime.strptime(tgl_input, "%d-%m-%y")
        else:
            tgl_obj = datetime.strptime(tgl_input, "%d-%m-%Y")
        hari_indo = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
        return f"{hari_indo[tgl_obj.weekday()]}, {tgl_obj.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()

def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    
    lebar_box, tinggi_box = 6.8 * cm, 4.6 * cm
    x_awal = (lebar_kertas - lebar_box) / 2
    center_x = lebar_kertas / 2
    y_top = 32 * cm 
    y_bottom = y_top - tinggi_box
    
    # Bingkai & Garis Potong
    c.setLineWidth(1.2); c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    y_gp = y_bottom - 1.0 * cm
    c.setDash(1, 3); c.setLineWidth(0.5); c.line(0, y_gp, lebar_kertas, y_gp); c.setDash() 
    
    # Header & Data
    tgl_display = format_tgl_indo(data['Tanggal'])
    c.setFont("Helvetica-Bold", 7); c.drawCentredString(center_x, y_top - 0.5*cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6); c.drawCentredString(center_x, y_top - 0.9*cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.line(x_awal + 0.3*cm, y_top - 1.1*cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1*cm)
    
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_awal + 0.3*cm, y_top - 1.5*cm, f"TGL : {tgl_display}")
    c.drawString(x_awal + 0.3*cm, y_top - 1.9*cm, f"NAMA : {str(data['Nama_Petugas']).upper()}")

    # Tabel Mini
    y_tab, t_row = y_top - 2.2*cm, 0.6*cm
    x_tab, l_tab = x_awal + 0.3*cm, lebar_box - 0.6*cm
    
    items = [("RODA 2", data.get('MPP_Roda_R2', 0)), ("RODA 4", data.get('MPP_Roda_R4', 0))]
    for i, (jns, jml) in enumerate(items):
        y_r = y_tab - ((i+1) * t_row)
        c.rect(x_tab, y_r, l_tab, t_row)
        c.setFont("Helvetica", 6); c.drawString(x_tab + 0.1*cm, y_r + 0.2*cm, jns)
        c.drawCentredString(center_x, y_r + 0.2*cm, f"{jml} LBR")
        c.drawRightString(x_tab + l_tab - 0.1*cm, y_r + 0.2*cm, "MPP")
    
    c.showPage(); c.save(); buffer.seek(0)
    return buffer

# ==========================================
# 2. DATABASE UTAMA
# ==========================================

def load_data(sheet_name):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=sheet_name, ttl="0")

def safe_update(sheet_name, df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet=sheet_name, data=df)
    return True

def halaman_parkir(menu_aktif):
    # TAMPILAN LOGO HSS
    path_logo = "logo_hss.png" 
    if os.path.exists(path_logo):
        st.image(path_logo, width=80)
    
    st.header(f"🚗 {menu_aktif}")
    df_parkir = load_data("DATA_PARKIR")

    if menu_aktif == "INPUT REKAP":
        st.subheader("📝 FORM REKAP SETORAN")
        tgl_input = st.text_input("MASUKKAN TANGGAL", value=datetime.now().strftime("%d-%m-%Y"))
        
        # Logika Mencari Baris Jadwal
        baris_cocok = df_parkir[df_parkir["Tanggal"].astype(str) == tgl_input]
        
        if not baris_cocok.empty:
            idx = baris_cocok.index[0]
            nama_ptgs = baris_cocok.iloc[0]["Nama_Petugas"]
            st.success(f"👤 PETUGAS: **{nama_ptgs}** | 📅 **{format_tgl_indo(tgl_input)}**")
            
            # AMBIL SISA KEMARIN (idx - 1)
            sisa_r2_lama = df_parkir.iloc[idx - 1]["Sisa_Stok_R2"] if idx > 0 else 0
            sisa_
