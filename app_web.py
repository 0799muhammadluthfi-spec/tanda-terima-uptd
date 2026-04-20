import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. FUNGSI KHUSUS CETAK PARKIR
# ==========================================
def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    lebar_box, tinggi_box = 6.8 * cm, 4.6 * cm
    x_awal, center_x = (lebar_kertas - lebar_box) / 2, lebar_kertas / 2
    y_top = 32 * cm 
    y_bottom = y_top - tinggi_box
    c.setLineWidth(1.2)
    c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    
    y_garis_potong = y_bottom - 1.0 * cm
    c.setDash(1, 3); c.setLineWidth(0.5)
    c.line(0, y_garis_potong, lebar_kertas, y_garis_potong); c.setDash() 
    
    tgl_raw = str(data.get('Tanggal', '-')).replace('/', '-')
    try:
        if len(tgl_raw.split('-')[-1]) == 2:
            tgl_obj = datetime.strptime(tgl_raw, "%d-%m-%y")
        else:
            tgl_obj = datetime.strptime(tgl_raw, "%d-%m-%Y")
        hari_indo = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
        tgl_final = f"{hari_indo[tgl_obj.weekday()]}, {tgl_obj.strftime('%d - %m - %Y')}"
    except: 
        tgl_final = str(tgl_raw).upper()

    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(center_x, y_top - 0.5 * cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(center_x, y_top - 0.9 * cm, "TANDA TERIMA KARCIS PARKIR (MPP)")
    c.setLineWidth(0.8); c.line(x_awal + 0.3*cm, y_top - 1.1 * cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1 * cm)
    
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_awal + 0.3*cm, y_top - 1.5 * cm, f"TGL : {tgl_final}")
    c.drawString(x_awal + 0.3*cm, y_top - 1.9 * cm, f"NAMA : {str(data.get('Nama_Petugas', '-')).upper()}")
    
    y_tab, t_row = y_top - 2.2 * cm, 0.6 * cm
    lebar_tabel_mini, x_tab = lebar_box - 0.6 * cm, x_awal + 0.3 * cm
    c.rect(x_tab, y_tab - t_row, lebar_tabel_mini, t_row)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(x_tab + 0.1*cm, y_tab - 0.4*cm, "JENIS")
    c.drawCentredString(center_x, y_tab - 0.4*cm, "JUMLAH"); c.drawRightString(x_tab + lebar_tabel_mini - 0.1*cm, y_tab - 0.4*cm, "KET")
    
    for i, r in enumerate([('RODA 2', 'MPP_Roda_R2'), ('RODA 4', 'MPP_Roda_R4')], 2):
        yy = y_tab - (i * t_row); c.rect(x_tab, yy, lebar_tabel_mini, t_row)
        c.setFont("Helvetica", 6); c.drawString(x_tab + 0.1*cm, yy + 0.2*cm, r[0])
        c.drawCentredString(center_x, yy + 0.2*cm, f"{data.get(r[1], 0)} LBR"); c.drawRightString(x_tab + lebar_tabel_mini - 0.1*cm, yy + 0.2*cm, "MPP")
    
    c.showPage(); c.save(); buffer.seek(0); return buffer

# ==========================================
# 2. KONFIGURASI & HELPER
# ==========================================
st.set_page_config(page_title="UPTD PASAR KANDANGAN", page_icon="🏪", layout="wide")

