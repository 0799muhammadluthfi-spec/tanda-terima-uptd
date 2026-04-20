import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI
# ==========================================
st.set_page_config(
    page_title="UPTD PASAR KANDANGAN",
    page_icon="🏪",
    layout="wide"
)

conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI HELPER
# ==========================================
def load_data(worksheet: str) -> pd.DataFrame:
    """Load data dari Google Sheets dengan error handling."""
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        # FIX PENCARIAN 1.0 -> 1 
        df = df.astype(str).replace(r'\.0$', '', regex=True).replace("nan", "-").replace("None", "-")
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return pd.DataFrame()

def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    """Hitung nomor urut berikutnya."""
    try:
        if df.empty or col not in df.columns:
            return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except Exception:
        return 1

def safe_update(worksheet: str, data: pd.DataFrame) -> bool:
    """Update Google Sheets dengan error handling."""
    try:
        conn.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")
        return False

# ==========================================
# 3. FUNGSI PDF (VERSI F4 PORTRAIT - CETAK DI ATAS)
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    # KERTAS FULL F4 PORTRAIT (21.5 cm x 33 cm)
    # Printer setting harus PORTRAIT (Berdiri) & Kertas F4/Folio
    UKURAN_KERTAS = (21.5 * cm, 33 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)
    
    # Koordinat ditaruh di paling atas kertas
    Y_BASE = 21.5 * cm # Jarak dari bawah kertas, menyisakan ruang 11.5cm di atas
    X_POS = 0.75 * cm 
    LEBAR = 21.5 * cm
    TENGAH = LEBAR / 2

    # ------------------------------------------
    # HALAMAN 1 - DEPAN
    # ------------------------------------------
    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, 20 * cm, 10 * cm) # Bingkai Luar
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, 19.7 * cm, 9.7 * cm) # Bingkai Dalam

    # Judul
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(TENGAH, Y_BASE + 8.8 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    
    # Garis Judul (Ketebalan 2)
    c.setLineWidth(2)
    c.line(TENGAH - 5.5*cm, Y_BASE + 8.5*cm, TENGAH + 5.5*cm, Y_BASE + 8.5*cm)

    # Checklist Berkas
    yy = Y_BASE + 7.5 * cm
    SEMUA_BERKAS = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    
    for i, item in enumerate(SEMUA_BERKAS, 1):
        c.setFont("Helvetica-BoldOblique", 10)
        c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")
        
        c.setFont("Helvetica-Bold", 10)
        x_status = X_POS + 14 * cm
        c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        
        # Coretan (Ketebalan 1.5) & Panjang disesuaikan
        c.setLineWidth(1.5)
        y_strike = yy + 0.11 * cm 
        if item in berkas_list:
            # Coret TIDAK ADA (Panjang sudah diperpendek)
            c.line(x_status + 1.4 * cm, y_strike, x_status + 3.5 * cm, y_strike)
        else:
            # Coret ADA
            c.line(x_status - 0.1 * cm, y_strike, x_status + 0.8 * cm, y_strike)
        yy -= 0.7 * cm

    # Garis Tanda Tangan (Ketebalan 1.5)
    c.setLineWidth(1.5)
    c.line(X_POS + 0.15 * cm, Y_BASE + 3.0 * cm, X_POS + 19.85 * cm, Y_BASE + 3.0 * cm) 
    c.line(TENGAH, Y_BASE + 0.15 * cm, TENGAH, Y_BASE + 3.0 * cm) 

    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(X_POS + 5 * cm, Y_BASE + 2.5 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 2.5 * cm, "PETUGAS PENERIMA")

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(X_POS + 5 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Nama_Pengantar_Berkas', '')).upper()} )")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm, f"( {str(data.get('Penerima_Berkas', '')).upper()} )")

    c.showPage()

    # ------------------------------------------
    # HALAMAN 2 - BELAKANG
    # ------------------------------------------
    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, 20 * cm, 10 * cm)
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, 19.7 * cm, 9.7 * cm)

    # Memulai tabel PERSIS dari garis kotak dalam bagian atas, agar tidak ada sisa kolom
    y_tab = Y_BASE + 9.85 * cm 
    TINGGI_B = 1.15 * cm
    
    tgl_ambil_pdf = data.get("Tanggal_Pengambilan", "-")
    if tgl_ambil_pdf in ["-", "nan", "NAN", ""]:
        tgl_ambil_pdf = ""

    DETAIL_ROWS = [
        ("NOMOR", data.get("No", "-")),
        ("TGL TERIMA", data.get("Tanggal_Pengantaran", "-")),
        ("TGL AMBIL", tgl_ambil_pdf),
        ("NAMA & NO. TOKO", f"{data.get('Nama_Toko', '-')} - {data.get('No_Toko', '-')}"),
        ("PEMILIK (SK)", data.get("Nama_Pemilik_Asli", "-"))
    ]

    for label, val in DETAIL_ROWS:
        c.setLineWidth(1.5) 
        c.rect(X_POS + 0.15 * cm, y_tab - TINGGI_B, 6 * cm, TINGGI_B)
        c.rect(X_POS + 6.15 * cm, y_tab - TINGGI_B, 13.7 * cm, TINGGI_B)
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(X_POS + 0.5 * cm, y_tab - 0.7 * cm, label)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(X_POS + 6.5 * cm, y_tab - 0.7 * cm, str(val).upper())
        y_tab -= TINGGI_B

    # Teks Perhatian Baru
    c.setFont("Helvetica-Bold", 10)
    c.drawString(X_POS + 0.6 * cm, Y_BASE + 2.8 * cm, "PERHATIAN:")
    c.setFont("Helvetica", 9)
    c.drawString(X_POS + 0.6 * cm, Y_BASE + 2.2 * cm, "1. Simpan tanda terima ini sebagai syarat pengambilan SK asli.")
    c.drawString(X_POS + 0.6 * cm, Y_BASE + 1.6 * cm, "2. Pengambilan SK hanya dapat dilakukan di jam kerja UPTD.")

    c.save()
    buffer.seek(0)
    return buffer

