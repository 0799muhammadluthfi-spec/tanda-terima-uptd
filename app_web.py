import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. FUNGSI KHUSUS PDF & HELPER
# ==========================================
def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    lebar_box, tinggi_box = 6.8 * cm, 4.6 * cm
    x_awal, center_x = (lebar_kertas - lebar_box) / 2, lebar_kertas / 2
    y_top = 32 * cm 
    y_bottom = y_top - tinggi_box
    c.setLineWidth(1.2); c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    y_garis_potong = y_bottom - 1.0 * cm
    c.setDash(1, 3); c.setLineWidth(0.5); c.line(0, y_garis_potong, lebar_kertas, y_garis_potong); c.setDash() 
    
    tgl_raw = str(data.get('Tanggal', '-')).replace('/', '-')
    try:
        t_obj = datetime.strptime(tgl_raw, "%d-%m-%y") if len(tgl_raw.split('-')[-1]) == 2 else datetime.strptime(tgl_raw, "%d-%m-%Y")
        tgl_f = f"{['SENIN','SELASA','RABU','KAMIS','JUMAT','SABTU','MINGGU'][t_obj.weekday()]}, {t_obj.strftime('%d-%m-%Y')}"
    except: tgl_f = str(tgl_raw).upper()

    c.setFont("Helvetica-Bold", 7); c.drawCentredString(center_x, y_top - 0.5 * cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6); c.drawCentredString(center_x, y_top - 0.9 * cm, "TANDA TERIMA KARCIS PARKIR (MPP)")
    c.setLineWidth(0.8); c.line(x_awal + 0.3*cm, y_top - 1.1 * cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1 * cm)
    c.setFont("Helvetica-Bold", 6); c.drawString(x_awal + 0.3*cm, y_top - 1.5 * cm, f"TGL : {tgl_f}")
    c.drawString(x_awal + 0.3*cm, y_top - 1.9 * cm, f"NAMA : {str(data.get('Nama_Petugas','')).upper()}")
    
    y_tab, t_row = y_top - 2.2 * cm, 0.6 * cm
    x_tab = x_awal + 0.3 * cm
    c.rect(x_tab, y_tab - t_row, lebar_box - 0.6*cm, t_row)
    c.setFont("Helvetica-Bold", 5.5); c.drawString(x_tab + 0.1*cm, y_tab - 0.4*cm, "JENIS")
    c.drawCentredString(center_x, y_tab - 0.4*cm, "JUMLAH"); c.drawRightString(x_tab + lebar_box - 0.7*cm, y_tab - 0.4*cm, "KET")
    
    for i, r in enumerate([('RODA 2', 'MPP_Roda_R2'), ('RODA 4', 'MPP_Roda_R4')], 2):
        yy = y_tab - (i * t_row); c.rect(x_tab, yy, lebar_box - 0.6*cm, t_row)
        c.setFont("Helvetica", 6); c.drawString(x_tab + 0.1*cm, yy + 0.2*cm, r[0])
        c.drawCentredString(center_x, yy + 0.2*cm, f"{data.get(r[1], 0)} LBR"); c.drawRightString(x_tab + lebar_box - 0.7*cm, yy + 0.2*cm, "MPP")
    c.showPage(); c.save(); buffer.seek(0); return buffer

def buat_pdf_full(data, berkas):
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm))
    c.setFont("Helvetica-Bold", 12); c.drawCentredString(10.75*cm, 31*cm, "TANDA TERIMA BERKAS SK TOKO")
    c.setFont("Helvetica", 10); yy = 29*cm
    for k, v in data.items():
        c.drawString(2*cm, yy, f"{k} : {v}"); yy -= 0.8*cm
    c.drawString(2*cm, yy, f"Berkas: {', '.join(berkas)}"); c.showPage(); c.save(); buffer.seek(0); return buffer

