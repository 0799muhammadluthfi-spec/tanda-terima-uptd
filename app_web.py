import streamlit as st
import pandas as pd
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os

# ==========================================
# 1. KONFIGURASI HALAMAN & TAMPILAN (UI/UX)
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SUNTIKAN CSS UNTUK MENIRU TAMPILAN REACT/VITE
st.markdown("""
    <style>
    /* Latar Belakang Utama */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* Styling Sidebar (Biru Tua Vite) */
    [data-testid="stSidebar"] {
        background-color: #1e3a5f !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Styling Card/Kotak Putih */
    div.stBlock {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Judul Modern */
    h1, h2, h3 {
        color: #1e3a5f !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
    }

    /* Metrik/Statistik (Card Atas) */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #1e3a5f;
    }
    [data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* Tombol Biru Modern */
    .stButton>button {
        background-color: #1e3a5f;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2a5282;
        box-shadow: 0 4px 12px rgba(30, 58, 95, 0.2);
    }

    /* Checkbox & Input */
    .stCheckbox label {
        background-color: white;
        padding: 10px 15px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        width: 100%;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def tombol_refresh_pojok(key_btn):
    if st.button("🔄 Refresh Data", key=key_btn, use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 2. FUNGSI HELPER (LOGIKA ASLI TETAP SAMA)
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip()
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")
        if worksheet == "DATA_PARKIR" and not df.empty:
            if "Status_Cetak" not in df.columns:
                df["Status_Cetak"] = "BELUM"
                conn.update(worksheet=worksheet, data=df)
                st.cache_data.clear()
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns: return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except Exception: return 1

def safe_update(worksheet: str, data: pd.DataFrame) -> bool:
    try:
        conn.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")
        return False

def format_tgl_hari_indo(tgl_str):
    if not tgl_str or tgl_str in ["-", "nan", "NAN", ""]: return ""
    try:
        tgl_bersih = str(tgl_str).strip().replace('/', '-')
        if len(tgl_bersih.split('-')[-1]) == 2:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%y")
        else:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()

# ==========================================
# 3. FUNGSI PDF (LOGIKA ASLI TETAP SAMA)
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    UKURAN_KERTAS = (21.5 * cm, 33 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)
    M = 0.75 * cm; TINGGI_POTONG = 12 * cm; Y_POTONG = 33 * cm - TINGGI_POTONG
    Y_BASE = Y_POTONG + M; X_POS = M; LEBAR_BOX = 21.5 * cm - (2 * M); TINGGI_BOX = TINGGI_POTONG - (2 * M); TENGAH = 21.5 * cm / 2
    def gambar_garis_potong():
        c.setLineWidth(1); c.setDash(4, 4); c.line(0, Y_POTONG, 21.5 * cm, Y_POTONG)
        c.setFont("Helvetica-Oblique", 8); c.drawString(0.5 * cm, Y_POTONG + 0.15 * cm, "✂ --- Batas potong ---"); c.setDash()
    gambar_garis_potong(); c.setLineWidth(1.5); c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX) 
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm) 
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(TENGAH, Y_BASE + 9.3 * cm, "TANDA TERIMA BERKAS IZIN TOKO")
    c.setLineWidth(2); c.line(TENGAH - 5.5*cm, Y_BASE + 9.0*cm, TENGAH + 5.5*cm, Y_BASE + 9.0*cm)
    yy = Y_BASE + 8.0 * cm
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(SEMUA_BERKAS, 1):
        c.setFont("Helvetica-BoldOblique", 10); c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10); x_status = X_POS + 14 * cm; c.drawString(x_status, yy, "ADA / TIDAK")
        c.setLineWidth(1.5); y_strike = yy + 0.11 * cm 
        if item in berkas_list: c.line(x_status + 0.8 * cm, y_strike, x_status + 1.8 * cm, y_strike)
        yy -= 0.7 * cm
    c.setLineWidth(1.5); c.line(X_POS + 0.15 * cm, Y_BASE + 3.0 * cm, X_POS + LEBAR_BOX - 0.15 * cm, Y_BASE + 3.0 * cm) 
    c.line(TENGAH, Y_BASE + 0.15 * cm, TENGAH, Y_BASE + 3.0 * cm) 
    c.setFont("Helvetica-Bold", 11); c.drawCentredString(X_POS + 5 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Nama_Pengantar_Berkas', '')).upper()} )"); c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Penerima_Berkas', '')).upper()} )")
    c.save(); buffer.seek(0); return buffer

def cetak_tanda_terima_parkir(data):
    buffer = BytesIO(); lebar_kertas = 21.5 * cm; c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    lebar_box, tinggi_box = 6.8 * cm, 4.6 * cm; x_awal = (lebar_kertas - lebar_box) / 2; center_x = lebar_kertas / 2; y_top = 32 * cm; y_bottom = y_top - tinggi_box
    c.setLineWidth(1.2); c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    tgl_dis = format_tgl_hari_indo(data['Tanggal'])
    c.setFont("Helvetica-Bold", 7); c.drawCentredString(center_x, y_top - 0.5*cm, "UPTD PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6); c.drawCentredString(center_x, y_top - 0.9*cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.save(); buffer.seek(0); return buffer

def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm)); c.setFont("Helvetica-Bold", 10); X_POS = 0.75 * cm
    y_target = 21.5 * cm + 0.75 * cm + 10.35 * cm - (1.05 * cm * 2) - 0.7 * cm
    c.drawString(X_POS + 7.0 * cm, y_target, format_tgl_hari_indo(tgl_ambil).upper()); c.save(); buffer.seek(0); return buffer

# ==========================================
# 4. MODUL SK TOKO (TAMPILAN BARU)
# ==========================================
def halaman_pengantaran():
    st.markdown('<div class="stBlock">', unsafe_allow_html=True)
    c_head, c_btn = st.columns([0.8, 0.2])
    c_head.subheader("📄 Pendaftaran Berkas Izin Toko")
    with c_btn: tombol_refresh_pojok("ref_pengantaran")
    
    df_sk = load_data("DATA_SK")
    total = len(df_sk) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    
    # STATS CARDS (Persis Foto Bapak)
    m1, m2, m3 = st.columns(3)
    m1.metric("📦 Total Berkas", total)
    m2.metric("✅ Sudah Diambil", sudah_ambil)
    m3.metric("⚠️ Belum Diambil", total - sudah_ambil)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stBlock">', unsafe_allow_html=True)
    st.write("**PILIH BERKAS YANG DIBAWA (0/6)**")
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    cols_berkas = st.columns(2)
    sel_berkas = []
    for i, item in enumerate(SEMUA_BERKAS):
        with cols_berkas[i % 2]:
            if st.checkbox(item, key=f"cb_{item}"): sel_berkas.append(item)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("form_pengantaran", clear_on_submit=False):
        st.markdown('**📋 Data Lengkap Pengantaran**')
        next_no = get_next_no(df_sk); col1, col2 = st.columns(2)
        with col1:
            no_urut = st.text_input("NOMOR URUT", value=str(next_no))
            tgl_terima = st.text_input("TANGGAL TERIMA", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = st.text_input("NAMA TOKO").strip().upper()
        with col2:
            no_toko = st.text_input("NOMOR TOKO").strip().upper()
            nama_pemilik = st.text_input("NAMA PEMILIK SK").strip().upper()
            nama_penerima = st.text_input("PENERIMA BERKAS").strip().upper()
        
        nama_pengantar = st.text_input("NAMA PENGANTAR BERKAS").strip().upper()
        
        if st.form_submit_button("📥 SIMPAN & CETAK BERKAS"):
            if not no_urut.strip() or not nama_toko or not nama_pemilik: st.error("❌ Data Wajib Diisi!")
            else:
                is_exist = not df_sk.empty and no_urut.strip() in df_sk["No"].str.strip().values
                new_row = {"No": no_urut.strip(), "Tanggal_Pengantaran": tgl_terima, "Tanggal_Pengambilan": "-", "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": nama_pemilik, "Nama_Pengantar_Berkas": nama_pengantar, "Penerima_Berkas": nama_penerima}
                if is_exist: st.session_state["pending_sk"] = new_row; st.session_state["show_confirm_sk"] = True
                else:
                    df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                    if safe_update("DATA_SK", df_baru): st.session_state["last_sk"] = new_row; st.session_state["last_berkas"] = sel_berkas; st.success("✅ Berhasil!"); st.rerun()

    if "last_sk" in st.session_state:
        l = st.session_state["last_sk"]
        st.download_button("🖨️ CETAK TANDA TERIMA (PDF)", data=buat_pdf_full(l, st.session_state["last_berkas"]), file_name=f"TANDA_{l['No']}.pdf")

def halaman_pengambilan_sk():
    st.markdown('<div class="stBlock">', unsafe_allow_html=True)
    st.subheader("📤 Pengambilan Berkas SK")
    df_m = load_data("DATA_SK")
    no_cari = st.text_input("🔍 CARI NOMOR URUT BERKAS:").strip()
    if no_cari:
        hasil = df_m[df_m["No"].str.strip() == no_cari]
        if not hasil.empty:
            data = hasil.iloc[0]; sudah = data["Tanggal_Pengambilan"] != "-"
            if sudah:
                st.success(f"✅ Sudah diambil pada: {format_tgl_hari_indo(data['Tanggal_Pengambilan'])}")
                st.download_button("🖨️ PRINT ULANG", data=cetak_overprint(data['Tanggal_Pengambilan']), file_name=f"AMBIL_{no_cari}.pdf")
            else:
                st.warning(f"🏪 Toko: {data['Nama_Toko']}"); tgl_a = st.text_input("📅 TANGGAL AMBIL:", value=datetime.now().strftime("%d-%m-%Y"))
                if st.button("✅ KONFIRMASI PENGAMBILAN"):
                    df_m.loc[df_m["No"].str.strip() == no_cari, "Tanggal_Pengambilan"] = tgl_a
                    if safe_update("DATA_SK", df_m): st.success("Berhasil!"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. MODUL PARKIR (TAMPILAN DASHBOARD)
# ==========================================
def halaman_parkir(menu):
    st.markdown(f'<div class="stBlock"><h3>🚗 Parkir - {menu}</h3>', unsafe_allow_html=True)
    df_p = load_data("DATA_PARKIR")
    hari_ini = datetime.now().date()
    tgl_input_user = st.text_input("🔍 MASUKKAN TANGGAL", value=datetime.now().strftime("%d-%m-%Y"))
    
    try:
        tgl_bersih = str(tgl_input_user).strip().replace('/', '-')
        dt_user = datetime.strptime(tgl_bersih, "%d-%m-%y" if len(tgl_bersih.split('-')[-1]) == 2 else "%d-%m-%Y").date()
        df_p['Tgl_Temp'] = pd.to_datetime(df_p['Tanggal'], dayfirst=True, errors='coerce').dt.date
        baris = df_p[df_p['Tgl_Temp'] == dt_user]
    except: baris = pd.DataFrame()

    if baris.empty and menu != "KONFIRMASI":
        st.warning("⚠️ Jadwal belum ada di Sheet."); return

    if not baris.empty:
        idx = baris.index[0]; nama_p = baris.iloc[0]["Nama_Petugas"]
        if menu == "INPUT REKAP":
            st.success(f"👤 PETUGAS: {nama_p}")
            with st.form("form_rekap"):
                c1, c2 = st.columns(2)
                tr2 = c1.number_input("TERJUAL R2", min_value=0)
                mr2 = c1.number_input("MPP R2", min_value=0)
                tr4 = c2.number_input("TERJUAL R4", min_value=0)
                mr4 = c2.number_input("MPP R4", min_value=0)
                if st.form_submit_button("💾 SIMPAN REKAP"):
                    df_p.loc[idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Status_Khusus", "Status_MPP", "Status_Cetak"]] = [str(tr2), str(mr2), "BELUM", "BELUM", "BELUM"]
                    df_p.loc[idx, ["Total_Karcis_R4", "MPP_Roda_R4"]] = [str(tr4), str(mr4)]
                    if safe_update("DATA_PARKIR", df_p.drop(columns=['Tgl_Temp'])): st.success("✅ Berhasil!"); st.rerun()

    if menu == "KONFIRMASI":
        st.write("**Daftar Antrian Konfirmasi**")
        df_pen = df_p[df_p["Total_Karcis_R2"].str.isnumeric()].copy()
        for i, row in df_pen.sort_index(ascending=False).head(5).iterrows():
            with st.expander(f"📦 {row['Tanggal']} - {row['Nama_Petugas']}"):
                col_a, col_b = st.columns(2)
                if col_a.button("Terima Khusus", key=f"k{i}"):
                    df_p.loc[i, "Status_Khusus"] = "SUDAH"
                    safe_update("DATA_PARKIR", df_p.drop(columns=['Tgl_Temp'], errors='ignore')); st.rerun()
                if col_b.button("Cetak MPP", key=f"m{i}"):
                    st.success("PDF Siap Cetak")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. SIDEBAR MODERN (VITE STYLE)
# ==========================================
def main():
    # HEADER SIDEBAR
    st.sidebar.markdown("""
        <div style="padding: 10px; background-color: #2a5282; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0; font-size: 20px;">🏪 UPTD Pasar</h2>
            <p style="color: #cbd5e0; margin: 0; font-size: 12px;">Kandangan, HSS</p>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.write("---")
        st.write("**📂 PILIH MODUL**")
        modul = st.selectbox("", ["SK TOKO", "PARKIR"], label_visibility="collapsed")
        
        st.write("")
        st.write("**🎮 SUB MENU**")
        if modul == "SK TOKO":
            menu = st.radio("", ["Pengantaran", "Pengambilan"], label_visibility="collapsed")
        else:
            menu = st.radio("", ["INPUT REKAP", "INPUT STOK", "KONFIRMASI"], label_visibility="collapsed")
        
        st.write("---")
        st.caption("v1.0 UPTD Pasar Kandangan")

    # ROUTING
    if modul == "SK TOKO":
        if menu == "Pengantaran": halaman_pengantaran()
        else: halaman_pengambilan_sk()
    else:
        halaman_parkir(menu)

if __name__ == "__main__":
    main()