def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO()
    # Overprint juga disesuaikan dengan F4 Portrait
    c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm))
    c.setFont("Helvetica-Bold", 10)
    
    Y_BASE = 21.5 * cm
    X_POS = 0.75 * cm
    # Koordinat presisi di dalam kotak TGL AMBIL
    y_target = Y_BASE + 6.8 * cm 
    c.drawString(X_POS + 6.5 * cm, y_target, tgl_ambil.upper())
    
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 4. MODUL SK TOKO - PENGANTARAN
# ==========================================
def halaman_pengantaran():
    st.header("📝 INPUT PENGANTARAN BERKAS")

    df_sk = load_data("DATA_SK")

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(df_sk) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    belum_ambil = total - sudah_ambil

    col_stat1.metric("📦 Total Berkas", total)
    col_stat2.metric("✅ Sudah Diambil", sudah_ambil)
    col_stat3.metric("⏳ Belum Diambil", belum_ambil)

    st.divider()

    SEMUA_BERKAS = [
        "SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", 
        "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"
    ]

    if "sel_berkas" not in st.session_state:
        st.session_state["sel_berkas"] = []

    st.subheader("☑️ Pilih Berkas yang Dibawa:")
    cols_berkas = st.columns(3)
    sel_berkas = []
    for i, item in enumerate(SEMUA_BERKAS):
        with cols_berkas[i % 3]:
            if st.checkbox(item, key=f"cb_{item}"):
                sel_berkas.append(item)

    st.divider()

    with st.form("form_pengantaran", clear_on_submit=False):
        st.subheader("📋 Data Pengantaran")
        next_no = get_next_no(df_sk)
        col1, col2 = st.columns(2)

        with col1:
            no_urut = st.text_input("NO. URUT *", value=str(next_no), help="Nomor urut otomatis")
            tgl_terima = st.text_input("TANGGAL TERIMA *", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = st.text_input("NAMA TOKO *").strip().upper()
            no_toko = st.text_input("NOMOR TOKO *").strip().upper()

        with col2:
            nama_pemilik = st.text_input("NAMA PEMILIK SK *").strip().upper()
            nama_pengantar = st.text_input("NAMA PENGANTAR *").strip().upper()
            nama_penerima = st.text_input("NAMA PENERIMA *").strip().upper()

        submitted = st.form_submit_button("💾 SIMPAN DATA", type="primary")

        if submitted:
            errors = []
            if not no_urut.strip(): errors.append("No. Urut wajib diisi")
            if not nama_toko: errors.append("Nama Toko wajib diisi")
            if not nama_pemilik: errors.append("Nama Pemilik wajib diisi")

            if not df_sk.empty and no_urut.strip() in df_sk["No"].str.strip().values:
                errors.append(f"No. Urut {no_urut} sudah ada!")

            if errors:
                for err in errors: st.error(f"❌ {err}")
            else:
                new_row = {
                    "No": no_urut.strip(), "Tanggal_Pengantaran": tgl_terima,
                    "Tanggal_Pengambilan": "-", "Nama_Toko": nama_toko, "No_Toko": no_toko,
                    "Nama_Pemilik_Asli": nama_pemilik, "Nama_Pengantar_Berkas": nama_pengantar,
                    "Penerima_Berkas": nama_penerima,
                }

                df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)

                if safe_update("DATA_SK", df_baru):
                    st.session_state["last_data"] = new_row
                    st.session_state["last_berkas"] = sel_berkas
                    st.success(f"✅ Data No. {no_urut} berhasil disimpan!")
                    st.balloons()

    if "last_data" in st.session_state and st.session_state["last_data"]:
        st.divider()
        st.subheader("📄 Download Tanda Terima")
        last = st.session_state["last_data"]
        st.info(f"**No:** {last['No']} | **Toko:** {last['Nama_Toko']} | **Pemilik:** {last['Nama_Pemilik_Asli']}")

        pdf_buffer = buat_pdf_full(last, st.session_state.get("last_berkas", []))
        st.download_button(
            label="📥 DOWNLOAD PDF TANDA TERIMA", data=pdf_buffer,
            file_name=f"TANDA_TERIMA_{last['No']}_{last['Nama_Toko']}.pdf",
            mime="application/pdf", type="primary",
        )

        if st.button("🔄 Input Baru", type="secondary"):
            del st.session_state["last_data"]
            del st.session_state["last_berkas"]
            st.rerun()

    st.divider()
    st.subheader("📊 Data Terbaru (10 Record Terakhir)")
    if not df_sk.empty:
        st.dataframe(df_sk.tail(10).reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data.")

# ==========================================
# 5. MODUL SK TOKO - PENGAMBILAN
# ==========================================
def halaman_pengambilan():
    st.header("🏁 PENGAMBILAN BERKAS")

    df_sk = load_data("DATA_SK")
    if df_sk.empty:
        st.warning("Tidak ada data tersedia.")
        return

    col_filter, col_search = st.columns([1, 2])
    with col_filter:
        tampilkan = st.selectbox("Tampilkan:", ["Semua", "Belum Diambil", "Sudah Diambil"])
    with col_search:
        no_cari = st.text_input("🔍 CARI NOMOR URUT:", placeholder="Masukkan nomor urut...").strip()

    df_tampil = df_sk.copy()
    if tampilkan == "Belum Diambil":
        df_tampil = df_tampil[df_tampil["Tanggal_Pengambilan"] == "-"]
    elif tampilkan == "Sudah Diambil":
        df_tampil = df_tampil[df_tampil["Tanggal_Pengambilan"] != "-"]

    if no_cari:
        hasil = df_sk[df_sk["No"].str.strip() == no_cari]
        if not hasil.empty:
            data_row = hasil.iloc[0]
            sudah_ambil = data_row["Tanggal_Pengambilan"] not in ["-", "nan", "NAN", ""]

            st.divider()
            col_info1, col_info2, col_info3 = st.columns(3)
            col_info1.metric("🏪 Nama Toko", data_row["Nama_Toko"])
            col_info2.metric("👤 Pemilik", data_row["Nama_Pemilik_Asli"])
            col_info3.metric("📅 Tgl Terima", data_row["Tanggal_Pengantaran"])

            if sudah_ambil:
                st.success(f"✅ Berkas ini sudah diambil pada: **{data_row['Tanggal_Pengambilan']}**")
                st.download_button(
                    label="🖨️ PRINT ULANG TANGGAL AMBIL",
                    data=cetak_overprint(data_row['Tanggal_Pengambilan']),
                    file_name=f"OVERPRINT_{no_cari}.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("⏳ Berkas BELUM diambil.")
                tgl_ambil = st.text_input("📅 TANGGAL PENGAMBILAN:", value=datetime.now().strftime("%d-%m-%Y"))

                if st.button("✅ KONFIRMASI PENGAMBILAN", type="primary"):
                    mask = df_sk["No"].str.strip() == no_cari
                    df_sk.loc[mask, "Tanggal_Pengambilan"] = tgl_ambil
                    
                    if safe_update("DATA_SK", df_sk):
                        st.session_state['ready_to_print_overprint'] = tgl_ambil
                        st.session_state['print_no'] = no_cari
                        st.success(f"✅ Berkas No. {no_cari} berhasil diupdate!")

            if st.session_state.get('print_no') == no_cari:
                st.write("---")
                st.download_button(
                    label="🖨️ PRINT TANGGAL AMBIL DI KERTAS SEKARANG",
                    data=cetak_overprint(st.session_state['ready_to_print_overprint']),
                    file_name=f"OVERPRINT_{no_cari}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
        else:
            st.error(f"❌ Nomor urut **{no_cari}** tidak ditemukan!")

    st.divider()
    st.subheader(f"📊 Data ({tampilkan}): {len(df_tampil)} record")

    if not df_tampil.empty:
        def highlight_row(row):
            if row["Tanggal_Pengambilan"] in ["-", "", "nan"]:
                return ["background-color: #fff3cd"] * len(row)
            return ["background-color: #d4edda"] * len(row)

        st.dataframe(
            df_tampil.reset_index(drop=True).style.apply(highlight_row, axis=1),
            use_container_width=True, hide_index=True
        )
    else:
        st.info(f"Tidak ada data untuk kategori: {tampilkan}")

# ==========================================
# 6. MODUL PARKIR
# ==========================================
def halaman_parkir():
    st.header("🚗 MANAJEMEN PARKIR")
    tab1, tab2 = st.tabs(["📝 Input Parkir", "📊 Data Parkir"])

    with tab1:
        df_parkir = load_data("DATA_PARKIR")
        next_no = get_next_no(df_parkir)

        with st.form("form_parkir"):
            col1, col2 = st.columns(2)
            with col1:
                no_urut = st.text_input("NO. URUT", value=str(next_no))
                tgl = st.text_input("TANGGAL", value=datetime.now().strftime("%d-%m-%Y"))
                nama = st.text_input("NAMA").strip().upper()
            with col2:
                no_kendaraan = st.text_input("NO. KENDARAAN").strip().upper()
                jenis = st.selectbox("JENIS KENDARAAN", ["MOTOR", "MOBIL", "TRUK", "LAINNYA"])
                tarif = st.number_input("TARIF (Rp)", min_value=0, step=500, value=2000)

            if st.form_submit_button("💾 SIMPAN", type="primary"):
                new_row = {"No": no_urut, "Tanggal": tgl, "Nama": nama, "No_Kendaraan": no_kendaraan, "Jenis": jenis, "Tarif": tarif}
                df_baru = pd.concat([df_parkir, pd.DataFrame([new_row])], ignore_index=True)
                if safe_update("DATA_PARKIR", df_baru):
                    st.success("✅ Data parkir berhasil disimpan!")

    with tab2:
        df_parkir = load_data("DATA_PARKIR")
        if not df_parkir.empty:
            try:
                total_tarif = pd.to_numeric(df_parkir["Tarif"], errors="coerce").sum()
                col1, col2 = st.columns(2)
                col1.metric("🚗 Total Kendaraan", len(df_parkir))
                col2.metric("💰 Total Tarif", f"Rp {total_tarif:,.0f}")
            except Exception: pass
            st.dataframe(df_parkir.reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data parkir.")

# ==========================================
# 7. MAIN APP
# ==========================================
def main():
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80?text=UPTD+PASAR", use_column_width=True)
        st.title("🗂️ DASHBOARD UPTD")
        st.caption("PASAR KANDANGAN")
        st.divider()
        modul = st.selectbox("📁 PILIH MODUL:", ["SK TOKO", "PARKIR"])
        if modul == "SK TOKO":
            menu = st.radio("📋 MENU SK TOKO:", ["PENGANTARAN", "PENGAMBILAN"])
        else:
            menu = None
        st.divider()
        st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    if modul == "SK TOKO":
        if menu == "PENGANTARAN": halaman_pengantaran()
        elif menu == "PENGAMBILAN": halaman_pengambilan()
    elif modul == "PARKIR":
        halaman_parkir()

if __name__ == "__main__":
    main()
