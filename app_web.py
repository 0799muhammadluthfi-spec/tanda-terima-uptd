import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UPTD PASAR KANDANGAN", layout="wide")

# --- KONEKSI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI KAMUS TANGGAL INDONESIA ---
def format_tgl_indo(tgl_input):
    if not tgl_input or tgl_input == "-" or str(tgl_input).lower() == "nan": return ""
    try:
        dt = pd.to_datetime(tgl_input, dayfirst=True)
        hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"][dt.weekday()]
        bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", 
                 "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"][dt.month-1]
        return f"{hari}, {dt.day:02d} - {dt.month:02d} - {dt.year}"
    except:
        return str(tgl_input).upper()

# --- FUNGSI CETAK PDF (FULL & OVERPRINT) ---
def buat_pdf_full(data, berkas_list):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 11 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    x_pos, y_pos = 1 * cm, 1 * cm
    lebar_kertas = 22 * cm
    # HALAMAN 1 (DEPAN)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    c.setFont("Helvetica-Bold", 14); c.drawCentredString(lebar_kertas/2, y_pos + 8.1 * cm, "TANDA TERIMA BERKAS PERMOHONAN PERPANJANGAN IZIN TOKO")
    c.setLineWidth(1); c.line(x_pos + 0.4*cm, y_pos + 7.85*cm, x_pos + 19.6*cm, y_pos + 7.85*cm)
    c.line(x_pos + 0.4*cm, y_pos + 7.75*cm, x_pos + 19.6*cm, y_pos + 7.75*cm)
    c.setFont("Helvetica-Bold", 11); c.drawString(x_pos + 0.8 * cm, y_pos + 7.1 * cm, "DAFTAR KELENGKAPAN DOKUMEN PERMOHONAN:")
    yy = y_pos + 6.3 * cm
    items = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(items, 1):
        c.setFont("Helvetica-BoldOblique", 10.5); c.drawString(x_pos + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 11); x_status = x_pos + 15.2 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        c.setLineWidth(1.5)
        if item in berkas_list: c.line(x_status + 1.5 * cm, yy + 0.12 * cm, x_status + 3.8 * cm, yy + 0.12 * cm)
        else: c.line(x_status - 0.1 * cm, yy + 0.12 * cm, x_status + 0.9 * cm, yy + 0.12 * cm)
        yy -= 0.65 * cm
    c.setLineWidth(1.5); c.line(x_pos + 0.15*cm, y_pos + 2.8 * cm, x_pos + 19.85*cm, y_pos + 2.8 * cm)
    c.line(lebar_kertas/2, y_pos + 0.15*cm, lebar_kertas/2, y_pos + 2.8 * cm)
    c.setFont("Helvetica-Bold", 10); c.drawCentredString(x_pos + 5 * cm, y_pos + 2.3 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 2.3 * cm, "PETUGAS PENERIMA BERKAS")
    c.setFont("Helvetica-Bold", 12); c.drawCentredString(x_pos + 5 * cm, y_pos + 0.5 * cm, f"( {data['Nama_Pengantar_Berkas']} )")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 0.5 * cm, f"( {data['Penerima_Berkas']} )")
    c.showPage()
    # HALAMAN 2 (BELAKANG)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    y_tab = y_pos + 8.85 * cm; tinggi_baris = 1.15 * cm
    tgl_ambil_pdf = "" if data['Tanggal_Pengambilan'] in ["-", "nan", "NAN"] else data['Tanggal_Pengambilan']
    rows = [("NO. URUT PENDAFTARAN", data['No']), ("TANGGAL TERIMA BERKAS", data['Tanggal_Pengantaran']),
            ("TANGGAL PENGAMBILAN", tgl_ambil_pdf), ("NAMA & NOMOR TOKO / LAPAK", f"{data['Nama_Toko']} - {data['No_Toko']}"),
            ("NAMA PEMILIK (SESUAI SK)", data['Nama_Pemilik_Asli']), ("NAMA PENGANTAR BERKAS", data['Nama_Pengantar_Berkas'])]
    for label, val in rows:
        c.rect(x_pos + 0.15*cm, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris); c.rect(lebar_kertas/2, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.setFont("Helvetica-Bold", 10); c.drawString(x_pos + 0.6 * cm, y_tab - 0.75 * cm, label)
        c.setFont("Helvetica-Bold", 11); c.drawString(lebar_kertas/2 + 0.6 * cm, y_tab - 0.75 * cm, str(val).upper())
        y_tab -= tinggi_baris
    c.save(); buffer.seek(0)
    return buffer

def cetak_overprint(tgl_ambil):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 11 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    y_pos_tgl = 1 * cm + 8.85 * cm - (1.15 * cm * 3) + 0.4 * cm
    c.setFont("Helvetica-Bold", 12); c.drawString(11 * cm + 0.6 * cm, y_pos_tgl, tgl_ambil.upper())
    c.save(); buffer.seek(0)
    return buffer

# --- INTERFACE UTAMA ---
st.sidebar.title("SURAT KEPUTUSAN MENEMPATI TOKO")
menu = st.sidebar.radio("KEPERLUAN:", ["PENGANTARAN BERKAS", "PENGAMBILAN BERKAS"])

# AMBIL DATA (TTL 60 detik agar stabil)
@st.cache_data(ttl=60)
def ambil_data():
    try:
        raw = conn.read(ttl=60)
        bersih = raw.astype(str).replace("nan", "-")
        if not bersih.empty:
            bersih['No'] = bersih['No'].str.replace(r'\.0$', '', regex=True).str.strip()
        return bersih
    except: return pd.DataFrame()

df = ambil_data()

# --- BAGIAN 1: PENGANTARAN BERKAS ---
if menu == "PENGANTARAN BERKAS":
    st.header("📝 FORM PENGANTARAN BERKAS BARU")
    
    # Hitung No Urut Terakhir
    try:
        nums = pd.to_numeric(df['No'], errors='coerce').dropna()
        last_no = 0 if nums.empty else int(nums.max())
    except: last_no = 0
    
    # Reset form jika diinginkan
    if st.button("🔄 BERSIHKAN FORM / INPUT BARU"):
        st.rerun()

    # Layout Input
    no_urut = st.text_input("NO. URUT PENDAFTARAN", value=str(last_no + 1)).strip()
    
    # Cek Duplikat
    is_duplicate = False
    if not df.empty and no_urut in df['No'].values:
        is_duplicate = True
        st.warning(f"⚠️ NOMOR {no_urut} SUDAH TERPAKAI! DATA LAMA AKAN TERTIMPA.")

    col1, col2 = st.columns(2)
    with col1:
        tgl_skrg = datetime.now().strftime("%d/%m/%Y")
        raw_tgl_t = st.text_input("TANGGAL PENGANTARAN (DD/MM/YYYY)", value=tgl_skrg)
        tgl_t = format_tgl_indo(raw_tgl_t)
        st.caption(f"FORMAT: {tgl_t}")
        
        nama_toko = st.text_input("NAMA TOKO").upper()
        no_toko = st.text_input("NOMOR TOKO").upper()
    with col2:
        sk = st.text_input("NAMA PEMILIK (SESUAI SK)").upper()
        pengantar = st.text_input("NAMA PENGANTAR BERKAS").upper()
        penerima = st.text_input("PETUGAS PENERIMA BERKAS").upper()
    
    st.write("---")
    st.write("📋 **CEKLIS KELENGKAPAN BERKAS:**")
    t_list = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN (APABILA BERKAS SK HILANG)"]
    cols_cek = st.columns(3)
    sel_berkas = []
    for i, t in enumerate(t_list):
        if cols_cek[i % 3].checkbox(t):
            sel_berkas.append(t)

    if st.button("💾 SIMPAN & CETAK TANDA TERIMA"):
        if not nama_toko or not sk:
            st.error("❌ NAMA TOKO DAN PEMILIK TIDAK BOLEH KOSONG!")
        else:
            new_row = {"No": no_urut, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", 
                       "Nama_Toko": nama_toko, "No_Toko": no_toko, "Nama_Pemilik_Asli": sk, 
                       "Nama_Pengantar_Berkas": pengantar, "Penerima_Berkas": penerima}
            
            if is_duplicate: df = df[df['No'] != no_urut]
            df_final = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            conn.update(data=df_final)
            st.cache_data.clear()
            st.success("✅ DATA BERHASIL DISIMPAN!")
            st.download_button("📥 DOWNLOAD PDF TANDA TERIMA", buat_pdf_full(new_row, sel_berkas), f"TANDA_{Nama_Pengantar_Berkas}.pdf")

# --- BAGIAN 2: PENGAMBILAN BERKAS ---
elif menu == "PENGAMBILAN BERKAS":
    st.header("PENCARIAN & PENGAMBILAN BERKAS")
    
    no_cari = st.text_input("🔍 MASUKKAN NOMOR URUT PENDAFTARAN").strip()
    
    if no_cari:
        hasil = df[df['No'] == no_cari]
        if not hasil.empty:
            data_lama = hasil.iloc[0]
            
            # TAMPILAN DATA YANG DITEMUKAN (BEDA DENGAN FORM INPUT)
            st.success(f"✅ DATA DITEMUKAN UNTUK NOMOR: {no_cari}")
            
            with st.container(border=True):
                c1, c2 = st.columns(2)
                c1.write(f"**NAMA TOKO:** {data_lama['Nama_Toko']}")
                c1.write(f"**NOMOR TOKO:** {data_lama['No_Toko']}")
                c2.write(f"**PEMILIK:** {data_lama['Nama_Pemilik_Asli']}")
                c2.write(f"**TGL PENGANTARAN:** {data_lama['Tanggal_Pengantaran']}")
            
            st.write("---")
            # Hanya input tanggal pengambilan yang muncul
            tgl_skrg_a = datetime.now().strftime("%d/%m/%Y")
            raw_tgl_a = st.text_input("📝 INPUT TANGGAL PENGAMBILAN", value=tgl_skrg_a)
            tgl_ambil = format_tgl_indo(raw_tgl_a)
            st.caption(f"FORMAT: {tgl_ambil}")
            
            if st.button("✅ UPDATE TANGGAL & CETAK OVERPRINT"):
                df.loc[df['No'] == no_cari, 'Tanggal_Pengambilan'] = tgl_ambil
                conn.update(data=df)
                st.cache_data.clear()
                st.success("✅ BERHASIL! SILAKAN CETAK DI HALAMAN BELAKANG KERTAS.")
                st.download_button("📥 DOWNLOAD PDF OVERPRINT (1 HALAMAN)", cetak_overprint(tgl_ambil), f"UPDATE_{no_cari}.pdf")
        else:
            st.error(f"❌ NOMOR URUT '{no_cari}' TIDAK DITEMUKAN DI DATABASE.")
