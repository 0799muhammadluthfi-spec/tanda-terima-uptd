import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UPTD PASAR KANDANGAN", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI FORMAT TANGGAL INDO ---
def format_tgl_indo(tgl_input):
    if not tgl_input or tgl_input == "-" or str(tgl_input).lower() == "nan": return ""
    try:
        dt = pd.to_datetime(tgl_input, dayfirst=True)
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.day:02d}-{dt.month:02d}-{dt.year}"
    except: return str(tgl_input).upper()

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🗂️ DASHBOARD UPTD")
modul = st.sidebar.selectbox("PILIH MODUL:", ["SK MENEMPATI TOKO", "REKAP PARKIR"])

# ---------------------------------------------------------
# MODUL 1: SK MENEMPATI TOKO (KODE LAMA BAPAK)
# ---------------------------------------------------------
if modul == "SK MENEMPATI TOKO":
    menu_sk = st.sidebar.radio("MENU SK:", ["PENGANTARAN", "PENGAMBILAN"])
    # Mengambil data dari tab DATA_SK
    df_sk = conn.read(worksheet="DATA_SK", ttl=60).astype(str).replace("nan", "-")
    
    if menu_sk == "PENGANTARAN":
        st.header("📝 PENGANTARAN BERKAS SK")
        # ... (Gunakan logika input pengantaran Bapak yang sebelumnya di sini) ...
        st.info("MODUL PENGANTARAN BERKAS SIAP.")

    elif menu_sk == "PENGAMBILAN":
        st.header("🏁 PENGAMBILAN BERKAS (OVERPRINT)")
        # ... (Gunakan logika cari no urut & overprint Bapak di sini) ...
        st.info("MODUL PENGAMBILAN BERKAS SIAP.")

# ---------------------------------------------------------
# MODUL 2: REKAP PARKIR (MODUL BARU)
# ---------------------------------------------------------
elif modul == "REKAP PARKIR":
    menu_p = st.sidebar.radio("MENU PARKIR:", ["INPUT HARIAN", "VERIFIKASI TERIMA"])
    # Mengambil data dari tab LOG_PARKIR
    df_p = conn.read(worksheet="LOG_PARKIR", ttl=0).astype(str)

    if menu_p == "INPUT HARIAN":
        st.header("🅿️ INPUT LAPORAN PARKIR HARIAN")
        
        # Ambil saldo sisa karcis terakhir secara otomatis
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
                # HITUNG OTOMATIS SEPERTI RUMUS EXCEL BAPAK
                total_pakai_r2 = khusus_r2 + mpp_r2
                total_pakai_r4 = khusus_r4 + mpp_r4
                
                sisa_baru_r2 = sisa_r2_lalu + ambil_r2 - total_pakai_r2
                sisa_baru_r4 = sisa_r4_lalu + ambil_r4 - total_pakai_r4
                
                new_data = {
                    "TANGGAL": tgl.strftime("%d/%m/%Y"),
                    "NAMA": petugas,
                    "AMBIL_R2": ambil_r2, "KHUSUS_R2": khusus_r2, "MPP_R2": mpp_r2,
                    "AMBIL_R4": ambil_r4, "KHUSUS_R4": khusus_r4, "MPP_R4": mpp_r4,
                    "SISA_R2": sisa_baru_r2, "SISA_R4": sisa_baru_r4,
                    "STATUS_TERIMA": "BELUM"
                }
                
                df_up = pd.concat([df_p, pd.DataFrame([new_data])], ignore_index=True)
                conn.update(worksheet="LOG_PARKIR", data=df_up)
                st.success(f"✅ DATA TANGGAL {tgl.strftime('%d/%m/%Y')} TERSIMPAN!")
                st.cache_data.clear()

    elif menu_p == "VERIFIKASI TERIMA":
        st.header("✅ VERIFIKASI PENERIMAAN KARCIS")
        df_pending = df_p[df_p['STATUS_TERIMA'] == "BELUM"]
        
        if df_pending.empty:
            st.success("TIDAK ADA TUNGGAKAN. SEMUA KARCIS SUDAH DITERIMA.")
        else:
            st.write(f"ADA **{len(df_pending)}** DATA YANG BELUM ANDA TERIMA:")
            st.table(df_pending[['TANGGAL', 'NAMA', 'SISA_R2', 'SISA_R4']])
            
            tgl_verif = st.selectbox("PILIH TANGGAL UNTUK DIVERIFIKASI:", df_pending['TANGGAL'].unique())
            if st.button("SAYA SUDAH TERIMA KARCIS & SETORAN TANGGAL INI"):
                df_p.loc[df_p['TANGGAL'] == tgl_verif, 'STATUS_TERIMA'] = "SUDAH"
                conn.update(worksheet="LOG_PARKIR", data=df_p)
                st.cache_data.clear()
                st.success("VERIFIKASI BERHASIL!")
                st.rerun()
