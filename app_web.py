import streamlit as st
import pandas as pd
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os

# ==========================================
# 1. KONFIGURASI HALAMAN (TAMPILAN STANDAR)
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="🏪",
    layout="wide"
)

# Koneksi Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI HELPER & LOGIKA DATA
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        # Bersihkan data dari spasi dan format .0
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip()
        # Seragamkan data kosong jadi "-"
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

def safe_update(worksheet: str, data: pd.DataFrame) -> bool:
    try:
        # Hapus kolom pembantu (Tgl_DT) sebelum upload agar Sheets tidak rusak
        cols_to_drop = ["Tgl_DT", "Tgl_Temp"]
        data_clean = data.drop(columns=[c for c in cols_to_drop if c in data.columns])
        conn.update(worksheet=worksheet, data=data_clean)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")
        return False

def format_tgl_hari_indo(tgl_str):
    if not tgl_str or tgl_str in ["-", "nan", ""]: return ""
    try:
        tgl_b = str(tgl_str).strip().replace('/', '-')
        fmt = "%d-%m-%y" if len(tgl_b.split('-')[-1]) == 2 else "%d-%m-%Y"
        dt = datetime.strptime(tgl_b, fmt)
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except: return str(tgl_str).upper()

# ==========================================
# 3. FUNGSI PDF (SK & PARKIR)
# ==========================================
def buat_pdf_sk(data: dict, berkas_pilihan: list) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm))
    M = 0.75*cm; BOX_H = 10.5*cm; Y_BASE = (33*cm - BOX_H) - M; MID = 10.75*cm
    c.setLineWidth(1.5); c.rect(M, Y_BASE, 20*cm, BOX_H); c.rect(M+0.15*cm, Y_BASE+0.15*cm, 19.7*cm, BOX_H-0.3*cm)
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(MID, Y_BASE+9.3*cm, "TANDA TERIMA BERKAS IZIN TOKO")
    
    y_text = Y_BASE + 8.2*cm
    c.setFont("Helvetica-Bold", 9); c.drawString(M+1*cm, y_text, "BERKAS YANG DITERIMA:")
    y_text -= 0.7*cm
    berkas_master = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for item in berkas_master:
        c.setFont("Helvetica", 9)
        status = "[X]" if item in berkas_pilihan else "[   ]"
        c.drawString(M+1.5*cm, y_text, f"{status} {item}")
        y_text -= 0.6*cm
    
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(M+5*cm, Y_BASE+0.6*cm, f"( {data.get('Nama_Pengantar_Berkas','')} )")
    c.drawCentredString(M+15*cm, Y_BASE+0.6*cm, f"( {data.get('Penerima_Berkas','')} )")
    c.showPage(); c.save(); buffer.seek(0); return buffer

def cetak_tanda_terima_parkir(data):
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm))
    c.setFont("Helvetica-Bold", 9); c.drawCentredString(10.75*cm, 31.5*cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.setFont("Helvetica", 8); c.drawCentredString(10.75*cm, 30.5*cm, f"Tgl: {data['Tanggal']} | Petugas: {data['Nama_Petugas']}")
    c.showPage(); c.save(); buffer.seek(0); return buffer

def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm))
    c.setFont("Helvetica-Bold", 10); c.drawString(7.75*cm, 29.3*cm, format_tgl_hari_indo(tgl_ambil).upper())
    c.showPage(); c.save(); buffer.seek(0); return buffer

# ==========================================
# 4. MODUL SK TOKO
# ==========================================
def halaman_sk(menu):
    st.header(f"📄 SK TOKO - {menu}")
    df_sk = load_data("DATA_SK")
    
    if menu == "PENGANTARAN":
        st.subheader("☑️ Pilih Berkas yang Dibawa:")
        berkas_master = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
        col_b1, col_b2 = st.columns(2)
        sel_berkas = []
        for i, b in enumerate(berkas_master):
            with col_b1 if i < 3 else col_b2:
                if st.checkbox(b, key=f"sk_{b}"): sel_berkas.append(b)

        with st.form("form_sk", clear_on_submit=False):
            c1, c2 = st.columns(2)
            no_u = c1.text_input("NOMOR URUT", value=str(len(df_sk[df_sk['No']!='-'])+1))
            tgl_t = c1.text_input("TANGGAL TERIMA", value=datetime.now().strftime("%d-%m-%Y"))
            toko = c1.text_input("NAMA TOKO").upper()
            asli = c2.text_input("NAMA PEMILIK SK").upper()
            antar = c2.text_input("PENGANTAR BERKAS").upper()
            terima = c2.text_input("PENERIMA BERKAS").upper()
            
            if st.form_submit_button("💾 SIMPAN & CETAK", type="primary"):
                if not all([no_u, toko, asli, antar, terima]):
                    st.error("❌ Semua data wajib diisi!")
                else:
                    new_row = {"No": no_u, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", "Nama_Toko": toko, "Nama_Pemilik_Asli": asli, "Nama_Pengantar_Berkas": antar, "Penerima_Berkas": terima}
                    if safe_update("DATA_SK", pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)):
                        st.success("✅ Berhasil Disimpan!"); st.session_state["last_sk_pdf"] = buat_pdf_sk(
