# ==========================================
# pages/2_🅿️_Parkir.py
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css
from utils.helpers import (
    WS_PARKIR,
    load_data,
    safe_update,
    format_tgl_hari_indo,
    cari_tanggal_belum_input_parkir,
    daftar_tanggal_kosong_bulan_ini,
    daftar_tanggal_belum_konfirmasi_bulan_ini,
    tombol_refresh,
    tampilkan_n_terakhir
)
from utils.pdf_generator import cetak_tanda_terima_parkir

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Parkir | UPTD Pasar Kandangan",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# ==========================================
# KONEKSI
# ==========================================
conn_parkir = st.connection("gsheets_parkir", type=GSheetsConnection)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    logo_b64 = st.session_state.get("logo_b64")
    if logo_b64:
        st.markdown(
            f"""
            <div style="text-align:center; padding:18px 0 6px 0;">
                <img src="data:image/png;base64,{logo_b64}"
                     width="78" height="auto"
                     style="display:inline-block;
                            filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4));">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="text-align:center; padding:18px 0 6px 0;">
                <div style="font-size:3rem;">🏛️</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div style="text-align:center; padding:4px 0 14px 0;
                    border-bottom:1px solid rgba(255,255,255,0.08);
                    margin-bottom:14px;">
            <p style="font-family:'Inter',sans-serif;
                      font-size:1.05rem; font-weight:800;
                      color:#f1f5f9 !important;
                      letter-spacing:-0.02em;
                      margin:0 0 4px 0; line-height:1.3;">
                UPTD PASAR KANDANGAN
            </p>
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.78rem; font-weight:600;
                      color:#94a3b8 !important;
                      letter-spacing:0.04em;
                      margin:0; line-height:1.4;">
                KABUPATEN HULU SUNGAI SELATAN
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.page_link("app_web.py", label="🏠  Beranda", use_container_width=True)

    st.markdown(
        """
        <div style="padding: 8px 4px 4px 4px;">
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.7rem; font-weight:600;
                      color:#64748b !important;
                      text-transform:uppercase;
                      letter-spacing:0.06em;
                      margin:0 0 6px 0;">
                MODUL
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.page_link(
        "pages/1_📋_SK_Toko.py",
        label="📋  SK Toko",
        use_container_width=True
    )
    st.page_link(
        "pages/2_🅿️_Parkir.py",
        label="🅿️  Parkir",
        use_container_width=True
    )
    st.page_link(
        "pages/3_💰_Kas.py",
        label="💰  Kas UPTD",
        use_container_width=True
    )

    st.markdown(
        """
        <div style="text-align:center; padding:24px 0 8px 0;
                    border-top:1px solid rgba(255,255,255,0.06);
                    margin-top:40px;">
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.56rem; font-weight:400;
                      color:#64748b !important;
                      margin:0; line-height:1.7;">
                Developed by
            </p>
            <p style="font-family:'Inter',sans-serif;
                      font-size:0.68rem; font-weight:700;
                      color:#94a3b8 !important;
                      margin:2px 0 0 0;">
                M. Luthfi Renaldi
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# HELPER LOKAL
# ==========================================
def parse_tanggal_input(tgl_input_user: str):
    try:
        tgl_bersih = str(tgl_input_user).strip().replace("/", "-")
        if len(tgl_bersih.split("-")[-1]) == 2:
            return datetime.strptime(tgl_bersih, "%d-%m-%y").date()
        return datetime.strptime(tgl_bersih, "%d-%m-%Y").date()
    except:
        return None

def ambil_info_tanggal_parkir(df_p: pd.DataFrame, tgl_input_user: str):
    dt_user = parse_tanggal_input(tgl_input_user)
    if dt_user is None or df_p.empty or "Tanggal" not in df_p.columns:
        return None, pd.DataFrame(), None, "-", 0, 0

    df = df_p.copy()
    df["Tgl_Temp"] = pd.to_datetime(df["Tanggal"], dayfirst=True, errors="coerce").dt.date
    baris = df[df["Tgl_Temp"] == dt_user]

    if baris.empty:
        return dt_user, pd.DataFrame(), None, "-", 0, 0

    idx = baris.index[0]
    nama_p = baris.iloc[0]["Nama_Petugas"]

    df_petugas_sama = df[(df["Nama_Petugas"] == nama_p) & (df.index < idx)]
    if not df_petugas_sama.empty:
        idx_terakhir_petugas = df_petugas_sama.index[-1]
        sisa_r2 = pd.to_numeric(df_petugas_sama.loc[idx_terakhir_petugas, "Sisa_Stok_R2"], errors="coerce")
        sisa_r4 = pd.to_numeric(df_petugas_sama.loc[idx_terakhir_petugas, "Sisa_Stok_R4"], errors="coerce")
    else:
        sisa_r2 = 0
        sisa_r4 = 0

    sisa_r2 = 0 if pd.isna(sisa_r2) else int(sisa_r2)
    sisa_r4 = 0 if pd.isna(sisa_r4) else int(sisa_r4)

    return dt_user, baris, idx, nama_p, sisa_r2, sisa_r4

def render_log_rekap(df_p: pd.DataFrame, dt_user):
    with st.expander("📊 LOG INPUT & STATUS BULAN INI", expanded=False):
        if "Total_Karcis_R2" not in df_p.columns:
            st.info("Belum ada data.")
            return

        df_isi = df_p[
            (df_p["Total_Karcis_R2"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""])) |
            (df_p["Total_Karcis_R4"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""]))
        ].copy()

        if not df_isi.empty:
            df_isi["Tgl_Sort"] = pd.to_datetime(df_isi["Tanggal"], dayfirst=True, errors="coerce").dt.date
            last = df_isi[df_isi["Tgl_Sort"] == dt_user] if dt_user else pd.DataFrame()
            if last.empty:
                last = df_isi.sort_values(by="Tgl_Sort", ascending=False).head(1)
            else:
                last = last.head(1)

            kolom = ["Tanggal", "Nama_Petugas", "Total_Karcis_R2", "Total_Karcis_R4", "MPP_Roda_R2", "MPP_Roda_R4"]
            kolom_ada = [k for k in kolom if k in last.columns]
            st.subheader("📋 Input Terakhir")
            st.dataframe(last[kolom_ada], hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada data yang diinput.")

        st.divider()
        st.subheader("📅 Tanggal Belum Diinput (Awal Bulan s/d Hari Ini)")
        df_kosong_bulan = daftar_tanggal_kosong_bulan_ini(df_p)
        if not df_kosong_bulan.empty:
            st.dataframe(df_kosong_bulan, hide_index=True, use_container_width=True)
        else:
            st.success("✅ Tidak ada tanggal kosong bulan ini.")

def render_log_stok(df_p: pd.DataFrame, dt_user):
    with st.expander("📊 LOG INPUT & STATUS BULAN INI", expanded=False):
        if "Pengambilan_Karcis_R2" not in df_p.columns:
            st.info("Belum ada data.")
            return

        df_isi = df_p[
            (df_p["Pengambilan_Karcis_R2"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""])) |
            (df_p["Pengambilan_Karcis_R4"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""]))
        ].copy()

        if not df_isi.empty:
            df_isi["Tgl_Sort"] = pd.to_datetime(df_isi["Tanggal"], dayfirst=True, errors="coerce").dt.date
            last = df_isi[df_isi["Tgl_Sort"] == dt_user] if dt_user else pd.DataFrame()
            if last.empty:
                last = df_isi.sort_values(by="Tgl_Sort", ascending=False).head(1)
            else:
                last = last.head(1)

            kolom = ["Tanggal", "Nama_Petugas", "Pengambilan_Karcis_R2", "Pengambilan_Karcis_R4"]
            kolom_ada = [k for k in kolom if k in last.columns]
            st.subheader("📋 Input Terakhir")
            st.dataframe(last[kolom_ada], hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada data yang diinput.")

        st.divider()
        st.subheader("📅 Tanggal Belum Diinput (Awal Bulan s/d Hari Ini)")
        df_kosong_bulan = daftar_tanggal_kosong_bulan_ini(df_p)
        if not df_kosong_bulan.empty:
            st.dataframe(df_kosong_bulan, hide_index=True, use_container_width=True)
        else:
            st.success("✅ Tidak ada tanggal kosong bulan ini.")

def render_log_konfirmasi(df_p: pd.DataFrame):
    with st.expander("📊 LOG INPUT & STATUS BULAN INI", expanded=False):
        if "Status_Khusus" not in df_p.columns:
            st.info("Belum ada data.")
            return

        df_isi = df_p[
            (df_p["Status_Khusus"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""])) |
            (df_p["Status_MPP"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""])) |
            (df_p["Status_Cetak"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""]))
        ].copy()

        if not df_isi.empty:
            df_isi["Tgl_Sort"] = pd.to_datetime(df_isi["Tanggal"], dayfirst=True, errors="coerce")
            last = df_isi.sort_values(by="Tgl_Sort", ascending=False).head(1)
            kolom = ["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"]
            kolom_ada = [k for k in kolom if k in last.columns]
            st.subheader("📋 Konfirmasi Terakhir")
            st.dataframe(last[kolom_ada], hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada data yang diinput.")

        st.divider()
        st.subheader("⏳ Tanggal Belum Selesai Konfirmasi (Awal Bulan s/d Hari Ini)")
        df_belum_konfirmasi = daftar_tanggal_belum_konfirmasi_bulan_ini(df_p)
        if not df_belum_konfirmasi.empty:
            st.dataframe(df_belum_konfirmasi, hide_index=True, use_container_width=True)
        else:
            st.success("✅ Semua konfirmasi bulan ini sudah selesai.")

# ==========================================
# LOAD DATA
# ==========================================
df_p = load_data(conn_parkir, WS_PARKIR)

# ==========================================
# HEADER PAGE
# ==========================================
st.title("🅿️ MODUL PARKIR")

if df_p.empty:
    st.warning("⚠️ Data PARKIR kosong atau worksheet tidak ditemukan.")
    st.stop()

hari_ini = datetime.now().date()

tab1, tab2, tab3 = st.tabs(["📝 INPUT REKAP", "📦 INPUT STOK", "✅ KONFIRMASI"])

# ==========================================
# TAB 1 - INPUT REKAP
# ==========================================
with tab1:
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.subheader("📝 INPUT REKAP HARIAN")
    with c_btn:
        tombol_refresh("ref_parkir_rekap")

    tgl_belum, df_belum = cari_tanggal_belum_input_parkir(df_p)
    if tgl_belum:
        st.warning(f"⚠️ Input parkir belum terisi mulai: **{tgl_belum.strftime('%d-%m-%Y')}**")
        with st.expander("📅 Lihat daftar tanggal yang belum diinput", expanded=False):
            if not df_belum.empty:
                tampil = df_belum[["Tanggal", "Nama_Petugas"]].copy()
                st.dataframe(tampil, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Semua data parkir sampai hari ini sudah terinput.")

    tgl_input_user = st.text_input(
        "🔍 MASUKKAN TANGGAL",
        value=datetime.now().strftime("%d-%m-%Y"),
        key="tgl_input_parkir_rekap"
    )

    dt_user, baris, idx, nama_p, sisa_r2, sisa_r4 = ambil_info_tanggal_parkir(df_p, tgl_input_user)

    if baris.empty or idx is None:
        st.warning("⚠️ Tanggal belum ada di jadwal Sheet. Silakan isi jadwal dulu.")
    else:
        st.success(f"👤 PETUGAS: **{nama_p}** | 📅 **{format_tgl_hari_indo(tgl_input_user)}**")
        col_s1, col_s2 = st.columns(2)
        col_s1.metric(f"📊 Sisa Karcis R2 ({nama_p})", int(sisa_r2))
        col_s2.metric(f"📊 Sisa Karcis R4 ({nama_p})", int(sisa_r4))

        with st.form("form_rekap_harian", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                tr2 = st.number_input("TOTAL KARCIS R2", min_value=0)
                mr2 = st.number_input("MPP RODA R2", min_value=0)
            with c2:
                tr4 = st.number_input("TOTAL KARCIS R4", min_value=0)
                mr4 = st.number_input("MPP RODA R4", min_value=0)

            cb1, cb2 = st.columns(2)
            with cb1:
                subm = st.form_submit_button("💾 SIMPAN REKAP", type="primary", use_container_width=True)
            with cb2:
                reset = st.form_submit_button("🔄 RESET FORM", use_container_width=True)

            if reset:
                st.rerun()

            if subm:
                pk2_lama = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R2"], errors='coerce')
                pk4_lama = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R4"], errors='coerce')
                pk2_lama = 0 if pd.isna(pk2_lama) else pk2_lama
                pk4_lama = 0 if pd.isna(pk4_lama) else pk4_lama

                sn2 = (pk2_lama + sisa_r2) - tr2
                sn4 = (pk4_lama + sisa_r4) - tr4

                tr2_str = str(tr2) if tr2 > 0 else "0"
                tr4_str = str(tr4) if tr4 > 0 else "0"

                karcis_r2_sekarang = str(df_p.loc[idx, "Total_Karcis_R2"]).strip()
                sudah_diisi = karcis_r2_sekarang not in ["-", "nan", ""]

                data_baru = {
                    "tr2_str": tr2_str,
                    "mr2_str": str(mr2),
                    "sn2_str": str(sn2),
                    "kh2_str": str(tr2 - mr2),
                    "tr4_str": tr4_str,
                    "mr4_str": str(mr4),
                    "sn4_str": str(sn4),
                    "kh4_str": str(tr4 - mr4)
                }

                if sudah_diisi:
                    st.session_state["pending_parkir"] = data_baru
                    st.session_state["pending_idx"] = idx
                    st.session_state["show_confirm_parkir"] = True
                else:
                    df_update = df_p.copy()
                    df_update.loc[idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [
                        data_baru["tr2_str"], data_baru["mr2_str"], data_baru["sn2_str"], data_baru["kh2_str"]
                    ]
                    df_update.loc[idx, ["Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [
                        data_baru["tr4_str"], data_baru["mr4_str"], data_baru["sn4_str"], data_baru["kh4_str"]
                    ]
                    df_update.loc[idx, ["Status_Khusus", "Status_MPP", "Status_Cetak"]] = ["BELUM", "BELUM", "BELUM"]
                    if safe_update(conn_parkir, WS_PARKIR, df_update):
                        st.success("✅ Berhasil Diupdate!")
                        st.rerun()

        if st.session_state.get("show_confirm_parkir"):
            st.warning(f"⚠️ Data setoran untuk tanggal **{tgl_input_user}** sudah pernah diisi! Yakin ingin menimpanya?")
            col_c1, col_c2 = st.columns(2)
            if col_c1.button("✅ YA, TIMPA DATA", type="primary", key="btn_timpa_parkir"):
                d = st.session_state["pending_parkir"]
                p_idx = st.session_state["pending_idx"]

                df_update = df_p.copy()
                df_update.loc[p_idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [
                    d["tr2_str"], d["mr2_str"], d["sn2_str"], d["kh2_str"]
                ]
                df_update.loc[p_idx, ["Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [
                    d["tr4_str"], d["mr4_str"], d["sn4_str"], d["kh4_str"]
                ]
                if str(df_update.loc[p_idx, "Status_Cetak"]).strip() != "SUDAH":
                    df_update.loc[p_idx, ["Status_Khusus", "Status_MPP", "Status_Cetak"]] = ["BELUM", "BELUM", "BELUM"]

                if safe_update(conn_parkir, WS_PARKIR, df_update):
                    st.session_state["show_confirm_parkir"] = False
                    st.success("✅ Berhasil Ditimpa!")
                    st.rerun()

            if col_c2.button("❌ BATAL", key="btn_batal_parkir"):
                st.session_state["show_confirm_parkir"] = False
                st.rerun()

    render_log_rekap(df_p, dt_user)

# ==========================================
# TAB 2 - INPUT STOK
# ==========================================
with tab2:
    c_head2, c_btn2 = st.columns([0.88, 0.12])
    c_head2.subheader("📦 INPUT STOK BARU")
    with c_btn2:
        tombol_refresh("ref_parkir_stok")

    # SESUAI PERMINTAAN: jangan tampilkan success
    tgl_belum_stok, df_belum_stok = cari_tanggal_belum_input_parkir(df_p)
    if tgl_belum_stok:
        st.warning(f"⚠️ Input parkir belum terisi mulai: **{tgl_belum_stok.strftime('%d-%m-%Y')}**")
        with st.expander("📅 Lihat daftar tanggal yang belum diinput", expanded=False):
            if not df_belum_stok.empty:
                tampil = df_belum_stok[["Tanggal", "Nama_Petugas"]].copy()
                st.dataframe(tampil, use_container_width=True, hide_index=True)

    tgl_input_stok = st.text_input(
        "🔍 MASUKKAN TANGGAL",
        value=datetime.now().strftime("%d-%m-%Y"),
        key="tgl_input_parkir_stok"
    )

    dt_user_stok, baris_stok, idx_stok, nama_p_stok, sisa_r2_stok, sisa_r4_stok = ambil_info_tanggal_parkir(df_p, tgl_input_stok)

    if baris_stok.empty or idx_stok is None:
        st.warning("⚠️ Tanggal belum ada di jadwal Sheet. Silakan isi jadwal dulu.")
    else:
        st.info(f"Mengisi stok baru untuk petugas: **{nama_p_stok}**")

        with st.form("form_stok_baru", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                pk2 = st.number_input("PENGAMBILAN KARCIS R2", min_value=0)
            with c2:
                pk4 = st.number_input("PENGAMBILAN KARCIS R4", min_value=0)

            cb1, cb2 = st.columns(2)
            with cb1:
                subm_stok = st.form_submit_button("➕ TAMBAH STOK", type="primary", use_container_width=True)
            with cb2:
                reset_stok = st.form_submit_button("🔄 RESET FORM", use_container_width=True)

            if reset_stok:
                st.rerun()

            if subm_stok:
                df_update = df_p.copy()
                df_update.loc[idx_stok, ["Pengambilan_Karcis_R2", "Pengambilan_Karcis_R4"]] = [str(pk2), str(pk4)]
                if safe_update(conn_parkir, WS_PARKIR, df_update):
                    st.success("✅ Stok Berhasil Ditambahkan!")
                    st.rerun()

    render_log_stok(df_p, dt_user_stok)

# ==========================================
# TAB 3 - KONFIRMASI
# ==========================================
with tab3:
    c_head3, c_btn3 = st.columns([0.88, 0.12])
    c_head3.subheader("✅ KONFIRMASI SETORAN")
    with c_btn3:
        tombol_refresh("ref_parkir_konfirmasi")

    if "Total_Karcis_R2" not in df_p.columns or "Total_Karcis_R4" not in df_p.columns:
        st.error("❌ Kolom tidak ditemukan di worksheet DATA_PARKIR.")
    else:
        kondisi_angka_r2 = df_p["Total_Karcis_R2"].astype(str).str.strip().str.isnumeric()
        kondisi_angka_r4 = df_p["Total_Karcis_R4"].astype(str).str.strip().str.isnumeric()
        df_pen = df_p[kondisi_angka_r2 | kondisi_angka_r4].copy()

        if df_pen.empty:
            st.info("TIDAK ADA DATA KONFIRMASI.")
        else:
            df_pen["Tgl_Temp"] = pd.to_datetime(df_pen["Tanggal"], dayfirst=True, errors="coerce").dt.date
            df_terfilter = df_pen[
                (df_pen["Status_Khusus"] != "SUDAH") |
                (df_pen["Status_MPP"] != "SUDAH") |
                (df_pen["Status_Cetak"] != "SUDAH") |
                (df_pen["Tgl_Temp"] == hari_ini)
            ].copy()

            if df_terfilter.empty:
                st.info("TIDAK ADA DATA KONFIRMASI (Semua data lama sudah Lunas).")
            else:
                df_terfilter = df_terfilter.sort_index(ascending=False).head(10)

                for i, row in df_terfilter.iterrows():
                    stat_k = str(row.get("Status_Khusus", "BELUM")).strip()
                    stat_m = str(row.get("Status_MPP", "BELUM")).strip()
                    stat_c = str(row.get("Status_Cetak", "BELUM")).strip()
                    lunas = (stat_k == "SUDAH") and (stat_m == "SUDAH") and (stat_c == "SUDAH")
                    ikon = "✅ [SELESAI]" if lunas else "📦 [BELUM SELESAI]"

                    with st.expander(f"{ikon} {row['Tanggal']} - {row['Nama_Petugas']}", expanded=not lunas):
                        if lunas:
                            st.success("✨ PROSES SELESAI: Data ini akan otomatis hilang besok.")

                        ck, cm_col = st.columns(2)

                        with ck:
                            st.write(f"**KHUSUS**\nR2: {row.get('Khusus_Roda_R2','-')} | R4: {row.get('Khusus_Roda_R4','-')}")
                            if stat_k != "SUDAH":
                                if st.button("TERIMA KHUSUS", key=f"k_{i}", use_container_width=True):
                                    df_update = df_p.copy()
                                    df_update.loc[i, "Status_Khusus"] = "SUDAH"
                                    if safe_update(conn_parkir, WS_PARKIR, df_update):
                                        st.rerun()
                            else:
                                st.success("✅ Khusus Diterima")

                        with cm_col:
                            st.write(f"**MPP**\nR2: {row.get('MPP_Roda_R2','-')} | R4: {row.get('MPP_Roda_R4','-')}")
                            if stat_m != "SUDAH":
                                if st.button("TERIMA MPP", key=f"m_{i}", type="primary", use_container_width=True):
                                    df_update = df_p.copy()
                                    df_update.loc[i, "Status_MPP"] = "SUDAH"
                                    if safe_update(conn_parkir, WS_PARKIR, df_update):
                                        st.rerun()
                            else:
                                st.download_button(
                                    "🖨️ CETAK PDF MPP",
                                    data=cetak_tanda_terima_parkir(row.to_dict()),
                                    file_name=f"MPP_{row['Tanggal']}.pdf",
                                    key=f"p_{i}",
                                    use_container_width=True
                                )
                                if stat_c != "SUDAH":
                                    if st.button("✅ SUDAH CETAK", key=f"c_{i}", use_container_width=True):
                                        df_update = df_p.copy()
                                        df_update.loc[i, "Status_Cetak"] = "SUDAH"
                                        if safe_update(conn_parkir, WS_PARKIR, df_update):
                                            st.rerun()
                                else:
                                    st.success("✅ Telah Dicetak")

    render_log_konfirmasi(df_p)
