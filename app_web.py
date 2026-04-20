import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
import os

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="🏪",
    layout="wide"
)
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI HELPER (LOAD, SAVE, FORMAT)
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        # Menghilangkan .0 pada angka dan menangani nilai kosong
        df = df.astype(str).replace(r'\.0$', '', regex=True).replace("nan", "-").replace("None", "-")
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
        # Deteksi format 2 digit atau 4 digit tahun
        if len(tgl_bersih.split('-')[-1]) == 2:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%y")
        else:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()

# ==========================================
# 3. FUNGSI PDF (SK TOKO & PARKIR)
# ==========================================

# --- PDF SK TOKO (F4 PORTRAIT) ---
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    UKURAN_KERTAS = (21.5 * cm, 33 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)
    M = 0.75 * cm; TINGGI_POTONG = 12 * cm; Y_POTONG = 33 * cm - TINGGI_POTONG
    Y_BASE = Y_POTONG + M; X_POS = M; LEBAR_BOX = 21.5 * cm - (2 * M); TINGGI_BOX = TINGGI_POTONG - (2 * M); TENGAH = 21.5 * cm / 2

    def gambar_garis_potong():
        c.setLineWidth(1); c.setDash(4, 4); c.line(0, Y_POTONG, 21.5 * cm, Y_POTONG)
        c.setFont("Helvetica-Oblique", 8); c.drawString(0.5 * cm, Y_POTONG + 0.15 * cm, "✂ --- Batas potong (Tinggi 12 cm) ---"); c.setDash()

    # HALAMAN 1 - DEPAN
    gambar_garis_potong(); c.setLineWidth(1.5); c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX) 
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm) 
    c.setFont("Helvetica-Bold", 13); c.drawCentredString(TENGAH, Y_BASE + 9.3 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    c.setLineWidth(2); c.line(TENGAH - 5.5*cm, Y_BASE + 9.0*cm, TENGAH + 5.5*cm, Y_BASE + 9.0*cm)
    
    yy = Y_BASE + 8.0 * cm
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(SEMUA_BERKAS, 1):
        c.setFont("Helvetica-BoldOblique", 10); c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10); x_status = X_POS + 14 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        c.setLineWidth(1.5); y_strike = yy + 0.11 * cm 
        if item in berkas_list: c.line(x_status + 1.4 * cm, y_strike, x_status + 3.5 * cm, y_strike)
        else: c.line(x_status - 0.1 * cm, y_strike, x_status + 0.8 * cm, y_strike)
        yy -= 0.7 * cm
    
    c.setLineWidth(1.5); c.line(X_POS + 0.15 * cm, Y_BASE + 3.0 * cm, X_POS + LEBAR_BOX - 0.15 * cm, Y_BASE + 3.0 * cm) 
    c.line(TENGAH, Y_BASE + 0.15 * cm, TENGAH, Y_BASE + 3.0 * cm) 
    c.setFont("Helvetica-Bold", 9); c.drawCentredString(X_POS + 5 * cm, Y_BASE + 2.5 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 2.5 * cm, "PETUGAS PENERIMA")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(X_POS + 5 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Nama_Pengantar_Berkas', '')).upper()} )")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Penerima_Berkas', '')).upper()} )")
    c.showPage()

    # HALAMAN 2 - BELAKANG (Watermark)
    gambar_garis_potong(); c.saveState(); c.setFillColorRGB(0.9, 0.9, 0.9); c.setFont("Helvetica-Bold", 35)
    c.translate(TENGAH, Y_BASE + (TINGGI_BOX / 2)); c.rotate(25); c.drawCentredString(0, 0, "UPTD PASAR KANDANGAN"); c.restoreState()
    c.setLineWidth(1.5); c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX); c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm)
    
    y_tab = Y_BASE + 10.35 * cm; TINGGI_B = 1.05 * cm
    DETAIL_ROWS = [("NOMOR URUT", data.get("No", "-")), ("TANGGAL TERIMA", format_tgl_hari_indo(data.get("Tanggal_Pengantaran", "-"))), ("TANGGAL PENGAMBILAN", format_tgl_hari_indo(data.get("Tanggal_Pengambilan", "-"))), ("NAMA & NOMOR TOKO", f"{data.get('Nama_Toko', '-')} - {data.get('No_Toko', '-')}"), ("NAMA PEMILIK (SK)", data.get("Nama_Pemilik_Asli", "-")), ("NAMA PENGANTAR", data.get("Nama_Pengantar_Berkas", "-"))]
    for label, val in DETAIL_ROWS:
        c.setLineWidth(1.5); c.rect(X_POS + 0.15 * cm, y_tab - TINGGI_B, 6.5 * cm, TINGGI_B); c.rect(X_POS + 6.65 * cm, y_tab - TINGGI_B, 13.2 * cm, TINGGI_B) 
        c.setFont("Helvetica-Bold", 9); c.drawString(X_POS + 0.4 * cm, y_tab - 0.7 * cm, label)
        c.setFont("Helvetica-Bold", 10); c.drawString(X_POS + 7.0 * cm, y_tab - 0.7 * cm, str(val).upper())
        y_tab -= TINGGI_B
    c.setFont("Helvetica-Bold", 10); c.drawString(X_POS + 0.6 * cm, Y_BASE + 2.8 * cm, "PERHATIAN:"); c.setFont("Helvetica", 9)
    c.drawString(X_POS + 0.6 * cm, Y_BASE + 2.2 * cm, "1. Simpan tanda terima ini sebagai syarat pengambilan SK asli."); c.drawString(X_POS + 0.6 * cm, Y_BASE + 1.6 * cm, "2. Pengambilan SK hanya dapat dilakukan di jam kerja UPTD.")
    c.save(); buffer.seek(0); return buffer

