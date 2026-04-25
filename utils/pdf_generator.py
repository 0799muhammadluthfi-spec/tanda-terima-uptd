import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth

from utils.helpers import format_tgl_hari_indo, safe_int


def buat_pdf_full(data: dict, berkas_list: list) -> BytesIO:
    buffer = BytesIO()
    UKURAN_KERTAS = (21.5 * cm, 33 * cm)
    c = canvas.Canvas(buffer, pagesize=UKURAN_KERTAS)

    M = 0.75 * cm
    TINGGI_POTONG = 12 * cm
    Y_POTONG = 33 * cm - TINGGI_POTONG
    Y_BASE = Y_POTONG + M
    X_POS = M
    LEBAR_BOX = 21.5 * cm - (2 * M)
    TINGGI_BOX = TINGGI_POTONG - (2 * M)
    TENGAH = 21.5 * cm / 2

    def gambar_garis_potong():
        c.setLineWidth(1)
        c.setDash(4, 4)
        c.line(0, Y_POTONG, 21.5 * cm, Y_POTONG)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(0.5 * cm, Y_POTONG + 0.15 * cm, "--- Batas potong (Tinggi 12 cm) ---")
        c.setDash()

    def gambar_kotak_no_urut(no_urut_val):
        kotak_luar = 6 * cm
        kotak_dalam = 5 * cm
        x_kanan = 21.5 * cm - M - kotak_luar
        y_bawah = Y_POTONG - kotak_luar - 0.3 * cm

        c.setLineWidth(1)
        c.setDash(3, 3)
        c.rect(x_kanan, y_bawah, kotak_luar, kotak_luar)
        c.setDash()

        offset = (kotak_luar - kotak_dalam) / 2
        x_dalam = x_kanan + offset
        y_dalam = y_bawah + offset

        c.setLineWidth(1.5)
        c.rect(x_dalam, y_dalam, kotak_dalam, kotak_dalam)

        center_x = x_dalam + kotak_dalam / 2

        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(center_x, y_dalam + kotak_dalam - 1.5 * cm, "NO URUT")

        c.setFont("Helvetica-Bold", 40)
        c.drawCentredString(center_x, y_dalam + 1.2 * cm, str(no_urut_val).upper())

    # ==========================================
    # HALAMAN 1
    # ==========================================
    gambar_garis_potong()
    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX)
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm)

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(TENGAH, Y_BASE + 9.3 * cm, "TANDA TERIMA BERKAS PERPANJANGAN IZIN TOKO")
    c.setLineWidth(2)
    c.line(TENGAH - 5.5 * cm, Y_BASE + 9.0 * cm, TENGAH + 5.5 * cm, Y_BASE + 9.0 * cm)

    yy = Y_BASE + 8.0 * cm
    SEMUA_BERKAS = [
        "SK ASLI MENEMPATI",
        "PAS FOTO 3X4 (2 LBR)",
        "MATERAI 10.000 (2 LBR)",
        "FC KTP PEMILIK",
        "FC KARTU SEWA",
        "SURAT KUASA",
        "SURAT KEHILANGAN"
    ]

    for i, item in enumerate(SEMUA_BERKAS, 1):
        c.setFont("Helvetica-BoldOblique", 10)
        c.drawString(X_POS + 1 * cm, yy, f"{i}. {item}")
        c.setFont("Helvetica-Bold", 10)
        x_status = X_POS + 14 * cm
        c.drawString(x_status, yy, "ADA   /   TIDAK ADA")
        c.setLineWidth(1.5)
        y_strike = yy + 0.11 * cm
        if item in berkas_list:
            c.line(x_status + 1.4 * cm, y_strike, x_status + 3.5 * cm, y_strike)
        else:
            c.line(x_status - 0.1 * cm, y_strike, x_status + 0.8 * cm, y_strike)
        yy -= 0.7 * cm

    c.setLineWidth(1.5)
    c.line(X_POS + 0.15 * cm, Y_BASE + 3.0 * cm, X_POS + LEBAR_BOX - 0.15 * cm, Y_BASE + 3.0 * cm)
    c.line(TENGAH, Y_BASE + 0.15 * cm, TENGAH, Y_BASE + 3.0 * cm)

    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(X_POS + 5 * cm, Y_BASE + 2.5 * cm, "PENGANTAR BERKAS")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 2.5 * cm, "PETUGAS PENERIMA")

    nama_pengantar = str(data.get('Nama_Pengantar_Berkas', '')).upper()
    no_hp = str(data.get('No_HP_Pengantar', '')).strip()

    # Halaman depan: nama saja tanpa no HP
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(X_POS + 5 * cm, Y_BASE + 0.6 * cm, f"( {nama_pengantar} )")
    c.drawCentredString(X_POS + 15 * cm, Y_BASE + 0.6 * cm,
                        f"( {str(data.get('Penerima_Berkas', '')).upper()} )")

    gambar_kotak_no_urut(data.get("No", "-"))

    c.showPage()

    # ==========================================
    # HALAMAN 2
    # ==========================================
    gambar_garis_potong()

    c.saveState()
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.setFont("Helvetica-Bold", 35)
    c.translate(TENGAH, Y_BASE + (TINGGI_BOX / 2))
    c.rotate(25)
    c.drawCentredString(0, 0, "UPTD PASAR KANDANGAN")
    c.restoreState()

    c.setLineWidth(1.5)
    c.rect(X_POS, Y_BASE, LEBAR_BOX, TINGGI_BOX)
    c.rect(X_POS + 0.15 * cm, Y_BASE + 0.15 * cm, LEBAR_BOX - 0.3 * cm, TINGGI_BOX - 0.3 * cm)

    def wrap_text(text, max_width, font_name="Helvetica-Bold", font_size=10, max_lines=2):
        text = str(text).upper().strip()
        if not text or text in ["-", "NONE", "NAN"]:
            return ["-"]
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test_line = word if current == "" else current + " " + word
            if stringWidth(test_line, font_name, font_size) <= max_width:
                current = test_line
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            while len(lines[-1]) > 0 and stringWidth(lines[-1] + "...", font_name, font_size) > max_width:
                lines[-1] = lines[-1][:-1]
            lines[-1] += "..."
        return lines

    y_tab = Y_BASE + 10.35 * cm
    TINGGI_B = 0.95 * cm
    FONT_SIZE = 10
    lebar_label = 6.5 * cm
    lebar_value = 13.2 * cm
    max_val_width = 12.2 * cm

    pengantar_display = nama_pengantar
    if no_hp and no_hp != "-":
        pengantar_display = f"{nama_pengantar} / {no_hp}"

    DETAIL_ROWS = [
        ("NOMOR URUT", data.get("No", "-")),
        ("TANGGAL TERIMA", format_tgl_hari_indo(data.get("Tanggal_Pengantaran", "-"))),
        ("TANGGAL PENGAMBILAN", format_tgl_hari_indo(data.get("Tanggal_Pengambilan", "-"))),
        ("NAMA & NOMOR TOKO", f"{data.get('Nama_Toko', '-')} - {data.get('No_Toko', '-')}"),
        ("NAMA PEMILIK (SK)", data.get("Nama_Pemilik_Asli", "-")),
        ("NIK PEMILIK ASLI", data.get("No_NIK", "-")),
        ("ALAMAT PEMILIK ASLI", data.get("Alamat", "-")),
        ("NAMA PENGANTAR", pengantar_display)
    ]

    for label, val in DETAIL_ROWS:
        if label == "ALAMAT PEMILIK ASLI":
            value_lines = wrap_text(val, max_val_width, "Helvetica-Bold", FONT_SIZE, 2)
            row_height = 1.15 * cm if len(value_lines) > 1 else TINGGI_B
        else:
            value_lines = [str(val).upper()]
            row_height = TINGGI_B

        c.setLineWidth(1.5)
        c.rect(X_POS + 0.15 * cm, y_tab - row_height, lebar_label, row_height)
        c.rect(X_POS + 6.65 * cm, y_tab - row_height, lebar_value, row_height)

        c.setFont("Helvetica-Bold", FONT_SIZE)
        c.drawString(X_POS + 0.4 * cm, y_tab - 0.60 * cm, label)

        c.setFont("Helvetica-Bold", FONT_SIZE)
        x_value = X_POS + 7.0 * cm

        if len(value_lines) == 1:
            # 1 baris → center vertikal
            val_y = y_tab - (row_height / 2) - 0.12 * cm
            c.drawString(x_value, val_y, value_lines[0])
        else:
            # 2 baris → dua baris rata kiri dengan titik awal sama
            line_height = 0.40 * cm
            center_of_box = y_tab - (row_height / 2)

            y_line1 = center_of_box + 0.10 * cm
            y_line2 = center_of_box - 0.30 * cm

            c.drawString(x_value, y_line1, value_lines[0])
            c.drawString(x_value, y_line2, value_lines[1])

        y_tab -= row_height

    jarak_baris = 0.35 * cm
    y_notice_title = min(Y_BASE + 1.70 * cm, y_tab - 0.15 * cm)
    y_notice_1 = y_notice_title - jarak_baris
    y_notice_2 = y_notice_1 - jarak_baris
    y_notice_3 = y_notice_2 - jarak_baris
    y_notice_4 = y_notice_3 - jarak_baris

    if y_notice_4 < Y_BASE + 0.20 * cm:
        y_notice_4 = Y_BASE + 0.20 * cm
        y_notice_3 = y_notice_4 + jarak_baris
        y_notice_2 = y_notice_3 + jarak_baris
        y_notice_1 = y_notice_2 + jarak_baris
        y_notice_title = y_notice_1 + jarak_baris

    c.setFont("Helvetica-Bold", FONT_SIZE)
    c.drawString(X_POS + 0.6 * cm, y_notice_title, "PERHATIAN:")
    c.setFont("Helvetica", 9)
    c.drawString(X_POS + 0.6 * cm, y_notice_1, "1. Mohon simpan dan bawa tanda terima ini sebagai syarat pengambilan SK Toko Anda.")
    c.drawString(X_POS + 0.6 * cm, y_notice_2, "2. Pelayanan pengambilan SK dapat dilakukan pada saat jam kerja operasional UPTD.")
    c.drawString(X_POS + 0.6 * cm, y_notice_3, "3. Jika tanda terima hilang, harap melampirkan fotokopi KTP Pemilik SK dan Pengantar.")
    c.drawString(X_POS + 0.6 * cm, y_notice_4, "4. UPTD tidak bertanggung jawab atas berkas yang tidak diambil 30 hari setelah SK selesai.")

    c.save()
    buffer.seek(0)
    return buffer


