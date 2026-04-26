import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# TIMEZONE
# ==========================================
def now_wita():
    return datetime.now(ZoneInfo("Asia/Makassar"))

def today_wita():
    return now_wita().date()

# ==========================================
# NAMA WORKSHEET
# ==========================================
WS_SK = "DATA_PERPANJANGAN_SK"
WS_PARKIR = "DATA_PARKIR"
WS_KAS = "DATA_KAS"
WS_MASTER_ABSEN = "MASTER_ABSEN"
WS_DATA_ABSEN = "DATA_ABSEN"

# ==========================================
# KOLOM STANDAR
# ==========================================
KOLOM_PARKIR = [
    "No", "Tanggal", "Nama_Petugas",
    "Pengambilan_Karcis_R2", "Pengambilan_Karcis_R4",
    "Khusus_Roda_R2", "Khusus_Roda_R4",
    "MPP_Roda_R2", "MPP_Roda_R4",
    "Total_Karcis_R2", "Total_Karcis_R4",
    "Status_Khusus", "Status_MPP",
    "Sisa_Stok_R2", "Sisa_Stok_R4",
    "Status_Cetak"
]

KOLOM_SK = [
    "No", "Tanggal_Pengantaran", "Tanggal_Pengambilan",
    "Nama_Toko", "No_Toko", "Nama_Pemilik_Asli",
    "No_NIK", "Alamat",
    "Nama_Pengantar_Berkas", "No_HP_Pengantar",
    "Penerima_Berkas"
]

KOLOM_KAS = [
    "No", "Tanggal", "Keterangan",
    "Jenis_Transaksi", "Nominal",
    "PAD_Aktif", "TAKTIS_Aktif",
    "Potongan_PAD", "Potongan_TAKTIS",
    "PPN", "PPH_21_22_23", "Biaya_Admin_Penyedia",
    "Bersih", "Jenis_Keluar", "Nota",
    "Sumber_Anggaran", "Tujuan_Anggaran",
    "Sisa_Uang_Kas_Seluruh_Sebelumnya",
    "Sisa_Uang_Kas_Sebelumnya",
    "Sisa_Uang_Di_ATM", "Sisa_Uang_Di_Penyedia",
    "Sisa_Uang_Kas_Seluruh", "Sisa_Uang_Kas_Auto",
    "Sisa_Uang_Kas", "Selisih_Kurang"
]

KOLOM_MASTER_ABSEN = [
    "No_Absen", "Nama", "NIP", "Gol_Pangkat", "Jabatan"
]

KOLOM_DATA_ABSEN = [
    "Tanggal", "No_Absen", "Nama", "NIP",
    "Gol_Pangkat", "Jabatan", "Keterangan"
]

# ==========================================
# FORMAT & KONVERSI
# ==========================================
def to_float(val):
    try:
        txt = str(val).strip().replace(",", "")
        if txt in ["", "-", "nan", "None", "null", "<NA>"]:
            return 0.0
        return float(txt)
    except:
        return 0.0

def fmt_nominal(val):
    try:
        num = float(val)
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}".rstrip("0").rstrip(".")
    except:
        return "0"

def rupiah(val):
    try:
        num = int(round(float(val)))
        if num < 0:
            return f"-Rp {abs(num):,}".replace(",", ".")
        return f"Rp {num:,}".replace(",", ".")
    except:
        return "Rp 0"

