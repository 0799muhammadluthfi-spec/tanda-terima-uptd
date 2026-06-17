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
    today_wita
)
from utils.pdf_generator import cetak_tanda_terima_parkir
from utils.auth import wajib_login

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Parkir | UPTD Pasar Kandangan",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_css()
wajib_login()

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

    st.markdown("""
    <div style="text-align:center; padding:4px 0 14px 0;
                border-bottom:1px solid rgba(255,255,255,0.08);
                margin-bottom:14px;">
        <p style="font-family:'Inter',sans-serif; font-size:1.05rem; font-weight:800;
                  color:#f1f5f9 !important; margin:0 0 4px 0;">
            UPTD PASAR KANDANGAN</p>
        <p style="font-family:'Inter',sans-serif; font-size:0.78rem; font-weight:600;
                  color:#94a3b8 !important; margin:0;">
            KABUPATEN HULU SUNGAI SELATAN</p>
    </div>
    """, unsafe_allow_html=True)

    st.page_link("Home.py", label="🏠  Beranda", use_container_width=True)

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
        '<div style="padding: 16px 4px 4px 4px;">'
        '<p style="font-family:\'Inter\',sans-serif; font-size:0.7rem; font-weight:600;'
        'color:#64748b !important; text-transform:uppercase; letter-spacing:0.06em;'
        'margin:0 0 6px 0;">SISTEM</p></div>',
        unsafe_allow_html=True
    )

    st.page_link("pages/4_⚙️_Pengaturan.py", label="⚙️  PENGATURAN", use_container_width=True)

    st.markdown("""
    <div style="text-align:center; padding:24px 0 8px 0;
                border-top:1px solid rgba(255,255,255,0.06); margin-top:40px;">
        <p style="font-family:'Inter',sans-serif; font-size:0.56rem;
                  color:#64748b !important; margin:0;">Developed by</p>
        <p style="font-family:'Inter',sans-serif; font-size:0.68rem; font-weight:700;
                  color:#94a3b8 !important; margin:2px 0 0 0;">M. Luthfi Renaldi</p>
    </div>
    """, unsafe_allow_html=True)

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


def to_int_input(val, default=0):
    try:
        txt = str(val).strip().replace(",", ".")
        if txt == "":
            return default
        return int(float(txt))
    except:
        return default


def ambil_info_tanggal_parkir(df_p, tgl_input_user):
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

    df_petugas_sebelum = df[
        (df["Nama_Petugas"] == nama_p) &
        (df["Tgl_Temp"].notna()) &
        (df["Tgl_Temp"] < dt_user)
    ].copy()

    df_petugas_sebelum = df_petugas_sebelum[
        ~df_petugas_sebelum["Sisa_Stok_R2"].astype(str).str.strip().isin(["-", "nan", "", "None"])
    ]

    if not df_petugas_sebelum.empty:
        df_petugas_sebelum = df_petugas_sebelum.sort_values(by="Tgl_Temp", ascending=False)
        baris_terakhir = df_petugas_sebelum.iloc[0]
        sisa_r2 = pd.to_numeric(baris_terakhir.get("Sisa_Stok_R2", 0), errors="coerce")
        sisa_r4 = pd.to_numeric(baris_terakhir.get("Sisa_Stok_R4", 0), errors="coerce")
    else:
        sisa_r2 = 0
        sisa_r4 = 0

    sisa_r2 = 0 if pd.isna(sisa_r2) else int(sisa_r2)
    sisa_r4 = 0 if pd.isna(sisa_r4) else int(sisa_r4)

    return dt_user, baris, idx, nama_p, sisa_r2, sisa_r4


