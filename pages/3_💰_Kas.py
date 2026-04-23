# ==========================================
# pages/3_💰_Kas.py
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css
from utils.helpers import (
    WS_KAS,
    KOLOM_KAS,
    load_data,
    safe_update,
    get_next_no,
    pastikan_kolom,
    tampilkan_n_terakhir,
    tombol_refresh,
    to_float,
    fmt_nominal,
    rupiah,
    get_last_kas_state,
    hitung_ringkasan_kas
)

# ==========================================
# KONFIGURASI
# ==========================================
st.set_page_config(
    page_title="Kas UPTD | UPTD Pasar Kandangan",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_css()

# ==========================================
# KONEKSI
# ==========================================
conn_kas = st.connection("gsheets_kas", type=GSheetsConnection)

# ==========================================
# KOLOM TAMBAHAN INTERNAL
# ==========================================
KOLOM_TAMBAHAN_KAS = [
    "Jenis_Record",
    "Kas_Fisik_Pengecekan",
    "Selisih_Pengecekan",
    "Status_Selisih_Aktif",
    "Tanggal_Pengecekan"
]

# ==========================================
# RESET COUNTER
# ==========================================
if "kas_reset_counter" not in st.session_state:
    st.session_state["kas_reset_counter"] = 0

def reset_form_kas():
    st.session_state["kas_reset_counter"] += 1

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
    st.page_link("pages/1_📋_SK_Toko.py", label="📋  SK Toko", use_container_width=True)
    st.page_link("pages/2_🅿️_Parkir.py", label="🅿️  Parkir", use_container_width=True)
    st.page_link("pages/3_💰_Kas.py", label="💰  Kas UPTD", use_container_width=True)
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
# LOAD DATA
# ==========================================
df_kas = load_data(conn_kas, WS_KAS)
df_kas = pastikan_kolom(df_kas, KOLOM_KAS)

for col in KOLOM_TAMBAHAN_KAS:
    if col not in df_kas.columns:
        df_kas[col] = "-"

# ==========================================
# HEADER RINGKASAN
# ==========================================
st.title("💰 KAS UPTD")

c_head, c_btn = st.columns([0.88, 0.12])
c_head.subheader("Ringkasan Kas")
with c_btn:
    tombol_refresh("ref_kas")

total_masuk_bersih, total_keluar, saldo_seluruh, saldo_kas = hitung_ringkasan_kas(df_kas)
last_seluruh, last_kas, last_atm, last_penyedia = get_last_kas_state(df_kas)

# 2 baris x 3 kolom
r1c1, r1c2, r1c3 = st.columns(3)
r1c1.metric("📥 Total Masuk Bersih", rupiah(total_masuk_bersih))
r1c2.metric("📤 Total Keluar", rupiah(total_keluar))
r1c3.metric("🏦 Saldo Kas Seluruh", rupiah(last_seluruh))

r2c1, r2c2, r2c3 = st.columns(3)
r2c1.metric("💵 Kas di Tangan", rupiah(last_kas))
r2c2.metric("🏧 ATM", rupiah(last_atm))
r2c3.metric("🏢 Penyedia", rupiah(last_penyedia))

st.divider()

# ==========================================
# ALERT SELISIH TERSIMPAN
# ==========================================
df_cek = df_kas[
    (df_kas["No"] != "-") &
    (df_kas["Jenis_Record"] == "PENGECEKAN")
].copy()

if not df_cek.empty:
    try:
        df_cek["_sort_no"] = pd.to_numeric(df_cek["No"], errors="coerce")
        df_cek = df_cek.sort_values("_sort_no", ascending=True)
        cek_terakhir = df_cek.iloc[-1]

        status_aktif = str(cek_terakhir.get("Status_Selisih_Aktif", "TIDAK")).strip().upper()
        nilai_selisih = to_float(cek_terakhir.get("Selisih_Pengecekan", 0))
        tgl_cek = str(cek_terakhir.get("Tanggal_Pengecekan", "-")).strip()

        if status_aktif == "YA" and abs(nilai_selisih) > 0.5:
            if nilai_selisih > 0:
                st.error(
                    f"❌ **PERINGATAN SELISIH AKTIF**  \n"
                    f"Pengecekan terakhir pada **{tgl_cek}** menunjukkan "
                    f"**KURANG {rupiah(nilai_selisih)}**."
                )
            else:
                st.success(
                    f"✅ **PERINGATAN SELISIH AKTIF**  \n"
                    f"Pengecekan terakhir pada **{tgl_cek}** menunjukkan "
                    f"**LEBIH {rupiah(abs(nilai_selisih))}**."
                )
    except:
        pass

# ==========================================
# PENGECEKAN SELISIH
# ==========================================
st.subheader("🔎 Pengecekan Selisih Kas")
aktif_cek = st.toggle(
    "Aktifkan pengecekan selisih",
    value=False,
    key="toggle_pengecekan_selisih"
)

if aktif_cek:
    st.info(
        "Bagian ini **hanya untuk pengecekan**. "
        "Tidak mengubah transaksi kas, hanya menyimpan hasil audit selisih."
    )

    st.metric("💵 Kas di Tangan (Hitungan Sistem)", rupiah(last_kas))

    kas_fisik = st.number_input(
        "INPUT KAS DI TANGAN FISIK",
        value=float(last_kas),
        step=1000.0,
        format="%.0f",
        key="input_kas_fisik_cek"
    )

    selisih_cek = last_kas - kas_fisik

    if selisih_cek > 0.5:
        st.warning(
            f"⚠️ **HASIL CEK: KURANG {rupiah(selisih_cek)}**  \n"
            f"Uang fisik di tangan lebih sedikit dari hitungan sistem."
        )
    elif selisih_cek < -0.5:
        st.success(
            f"✅ **HASIL CEK: LEBIH {rupiah(abs(selisih_cek))}**  \n"
            f"Uang fisik di tangan lebih banyak dari hitungan sistem."
        )
    else:
        st.success("✅ **HASIL CEK: PAS / Rp 0**")

    if st.button(
        "💾 SIMPAN HASIL PENGECEKAN",
        use_container_width=True,
        type="primary",
        key="btn_simpan_pengecekan"
    ):
        next_no_cek = get_next_no(df_kas)
        status_aktif = "YA" if abs(selisih_cek) > 0.5 else "TIDAK"

        row_cek = {
            "No": str(next_no_cek),
            "Tanggal": datetime.now().strftime("%d/%m/%Y"),
            "Keterangan": "PENGECEKAN SELISIH KAS",
            "Jenis_Transaksi": "PENGECEKAN",
            "Nominal": "0",
            "PAD_Aktif": "TIDAK",
            "TAKTIS_Aktif": "TIDAK",
            "Potongan_PAD": "0",
            "Potongan_TAKTIS": "0",
            "PPN": "0",
            "PPH_21_22_23": "0",
            "Biaya_Admin_Penyedia": "0",
            "Bersih": "0",
            "Jenis_Keluar": "-",
            "Nota": "-",
            "Sumber_Anggaran": "-",
            "Tujuan_Anggaran": "-",
            "Sisa_Uang_Kas_Seluruh_Sebelumnya": fmt_nominal(last_seluruh),
            "Sisa_Uang_Kas_Sebelumnya": fmt_nominal(last_kas),
            "Sisa_Uang_Di_ATM": fmt_nominal(last_atm),
            "Sisa_Uang_Di_Penyedia": fmt_nominal(last_penyedia),
            "Sisa_Uang_Kas_Seluruh": fmt_nominal(last_seluruh),
            "Sisa_Uang_Kas_Auto": fmt_nominal(last_kas),
            "Sisa_Uang_Kas": fmt_nominal(last_kas),
            "Selisih_Kurang": fmt_nominal(selisih_cek),
            "Jenis_Record": "PENGECEKAN",
            "Kas_Fisik_Pengecekan": fmt_nominal(kas_fisik),
            "Selisih_Pengecekan": fmt_nominal(selisih_cek),
            "Status_Selisih_Aktif": status_aktif,
            "Tanggal_Pengecekan": datetime.now().strftime("%d/%m/%Y")
        }

        df_baru = pd.concat([df_kas, pd.DataFrame([row_cek])], ignore_index=True)
        if safe_update(conn_kas, WS_KAS, df_baru):
            st.success("✅ Hasil pengecekan berhasil disimpan!")
            st.rerun()

st.divider()

# ==========================================
# TAB
# ==========================================
tab1, tab2, tab3 = st.tabs(["📝 INPUT KAS", "📊 DATA KAS", "🔁 KOREKSI REIMBURSE"])

# ==========================================
# TAB 1 - INPUT KAS
# ==========================================
with tab1:
    st.subheader("📝 FORM INPUT KAS")

    rc = st.session_state["kas_reset_counter"]
    next_no = get_next_no(df_kas)

    # FIELD DASAR
    c1, c2 = st.columns(2)
    with c1:
        tanggal_kas = st.text_input(
            "TANGGAL *",
            value=datetime.now().strftime("%d/%m/%Y"),
            key=f"kas_{rc}_tgl"
        )
        keterangan_raw = st.text_input(
            "KETERANGAN *",
            key=f"kas_{rc}_ket"
        )
    with c2:
        jenis_transaksi = st.selectbox(
            "JENIS TRANSAKSI *",
            ["MASUK", "KELUAR"],
            key=f"kas_{rc}_jenis"
        )
        nominal = st.number_input(
            "NOMINAL *",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            format="%.0f",
            key=f"kas_{rc}_nom"
        )

    pad_aktif = False
    taktis_aktif = False
    pot_pad = 0.0
    pot_taktis = 0.0
    ppn = 0.0
    pph = 0.0
    biaya_admin = 0.0
    bersih = 0.0
    jenis_keluar = "-"
    nota = "-"
    sumber_anggaran = "-"
    tujuan_anggaran = "-"

    if jenis_transaksi == "MASUK":
        st.divider()
        st.subheader("📥 DETAIL UANG MASUK")

        a1, a2 = st.columns(2)
        with a1:
            pad_aktif = st.checkbox("PAD (Potongan 10%)", value=False, key=f"kas_{rc}_pad")
            ppn = st.number_input("PPN", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key=f"kas_{rc}_ppn")
            biaya_admin = st.number_input("BIAYA ADMIN PENYEDIA", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key=f"kas_{rc}_admin")
        with a2:
            taktis_aktif = st.checkbox("TAKTIS (Potongan 5%)", value=False, key=f"kas_{rc}_taktis")
            pph = st.number_input("PPH 21/22/23", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key=f"kas_{rc}_pph")

        pot_pad = nominal * 0.10 if pad_aktif else 0.0
        pot_taktis = nominal * 0.05 if taktis_aktif else 0.0
        bersih = nominal - pot_pad - pot_taktis - ppn - pph - biaya_admin

        st.markdown("---")
        p1, p2, p3 = st.columns(3)
        p1.metric("Potongan PAD (10%)", rupiah(pot_pad))
        p2.metric("Potongan TAKTIS (5%)", rupiah(pot_taktis))
        p3.metric("💰 BERSIH", rupiah(bersih))

        st.divider()
        st.subheader("🎯 TUJUAN ANGGARAN MASUK")
        tujuan_anggaran = st.selectbox(
            "UANG MASUK DIARAHKAN KE MANA? *",
            ["SALDO KAS (DI TANGAN)", "UANG DI ATM", "UANG DI PENYEDIA"],
            key=f"kas_{rc}_tujuan"
        )

    else:
        st.divider()
        st.subheader("📤 DETAIL UANG KELUAR")

        b1, b2 = st.columns(2)
        with b1:
            jenis_keluar = st.selectbox(
                "JENIS KELUAR",
                ["DISBURSEMENT", "REIMBURSE"],
                key=f"kas_{rc}_jk"
            )
        with b2:
            nota = st.selectbox(
                "NOTA",
                ["ADA", "TIDAK ADA"],
                key=f"kas_{rc}_nota"
            )

        st.divider()
        st.subheader("💳 SUMBER ANGGARAN")
        sumber_anggaran = st.selectbox(
            "UANG KELUAR DARI MANA? *",
            ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI PENYEDIA"],
            key=f"kas_{rc}_sumber"
        )

        if sumber_anggaran == "UANG KAS (DI TANGAN)":
            st.info(f"💵 Sisa Uang Kas saat ini: **{rupiah(last_kas)}**")
            if nominal > last_kas and nominal > 0:
                st.warning(f"⚠️ Melebihi sisa kas ({rupiah(last_kas)})")
        elif sumber_anggaran == "UANG DI ATM":
            st.info(f"🏧 Sisa Uang ATM saat ini: **{rupiah(last_atm)}**")
            if nominal > last_atm and nominal > 0:
                st.warning(f"⚠️ Melebihi sisa ATM ({rupiah(last_atm)})")
        elif sumber_anggaran == "UANG DI PENYEDIA":
            st.info(f"🏢 Sisa Uang Penyedia saat ini: **{rupiah(last_penyedia)}**")
            if nominal > last_penyedia and nominal > 0:
                st.warning(f"⚠️ Melebihi sisa Penyedia ({rupiah(last_penyedia)})")

    # HITUNG SALDO OTOMATIS TRANSAKSI
    if jenis_transaksi == "MASUK":
        if tujuan_anggaran == "SALDO KAS (DI TANGAN)":
            new_kas = last_kas + bersih
            new_atm = last_atm
            new_penyedia = last_penyedia
        elif tujuan_anggaran == "UANG DI ATM":
            new_kas = last_kas
            new_atm = last_atm + bersih
            new_penyedia = last_penyedia
        elif tujuan_anggaran == "UANG DI PENYEDIA":
            new_kas = last_kas
            new_atm = last_atm
            new_penyedia = last_penyedia + bersih
        else:
            new_kas = last_kas + bersih
            new_atm = last_atm
            new_penyedia = last_penyedia
    else:
        if sumber_anggaran == "UANG KAS (DI TANGAN)":
            new_kas = last_kas - nominal
            new_atm = last_atm
            new_penyedia = last_penyedia
        elif sumber_anggaran == "UANG DI ATM":
            new_kas = last_kas
            new_atm = last_atm - nominal
            new_penyedia = last_penyedia
        elif sumber_anggaran == "UANG DI PENYEDIA":
            new_kas = last_kas
            new_atm = last_atm
            new_penyedia = last_penyedia - nominal
        else:
            new_kas = last_kas - nominal
            new_atm = last_atm
            new_penyedia = last_penyedia

    total_auto = new_kas + new_atm + new_penyedia

    st.divider()
    st.subheader("🏦 HASIL SALDO OTOMATIS TRANSAKSI")
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("💵 Kas di Tangan", rupiah(new_kas))
    h2.metric("🏧 ATM", rupiah(new_atm))
    h3.metric("🏢 Penyedia", rupiah(new_penyedia))
    h4.metric("🏦 Total Kas Seluruh", rupiah(total_auto))

    st.divider()
    cb1, cb2 = st.columns(2)
    with cb1:
        simpan_kas = st.button(
            "💾 SIMPAN DATA KAS",
            type="primary",
            use_container_width=True,
            key="btn_simpan_kas"
        )
    with cb2:
        st.button(
            "🔄 RESET",
            use_container_width=True,
            key="btn_reset_kas",
            on_click=reset_form_kas
        )

    if simpan_kas:
        keterangan = keterangan_raw.strip().upper()
        if not keterangan:
            st.error("❌ Keterangan wajib diisi.")
        elif nominal <= 0:
            st.error("❌ Nominal harus lebih dari 0.")
        elif jenis_transaksi == "MASUK" and bersih < 0:
            st.error("❌ Hasil bersih tidak boleh negatif.")
        else:
            new_row = {
                "No": str(next_no),
                "Tanggal": tanggal_kas,
                "Keterangan": keterangan,
                "Jenis_Transaksi": jenis_transaksi,
                "Nominal": fmt_nominal(nominal),
                "PAD_Aktif": "YA" if pad_aktif else "TIDAK",
                "TAKTIS_Aktif": "YA" if taktis_aktif else "TIDAK",
                "Potongan_PAD": fmt_nominal(pot_pad),
                "Potongan_TAKTIS": fmt_nominal(pot_taktis),
                "PPN": fmt_nominal(ppn),
                "PPH_21_22_23": fmt_nominal(pph),
                "Biaya_Admin_Penyedia": fmt_nominal(biaya_admin),
                "Bersih": fmt_nominal(bersih if jenis_transaksi == "MASUK" else 0),
                "Jenis_Keluar": jenis_keluar,
                "Nota": nota,
                "Sumber_Anggaran": sumber_anggaran if jenis_transaksi == "KELUAR" else "-",
                "Tujuan_Anggaran": tujuan_anggaran if jenis_transaksi == "MASUK" else "-",
                "Sisa_Uang_Kas_Seluruh_Sebelumnya": fmt_nominal(last_seluruh),
                "Sisa_Uang_Kas_Sebelumnya": fmt_nominal(last_kas),
                "Sisa_Uang_Di_ATM": fmt_nominal(new_atm),
                "Sisa_Uang_Di_Penyedia": fmt_nominal(new_penyedia),
                "Sisa_Uang_Kas_Seluruh": fmt_nominal(total_auto),
                "Sisa_Uang_Kas_Auto": fmt_nominal(new_kas),
                "Sisa_Uang_Kas": fmt_nominal(new_kas),
                "Selisih_Kurang": fmt_nominal(total_selisih_lama),
                "Jenis_Record": "TRANSAKSI",
                "Kas_Fisik_Pengecekan": "-",
                "Selisih_Pengecekan": "0",
                "Status_Selisih_Aktif": "TIDAK",
                "Tanggal_Pengecekan": "-"
            }

            df_baru = pd.concat([df_kas, pd.DataFrame([new_row])], ignore_index=True)
            if safe_update(conn_kas, WS_KAS, df_baru):
                st.success("✅ Data kas berhasil disimpan!")
                reset_form_kas()
                st.rerun()

# ==========================================
# TAB 2 - DATA KAS
# ==========================================
with tab2:
    c_head2, c_btn2 = st.columns([0.88, 0.12])
    c_head2.subheader("📊 DATA KAS UPTD")
    with c_btn2:
        tombol_refresh("ref_kas_data")

    if df_kas.empty or len(df_kas[df_kas["No"] != "-"]) == 0:
        st.info("Belum ada data kas.")
    else:
        tampil = df_kas[
            (df_kas["No"] != "-") &
            (df_kas["Jenis_Record"] != "PENGECEKAN")
        ].copy()

        kolom_tampil = [
            "No", "Tanggal", "Keterangan",
            "Jenis_Transaksi", "Nominal",
            "PAD_Aktif", "TAKTIS_Aktif",
            "Potongan_PAD", "Potongan_TAKTIS",
            "PPN", "PPH_21_22_23",
            "Biaya_Admin_Penyedia", "Bersih",
            "Jenis_Keluar", "Nota",
            "Sumber_Anggaran", "Tujuan_Anggaran",
            "Sisa_Uang_Di_ATM", "Sisa_Uang_Di_Penyedia",
            "Sisa_Uang_Kas_Seluruh", "Sisa_Uang_Kas",
            "Selisih_Kurang"
        ]
        kolom_ada = [k for k in kolom_tampil if k in tampil.columns]

        st.dataframe(
            tampilkan_n_terakhir(tampil, 30)[kolom_ada],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# TAB 3 - KOREKSI REIMBURSE
# ==========================================
with tab3:
    c_head3, c_btn3 = st.columns([0.88, 0.12])
    c_head3.subheader("🔁 KOREKSI REIMBURSE → DISBURSEMENT")
    with c_btn3:
        tombol_refresh("ref_kas_koreksi")

    if df_kas.empty:
        st.info("Belum ada data kas.")
    else:
        df_reimburse = df_kas[
            (df_kas["No"] != "-") &
            (df_kas["Jenis_Transaksi"] == "KELUAR") &
            (df_kas["Jenis_Keluar"] == "REIMBURSE") &
            (~df_kas["Keterangan"].astype(str).str.contains("SUDAH DIKOREKSI", case=False, na=False))
        ].copy()

        if df_reimburse.empty:
            st.success("✅ Tidak ada transaksi Reimburse yang perlu dikoreksi.")
        else:
            st.info(f"Ditemukan **{len(df_reimburse)}** transaksi Reimburse yang bisa dikoreksi.")

            for idx, row in df_reimburse.iterrows():
                tgl = row.get("Tanggal", "-")
                ket = row.get("Keterangan", "-")
                nom = row.get("Nominal", "0")
                sumber = row.get("Sumber_Anggaran", "-")

                with st.expander(
                    f"📋 No.{row.get('No','-')} | {tgl} | {ket} | {rupiah(to_float(nom))}",
                    expanded=False
                ):
                    st.write(f"**Tanggal:** {tgl}")
                    st.write(f"**Keterangan:** {ket}")
                    st.write(f"**Nominal:** {rupiah(to_float(nom))}")
                    st.write(f"**Sumber Anggaran:** {sumber}")
                    st.write(f"**Nota:** {row.get('Nota', '-')}")

                    st.divider()

                    if st.button(
                        "🔁 KOREKSI → Kembalikan ke Kas",
                        key=f"koreksi_{idx}",
                        type="primary",
                        use_container_width=True
                    ):
                        df_update = df_kas.copy()

                        # tandai transaksi lama
                        df_update.loc[idx, "Keterangan"] = f"{ket} [SUDAH DIKOREKSI]"
                        df_update.loc[idx, "Jenis_Keluar"] = "DISBURSEMENT"

                        # ambil saldo terakhir terbaru
                        ls, lk, la, lp = get_last_kas_state(df_update)

                        # buat transaksi masuk koreksi
                        next_no_koreksi = get_next_no(df_update)
                        koreksi_row = {
                            "No": str(next_no_koreksi),
                            "Tanggal": datetime.now().strftime("%d/%m/%Y"),
                            "Keterangan": f"KOREKSI REIMBURSE: {ket}",
                            "Jenis_Transaksi": "MASUK",
                            "Nominal": fmt_nominal(to_float(nom)),
                            "PAD_Aktif": "TIDAK",
                            "TAKTIS_Aktif": "TIDAK",
                            "Potongan_PAD": "0",
                            "Potongan_TAKTIS": "0",
                            "PPN": "0",
                            "PPH_21_22_23": "0",
                            "Biaya_Admin_Penyedia": "0",
                            "Bersih": fmt_nominal(to_float(nom)),
                            "Jenis_Keluar": "-",
                            "Nota": "-",
                            "Sumber_Anggaran": "-",
                            "Tujuan_Anggaran": sumber if sumber in ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI PENYEDIA"] else "SALDO KAS (DI TANGAN)",
                            "Sisa_Uang_Kas_Seluruh_Sebelumnya": fmt_nominal(ls),
                            "Sisa_Uang_Kas_Sebelumnya": fmt_nominal(lk),
                            "Sisa_Uang_Di_ATM": fmt_nominal(la),
                            "Sisa_Uang_Di_Penyedia": fmt_nominal(lp),
                            "Sisa_Uang_Kas_Seluruh": fmt_nominal(ls + to_float(nom)),
                            "Sisa_Uang_Kas_Auto": fmt_nominal(lk + to_float(nom)),
                            "Sisa_Uang_Kas": fmt_nominal(lk + to_float(nom)),
                            "Selisih_Kurang": fmt_nominal(to_float(df_update[df_update['No'] != '-']['Selisih_Kurang'].iloc[-1]) if not df_update[df_update['No'] != '-'].empty else 0),
                            "Jenis_Record": "TRANSAKSI",
                            "Kas_Fisik_Pengecekan": "-",
                            "Selisih_Pengecekan": "0",
                            "Status_Selisih_Aktif": "TIDAK",
                            "Tanggal_Pengecekan": "-"
                        }

                        df_update = pd.concat([df_update, pd.DataFrame([koreksi_row])], ignore_index=True)

                        if safe_update(conn_kas, WS_KAS, df_update):
                            st.success(
                                f"✅ Transaksi Reimburse **{ket}** berhasil dikoreksi!\n\n"
                                f"Uang **{rupiah(to_float(nom))}** dikembalikan ke kas."
                            )
                            st.rerun()
