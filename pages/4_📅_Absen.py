import streamlit as st
import pandas as pd
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css
from utils.helpers import (
    load_data, safe_update, pastikan_kolom, tombol_refresh, today_wita,
    WS_MASTER_ABSEN, WS_DATA_ABSEN, WS_KALENDER_ABSEN,
    KOLOM_MASTER_ABSEN, KOLOM_DATA_ABSEN, KOLOM_KALENDER_ABSEN,
    get_master_absen, get_daftar_jabatan,
    hitung_rekap_absen_bulanan,
    generate_kalender_bulan, get_hari_kerja_bulan
)

st.set_page_config(page_title="Absen | UPTD", page_icon="📅", layout="wide", initial_sidebar_state="collapsed")
inject_css()
conn_absen = st.connection("gsheets_absen", type=GSheetsConnection)

with st.sidebar:
    logo_b64 = st.session_state.get("logo_b64")
    if logo_b64:
        st.markdown(f'<div style="text-align:center;padding:18px 0 6px 0;"><img src="data:image/png;base64,{logo_b64}" width="78" height="auto" style="display:inline-block;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4));"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;padding:18px 0 6px 0;"><div style="font-size:3rem;">🏛️</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;padding:4px 0 14px 0;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:14px;"><p style="font-family:\'Inter\',sans-serif;font-size:1.05rem;font-weight:800;color:#f1f5f9 !important;margin:0 0 4px 0;">UPTD PASAR KANDANGAN</p><p style="font-family:\'Inter\',sans-serif;font-size:0.78rem;font-weight:600;color:#94a3b8 !important;margin:0;">KABUPATEN HULU SUNGAI SELATAN</p></div>', unsafe_allow_html=True)
    st.page_link("app_web.py", label="🏠  Beranda", use_container_width=True)
    st.page_link("pages/1_📋_SK_Toko.py", label="📋  SK TOKO", use_container_width=True)
    st.page_link("pages/2_🅿️_Parkir.py", label="🅿️  PARKIR", use_container_width=True)
    st.page_link("pages/3_💰_Kas.py", label="💰  KAS UPTD", use_container_width=True)
    st.page_link("pages/4_📅_Absen.py", label="📅  ABSEN", use_container_width=True)
    st.markdown('<div style="text-align:center;padding:24px 0 8px 0;border-top:1px solid rgba(255,255,255,0.06);margin-top:40px;"><p style="font-family:\'Inter\',sans-serif;font-size:0.56rem;color:#64748b !important;margin:0;">Developed by</p><p style="font-family:\'Inter\',sans-serif;font-size:0.68rem;font-weight:700;color:#94a3b8 !important;margin:2px 0 0 0;">M. Luthfi Renaldi</p></div>', unsafe_allow_html=True)

df_master = load_data(conn_absen, WS_MASTER_ABSEN)
df_master = pastikan_kolom(df_master, KOLOM_MASTER_ABSEN)
df_absen_data = load_data(conn_absen, WS_DATA_ABSEN)
df_absen_data = pastikan_kolom(df_absen_data, KOLOM_DATA_ABSEN)
df_kalender = load_data(conn_absen, WS_KALENDER_ABSEN)
df_kalender = pastikan_kolom(df_kalender, KOLOM_KALENDER_ABSEN)

tab1, tab2, tab3, tab4 = st.tabs(["📝 INPUT ABSEN", "📊 REKAP", "📆 KALENDER", "👥 MASTER"])

