import streamlit as st
import pandas as pd
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os

# ==========================================
# 1. PAGE CONFIG & THEME (VITE STYLE)
# ==========================================
st.set_page_config(page_title="UPTD Pasar Kandangan", page_icon="🏪", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f7fa; }
    [data-testid="stSidebar"] { background-color: #1e3a5f; border-right: 1px solid #d0d7e2; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Card/Container Style */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r {
        background-color: white; padding: 25px; border-radius: 12px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #1e3a5f !important; font-weight: 700 !important; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; }
    
    /* Simple Animation */
    .main .block-container { animation: fadeIn 0.4s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONNECTION & HELPERS
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)
EMPTY_VALUES = {"nan", "None", "", "null", "NaN", "<NA>", "-"}

def format_tgl_hari_indo(tgl_str: str) -> str:
    if not tgl_str or tgl_str.strip() in EMPTY_VALUES: return ""
    try:
        tgl_b = tgl_str.strip().replace("/", "-")
        fmt = "%d-%m-%y" if len(tgl_b.split("-")[-1]) == 2 else "%d-%m-%Y"
        dt = datetime.strptime(tgl_b, fmt)
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except: return str(tgl_str).upper()

def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        df = df.astype(str).replace(r"\.0$", "", regex=True)
        for col in df.columns: df[col] = df[col].str.strip()
        df = df.replace(list(EMPTY_VALUES), "-")
        return df
    except Exception as e:
        st.error(f"Gagal baca: {e}"); return pd.DataFrame()

def safe_update(worksheet: str, data: pd.DataFrame) -> bool:
    try:
        if "Tgl_DT" in data.columns: data = data.drop(columns=["Tgl_DT"])
        if "Tgl_Temp" in data.columns: data = data.drop(columns=["Tgl_Temp"])
        conn.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal simpan: {e}"); return False

# ==========================================
# 3. PDF GENERATOR
# ==========================================
def buat_pdf_sk(data: dict, berkas_pilihan: list) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm))
    M = 0.75*cm; BOX_H = 10.5*cm; Y = (33*cm - BOX_H) - M; MID = 10.75*cm
    c.setLineWidth(1.5); c.rect(M, Y, 20*cm, BOX_H); c.rect(M+0.15*cm, Y+0.15*cm, 19.7*cm, BOX_H-0.3*cm)
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(MID, Y+9.3*cm, "TANDA TERIMA BERKAS IZIN TOKO")
    
    # Isi Berkas
    y_text = Y + 8.2*cm
    c.setFont("Helvetica-Bold", 9); c.drawString(M+1*cm, y_text, "BERKAS YANG DITERIMA:")
    y_text -= 0.7*cm
    berkas_master = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for item in berkas_master:
        c.setFont("Helvetica", 9)
        status = "[X]" if item in berkas_pilihan else "[  ]"
        c.drawString(M+1.5*cm, y_text, f"{status} {item}")
        y_text -= 0.6*cm
    
    # Tanda Tangan
    c.drawCentredString(M+5*cm, Y+0.6*cm, f"( {data.get('Nama_Pengantar_Berkas','')} )")
    c.drawCentredString(M+15*cm, Y+0.6*cm, f"( {data.get('Penerima_Berkas','')} )")
    c.showPage(); c.save(); buffer.seek(0); return buffer

# ==========================================
# 4. MODUL SK TOKO
# ==========================================
def modul_sk(menu):
    st.title(f"📄 SK TOKO - {menu}")
    df_sk = load_data("DATA_SK")
    
    if menu == "PENGANTARAN":
        # Form Checkbox Berkas (Ini yang tadi hilang)
        st.subheader("☑️ Ceklis Berkas")
        berkas_master = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
        col_b1, col_b2 = st.columns(2)
        sel_berkas = []
        for i, b in enumerate(berkas_master):
            with col_b1 if i < 3 else col_b2:
                if st.checkbox(b, key=f"sk_{b}"): sel_berkas.append(b)

        with st.form("form_sk", clear_on_submit=True):
            c1, c2 = st.columns(2)
            no_u = c1.text_input("NOMOR URUT", value=str(len(df_sk[df_sk['No']!='-'])+1))
            tgl_t = c1.text_input("TANGGAL TERIMA", value=datetime.now().strftime("%d-%m-%Y"))
            toko = c1.text_input("NAMA TOKO").upper()
            asli = c2.text_input("NAMA PEMILIK SK").upper()
            antar = c2.text_input("PENGANTAR").upper()
            terima = c2.text_input("PENERIMA").upper()
            
            if st.form_submit_button("💾 SIMPAN & CETAK", type="primary"):
                new_row = {"No": no_u, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", "Nama_Toko": toko, "Nama_Pemilik_Asli": asli, "Nama_Pengantar_Berkas": antar, "Penerima_Berkas": terima}
                if safe_update("DATA_SK", pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)):
                    st.success("Berhasil!"); st.session_state["last_sk_pdf"] = buat_pdf_sk(new_row, sel_berkas); st.rerun()
        
        if "last_sk_pdf" in st.session_state:
            st.download_button("📥 Download PDF Tanda Terima", st.session_state["last_sk_pdf"], "TT_SK.pdf")

    # Log Data di bawah
    st.divider(); st.write("📊 10 DATA TERAKHIR")
    st.dataframe(df_sk.sort_index(ascending=False).head(10), hide_index=True, use_container_width=True)

