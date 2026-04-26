import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Absen | UPTD Pasar Kandangan",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_css()

# ==========================================
# KONEKSI
# ==========================================
conn_absen = st.connection("gsheets_absen", type=GSheetsConnection)

# ==========================================
# KONSTANTA
# ==========================================
WS_MASTER_ABSEN = "MASTER_ABSEN"
WS_DATA_ABSEN = "DATA_ABSEN"
WS_KALENDER_ABSEN = "KALENDER_ABSEN"

KOLOM_MASTER_ABSEN = [
    "No_Absen", "Nama", "NIP", "Gol_Pangkat", "Jabatan"
]

KOLOM_DATA_ABSEN = [
    "Tanggal", "No_Absen", "Nama", "NIP", "Gol_Pangkat", "Jabatan", "Keterangan"
]

KOLOM_KALENDER_ABSEN = [
    "Tanggal", "Status"
]

# ==========================================
# HELPER LOKAL
# ==========================================
def today_wita():
    # kalau tidak perlu timezone rumit, ini cukup stabil
    return datetime.now().date()

def tombol_refresh(key_btn):
    if st.button("🔄 Refresh", key=key_btn, use_container_width=True):
        st.rerun()

def get_empty_df(worksheet: str) -> pd.DataFrame:
    if worksheet == WS_MASTER_ABSEN:
        return pd.DataFrame(columns=KOLOM_MASTER_ABSEN)
    if worksheet == WS_DATA_ABSEN:
        return pd.DataFrame(columns=KOLOM_DATA_ABSEN)
    if worksheet == WS_KALENDER_ABSEN:
        return pd.DataFrame(columns=KOLOM_KALENDER_ABSEN)
    return pd.DataFrame()

def pastikan_kolom(df: pd.DataFrame, kolom_list: list) -> pd.DataFrame:
    for col in kolom_list:
        if col not in df.columns:
            df[col] = "-"
    return df