# ==========================================
# TAB 1 — INPUT ABSEN
# ==========================================
with tab1:
    ch, cb = st.columns([0.88, 0.12])
    ch.header("📝 Input Absen Harian")
    with cb:
        tombol_refresh("ref_absen_input")

    tgl_absen = st.text_input("📅 Tanggal", value=today_wita().strftime("%d/%m/%Y"), key="absen_tgl")
    daftar_jabatan = get_daftar_jabatan(df_master)
    jabatan_pilih = st.selectbox("🏢 Pilih Jabatan", ["Semua"] + daftar_jabatan, key="absen_jabatan")
    df_filtered = get_master_absen(df_master, jabatan_pilih)

    if df_filtered.empty:
        st.warning("⚠️ Belum ada data pegawai.")
    else:
        no_list = df_filtered["No_Absen"].tolist()
        nama_list = df_filtered["Nama"].tolist()
        pilihan = [f"{no} - {nama}" for no, nama in zip(no_list, nama_list)]
        selected = st.multiselect("🔢 Pilih No Absen", options=pilihan, default=pilihan, key="absen_pilih")

        if selected:
            sel_no = [s.split(" - ")[0].strip() for s in selected]
            df_t = df_filtered[df_filtered["No_Absen"].isin(sel_no)].copy()

            st.divider()
            st.subheader("📋 Daftar Absen")
            st.caption("Default: HADIR. Ubah jika tidak hadir.")

            ket_dict = {}
            for idx, row in df_t.iterrows():
                no = str(row["No_Absen"])
                c1, c2, c3, c4 = st.columns([1, 3, 2, 1])
                c1.write(f"**{no}**")
                c2.write(str(row["Nama"]))
                c3.write(f"_{row['Jabatan']}_")
                with c4:
                    ket = st.selectbox("K", ["HADIR","SAKIT","IZIN","ALPHA","CUTI"], index=0, key=f"ket_{no}_{idx}", label_visibility="collapsed")
                ket_dict[no] = ket

            st.divider()
            if st.button("💾 SIMPAN ABSEN", type="primary", use_container_width=True, key="btn_simpan_absen"):
                rows = []
                for _, row in df_t.iterrows():
                    no = str(row["No_Absen"])
                    kv = ket_dict.get(no, "HADIR")
                    if kv != "HADIR":
                        rows.append({
                            "Tanggal": tgl_absen, "No_Absen": no,
                            "Nama": str(row["Nama"]), "NIP": str(row["NIP"]),
                            "Gol_Pangkat": str(row["Gol_Pangkat"]),
                            "Jabatan": str(row["Jabatan"]), "Keterangan": kv
                        })
                if rows:
                    df_b = pd.concat([df_absen_data, pd.DataFrame(rows)], ignore_index=True)
                    if safe_update(conn_absen, WS_DATA_ABSEN, df_b):
                        st.success(f"✅ Disimpan! ({len(rows)} tidak hadir)")
                        st.rerun()
                else:
                    st.success(f"✅ Semua HADIR pada {tgl_absen}.")