# ==========================================
# 5. MODUL PARKIR
# ==========================================
def modul_parkir(menu):
    st.title(f"🚗 PARKIR - {menu}")
    df_p = load_data("DATA_PARKIR")
    
    tgl_user = st.text_input("📅 TANGGAL (dd-mm-yyyy):", value=datetime.now().strftime("%d-%m-%Y"))
    df_p["Tgl_DT"] = pd.to_datetime(df_p["Tanggal"], dayfirst=True, errors="coerce").dt.date
    try: tgl_obj = datetime.strptime(tgl_user, "%d-%m-%Y").date()
    except: st.error("Format tanggal salah!"); return
    
    baris = df_p[df_p["Tgl_DT"] == tgl_obj]
    
    if menu == "INPUT REKAP" and not baris.empty:
        idx = baris.index[0]; petugas = baris.iloc[0]["Nama_Petugas"]
        st.info(f"👤 Petugas: **{petugas}**")
        
        with st.form("rekap_p"):
            c1, c2 = st.columns(2)
            tr2 = c1.number_input("R2 TERJUAL", 0); mr2 = c1.number_input("R2 MPP", 0)
            tr4 = c2.number_input("R4 TERJUAL", 0); mr4 = c2.number_input("R4 MPP", 0)
            
            # Cek jika data sudah ada (Anti Timpa Tanpa Izin)
            if st.form_submit_button("💾 SIMPAN REKAP", type="primary"):
                if str(df_p.loc[idx, "Total_Karcis_R2"]) != "-":
                    st.error("⚠️ Data sudah ada di tanggal ini! Silakan hapus di Sheets dulu jika salah.")
                else:
                    df_p.loc[idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Khusus_Roda_R2"]] = [str(tr2), str(mr2), str(tr2-mr2)]
                    df_p.loc[idx, ["Total_Karcis_R4", "MPP_Roda_R4", "Khusus_Roda_R4"]] = [str(tr4), str(mr4), str(tr4-mr4)]
                    df_p.loc[idx, ["Status_Khusus", "Status_MPP", "Status_Cetak"]] = ["BELUM", "BELUM", "BELUM"]
                    if safe_update("DATA_PARKIR", df_p): st.success("Data masuk!"); st.rerun()

    elif menu == "KONFIRMASI":
        # Logika Filter Konfirmasi kita yang lama
        df_pen = df_p[df_p["Total_Karcis_R2"] != "-"].copy()
        for i, row in df_pen.sort_index(ascending=False).head(10).iterrows():
            with st.expander(f"📦 {row['Tanggal']} - {row['Nama_Petugas']}"):
                if st.button("Terima Khusus", key=f"k_{i}"):
                    df_p.loc[i, "Status_Khusus"] = "SUDAH"; safe_update("DATA_PARKIR", df_p); st.rerun()
    
    st.divider(); st.write("📊 LOG PARKIR")
    st.dataframe(df_p[df_p["Total_Karcis_R2"] != "-"].sort_index(ascending=False).head(10), hide_index=True)

# ==========================================
# 6. RUNNER
# ==========================================
def main():
    with st.sidebar:
        st.title("🏪 UPTD PASAR")
        modul = st.selectbox("MODUL:", ["SK TOKO", "PARKIR"])
        st.divider()
        if modul == "SK TOKO": menu = st.radio("MENU:", ["PENGANTARAN", "PENGAMBILAN"])
        else: menu = st.radio("MENU:", ["INPUT REKAP", "INPUT STOK", "KONFIRMASI"])
        if st.button("🔄 REFRESH DATA"): st.cache_data.clear(); st.rerun()

    if modul == "SK TOKO": modul_sk(menu)
    else: modul_parkir(menu)

if __name__ == "__main__":
    main()