def format_tgl_hari_indo(tgl_str):
    if not tgl_str or str(tgl_str).strip() in ["-", "nan", "NAN", "", "None"]:
        return ""
    try:
        tgl_bersih = str(tgl_str).strip().replace("/", "-")
        if len(tgl_bersih.split("-")[-1]) == 2:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%y")
        else:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%Y")
        hari = ["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU","MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()

def normalisasi_no(val):
    try:
        txt = str(val).replace("\u00a0", "").replace("'", "").strip()
        try:
            return str(int(float(txt)))
        except:
            return txt
    except:
        return ""

def safe_int(val):
    try:
        s = str(val).strip()
        if s in ["-", "nan", "", "None", "null"]:
            return 0
        return int(float(s))
    except:
        return 0

def get_jumlah_hari_bulan_ini():
    h = today_wita()
    return calendar.monthrange(h.year, h.month)[1]

def get_sisa_hari_bulan_ini():
    h = today_wita()
    total = calendar.monthrange(h.year, h.month)[1]
    return total - h.day + 1

def get_bulan_ini_str():
    h = today_wita()
    return f"{h.year}-{h.month:02d}"

def get_jumlah_minggu_bulan_ini():
    if get_jumlah_hari_bulan_ini() <= 28:
        return 4
    return 5

# ==========================================
# DATAFRAME
# ==========================================
def get_empty_df(worksheet):
    if worksheet == WS_PARKIR:
        return pd.DataFrame(columns=KOLOM_PARKIR)
    if worksheet == WS_SK:
        return pd.DataFrame(columns=KOLOM_SK)
    if worksheet == WS_KAS:
        return pd.DataFrame(columns=KOLOM_KAS)
    if worksheet == WS_MASTER_ABSEN:
        return pd.DataFrame(columns=KOLOM_MASTER_ABSEN)
    if worksheet == WS_DATA_ABSEN:
        return pd.DataFrame(columns=KOLOM_DATA_ABSEN)
    return pd.DataFrame()

def pastikan_kolom(df, kolom_list):
    for col in kolom_list:
        if col not in df.columns:
            df[col] = "-"
    return df

def urutkan_no(df, ascending=False):
    try:
        if df.empty or "No" not in df.columns:
            return df
        d = df.copy()
        d["_sort_no"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values(by="_sort_no", ascending=ascending, na_position="last").drop(columns="_sort_no")
        return d
    except:
        return df

def get_next_no(df, col="No"):
    try:
        if df.empty or col not in df.columns:
            return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except:
        return 1

def tampilkan_n_terakhir(df, n=30):
    try:
        if df.empty:
            return df
        return urutkan_no(df, ascending=False).head(n)
    except:
        return df

# ==========================================
# LOAD & SAVE
# ==========================================
def load_data(conn_obj, worksheet):
    try:
        df = conn_obj.read(worksheet=worksheet, ttl=60)
        if df is None or df.empty:
            return get_empty_df(worksheet)

        df = df.astype(str).replace(r"\.0$", "", regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip()
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")

        if worksheet == WS_PARKIR:
            df = pastikan_kolom(df, KOLOM_PARKIR)
            if "Status_Cetak" not in df.columns:
                df["Status_Cetak"] = "BELUM"
                conn_obj.update(worksheet=worksheet, data=df)
                st.cache_data.clear()
        elif worksheet == WS_SK:
            df = pastikan_kolom(df, KOLOM_SK)
        elif worksheet == WS_KAS:
            df = pastikan_kolom(df, KOLOM_KAS)
        elif worksheet == WS_MASTER_ABSEN:
            df = pastikan_kolom(df, KOLOM_MASTER_ABSEN)
        elif worksheet == WS_DATA_ABSEN:
            df = pastikan_kolom(df, KOLOM_DATA_ABSEN)

        return df
    except Exception as e:
        st.error(f"Gagal membaca ({worksheet}): {e}")
        return get_empty_df(worksheet)

def safe_update(conn_obj, worksheet, data):
    try:
        conn_obj.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan ({worksheet}): {e}")
        return False

def tombol_refresh(key_btn):
    if st.button("🔄 Refresh", key=key_btn, use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# FUNGSI PARKIR
# ==========================================
def total_karcis_belum_diisi(r2, r4):
    def kosong(v):
        txt = str(v).strip().lower().replace("\xa0", "").replace("\t", "")
        return txt in ["", "-", "nan", "none", "null", "<na>", "<n/a>"]
    return kosong(r2) and kosong(r4)

def cari_tanggal_belum_input_parkir(df_p):
    try:
        if df_p.empty or "Tanggal" not in df_p.columns:
            return None, pd.DataFrame()
        if "Total_Karcis_R2" not in df_p.columns or "Total_Karcis_R4" not in df_p.columns:
            return None, pd.DataFrame()

        df = df_p.copy()
        df["Tgl_Bersih"] = df["Tanggal"].astype(str).str.strip().str.replace("/", "-", regex=False)
        df["Tgl_Cek"] = pd.to_datetime(df["Tgl_Bersih"], dayfirst=True, errors="coerce").dt.date
        hari_ini = today_wita()

        def is_belum_input(v):
            txt = str(v).strip().lower().replace("\xa0", "").replace("\t", "")
            if txt in ["", "-", "nan", "none", "null", "<na>", "<n/a>"]:
                return True
            try:
                float(txt)
                return False
            except:
                return True

        df["Belum_R2"] = df["Total_Karcis_R2"].apply(is_belum_input)
        df["Belum_R4"] = df["Total_Karcis_R4"].apply(is_belum_input)

        df_belum = df[
            df["Tgl_Cek"].notna() &
            (df["Tgl_Cek"] <= hari_ini) &
            df["Belum_R2"] & df["Belum_R4"]
        ].copy()

        if df_belum.empty:
            return None, pd.DataFrame()

        tanggal_awal = df_belum.sort_values("Tgl_Cek").iloc[0]["Tgl_Cek"]
        return tanggal_awal, df_belum
    except:
        return None, pd.DataFrame()

def daftar_tanggal_kosong_bulan_ini(df_p):
    try:
        if df_p.empty or "Tanggal" not in df_p.columns:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])
        if "Total_Karcis_R2" not in df_p.columns:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])

        df = df_p.copy()
        df["Tgl_Bersih"] = df["Tanggal"].astype(str).str.strip().str.replace("/", "-", regex=False)
        df["Tgl_Cek"] = pd.to_datetime(df["Tgl_Bersih"], dayfirst=True, errors="coerce").dt.date
        hari_ini = today_wita()
        awal_bulan = hari_ini.replace(day=1)

        def is_belum_input(v):
            txt = str(v).strip().lower().replace("\xa0", "").replace("\t", "")
            if txt in ["", "-", "nan", "none", "null", "<na>", "<n/a>"]:
                return True
            try:
                float(txt)
                return False
            except:
                return True

        df["Belum_R2"] = df["Total_Karcis_R2"].apply(is_belum_input)
        df["Belum_R4"] = df["Total_Karcis_R4"].apply(is_belum_input)

        hasil = df[
            df["Tgl_Cek"].notna() &
            (df["Tgl_Cek"] >= awal_bulan) &
            (df["Tgl_Cek"] <= hari_ini) &
            df["Belum_R2"] & df["Belum_R4"]
        ].copy()

        if hasil.empty:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])
        return hasil.sort_values("Tgl_Cek")[["Tanggal", "Nama_Petugas"]]
    except:
        return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])

