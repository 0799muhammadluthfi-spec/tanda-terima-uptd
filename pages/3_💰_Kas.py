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

def reset_form_kas():
    keys_to_delete = [k for k in list(st.session_state.keys()) if k.startswith("kas_")]
    for k in keys_to_delete:
        del st.session_state[k]

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
# HEADER
# ==========================================
st.title("💰 KAS UPTD")

c_head, c_btn = st.columns([0.88, 0.12])
c_head.subheader("Ringkasan Kas")
with c_btn:
    tombol_refresh("ref_kas")

total_masuk_bersih, total_keluar, saldo_seluruh, saldo_kas = hitung_ringkasan_kas(df_kas)

m1, m2, m3, m4 = st.columns(4)
m1.metric("📥 Total Masuk Bersih", rupiah(total_masuk_bersih))
m2.metric("📤 Total Keluar", rupiah(total_keluar))
m3.metric("🏦 Saldo Kas Seluruh", rupiah(saldo_seluruh))
m4.metric("💵 Saldo Kas Tangan", rupiah(saldo_kas))

st.divider()

tab1, tab2 = st.tabs(["📝 INPUT KAS", "📊 DATA KAS"])

# ==========================================
# TAB 1 - INPUT KAS
# ==========================================
with tab1:
    st.subheader("📝 FORM INPUT KAS")

    last_seluruh, last_kas, last_atm, last_penyedia = get_last_kas_state(df_kas)
    next_no = get_next_no(df_kas)

    # ── FIELD DASAR ──
    c1, c2 = st.columns(2)
    with c1:
        tanggal_kas = st.text_input(
            "TANGGAL *",
            value=datetime.now().strftime("%d-%m-%Y"),
            key="kas_tgl"
        )
        keterangan = st.text_input(
            "KETERANGAN *",
            key="kas_ket"
        ).strip().upper()
    with c2:
        jenis_transaksi = st.selectbox(
            "JENIS TRANSAKSI *",
            ["MASUK", "KELUAR"],
            key="kas_jenis"
        )
        nominal = st.number_input(
            "NOMINAL *",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            format="%.0f",
            key="kas_nom"
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
            pad_aktif = st.checkbox("PAD (Potongan 10%)", value=False, key="kas_pad")
            ppn = st.number_input("PPN", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key="kas_ppn")
            biaya_admin = st.number_input("BIAYA ADMIN PENYEDIA", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key="kas_admin")
        with a2:
            taktis_aktif = st.checkbox("TAKTIS (Potongan 5%)", value=False, key="kas_taktis")
            pph = st.number_input("PPH 21/22/23", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key="kas_pph")

        pot_pad = nominal * 0.10 if pad_aktif else 0.0
        pot_taktis = nominal * 0.05 if taktis_aktif else 0.0
        bersih = nominal - pot_pad - pot_taktis - ppn - pph - biaya_admin

        st.markdown("---")
        p1, p2, p3 = st.columns(3)
        p1.metric("Potongan PAD (10%)", rupiah(pot_pad))
        p2.metric("Potongan TAKTIS (5%)", rupiah(pot_taktis))
        p3.metric("💰 BERSIH", rupiah(bersih))

        # ── TUJUAN ANGGARAN MASUK (POIN 4) ──
        st.divider()
        st.subheader("🎯 TUJUAN ANGGARAN MASUK")
        tujuan_anggaran = st.selectbox(
            "UANG MASUK DIARAHKAN KE MANA? *",
            ["SALDO KAS (DI TANGAN)", "UANG DI ATM", "UANG DI PENYEDIA"],
            key="kas_tujuan"
        )

    # ══════════════════════════════════════════
    # DETAIL KELUAR
    # ══════════════════════════════════════════
    else:
        st.divider()
        st.subheader("📤 DETAIL UANG KELUAR")

        b1, b2 = st.columns(2)
        with b1:
            jenis_keluar = st.selectbox("JENIS KELUAR", ["DISBURSEMENT", "REIMBURSE"], key="kas_jk")
        with b2:
            nota = st.selectbox("NOTA", ["ADA", "TIDAK ADA"], key="kas_nota")

        st.divider()
        st.subheader("💳 SUMBER ANGGARAN")
        sumber_anggaran = st.selectbox(
            "UANG KELUAR DARI MANA? *",
            ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI PENYEDIA"],
            key="kas_sumber"
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

    # ── HITUNG SALDO BARU (POIN 5 & 6) ──
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

    # ── POSISI SALDO BARU (POIN 5) ──
    st.divider()
    st.subheader("🏦 POSISI SALDO BARU")

    k1, k2, k3 = st.columns(3)
    with k1:
        sisa_kas_input = st.number_input(
            "SISA KAS DI TANGAN",
            value=float(new_kas),
            step=1000.0,
            format="%.0f",
            key="kas_sisa_tangan"
        )
    with k2:
        sisa_atm = st.number_input(
            "SISA UANG DI ATM",
            value=float(new_atm),
            step=1000.0,
            format="%.0f",
            key="kas_atm"
        )
    with k3:
        sisa_penyedia = st.number_input(
            "SISA UANG DI PENYEDIA",
            value=float(new_penyedia),
            step=1000.0,
            format="%.0f",
            key="kas_peny"
        )

    # ── HASIL PERHITUNGAN ──
    sisa_uang_kas_seluruh = sisa_kas_input + sisa_atm + sisa_penyedia

    # ── SELISIH ──
    selisih_kurang = sisa_uang_kas_seluruh - sisa_kas_input

    if selisih_kurang > 0.5:
        st.warning(f"⚠️ SELISIH / KURANG: **{rupiah(selisih_kurang)}** (uang di tangan kurang dari seharusnya)")
    elif selisih_kurang < -0.5:
        st.success(f"✅ SELISIH / LEBIH: **{rupiah(abs(selisih_kurang))}** (uang di tangan lebih dari seharusnya)")
    else:
        st.success("✅ SELISIH: **Rp 0** (Pas)")

    # ── TOMBOL SIMPAN & RESET (POIN 7) ──
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
        if not keterangan.strip():
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
