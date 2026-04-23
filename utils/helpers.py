# ==========================================
# utils/helpers.py
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# NAMA WORKSHEET
# ==========================================
WS_SK = "DATA_PERPANJANGAN_SK"
WS_PARKIR = "DATA_PARKIR"
WS_KAS = "DATA_KAS"

# ==========================================
# TIMEZONE WITA
# ==========================================
def now_wita():
    return datetime.now(ZoneInfo("Asia/Makassar"))

def today_wita():
    return now_wita().date()

def total_karcis_belum_diisi(r2, r4):
    def kosong(v):
        txt = str(v).strip().lower().replace("\xa0", "").replace("\t", "")
        return txt in ["", "-", "nan", "none", "null", "<na>", "<n/a>"]

    return kosong(r2) and kosong(r4)

# ==========================================
# KOLOM STANDAR
# ==========================================
KOLOM_PARKIR = [
    "No",
    "Tanggal",
    "Nama_Petugas",
    "Pengambilan_Karcis_R2",
    "Pengambilan_Karcis_R4",
    "Khusus_Roda_R2",
    "Khusus_Roda_R4",
    "MPP_Roda_R2",
    "MPP_Roda_R4",
    "Total_Karcis_R2",
    "Total_Karcis_R4",
    "Status_Khusus",
    "Status_MPP",
    "Sisa_Stok_R2",
    "Sisa_Stok_R4",
    "Status_Cetak"
]

KOLOM_SK = [
    "No",
    "Tanggal_Pengantaran",
    "Tanggal_Pengambilan",
    "Nama_Toko",
    "No_Toko",
    "Nama_Pemilik_Asli",
    "No_NIK",
    "Alamat",
    "Nama_Pengantar_Berkas",
    "Penerima_Berkas"
]

KOLOM_KAS = [
    "No",
    "Tanggal",
    "Keterangan",
    "Jenis_Transaksi",
    "Nominal",
    "PAD_Aktif",
    "TAKTIS_Aktif",
    "Potongan_PAD",
    "Potongan_TAKTIS",
    "PPN",
    "PPH_21_22_23",
    "Biaya_Admin_Penyedia",
    "Bersih",
    "Jenis_Keluar",
    "Nota",
    "Sumber_Anggaran",
    "Tujuan_Anggaran",
    "Sisa_Uang_Kas_Seluruh_Sebelumnya",
    "Sisa_Uang_Kas_Sebelumnya",
    "Sisa_Uang_Di_ATM",
    "Sisa_Uang_Di_Penyedia",
    "Sisa_Uang_Kas_Seluruh",
    "Sisa_Uang_Kas_Auto",
    "Sisa_Uang_Kas",
    "Selisih_Kurang"
]

# ==========================================
# FUNGSI FORMAT & KONVERSI
# ==========================================
def to_float(val) -> float:
    try:
        txt = str(val).strip().replace(",", "")
        if txt in ["", "-", "nan", "None", "null", "<NA>"]:
            return 0.0
        return float(txt)
    except:
        return 0.0


def fmt_nominal(val) -> str:
    try:
        num = float(val)
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}".rstrip("0").rstrip(".")
    except:
        return "0"


def rupiah(val) -> str:
    try:
        return f"Rp {int(round(float(val))):,}".replace(",", ".")
    except:
        return "Rp 0"


def format_tgl_hari_indo(tgl_str) -> str:
    if not tgl_str or str(tgl_str).strip() in ["-", "nan", "NAN", "", "None"]:
        return ""
    try:
        tgl_bersih = str(tgl_str).strip().replace("/", "-")
        if len(tgl_bersih.split("-")[-1]) == 2:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%y")
        else:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%Y")
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        return f"{hari}, {dt.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()


def normalisasi_no(val) -> str:
    try:
        txt = str(val).replace("\u00a0", "").replace("'", "").strip()
        try:
            return str(int(float(txt)))
        except:
            return txt
    except:
        return ""


def safe_int(val) -> int:
    try:
        s = str(val).strip()
        if s in ["-", "nan", "", "None", "null"]:
            return 0
        return int(float(s))
    except:
        return 0

# ==========================================
# FUNGSI DATAFRAME
# ==========================================
def get_empty_df(worksheet: str) -> pd.DataFrame:
    if worksheet == WS_PARKIR:
        return pd.DataFrame(columns=KOLOM_PARKIR)
    if worksheet == WS_SK:
        return pd.DataFrame(columns=KOLOM_SK)
    if worksheet == WS_KAS:
        return pd.DataFrame(columns=KOLOM_KAS)
    return pd.DataFrame()


