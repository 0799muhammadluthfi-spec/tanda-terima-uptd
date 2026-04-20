import streamlit as st
import pandas as pd
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os

# ==========================================
# 1. THEME & CSS (VITE INTERFACE STYLE)
# ==========================================
st.set_page_config(page_title="UPTD Pasar Kandangan", page_icon="🏪", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f7fa; }
    [data-testid="stSidebar"] { background-color: #1e3a5f; border-right: 1px solid #d0d7e2; }
    [data-testid="stSidebar"] * { color: white !important; }
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r { 
        background-color: white; padding: 20px; border-radius: 12px; 
        border: 1px solid #d0d7e2; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #1e3a5f !important; font-weight: 700 !important; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    .main .block-container { animation: fadeIn 0.4s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI HELPER & DATABASE
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        for col in df.columns: df[col] = df[col].str.strip()
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")
        if worksheet == "DATA_PARKIR" and not df.empty:
            if "Status_Cetak" not in df.columns:
                df["Status_Cetak"] = "BELUM"
                conn.update(worksheet=worksheet, data=df)
                st.cache_data.clear()
        return df
    except Exception as e:
        st.error(f"Gagal baca: {e}"); return pd.DataFrame()

def safe_update(worksheet: str, data: pd.DataFrame) -> bool:
    try:
        conn.update(worksheet=worksheet, data=data)
        st.cache_data.clear(); return True
    except Exception as e:
        st.error(f"Gagal simpan: {e}"); return False

def format_tgl_hari_indo(tgl_str):
    if not tgl_str or tgl_str in ["-", "nan", ""]: return ""
    try:
        tgl_b = str(tgl_str).strip().replace('/', '-')
        dt = datetime.strptime(tgl_b, "%d-%m-%y") if len(tgl_b.split('-')[-1]) == 2 else datetime.strptime(tgl_b, "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except: return str(tgl_str).upper()

# ==========================================
# 3. LOGIKA PDF
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm))
    M = 0.75*cm; TINGGI_P = 12*cm; Y_BASE = (33*cm - TINGGI_P) + M; TENGAH = 10.75*cm
    c.setLineWidth(1.5); c.rect(M, Y_BASE, 20*cm, 10.5*cm); c.rect(M+0.15*cm, Y_BASE+0.15*cm, 19.7*cm, 10.2*cm)
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(TENGAH, Y_BASE+9.3*cm, "TANDA TERIMA BERKAS IZIN TOKO")
    yy = Y_BASE + 8.0*cm
    for i, item in enumerate(["SK ASLI", "FOTO 3X4", "FC KTP", "FC SEWA", "KUASA", "HILANG"], 1):
        c.setFont("Helvetica-Bold", 9); c.drawString(M+1*cm, yy, f"{i}. {item}"); yy -= 0.7*cm
    c.drawCentredString(M+5*cm, Y_BASE+0.6*cm, f"({data.get('Nama_Pengantar_Berkas','')})"); c.drawCentredString(M+15*cm, Y_BASE+0.6*cm, f"({data.get('Penerima_Berkas','')})")
    c.showPage(); c.save(); buffer.seek(0); return buffer

def cetak_tanda_terima_parkir(data):
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm))
    c.setFont("Helvetica-Bold", 7); c.drawCentredString(10.75*cm, 31.5*cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.setFont("Helvetica", 6); c.drawString(7.5*cm, 30.5*cm, f"Tgl: {data['Tanggal']} | Petugas: {data['Nama_Petugas']}")
    c.save(); buffer.seek(0); return buffer

def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm)); c.setFont("Helvetica-Bold", 10)
    c.drawString(7.75*cm, 29.3*cm, format_tgl_hari_indo(tgl_ambil).upper()); c.save(); buffer.seek(0); return buffer

