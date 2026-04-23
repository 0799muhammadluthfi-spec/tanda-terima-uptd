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
    urutkan_no,
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

# ==========================================
# HEADER — 6 METRIC (2 baris × 3 kolom)
# ==========================================
st.title("💰 KAS UPTD")

c_head, c_btn = st.columns([0.88, 0.12])
c_head.subheader("Ringkasan Kas")
with c_btn:
    tombol_refresh("ref_kas")

total_masuk_bersih, total_keluar, saldo_seluruh, saldo_kas = hitung_ringkasan_kas(df_kas)
last_seluruh, last_kas, last_atm, last_penyedia = get_last_kas_state(df_kas)

# Baris 1
r1c1, r1c2, r1c3 = st.columns(3)
r1c1.metric("📥 Total Masuk Bersih", rupiah(total_masuk_bersih))
r1c2.metric("📤 Total Keluar", rupiah(total_keluar))
r1c3.metric("🏦 Saldo Kas Seluruh", rupiah(last_seluruh))

# Baris 2
r2c1, r2c2, r2c3 = st.columns(3)
r2c1.metric("💵 Kas di Tangan", rupiah(last_kas))
r2c2.metric("🏧 ATM", rupiah(last_atm))
r2c3.metric("🏢 Penyedia", rupiah(last_penyedia))

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

    # ── FIELD DASAR ──
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

    # ── Default ──
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

    # ══════════════════════════════════════════
    # DETAIL MASUK
    # ══════════════════════════════════════════
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

    # ══════════════════════════════════════════
    # DETAIL KELUAR
    # ══════════════════════════════════════════
    else:
        st.divider()
        st.subheader("📤 DETAIL UANG KELUAR")

        b1, b2 = st.columns(2)
        with b1:
            jenis_keluar = st.selectbox("JENIS KELUAR", ["DISBURSEMENT", "REIMBURSE"], key=f"kas_{rc}_jk")
        with b2:
            nota = st.selectbox("NOTA", ["ADA", "TIDAK ADA"], key=f"kas_{rc}_nota")

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

    # ── SALDO TERAKHIR ──
    st.divider()
    st.subheader("📌 SALDO TERAKHIR")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Kas Seluruh", rupiah(last_seluruh))
    s2.metric("Kas di Tangan", rupiah(last_kas))
    s3.metric("Di ATM", rupiah(last_atm))
    s4.metric("Di Penyedia", rupiah(last_penyedia))

    # ── HITUNG SALDO BARU ──
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

    # ── POSISI SALDO BARU (OTOMATIS) ──
    st.divider()
    st.subheader("🏦 POSISI SALDO BARU (OTOMATIS)")

    total_auto = new_kas + new_atm + new_penyedia

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💵 Kas di Tangan", rupiah(new_kas))
    k2.metric("🏧 ATM", rupiah(new_atm))
    k3.metric("🏢 Penyedia", rupiah(new_penyedia))
    k4.metric("🏦 Total Kas Seluruh", rupiah(total_auto))

    st.caption("Input uang kas fisik di tangan untuk cek selisih:")

    sisa_kas_input = st.number_input(
        "INPUT UANG KAS DI TANGAN (FISIK)",
        value=float(new_kas),
        step=1000.0,
        format="%.0f",
        key=f"kas_{rc}_sisa_tangan"
    )

    sisa_atm = float(new_atm)
    sisa_penyedia = float(new_penyedia)
    sisa_uang_kas_seluruh = total_auto

    # ── SELISIH ──
    selisih_transaksi = new_kas - sisa_kas_input

    total_selisih_lama = 0.0
    try:
        df_valid = df_kas[df_kas["No"] != "-"].copy()
        if not df_valid.empty:
            total_selisih_lama = to_float(df_valid["Selisih_Kurang"].iloc[-1])
    except:
        total_selisih_lama = 0.0

    total_selisih = total_selisih_lama + selisih_transaksi
    selisih_kurang = total_selisih

    st.divider()
    st.subheader("📊 SELISIH")

    if abs(selisih_transaksi) > 0.5:
        if selisih_transaksi > 0:
            st.warning(f"⚠️ **SELISIH TRANSAKSI INI: KURANG {rupiah(selisih_transaksi)}**")
        else:
            st.info(f"ℹ️ **SELISIH TRANSAKSI INI: LEBIH {rupiah(abs(selisih_transaksi))}**")

    if abs(total_selisih) > 0.5:
        if total_selisih > 0:
            st.error(
                f"❌ **TOTAL SELISIH: KURANG {rupiah(total_selisih)}**  \n"
                f"Total uang di tangan masih kurang {rupiah(total_selisih)}."
            )
        else:
            st.success(
                f"✅ **TOTAL SELISIH: LEBIH {rupiah(abs(total_selisih))}**  \n"
                f"Total uang di tangan masih lebih {rupiah(abs(total_selisih))}."
            )
    else:
        st.success("✅ **TOTAL SELISIH: Rp 0** (Tidak ada selisih)")

    # ── TOMBOL SIMPAN & RESET ──
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
                "Sisa_Uang_Di_ATM": fmt_nominal(sisa_atm),
                "Sisa_Uang_Di_Penyedia": fmt_nominal(sisa_penyedia),
                "Sisa_Uang_Kas_Seluruh": fmt_nominal(sisa_uang_kas_seluruh),
                "Sisa_Uang_Kas_Auto": fmt_nominal(new_kas),
                "Sisa_Uang_Kas": fmt_nominal(sisa_kas_input),
                "Selisih_Kurang": fmt_nominal(selisih_kurang)
            }

            df_baru = pd.concat(
                [df_kas, pd.DataFrame([new_row])],
                ignore_index=True
            )
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
        tampil = df_kas[df_kas["No"] != "-"].copy()

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
        # Filter transaksi REIMBURSE yang belum dikoreksi
        df_reimburse = df_kas[
            (df_kas["No"] != "-") &
            (df_kas["Jenis_Transaksi"] == "KELUAR") &
            (df_kas["Jenis_Keluar"] == "REIMBURSE") &
            (~df_kas["Keterangan"].str.contains("SUDAH DIKOREKSI", case=False, na=False))
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
                        f"🔁 KOREKSI → Kembalikan ke Kas",
                        key=f"koreksi_{idx}",
                        type="primary",
                        use_container_width=True
                    ):
                        # 1. Tandai transaksi lama sebagai SUDAH DIKOREKSI
                        df_kas.loc[idx, "Keterangan"] = f"{ket} [SUDAH DIKOREKSI]"
                        df_kas.loc[idx, "Jenis_Keluar"] = "DISBURSEMENT"

                        # 2. Buat transaksi MASUK koreksi
                        next_no_koreksi = get_next_no(df_kas)
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
                            "Tujuan_Anggaran": sumber,
                            "Sisa_Uang_Kas_Seluruh_Sebelumnya": fmt_nominal(last_seluruh),
                            "Sisa_Uang_Kas_Sebelumnya": fmt_nominal(last_kas),
                            "Sisa_Uang_Di_ATM": fmt_nominal(last_atm),
                            "Sisa_Uang_Di_Penyedia": fmt_nominal(last_penyedia),
                            "Sisa_Uang_Kas_Seluruh": fmt_nominal(last_seluruh + to_float(nom)),
                            "Sisa_Uang_Kas_Auto": fmt_nominal(last_kas + to_float(nom)),
                            "Sisa_Uang_Kas": fmt_nominal(last_kas + to_float(nom)),
                            "Selisih_Kurang": "0"
                        }

                        df_kas = pd.concat(
                            [df_kas, pd.DataFrame([koreksi_row])],
                            ignore_index=True
                        )

                        if safe_update(conn_kas, WS_KAS, df_kas):
                            st.success(
                                f"✅ Transaksi Reimburse **{ket}** berhasil dikoreksi!\n\n"
                                f"Uang **{rupiah(to_float(nom))}** dikembalikan ke kas."
                            )
                            st.rerun()
