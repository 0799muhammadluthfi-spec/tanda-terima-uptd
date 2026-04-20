import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI HALAMAN & KONEKSI
# ==========================================
st.set_page_config(page_title="UPTD PASAR KANDANGAN", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI PDF (UKURAN POTONG F4: 22x12 CM)
# ==========================================
def buat_pdf_full(data, berkas_list):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 12 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    x_pos, y_pos = 1 * cm, 1.2 * cm 
    lebar_kertas = 22 * cm
    
    # HALAMAN 1 (DEPAN)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9.5*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 9.2*cm)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(lebar_kertas/2, y_pos + 8.5 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    
    yy = y_pos + 7.0 * cm
    items = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(items, 1):
        c.setFont("Helvetica-BoldOblique", 10); c.drawString(x_pos + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10); x_status = x_pos + 15 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        if item in berkas_list: 
            c.line(x_status + 1.2 * cm, yy + 0.1 * cm, x_status + 3.5 * cm, yy + 0.1 * cm)
        else: 
            c.line(x_status - 0.1 * cm, yy + 0.1 * cm, x_status + 0.8 * cm, yy + 0.1 * cm)
        yy -= 0.7 * cm
        
    c.setLineWidth(1)
    c.line(x_pos + 0.15*cm, y_pos + 2.8 * cm, x_pos + 19.85*cm, y_pos + 2.8 * cm)
    c.line(lebar_kertas/2, y_pos + 0.15*cm, lebar_kertas/2, y_pos + 2.8 * cm)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 2.3 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 2.3 * cm, "PETUGAS PENERIMA")
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
st.sidebar.title("🗂️ DASHBOARD UPTD")
modul = st.sidebar.selectbox("PILIH MODUL:", ["SK MENEMPATI TOKO", "REKAP PARKIR"])