def cetak_overprint(tgl):
    buffer = BytesIO(); c = canvas.Canvas(buffer, pagesize=(21.5*cm, 33*cm))
    c.drawString(10*cm, 20*cm, f"DIAMBIL PADA: {tgl}"); c.showPage(); c.save(); buffer.seek(0); return buffer

# ==========================================
# 2. KONFIGURASI & KONEKSI
# ==========================================
st.set_page_config(page_title="UPTD PASAR KANDANGAN", page_icon="🏪", layout="wide")
URL_LOGO_HSS = "https://hsskab.go.id/wp-content/uploads/2021/04/Logo-HSS-min.png"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(ws):
    try:
        df = conn.read(worksheet=ws, ttl=0)
        return df.astype(str).replace(r'\.0$', '', regex=True).replace(["nan", "None", "NAN"], "-")
    except: return pd.DataFrame()

def safe_update(ws, data):
    try:
        conn.update(worksheet=ws, data=data); st.cache_data.clear(); return True
    except Exception as e: st.error(f"Gagal Simpan: {e}"); return False

def get_next_no(df, col="No"):
    try:
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except: return 1

# ==========================================
# 4. MODUL PENGANTARAN & PENGAMBILAN
# ==========================================
def halaman_pengantaran():
    st.header("📝 INPUT PENGANTARAN BERKAS")
    df_sk = load_data("DATA_SK")
    
    # Init session state untuk dialog konfirmasi
    if "show_confirm" not in st.session_state: st.session_state.show_confirm = False

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(df_sk) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    col_stat1.metric("📦 Total Berkas", total); col_stat2.metric("✅ Sudah Diambil", sudah_ambil); col_stat3.metric("⏳ Belum Diambil", total - sudah_ambil)
    
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
                
                # CEK APAKAH NOMOR SUDAH ADA
                is_exist = not df_sk.empty and no_urut.strip() in df_sk["No"].str.strip().values
                
                if is_exist:
                    st.session_state.pending_data = new_row
                    st.session_state.show_confirm = True
                else:
                    df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                    if safe_update("DATA_SK", df_baru):
                        st.session_state["last_data"] = new_row
                        st.session_state["last_berkas"] = sel_berkas
                        st.success("✅ Berhasil Disimpan!"); st.rerun()

    # DIALOG KONFIRMASI (DI LUAR FORM - BAGIAN YANG KAMU KIRIM)
    if st.session_state.get("show_confirm"):
        st.warning(f"⚠️ Nomor Urut {st.session_state.pending_data['No']} sudah ada di database!")
        col_conf1, col_conf2 = st.columns(2)
        
        if col_conf1.button("✅ YA, TIMPA DATA LAMA", type="primary", use_container_width=True):
            data_baru = st.session_state["pending_data"]
            df_sk = df_sk[df_sk["No"].str.strip() != data_baru["No"]]
            df_final = pd.concat([df_sk, pd.DataFrame([data_baru])], ignore_index=True)
            
            if safe_update("DATA_SK", df_final):
                st.session_state["last_data"] = data_baru
                st.session_state["last_berkas"] = sel_berkas
                st.session_state["show_confirm"] = False
                st.success("✅ Data Berhasil Diupdate!"); st.rerun()
                
        if col_conf2.button("❌ BATAL", use_container_width=True):
            st.session_state["show_confirm"] = False; st.rerun()

    if "last_data" in st.session_state:
        st.divider()
        last = st.session_state["last_data"]
        st.download_button(label="📥 DOWNLOAD PDF TANDA TERIMA", data=buat_pdf_full(last, st.session_state["last_berkas"]), file_name=f"TANDA_{last['No']}.pdf", mime="application/pdf")
    
    st.divider()
    st.subheader("📊 DATA TABEL GOOGLE SHEETS")
    if not df_sk.empty: 
        st.dataframe(df_sk.sort_values(by="No", ascending=False), use_container_width=True, hide_index=True)

