# BMKG Auto Input

Aplikasi otomatisasi input data untuk BMKGSoftV2 menggunakan Python dan PyQt6.

## Deskripsi

Aplikasi ini dirancang untuk membantu proses input (excel) data ke sistem BMKGSoft secara otomatis. Aplikasi ini menggunakan PyQt6 untuk Ui dan Playwright untuk otomatisasi browser.

## Fitur

- Ui update (bukan tk sprt prev version) dan mudah digunakan
- Otomatisasi input data ke form BMKG
- Dukungan untuk file Excel (.xls, .xlsx)
- Pemilihan waktu observasi yang fleksibel
- Manajemen browser yang persisten

## Persyaratan Sistem

- Python 3.8 atau lebih baru
- PyQt6
- Playwright
- Microsoft Excel (untuk membuka file input)

## Instalasi

1. Clone repositori ini:
```bash
git clone https://github.com/username/BMKG-AutoInput.git
cd BMKG-AutoInput
```

2. Buat dan aktifkan virtual environment (opsional tapi direkomendasikan):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependensi:
```bash
pip install -r requirements.txt
```

4. Install browser yang diperlukan untuk Playwright:
```bash
playwright install
```

## Penggunaan

1. Jalankan aplikasi:
```bash
python run.py
```

2. Klik "Buka Browser" untuk memulai browser
3. Pilih file Excel yang berisi data input
4. Pilih waktu observasi
5. Klik "Jalankan" untuk memulai proses input otomatis

## Struktur Proyek

```
BMKG-AutoInput/
├── src/
│   ├── core/           # Komponen inti aplikasi
│   ├── data/           # Data dan konfigurasi
│   ├── ui/             # Antarmuka pengguna
│   └── utils/          # Utilitas
├── legacy/             # Kode lama (untuk referensi)
├── run.py             # Entry point aplikasi
└── README.md          # Dokumentasi
```

## Kontribusi

Silakan buat pull request untuk kontribusi. Untuk perubahan besar, harap buka issue terlebih dahulu untuk mendiskusikan perubahan yang diinginkan.

## Lisensi

[MIT](https://choosealicense.com/licenses/mit/)

## Kontak

Untuk pertanyaan dan dukungan, silakan hubungi pengembang. 