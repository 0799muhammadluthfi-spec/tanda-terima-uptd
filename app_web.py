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
                        st.success("✅ Berhasil Disimpan!"); st.session_state["last_sk_pdf"] = buat_pdf_sk(new_row, sel_berkas)

        if "last_sk_pdf" in st.session_state:
            st.download_button("📥 Download PDF Tanda Terima", st.session_state["last_sk_pdf"], "TT_SK.pdf")

    else:
        no_cari = st.text_input("🔍 CARI NOMOR URUT BERKAS:").strip()
        if no_cari:
            res = df_sk[df_sk["No"] == no_cari]
            if not res.empty:
                data = res.iloc[0]
                st.info(f"Toko: {data['Nama_Toko']} | Pemilik: {data['Nama_Pemilik_Asli']}")
                if data["Tanggal_Pengambilan"] != "-":
                    st.success(f"✅ Sudah diambil: {data['Tanggal_Pengambilan']}")
                    st.download_button("🖨️ Print Ulang Overprint", data=cetak_overprint(data['Tanggal_Pengambilan']), file_name=f"AMBIL_{no_cari}.pdf")
                else:
                    tgl_a = st.text_input("TANGGAL PENGAMBILAN", value=datetime.now().strftime("%d-%m-%Y"))
                    if st.button("✅ KONFIRMASI PENGAMBILAN"):
                        df_sk.loc[df_sk["No"] == no_cari, "Tanggal_Pengambilan"] = tgl_a
                        if safe_update("DATA_SK", df_sk): st.success("Status Berhasil Diubah!"); st.rerun()

    st.divider(); st.subheader("📊 10 Data Terakhir")
    st.dataframe(df_sk.sort_index(ascending=False).head(10), hide_index=True, use_container_width=True)