# ==========================================
# 4. MODUL SK TOKO
# ==========================================
def halaman_sk(menu):
    st.title(f"{'📝' if menu == 'PENGANTARAN' else '📤'} SK TOKO - {menu}")
    df_sk = load_data("DATA_SK")
    
    if menu == "PENGANTARAN":
        with st.form("form_sk"):
            c1, c2 = st.columns(2)
            with c1:
                no_u = st.text_input("NOMOR URUT", value=str(len(df_sk[df_sk['No']!='-'])+1))
                tgl_t = st.text_input("TANGGAL TERIMA", value=datetime.now().strftime("%d-%m-%Y"))
                toko = st.text_input("NAMA TOKO").upper()
                noto = st.text_input("NO TOKO").upper()
            with c2:
                asli = st.text_input("NAMA PEMILIK SK").upper()
                antar = st.text_input("NAMA PENGANTAR").upper()
                terima = st.text_input("PENERIMA BERKAS").upper()
            if st.form_submit_button("💾 SIMPAN DATA", type="primary"):
                is_exist = no_u in df_sk["No"].values
                new_row = {"No": no_u, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", "Nama_Toko": toko, "No_Toko": noto, "Nama_Pemilik_Asli": asli, "Nama_Pengantar_Berkas": antar, "Penerima_Berkas": terima}
                if is_exist: st.warning("Nomor sudah ada! Gunakan fitur timpa jika perlu."); st.session_state["pending_sk"] = new_row
                else:
                    if safe_update("DATA_SK", pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)): st.success("Berhasil!"); st.rerun()
    else:
        no_cari = st.text_input("🔍 CARI NOMOR URUT BERKAS:").strip()
        if no_cari:
            res = df_sk[df_sk["No"] == no_cari]
            if not res.empty:
                data = res.iloc[0]
                if data["Tanggal_Pengambilan"] != "-":
                    st.success(f"Sudah diambil: {data['Tanggal_Pengambilan']}")
                    st.download_button("🖨️ PRINT ULANG", data=cetak_overprint(data['Tanggal_Pengambilan']), file_name=f"AMBIL_{no_cari}.pdf")
                else:
                    tgl_a = st.text_input("TANGGAL AMBIL", value=datetime.now().strftime("%d-%m-%Y"))
                    if st.button("✅ KONFIRMASI AMBIL"):
                        df_sk.loc[df_sk["No"] == no_cari, "Tanggal_Pengambilan"] = tgl_a
                        if safe_update("DATA_SK", df_sk): st.rerun()