# ==========================================
# TAB 2 — REKAP
# ==========================================
with tab2:
    ch2, cb2 = st.columns([0.88, 0.12])
    ch2.header("📊 Rekap Absen Bulanan")
    with cb2:
        tombol_refresh("ref_absen_rekap")

    bln_ini = today_wita()
    bln_opts = []
    for i in range(12):
        m = bln_ini.month - i
        y = bln_ini.year
        if m <= 0:
            m += 12
            y -= 1
        bln_opts.append(f"{m:02d}/{y}")

    bln_pilih = st.selectbox("📅 Pilih Bulan", bln_opts, key="rekap_bulan")

    hari_kerja = get_hari_kerja_bulan(df_kalender, bln_pilih)
    st.info(f"📆 Hari kerja aktif bulan ini: **{hari_kerja} hari** (dari kalender)")

    rekap = hitung_rekap_absen_bulanan(df_absen_data, bln_pilih, df_master, df_kalender)

    if rekap.empty:
        st.info("Belum ada data.")
    else:
        jab_rek = st.selectbox("🏢 Filter Jabatan", ["Semua"] + sorted(rekap["Jabatan"].unique().tolist()), key="rekap_jab")
        if jab_rek != "Semua":
            rekap = rekap[rekap["Jabatan"] == jab_rek]

        kol = ["No_Absen","Nama","Jabatan","Hadir","Sakit","Izin","Alpha","Cuti","Hari_Kerja","Persen"]
        ka = [k for k in kol if k in rekap.columns]
        st.dataframe(rekap[ka], use_container_width=True, hide_index=True)

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("📊 Rata-rata", f"{rekap['Persen'].mean():.1f}%")
        m2.metric("✅ Total Hadir", int(rekap["Hadir"].sum()))
        m3.metric("❌ Total Alpha", int(rekap["Alpha"].sum()))

        rendah = rekap[rekap["Persen"] < 80]
        if not rendah.empty:
            st.warning(f"⚠️ {len(rendah)} pegawai di bawah 80%:")
            for _, r in rendah.iterrows():
                st.write(f"- **{r['Nama']}** ({r['Jabatan']}) — {r['Persen']}%")

        st.divider()
        kol_xl = ["No_Absen","Nama","NIP","Gol_Pangkat","Jabatan","Hadir","Sakit","Izin","Alpha","Cuti","Hari_Kerja","Persen"]
        ka_xl = [k for k in kol_xl if k in rekap.columns]
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            rekap[ka_xl].to_excel(w, index=False, sheet_name="Rekap")
        buf.seek(0)
        st.download_button("📥 Download Excel", data=buf, file_name=f"Rekap_Absen_{bln_pilih.replace('/','-')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# ==========================================
# TAB 3 — KALENDER
# ==========================================
with tab3:
    ch3, cb3 = st.columns([0.88, 0.12])
    ch3.header("📆 Kalender Absen")
    with cb3:
        tombol_refresh("ref_kalender")

    st.subheader("🔄 Generate Kalender Bulan")

    gc1, gc2 = st.columns(2)
    with gc1:
        gen_bulan = st.number_input("Bulan", min_value=1, max_value=12, value=today_wita().month, key="gen_bln")
    with gc2:
        gen_tahun = st.number_input("Tahun", min_value=2020, max_value=2030, value=today_wita().year, key="gen_thn")

    if st.button("📆 Generate Kalender", type="primary", use_container_width=True, key="btn_gen_kal"):
        df_gen = generate_kalender_bulan(int(gen_tahun), int(gen_bulan))

        # Hapus kalender bulan yang sama kalau sudah ada
        bulan_target = f"{int(gen_bulan):02d}/{int(gen_tahun)}"
        df_kal_lama = df_kalender[df_kalender["Tanggal"] != "-"].copy()
        df_kal_lama["_tgl"] = df_kal_lama["Tanggal"].astype(str).str.strip().str.replace("-", "/", regex=False)
        df_kal_lama["_bulan"] = df_kal_lama["_tgl"].apply(
            lambda x: "/".join(x.split("/")[1:]) if len(x.split("/")) == 3 else ""
        )
        df_kal_sisa = df_kal_lama[df_kal_lama["_bulan"] != bulan_target][["Tanggal", "Status"]].copy()

        df_kal_baru = pd.concat([df_kal_sisa, df_gen], ignore_index=True)

        if safe_update(conn_absen, WS_KALENDER_ABSEN, df_kal_baru):
            st.success(f"✅ Kalender {int(gen_bulan):02d}/{int(gen_tahun)} berhasil di-generate!")
            st.rerun()

    st.divider()
    st.subheader("📋 Kelola Kalender")

    bln_kal_opts = []
    for i in range(12):
        m = today_wita().month - i
        y = today_wita().year
        if m <= 0:
            m += 12
            y -= 1
        bln_kal_opts.append(f"{m:02d}/{y}")

    bln_kal = st.selectbox("📅 Pilih Bulan", bln_kal_opts, key="kal_bulan")

    df_kal_view = df_kalender[df_kalender["Tanggal"] != "-"].copy()
    if not df_kal_view.empty:
        df_kal_view["_tgl"] = df_kal_view["Tanggal"].astype(str).str.strip().str.replace("-", "/", regex=False)
        df_kal_view["_bulan"] = df_kal_view["_tgl"].apply(
            lambda x: "/".join(x.split("/")[1:]) if len(x.split("/")) == 3 else ""
        )
        df_kal_bulan = df_kal_view[df_kal_view["_bulan"] == bln_kal].copy()
    else:
        df_kal_bulan = pd.DataFrame()

    if df_kal_bulan.empty:
        st.info("Belum ada kalender untuk bulan ini. Generate dulu.")
    else:
        hari_aktif = len(df_kal_bulan[df_kal_bulan["Status"].astype(str).str.strip().str.upper() == "AKTIF"])
        hari_libur = len(df_kal_bulan[df_kal_bulan["Status"].astype(str).str.strip().str.upper() == "LIBUR"])

        mk1, mk2, mk3 = st.columns(3)
        mk1.metric("📆 Total Hari", len(df_kal_bulan))
        mk2.metric("✅ Aktif", hari_aktif)
        mk3.metric("🔴 Libur", hari_libur)

        st.divider()

        for idx, row in df_kal_bulan.iterrows():
            tgl_val = str(row["Tanggal"])
            status_val = str(row["Status"]).strip().upper()

            real_idx = df_kalender[df_kalender["Tanggal"] == tgl_val].index

            kc1, kc2, kc3 = st.columns([3, 2, 1])
            kc1.write(f"📅 **{tgl_val}**")
            kc2.write(f"{'✅ AKTIF' if status_val == 'AKTIF' else '🔴 LIBUR'}")
            with kc3:
                if status_val == "AKTIF":
                    if st.button("🔴", key=f"libur_{idx}", use_container_width=True):
                        if len(real_idx) > 0:
                            df_kalender.loc[real_idx[0], "Status"] = "LIBUR"
                            safe_update(conn_absen, WS_KALENDER_ABSEN, df_kalender)
                            st.rerun()
                else:
                    if st.button("✅", key=f"aktif_{idx}", use_container_width=True):
                        if len(real_idx) > 0:
                            df_kalender.loc[real_idx[0], "Status"] = "AKTIF"
                            safe_update(conn_absen, WS_KALENDER_ABSEN, df_kalender)
                            st.rerun()

# ==========================================
# TAB 4 — MASTER PEGAWAI
# ==========================================
with tab4:
    ch4, cb4 = st.columns([0.88, 0.12])
    ch4.header("👥 Master Pegawai")
    with cb4:
        tombol_refresh("ref_master")

    df_mv = df_master[df_master["No_Absen"] != "-"].copy()
    if not df_mv.empty:
        df_mv["_s"] = pd.to_numeric(df_mv["No_Absen"], errors="coerce")
        df_mv = df_mv.sort_values("_s", ascending=True).drop(columns="_s")
        st.dataframe(df_mv[KOLOM_MASTER_ABSEN], use_container_width=True, hide_index=True)
        st.metric("👥 Total", len(df_mv))
    else:
        st.info("Belum ada data.")

    st.divider()
    st.subheader("➕ Tambah Pegawai")
    with st.form("form_tambah", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            no_b = st.text_input("No Absen *")
            nm_b = st.text_input("Nama *").strip().upper()
            nip_b = st.text_input("NIP").strip()
        with f2:
            gol_b = st.text_input("Gol/Pangkat").strip().upper()
            jab_b = st.text_input("Jabatan *").strip().upper()

        b1, b2 = st.columns(2)
        with b1:
            sv = st.form_submit_button("💾 Simpan", type="primary", use_container_width=True)
        with b2:
            st.form_submit_button("🔄 Reset", use_container_width=True)

        if sv:
            if not no_b.strip() or not nm_b or not jab_b:
                st.error("❌ No Absen, Nama, Jabatan wajib!")
            else:
                r = {"No_Absen": no_b.strip(), "Nama": nm_b, "NIP": nip_b if nip_b else "-",
                     "Gol_Pangkat": gol_b if gol_b else "-", "Jabatan": jab_b}
                df_mb = pd.concat([df_master, pd.DataFrame([r])], ignore_index=True)
                if safe_update(conn_absen, WS_MASTER_ABSEN, df_mb):
                    st.success(f"✅ '{nm_b}' ditambahkan!")
                    st.rerun()

    if not df_mv.empty:
        st.divider()
        st.subheader("🗑️ Hapus Pegawai")
        hl = [f"{r['No_Absen']} - {r['Nama']}" for _, r in df_mv.iterrows()]
        hp = st.selectbox("Pilih", hl, key="hapus_pg")
        if st.button("🗑️ Hapus", key="btn_hapus", use_container_width=True):
            nh = hp.split(" - ")[0].strip()
            df_mb = df_master[df_master["No_Absen"] != nh].copy()
            if safe_update(conn_absen, WS_MASTER_ABSEN, df_mb):
                st.success(f"✅ '{hp}' dihapus!")
                st.rerun()