# ==========================================
# 5. MODUL PARKIR
# ==========================================
def halaman_parkir(menu):
    st.header(f"🚗 PARKIR - {menu}")
    df_p = load_data("DATA_PARKIR")
    
    tgl_user = st.text_input("📅 TANGGAL (dd-mm-yyyy):", value=datetime.now().strftime("%d-%m-%Y"))
    df_p["Tgl_DT"] = pd.to_datetime(df_p["Tanggal"], dayfirst=True, errors="coerce").dt.date
    try: tgl_obj = datetime.strptime(tgl_user, "%d-%m-%Y").date()
    except: st.error("Format tanggal salah!"); return
    
    baris = df_p[df_p["Tgl_DT"] == tgl_obj]
    if baris.empty and menu != "KONFIRMASI":
        st.warning("⚠️ Jadwal Petugas untuk tanggal ini belum ada di Sheets."); return

    if not baris.empty:
        idx = baris.index[0]; petugas = baris.iloc[0]["Nama_Petugas"]
        
        # LOGIKA SISA KARCIS OTOMATIS
        df_prev = df_p[(df_p["Nama_Petugas"] == petugas) & (df_p.index < idx)]
        s_r2 = pd.to_numeric(df_prev.iloc[-1]["Sisa_Stok_R2"], errors='coerce') if not df_prev.empty else 0
        s_r4 = pd.to_numeric(df_prev.iloc[-1]["Sisa_Stok_R4"], errors='coerce') if not df_prev.empty else 0
        s_r2, s_r4 = (0 if pd.isna(x) else x for x in (s_r2, s_r4))

        if menu == "INPUT REKAP":
            st.info(f"👤 Petugas: **{petugas}** | Sisa Kemarin R2: **{int(s_r2)}** | R4: **{int(s_r4)}**")
            with st.form("rekap_p", clear_on_submit=True):
                c1, c2 = st.columns(2)
                tr2 = c1.number_input("R2 TERJUAL HARI INI", 0); mr2 = c1.number_input("R2 MPP", 0)
                tr4 = c2.number_input("R4 TERJUAL HARI INI", 0); mr4 = c2.number_input("R4 MPP", 0)
                
                if st.form_submit_button("💾 SIMPAN REKAP", type="primary"):
                    if str(df_p.loc[idx, "Total_Karcis_R2"]) != "-":
                        st.error("⚠️ Data tanggal ini sudah pernah diisi!")
                    else:
                        pk2 = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R2"], errors='coerce') or 0
                        pk4 = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R4"], errors='coerce') or 0
                        
                        df_p.loc[idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [str(tr2), str(mr2), str(int((pk2+s_r2)-tr2)), str(tr2-mr2)]
                        df_p.loc[idx, ["Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [str(tr4), str(mr4), str(int((pk4+s_r4)-tr4)), str(tr4-mr4)]
                        df_p.loc[idx, ["Status_Khusus", "Status_MPP", "Status_Cetak"]] = ["BELUM", "BELUM", "BELUM"]
                        
                        if safe_update("DATA_PARKIR", df_p): st.success("✅ Berhasil Diupdate!"); st.rerun()

        elif menu == "INPUT STOK":
            st.subheader("📦 Update Stok Baru")
            with st.form("stok_p", clear_on_submit=True):
                p2 = st.number_input("STOK BARU R2", 0); p4 = st.number_input("STOK BARU R4", 0)
                col1, col2 = st.columns(2)
                if col1.form_submit_button("➕ SIMPAN STOK", type="primary"):
                    df_p.loc[idx, ["Pengambilan_Karcis_R2", "Pengambilan_Karcis_R4"]] = [str(p2), str(p4)]
                    if safe_update("DATA_PARKIR", df_p): st.success("✅ Stok Berhasil Ditambah!"); st.rerun()
                if col2.form_submit_button("🔄 RESET"): st.rerun()

    if menu == "KONFIRMASI":
        # FILTER DATA HANTU (Hanya yang ada angkanya)
        df_pen = df_p[df_p["Total_Karcis_R2"].str.isnumeric()].copy()
        if df_pen.empty:
            st.info("Tidak ada antrean konfirmasi.")
        for i, row in df_pen.sort_index(ascending=False).head(10).iterrows():
            lunas = (row["Status_Khusus"] == "SUDAH") and (row["Status_MPP"] == "SUDAH")
            with st.expander(f"{'✅' if lunas else '⏳'} {row['Tanggal']} - {row['Nama_Petugas']}"):
                c1, c2, c3 = st.columns(3)
                if c1.button("Terima Khusus", key=f"k_{i}"):
                    df_p.loc[i, "Status_Khusus"] = "SUDAH"; safe_update("DATA_PARKIR", df_p); st.rerun()
                if c2.button("Terima MPP", key=f"m_{i}"):
                    df_p.loc[i, "Status_MPP"] = "SUDAH"; safe_update("DATA_PARKIR", df_p); st.rerun()
                c3.download_button("🖨️ Cetak MPP", data=cetak_tanda_terima_parkir(row), file_name=f"MPP_{i}.pdf", key=f"p_{i}")

    st.divider(); st.subheader("📊 Log Parkir")
    st.dataframe(df_p[df_p["Total_Karcis_R2"] != "-"].sort_index(ascending=False).head(10), hide_index=True)

# ==========================================
# 6. RUNNER UTAMA
# ==========================================
def main():
    st.sidebar.title("🏪 UPTD PASAR")
    modul = st.sidebar.selectbox("PILIH MODUL:", ["SK TOKO", "PARKIR"])
    st.sidebar.divider()
    
    if modul == "SK TOKO":
        menu = st.sidebar.radio("MENU:", ["PENGANTARAN", "PENGAMBILAN"])
        halaman_sk(menu)
    else:
        menu = st.sidebar.radio("MENU:", ["INPUT REKAP", "INPUT STOK", "KONFIRMASI"])
        halaman_parkir(menu)
    
    st.sidebar.divider()
    if st.sidebar.button("🔄 REFRESH SEMUA"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