# --- MODUL 1: SK MENEMPATI TOKO ---
if modul == "SK MENEMPATI TOKO":
    menu_sk = st.sidebar.radio("MENU SK:", ["PENGANTARAN", "PENGAMBILAN"])
    df_sk = conn.read(worksheet="DATA_SK", ttl=0).astype(str).replace("nan", "-")
    
    if menu_sk == "PENGANTARAN":
        st.header("📝 INPUT PENGANTARAN BERKAS SK")
        
        # Hitung No Urut Otomatis
        try:
            val_no = pd.to_numeric(df_sk['No'], errors='coerce').max()
            next_no = int(val_no) + 1 if not pd.isna(val_no) else 1
        except: next_no = 1
        
        with st.form("form_sk"):
            no_urut = st.text_input("NO. URUT", value=str(next_no))
            c1, c2 = st.columns(2)
            tgl_t = c1.text_input("TANGGAL TERIMA (DD-MM-YYYY)", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = c1.text_input("NAMA TOKO").upper()
            no_toko = c1.text_input("NOMOR TOKO").upper()
            sk = c2.text_input("NAMA PEMILIK SK").upper()
            pengantar = c2.text_input("PENGANTAR").upper()
            penerima = c2.text_input("PENERIMA").upper()
            
            st.write("---")
            st.subheader("📋 CEKLIST DOKUMEN")
            t_list = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
            sel_berkas = [t for t in t_list if st.checkbox(t)]
            
            submit = st.form_submit_button("💾 SIMPAN & BUAT PDF")
            
            if submit:
                if not nama_toko or not sk:
                    st.error("⚠️ NAMA TOKO & PEMILIK WAJIB DIISI!")
                else:
                    new_row = {"No": no_urut, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", 
                               "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": sk, 
                               "Nama_Pengantar_Berkas": pengantar, "Penerima_Berkas": penerima}
                    df_final = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                    conn.update(worksheet="DATA_SK", data=df_final)
                    st.success(f"✅ DATA {nama_toko} BERHASIL DISIMPAN!")
                    st.download_button("📥 DOWNLOAD PDF TANDA TERIMA", buat_pdf_full(new_row, sel_berkas), f"TANDA_{no_urut}.pdf")

    elif menu_sk == "PENGAMBILAN":
        st.header("🏁 PENGAMBILAN BERKAS (UPDATE TANGGAL)")
        no_cari = st.text_input("MASUKKAN NOMOR URUT:").strip()
        if no_cari:
            hasil = df_sk[df_sk['No'].str.strip() == no_cari]
            if not hasil.empty:
                data_lama = hasil.iloc[0]
                st.success(f"📦 DATA DITEMUKAN: {data_lama['Nama_Toko']} (Pemilik: {data_lama['Nama_Pemilik_Asli']})")
                tgl_a = st.text_input("TANGGAL AMBIL", value=datetime.now().strftime("%d-%m-%Y"))
                if st.button("✅ UPDATE TANGGAL AMBIL"):
                    df_sk.loc[df_sk['No'].str.strip() == no_cari, 'Tanggal_Pengambilan'] = tgl_a
                    conn.update(worksheet="DATA_SK", data=df_sk)
                    st.success("✅ TANGGAL BERHASIL DIUPDATE!")
            else:
                st.error("❌ NOMOR URUT TIDAK DITEMUKAN!")

# --- MODUL 2: REKAP PARKIR ---
elif modul == "REKAP PARKIR":
    menu_p = st.sidebar.radio("MENU PARKIR:", ["INPUT HARIAN", "VERIFIKASI TERIMA"])
    df_p = conn.read(worksheet="LOG_PARKIR", ttl=0).astype(str)

    if menu_p == "INPUT HARIAN":
        st.header("🅿️ INPUT LAPORAN PARKIR HARIAN")
        try:
            sisa_r2_lalu = int(float(df_p['SISA_R2'].iloc[-1]))
            sisa_r4_lalu = int(float(df_p['SISA_R4'].iloc[-1]))
        except:
            sisa_r2_lalu = 0; sisa_r4_lalu = 0

        st.info(f"📊 SALDO KARCIS SAAT INI: R2: **{sisa_r2_lalu}** | R4: **{sisa_r4_lalu}**")

        with st.form("form_parkir", clear_on_submit=True):
            col1, col2 = st.columns(2)
            tgl = col1.date_input("TANGGAL LAPORAN")
            petugas = col2.text_input("NAMA PETUGAS").upper()
            
            st.write("---")
            c3, c4 = st.columns(2)
            with c3:
                st.subheader("🎟️ PENGAMBILAN BARU")
                ambil_r2 = st.number_input("AMBIL R2", min_value=0, step=1)
                ambil_r4 = st.number_input("AMBIL R4", min_value=0, step=1)
            with c4:
                st.subheader("🏙️ PARKIR KHUSUS")
                khusus_r2 = st.number_input("KHUSUS R2", min_value=0, step=1)
                khusus_r4 = st.number_input("KHUSUS R4", min_value=0, step=1)
            
            st.subheader("🏢 PARKIR MPP")
            c5, c6 = st.columns(2)
            mpp_r2 = c5.number_input("MPP R2", min_value=0, step=1)
            mpp_r4 = c6.number_input("MPP R4", min_value=0, step=1)
            
            if st.form_submit_button("💾 SIMPAN REKAP PARKIR"):
                total_pakai_r2 = khusus_r2 + mpp_r2
                total_pakai_r4 = khusus_r4 + mpp_r4
                sisa_baru_r2 = sisa_r2_lalu + ambil_r2 - total_pakai_r2
                sisa_baru_r4 = sisa_r4_lalu + ambil_r4 - total_pakai_r4
                
                new_data = {
                    "TANGGAL": tgl.strftime("%d/%m/%Y"), "NAMA": petugas,
                    "AMBIL_R2": ambil_r2, "KHUSUS_R2": khusus_r2, "MPP_R2": mpp_r2,
                    "AMBIL_R4": ambil_r4, "KHUSUS_R4": khusus_r4, "MPP_R4": mpp_r4,
                    "SISA_R2": sisa_baru_r2, "SISA_R4": sisa_baru_r4, "STATUS_TERIMA": "BELUM"
                }
                df_up = pd.concat([df_p, pd.DataFrame([new_data])], ignore_index=True)
                conn.update(worksheet="LOG_PARKIR", data=df_up)
                st.success("✅ DATA PARKIR TERSIMPAN!")
                st.cache_data.clear()

    elif menu_p == "VERIFIKASI TERIMA":
        st.header("✅ VERIFIKASI PENERIMAAN")
        df_pending = df_p[df_p['STATUS_TERIMA'] == "BELUM"]
        if df_pending.empty:
            st.success("SEMUA SUDAH BERES!")
        else:
            st.table(df_pending[['TANGGAL', 'NAMA', 'SISA_R2', 'SISA_R4']])
            tgl_verif = st.selectbox("PILIH TANGGAL:", df_pending['TANGGAL'].unique())
            if st.button("SAYA SUDAH TERIMA SETORAN"):
                df_p.loc[df_p['TANGGAL'] == tgl_verif, 'STATUS_TERIMA'] = "SUDAH"
                conn.update(worksheet="LOG_PARKIR", data=df_p)
                st.cache_data.clear()
                st.rerun()