def pastikan_kolom(df: pd.DataFrame, kolom_list: list) -> pd.DataFrame:
    for col in kolom_list:
        if col not in df.columns:
            df[col] = "-"
    return df


def urutkan_no(df: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
    try:
        if df.empty or "No" not in df.columns:
            return df
        d = df.copy()
        d["_sort_no"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values(by="_sort_no", ascending=ascending, na_position="last").drop(columns="_sort_no")
        return d
    except:
        return df


def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns:
            return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except:
        return 1


def tampilkan_n_terakhir(df: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    try:
        if df.empty:
            return df
        return urutkan_no(df, ascending=False).head(n)
    except:
        return df

# ==========================================
# FUNGSI LOAD & SAVE DATA
# ==========================================
def load_data(conn_obj, worksheet: str) -> pd.DataFrame:
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

        return df

    except Exception as e:
        st.error(f"Gagal membaca data ({worksheet}): {e}")
        return get_empty_df(worksheet)


def safe_update(conn_obj, worksheet: str, data: pd.DataFrame) -> bool:
    try:
        conn_obj.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan ({worksheet}): {e}")
        return False


def tombol_refresh(key_btn: str):
    if st.button("🔄 Refresh", key=key_btn, use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# FUNGSI KHUSUS PARKIR
# ==========================================
def cari_tanggal_belum_input_parkir(df_p: pd.DataFrame):
    try:
        if df_p.empty or "Tanggal" not in df_p.columns:
            return None, pd.DataFrame()
        if "Total_Karcis_R2" not in df_p.columns or "Total_Karcis_R4" not in df_p.columns:
            return None, pd.DataFrame()

        df = df_p.copy()
        df["Tgl_Bersih"] = df["Tanggal"].astype(str).str.strip().str.replace("/", "-", regex=False)
        df["Tgl_Cek"] = pd.to_datetime(df["Tgl_Bersih"], dayfirst=True, errors="coerce").dt.date

        hari_ini = today_wita()

        df["Belum_Input"] = df.apply(
            lambda row: total_karcis_belum_diisi(
                row.get("Total_Karcis_R2", ""),
                row.get("Total_Karcis_R4", "")
            ),
            axis=1
        )

        df_belum = df[
            (df["Tgl_Cek"].notna()) &
            (df["Tgl_Cek"] <= hari_ini) &
            (df["Belum_Input"])
        ].copy()

        if df_belum.empty:
            return None, pd.DataFrame()

        tanggal_awal = df_belum.sort_values("Tgl_Cek").iloc[0]["Tgl_Cek"]
        return tanggal_awal, df_belum

    except Exception:
        return None, pd.DataFrame()

def daftar_tanggal_kosong_bulan_ini(df_p: pd.DataFrame) -> pd.DataFrame:
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

        kondisi_belum = (
            df["Total_Karcis_R2"].astype(str).str.strip().isin(["-", "nan", "", "None", "null"]) &
            df["Total_Karcis_R4"].astype(str).str.strip().isin(["-", "nan", "", "None", "null"])
        )

        hasil = df[
            df["Tgl_Cek"].notna() &
            (df["Tgl_Cek"] >= awal_bulan) &
            (df["Tgl_Cek"] <= hari_ini) &
            kondisi_belum
        ].copy()

        if hasil.empty:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])

        return hasil.sort_values("Tgl_Cek")[["Tanggal", "Nama_Petugas"]]
    except:
        return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])


def daftar_tanggal_kosong_bulan_ini(df_p: pd.DataFrame) -> pd.DataFrame:
    try:
        if df_p.empty or "Tanggal" not in df_p.columns:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])
        if "Total_Karcis_R2" not in df_p.columns or "Total_Karcis_R4" not in df_p.columns:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])

        df = df_p.copy()
        df["Tgl_Bersih"] = df["Tanggal"].astype(str).str.strip().str.replace("/", "-", regex=False)
        df["Tgl_Cek"] = pd.to_datetime(df["Tgl_Bersih"], dayfirst=True, errors="coerce").dt.date

        hari_ini = today_wita()
        awal_bulan = hari_ini.replace(day=1)

        df["Belum_Input"] = df.apply(
            lambda row: total_karcis_belum_diisi(
                row.get("Total_Karcis_R2", ""),
                row.get("Total_Karcis_R4", "")
            ),
            axis=1
        )

        hasil = df[
            (df["Tgl_Cek"].notna()) &
            (df["Tgl_Cek"] >= awal_bulan) &
            (df["Tgl_Cek"] <= hari_ini) &
            (df["Belum_Input"])
        ].copy()

        if hasil.empty:
            return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])

        return hasil.sort_values("Tgl_Cek")[["Tanggal", "Nama_Petugas"]]

    except Exception:
        return pd.DataFrame(columns=["Tanggal", "Nama_Petugas"])