# ==========================================
# 5. MODUL PARKIR
# ==========================================
def halaman_parkir(menu):
    st.title(f"🚗 PARKIR - {menu}")
    df_p = load_data("DATA_PARKIR")
    tgl_user = st.text_input("📅 TANGGAL:", value=datetime.now().strftime("%d-%m-%Y"))
    
    try:
        df_p['Tgl_DT'] = pd.to_datetime(df_p['Tanggal'], dayfirst=True, errors='coerce').dt.date
        tgl_obj = datetime.strptime(tgl_user, "%d-%m-%Y").date()
        baris = df_p[df_p['Tgl_DT'] == tgl_obj]
    except: baris = pd.DataFrame()

    if baris.empty and menu != "KONFIRMASI": st.warning("Jadwal tidak ditemukan."); return

    if not baris.empty:
        idx = baris.index[0]; petugas = baris.iloc[0]["Nama_Petugas"]
        # Logika Sisa Karcis Per-Petugas
        df_prev = df_p[(df_p["Nama_Petugas"] == petugas) & (df_p.index < idx)]
        sisa2 = pd.to_numeric(df_prev.iloc[-1]["Sisa_Stok_R2"], errors='coerce') if not df_prev.empty else 0
        sisa4 = pd.to_numeric(df_prev.iloc[-1]["Sisa_Stok_R4"], errors='coerce') if not df_prev.empty else 0

        if menu == "INPUT REKAP":
            st.info(f"Petugas: {petugas} | Sisa R2: {int(sisa2)} | Sisa R4: {int(sisa4)}")
            with st.form("rekap", clear_on_submit=True):
                tr2 = st.number_input("TERJUAL R2", 0); mr2 = st.number_input("MPP R2", 0)
                tr4 = st.number_input("TERJUAL R4", 0); mr4 = st.number_input("MPP R4", 0)
                if st.form_submit_button("💾 SIMPAN"):
                    pk2 = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R2"], errors='coerce') or 0
                    pk4 = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R4"], errors='coerce') or 0
                    df_p.loc[idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [str(tr2), str(mr2), str((pk2+sisa2)-tr2), str(tr2-mr2)]
                    df_p.loc[idx, ["Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [str(tr4), str(mr4), str((pk4+sisa4)-tr4), str(tr4-mr4)]
                    df_p.loc[idx, ["Status_Khusus", "Status_MPP", "Status_Cetak"]] = ["BELUM", "BELUM", "BELUM"]
                    if safe_update("DATA_PARKIR", df_p.drop(columns=['Tgl_DT'])): st.rerun()

        elif menu == "INPUT STOK":
            with st.form("stok", clear_on_submit=True):
                p2 = st.number_input("STOK BARU R2", 0); p4 = st.number_input("STOK BARU R4", 0)
                c1, c2 = st.columns(2)
                if c1.form_submit_button("➕ TAMBAH"):
                    df_p.loc[idx, ["Pengambilan_Karcis_R2", "Pengambilan_Karcis_R4"]] = [str(p2), str(p4)]
                    if safe_update("DATA_PARKIR", df_p.drop(columns=['Tgl_DT'])): st.rerun()
                if c2.form_submit_button("🔄 RESET"): st.rerun()

    if menu == "KONFIRMASI":
        df_pen = df_p[df_p["Total_Karcis_R2"].str.isnumeric()].copy()
        df_pen['Tgl_DT'] = pd.to_datetime(df_pen['Tanggal'], dayfirst=True, errors='coerce').dt.date
        hari_ini = date.today()
        # Logika Sembunyi: Jika lunas dan bukan hari ini, maka hilang.
        df_show = df_pen[(df_pen["Status_Cetak"] != "SUDAH") | (df_pen["Tgl_DT"] == hari_ini)]
        for i, row in df_show.sort_index(ascending=False).iterrows():
            lunas = (row["Status_Khusus"] == "SUDAH") and (row["Status_MPP"] == "SUDAH") and (row["Status_Cetak"] == "SUDAH")
            with st.expander(f"{'✅' if lunas else '📦'} {row['Tanggal']} - {row['Nama_Petugas']}"):
                if st.button("TERIMA KHUSUS", key=f"k{i}"): 
                    df_p.loc[i, "Status_Khusus"] = "SUDAH"
                    safe_update("DATA_PARKIR", df_p.drop(columns=['Tgl_DT', 'Tgl_Temp'], errors='ignore')); st.rerun()
                if st.button("TERIMA MPP", key=f"m{i}"):
                    df_p.loc[i, "Status_MPP"] = "SUDAH"
                    safe_update("DATA_PARKIR", df_p.drop(columns=['Tgl_DT', 'Tgl_Temp'], errors='ignore')); st.rerun()
                st.download_button("🖨️ PRINT", data=cetak_tanda_terima_parkir(row), file_name="MPP.pdf", key=f"p{i}")
                if st.button("✅ SELESAI CETAK", key=f"c{i}"):
                    df_p.loc[i, "Status_Cetak"] = "SUDAH"
                    safe_update("DATA_PARKIR", df_p.drop(columns=['Tgl_DT', 'Tgl_Temp'], errors='ignore')); st.rerun()

# ==========================================
# 6. MAIN APP
# ==========================================
def main():
    with st.sidebar:
        st.markdown("<h2 style='color:white;'>🏪 UPTD PASAR</h2>", unsafe_allow_html=True)
        modul = st.selectbox("MODUL:", ["SK TOKO", "PARKIR"], key="main_mod")
        st.divider()
        if modul == "SK TOKO": menu = st.radio("MENU:", ["PENGANTARAN", "PENGAMBILAN"], key="sk_m")
        else: menu = st.radio("MENU:", ["INPUT REKAP", "INPUT STOK", "KONFIRMASI"], key="pk_m")
        if st.button("🔄 REFRESH SEMUA"): st.cache_data.clear(); st.rerun()

    if modul == "SK TOKO": halaman_sk(menu)
    else: halaman_parkir(menu)

if __name__ == "__main__":
    main()