def load_data_local(conn_obj, worksheet: str) -> pd.DataFrame:
    try:
        df = conn_obj.read(worksheet=worksheet, ttl=120)
        if df is None or df.empty:
            return get_empty_df(worksheet)

        df = df.astype(str).replace(r"\.0$", "", regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip()

        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")

        if worksheet == WS_MASTER_ABSEN:
            df = pastikan_kolom(df, KOLOM_MASTER_ABSEN)
        elif worksheet == WS_DATA_ABSEN:
            df = pastikan_kolom(df, KOLOM_DATA_ABSEN)
        elif worksheet == WS_KALENDER_ABSEN:
            df = pastikan_kolom(df, KOLOM_KALENDER_ABSEN)

        return df
    except Exception as e:
        st.error(f"Gagal membaca data ({worksheet}): {e}")
        return get_empty_df(worksheet)

def safe_update_local(conn_obj, worksheet: str, data: pd.DataFrame) -> bool:
    try:
        conn_obj.update(worksheet=worksheet, data=data)
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan ({worksheet}): {e}")
        return False

def to_float(val):
    try:
        txt = str(val).strip().replace(",", "")
        if txt in ["", "-", "nan", "None", "null", "<NA>"]:
            return 0.0
        return float(txt)
    except:
        return 0.0

def get_master_absen(df_master, jabatan=None):
    try:
        if df_master.empty:
            return pd.DataFrame(columns=KOLOM_MASTER_ABSEN)

        d = df_master[df_master["No_Absen"] != "-"].copy()

        if jabatan and jabatan != "Semua":
            d = d[d["Jabatan"].astype(str).str.strip().str.upper() == jabatan.strip().upper()]

        d["_sort"] = pd.to_numeric(d["No_Absen"], errors="coerce")
        d = d.sort_values("_sort", ascending=True).drop(columns="_sort")
        return d
    except:
        return pd.DataFrame(columns=KOLOM_MASTER_ABSEN)

def get_daftar_jabatan(df_master):
    try:
        if df_master.empty:
            return []
        jabatan = (
            df_master[df_master["Jabatan"] != "-"]["Jabatan"]
            .astype(str).str.strip().str.upper()
            .unique().tolist()
        )
        return sorted(jabatan)
    except:
        return []

def generate_kalender_bulan(tahun, bulan):
    try:
        jumlah_hari = calendar.monthrange(tahun, bulan)[1]
        rows = []
        for day in range(1, jumlah_hari + 1):
            tgl = f"{day:02d}/{bulan:02d}/{tahun}"
            rows.append({
                "Tanggal": tgl,
                "Status": "AKTIF"
            })
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame(columns=KOLOM_KALENDER_ABSEN)

def get_hari_kerja_bulan(df_kalender, bulan_str):
    try:
        if df_kalender.empty:
            return 0

        d = df_kalender[df_kalender["Tanggal"] != "-"].copy()
        d["_tgl"] = d["Tanggal"].astype(str).str.strip().str.replace("-", "/", regex=False)
        d["_bulan"] = d["_tgl"].apply(
            lambda x: "/".join(x.split("/")[1:]) if len(x.split("/")) == 3 else ""
        )
        d = d[d["_bulan"] == bulan_str]
        d_aktif = d[d["Status"].astype(str).str.strip().str.upper() == "AKTIF"]

        return len(d_aktif)
    except:
        return 0

def hitung_rekap_absen_bulanan(df_absen, bulan_str, df_master=None, df_kalender=None):
    try:
        if df_master is None or df_master.empty:
            return pd.DataFrame()

        # Hitung hari kerja dari kalender
        if df_kalender is not None and not df_kalender.empty:
            total_hari_kerja = get_hari_kerja_bulan(df_kalender, bulan_str)
        else:
            try:
                bln, thn = bulan_str.split("/")
                total_hari_kerja = calendar.monthrange(int(thn), int(bln))[1]
            except:
                total_hari_kerja = 30

        if total_hari_kerja <= 0:
            return pd.DataFrame()

        # Data absen bulan ini
        d_absen = pd.DataFrame()
        if not df_absen.empty:
            d = df_absen[df_absen["Tanggal"] != "-"].copy()
            d["_tgl"] = d["Tanggal"].astype(str).str.strip().str.replace("-", "/", regex=False)
            d["_bulan"] = d["_tgl"].apply(
                lambda x: "/".join(x.split("/")[1:]) if len(x.split("/")) == 3 else ""
            )
            d_absen = d[d["_bulan"] == bulan_str].copy()
            if not d_absen.empty:
                d_absen["Ket_Upper"] = d_absen["Keterangan"].astype(str).str.strip().str.upper()

        semua_pegawai = df_master[df_master["No_Absen"] != "-"][
            ["No_Absen", "Nama", "NIP", "Gol_Pangkat", "Jabatan"]
        ].copy()

        if semua_pegawai.empty:
            return pd.DataFrame()

        hasil_list = []

        for _, pegawai in semua_pegawai.iterrows():
            no = str(pegawai["No_Absen"]).strip()

            sakit = 0
            izin = 0
            alpha = 0
            cuti = 0

            if not d_absen.empty:
                data_pg = d_absen[d_absen["No_Absen"].astype(str).str.strip() == no]
                if not data_pg.empty:
                    sakit = (data_pg["Ket_Upper"] == "SAKIT").sum()
                    izin = (data_pg["Ket_Upper"] == "IZIN").sum()
                    alpha = (data_pg["Ket_Upper"] == "ALPHA").sum()
                    cuti = (data_pg["Ket_Upper"] == "CUTI").sum()

            # Yang tidak ada catatan dianggap HADIR
            tidak_hadir = sakit + izin + alpha + cuti
            hadir = total_hari_kerja - tidak_hadir
            if hadir < 0:
                hadir = 0

            # Persentase: HADIR / (HADIR + ALPHA)
            if (hadir + alpha) > 0:
                persen = round(hadir / (hadir + alpha) * 100, 1)
            else:
                persen = 100.0

            hasil_list.append({
                "No_Absen": no,
                "Nama": str(pegawai["Nama"]),
                "NIP": str(pegawai["NIP"]),
                "Gol_Pangkat": str(pegawai["Gol_Pangkat"]),
                "Jabatan": str(pegawai["Jabatan"]),
                "Hadir": hadir,
                "Sakit": sakit,
                "Izin": izin,
                "Alpha": alpha,
                "Cuti": cuti,
                "Hari_Kerja": total_hari_kerja,
                "Persen": persen
            })

        rekap = pd.DataFrame(hasil_list)
        rekap["_sort"] = pd.to_numeric(rekap["No_Absen"], errors="coerce")
        rekap = rekap.sort_values("_sort", ascending=True).drop(columns="_sort")
        return rekap
    except:
        return pd.DataFrame()

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

# ==========================================
# LOAD DATA
# ==========================================
df_master = load_data_local(conn_absen, WS_MASTER_ABSEN)
df_master = pastikan_kolom(df_master, KOLOM_MASTER_ABSEN)

df_absen_data = load_data_local(conn_absen, WS_DATA_ABSEN)
df_absen_data = pastikan_kolom(df_absen_data, KOLOM_DATA_ABSEN)

df_kalender = load_data_local(conn_absen, WS_KALENDER_ABSEN)
df_kalender = pastikan_kolom(df_kalender, KOLOM_KALENDER_ABSEN)

# ==========================================
# TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📝 INPUT ABSEN", "📊 REKAP", "📆 KALENDER", "👥 MASTER"])

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
        st.warning("⚠️ Belum ada data pegawai.")
    else:
        no_list = df_filtered["No_Absen"].tolist()
        nama_list = df_filtered["Nama"].tolist()
        pilihan = [f"{no} - {nama}" for no, nama in zip(no_list, nama_list)]

        selected = st.multiselect(
            "🔢 Pilih No Absen",
            options=pilihan,
            default=pilihan,
            key="absen_pilih"
        )

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
                    ket = st.selectbox(
                        "K",
                        ["HADIR", "SAKIT", "IZIN", "ALPHA", "CUTI"],
                        index=0,
                        key=f"ket_{no}_{idx}",
                        label_visibility="collapsed"
                    )
                ket_dict[no] = ket

            st.divider()
            if st.button("💾 SIMPAN ABSEN", type="primary", use_container_width=True, key="btn_simpan_absen"):
                rows = []
                for _, row in df_t.iterrows():
                    no = str(row["No_Absen"])
                    kv = ket_dict.get(no, "HADIR")
                    if kv != "HADIR":
                        rows.append({
                            "Tanggal": tgl_absen,
                            "No_Absen": no,
                            "Nama": str(row["Nama"]),
                            "NIP": str(row["NIP"]),
                            "Gol_Pangkat": str(row["Gol_Pangkat"]),
                            "Jabatan": str(row["Jabatan"]),
                            "Keterangan": kv
                        })

                if rows:
                    df_b = pd.concat([df_absen_data, pd.DataFrame(rows)], ignore_index=True)
                    if safe_update_local(conn_absen, WS_DATA_ABSEN, df_b):
                        st.success(f"✅ Disimpan! ({len(rows)} pegawai tidak hadir)")
                        st.rerun()
                else:
                    st.success(f"✅ Semua HADIR pada {tgl_absen}.")

# ==========================================
# TAB 2 — REKAP
# ==========================================
with tab2:
    c_h2, c_b2 = st.columns([0.88, 0.12])
    c_h2.header("📊 Rekap Absen Bulanan")
    with c_b2:
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
    st.info(f"📆 Hari kerja aktif bulan ini: **{hari_kerja} hari**")

    rekap = hitung_rekap_absen_bulanan(df_absen_data, bln_pilih, df_master, df_kalender)

    if rekap.empty:
        st.info("Belum ada data.")
    else:
        jab_rek = st.selectbox(
            "🏢 Filter Jabatan",
            ["Semua"] + sorted(rekap["Jabatan"].unique().tolist()),
            key="rekap_jab"
        )
        if jab_rek != "Semua":
            rekap = rekap[rekap["Jabatan"] == jab_rek]

        kol = ["No_Absen", "Nama", "Jabatan", "Hadir", "Sakit", "Izin", "Alpha", "Cuti", "Hari_Kerja", "Persen"]
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
        kol_xl = ["No_Absen", "Nama", "NIP", "Gol_Pangkat", "Jabatan", "Hadir", "Sakit", "Izin", "Alpha", "Cuti", "Hari_Kerja", "Persen"]
        ka_xl = [k for k in kol_xl if k in rekap.columns]
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            rekap[ka_xl].to_excel(w, index=False, sheet_name="Rekap")
        buf.seek(0)
        st.download_button(
            "📥 Download Excel",
            data=buf,
            file_name=f"Rekap_Absen_{bln_pilih.replace('/','-')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ==========================================
# TAB 3 — KALENDER
# ==========================================
with tab3:
    c_h3, c_b3 = st.columns([0.88, 0.12])
    c_h3.header("📆 Kalender Absen")
    with c_b3:
        tombol_refresh("ref_kalender")

    st.subheader("🔄 Generate Kalender Bulan")
    gc1, gc2 = st.columns(2)
    with gc1:
        gen_bulan = st.number_input("Bulan", min_value=1, max_value=12, value=today_wita().month, key="gen_bln")
    with gc2:
        gen_tahun = st.number_input("Tahun", min_value=2020, max_value=2035, value=today_wita().year, key="gen_thn")

    if st.button("📆 Generate Kalender", type="primary", use_container_width=True, key="btn_gen_kal"):
        df_gen = generate_kalender_bulan(int(gen_tahun), int(gen_bulan))
        bulan_target = f"{int(gen_bulan):02d}/{int(gen_tahun)}"

        df_kal_lama = df_kalender[df_kalender["Tanggal"] != "-"].copy()
        if not df_kal_lama.empty:
            df_kal_lama["_tgl"] = df_kal_lama["Tanggal"].astype(str).str.strip().str.replace("-", "/", regex=False)
            df_kal_lama["_bulan"] = df_kal_lama["_tgl"].apply(
                lambda x: "/".join(x.split("/")[1:]) if len(x.split("/")) == 3 else ""
            )
            df_kal_sisa = df_kal_lama[df_kal_lama["_bulan"] != bulan_target][["Tanggal", "Status"]].copy()
        else:
            df_kal_sisa = pd.DataFrame(columns=KOLOM_KALENDER_ABSEN)

        df_kal_baru = pd.concat([df_kal_sisa, df_gen], ignore_index=True)

        if safe_update_local(conn_absen, WS_KALENDER_ABSEN, df_kal_baru):
            st.success(f"✅ Kalender {bulan_target} berhasil dibuat!")
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
                            safe_update_local(conn_absen, WS_KALENDER_ABSEN, df_kalender)
                            st.rerun()
                else:
                    if st.button("✅", key=f"aktif_{idx}", use_container_width=True):
                        if len(real_idx) > 0:
                            df_kalender.loc[real_idx[0], "Status"] = "AKTIF"
                            safe_update_local(conn_absen, WS_KALENDER_ABSEN, df_kalender)
                            st.rerun()

# ==========================================
# TAB 4 — MASTER
# ==========================================
with tab4:
    c_h4, c_b4 = st.columns([0.88, 0.12])
    c_h4.header("👥 Master Pegawai")
    with c_b4:
        tombol_refresh("ref_master")

    df_mv = df_master[df_master["No_Absen"] != "-"].copy()
    if not df_mv.empty:
        df_mv["_s"] = pd.to_numeric(df_mv["No_Absen"], errors="coerce")
        df_mv = df_mv.sort_values("_s", ascending=True).drop(columns="_s")
        st.dataframe(df_mv[KOLOM_MASTER_ABSEN], use_container_width=True, hide_index=True)
        st.metric("👥 Total Pegawai", len(df_mv))
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
                row = {
                    "No_Absen": no_b.strip(),
                    "Nama": nm_b,
                    "NIP": nip_b if nip_b else "-",
                    "Gol_Pangkat": gol_b if gol_b else "-",
                    "Jabatan": jab_b
                }
                df_mb = pd.concat([df_master, pd.DataFrame([row])], ignore_index=True)
                if safe_update_local(conn_absen, WS_MASTER_ABSEN, df_mb):
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
            if safe_update_local(conn_absen, WS_MASTER_ABSEN, df_mb):
                st.success(f"✅ '{hp}' dihapus!")
                st.rerun()