def cetak_tanda_terima_parkir(data) -> BytesIO:
    if isinstance(data, pd.Series):
        data = data.to_dict()
    buffer = BytesIO()
    lebar_kertas = 21.5 * cm
    c = canvas.Canvas(buffer, pagesize=(lebar_kertas, 33 * cm))
    lebar_box, tinggi_box = 6.8 * cm, 4.6 * cm
    x_awal = (lebar_kertas - lebar_box) / 2
    center_x = lebar_kertas / 2
    y_top = 32 * cm
    y_bottom = y_top - tinggi_box
    c.setLineWidth(1.2)
    c.rect(x_awal, y_bottom, lebar_box, tinggi_box)
    y_gp = y_bottom - 1.0 * cm
    c.setDash(1, 3)
    c.setLineWidth(0.5)
    c.line(0, y_gp, lebar_kertas, y_gp)
    c.setDash()
    tgl_dis = format_tgl_hari_indo(data.get('Tanggal', '-'))
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(center_x, y_top - 0.5 * cm, "UPTD PENGELOLAAN PASAR KANDANGAN")
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(center_x, y_top - 0.9 * cm, "TANDA TERIMA KARCIS PARKIR (MPP)")
    c.line(x_awal + 0.3 * cm, y_top - 1.1 * cm, x_awal + lebar_box - 0.3 * cm, y_top - 1.1 * cm)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_awal + 0.3 * cm, y_top - 1.5 * cm, f"TGL : {tgl_dis}")
    c.drawString(x_awal + 0.3 * cm, y_top - 1.9 * cm, f"NAMA : {str(data.get('Nama_Petugas', '-')).upper()}")
    y_tab, t_row = y_top - 2.2 * cm, 0.6 * cm
    x_tab, l_tab = x_awal + 0.3 * cm, lebar_box - 0.6 * cm
    for i, (jns, jml) in enumerate([
        ("RODA 2", safe_int(data.get('MPP_Roda_R2', 0))),
        ("RODA 4", safe_int(data.get('MPP_Roda_R4', 0)))
    ]):
        y_r = y_tab - ((i + 1) * t_row)
        c.rect(x_tab, y_r, l_tab, t_row)
        c.setFont("Helvetica", 6)
        c.drawString(x_tab + 0.1 * cm, y_r + 0.2 * cm, jns)
        c.drawCentredString(center_x, y_r + 0.2 * cm, f"{jml} LBR")
        c.drawRightString(x_tab + l_tab - 0.1 * cm, y_r + 0.2 * cm, "MPP")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def cetak_overprint(tgl_ambil: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(21.5 * cm, 33 * cm))
    c.setFont("Helvetica-Bold", 10)
    X_POS = 0.75 * cm
    y_target = 21.5 * cm + 0.75 * cm + 10.35 * cm - (1.05 * cm * 2) - 0.7 * cm
    c.drawString(X_POS + 7.0 * cm, y_target, format_tgl_hari_indo(tgl_ambil).upper())
    c.save()
    buffer.seek(0)
    return buffer
