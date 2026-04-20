import streamlit as st
import pandas as pd
from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. FUNGSI PENUNJANG (LOGIKA & PDF)
# ==========================================

def format_tgl_indo(tgl_str):
    try:
        tgl_input = str(tgl_str).replace('/', '-')
        if len(tgl_input.split('-')[-1]) == 2:
            tgl_obj = datetime.strptime(tgl_input, "%d-%m-%y")
        else:
            tgl_obj = datetime.strptime(tgl_input, "%d-%m-%Y")
        hari_indo = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
        return f"{hari_indo[tgl_obj.weekday()]}, {tgl_obj.strftime('%d - %m - %Y')}"
    except:
        return str(tgl_str).upper()

def cetak_tanda_terima_parkir(data):
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    
    lebar_box, tinggi_box = 6.8 * cm, 4.6 * cm
    x_awal = (lebar_kertas - lebar_box) / 2
    center_x = lebar_kertas / 2
    y_top = 32 * cm 
    y_bottom = y_top - tinggi_box
    
    # Bingkai & Garis Potong
    c.setLineWidth(1.2); c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    y_gp = y_bottom - 1.0 * cm
    c.setDash(1, 3); c.setLineWidth(0.5); c.line(0, y_gp, lebar_kertas, y_gp); c.setDash() 
    
    # Header & Data
    tgl_display = format_tgl_indo(data['Tanggal'])
    c.setFont("Helvetica-Bold", 7); c.drawCentredString(center_x, y_top - 0.5*cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6); c.drawCentredString(center_x, y_top - 0.9*cm, "TANDA TERIMA SETORAN PARKIR (MPP)")
    c.line(x_awal + 0.3*cm, y_top - 1.1*cm, x_awal + lebar_box - 0.3*cm, y_top - 1.1*cm)
    
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_awal + 0.3*cm, y_top - 1.5*cm, f"TGL : {tgl_display}")
    c.drawString(x_awal + 0.3*cm, y_top - 1.9*cm, f"NAMA : {str(data['Nama_Petugas']).upper()}")

    # Tabel Mini
    y_tab, t_row = y_top - 2.2*cm, 0.6*cm
    x_tab, l_tab = x_awal + 0.3*cm, lebar_box - 0.6*cm
    
    items = [("RODA 2", data.get('MPP_Roda_R2', 0)), ("RODA 4", data.get('MPP_Roda_R4', 0))]
    for i, (jns, jml) in enumerate(items):
        y_r = y_tab - ((i+1) * t_row)
        c.rect(x_tab, y_r, l_tab, t_row)
        c.setFont("Helvetica", 6); c.drawString(x_tab + 0.1*cm, y_r + 0.2*cm, jns)
        c.drawCentredString(center_x, y_r + 0.2*cm, f"{jml} LBR")
        c.drawRightString(x_tab + l_tab - 0.1*cm, y_r + 0.2*cm, "MPP")
    
    c.showPage(); c.save(); buffer.seek(0)
    return buffer

# ==========================================
# 2. DATABASE UTAMA
# ==========================================

def load_data(sheet_name):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=sheet_name, ttl="0")

def safe_update(sheet_name, df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet=sheet_name, data=df)
    return True

