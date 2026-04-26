import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css
from utils.helpers import (
    load_data,
    safe_update,
    pastikan_kolom,
    tombol_refresh,
    today_wita,
    WS_MASTER_ABSEN,
    WS_DATA_ABSEN,
    KOLOM_MASTER_ABSEN,
    KOLOM_DATA_ABSEN,
    get_master_absen,
    get_daftar_jabatan,
    hitung_rekap_absen_bulanan
)

st.set_page_config(
    page_title="Absen | UPTD Pasar Kandangan",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_css()

conn_absen = st.connection("gsheets_absen", type=GSheetsConnection)

# ── SIDEBAR ──
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
                border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:14px;">
        <p style="font-family:'Inter',sans-serif; font-size:1.05rem; font-weight:800;
                  color:#f1f5f9 !important; margin:0 0 4px 0;">
            UPTD PASAR KANDANGAN</p>
        <p style="font-family:'Inter',sans-serif; font-size:0.78rem; font-weight:600;
                  color:#94a3b8 !important; margin:0;">
            KABUPATEN HULU SUNGAI SELATAN</p>
    </div>""", unsafe_allow_html=True)

    st.page_link("app_web.py", label="🏠  Beranda", use_container_width=True)
    st.page_link("pages/1_📋_SK_Toko.py", label="📋  SK TOKO", use_container_width=True)
    st.page_link("pages/2_🅿️_Parkir.py", label="🅿️  PARKIR", use_container_width=True)
    st.page_link("pages/3_💰_Kas.py", label="💰  KAS UPTD", use_container_width=True)
    st.page_link("pages/4_📅_Absen.py", label="📅  ABSEN", use_container_width=True)

    st.markdown("""
    <div style="text-align:center; padding:24px 0 8px 0;
                border-top:1px solid rgba(255,255,255,0.06); margin-top:40px;">
        <p style="font-family:'Inter',sans-serif; font-size:0.56rem;
                  color:#64748b !important; margin:0;">Developed by</p>
        <p style="font-family:'Inter',sans-serif; font-size:0.68rem; font-weight:700;
                  color:#94a3b8 !important; margin:2px 0 0 0;">M. Luthfi Renaldi</p>
    </div>""", unsafe_allow_html=True)

# ── LOAD DATA ──
df_master = load_data(conn_absen, WS_MASTER_ABSEN)
df_master = pastikan_kolom(df_master, KOLOM_MASTER_ABSEN)

df_absen_data = load_data(conn_absen, WS_DATA_ABSEN)
df_absen_data = pastikan_kolom(df_absen_data, KOLOM_DATA_ABSEN)

# ── TABS ──
tab1, tab2, tab3 = st.tabs(["📝 INPUT ABSEN", "📊 REKAP ABSEN", "👥 MASTER PEGAWAI"])

# ==========================================
# TAB 1 — INPUT ABSEN
# ==========================================
with tab1:
    c_h, c_b = st.columns([0.88, 0.12])
    c_h.header("📝 Input Absen Harian")
    with c_b:
        tombol_refresh("ref_absen_input")

    tgl_absen = st.text_input(
        "📅 Tanggal",
        value=today_wita().strftime("%d/%m/%Y"),
        key="absen_tgl"
    )

    daftar_jabatan = get_daftar_jabatan(df_master)

    jabatan_pilih = st.selectbox(
        "🏢 Pilih Jabatan",
        ["Semua"] + daftar_jabatan,
        key="absen_jabatan"
    )

    df_filtered = get_master_absen(df_master, jabatan_pilih)

    if df_filtered.empty:
        st.warning("⚠️ Belum ada data pegawai. Tambahkan di tab Master Pegawai.")
    else:
        no_list = df_filtered["No_Absen"].tolist()
        nama_list = df_filtered["Nama"].tolist()

        pilihan_display = [f"{no} - {nama}" for no, nama in zip(no_list, nama_list)]

        selected = st.multiselect(
            "🔢 Pilih No Absen",
            options=pilihan_display,
            default=pilihan_display,
            key="absen_pilih_no"
        )

        if selected:
            selected_no = [s.split(" - ")[0].strip() for s in selected]
            df_terpilih = df_filtered[df_filtered["No_Absen"].isin(selected_no)].copy()

            st.divider()
            st.subheader("📋 Daftar Absen")
            st.caption("Default: HADIR. Ubah jika tidak hadir.")

            keterangan_dict = {}

            for idx, row in df_terpilih.iterrows():
                no = str(row["No_Absen"])
                nama = str(row["Nama"])
                jabatan = str(row["Jabatan"])

                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                col1.write(f"**{no}**")
                col2.write(f"{nama}")
                col3.write(f"_{jabatan}_")
                with col4:
                    ket = st.selectbox(
                        "Ket",
                        ["HADIR", "SAKIT", "IZIN", "ALPHA", "CUTI"],
                        index=0,
                        key=f"ket_{no}_{idx}",
                        label_visibility="collapsed"
                    )
                keterangan_dict[no] = ket

            st.divider()

            # Hanya simpan yang BUKAN hadir
            if st.button(
                "💾 SIMPAN ABSEN",
                type="primary",
                use_container_width=True,
                key="btn_simpan_absen"
            ):
                rows_baru = []
                for _, row in df_terpilih.iterrows():
                    no = str(row["No_Absen"])
                    ket_val = keterangan_dict.get(no, "HADIR")

                    # Hanya simpan yang tidak hadir
                    if ket_val != "HADIR":
                        rows_baru.append({
                            "Tanggal": tgl_absen,
                            "No_Absen": no,
                            "Nama": str(row["Nama"]),
                            "NIP": str(row["NIP"]),
                            "Gol_Pangkat": str(row["Gol_Pangkat"]),
                            "Jabatan": str(row["Jabatan"]),
                            "Keterangan": ket_val
                        })

                if rows_baru:
                    df_baru = pd.concat(
                        [df_absen_data, pd.DataFrame(rows_baru)],
                        ignore_index=True
                    )
                    if safe_update(conn_absen, WS_DATA_ABSEN, df_baru):
                        st.success(
                            f"✅ Absen {tgl_absen} disimpan! "
                            f"({len(rows_baru)} pegawai tidak hadir tercatat)"
                        )
                        st.rerun()
                else:
                    st.success(f"✅ Semua pegawai HADIR pada {tgl_absen}. Tidak ada yang perlu disimpan.")

# ==========================================
# TAB 2 — REKAP ABSEN
# ==========================================
with tab2:
    c_h2, c_b2 = st.columns([0.88, 0.12])
    c_h2.header("📊 Rekap Absen Bulanan")
    with c_b2:
        tombol_refresh("ref_absen_rekap")

    bulan_ini = today_wita()
    bulan_options = []
    for i in range(12):
        m = bulan_ini.month - i
        y = bulan_ini.year
        if m <= 0:
            m += 12
            y -= 1
        bulan_options.append(f"{m:02d}/{y}")

    bulan_pilih = st.selectbox("📅 Pilih Bulan", bulan_options, key="rekap_bulan")

    rekap = hitung_rekap_absen_bulanan(df_absen_data, bulan_pilih, df_master)

    if rekap.empty:
        st.info("Belum ada data absen untuk bulan ini.")
    else:
        jabatan_rekap = st.selectbox(
            "🏢 Filter Jabatan",
            ["Semua"] + sorted(rekap["Jabatan"].unique().tolist()),
            key="rekap_jabatan"
        )

        if jabatan_rekap != "Semua":
            rekap = rekap[rekap["Jabatan"] == jabatan_rekap]

        kolom_tampil = [
            "No_Absen", "Nama", "Jabatan",
            "Hadir", "Sakit", "Izin", "Alpha", "Cuti",
            "Hari_Kerja", "Persen"
        ]
        kolom_ada = [k for k in kolom_tampil if k in rekap.columns]

        st.dataframe(rekap[kolom_ada], use_container_width=True, hide_index=True)

        st.divider()

        avg_persen = rekap["Persen"].mean()
        total_hadir = rekap["Hadir"].sum()
        total_alpha = rekap["Alpha"].sum()

        m1, m2, m3 = st.columns(3)
        m1.metric("📊 Rata-rata Kehadiran", f"{avg_persen:.1f}%")
        m2.metric("✅ Total Hadir", int(total_hadir))
        m3.metric("❌ Total Alpha", int(total_alpha))

        pegawai_rendah = rekap[rekap["Persen"] < 80]
        if not pegawai_rendah.empty:
            st.warning(f"⚠️ {len(pegawai_rendah)} pegawai kehadiran di bawah 80%:")
            for _, row in pegawai_rendah.iterrows():
                st.write(f"- **{row['Nama']}** ({row['Jabatan']}) — {row['Persen']}%")

# ==========================================
# TAB 3 — MASTER PEGAWAI
# ==========================================
with tab3:
    c_h3, c_b3 = st.columns([0.88, 0.12])
    c_h3.header("👥 Master Pegawai")
    with c_b3:
        tombol_refresh("ref_absen_master")

    df_master_valid = df_master[df_master["No_Absen"] != "-"].copy()

    if not df_master_valid.empty:
        df_master_valid["_sort"] = pd.to_numeric(df_master_valid["No_Absen"], errors="coerce")
        df_master_valid = df_master_valid.sort_values("_sort", ascending=True).drop(columns="_sort")

        st.dataframe(
            df_master_valid[KOLOM_MASTER_ABSEN],
            use_container_width=True,
            hide_index=True
        )
        st.metric("👥 Total Pegawai", len(df_master_valid))
    else:
        st.info("Belum ada data pegawai.")

    st.divider()
    st.subheader("➕ Tambah Pegawai")

    with st.form("form_tambah_pegawai", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            no_absen_baru = st.text_input("No Absen *")
            nama_baru = st.text_input("Nama *").strip().upper()
            nip_baru = st.text_input("NIP").strip()
        with f2:
            gol_baru = st.text_input("Gol/Pangkat").strip().upper()
            jabatan_baru = st.text_input("Jabatan *").strip().upper()

        b1, b2 = st.columns(2)
        with b1:
            simpan_pg = st.form_submit_button("💾 Simpan", type="primary", use_container_width=True)
        with b2:
            st.form_submit_button("🔄 Reset", use_container_width=True)

        if simpan_pg:
            if not no_absen_baru.strip() or not nama_baru or not jabatan_baru:
                st.error("❌ No Absen, Nama, dan Jabatan wajib diisi!")
            else:
                row_baru = {
                    "No_Absen": no_absen_baru.strip(),
                    "Nama": nama_baru,
                    "NIP": nip_baru if nip_baru else "-",
                    "Gol_Pangkat": gol_baru if gol_baru else "-",
                    "Jabatan": jabatan_baru
                }
                df_master_baru = pd.concat(
                    [df_master, pd.DataFrame([row_baru])],
                    ignore_index=True
                )
                if safe_update(conn_absen, WS_MASTER_ABSEN, df_master_baru):
                    st.success(f"✅ '{nama_baru}' berhasil ditambahkan!")
                    st.rerun()

    if not df_master_valid.empty:
        st.divider()
        st.subheader("🗑️ Hapus Pegawai")

        hapus_list = [f"{r['No_Absen']} - {r['Nama']}" for _, r in df_master_valid.iterrows()]
        hapus_pilih = st.selectbox("Pilih pegawai", hapus_list, key="hapus_pegawai")

        if st.button("🗑️ Hapus", key="btn_hapus_pegawai", use_container_width=True):
            no_hapus = hapus_pilih.split(" - ")[0].strip()
            df_master_baru = df_master[df_master["No_Absen"] != no_hapus].copy()

            if safe_update(conn_absen, WS_MASTER_ABSEN, df_master_baru):
                st.success(f"✅ '{hapus_pilih}' berhasil dihapus!")
                st.rerun()