def halaman_pengambilan():
    st.header("PENGAMBILAN BERKAS"); df_mentah = load_data("DATA_SK")
    if df_mentah.empty: st.warning("Data tidak ditemukan."); return
    df_belum_diambil = df_mentah[df_mentah["Tanggal_Pengambilan"] == "-"]
    no_cari = st.text_input("🔍 CARI NOMOR URUT:").strip()
    if no_cari:
        hasil = df_mentah[df_mentah["No"].str.strip() == no_cari]
        if not hasil.empty:
            data_row = hasil.iloc[0]
            if data_row["Tanggal_Pengambilan"] != "-":
                st.success(f"✅ Berkas Toko **{data_row['Nama_Toko']}** sudah diambil pada: {data_row['Tanggal_Pengambilan']}")
                st.download_button("🖨️ PRINT ULANG", data=cetak_overprint(data_row['Tanggal_Pengambilan']), file_name=f"AMBIL_{no_cari}.pdf")
            else:
                st.warning(f"🏪 Toko: {data_row['Nama_Toko']} (BELUM DIAMBIL)")
                tgl_ambil = st.text_input("📅 TANGGAL PENGAMBILAN:", value=datetime.now().strftime("%d-%m-%Y"))
                if st.button("✅ KONFIRMASI PENGAMBILAN"):
                    df_mentah.loc[df_mentah["No"].str.strip() == no_cari, "Tanggal_Pengambilan"] = tgl_ambil
                    if safe_update("DATA_SK", df_mentah): st.success("Konfirmasi berhasil!"); st.rerun()
        else: st.error("❌ Nomor Urut tidak terdaftar.")
    st.divider()
    st.subheader(f"📊 DAFTAR BERKAS BELUM DIAMBIL ({len(df_belum_diambil)} Berkas)")
    st.dataframe(df_belum_diambil.sort_values(by="No", ascending=True), use_container_width=True, hide_index=True)

