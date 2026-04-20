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
        return df.astype(str).replace("nan", "-").replace("None", "-")
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
# 3. FUNGSI PDF
# ==========================================
def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    """
    Buat PDF 2 halaman (depan & belakang) untuk tanda terima berkas.
    
    Args:
        data: Dictionary berisi data pengantaran
        berkas_list: List berkas yang ADA
    
    Returns:
        BytesIO buffer berisi PDF
    """
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 12 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    
    # Konstanta layout
    X_POS = 1 * cm
    Y_POS = 1 * cm
    LEBAR = 22 * cm
    TENGAH = LEBAR / 2

    SEMUA_BERKAS = [
        "SK ASLI MENEMPATI",
        "PAS FOTO 3X4 (2 LBR)",
        "FC KTP PEMILIK",
        "FC KARTU SEWA",
        "SURAT KUASA",
        "SURAT KEHILANGAN",
    ]

    # ------------------------------------------
    # HALAMAN 1 - DEPAN
    # ------------------------------------------
    def gambar_border():
        c.setLineWidth(1.5)
        c.rect(X_POS, Y_POS, 20 * cm, 10 * cm)
        c.rect(X_POS + 0.15 * cm, Y_POS + 0.15 * cm, 19.7 * cm, 9.7 * cm)

    gambar_border()

    # Judul
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(
        TENGAH,
        Y_POS + 9.2 * cm,
        "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO",
    )

    # Subtitle info
    c.setFont("Helvetica", 8)
    c.drawCentredString(
        TENGAH,
        Y_POS + 8.7 * cm,
        f"No: {data.get('No', '-')}  |  "
        f"Tgl Terima: {data.get('Tanggal_Pengantaran', '-')}  |  "
        f"Tgl Ambil: {data.get('Tanggal_Pengambilan', '-')}",
    )

    # Daftar berkas
    yy = Y_POS + 7.8 * cm
    for i, item in enumerate(SEMUA_BERKAS, 1):
        ada = item in berkas_list

        # Nama berkas
        c.setFont("Helvetica-BoldOblique", 9)
        c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")

        # Status ADA / TIDAK ADA
        x_status = X_POS + 14 * cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x_status, yy, "ADA   /   TIDAK ADA")

        # Garis bawah pada pilihan yang sesuai
        if ada:
            # Garis bawah "ADA"
            c.line(
                x_status,
                yy - 0.05 * cm,
                x_status + 1.4 * cm,
                yy - 0.05 * cm,
            )
        else:
            # Garis bawah "TIDAK ADA"
            c.line(
                x_status + 2.2 * cm,
                yy - 0.05 * cm,
                x_status + 5.5 * cm,
                yy - 0.05 * cm,
            )

        yy -= 0.65 * cm

    # Garis pemisah tanda tangan
    c.setLineWidth(1)
    c.line(
        X_POS + 0.15 * cm,
        Y_POS + 2.8 * cm,
        X_POS + 19.85 * cm,
        Y_POS + 2.8 * cm,
    )
    c.line(TENGAH, Y_POS + 0.15 * cm, TENGAH, Y_POS + 2.8 * cm)

    # Label tanda tangan
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(X_POS + 5 * cm, Y_POS + 2.4 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(X_POS + 15 * cm, Y_POS + 2.4 * cm, "PETUGAS PENERIMA")

    # Nama tanda tangan
    c.setFont("Helvetica-Bold", 10)
    nama_pengantar = str(data.get("Nama_Pengantar_Berkas", "-")).upper()
    nama_penerima = str(data.get("Penerima_Berkas", "-")).upper()
    c.drawCentredString(X_POS + 5 * cm, Y_POS + 0.5 * cm, f"( {nama_pengantar} )")
    c.drawCentredString(X_POS + 15 * cm, Y_POS + 0.5 * cm, f"( {nama_penerima} )")

    c.showPage()

    # ------------------------------------------
    # HALAMAN 2 - BELAKANG
    # ------------------------------------------
    gambar_border()

    # Judul halaman belakang
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(TENGAH, Y_POS + 9.3 * cm, "DETAIL PENGANTARAN BERKAS")

    # Tabel informasi
    ROWS = [
        ("NO. URUT", data.get("No", "-")),
        ("TGL TERIMA", data.get("Tanggal_Pengantaran", "-")),
        ("TGL AMBIL", data.get("Tanggal_Pengambilan", "-")),
        ("NAMA TOKO", str(data.get("Nama_Toko", "-")).upper()),
        ("NO. TOKO", str(data.get("No_Toko", "-")).upper()),
        ("PEMILIK SK", str(data.get("Nama_Pemilik_Asli", "-")).upper()),
        ("PENGANTAR", str(data.get("Nama_Pengantar_Berkas", "-")).upper()),
        ("PENERIMA", str(data.get("Penerima_Berkas", "-")).upper()),
    ]

    TINGGI_BARIS = 0.75 * cm
    LEBAR_LABEL = 4.5 * cm
    LEBAR_NILAI = 14.5 * cm
    y_tab = Y_POS + 8.8 * cm

    for label, val in ROWS:
        # Sel label
        c.setLineWidth(0.5)
        c.rect(X_POS + 0.15 * cm, y_tab - TINGGI_BARIS, LEBAR_LABEL, TINGGI_BARIS)
        # Sel nilai
        c.rect(
            X_POS + 0.15 * cm + LEBAR_LABEL,
            y_tab - TINGGI_BARIS,
            LEBAR_NILAI,
            TINGGI_BARIS,
        )

        c.setFont("Helvetica-Bold", 8)
        c.drawString(X_POS + 0.3 * cm, y_tab - 0.52 * cm, label)

        c.setFont("Helvetica", 9)
        c.drawString(
            X_POS + 0.15 * cm + LEBAR_LABEL + 0.2 * cm,
            y_tab - 0.52 * cm,
            str(val),
        )

        y_tab -= TINGGI_BARIS

    # Berkas yang dibawa (ringkasan)
    berkas_str = ", ".join(berkas_list) if berkas_list else "TIDAK ADA"
    c.setFont("Helvetica-Bold", 8)
    c.drawString(X_POS + 0.5 * cm, Y_POS + 2.6 * cm, "BERKAS YANG DIBAWA:")
    c.setFont("Helvetica", 7.5)

    # Wrap text jika panjang
    maks_char = 90
    if len(berkas_str) > maks_char:
        c.drawString(X_POS + 0.5 * cm, Y_POS + 2.2 * cm, berkas_str[:maks_char])
        c.drawString(X_POS + 0.5 * cm, Y_POS + 1.8 * cm, berkas_str[maks_char:])
    else:
        c.drawString(X_POS + 0.5 * cm, Y_POS + 2.2 * cm, berkas_str)

    # Catatan perhatian
    c.setFont("Helvetica-Bold", 8)
    c.drawString(X_POS + 0.5 * cm, Y_POS + 1.5 * cm, "PERHATIAN:")
    c.setFont("Helvetica", 7.5)
    c.drawString(
        X_POS + 0.5 * cm,
        Y_POS + 1.1 * cm,
        "1. Simpan tanda terima ini untuk mengambil SK asli.",
    )
    c.drawString(
        X_POS + 0.5 * cm,
        Y_POS + 0.75 * cm,
        "2. Kehilangan tanda terima harap melapor ke petugas UPTD.",
    )
    c.drawString(
        X_POS + 0.5 * cm,
        Y_POS + 0.4 * cm,
        "3. Pengambilan tidak dapat diwakilkan tanpa surat kuasa.",
    )

    c.save()
    buffer.seek(0)
    return buffer


# ==========================================
# 4. MODUL SK TOKO - PENGANTARAN
# ==========================================
def halaman_pengantaran():
    st.header("📝 INPUT PENGANTARAN BERKAS")

    df_sk = load_data("DATA_SK")

    # Info statistik singkat
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(df_sk) if not df_sk.empty else 0
    sudah_ambil = (
        len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"])
        if not df_sk.empty
        else 0
    )
    belum_ambil = total - sudah_ambil

    col_stat1.metric("📦 Total Berkas", total)
    col_stat2.metric("✅ Sudah Diambil", sudah_ambil)
    col_stat3.metric("⏳ Belum Diambil", belum_ambil)

    st.divider()

    SEMUA_BERKAS = [
        "SK ASLI MENEMPATI",
        "PAS FOTO 3X4 (2 LBR)",
        "FC KTP PEMILIK",
        "FC KARTU SEWA",
        "SURAT KUASA",
        "SURAT KEHILANGAN",
    ]

    # State untuk menyimpan berkas yang dipilih (di luar form)
    if "sel_berkas" not in st.session_state:
        st.session_state["sel_berkas"] = []

    # Pilih berkas DI LUAR form agar tidak reset
    st.subheader("☑️ Pilih Berkas yang Dibawa:")
    cols_berkas = st.columns(3)
    sel_berkas = []
    for i, item in enumerate(SEMUA_BERKAS):
        with cols_berkas[i % 3]:
            if st.checkbox(item, key=f"cb_{item}"):
                sel_berkas.append(item)

    st.divider()

    # Form input data
    with st.form("form_pengantaran", clear_on_submit=False):
        st.subheader("📋 Data Pengantaran")

        next_no = get_next_no(df_sk)

        col1, col2 = st.columns(2)

        with col1:
            no_urut = st.text_input(
                "NO. URUT *",
                value=str(next_no),
                help="Nomor urut otomatis, bisa diubah",
            )
            tgl_terima = st.text_input(
                "TANGGAL TERIMA *",
                value=datetime.now().strftime("%d-%m-%Y"),
                help="Format: DD-MM-YYYY",
            )
            nama_toko = st.text_input("NAMA TOKO *").strip().upper()
            no_toko = st.text_input("NOMOR TOKO *").strip().upper()

        with col2:
            nama_pemilik = st.text_input("NAMA PEMILIK SK *").strip().upper()
            nama_pengantar = st.text_input("NAMA PENGANTAR *").strip().upper()
            nama_penerima = st.text_input("NAMA PENERIMA *").strip().upper()

        submitted = st.form_submit_button("💾 SIMPAN DATA", type="primary")

        if submitted:
            # Validasi
            errors = []
            if not no_urut.strip():
                errors.append("No. Urut wajib diisi")
            if not nama_toko:
                errors.append("Nama Toko wajib diisi")
            if not no_toko:
                errors.append("Nomor Toko wajib diisi")
            if not nama_pemilik:
                errors.append("Nama Pemilik wajib diisi")
            if not nama_pengantar:
                errors.append("Nama Pengantar wajib diisi")
            if not nama_penerima:
                errors.append("Nama Penerima wajib diisi")

            # Cek duplikat No Urut
            if not df_sk.empty and no_urut.strip() in df_sk["No"].str.strip().values:
                errors.append(f"No. Urut {no_urut} sudah ada!")

            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                new_row = {
                    "No": no_urut.strip(),
                    "Tanggal_Pengantaran": tgl_terima,
                    "Tanggal_Pengambilan": "-",
                    "Nama_Toko": nama_toko,
                    "No_Toko": no_toko,
                    "Nama_Pemilik_Asli": nama_pemilik,
                    "Nama_Pengantar_Berkas": nama_pengantar,
                    "Penerima_Berkas": nama_penerima,
                }

                df_baru = pd.concat(
                    [df_sk, pd.DataFrame([new_row])],
                    ignore_index=True,
                )

                if safe_update("DATA_SK", df_baru):
                    st.session_state["last_data"] = new_row
                    st.session_state["last_berkas"] = sel_berkas
                    st.success(
                        f"✅ Data No. {no_urut} berhasil disimpan!"
                    )
                    st.balloons()

    # Tombol download PDF (di luar form agar tetap muncul)
    if "last_data" in st.session_state and st.session_state["last_data"]:
        st.divider()
        st.subheader("📄 Download Tanda Terima")

        last = st.session_state["last_data"]
        st.info(
            f"**No:** {last['No']} | "
            f"**Toko:** {last['Nama_Toko']} | "
            f"**Pemilik:** {last['Nama_Pemilik_Asli']}"
        )

        pdf_buffer = buat_pdf_full(last, st.session_state.get("last_berkas", []))
        st.download_button(
            label="📥 DOWNLOAD PDF TANDA TERIMA",
            data=pdf_buffer,
            file_name=f"TANDA_TERIMA_{last['No']}_{last['Nama_Toko']}.pdf",
            mime="application/pdf",
            type="primary",
        )

        if st.button("🔄 Input Baru", type="secondary"):
            del st.session_state["last_data"]
            del st.session_state["last_berkas"]
            st.rerun()

    # Tabel data terbaru
    st.divider()
    st.subheader("📊 Data Terbaru (10 Record Terakhir)")
    if not df_sk.empty:
        st.dataframe(
            df_sk.tail(10).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
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

    # Filter tampilkan yang belum diambil
    col_filter, col_search = st.columns([1, 2])

    with col_filter:
        tampilkan = st.selectbox(
            "Tampilkan:",
            ["Semua", "Belum Diambil", "Sudah Diambil"],
        )

    with col_search:
        no_cari = st.text_input(
            "🔍 CARI NOMOR URUT:",
            placeholder="Masukkan nomor urut...",
        ).strip()

    # Filter data untuk tabel
    df_tampil = df_sk.copy()
    if tampilkan == "Belum Diambil":
        df_tampil = df_tampil[df_tampil["Tanggal_Pengambilan"] == "-"]
    elif tampilkan == "Sudah Diambil":
        df_tampil = df_tampil[df_tampil["Tanggal_Pengambilan"] != "-"]

    # Pencarian spesifik
    if no_cari:
        hasil = df_sk[df_sk["No"].str.strip() == no_cari]

        if not hasil.empty:
            data_row = hasil.iloc[0]
            sudah_ambil = data_row["Tanggal_Pengambilan"] != "-"

            st.divider()

            # Info card
            col_info1, col_info2, col_info3 = st.columns(3)
            col_info1.metric("🏪 Nama Toko", data_row["Nama_Toko"])
            col_info2.metric("👤 Pemilik", data_row["Nama_Pemilik_Asli"])
            col_info3.metric(
                "📅 Tgl Terima",
                data_row["Tanggal_Pengantaran"],
            )

            if sudah_ambil:
                st.success(
                    f"✅ Berkas ini sudah diambil pada: "
                    f"**{data_row['Tanggal_Pengambilan']}**"
                )
            else:
                st.warning("⏳ Berkas BELUM diambil.")

                tgl_ambil = st.text_input(
                    "📅 TANGGAL PENGAMBILAN:",
                    value=datetime.now().strftime("%d-%m-%Y"),
                )

                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    if st.button("✅ KONFIRMASI PENGAMBILAN", type="primary"):
                        mask = df_sk["No"].str.strip() == no_cari
                        df_sk.loc[mask, "Tanggal_Pengambilan"] = tgl_ambil

                        if safe_update("DATA_SK", df_sk):
                            st.success(
                                f"✅ Berkas No. {no_cari} berhasil diupdate!"
                            )
                            st.rerun()
        else:
            st.error(f"❌ Nomor urut **{no_cari}** tidak ditemukan!")

    # Tabel data
    st.divider()
    st.subheader(f"📊 Data ({tampilkan}): {len(df_tampil)} record")

    if not df_tampil.empty:
        # Highlight belum diambil
        def highlight_row(row):
            if row["Tanggal_Pengambilan"] == "-":
                return ["background-color: #fff3cd"] * len(row)
            return ["background-color: #d4edda"] * len(row)

        st.dataframe(
            df_tampil.reset_index(drop=True).style.apply(highlight_row, axis=1),
            use_container_width=True,
            hide_index=True,
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
                tgl = st.text_input(
                    "TANGGAL",
                    value=datetime.now().strftime("%d-%m-%Y"),
                )
                nama = st.text_input("NAMA").strip().upper()

            with col2:
                no_kendaraan = st.text_input("NO. KENDARAAN").strip().upper()
                jenis = st.selectbox(
                    "JENIS KENDARAAN",
                    ["MOTOR", "MOBIL", "TRUK", "LAINNYA"],
                )
                tarif = st.number_input(
                    "TARIF (Rp)", min_value=0, step=500, value=2000
                )

            if st.form_submit_button("💾 SIMPAN", type="primary"):
                new_row = {
                    "No": no_urut,
                    "Tanggal": tgl,
                    "Nama": nama,
                    "No_Kendaraan": no_kendaraan,
                    "Jenis": jenis,
                    "Tarif": tarif,
                }
                df_baru = pd.concat(
                    [df_parkir, pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                if safe_update("DATA_PARKIR", df_baru):
                    st.success("✅ Data parkir berhasil disimpan!")

    with tab2:
        df_parkir = load_data("DATA_PARKIR")
        if not df_parkir.empty:
            # Summary
            try:
                total_tarif = pd.to_numeric(
                    df_parkir["Tarif"], errors="coerce"
                ).sum()
                col1, col2 = st.columns(2)
                col1.metric("🚗 Total Kendaraan", len(df_parkir))
                col2.metric("💰 Total Tarif", f"Rp {total_tarif:,.0f}")
            except Exception:
                pass

            st.dataframe(
                df_parkir.reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Belum ada data parkir.")


# ==========================================
# 7. MAIN APP
# ==========================================
def main():
    # Sidebar
    with st.sidebar:
        st.image(
            "https://via.placeholder.com/200x80?text=UPTD+PASAR",
            use_column_width=True,
        )
        st.title("🗂️ DASHBOARD UPTD")
        st.caption("PASAR KANDANGAN")
        st.divider()

        modul = st.selectbox(
            "📁 PILIH MODUL:",
            ["SK TOKO", "PARKIR"],
        )

        if modul == "SK TOKO":
            menu = st.radio(
                "📋 MENU SK TOKO:",
                ["PENGANTARAN", "PENGAMBILAN"],
            )
        else:
            menu = None

        st.divider()
        st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Routing
    if modul == "SK TOKO":
        if menu == "PENGANTARAN":
            halaman_pengantaran()
        elif menu == "PENGAMBILAN":
            halaman_pengambilan()
    elif modul == "PARKIR":
        halaman_parkir()


if __name__ == "__main__":
    main()