def render_log_rekap(df_p, dt_user):
    with st.expander("LOG INPUT & STATUS BULAN INI", expanded=False):
        if df_p.empty or "Tanggal" not in df_p.columns:
            st.info("Belum ada data.")
            return

        if "Total_Karcis_R2" not in df_p.columns or "Total_Karcis_R4" not in df_p.columns:
            st.info("Kolom total karcis belum tersedia.")
            return

        hari_ini = today_wita()
        awal_bulan = hari_ini.replace(day=1)

        df = df_p.copy()
        df["Tgl_Bersih"] = df["Tanggal"].astype(str).str.strip().str.replace("/", "-", regex=False)
        df["Tgl_Sort"] = pd.to_datetime(df["Tgl_Bersih"], dayfirst=True, errors="coerce").dt.date

        df = df[
            (df["Tgl_Sort"].notna()) &
            (df["Tgl_Sort"] >= awal_bulan) &
            (df["Tgl_Sort"] <= hari_ini)
        ].copy()

        def is_kosong(v):
            txt = str(v).strip().lower().replace("\xa0", "").replace("\t", "")
            return txt in ["", "-", "nan", "none", "null", "<na>", "<n/a>"]

        df_sudah = df[
            ~(df["Total_Karcis_R2"].apply(is_kosong) & df["Total_Karcis_R4"].apply(is_kosong))
        ].copy()

        df_kosong = df[
            (df["Total_Karcis_R2"].apply(is_kosong) & df["Total_Karcis_R4"].apply(is_kosong))
        ].copy()

        if "Status_Libur" in df_kosong.columns:
            df_kosong = df_kosong[
                df_kosong["Status_Libur"].astype(str).str.strip().str.upper() != "LIBUR"
            ]

        st.subheader("Input Terakhir")
        if not df_sudah.empty:
            last = df_sudah.sort_values(by="Tgl_Sort", ascending=False).head(1)
            kolom = ["Tanggal", "Nama_Petugas", "Total_Karcis_R2", "Total_Karcis_R4", "MPP_Roda_R2", "MPP_Roda_R4"]
            kolom_ada = [k for k in kolom if k in last.columns]
            st.dataframe(last[kolom_ada], hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada data yang diinput.")

        st.divider()
        st.subheader("Tanggal Belum Diinput (Awal Bulan s/d Hari Ini)")
        if not df_kosong.empty:
            st.dataframe(
                df_kosong.sort_values("Tgl_Sort")[["Tanggal", "Nama_Petugas"]],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.success("Tidak ada tanggal kosong bulan ini.")


def render_log_stok(df_p, pakai_expander=True):
    def _isi():
        if "Sisa_Stok_R2" not in df_p.columns or "Nama_Petugas" not in df_p.columns:
            st.info("Belum ada data.")
            return

        hari_ini = today_wita()
        semua_petugas = df_p["Nama_Petugas"].unique()

        df_stok = df_p.copy()
        df_stok["Tgl_Sort"] = pd.to_datetime(
            df_stok["Tanggal"].astype(str).str.strip().str.replace("/", "-", regex=False),
            dayfirst=True, errors="coerce"
        ).dt.date

        df_stok = df_stok[
            (df_stok["Tgl_Sort"].notna()) &
            (df_stok["Tgl_Sort"] <= hari_ini)
        ]

        def is_ada_stok(v):
            txt = str(v).strip().lower()
            if txt in ["", "-", "nan", "none", "null", "<na>"]:
                return False
            try:
                float(txt)
                return True
            except:
                return False

        df_ada_stok = df_stok[
            df_stok["Sisa_Stok_R2"].apply(is_ada_stok) | df_stok["Sisa_Stok_R4"].apply(is_ada_stok)
        ].copy()

        if not df_ada_stok.empty:
            df_ada_stok = df_ada_stok.sort_values("Tgl_Sort", ascending=False)

        ada_data = False
        for petugas in semua_petugas:
            if str(petugas).strip() in ["-", "nan", "", "None", "null"]:
                continue

            data_petugas = df_ada_stok[df_ada_stok["Nama_Petugas"] == petugas]

            if not data_petugas.empty:
                row = data_petugas.iloc[0]
                sisa_r2_raw = str(row["Sisa_Stok_R2"]).strip()
                sisa_r4_raw = str(row["Sisa_Stok_R4"]).strip()

                try:
                    sisa_r2 = int(float(sisa_r2_raw)) if sisa_r2_raw.lower() not in ["-", "nan", "", "none", "null"] else 0
                except:
                    sisa_r2 = 0

                try:
                    sisa_r4 = int(float(sisa_r4_raw)) if sisa_r4_raw.lower() not in ["-", "nan", "", "none", "null"] else 0
                except:
                    sisa_r4 = 0

                tgl_terakhir = str(row["Tanggal"]).strip()
                if tgl_terakhir.lower() in ["-", "nan", "", "none"]:
                    tgl_terakhir = "-"

                st.markdown(f"### {petugas}")
                st.caption(f"Data stok terakhir: {tgl_terakhir}")

                c1, c2 = st.columns(2)

                if sisa_r2 < 0:
                    c1.error(f"Sisa Karcis R2: **{sisa_r2}** MINUS")
                elif sisa_r2 == 0:
                    c1.warning(f"Sisa Karcis R2: **{sisa_r2}** HABIS")
                else:
                    c1.metric("Sisa Karcis R2", sisa_r2)

                if sisa_r4 < 0:
                    c2.error(f"Sisa Karcis R4: **{sisa_r4}** MINUS")
                elif sisa_r4 == 0:
                    c2.warning(f"Sisa Karcis R4: **{sisa_r4}** HABIS")
                else:
                    c2.metric("Sisa Karcis R4", sisa_r4)

            else:
                st.markdown(f"### {petugas}")
                st.caption("Belum ada data stok")
                c1, c2 = st.columns(2)
                c1.metric("Sisa Karcis R2", 0)
                c2.metric("Sisa Karcis R4", 0)

            st.divider()
            ada_data = True

        if not ada_data:
            st.info("Belum ada data petugas.")

    if pakai_expander:
        with st.expander("SISA STOK KARCIS PER PETUGAS", expanded=False):
            _isi()
    else:
        _isi()


def render_log_konfirmasi(df_p, pakai_expander=True):
    def _isi():
        if "Status_Khusus" not in df_p.columns:
            st.info("Belum ada data.")
            return

        hari_ini = datetime.now().date()

        df_isi = df_p.copy()
        df_isi["Tgl_Sort"] = pd.to_datetime(
            df_isi["Tanggal"], dayfirst=True, errors="coerce"
        ).dt.date

        df_isi = df_isi[
            (df_isi["Tgl_Sort"].notna()) &
            (df_isi["Tgl_Sort"] <= hari_ini)
        ]

        df_isi = df_isi[
            (df_isi["Status_Khusus"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""])) |
            (df_isi["Status_MPP"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""])) |
            (df_isi["Status_Cetak"].astype(str).str.strip().apply(lambda x: x not in ["-", "nan", ""]))
        ].copy()

        if not df_isi.empty:
            last = df_isi.sort_values(by="Tgl_Sort", ascending=False).head(1)
            kolom = ["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"]
            kolom_ada = [k for k in kolom if k in last.columns]
            st.subheader("Konfirmasi Terakhir")
            st.dataframe(last[kolom_ada], hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada data yang diinput.")

        st.divider()
        st.subheader("Tanggal Belum Selesai Konfirmasi (Awal Bulan s/d Hari Ini)")
        df_blm = daftar_tanggal_belum_konfirmasi_bulan_ini(df_p)
        if not df_blm.empty:
            st.dataframe(df_blm, hide_index=True, use_container_width=True)
        else:
            st.success("Semua konfirmasi bulan ini sudah selesai.")

    if pakai_expander:
        with st.expander("LOG KONFIRMASI BULAN INI", expanded=False):
            _isi()
    else:
        _isi()


# ==========================================
# LOAD DATA
# ==========================================
df_p = load_data(conn_parkir, WS_PARKIR)

st.title("MODUL PARKIR")

if df_p.empty:
    st.warning("Data PARKIR kosong atau worksheet tidak ditemukan.")
    st.stop()

hari_ini = today_wita()

tab1, tab2, tab3 = st.tabs(["INPUT & EDIT REKAP", "SISA STOK", "KONFIRMASI"])

# ==========================================
# TAB 1 - INPUT & EDIT REKAP
# ==========================================
with tab1:
    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.subheader("INPUT & EDIT REKAP HARIAN")
    with c_btn:
        tombol_refresh("ref_parkir_rekap")

    tgl_belum, df_belum = cari_tanggal_belum_input_parkir(df_p)
    if tgl_belum:
        st.warning(f"Input parkir belum terisi mulai: **{tgl_belum.strftime('%d-%m-%Y')}**")
    else:
        st.success("Semua data parkir sampai hari ini sudah terinput.")

    tgl_input_user = st.text_input(
        "MASUKKAN TANGGAL",
        value=datetime.now().strftime("%d-%m-%Y"),
        key="tgl_input_parkir_rekap"
    )

    dt_user, baris, idx, nama_p, sisa_r2, sisa_r4 = ambil_info_tanggal_parkir(df_p, tgl_input_user)

    if baris.empty or idx is None:
        st.warning("Tanggal belum ada di jadwal Sheet.")
    else:
        status_libur_skrg = ""
        if "Status_Libur" in df_p.columns:
            status_libur_skrg = str(df_p.loc[idx, "Status_Libur"]).strip().upper()

        is_libur = status_libur_skrg == "LIBUR"

        st.success(f"PETUGAS: **{nama_p}** | **{format_tgl_hari_indo(tgl_input_user)}**")

        lib1, lib2 = st.columns(2)
        with lib1:
            if is_libur:
                st.warning("Tanggal ini ditandai **LIBUR**")
                if st.button("BATAL LIBUR", key="btn_batal_libur", use_container_width=True):
                    df_u = df_p.copy()
                    df_u.loc[idx, "Status_Libur"] = "-"
                    if safe_update(conn_parkir, WS_PARKIR, df_u):
                        st.success("Status libur dibatalkan!")
                        st.rerun()
            else:
                if st.button("TANDAI LIBUR", key="btn_tandai_libur", use_container_width=True):
                    df_u = df_p.copy()
                    df_u.loc[idx, "Status_Libur"] = "LIBUR"
                    if safe_update(conn_parkir, WS_PARKIR, df_u):
                        st.success("Tanggal ditandai LIBUR!")
                        st.rerun()

        if is_libur:
            st.info("Tanggal ini LIBUR. Tidak perlu input rekap. Sisa stok tetap terbawa ke hari berikutnya.")
        else:
            karcis_skrg = str(df_p.loc[idx, "Total_Karcis_R2"]).strip()
            sudah_diisi = karcis_skrg not in ["-", "nan", ""]

            if sudah_diisi:
                val_tr2 = pd.to_numeric(df_p.loc[idx, "Total_Karcis_R2"], errors="coerce")
                val_tr4 = pd.to_numeric(df_p.loc[idx, "Total_Karcis_R4"], errors="coerce")
                val_mr2 = pd.to_numeric(df_p.loc[idx, "MPP_Roda_R2"], errors="coerce")
                val_mr4 = pd.to_numeric(df_p.loc[idx, "MPP_Roda_R4"], errors="coerce")
                val_pk2 = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R2"], errors="coerce")
                val_pk4 = pd.to_numeric(df_p.loc[idx, "Pengambilan_Karcis_R4"], errors="coerce")

                val_tr2 = 0 if pd.isna(val_tr2) else int(val_tr2)
                val_tr4 = 0 if pd.isna(val_tr4) else int(val_tr4)
                val_mr2 = 0 if pd.isna(val_mr2) else int(val_mr2)
                val_mr4 = 0 if pd.isna(val_mr4) else int(val_mr4)
                val_pk2 = 0 if pd.isna(val_pk2) else int(val_pk2)
                val_pk4 = 0 if pd.isna(val_pk4) else int(val_pk4)
            else:
                val_tr2 = 0
                val_tr4 = 0
                val_mr2 = 0
                val_mr4 = 0
                val_pk2 = 0
                val_pk4 = 0

            st.divider()

            judul_form = "EDIT REKAP" if sudah_diisi else "INPUT REKAP"
            st.subheader(judul_form)

            mr2 = to_int_input(st.text_input("MPP RODA R2", value=str(val_mr2), key="txt_mr2"))
            mr4 = to_int_input(st.text_input("MPP RODA R4", value=str(val_mr4), key="txt_mr4"))

            tr2 = to_int_input(st.text_input("TOTAL KARCIS R2", value=str(val_tr2), key="txt_tr2"))
            tr4 = to_int_input(st.text_input("TOTAL KARCIS R4", value=str(val_tr4), key="txt_tr4"))

            pk2_input = to_int_input(st.text_input("PENGAMBILAN KARCIS R2", value=str(val_pk2), key="txt_pk2"))
            pk4_input = to_int_input(st.text_input("PENGAMBILAN KARCIS R4", value=str(val_pk4), key="txt_pk4"))

            st.divider()

            btn_hitung = st.button(
                "HITUNG",
                use_container_width=True,
                key="btn_hitung_parkir"
            )

            if btn_hitung:
                st.session_state["hasil_hitung"] = {
                    "tr2": tr2,
                    "tr4": tr4,
                    "mr2": mr2,
                    "mr4": mr4,
                    "kh2": tr2 - mr2,
                    "kh4": tr4 - mr4,
                    "pk2": pk2_input,
                    "pk4": pk4_input,
                    "sn2": (pk2_input + sisa_r2) - tr2,
                    "sn4": (pk4_input + sisa_r4) - tr4
                }

            if "hasil_hitung" in st.session_state:
                h = st.session_state["hasil_hitung"]

                st.subheader("Hasil Perhitungan")
                st.metric("Khusus R2", h["kh2"])
                st.metric("Khusus R4", h["kh4"])

                if h["sn2"] < 0:
                    st.error(f"Sisa Stok R2: **{h['sn2']}** MINUS")
                else:
                    st.metric("Sisa Stok R2", h["sn2"])

                if h["sn4"] < 0:
                    st.error(f"Sisa Stok R4: **{h['sn4']}** MINUS")
                else:
                    st.metric("Sisa Stok R4", h["sn4"])

                st.divider()

                label_simpan = "SIMPAN EDIT" if sudah_diisi else "SIMPAN REKAP"
                btn_simpan = st.button(
                    label_simpan,
                    type="primary",
                    use_container_width=True,
                    key="btn_simpan_parkir"
                )

                btn_batal = st.button(
                    "BATAL",
                    use_container_width=True,
                    key="btn_batal_hitung"
                )

                if btn_simpan:
                    df_u = df_p.copy()
                    df_u.loc[idx, ["Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [
                        str(h["tr2"]), str(h["mr2"]), str(h["sn2"]), str(h["kh2"])
                    ]
                    df_u.loc[idx, ["Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [
                        str(h["tr4"]), str(h["mr4"]), str(h["sn4"]), str(h["kh4"])
                    ]
                    df_u.loc[idx, ["Pengambilan_Karcis_R2", "Pengambilan_Karcis_R4"]] = [
                        str(h["pk2"]), str(h["pk4"])
                    ]
                    df_u.loc[idx, ["Status_Khusus", "Status_MPP", "Status_Cetak"]] = [
                        "BELUM", "BELUM", "BELUM"
                    ]

                    if safe_update(conn_parkir, WS_PARKIR, df_u):
                        del st.session_state["hasil_hitung"]
                        if sudah_diisi:
                            st.success("Data berhasil diedit!")
                        else:
                            st.success("Rekap berhasil disimpan!")
                        st.rerun()

                if btn_batal:
                    del st.session_state["hasil_hitung"]
                    st.rerun()

    render_log_rekap(df_p, dt_user)

# ==========================================
# TAB 2 - SISA STOK
# ==========================================
with tab2:
    c_head2, c_btn2 = st.columns([0.88, 0.12])
    c_head2.subheader("SISA STOK KARCIS PER PETUGAS")
    with c_btn2:
        tombol_refresh("ref_parkir_stok")

    render_log_stok(df_p, pakai_expander=False)

# ==========================================
# TAB 3 - KONFIRMASI
# ==========================================
with tab3:
    c_head3, c_btn3 = st.columns([0.88, 0.12])
    c_head3.subheader("KONFIRMASI SETORAN")
    with c_btn3:
        tombol_refresh("ref_parkir_konfirmasi")

    if "Total_Karcis_R2" not in df_p.columns or "Total_Karcis_R4" not in df_p.columns:
        st.error("Kolom tidak ditemukan.")
    else:
        angka_r2 = df_p["Total_Karcis_R2"].astype(str).str.strip().str.isnumeric()
        angka_r4 = df_p["Total_Karcis_R4"].astype(str).str.strip().str.isnumeric()
        df_pen = df_p[angka_r2 | angka_r4].copy()

        if df_pen.empty:
            st.info("TIDAK ADA DATA KONFIRMASI.")
        else:
            df_pen["Tgl_Temp"] = pd.to_datetime(
                df_pen["Tanggal"], dayfirst=True, errors="coerce"
            ).dt.date
            df_fil = df_pen[
                (df_pen["Status_Khusus"] != "SUDAH") |
                (df_pen["Status_MPP"] != "SUDAH") |
                (df_pen["Status_Cetak"] != "SUDAH") |
                (df_pen["Tgl_Temp"] == hari_ini)
            ].copy()

            if df_fil.empty:
                st.info("Semua data sudah Lunas.")
            else:
                df_fil = df_fil.sort_index(ascending=False).head(10)

                for i, row in df_fil.iterrows():
                    sk = str(row.get("Status_Khusus", "BELUM")).strip()
                    sm = str(row.get("Status_MPP", "BELUM")).strip()
                    sc = str(row.get("Status_Cetak", "BELUM")).strip()
                    lunas = (sk == "SUDAH") and (sm == "SUDAH") and (sc == "SUDAH")
                    ikon = "[SELESAI]" if lunas else "[BELUM]"

                    with st.expander(
                        f"{ikon} {row['Tanggal']} - {row['Nama_Petugas']}",
                        expanded=not lunas
                    ):
                        if lunas:
                            st.success("SELESAI")

                        ck, cm_col = st.columns(2)

                        with ck:
                            st.write(
                                f"**TOTAL**\n"
                                f"R2: {row.get('Total_Karcis_R2', '-')} | "
                                f"R4: {row.get('Total_Karcis_R4', '-')}"
                            )
                            if sk != "SUDAH":
                                if st.button(
                                    "TERIMA TOTAL",
                                    key=f"k_{i}",
                                    use_container_width=True
                                ):
                                    df_u = df_p.copy()
                                    df_u.loc[i, "Status_Khusus"] = "SUDAH"
                                    if safe_update(conn_parkir, WS_PARKIR, df_u):
                                        st.rerun()
                            else:
                                st.success("Diterima")

                        with cm_col:
                            st.write(
                                f"**MPP**\n"
                                f"R2: {row.get('MPP_Roda_R2', '-')} | "
                                f"R4: {row.get('MPP_Roda_R4', '-')}"
                            )
                            if sm != "SUDAH":
                                if st.button(
                                    "TERIMA MPP",
                                    key=f"m_{i}",
                                    type="primary",
                                    use_container_width=True
                                ):
                                    df_u = df_p.copy()
                                    df_u.loc[i, "Status_MPP"] = "SUDAH"
                                    if safe_update(conn_parkir, WS_PARKIR, df_u):
                                        st.rerun()
                            else:
                                st.download_button(
                                    "CETAK PDF MPP",
                                    data=cetak_tanda_terima_parkir(row.to_dict()),
                                    file_name=f"MPP_{row['Tanggal']}.pdf",
                                    key=f"p_{i}",
                                    use_container_width=True
                                )
                                if sc != "SUDAH":
                                    if st.button(
                                        "SUDAH CETAK",
                                        key=f"c_{i}",
                                        use_container_width=True
                                    ):
                                        df_u = df_p.copy()
                                        df_u.loc[i, "Status_Cetak"] = "SUDAH"
                                        if safe_update(conn_parkir, WS_PARKIR, df_u):
                                            st.rerun()
                                else:
                                    st.success("Dicetak")

    render_log_konfirmasi(df_p, pakai_expander=False)