# --- PDF PARKIR (MIKRO 6.8 x 4.6) ---
def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    lebar_box, tinggi_box = 6.8 * cm, 4.6 * cm
    x_awal = (lebar_kertas - lebar_box) / 2; center_x = lebar_kertas / 2; y_top = 32 * cm; y_bottom = y_top - tinggi_box
    c.setLineWidth(1.2); c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    y_gp = y_bottom - 1.0 * cm; c.setDash(1, 3); c.setLineWidth(0.5); c.line(0, y_gp, lebar_kertas, y_gp); c.setDash() 
    tgl_dis = format_tgl_hari_indo(data['Tanggal'])
    c.setFont("Helvetica-Bold", 7); c.drawCentredString(center_x, y_top - 0.5*cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6); c.drawCentredString(center_x, y_top - 0.9*cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.line(x_awal + 0.3*cm, y_top - 1.1*cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1*cm)
    c.setFont("Helvetica-Bold", 6); c.drawString(x_awal + 0.3*cm, y_top - 1.5*cm, f"TGL : {tgl_dis}"); c.drawString(x_awal + 0.3*cm, y_top - 1.9*cm, f"NAMA : {str(data['Nama_Petugas']).upper()}")
    y_tab, t_row = y_top - 2.2*cm, 0.6*cm; x_tab, l_tab = x_awal + 0.3*cm, lebar_box - 0.6*cm
    for i, (jns, jml) in enumerate([("RODA 2", data.get('MPP_Roda_R2', 0)), ("RODA 4", data.get('MPP_Roda_R4', 0))]):
        y_r = y_tab - ((i+1) * t_row); c.rect(x_tab, y_r, l_tab, t_row)
        c.setFont("Helvetica", 6); c.drawString(x_tab + 0.1*cm, y_r + 0.2*cm, jns); c.drawCentredString(center_x, y_r + 0.2*cm, f"{jml} LBR"); c.drawRightString(x_tab + l_tab - 0.1*cm, y_r + 0.2*cm, "MPP")
    c.showPage(); c.save(); buffer.seek(0); return buffer

def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm)); c.setFont("Helvetica-Bold", 10); X_POS = 0.75 * cm
    y_target = 21.5 * cm + 0.75 * cm + 10.35 * cm - (1.05 * cm * 2) - 0.7 * cm
    c.drawString(X_POS + 7.0 * cm, y_target, format_tgl_hari_indo(tgl_ambil).upper()); c.save(); buffer.seek(0); return buffer