def daftar_tanggal_belum_konfirmasi_bulan_ini(df_p: pd.DataFrame) -> pd.DataFrame:
    try:
        if df_p.empty or "Tanggal" not in df_p.columns:
            return pd.DataFrame(
                columns=["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"]
            )

        kolom_wajib = [
            "Total_Karcis_R2",
            "Total_Karcis_R4",
            "Status_Khusus",
            "Status_MPP",
            "Status_Cetak",
            "Nama_Petugas"
        ]
        for col in kolom_wajib:
            if col not in df_p.columns:
                return pd.DataFrame(
                    columns=["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"]
                )

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

        kondisi_sudah_input = (
            df["Total_Karcis_R2"].apply(is_sudah_input) |
            df["Total_Karcis_R4"].apply(is_sudah_input)
        )

        kondisi_belum_selesai = (
            (df["Status_Khusus"].astype(str).str.strip().str.upper() != "SUDAH") |
            (df["Status_MPP"].astype(str).str.strip().str.upper() != "SUDAH") |
            (df["Status_Cetak"].astype(str).str.strip().str.upper() != "SUDAH")
        )

        hasil = df[
            (df["Tgl_Cek"].notna()) &
            (df["Tgl_Cek"] >= awal_bulan) &
            (df["Tgl_Cek"] <= hari_ini) &
            kondisi_sudah_input &
            kondisi_belum_selesai
        ].copy()

        if hasil.empty:
            return pd.DataFrame(
                columns=["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"]
            )

        return hasil.sort_values("Tgl_Cek")[[
            "Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"
        ]]

    except Exception:
        return pd.DataFrame(
            columns=["Tanggal", "Nama_Petugas", "Status_Khusus", "Status_MPP", "Status_Cetak"]
        )

# ==========================================
# FUNGSI KHUSUS KAS
# ==========================================
def get_last_kas_state(df_kas: pd.DataFrame):
    try:
        if df_kas.empty:
            return 0.0, 0.0, 0.0, 0.0

        d = df_kas.copy()

        if "No" not in d.columns:
            return 0.0, 0.0, 0.0, 0.0

        d = d[d["No"] != "-"].copy()

        # Ambil hanya transaksi, abaikan pengecekan
        if "Jenis_Record" in d.columns:
            d = d[
                (d["Jenis_Record"].astype(str).str.strip() == "TRANSAKSI") |
                (d["Jenis_Record"].astype(str).str.strip() == "-") |
                (d["Jenis_Record"].astype(str).str.strip() == "")
            ].copy()

        if d.empty:
            return 0.0, 0.0, 0.0, 0.0

        d["_sort_no"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values("_sort_no", ascending=True)

        last = d.iloc[-1]

        last_kas = to_float(last.get("Sisa_Uang_Kas_Auto", 0))
        last_atm = to_float(last.get("Sisa_Uang_Di_ATM", 0))
        last_penyedia = to_float(last.get("Sisa_Uang_Di_Penyedia", 0))
        last_seluruh = last_kas + last_atm + last_penyedia

        return last_seluruh, last_kas, last_atm, last_penyedia
    except:
        return 0.0, 0.0, 0.0, 0.0

def hitung_ringkasan_kas(df_kas: pd.DataFrame):
    try:
        if df_kas.empty:
            return 0.0, 0.0, 0.0, 0.0

        df = df_kas[df_kas["No"] != "-"].copy()

        total_masuk_bersih = df[df["Jenis_Transaksi"] == "MASUK"]["Bersih"].apply(to_float).sum()
        total_keluar = df[df["Jenis_Transaksi"] == "KELUAR"]["Nominal"].apply(to_float).sum()

        last_seluruh, last_kas, _, _ = get_last_kas_state(df)

        return total_masuk_bersih, total_keluar, last_seluruh, last_kas
    except:
        return 0.0, 0.0, 0.0, 0.0
