import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. FUNGSI KHUSUS CETAK PARKIR (PORTRAIT)
# ==========================================
def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    
    lebar_box = 6.8 * cm
    tinggi_box = 4.6 * cm
    x_awal = (lebar_kertas - lebar_box) / 2
    center_x = lebar_kertas / 2
    y_top = 32 * cm 
    y_bottom = y_top - tinggi_box
    
    c.setLineWidth(1.2)
    c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    
    y_garis_potong = y_bottom - 1.0 * cm
    c.setDash(1, 3)
    c.setLineWidth(0.5)
    c.line(0, y_garis_potong, lebar_kertas, y_garis_potong)
    c.setDash() 
    
    tgl_input = str(data['Tanggal']).replace('/', '-')
    try:
        if len(tgl_input.split('-')[-1]) == 2:
            tgl_obj = datetime.strptime(tgl_input, "%d-%m-%y")
        else:
            tgl_obj = datetime.strptime(tgl_input, "%d-%m-%Y")
            
        hari_indo = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
        nama_hari = hari_indo[tgl_obj.weekday()]
        tgl_final = f"{nama_hari}, {tgl_obj.strftime('%d - %m - %Y')}"
    except:
        tgl_final = str(data['Tanggal']).upper()

    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(center_x, y_top - 0.5 * cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(center_x, y_top - 0.9 * cm, "TANDA TERIMA KARCIS PARKIR (MPP)")
    c.setLineWidth(0.8)
    c.line(x_awal + 0.3*cm, y_top - 1.1 * cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1 * cm)
    
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_awal + 0.3*cm, y_top - 1.5 * cm, f"TGL : {tgl_final}")
    c.drawString(x_awal + 0.3*cm, y_top - 1.9 * cm, f"NAMA : {str(data['Nama_Petugas']).upper()}")

    y_tab = y_top - 2.2 * cm
    t_row = 0.6 * cm
    lebar_tabel_mini = lebar_box - 0.6 * cm
    x_tab = x_awal + 0.3 * cm
    
    c.rect(x_tab, y_tab - t_row, lebar_tabel_mini, t_row)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(x_tab + 0.1*cm, y_tab - 0.4*cm, "JENIS")
    c.drawCentredString(center_x, y_tab - 0.4*cm, "JUMLAH")
    c.drawRightString(x_tab + lebar_tabel_mini - 0.1*cm, y_tab - 0.4*cm, "KET")
    
    y_r2 = y_tab - (2 * t_row)
    c.rect(x_tab, y_r2, lebar_tabel_mini, t_row)
    c.setFont("Helvetica", 6)
    c.drawString(x_tab + 0.1*cm, y_r2 + 0.2*cm, "RODA 2")
    c.drawCentredString(center_x, y_r2 + 0.2*cm, f"{data['MPP_Roda_R2']} LBR")
    c.drawRightString(x_tab + lebar_tabel_mini - 0.1*cm, y_r2 + 0.2*cm, "MPP")

    y_r4 = y_tab - (3 * t_row)
    c.rect(x_tab, y_r4, lebar_tabel_mini, t_row)
    c.drawString(x_tab + 0.1*cm, y_r4 + 0.2*cm, "RODA 4")
    c.drawCentredString(center_x, y_r4 + 0.2*cm, f"{data['MPP_Roda_R4']} LBR")
    c.drawRightString(x_tab + lebar_tabel_mini - 0.1*cm, y_r4 + 0.2*cm, "MPP")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 1. KONFIGURASI & LOGO
# ==========================================
st.set_page_config(page_title="UPTD PASAR KANDANGAN", page_icon="🏪", layout="wide")

URL_LOGO_HSS = "https://hsskab.go.id/wp-content/uploads/2021/04/Logo-HSS-min.png"

conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI HELPER
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        df = df.astype(str).replace(r'\.0$', '', regex=True).replace("nan", "-").replace("None", "-")
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

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
        dt = datetime.strptime(str(tgl_str).strip(), "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()

def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns: return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except: return 1

# ==========================================
# 4. MODUL PENGANTARAN & PENGAMBILAN
# ==========================================
def halaman_pengantaran():
    st.header("📝 INPUT PENGANTARAN BERKAS")
    df_sk = load_data("DATA_SK")
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(df_sk) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    col_stat1.metric("📦 Total Berkas", total)
    col_stat2.metric("✅ Sudah Diambil", sudah_ambil)
    col_stat3.metric("⏳ Belum Diambil", total - sudah_ambil)
    
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    st.subheader("☑️ Pilih Berkas yang Dibawa:")
    cols_berkas = st.columns(3)
    sel_berkas = []
    for i, item in enumerate(SEMUA_BERKAS):
        with cols_berkas[i % 3]:
            if st.checkbox(item, key=f"cb_{item}"): sel_berkas.append(item)
    
    st.divider()
    with st.form("form_pengantaran", clear_on_submit=False):
        st.subheader("📋 Data Pengantaran")
        next_no = get_next_no(df_sk)
        col1, col2 = st.columns(2)
        with col1:
            no_urut = st.text_input("NOMOR URUT *", value=str(next_no))
            tgl_terima = st.text_input("TANGGAL TERIMA *", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = st.text_input("NAMA TOKO *").strip().upper()
            no_toko = st.text_input("NOMOR TOKO *").strip().upper()
        with col2:
            nama_pemilik = st.text_input("NAMA PEMILIK SK *").strip().upper()
            nama_pengantar = st.text_input("NAMA PENGANTAR *").strip().upper()
            nama_penerima = st.text_input("NAMA PENERIMA *").strip().upper()
        
        if st.form_submit_button("💾 SIMPAN DATA", type="primary"):
            if not no_urut.strip() or not nama_toko or not nama_pemilik: 
                st.error("❌ Data Bintang (*) Wajib Diisi!")
            else:
                new_row = {"No": no_urut.strip(), "Tanggal_Pengantaran": tgl_terima, "Tanggal_Pengambilan": "-", "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": nama_pemilik, "Nama_Pengantar_Berkas": nama_pengantar, "Penerima_Berkas": nama_penerima}
                df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                if safe_update("DATA_SK", df_baru):
                    st.session_state["last_data"] = new_row
                    st.session_state["last_berkas"] = sel_berkas
                    st.success("✅ Berhasil Disimpan!")
                    st.rerun()

    if "last_data" in st.session_state:
        st.divider()
        last = st.session_state["last_data"]
        st.download_button(label="📥 DOWNLOAD PDF TANDA TERIMA", data=buat_pdf_full(last, st.session_state["last_berkas"]), file_name=f"TANDA_{last['No']}.pdf", mime="application/pdf")
    
    st.divider()
    st.subheader("📊 DATA TABEL GOOGLE SHEETS")
    if not df_sk.empty: 
        st.dataframe(df_sk.sort_values(by="No", ascending=False), use_container_width=True, hide_index=True)

def halaman_pengambilan():
    st.header("PENGAMBILAN BERKAS")
    df_mentah = load_data("DATA_SK")
    if df_mentah.empty: 
        st.warning("Data tidak ditemukan.")
        return
    
    df_belum_diambil = df_mentah[df_mentah["Tanggal_Pengambilan"] == "-"]
    no_cari = st.text_input("🔍 CARI NOMOR URUT:").strip()
    if no_cari:
        hasil = df_mentah[df_mentah["No"].str.strip() == no_cari]
        if not hasil.empty:
            data_row = hasil.iloc[0]
            sudah_ambil = data_row["Tanggal_Pengambilan"] not in ["-", "nan", "NAN", ""]
            if sudah_ambil:
                st.success(f"✅ Berkas Toko **{data_row['Nama_Toko']}** sudah diambil pada: {format_tgl_hari_indo(data_row['Tanggal_Pengambilan'])}")
                st.download_button("🖨️ PRINT ULANG TANGGAL AMBIL", data=cetak_overprint(data_row['Tanggal_Pengambilan']), file_name=f"AMBIL_{no_cari}.pdf")
            else:
                st.warning(f"🏪 Toko: {data_row['Nama_Toko']} (BELUM DIAMBIL)")
                tgl_ambil = st.text_input("📅 TANGGAL PENGAMBILAN:", value=datetime.now().strftime("%d-%m-%Y"))
                if st.button("✅ KONFIRMASI PENGAMBILAN"):
                    df_mentah.loc[df_mentah["No"].str.strip() == no_cari, "Tanggal_Pengambilan"] = tgl_ambil
                    if safe_update("DATA_SK", df_mentah): 
                        st.success("Konfirmasi berhasil!")
                        st.rerun()
        else: 
            st.error("❌ Nomor Urut tidak terdaftar.")
            
    st.divider()
    st.subheader(f"📊 DAFTAR BERKAS BELUM DIAMBIL ({len(df_belum_diambil)} Berkas)")
    st.dataframe(df_belum_diambil.sort_values(by="No", ascending=True), use_container_width=True, hide_index=True)

# ==========================================
# 6. MODUL PARKIR
# ==========================================
def halaman_parkir(menu_aktif):
    st.header(f"🚗 {menu_aktif}")
    df_parkir = load_data("DATA_PARKIR")
    
    if menu_aktif == "INPUT REKAP":
        st.subheader("📝 FORM REKAP SETORAN")
        raw_tgl = st.text_input("MASUKKAN TANGGAL (Bisa 1/1/26 atau 01-01-2026)", value=datetime.now().strftime("%d-%m-%Y"))
        tgl_bersih = raw_tgl.replace("/", "-").strip()
        try:
            if len(tgl_bersih.split("-")[-1]) == 2: 
                tgl_obj = datetime.strptime(tgl_bersih, "%d-%m-%y")
            else: 
                tgl_obj = datetime.strptime(tgl_bersih, "%d-%m-%Y")
            tgl_std = tgl_obj.strftime("%d-%m-%Y")
            tgl_alt = f"{tgl_obj.day}-{tgl_obj.month}-{tgl_obj.year}"
        except: 
            tgl_std = tgl_bersih
            tgl_alt = tgl_bersih
            
        baris_cocok = df_parkir[(df_parkir["Tanggal"].astype(str) == tgl_std) | (df_parkir["Tanggal"].astype(str) == tgl_alt)]
        if not baris_cocok.empty:
            idx = baris_cocok.index[0]
            nama_ptgs = baris_cocok.iloc[0]["Nama_Petugas"]
            st.success(f"👤 PETUGAS: **{nama_ptgs}** | 📅 **{tgl_std}**")
            
            try: sisa_r2_lama = int(float(df_parkir.iloc[idx - 1].get("Sisa_Karcis_r2", 0))) if idx > 0 else 0
            except: sisa_r2_lama = 0
            try: sisa_r4_lama = int(float(df_parkir.iloc[idx - 1].get("Sisa_Karcis_r4", 0))) if idx > 0 else 0
            except: sisa_r4_lama = 0
            
            st.info(f"📊 SISA KEMARIN: R2={sisa_r2_lama} | R4={sisa_r4_lama}")
            
            with st.form("form_parkir"):
                c1, c2 = st.columns(2)
                with c1: 
                    pk_r2 = st.number_input("AMBIL BARU R2", 0)
                    tot_r2 = st.number_input("TERJUAL R2", 0)
                    mpp_r2 = st.number_input("MPP R2", 0)
                with c2: 
                    pk_r4 = st.number_input("AMBIL BARU R4", 0)
                    tot_r4 = st.number_input("TERJUAL R4", 0)
                    mpp_r4 = st.number_input("MPP R4", 0)
                
                if st.form_submit_button("💾 UPDATE DATA", type="primary"):
                    sisa_n_r2 = (pk_r2 + sisa_r2_lama) - tot_r2
                    sisa_n_r4 = (pk_r4 + sisa_r4_lama) - tot_r4
                    df_parkir.loc[idx, ["Pengambilan_Karcis_R2", "Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Karcis_r2", "Khusus_Roda_R2"]] = [str(pk_r2), str(tot_r2), str(mpp_r2), str(sisa_n_r2), str(tot_r2-mpp_r2)]
                    df_parkir.loc[idx, ["Pengambilan_Karcis_R4", "Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Karcis_r4", "Khusus_Roda_R4"]] = [str(pk_r4), str(tot_r4), str(mpp_r4), str(sisa_n_r4), str(tot_r4-mpp_r4)]
                    df_parkir.loc[idx, ["Status_Khusus", "Status_MPP"]] = ["BELUM", "BELUM"]
                    if safe_update("DATA_PARKIR", df_parkir): 
                        st.success("✅ BERHASIL!")
                        st.rerun()
        else: 
            st.warning("⚠️ TANGGAL TIDAK DITEMUKAN.")
            
    elif menu_aktif == "KONFIRMASI":
        st.subheader("✅ Verifikasi Penerimaan Karcis")
        for col in ["Status_Khusus", "Status_MPP"]:
            if col not in df_parkir.columns: df_parkir[col] = "BELUM"
        
        df_pending = df_parkir[(df_parkir["Status_Khusus"] == "BELUM") | (df_parkir["Status_MPP"] == "BELUM")]
        if df_pending.empty: 
            st.info("Semua rekap sudah dikonfirmasi.")
        else:
            for index, row in df_pending.sort_values(by="No").iterrows():
                with st.expander(f"📦 Nomor: {row['No']} - {row['Nama_Petugas']} ({row['Tanggal']})"):
                    ck, cm = st.columns(2)
                    with ck:
                        st.markdown("### 🎫 KHUSUS")
                        st.write(f"R2: {row['Khusus_Roda_R2']} | R4: {row['Khusus_Roda_R4']}")
                        if row["Status_Khusus"] == "BELUM":
                            if st.button(f"TERIMA KHUSUS #{row['No']}", key=f"btn_kh_{index}", type="primary", use_container_width=True):
                                df_parkir.loc[index, "Status_Khusus"] = "SUDAH"
                                if safe_update("DATA_PARKIR", df_parkir): 
                                    st.rerun()
                        else: 
                            st.success("✅ KHUSUS OKE")
                    with cm:
                        st.markdown("### 🏢 MPP")
                        st.write(f"R2: {row['MPP_Roda_R2']} | R4: {row['MPP_Roda_R4']}")
                        if row["Status_MPP"] == "BELUM":
                            if st.button(f"TERIMA MPP #{row['No']}", key=f"btn_mpp_{index}", type="primary", use_container_width=True):
                                df_parkir.loc[index, "Status_MPP"] = "SUDAH"
                                if safe_update("DATA_PARKIR", df_parkir): 
                                    st.rerun()
                        else: 
                            st.success("✅ MPP OKE")
                            st.download_button(label="🖨️ CETAK TANDA TERIMA (MPP)", data=cetak_tanda_terima_parkir(row), file_name=f"TANDA_MPP_{row['Nama_Petugas']}.pdf", key=f"dl_mpp_{index}", use_container_width=True)
                            
    st.divider()
    st.subheader("📊 LOG REKAP PARKIR")
    if not df_parkir.empty: 
        st.dataframe(df_parkir.sort_values(by="No", ascending=False), use_container_width=True, hide_index=True)

# ==========================================
# 7. MAIN APP
# ==========================================
def main():
    if "sudah_masuk" not in st.session_state: 
        st.session_state["sudah_masuk"] = False

    if not st.session_state["sudah_masuk"]:
        st.write("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(URL_LOGO_HSS, width=250)
            st.markdown("""
                <h2 style='text-align: center; margin-top: 10px;'>Selamat Datang</h2>
                <h1 style='text-align: center; color: #4CAF50;'>M. Luthfi Renaldi</h1>
                <p style='text-align: center; color: gray;'>Sistem Informasi Pelayanan UPTD Pasar Kandangan</p>
            """, unsafe_allow_html=True)
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🚀 MASUK KE DASHBOARD", use_container_width=True, type="primary"):
                st.session_state["sudah_masuk"] = True
                st.rerun()
    else:
        with st.sidebar:
            col_l, col_j = st.columns([1, 3])
            with col_l: st.image(URL_LOGO_HSS, width=50)
            with col_j: st.markdown("<h3 style='margin-top: 5px;'>UPTD PASAR</h3>", unsafe_allow_html=True)
            st.divider()
            modul = st.selectbox("PILIH MODUL:", ["SK TOKO", "PARKIR"])
            if modul == "SK TOKO": 
                menu = st.radio("MENU SK:", ["PENGANTARAN", "PENGAMBILAN"])
            else: 
                menu = st.radio("MENU PARKIR:", ["INPUT REKAP", "KONFIRMASI"])
        
        if modul == "SK TOKO":
            if menu == "PENGANTARAN": halaman_pengantaran()
            else: halaman_pengambilan()
        else: 
            halaman_parkir(menu)

if __name__ == "__main__":
    main()
