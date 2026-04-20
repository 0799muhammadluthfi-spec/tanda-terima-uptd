import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI
# ==========================================
st.set_page_config(page_title="UPTD PASAR KANDANGAN", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI PDF (FIX Teks Perhatian & Koordinat)
# ==========================================
def buat_pdf_full(data, berkas_list):
    buffer = BytesIO()
    UKURAN_CUSTOM = (22 * cm, 12 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_CUSTOM)
    x_pos, y_pos = 1 * cm, 1 * cm 
    lebar_kertas = 22 * cm
    
    # HALAMAN 1 (DEPAN)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 10*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 9.7*cm)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(lebar_kertas/2, y_pos + 9.2 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    
    yy = y_pos + 7.6 * cm
    items = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
    for i, item in enumerate(items, 1):
        c.setFont("Helvetica-BoldOblique", 9); c.drawString(x_pos + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 9); x_status = x_pos + 15 * cm; c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        if item in berkas_list: 
            c.line(x_status + 1 * cm, yy + 0.1 * cm, x_status + 3.2 * cm, yy + 0.1 * cm)
        else: 
            c.line(x_status - 0.1 * cm, yy + 0.1 * cm, x_status + 0.7 * cm, yy + 0.1 * cm)
        yy -= 0.6 * cm
        
    c.line(x_pos + 0.15*cm, y_pos + 2.8 * cm, x_pos + 19.85*cm, y_pos + 2.8 * cm)
    c.line(lebar_kertas/2, y_pos + 0.15*cm, lebar_kertas/2, y_pos + 2.8 * cm)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 2.3 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 2.3 * cm, "PETUGAS PENERIMA")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_pos + 5 * cm, y_pos + 0.5 * cm, f"( {str(data['Nama_Pengantar_Berkas']).upper()} )")
    c.drawCentredString(x_pos + 15 * cm, y_pos + 0.5 * cm, f"( {str(data['Penerima_Berkas']).upper()} )")
    c.showPage()
    
    # HALAMAN 2 (BELAKANG)
    c.setLineWidth(1.5); c.rect(x_pos, y_pos, 20*cm, 10*cm)
    c.setLineWidth(1.5); c.rect(x_pos + 0.15*cm, y_pos + 0.15*cm, 19.7*cm, 9.7*cm)
    
    y_tab = y_pos + 9.85 * cm; tinggi_baris = 1.1 * cm
    rows = [("NO. URUT", data['No']), ("TGL TERIMA", data['Tanggal_Pengantaran']),
            ("TGL AMBIL", data['Tanggal_Pengambilan']), ("TOKO", f"{data['Nama_Toko']} - {data['No_Toko']}"),
            ("PEMILIK", data['Nama_Pemilik_Asli']), ("PENGANTAR", data['Nama_Pengantar_Berkas'])]
    
    for label, val in rows:
        c.rect(x_pos + 0.15*cm, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.rect(lebar_kertas/2, y_tab - tinggi_baris, 9.85 * cm, tinggi_baris)
        c.setFont("Helvetica-Bold", 8); c.drawString(x_pos + 0.4 * cm, y_tab - 0.7 * cm, label)
        c.setFont("Helvetica-Bold", 9); c.drawString(lebar_kertas/2 + 0.4 * cm, y_tab - 0.7 * cm, str(val).upper())
        y_tab -= tinggi_baris
    
    # BAGIAN PERHATIAN (Muncul Lagi di Bawah Tabel)
    c.setFont("Helvetica-Bold", 9); c.drawString(x_pos + 0.5 * cm, y_pos + 2.5 * cm, "PERHATIAN:")
    c.setFont("Helvetica", 8)
    c.drawString(x_pos + 0.5 * cm, y_pos + 2.0 * cm, "1. Simpan tanda terima ini untuk mengambil SK asli.")
    c.drawString(x_pos + 0.5 * cm, y_pos + 1.5 * cm, "2. Kehilangan tanda terima harap melapor ke petugas UPTD.")
    c.drawString(x_pos + 0.5 * cm, y_pos + 1.0 * cm, "3. Pengambilan tidak dapat diwakilkan tanpa surat kuasa.")

    c.save(); buffer.seek(0)
    return buffer

# ==========================================
# 3. INTERFACE (Fix Pencarian)
# ==========================================
st.sidebar.title("🗂️ DASHBOARD UPTD")
modul = st.sidebar.selectbox("PILIH:", ["SK TOKO", "PARKIR"])

if modul == "SK TOKO":
    menu = st.sidebar.radio("MENU:", ["PENGANTARAN", "PENGAMBILAN"])
    # Paksa semua data jadi teks (String) agar pencarian No Urut akurat
    df_sk = conn.read(worksheet="DATA_SK", ttl=0).astype(str).replace("nan", "-")
    
    if menu == "PENGANTARAN":
        st.header("📝 INPUT PENGANTARAN")
        # Hitung No Urut
        try:
            nums = pd.to_numeric(df_sk['No'], errors='coerce').dropna()
            next_no = int(nums.max()) + 1
        except: next_no = 1
        
        with st.form("form_sk"):
            no_urut = st.text_input("NO. URUT", value=str(next_no))
            c1, c2 = st.columns(2)
            tgl_t = c1.text_input("TANGGAL TERIMA", value=datetime.now().strftime("%d-%m-%Y"))
            nama_t = c1.text_input("NAMA TOKO").upper()
            no_t = c1.text_input("NOMOR TOKO").upper()
            pemilik = c2.text_input("PEMILIK SK").upper()
            pengantar = c2.text_input("PENGANTAR").upper()
            penerima = c2.text_input("PENERIMA").upper()
            t_list = ["SK ASLI MENEMPATI", "PAS FOTO 3X4 (2 LBR)", "FC KTP PEMILIK", "FC KARTU SEWA", "SURAT KUASA", "SURAT KEHILANGAN"]
            sel_berkas = [t for t in t_list if st.checkbox(t)]
            if st.form_submit_button("💾 SIMPAN DATA"):
                new_row = {"No": no_urut, "Tanggal_Pengantaran": tgl_t, "Tanggal_Pengambilan": "-", 
                           "Nama_Toko": nama_t, "No_Toko": no_t, "Nama_Pemilik_Asli": pemilik, 
                           "Nama_Pengantar_Berkas": pengantar, "Penerima_Berkas": penerima}
                df_f = pd.concat([df_sk, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(worksheet="DATA_SK", data=df_f)
                st.session_state['last_data'] = new_row
                st.session_state['last_berkas'] = sel_berkas
                st.success("BERHASIL!")
                st.cache_data.clear()

        if 'last_data' in st.session_state:
            st.download_button("📥 DOWNLOAD PDF", buat_pdf_full(st.session_state['last_data'], st.session_state['last_berkas']), f"TANDA_{st.session_state['last_data']['No']}.pdf")

    elif menu == "PENGAMBILAN":
        st.header("🏁 PENGAMBILAN")
        no_cari = st.text_input("CARI NOMOR URUT:").strip()
        if no_cari:
            # Pencarian lebih kuat: dicocokkan sebagai teks
            hasil = df_sk[df_sk['No'].str.strip() == no_cari]
            if not hasil.empty:
                data = hasil.iloc[0]
                st.success(f"DITEMUKAN: {data['Nama_Toko']} - {data['Nama_Pemilik_Asli']}")
                tgl_a = st.text_input("TANGGAL AMBIL", value=datetime.now().strftime("%d-%m-%Y"))
                if st.button("✅ UPDATE"):
                    df_sk.loc[df_sk['No'].str.strip() == no_cari, 'Tanggal_Pengambilan'] = tgl_a
                    conn.update(worksheet="DATA_SK", data=df_sk)
                    st.success("TANGGAL UPDATE!")
                    st.cache_data.clear()
            else: st.error("NOMOR TIDAK ADA!")
