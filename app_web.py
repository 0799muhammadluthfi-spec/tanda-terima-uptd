import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UPTD Pasar Kandangan", layout="wide")

# --- KONEKSI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI KAMUS TANGGAL INDONESIA ---
def format_tgl_indo(tgl_input):
    if not tgl_input or tgl_input == "-": return ""
    try:
        dt = pd.to_datetime(tgl_input, dayfirst=True)
        hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][dt.weekday()]
        return f"{hari.upper()}, {dt.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_input).upper()

# --- FUNGSI CETAK PDF LENGKAP (2 HALAMAN) ---
def buat_pdf_full(data):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 11 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    x_pos, y_pos = 1 * cm, 1 * cm
    lebar_kertas = 22 * cm
    
    # HALAMAN 1: DEPAN
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    c.setFont("Helvetica-Bold", 14); c.drawCentredString(lebar_kertas/2, y_pos + 8.1 * cm, "TANDA TERIMA BERKAS PERMOHONAN PERPANJANGAN IZIN TOKO")
    c.setLineWidth(1); c.line(x_pos + 0.4*cm, y_pos + 7.85*cm, x_pos + 19.6*cm, y_pos + 7.85*cm)
    c.line(x_pos + 0.4*cm, y_pos + 7.75*cm, x_pos + 19.6*cm, y_pos + 7.75*cm)
    c.setFont("Helvetica-Bold", 11); c.drawString(x_pos + 0.8 * cm, y_pos + 7.1 * cm, "Daftar kelengkapan dokumen permohonan:")
    yy = y_pos + 6.3 * cm
    items = ["SK Asli Menempati", "Pas Foto 3x4 (2 lbr)", "FC KTP Pemilik", "FC Kartu Sewa", "Surat Kuasa", "Surat Kehilangan"]
    berkas_list = str(data['Keterangan']).split(", ")
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
    
    # HALAMAN 2: BELAKANG
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 9*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 8.7*cm)
    y_tab = y_pos + 8.85 * cm; tinggi_baris = 1.15 * cm
    tgl_ambil_pdf = "" if data['Tanggal_Pengambilan'] == "-" else data['Tanggal_Pengambilan']
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

# --- PERBAIKAN: FUNGSI OVERPRINT HANYA 1 HALAMAN ---
def cetak_overprint(tgl_ambil):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 11 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    # Halaman 1 langsung berisi tanggal (Tidak ada c.showPage() di awal)
    # Posisinya tetap di baris ke-3 sesuai layout tabel belakang
    y_pos_tgl = 1 * cm + 8.85 * cm - (1.15 * cm * 3) + 0.4 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(11 * cm + 0.6 * cm, y_pos_tgl, tgl_ambil.upper())
    c.save(); buffer.seek(0)
    return buffer

# --- INTERFACE UTAMA ---
st.sidebar.title("SURAT KEPUTUSAN MENEMPATI TOKO")
menu = st.sidebar.radio("KEPERLUAN:", ["PENGANTARAN BERKAS", "PENGAMBILAN BERKAS"])

# Ambil data LIVE (Tanpa Cache)
df = conn.read(ttl=0)
if not df.empty:
    df['No'] = df['No'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

if 'tgl_p_input' not in st.session_state: st.session_state.tgl_p_input = datetime.now().strftime("%d/%m/%Y")
if 'tgl_a_input' not in st.session_state: st.session_state.tgl_a_input = datetime.now().strftime("%d/%m/%Y")

if menu == "PENGANTARAN BERKAS":
    st.header("📝 Pengantaran Berkas Baru")
    try:
        last_no = 0 if df.empty else pd.to_numeric(df['No'], errors='coerce').max()
        if pd.isna(last_no): last_no = 0
    except: last_no = 0
    
    no_urut = st.text_input("No. Urut Pendaftaran", value=str(int(last_no) + 1))
    
    col1, col2 = st.columns(2)
    with col1:
        raw_tgl_t = st.text_input("TANGGAL PENGANTARAN", value=st.session_state.tgl_p_input)
        tgl_t = format_tgl_indo(raw_tgl_t)
        if tgl_t != raw_tgl_t:
            st.session_state.tgl_p_input = tgl_t
            st.rerun()
        nama_toko = st.text_input("NAMA TOKO").upper()
        no_toko = st.text_input("NOMOR TOKO").upper()
    with col2:
        sk = st.text_input("NAMA PEMILIK SESUAI SK").upper()
        pengantar = st.text_input("NAMA PENGANTAR BERKAS").upper()
        penerima = st.text_input("PETUGAS PENERIMA").upper()
    
    t_list = ["SK Asli Menempati", "Pas Foto 3x4 (2 lbr)", "FC KTP Pemilik", "FC Kartu Sewa", "Surat Kuasa", "Surat Kehilangan"]
    st.write("Ceklis Kelengkapan Berkas:")
    sel_berkas = [t for t in t_list if st.checkbox(t)]

    if st.button("SIMPAN & CETAK FULL"):
        ket_gabung = ", ".join(sel_berkas)
        new_row = {"No": no_urut, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", "Nama_Toko": nama_toko, 
                   "No_Toko": no_toko, "Nama_Pemilik_Asli": sk, "Nama_Pengantar_Berkas": pengantar, "Penerima_Berkas": penerima, "Keterangan": ket_gabung}
        # Tambahkan data baru ke data lama agar tidak tertimpa
        df_full = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        conn.update(data=df_full)
        st.success(f"Berhasil Tersimpan di Baris Baru!")
        st.download_button("📥 Download PDF Tanda Terima", buat_pdf_full(new_row), f"Tanda_Terima_{no_urut}.pdf", "application/pdf")

elif menu == "PENGAMBILAN BERKAS":
    st.header("🏁 Pengambilan Berkas (Overprint)")
    no_cari = st.text_input("Cari No. Urut Pendaftaran").strip()
    
    if no_cari:
        # Mencari di data live yang sudah dibersihkan
        hasil = df[df['No'] == no_cari]
        if not hasil.empty:
            data_lama = hasil.iloc[0]
            st.info(f"Ditemukan: {data_lama['Nama_Toko']} (Pemilik: {data_lama['Nama_Pemilik_Asli']})")
            
            raw_tgl_a = st.text_input("TANGGAL PENGAMBILAN", value=st.session_state.tgl_a_input)
            tgl_ambil = format_tgl_indo(raw_tgl_a)
            if tgl_ambil != raw_tgl_a:
                st.session_state.tgl_a_input = tgl_ambil
                st.rerun()
            
            if st.button("UPDATE DATA & CETAK TANGGAL"):
                df.loc[df['No'] == no_cari, 'Tanggal_Pengambilan'] = tgl_ambil
                conn.update(data=df)
                st.success("Berhasil Update! Cetak di halaman belakang kertas.")
                # PDF ini sekarang hanya 1 halaman (langsung tanggal)
                st.download_button("📥 Download PDF Overprint (1 Hal)", cetak_overprint(tgl_ambil), f"Update_Tgl_{no_cari}.pdf", "application/pdf")
        else:
            st.error(f"Nomor '{no_cari}' tidak ditemukan. Coba cek lagi di Google Sheets.")
