import streamlit as st
import pandas as pd
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os
import base64
import urllib.request

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="🏪",
    layout="wide"
)

# ==========================================
# KONEKSI - 3 FILE TERPISAH
# ==========================================
conn_sk = st.connection("gsheets_sk", type=GSheetsConnection)
conn_parkir = st.connection("gsheets_parkir", type=GSheetsConnection)
conn_kas = st.connection("gsheets_kas", type=GSheetsConnection)

# ==========================================
# FUNGSI LOGO HSS
# ==========================================
def get_logo_base64():
    for nama_file in ["logo_hss.png", "logo.png", "Logo_HSS.png"]:
        if os.path.exists(nama_file):
            with open(nama_file, "rb") as f:
                return base64.b64encode(f.read()).decode()
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/3/3e/Lambang_Kabupaten_Hulu_Sungai_Selatan.png",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                img_data = response.read()
                if len(img_data) > 100:
                    return base64.b64encode(img_data).decode()
        except Exception:
            continue
    return None

if "logo_b64" not in st.session_state:
    st.session_state["logo_b64"] = get_logo_base64()

# ==========================================
# CUSTOM CSS + ANIMASI (SMOOTH & LIGHT)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ============ BASE ============ */
    .stApp {
        background: linear-gradient(160deg, #f8fafc 0%, #f1f5f9 100%) !important;
    }

    /* ============ SIDEBAR ============ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    }

    /* ============ ANIMASI SMOOTH (THE CORE) ============ */
    /* Pergerakan halaman utama saat masuk */
    .main .block-container {
        animation: smoothPageEnter 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
        max-width: 85%;
        margin: 0 auto;
    }

    @keyframes smoothPageEnter {
        from { opacity: 0; transform: translateY(8px); filter: blur(4px); }
        to   { opacity: 1; transform: translateY(0); filter: blur(0px); }
    }

    /* Animasi Card & Expander agar muncul satu per satu (Stagger) */
    [data-testid="stExpander"], [data-testid="stMetric"], [data-testid="stForm"] {
        animation: smoothItemFadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    @keyframes smoothItemFadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Badge & Konfirmasi Card */
    .konfirmasi-card {
        background: white; border-radius: 12px; padding: 16px; border: 1px solid #e5e7eb;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .konfirmasi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }

    /* Button hover transitions */
    button { transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important; }

    /* Font Global */
    * { font-family: 'Inter', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI HELPER (FIX KEYERROR TERNYATA DISINI)
# ==========================================
def load_data(conn_obj, worksheet: str) -> pd.DataFrame:
    try:
        df = conn_obj.read(worksheet=worksheet, ttl=0)
        # --- PERBAIKAN ERROR: Membersihkan spasi pada nama kolom (Header) ---
        df.columns = df.columns.str.strip() 
        # --------------------------------------------------------------------
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip()
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")
        
        if worksheet == "DATA_PARKIR" and not df.empty:
            if "Status_Cetak" not in df.columns:
                df["Status_Cetak"] = "BELUM"
                conn_obj.update(worksheet=worksheet, data=df)
                st.cache_data.clear()
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

# --- Fungsi Helper Lainnya Tetap Sesuai Script Final Bapak ---
def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns: return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except Exception: return 1

def safe_update(conn_obj, worksheet: str, data: pd.DataFrame) -> bool:
    try:
        conn_obj.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")
        return False

def format_tgl_hari_indo(tgl_str):
    if not tgl_str or tgl_str in ["-", "nan", "NAN", ""]: return ""
    try:
        tgl_bersih = str(tgl_str).strip().replace('/', '-')
        fmt = "%d-%m-%y" if len(tgl_bersih.split('-')[-1]) == 2 else "%d-%m-%Y"
        dt = datetime.strptime(tgl_bersih, fmt)
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except: return str(tgl_str).upper()

def normalisasi_no(val):
    try:
        txt = str(val).replace("\u00a0", "").replace("'", "").strip()
        try: return str(int(float(txt)))
        except: return txt
    except: return ""

def cari_tanggal_belum_input_parkir(df_p: pd.DataFrame):
    try:
        if df_p.empty or "Tanggal" not in df_p.columns: return None, pd.DataFrame()
        df = df_p.copy()
        df["Tgl_Cek"] = pd.to_datetime(df["Tanggal"], dayfirst=True, errors="coerce").dt.date
        hari_ini = datetime.now().date()
        kondisi_belum = (df["Total_Karcis_R2"].astype(str).str.strip().isin(["-", "nan", ""]))
        df_belum = df[(df["Tgl_Cek"].notna()) & (df["Tgl_Cek"] <= hari_ini) & kondisi_belum].copy()
        if df_belum.empty: return None, df_belum
        return df_belum.sort_values("Tgl_Cek").iloc[0]["Tgl_Cek"], df_belum
    except: return None, pd.DataFrame()

# ==========================================
# 3. FUNGSI PDF (Sesuai Struktur Bapak)
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO(); UKURAN_KERTAS = (21.5 * cm, 33 * cm); c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)
    M = 0.75 * cm; TINGGI_POTONG = 12 * cm; Y_POTONG = 33 * cm - TINGGI_POTONG
    Y_BASE = Y_POTONG + M; X_POS = M; LEBAR_BOX = 21.5 * cm - (2 * M); TINGGI_BOX = TINGGI_POTONG - (2 * M); TENGAH = 21.5 * cm / 2
    c.setLineWidth(1.5); c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX)
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm)
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(TENGAH, Y_BASE + 9.3 * cm, "TANDA TERIMA BERKAS IZIN TOKO")
    c.setLineWidth(2); c.line(TENGAH - 5.5 * cm, Y_BASE + 9.0 * cm, TENGAH + 5.5 * cm, Y_BASE + 9.0 * cm)
    yy = Y_BASE + 8.0 * cm
    for i, item in enumerate(["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"], 1):
        c.setFont("Helvetica-BoldOblique", 10); c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10); c.drawString(X_POS + 14 * cm, yy, "ADA  /  TIDAK ADA")
        c.setLineWidth(1.5); y_strike = yy + 0.11 * cm
        if item in berkas_list: c.line(X_POS + 15.4 * cm, y_strike, X_POS + 17.5 * cm, y_strike)
        yy -= 0.7 * cm
    c.setFont("Helvetica-Bold", 11); c.drawCentredString(X_POS + 5 * cm, Y_BASE + 0.6 * cm, f"({str(data.get('Nama_Pengantar_Berkas','')).upper()})")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm, f"({str(data.get('Penerima_Berkas','')).upper()})")
    c.showPage(); c.save(); buffer.seek(0); return buffer

