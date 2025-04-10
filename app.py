from flask import Flask, render_template, request
import csv
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def absensi():
    if request.method == 'POST':
        nama = request.form['nama']
        shift = request.form['shift']
        waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # simpan ke csv
        with open('absensi.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([nama, shift, waktu])

        return f'Terima kasih {nama}, kamu sudah absen shift {shift}!'
    
    # kalau GET, tampilin form-nya
    return render_template('form.html')

@app.route('/riwayat')
def riwayat():
    shift_filter = request.args.get('shift')
    tanggal_filter = request.args.get('tanggal')

    data_absen = []
    try:
        with open('absensi.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                nama, shift, waktu = row
                if shift_filter and shift != shift_filter:
                    continue
                if tanggal_filter and not waktu.startswith(tanggal_filter):
                    continue
                data_absen.append(row)
    except FileNotFoundError:
        data_absen = []

    return render_template('riwayat.html', data_absen=data_absen)

from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

@app.route('/export/pdf')
def export_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, y, "Riwayat Absensi")
    y -= 30

    c.setFont("Helvetica", 12)
    try:
        with open('absensi.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                c.drawString(50, y, f"{row[0]} | {row[1]} | {row[2]}")
                y -= 20
                if y < 50:  # halaman penuh
                    c.showPage()
                    y = height - 50
    except FileNotFoundError:
        c.drawString(50, y, "Data tidak ditemukan.")

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='riwayat_absensi.pdf', mimetype='application/pdf')

@app.route('/grafik')
def grafik():
    data_absen = []

    try:
        with open('absensi.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data_absen = list(reader)
    except FileNotFoundError:
        pass

    # Hitung jumlah shift
    shift_count = {'Siang': 0, 'Malam': 0}
    for row in data_absen:
        if row[1] in shift_count:
            shift_count[row[1]] += 1

    return render_template('grafik.html', shift_count=shift_count)


if __name__ == '__main__':
    app.run(debug=True)