# ==========================================
# 4. MODUL SK TOKO
# ==========================================
def halaman_pengantaran():
    st.header("📝 INPUT PENGANTARAN BERKAS")
    df_sk = load_data("DATA_SK")
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(df_sk) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    col_stat1.metric("📦 Total Berkas", total); col_stat2.metric("✅ Sudah Diambil", sudah_ambil); col_stat3.metric("⏳ Belum Diambil", total - sudah_ambil)
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    if "sel_berkas" not in st.session_state: st.session_state["sel_berkas"] = []
    st.subheader("☑️ Pilih Berkas yang Dibawa:"); cols_berkas = st.columns(3); sel_berkas = []
    for i, item in enumerate(SEMUA_BERKAS):
        with cols_berkas[i % 3]:
            if st.checkbox(item, key=f"cb_{item}"): sel_berkas.append(item)
    st.divider()
    with st.form("form_pengantaran", clear_on_submit=False):
        st.subheader("📋 Data Pengantaran")
        next_no = get_next_no(df_sk); col1, col2 = st.columns(2)
        with col1:
            no_urut = st.text_input("NOMOR URUT *", value=str(next_no))
            tgl_terima = st.text_input("TANGGAL TERIMA *", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = st.text_input("NAMA TOKO *").strip().upper(); no_toko = st.text_input("NOMOR TOKO *").strip().upper()
        with col2:
            nama_pemilik = st.text_input("NAMA PEMILIK SK *").strip().upper(); nama_pengantar = st.text_input("NAMA PENGANTAR *").strip().upper(); nama_penerima = st.text_input("NAMA PENERIMA *").strip().upper()
        if st.form_submit_button("💾 SIMPAN DATA", type="primary"):
            if not no_urut.strip() or not nama_toko or not nama_pemilik: st.error("❌ Data Wajib Diisi!")
            else:
                is_exist = not df_sk.empty and no_urut.strip() in df_sk["No"].str.strip().values
                new_row = {"No": no_urut.strip(), "Tanggal_Pengantaran": tgl_terima, "Tanggal_Pengambilan": "-", "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": nama_pemilik, "Nama_Pengantar_Berkas": nama_pengantar, "Penerima_Berkas": nama_penerima}
                if is_exist: st.session_state["pending_sk"] = new_row; st.session_state["show_confirm_sk"] = True
                else:
                    df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                    if safe_update("DATA_SK", df_baru): st.session_state["last_sk"] = new_row; st.session_state["last_berkas"] = sel_berkas; st.success("✅ Berhasil!"); st.rerun()

    if st.session_state.get("show_confirm_sk"):
        st.warning(f"⚠️ Nomor {no_urut} sudah ada!"); col_c1, col_c2 = st.columns(2)
        if col_c1.button("✅ YA, TIMPA DATA", type="primary"):
            d = st.session_state["pending_sk"]; df_sk = df_sk[df_sk["No"] != d["No"]]; df_final = pd.concat([df_sk, pd.DataFrame([d])], ignore_index=True)
            if safe_update("DATA_SK", df_final): st.session_state["last_sk"] = d; st.session_state["last_berkas"] = sel_berkas; st.session_state["show_confirm_sk"] = False; st.rerun()
        if col_c2.button("❌ BATAL"): st.session_state["show_confirm_sk"] = False; st.rerun()

    if "last_sk" in st.session_state:
        st.divider(); l = st.session_state["last_sk"]
        st.download_button("📥 DOWNLOAD PDF TANDA TERIMA", data=buat_pdf_full(l, st.session_state["last_berkas"]), file_name=f"TANDA_{l['No']}.pdf", mime="application/pdf")
    st.divider(); st.subheader("📊 DATA GOOGLE SHEETS")
    if not df_sk.empty: st.dataframe(df_sk.sort_values(by="No", ascending=False), use_container_width=True, hide_index=True)

def halaman_pengambilan_sk():
    st.header("PENGAMBILAN BERKAS SK"); df_m = load_data("DATA_SK")
    if df_m.empty: return
    df_b = df_m[df_m["Tanggal_Pengambilan"] == "-"]; no_cari = st.text_input("🔍 CARI NOMOR URUT:").strip()
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
        else: st.error("❌ Nomor Urut tidak terdaftar.")
    st.divider(); st.subheader(f"📊 BELUM DIAMBIL ({len(df_b)})"); st.dataframe(df_b.sort_values(by="No", ascending=True), use_container_width=True, hide_index=True)

# ==========================================
# 5. MODUL PARKIR (PERBAIKAN PENCARIAN TGL)
# ==========================================
def halaman_parkir(menu):
    st.header(f"🚗 {menu}"); df_p = load_data("DATA_PARKIR")

    if menu == "INPUT REKAP":
        st.subheader("📝 REKAP SETORAN")
        tgl_input_user = st.text_input("MASUKKAN TANGGAL", value=datetime.now().strftime("%d-%m-%Y"))
        
        # --- LOGIKA PENCARIAN TANGGAL SAKTI ---
        # 1. Ubah input user jadi objek tanggal
        try:
            tgl_bersih = str(tgl_input_user).strip().replace('/', '-')
            if len(tgl_bersih.split('-')[-1]) == 2:
                dt_user = datetime.strptime(tgl_bersih, "%d-%m-%y").date()
            else:
                dt_user = datetime.strptime(tgl_bersih, "%d-%m-%Y").date()
            
            # 2. Ubah kolom Tanggal di Sheets jadi objek tanggal untuk dibandingkan
            # pd.to_datetime sangat pintar mendeteksi format Sheets (1/4/2026 atau 2026-04-01)
            df_p['Tgl_Temp'] = pd.to_datetime(df_p['Tanggal'], dayfirst=True, errors='coerce').dt.date
            
            # 3. Cari baris yang tanggalnya SAMA
            baris = df_p[df_p['Tgl_Temp'] == dt_user]
        except:
            baris = pd.DataFrame()

        if not baris.empty:
            idx = baris.index[0]
            nama_p = baris.iloc[0]["Nama_Petugas"]
            st.success(f"👤 PETUGAS: **{nama_p}** | 📅 **{format_tgl_hari_indo(tgl_input_user)}**")
            
            # AMBIL SISA KEMARIN (idx - 1) - ANTI ERROR
            sisa_r2 = pd.to_numeric(df_p.iloc[idx - 1].get("Sisa_Stok_R2", 0), errors='coerce') if idx > 0 else 0
            sisa_r4 = pd.to_numeric(df_p.iloc[idx - 1].get("Sisa_Stok_R4", 0), errors='coerce') if idx > 0 else 0
            
            # Jika kosong/tidak terbaca, paksa jadi angka 0
            sisa_r2 = 0 if pd.isna(sisa_r2) else sisa_r2
            sisa_r4 = 0 if pd.isna(sisa_r4) else sisa_r4
            
            st.info(f"📊 SISA KEMARIN: R2={sisa_r2} | R4={sisa_r4}")
            
            with st.form("form_p_rekap"):
                c1, c2 = st.columns(2)
                with c1: 
                    pk2 = st.number_input("AMBIL R2", min_value=0)
                    tr2 = st.number_input("TERJUAL R2", min_value=0)
                    mr2 = st.number_input("MPP R2", min_value=0)
                with c2: 
                    pk4 = st.number_input("AMBIL R4", min_value=0)
                    tr4 = st.number_input("TERJUAL R4", min_value=0)
                    mr4 = st.number_input("MPP R4", min_value=0)
                
                if st.form_submit_button("💾 SIMPAN UPDATE", type="primary"):
                    sn2 = (pk2 + sisa_r2) - tr2
                    sn4 = (pk4 + sisa_r4) - tr4
                    
                    df_p.loc[idx, ["Pengambilan_Karcis_R2", "Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [pk2, tr2, mr2, sn2, tr2-mr2]
                    df_p.loc[idx, ["Pengambilan_Karcis_R4", "Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [pk4, tr4, mr4, sn4, tr4-mr4]
                    df_p.loc[idx, ["Status_Khusus", "Status_MPP"]] = ["BELUM", "BELUM"]
                    
                    # Hapus kolom temp sebelum save
                    if 'Tgl_Temp' in df_p.columns: df_p = df_p.drop(columns=['Tgl_Temp'])
                    
                    if safe_update("DATA_PARKIR", df_p): 
                        st.success("✅ Berhasil!"); st.rerun()
        else: 
            st.warning("⚠️ Tanggal belum ada di jadwal Sheet. Pastikan jadwal di Sheets sudah terisi.")

    elif menu == "KONFIRMASI":
        df_pen = df_p[(df_p["Status_Khusus"] == "BELUM") | (df_p["Status_MPP"] == "BELUM")].copy()
        # Filter baris yang sudah diisi datanya (Total tidak '-')
        df_pen = df_pen[df_pen["Total_Karcis_R2"] != "-"]
        
        if df_pen.empty: 
            st.info("TIDAK ADA DATA KONFIRMASI.")
        else:
            for i, row in df_pen.iterrows():
                with st.expander(f"📦 {row['Tanggal']} - {row['Nama_Petugas']}"):
                    ck, cm = st.columns(2)
                    with ck:
                        st.write(f"**KHUSUS**\nR2: {row['Khusus_Roda_R2']}\nR4: {row['Khusus_Roda_R4']}")
                        if st.button("TERIMA KHUSUS", key=f"k{i}", use_container_width=True):
                            df_p.loc[i, "Status_Khusus"] = "SUDAH"
                            if safe_update("DATA_PARKIR", df_p): st.rerun()
                    with cm:
                        st.write(f"**MPP**\nR2: {row['MPP_Roda_R2']}\nR4: {row['MPP_Roda_R4']}")
                        if row["Status_MPP"] == "BELUM":
                            if st.button("TERIMA MPP", key=f"m{i}", type="primary", use_container_width=True):
                                df_p.loc[i, "Status_MPP"] = "SUDAH"
                                if safe_update("DATA_PARKIR", df_p): st.rerun()
                        else: 
                            st.download_button("🖨️ CETAK PDF", data=cetak_tanda_terima_parkir(row), file_name=f"MPP_{row['Tanggal']}.pdf", key=f"p{i}", use_container_width=True)
    
    st.divider()
    st.subheader("📊 LOG DATA TERAKHIR")
    # Hapus kolom temp jika ada sebelum tampil
    if 'Tgl_Temp' in df_p.columns: df_p = df_p.drop(columns=['Tgl_Temp'])
    st.dataframe(df_p.sort_values(by="Tanggal", ascending=False).head(10), hide_index=True)

# ==========================================
# 6. MAIN RUNNER (MODUL SELECTOR)
# ==========================================
def main():
    # Menampilkan Logo HSS di Sidebar jika ada
    path_logo = "logo_hss.png" 
    if os.path.exists(path_logo):
        st.sidebar.image(path_logo, width=100)
        
    with st.sidebar:
        st.title("🗂️ UPTD PASAR")
        modul = st.selectbox("PILIH MODUL:", ["SK TOKO", "PARKIR"])
        if modul == "SK TOKO": 
            menu = st.radio("MENU SK:", ["PENGANTARAN", "PENGAMBILAN"])
        else: 
            menu = st.radio("MENU PARKIR:", ["INPUT REKAP", "KONFIRMASI"])
    
    if modul == "SK TOKO":
        if menu == "PENGANTARAN": 
            halaman_pengantaran()
        else: 
            halaman_pengambilan_sk()
    else: 
        halaman_parkir(menu)

if __name__ == "__main__":
    main()
