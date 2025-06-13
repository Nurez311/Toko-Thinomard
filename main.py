from flask import Flask, render_template, request, redirect, url_for, session
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_KEY', 'kunci-rahasia-bebas-diisi')

utang_data = []

# --- FUNGSI INI KITA ROMBAK TOTAL ---
def hitung_ringkasan():
    ringkasan_bulanan = {} 
    bulan_map = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
        7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    
    for utang in utang_data:
        nama = utang['nama']
        harga = utang['harga']
        status = utang.get('status', 'Belum Lunas') # Dapatkan status utang
        
        tanggal_obj = datetime.strptime(utang['tanggal'], '%Y-%m-%d')
        kunci_bulan = f"{bulan_map[tanggal_obj.month]} {tanggal_obj.year}"

        # Jika nama pelanggan belum ada di ringkasan, buatkan "laci" baru
        if nama not in ringkasan_bulanan:
            ringkasan_bulanan[nama] = {}
        
        # Di dalam laci pelanggan, cek apakah sudah ada "map" untuk bulan ini
        if kunci_bulan not in ringkasan_bulanan[nama]:
            # Jika belum, buat map baru dengan total awal nol
            ringkasan_bulanan[nama][kunci_bulan] = {'aktif': 0, 'lunas': 0}

        # Tambahkan harga ke kategori yang sesuai (aktif atau lunas)
        if status == 'Lunas':
            ringkasan_bulanan[nama][kunci_bulan]['lunas'] += harga
        else: # 'Belum Lunas'
            ringkasan_bulanan[nama][kunci_bulan]['aktif'] += harga
            
    return ringkasan_bulanan
# --- AKHIR DARI ROMBAKAN ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id_unik = datetime.now().timestamp()
        tanggal_dari_form = request.form['tanggal']
        nama = request.form['nama']
        barang = request.form['barang']
        harga = request.form['harga']
        utang_data.append({
            'id': id_unik, 'tanggal': tanggal_dari_form, 'nama': nama,
            'barang': barang, 'harga': int(harga), 'status': 'Belum Lunas',
            'tanggal_lunas': None
        })
        return redirect(url_for('index'))

    data_utang_terformat = []
    # Mengurutkan utang berdasarkan tanggal, yang terbaru di atas
    for utang in sorted(utang_data, key=lambda x: x['tanggal'], reverse=True):
        utang_copy = utang.copy()
        tanggal_obj = datetime.strptime(utang_copy['tanggal'], '%Y-%m-%d')
        utang_copy['tanggal_tampil'] = tanggal_obj.strftime('%d-%m-%Y')
        if utang_copy.get('tanggal_lunas'):
             utang_copy['tanggal_lunas'] = datetime.strptime(utang_copy['tanggal_lunas'], '%d-%m-%Y').strftime('%d-%m-%Y')
        data_utang_terformat.append(utang_copy)

    return render_template('index.html', daftar_utang=data_utang_terformat)

@app.route('/ringkasan')
def ringkasan_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    ringkasan_data = hitung_ringkasan()
    return render_template('ringkasan.html', ringkasan=ringkasan_data)

@app.route('/lunas/<float:id_utang>')
def lunas(id_utang):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    for utang in utang_data:
        if utang['id'] == id_utang:
            utang['status'] = 'Lunas'
            utang['tanggal_lunas'] = datetime.now().strftime('%d-%m-%Y')
            break
    return redirect(url_for('index'))

# ... sisa kode login dan logout tidak berubah ...
@app.route('/login', methods=['GET', 'POST'])
#...
@app.route('/logout')
#...