def daftar_tanggal_belum_konfirmasi_bulan_ini(df_p):
    try:
        if df_p.empty or "Tanggal" not in df_p.columns:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"])

        kolom_wajib = ["Total_Karcis_R2", "Total_Karcis_R4", "Status_Khusus", "Status_MPP", "Status_Cetak", "Nama_Petugas"]
        for col in kolom_wajib:
            if col not in df_p.columns:
                return pd.DataFrame(columns=["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"])

        df = df_p.copy()
        df["Tgl_Bersih"] = df["Tanggal"].astype(str).str.strip().str.replace("/", "-", regex=False)
        df["Tgl_Cek"] = pd.to_datetime(df["Tgl_Bersih"], dayfirst=True, errors="coerce").dt.date
        hari_ini = today_wita()
        awal_bulan = hari_ini.replace(day=1)

        def is_sudah_input(v):
            txt = str(v).strip().lower().replace("\xa0", "").replace("\t", "")
            if txt in ["", "-", "nan", "none", "null", "<na>", "<n/a>"]:
                return False
            try:
                float(txt)
                return True
            except:
                return False

        kondisi_sudah = df["Total_Karcis_R2"].apply(is_sudah_input) | df["Total_Karcis_R4"].apply(is_sudah_input)
        kondisi_belum_selesai = (
            (df["Status_Khusus"].astype(str).str.strip().str.upper() != "SUDAH") |
            (df["Status_MPP"].astype(str).str.strip().str.upper() != "SUDAH") |
            (df["Status_Cetak"].astype(str).str.strip().str.upper() != "SUDAH")
        )

        hasil = df[
            df["Tgl_Cek"].notna() &
            (df["Tgl_Cek"] >= awal_bulan) &
            (df["Tgl_Cek"] <= hari_ini) &
            kondisi_sudah & kondisi_belum_selesai
        ].copy()

        if hasil.empty:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"])
        return hasil.sort_values("Tgl_Cek")[["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"]]
    except:
        return pd.DataFrame(columns=["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"])

