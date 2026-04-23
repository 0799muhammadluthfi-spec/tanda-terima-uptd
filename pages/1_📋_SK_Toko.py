# ==========================================
# pages/1_📋_SK_Toko.py
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css
from utils.helpers import (
    WS_SK,
    load_data,
    safe_update,
    get_next_no,
    normalisasi_no,
    format_tgl_hari_indo,
    urutkan_no,
    tampilkan_n_terakhir,
    tombol_refresh
)
from utils.pdf_generator import buat_pdf_full, cetak_overprint

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="SK Toko | UPTD Pasar Kandangan",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_css()

# ==========================================
# KONEKSI
# ==========================================
conn_sk = st.connection("gsheets_sk", type=GSheetsConnection)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    logo_b64 = st.session_state.get("logo_b64")
    if logo_b64:
        st.markdown(
            f'<div style="text-align:center; padding:18px 0 6px 0;">'
            f'<img src="data:image/png;base64,{logo_b64}" width="78" height="auto" '
            f'style="display:inline-block; filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4));">'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="text-align:center; padding:18px 0 6px 0;">'
            '<div style="font-size:3rem;">🏛️</div></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div style="text-align:center; padding:4px 0 14px 0;
                    border-bottom:1px solid rgba(255,255,255,0.08);
                    margin-bottom:14px;">
            <p style="font-family:'Inter',sans-serif; font-size:1.05rem; font-weight:800;
                      color:#f1f5f9 !important; letter-spacing:-0.02em;
                      margin:0 0 4px 0; line-height:1.3;">
                UPTD PASAR KANDANGAN</p>
            <p style="font-family:'Inter',sans-serif; font-size:0.78rem; font-weight:600;
                      color:#94a3b8 !important; letter-spacing:0.04em;
                      margin:0; line-height:1.4;">
                KABUPATEN HULU SUNGAI SELATAN</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.page_link("app_web.py", label="🏠  Beranda", use_container_width=True)

    st.markdown(
        '<div style="padding: 8px 4px 4px 4px;">'
        '<p style="font-family:\'Inter\',sans-serif; font-size:0.7rem; font-weight:600;'
        'color:#64748b !important; text-transform:uppercase; letter-spacing:0.06em;'
        'margin:0 0 6px 0;">MODUL</p></div>',
        unsafe_allow_html=True
    )

    st.page_link("pages/1_📋_SK_Toko.py", label="📋  SK TOKO", use_container_width=True)
    st.page_link("pages/2_🅿️_Parkir.py", label="🅿️  PARKIR", use_container_width=True)
    st.page_link("pages/3_💰_Kas.py", label="💰  KAS UPTD", use_container_width=True)

    st.markdown(
        """
        <div style="text-align:center; padding:24px 0 8px 0;
                    border-top:1px solid rgba(255,255,255,0.06); margin-top:40px;">
            <p style="font-family:'Inter',sans-serif; font-size:0.56rem;
                      color:#64748b !important; margin:0; line-height:1.7;">Developed by</p>
            <p style="font-family:'Inter',sans-serif; font-size:0.68rem; font-weight:700;
                      color:#94a3b8 !important; margin:2px 0 0 0;">M. Luthfi Renaldi</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# MENU TAB
# ==========================================
tab1, tab2 = st.tabs(["📝 PENGANTARAN", "📤 PENGAMBILAN"])

# ==========================================
# TAB 1 - PENGANTARAN
# ==========================================
with tab1:
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.header("📝 INPUT PENGANTARAN BERKAS")
    with c_btn:
        tombol_refresh("ref_pengantaran")

    df_sk = load_data(conn_sk, WS_SK)

    # Statistik
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(df_sk[df_sk["No"] != "-"]) if not df_sk.empty else 0
    sudah_ambil = len(df_sk[df_sk["Tanggal_Pengambilan"] != "-"]) if not df_sk.empty else 0
    col_stat1.metric("📦 Total Berkas", total)
    col_stat2.metric("✅ Sudah Diambil", sudah_ambil)
    col_stat3.metric("⏳ Belum Diambil", total - sudah_ambil)

    # Pilih berkas
    SEMUA_BERKAS = [
        "SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK",
        "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"
    ]

    st.subheader("☑️ Pilih Berkas yang Dibawa:")
    cols_berkas = st.columns(3)
    sel_berkas = []
    for i, item in enumerate(SEMUA_BERKAS):
        with cols_berkas[i % 3]:
            if st.checkbox(item, key=f"cb_{item}"):
                sel_berkas.append(item)

    st.divider()

    # Form input
    with st.form("form_pengantaran", clear_on_submit=False):
        st.subheader("📋 Data Pengantaran")
        next_no = get_next_no(df_sk)
        col1, col2 = st.columns(2)
        with col1:
            no_urut = st.text_input("NOMOR URUT *", value=str(next_no))
            tgl_terima = st.text_input("TANGGAL TERIMA *", value=datetime.now().strftime("%d-%m-%Y"))
            nama_toko = st.text_input("NAMA TOKO *").strip().upper()
            no_toko = st.text_input("NOMOR TOKO *").strip().upper()
            no_nik = st.text_input("NO NIK PEMILIK ASLI").strip()

        with col2:
            nama_pemilik = st.text_input("NAMA PEMILIK SK *").strip().upper()
            alamat = st.text_input("ALAMAT PEMILIK ASLI").strip().upper()
            nama_pengantar = st.text_input("NAMA PENGANTAR *").strip().upper()
            nama_penerima = st.text_input("NAMA PENERIMA *").strip().upper()

        b1, b2 = st.columns(2)
        with b1:
            submit_sk = st.form_submit_button("💾 SIMPAN DATA", type="primary", use_container_width=True)
        with b2:
            reset_sk = st.form_submit_button("🔄 RESET FORM", use_container_width=True)

        if reset_sk:
            st.rerun()

        if submit_sk:
            if not no_urut.strip() or not nama_toko or not nama_pemilik:
                st.error("❌ Data Wajib Diisi!")
            else:
                is_exist = (
                    not df_sk.empty and
                    normalisasi_no(no_urut) in df_sk["No"].apply(normalisasi_no).values
                )
                new_row = {
                    "No": no_urut.strip(),
                    "Tanggal_Pengantaran": tgl_terima,
                    "Tanggal_Pengambilan": "-",
                    "Nama_Toko": nama_toko,
                    "No_Toko": no_toko,
                    "Nama_Pemilik_Asli": nama_pemilik,
                    "No_NIK": no_nik if no_nik else "-",
                    "Alamat": alamat if alamat else "-",
                    "Nama_Pengantar_Berkas": nama_pengantar,
                    "Penerima_Berkas": nama_penerima
                }
                if is_exist:
                    st.session_state["pending_sk"] = new_row
                    st.session_state["show_confirm_sk"] = True
                else:
                    df_baru = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                    if safe_update(conn_sk, WS_SK, df_baru):
                        st.session_state["last_sk"] = new_row
                        st.session_state["last_berkas"] = sel_berkas
                        st.success("✅ Berhasil!")
                        st.rerun()

    # Konfirmasi timpa
    if st.session_state.get("show_confirm_sk"):
        st.warning("⚠️ Nomor sudah ada!")
        col_c1, col_c2 = st.columns(2)
        if col_c1.button("✅ YA, TIMPA DATA", type="primary", key="timpa_sk"):
            d = st.session_state["pending_sk"]
            df_sk = df_sk[df_sk["No"] != d["No"]]
            df_final = pd.concat([df_sk, pd.DataFrame([d])], ignore_index=True)
            if safe_update(conn_sk, WS_SK, df_final):
                st.session_state["last_sk"] = d
                st.session_state["last_berkas"] = sel_berkas
                st.session_state["show_confirm_sk"] = False
                st.rerun()
        if col_c2.button("❌ BATAL", key="batal_sk"):
            st.session_state["show_confirm_sk"] = False
            st.rerun()

    # Download PDF
    if "last_sk" in st.session_state:
        st.divider()
        l = st.session_state["last_sk"]
        st.download_button(
            "📥 DOWNLOAD PDF TANDA TERIMA",
            data=buat_pdf_full(l, st.session_state.get("last_berkas", [])),
            file_name=f"TANDA_{l['No']}.pdf",
            mime="application/pdf"
        )

    # Tabel data
    st.divider()
    st.subheader("📊 DATA TERAKHIR (30 Data)")
    if not df_sk.empty:
        df_tampil = df_sk[df_sk["No"] != "-"].copy()
        st.dataframe(
            tampilkan_n_terakhir(df_tampil, 30),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Belum ada data.")

# ==========================================
# TAB 2 - PENGAMBILAN
# ==========================================
with tab2:
    c_head2, c_btn2 = st.columns([0.88, 0.12])
    c_head2.header("📤 PENGAMBILAN BERKAS SK")
    with c_btn2:
        tombol_refresh("ref_ambil")

    df_m = load_data(conn_sk, WS_SK)

    if df_m.empty:
        st.warning("⚠️ Data kosong atau worksheet tidak ditemukan.")
    else:
        df_b = df_m[(df_m["Tanggal_Pengambilan"] == "-") & (df_m["No"] != "-")]

        no_cari = st.text_input(
            "🔍 CARI NOMOR URUT:",
            key="cari_no_sk",
            placeholder="Masukkan nomor urut, misal 1"
        ).strip()

        if no_cari:
            no_cari_norm = normalisasi_no(no_cari)
            mask_no = df_m["No"].apply(normalisasi_no) == no_cari_norm
            hasil = df_m[mask_no]

            if not hasil.empty:
                data = hasil.iloc[0]
                sudah = data["Tanggal_Pengambilan"] != "-"

                if sudah:
                    st.success(
                        f"✅ Sudah diambil pada: "
                        f"{format_tgl_hari_indo(data['Tanggal_Pengambilan'])}"
                    )
                    st.download_button(
                        "🖨️ PRINT ULANG",
                        data=cetak_overprint(data["Tanggal_Pengambilan"]),
                        file_name=f"AMBIL_{no_cari_norm}.pdf"
                    )
                else:
                    st.warning(f"👤 {data['Nama_Pemilik_Asli']}")
                    tgl_a = st.text_input(
                        "📅 TANGGAL AMBIL:",
                        value=datetime.now().strftime("%d-%m-%Y"),
                        key="tgl_ambil_sk"
                    )
                    if st.button("✅ KONFIRMASI PENGAMBILAN", type="primary"):
                        df_m.loc[mask_no, "Tanggal_Pengambilan"] = tgl_a
                        if safe_update(conn_sk, WS_SK, df_m):
                            st.success("✅ Berhasil!")
                            st.rerun()
            else:
                st.error("❌ Nomor Urut tidak terdaftar.")

        st.divider()
        st.subheader(f"📊 BELUM DIAMBIL ({len(df_b)})")
        if not df_b.empty:
            st.dataframe(
                urutkan_no(df_b, ascending=True),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("✅ Semua berkas sudah diambil.")