def halaman_parkir(menu_aktif):
    # TAMPILAN LOGO HSS
    path_logo = "logo_hss.png" 
    if os.path.exists(path_logo):
        st.image(path_logo, width=80)
    
    st.header(f"🚗 {menu_aktif}")
    df_parkir = load_data("DATA_PARKIR")

    if menu_aktif == "INPUT REKAP":
        st.subheader("📝 FORM REKAP SETORAN")
        tgl_input = st.text_input("MASUKKAN TANGGAL", value=datetime.now().strftime("%d-%m-%Y"))
        
        # Logika Mencari Baris Jadwal
        baris_cocok = df_parkir[df_parkir["Tanggal"].astype(str) == tgl_input]
        
        if not baris_cocok.empty:
            idx = baris_cocok.index[0]
            nama_ptgs = baris_cocok.iloc[0]["Nama_Petugas"]
            st.success(f"👤 PETUGAS: **{nama_ptgs}** | 📅 **{format_tgl_indo(tgl_input)}**")
            
            # AMBIL SISA KEMARIN (idx - 1)
            sisa_r2_lama = df_parkir.iloc[idx - 1]["Sisa_Stok_R2"] if idx > 0 else 0
            sisa_r4_lama = df_parkir.iloc[idx - 1]["Sisa_Stok_R4"] if idx > 0 else 0
            st.info(f"📊 SISA KEMARIN: R2={sisa_r2_lama} | R4={sisa_r4_lama}")

            with st.form("form_parkir", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    pk_r2 = st.number_input("PENGAMBILAN BARU R2", min_value=0)
                    tot_r2 = st.number_input("TERJUAL R2 (REKAP)", min_value=0)
                    mpp_r2 = st.number_input("MPP RODA R2", min_value=0)
                with c2:
                    pk_r4 = st.number_input("PENGAMBILAN BARU R4", min_value=0)
                    tot_r4 = st.number_input("TERJUAL R4 (REKAP)", min_value=0)
                    mpp_r4 = st.number_input("MPP RODA R4", min_value=0)

                if st.form_submit_button("💾 UPDATE DATA", type="primary"):
                    # RUMUS: (Baru + Sisa Lama) - Terjual
                    sisa_n_r2 = (pk_r2 + sisa_r2_lama) - tot_r2
                    sisa_n_r4 = (pk_r4 + sisa_r4_lama) - tot_r4
                    
                    df_parkir.loc[idx, ["Pengambilan_Karcis_R2", "Total_Karcis_R2", "MPP_Roda_R2", "Sisa_Stok_R2", "Khusus_Roda_R2"]] = [pk_r2, tot_r2, mpp_r2, sisa_n_r2, tot_r2-mpp_r2]
                    df_parkir.loc[idx, ["Pengambilan_Karcis_R4", "Total_Karcis_R4", "MPP_Roda_R4", "Sisa_Stok_R4", "Khusus_Roda_R4"]] = [pk_r4, tot_r4, mpp_r4, sisa_n_r4, tot_r4-mpp_r4]
                    df_parkir.loc[idx, ["Status_Khusus", "Status_MPP"]] = ["BELUM", "BELUM"]
                    
                    if safe_update("DATA_PARKIR", df_parkir):
                        st.success("✅ BERHASIL DIUPDATE!"); st.rerun()
        else:
            st.warning("⚠️ TANGGAL TIDAK DITEMUKAN DI JADWAL SPREADSHEET.")

    elif menu_aktif == "KONFIRMASI":
        # Filter data yang belum lunas konfirmasinya
        df_pend = df_parkir[(df_parkir["Status_Khusus"] == "BELUM") | (df_parkir["Status_MPP"] == "BELUM")].copy()
        # Buang baris yang datanya masih kosong (belum diisi rekap)
        df_pend = df_pend[df_pend["Total_Karcis_R2"].notnull()]

        if df_pend.empty: 
            st.info("TIDAK ADA DATA YANG MENUNGGU KONFIRMASI.")
        else:
            for i, row in df_pend.iterrows():
                # Gunakan index i sebagai key agar tidak duplicate
                with st.expander(f"📦 {row['Tanggal']} - {row['Nama_Petugas']}"):
                    ck, cm = st.columns(2)
                    with ck:
                        st.write(f"**KHUSUS**\nR2: {row['Khusus_Roda_R2']}\nR4: {row['Khusus_Roda_R4']}")
                        if st.button(f"TERIMA KHUSUS", key=f"k_{i}", use_container_width=True):
                            df_parkir.loc[i, "Status_Khusus"] = "SUDAH"
                            if safe_update("DATA_PARKIR", df_parkir): st.rerun()
                    
                    with cm:
                        st.write(f"**MPP**\nR2: {row['MPP_Roda_R2']}\nR4: {row['MPP_Roda_R4']}")
                        if row["Status_MPP"] == "BELUM":
                            if st.button(f"TERIMA MPP", key=f"m_{i}", type="primary", use_container_width=True):
                                df_parkir.loc[i, "Status_MPP"] = "SUDAH"
                                if safe_update("DATA_PARKIR", df_parkir): st.rerun()
                        else:
                            st.download_button("🖨️ CETAK MPP", data=cetak_tanda_terima_parkir(row), file_name=f"MPP_{row['Tanggal']}.pdf", key=f"p_{i}", use_container_width=True)

    st.divider()
    st.subheader("📊 LOG REKAP TERAKHIR")
    st.dataframe(df_parkir.sort_values(by="Tanggal", ascending=False).head(10), hide_index=True)

# ==========================================
# 3. MAIN RUNNER
# ==========================================
def main():
    st.sidebar.title("🅿️ PARKIR UPTD")
    menu = st.sidebar.radio("MENU UTAMA", ["INPUT REKAP", "KONFIRMASI"])
    halaman_parkir(menu)

if __name__ == "__main__":
    main()