# Link Logo HSS (Hulu Sungai Selatan)
URL_LOGO_HSS = "https://hsskab.go.id/wp-content/uploads/2021/04/Logo-HSS-min.png"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(worksheet: str) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        df = df.astype(str).replace(r'\.0$', '', regex=True).replace(["nan", "None", "NAN"], "-")
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
    if not tgl_str or tgl_str in ["-", "nan", ""]: return ""
    try:
        dt = datetime.strptime(str(tgl_str).strip(), "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except: return str(tgl_str).upper()

def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns: return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except: return 1

# ==========================================
# 3. MODUL PARKIR (TANGGAL PINTAR & KOLOM FIX)
# ==========================================
def halaman_parkir(menu_aktif):
    st.header(f"🚗 {menu_aktif}")
    df_parkir = load_data("DATA_PARKIR")
    if df_parkir.empty: 
        st.warning("Data Parkir tidak ditemukan di Spreadsheet.")
        return

    if menu_aktif == "INPUT REKAP":
        st.subheader("📝 FORM REKAP SETORAN")
        raw_tgl = st.text_input("MASUKKAN TANGGAL (Bisa 1/4/26 atau 01-04-2026)", value=datetime.now().strftime("%d-%m-%Y"))
        
        # Logika Pencarian Tanggal Pintar
        tgl_b = raw_tgl.replace("/", "-").strip()
        try:
            if len(tgl_b.split("-")[-1]) == 2:
                t_obj = datetime.strptime(tgl_b, "%d-%m-%y")
            else:
                t_obj = datetime.strptime(tgl_b, "%d-%m-%Y")
            t_std = t_obj.strftime("%d-%m-%Y")
            t_alt = f"{t_obj.day}-{t_obj.month}-{t_obj.year}"
        except: t_std, t_alt = tgl_b, tgl_b

        # Bersihkan spasi di kolom Tanggal agar pencarian akurat
        df_parkir["Tanggal"] = df_parkir["Tanggal"].str.strip()
        baris_cocok = df_parkir[(df_parkir["Tanggal"] == t_std) | (df_parkir["Tanggal"] == t_alt)]
        
        if not baris_cocok.empty:
            idx = baris_cocok.index[0]
            row = baris_cocok.iloc[0]
            st.success(f"👤 PETUGAS: **{row['Nama_Petugas']}** | 📅 **{t_std}**")
            
            # Ambil sisa kemarin dari baris sebelumnya secara aman
            try: sisa_r2 = int(float(df_parkir.iloc[idx-1].get("Sisa_Karcis_r2", 0))) if idx > 0 else 0
            except: sisa_r2 = 0
            try: sisa_r4 = int(float(df_parkir.iloc[idx-1].get("Sisa_Karcis_r4", 0))) if idx > 0 else 0
            except: sisa_r4 = 0
            st.info(f"📊 SISA KEMARIN: R2={sisa_r2} | R4={sisa_r4}")

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
                    sn2 = (pk_r2 + sisa_r2) - tot_r2
                    sn4 = (pk_r4 + sisa_r4) - tot_r4
                    
                    # Update data menggunakan nama kolom persis di Spreadsheet Anda
                    df_parkir.loc[idx, ["Pengambilan_Karcis_R2", "Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Karcis_r2", "Khusus_Roda_R2"]] = [str(pk_r2), str(tot_r2), str(mpp_r2), str(sn2), str(tot_r2-mpp_r2)]
                    df_parkir.loc[idx, ["Pengambilan_Karcis_R4", "Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Karcis_r4", "Khusus_Roda_R4"]] = [str(pk_r4), str(tot_r4), str(mpp_r4), str(sn4), str(tot_r4-mpp_r4)]
                    df_parkir.loc[idx, ["Status_Khusus", "Status_MPP"]] = ["BELUM", "BELUM"]
                    
                    if safe_update("DATA_PARKIR", df_parkir):
                        st.success("✅ BERHASIL DIUPDATE!"); st.rerun()
        else:
            st.warning(f"⚠️ TANGGAL '{t_std}' TIDAK DITEMUKAN DI GOOGLE SHEETS.")

    elif menu_aktif == "KONFIRMASI":
        st.subheader("✅ Verifikasi Penerimaan Karcis")
        df_pending = df_parkir[(df_parkir["Status_Khusus"] == "BELUM") | (df_parkir["Status_MPP"] == "BELUM")]
        
        if df_pending.empty: st.info("Semua rekap sudah dikonfirmasi.")
        else:
            for index, row in df_pending.sort_values(by="No").iterrows():
                with st.expander(f"📦 Nomor: {row['No']} - {row['Nama_Petugas']} ({row['Tanggal']})"):
                    ck, cm = st.columns(2)
                    with ck:
                        st.markdown("### 🎫 KHUSUS")
                        st.write(f"R2: {row['Khusus_Roda_R2']} | R4: {row['Khusus_Roda_R4']}")
                        if row["Status_Khusus"] == "BELUM":
                            if st.button(f"TERIMA KHUSUS #{row['No']}", key=f"kh_{index}", type="primary"):
                                df_parkir.loc[index, "Status_Khusus"] = "SUDAH"
                                safe_update("DATA_PARKIR", df_parkir); st.rerun()
                        else: st.success("✅ KHUSUS OKE")
                    with cm:
                        st.markdown("### 🏢 MPP")
                        st.write(f"R2: {row['MPP_Roda_R2']} | R4: {row['MPP_Roda_R4']}")
                        if row["Status_MPP"] == "BELUM":
                            if st.button(f"TERIMA MPP #{row['No']}", key=f"mpp_{index}", type="primary"):
                                df_parkir.loc[index, "Status_MPP"] = "SUDAH"
                                safe_update("DATA_PARKIR", df_parkir); st.rerun()
                        else: 
                            st.success("✅ MPP OKE")
                            st.download_button(label="🖨️ CETAK MPP", data=cetak_tanda_terima_parkir(row), file_name=f"MPP_{row['Nama_Petugas']}.pdf", key=f"dl_{index}")
    
    st.divider(); st.dataframe(df_parkir.sort_values(by="No", ascending=False), hide_index=True)

# ==========================================
# 4. MODUL SK TOKO (PENGANTARAN & PENGAMBILAN)
# ==========================================
def halaman_pengantaran():
    st.header("📝 INPUT PENGANTARAN BERKAS")
    df_sk = load_data("DATA_SK")
    next_no = get_next_no(df_sk)
    
    with st.form("form_sk"):
        c1, c2 = st.columns(2)
        with c1:
            no_urut = st.text_input("NOMOR URUT *", value=str(next_no))
            tgl_terima = st.text_input("TANGGAL TERIMA", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = st.text_input("NAMA TOKO").upper()
        with c2:
            no_toko = st.text_input("NOMOR TOKO").upper()
            nama_pemilik = st.text_input("NAMA PEMILIK SK").upper()
            nama_pengantar = st.text_input("NAMA PENGANTAR").upper()
        
        if st.form_submit_button("💾 SIMPAN DATA"):
            new_row = {"No": no_urut, "Tanggal_Pengantaran": tgl_terima, "Tanggal_Pengambilan": "-", "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": nama_pemilik, "Nama_Pengantar_Berkas": nama_pengantar}
            df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
            if safe_update("DATA_SK", df_baru): st.success("✅ Tersimpan!"); st.rerun()
    st.dataframe(df_sk.sort_values(by="No", ascending=False), hide_index=True)

# ==========================================
# 5. MAIN APP (SPLASH SCREEN & SIDEBAR)
# ==========================================
def main():
    if "masuk" not in st.session_state: st.session_state.masuk = False

    if not st.session_state.masuk:
        st.write("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(URL_LOGO_HSS, width=250)
            st.markdown(f"""
                <h2 style='text-align: center; margin-top: 10px;'>Selamat Datang</h2>
                <h1 style='text-align: center; color: #4CAF50;'>M. Luthfi Renaldi</h1>
                <p style='text-align: center; color: gray;'>Sistem Informasi Pelayanan UPTD Pasar Kandangan</p>
            """, unsafe_allow_html=True)
            if st.button("🚀 MASUK KE DASHBOARD", use_container_width=True, type="primary"):
                st.session_state.masuk = True; st.rerun()
    else:
        with st.sidebar:
            col_l, col_t = st.columns([1, 3])
            with col_l: st.image(URL_LOGO_HSS)
            with col_t: st.markdown("<h3 style='margin-top: 5px;'>UPTD PASAR</h3>", unsafe_allow_html=True)
            st.divider()
            modul = st.selectbox("PILIH MODUL:", ["SK TOKO", "PARKIR"])
            if modul == "SK TOKO":
                menu = st.radio("MENU SK:", ["PENGANTARAN", "PENGAMBILAN"])
            else:
                menu = st.radio("MENU PARKIR:", ["INPUT REKAP", "KONFIRMASI"])
        
        if modul == "PARKIR": halaman_parkir(menu)
        else: halaman_pengantaran() # Sesuaikan jika ada fungsi halaman_pengambilan

if __name__ == "__main__":
    main()