# ==========================================
# 6. MODUL PARKIR (TANGGAL PINTAR)
# ==========================================
def halaman_parkir(menu_aktif):
    st.header(f"🚗 {menu_aktif}"); df_parkir = load_data("DATA_PARKIR")
    if menu_aktif == "INPUT REKAP":
        st.subheader("📝 FORM REKAP SETORAN")
        raw_tgl = st.text_input("MASUKKAN TANGGAL (Bisa 1/1/26)", value=datetime.now().strftime("%d-%m-%Y"))
        tgl_b = raw_tgl.replace("/", "-").strip()
        try:
            t_dt = pd.to_datetime(tgl_b, dayfirst=True)
            df_parkir['temp_tgl'] = pd.to_datetime(df_parkir['Tanggal'], dayfirst=True, errors='coerce')
            baris_cocok = df_parkir[df_parkir['temp_tgl'].dt.date == t_dt.date()]
        except: baris_cocok = df_parkir[df_parkir["Tanggal"].str.strip() == tgl_b]
            
        if not baris_cocok.empty:
            idx = baris_cocok.index[0]; row = baris_cocok.iloc[0]
            st.success(f"👤 PETUGAS: **{row['Nama_Petugas']}** | 📅 **{tgl_b}**")
            try: s2 = int(float(df_parkir.iloc[idx-1].get("Sisa_Karcis_r2", 0))) if idx > 0 else 0
            except: s2 = 0
            try: s4 = int(float(df_parkir.iloc[idx-1].get("Sisa_Karcis_r4", 0))) if idx > 0 else 0
            except: s4 = 0
            st.info(f"📊 SISA KEMARIN: R2={s2} | R4={s4}")
            with st.form("form_parkir"):
                c1, c2 = st.columns(2)
                p2=c1.number_input("AMBIL R2", 0); t2=c1.number_input("LAKU R2", 0); m2=c1.number_input("MPP R2", 0)
                p4=c2.number_input("AMBIL R4", 0); t4=c2.number_input("LAKU R4", 0); m4=c2.number_input("MPP R4", 0)
                if st.form_submit_button("💾 UPDATE DATA", type="primary"):
                    if 'temp_tgl' in df_parkir.columns: df_parkir = df_parkir.drop(columns=['temp_tgl'])
                    df_parkir.loc[idx, ["Pengambilan_Karcis_R2", "Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Karcis_r2", "Khusus_Roda_R2"]] = [str(p2), str(t2), str(m2), str((p2+s2)-t2), str(t2-m2)]
                    df_parkir.loc[idx, ["Pengambilan_Karcis_R4", "Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Karcis_r4", "Khusus_Roda_R4"]] = [str(p4), str(t4), str(m4), str((p4+s4)-t4), str(t4-m4)]
                    df_parkir.loc[idx, ["Status_Khusus", "Status_MPP"]] = ["BELUM", "BELUM"]
                    if safe_update("DATA_PARKIR", df_parkir): st.success("✅ BERHASIL!"); st.rerun()
        else: st.warning("⚠️ TANGGAL TIDAK DITEMUKAN.")
    elif menu_aktif == "KONFIRMASI":
        st.subheader("✅ Verifikasi Penerimaan")
        pen = df_parkir[(df_parkir["Status_Khusus"] == "BELUM") | (df_parkir["Status_MPP"] == "BELUM")]
        if pen.empty: st.info("Semua rekap sudah dikonfirmasi.")
        else:
            for index, row in pen.sort_values(by="No").iterrows():
                with st.expander(f"📦 Nomor: {row['No']} - {row['Nama_Petugas']} ({row['Tanggal']})"):
                    ck, cm = st.columns(2)
                    if row["Status_Khusus"] == "BELUM":
                        if ck.button(f"TERIMA KHUSUS #{row['No']}", key=f"kh_{index}", type="primary", use_container_width=True):
                            df_parkir.loc[index, "Status_Khusus"] = "SUDAH"; safe_update("DATA_PARKIR", df_parkir); st.rerun()
                    if row["Status_MPP"] == "BELUM":
                        if cm.button(f"TERIMA MPP #{row['No']}", key=f"mpp_{index}", type="primary", use_container_width=True):
                            df_parkir.loc[index, "Status_MPP"] = "SUDAH"; safe_update("DATA_PARKIR", df_parkir); st.rerun()
                    else: st.download_button("🖨️ CETAK", cetak_tanda_terima_parkir(row), f"MPP_{index}.pdf", key=f"dl_{index}")
    st.dataframe(df_parkir.sort_values(by="No", ascending=False), hide_index=True)

# ==========================================
# 7. MAIN APP (SPLASH SCREEN)
# ==========================================
def main():
    if "sudah_masuk" not in st.session_state: st.session_state["sudah_masuk"] = False
    if not st.session_state["sudah_masuk"]:
        st.write("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(URL_LOGO_HSS, width=250)
            st.markdown("<h2 style='text-align: center;'>Selamat Datang</h2><h1 style='text-align: center; color: #4CAF50;'>M. Luthfi Renaldi</h1>", unsafe_allow_html=True)
            if st.button("🚀 MASUK KE DASHBOARD", use_container_width=True, type="primary"):
                st.session_state["sudah_masuk"] = True; st.rerun()
    else:
        with st.sidebar:
            col_l, col_j = st.columns([1, 3])
            with col_l: st.image(URL_LOGO_HSS, width=50)
            with col_j: st.markdown("<h3 style='margin-top: 5px;'>UPTD PASAR</h3>", unsafe_allow_html=True)
            st.divider()
            modul = st.selectbox("PILIH MODUL:", ["SK TOKO", "PARKIR"])
            menu = st.radio("MENU:", ["INPUT REKAP", "KONFIRMASI"] if modul=="PARKIR" else ["PENGANTARAN", "PENGAMBILAN"])
        if modul == "PARKIR": halaman_parkir(menu)
        elif menu == "PENGANTARAN": halaman_pengantaran()
        else: halaman_pengambilan()

if __name__ == "__main__": main()