# ==========================================
# FUNGSI KAS
# ==========================================
def get_last_kas_state(df_kas):
    try:
        if df_kas.empty:
            return 0.0, 0.0, 0.0, 0.0
        d = df_kas.copy()
        if "No" not in d.columns:
            return 0.0, 0.0, 0.0, 0.0
        d = d[d["No"] != "-"].copy()
        if "Jenis_Transaksi" in d.columns:
            d = d[
                (d["Jenis_Transaksi"].astype(str).str.strip() == "TRANSAKSI") |
                (d["Jenis_Transaksi"].astype(str).str.strip() == "MASUK") |
                (d["Jenis_Transaksi"].astype(str).str.strip() == "KELUAR") |
                (d["Jenis_Transaksi"].astype(str).str.strip() == "TRANSFER") |
                (d["Jenis_Transaksi"].astype(str).str.strip() == "-") |
                (d["Jenis_Transaksi"].astype(str).str.strip() == "")
            ].copy()
        if d.empty:
            return 0.0, 0.0, 0.0, 0.0
        d["_sort_no"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values("_sort_no", ascending=True)
        last = d.iloc[-1]
        last_seluruh = to_float(last.get("Sisa_Uang_Kas_Seluruh", 0))
        last_kas = to_float(last.get("Sisa_Uang_Kas_Auto", to_float(last.get("Sisa_Uang_Kas", 0))))
        last_atm = to_float(last.get("Sisa_Uang_Di_ATM", 0))
        last_penyedia = to_float(last.get("Sisa_Uang_Di_Penyedia", 0))
        return last_seluruh, last_kas, last_atm, last_penyedia
    except:
        return 0.0, 0.0, 0.0, 0.0

def hitung_ringkasan_kas(df_kas):
    try:
        if df_kas.empty:
            return 0.0, 0.0, 0.0, 0.0
        df = df_kas[df_kas["No"] != "-"].copy()
        if "Jenis_Transaksi" not in df.columns:
            return 0.0, 0.0, 0.0, 0.0
        df["_jenis"] = df["Jenis_Transaksi"].astype(str).str.strip().str.upper()
        df["_nominal"] = df["Nominal"].apply(to_float)
        total_masuk = df[df["_jenis"] == "MASUK"]["_nominal"].sum()
        total_keluar = df[df["_jenis"] == "KELUAR"]["_nominal"].sum()
        last_seluruh, last_kas, _, _ = get_last_kas_state(df_kas)
        return total_masuk, total_keluar, last_seluruh, last_kas
    except:
        return 0.0, 0.0, 0.0, 0.0

# ==========================================
# FUNGSI ABSEN
# ==========================================
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

def hitung_rekap_absen_bulanan(df_absen, bulan_str, df_master=None):
    try:
        if df_absen.empty:
            return pd.DataFrame()

        d = df_absen[df_absen["Tanggal"] != "-"].copy()
        d["_tgl"] = d["Tanggal"].astype(str).str.strip().str.replace("-", "/", regex=False)
        d["_bulan"] = d["_tgl"].apply(
            lambda x: "/".join(x.split("/")[1:]) if len(x.split("/")) == 3 else ""
        )
        d = d[d["_bulan"] == bulan_str]

        if d.empty:
            return pd.DataFrame()

        # Ambil semua tanggal unik di bulan ini
        tanggal_unik = d["_tgl"].unique().tolist()
        total_hari_kerja = len(tanggal_unik)

        if total_hari_kerja == 0:
            return pd.DataFrame()

        # Ambil semua pegawai dari master
        if df_master is not None and not df_master.empty:
            semua_pegawai = df_master[df_master["No_Absen"] != "-"][
                ["No_Absen", "Nama", "NIP", "Gol_Pangkat", "Jabatan"]
            ].copy()
        else:
            semua_pegawai = d[
                ["No_Absen", "Nama", "NIP", "Gol_Pangkat", "Jabatan"]
            ].drop_duplicates().copy()

        if semua_pegawai.empty:
            return pd.DataFrame()

        d["Ket_Upper"] = d["Keterangan"].astype(str).str.strip().str.upper()

        # Hitung per pegawai
        hasil_list = []

        for _, pegawai in semua_pegawai.iterrows():
            no = str(pegawai["No_Absen"])

            # Data absen pegawai ini di bulan ini
            data_pg = d[d["No_Absen"].astype(str).str.strip() == no]

            # Hitung keterangan
            sakit = (data_pg["Ket_Upper"] == "SAKIT").sum()
            izin = (data_pg["Ket_Upper"] == "IZIN").sum()
            alpha = (data_pg["Ket_Upper"] == "ALPHA").sum()
            cuti = (data_pg["Ket_Upper"] == "CUTI").sum()

            # Tanggal yang tercatat tidak hadir
            tidak_hadir = sakit + izin + alpha + cuti

            # Hadir = total hari kerja - tidak hadir
            hadir = total_hari_kerja - tidak_hadir

            # Pastikan tidak minus
            if hadir < 0:
                hadir = 0

            total = hadir + sakit + izin + alpha + cuti

            # Persen: Hadir / (Hadir + Alpha) × 100
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
                "Total": total,
                "Hari_Kerja": total_hari_kerja,
                "Persen": persen
            })

        rekap = pd.DataFrame(hasil_list)

        rekap["_sort"] = pd.to_numeric(rekap["No_Absen"], errors="coerce")
        rekap = rekap.sort_values("_sort", ascending=True).drop(columns="_sort")

        return rekap
    except:
        return pd.DataFrame()