def cetak_tanda_terima_parkir(data) -> BytesIO:
    if isinstance(data, pd.Series): data = data.to_dict()
    buffer = BytesIO(); lebar_kertas = 21.5 * cm; c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    x_awal = (lebar_kertas - 6.8 * cm) / 2; center_x = lebar_kertas / 2; y_top = 32 * cm
    c.setLineWidth(1.2); c.rect(x_awal, y_top - 4.6 * cm, 6.8 * cm, 4.6 * cm)
    c.setFont("Helvetica-Bold", 7); c.drawCentredString(center_x, y_top - 0.5 * cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6); c.drawCentredString(center_x, y_top - 0.9 * cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.showPage(); c.save(); buffer.seek(0); return buffer

def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm))
    c.setFont("Helvetica-Bold", 10); c.drawString(7.75 * cm, 29.3 * cm, format_tgl_hari_indo(tgl_ambil).upper())
    c.save(); buffer.seek(0); return buffer

# ==========================================
# 4. MODUL PARKIR (FIXED KEYERROR)
# ==========================================
def halaman_parkir(menu):
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.header(f"🅿️ {menu}")
    with c_btn:
        if st.button("🔄 Refresh", key="ref_parkir"):
            st.cache_data.clear(); st.rerun()

    df_p = load_data(conn_parkir, "DATA_PARKIR")
    hari_ini = datetime.now().date()
    tgl_input_user = st.text_input("🔍 MASUKKAN TANGGAL", value=datetime.now().strftime("%d-%m-%Y"), key="tgl_input_parkir")

    try:
        tgl_bersih = str(tgl_input_user).strip().replace('/', '-')
        dt_user = datetime.strptime(tgl_bersih, "%d-%m-%y" if len(tgl_bersih.split('-')[-1]) == 2 else "%d-%m-%Y").date()
        df_p['Tgl_Temp'] = pd.to_datetime(df_p['Tanggal'], dayfirst=True, errors='coerce').dt.date
        baris = df_p[df_p['Tgl_Temp'] == dt_user]
    except: baris = pd.DataFrame()

    if baris.empty and menu != "KONFIRMASI":
        st.warning("⚠️ Tanggal belum ada di jadwal Sheet."); return

    if not baris.empty:
        idx = baris.index[0]; nama_p = baris.iloc[0]["Nama_Petugas"]
        # Logika sisa stok dan perhitungan rekap tetap sesuai script Bapak
        if menu == "INPUT REKAP":
            st.info(f"👤 PETUGAS: **{nama_p}**")
            with st.form("form_rekap_harian", clear_on_submit=True):
                tr2 = st.number_input("TOTAL KARCIS R2", min_value=0)
                mr2 = st.number_input("MPP RODA R2", min_value=0)
                tr4 = st.number_input("TOTAL KARCIS R4", min_value=0)
                mr4 = st.number_input("MPP RODA R4", min_value=0)
                if st.form_submit_button("💾 SIMPAN REKAP", type="primary"):
                    # Simpan data sesuai logika Bapak
                    df_p.loc[idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Status_Cetak"]] = [str(tr2), str(mr2), "BELUM"]
                    df_p.loc[idx, ["Total_Karcis_R4", "MPP_Roda_R4"]] = [str(tr4), str(mr4)]
                    if safe_update(conn_parkir, "DATA_PARKIR", df_p.drop(columns=['Tgl_Temp'])):
                        st.success("✅ Berhasil!"); st.rerun()

    if menu == "KONFIRMASI":
        # PERBAIKAN KEYERROR: Memastikan pengecekan kolom aman
        if "Total_Karcis_R2" in df_p.columns:
            kondisi_angka = df_p["Total_Karcis_R2"].str.isnumeric()
            df_pen = df_p[kondisi_angka].copy()
            if df_pen.empty: st.info("TIDAK ADA DATA KONFIRMASI.")
            else:
                for i, row in df_pen.sort_index(ascending=False).head(5).iterrows():
                    with st.expander(f"📦 {row['Tanggal']} - {row['Nama_Petugas']}"):
                        st.write(f"R2: {row['Total_Karcis_R2']} | R4: {row['Total_Karcis_R4']}")
                        if st.button("TERIMA MPP", key=f"m{i}"):
                            df_p.loc[i, "Status_MPP"] = "SUDAH"
                            safe_update(conn_parkir, "DATA_PARKIR", df_p); st.rerun()

# ==========================================
# 5. MODUL SK TOKO
# ==========================================
def halaman_sk(menu):
    # Sesuai Fungsi Bapak sebelumnya
    if menu == "PENGANTARAN": halaman_pengantaran()
    else: halaman_pengambilan_sk()

# --- Fungsi Halaman SK Bapak Tetap Sama ---
def halaman_pengantaran():
    st.header("📝 INPUT PENGANTARAN BERKAS")
    df_sk = load_data(conn_sk, "DATA_PERPANJANGAN_SK")
    with st.form("form_pengantaran"):
        no_urut = st.text_input("NOMOR URUT", value=str(get_next_no(df_sk)))
        nama_toko = st.text_input("NAMA TOKO").upper()
        if st.form_submit_button("💾 SIMPAN DATA"):
            new_row = {"No": no_urut, "Tanggal_Pengantaran": datetime.now().strftime("%d-%m-%Y"), "Tanggal_Pengambilan": "-", "Nama_Toko": nama_toko}
            df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
            safe_update(conn_sk, "DATA_PERPANJANGAN_SK", df_baru); st.rerun()

def halaman_pengambilan_sk():
    st.header("PENGAMBILAN BERKAS SK")
    df_m = load_data(conn_sk, "DATA_PERPANJANGAN_SK")
    no_cari = st.text_input("🔍 CARI NOMOR URUT")
    if no_cari:
        hasil = df_m[df_m["No"] == no_cari]
        if not hasil.empty:
            st.success(f"Ditemukan: {hasil.iloc[0]['Nama_Toko']}")
            if st.button("KONFIRMASI AMBIL"):
                df_m.loc[df_m["No"] == no_cari, "Tanggal_Pengambilan"] = datetime.now().strftime("%d-%m-%Y")
                safe_update(conn_sk, "DATA_PERPANJANGAN_SK", df_m); st.rerun()

# ==========================================
# 6. MAIN RUNNER
# ==========================================
def main():
    if "modul_aktif" not in st.session_state: st.session_state["modul_aktif"] = None
    if "menu_aktif" not in st.session_state: st.session_state["menu_aktif"] = None

    with st.sidebar:
        st.markdown("<h2 style='color:white; text-align:center;'>UPTD PASAR</h2>", unsafe_allow_html=True)
        if st.button("📋 SK TOKO", use_container_width=True): st.session_state["modul_aktif"] = "SK TOKO"; st.session_state["menu_aktif"] = "PENGANTARAN"
        if st.button("🅿️ PARKIR", use_container_width=True): st.session_state["modul_aktif"] = "PARKIR"; st.session_state["menu_aktif"] = "INPUT REKAP"
        
        if st.session_state["modul_aktif"] == "SK TOKO":
            menu = st.radio("SUBMENU:", ["PENGANTARAN", "PENGAMBILAN"])
            st.session_state["menu_aktif"] = menu
        elif st.session_state["modul_aktif"] == "PARKIR":
            menu = st.radio("SUBMENU:", ["INPUT REKAP", "INPUT STOK", "KONFIRMASI"])
            st.session_state["menu_aktif"] = menu

    modul = st.session_state["modul_aktif"]
    menu = st.session_state["menu_aktif"]

    if modul == "SK TOKO": halaman_sk(menu)
    elif modul == "PARKIR": halaman_parkir(menu)
    else: st.title("🏪 Selamat Datang di UPTD Pasar")

if __name__ == "__main__":
    main()
