# Sistem Segmentasi Jenis Usaha UMKM DKI Jakarta Berbasis Wilayah Menggunakan K-Modes

Program skripsi untuk mengelompokkan (segmentasi) UMKM DKI Jakarta per wilayah administrasi menggunakan algoritma **K-Modes Clustering** pada 2 fitur kategorikal, yaitu **sektor usaha** (`sektor_makro`) dan **usia usaha** (`kelompok_tahun_berdiri`). Program ini juga mengklasifikasikan peluang tiap sektor per wilayah sebagai **Red / Neutral / Blue Ocean** berdasarkan *Location Quotient* (LQ).

Data yang dipakai adalah data terbuka UMKM DKI Jakarta periode 2024 (266.678 baris setelah dibersihkan).

## 🌐 Akses Online

Aplikasi dapat langsung dibuka tanpa instalasi di:

**https://program-segmentasi-umkm-535230017.streamlit.app/**

> Jika aplikasi lama tidak dibuka, Streamlit Community Cloud akan menidurkannya. Klik tombol **"Yes, get this app back up!"** lalu tunggu sekitar 1 menit sampai aplikasi aktif kembali.

## Fitur Aplikasi

Aplikasi (dashboard Streamlit) terdiri dari 3 tab. Wilayah dipilih lewat sidebar.

| Tab | Isi |
|---|---|
| 📍 **Analisis per Wilayah** | Ringkasan wilayah, kartu profil tiap klaster (sektor dan usia usaha dominan, label Ocean), heatmap klaster sektor × usia usaha, komposisi segmen, komoditas terbanyak per segmen, tabel daftar usaha, dan **unduh data dalam format Excel (.xlsx)** |
| 📊 **Perbandingan Sektor Lintas Wilayah** | Pilih 1 sektor, lalu lihat LQ dan label Red/Neutral/Blue Ocean-nya di 6 wilayah dalam bentuk **peta choropleth**, tabel, dan grafik batang |
| 📉 **Evaluasi Jumlah Klaster (k)** | Tabel k optimal per wilayah beserta kekuatan siku, dan kurva Elbow wilayah terpilih |

Sidebar juga menyediakan pencarian jenis usaha (misalnya "Sablon", "Ikan", "Fesyen").

## Struktur Folder

```
PROGRAM/
├── app/
│   └── app.py                      # Aplikasi Streamlit (dashboard)
├── data/
│   ├── raw/                        # Data mentah UMKM DKI Jakarta (.xls)
│   ├── processed/                  # Hasil olahan notebook (dibaca oleh app.py)
│   │   ├── 01_umkm_clean.csv
│   │   ├── 02_umkm_kmodes_clustered.csv
│   │   ├── 02b_elbow_costs.csv
│   │   ├── 02c_k_optimal.csv
│   │   ├── 03_kmodes_evaluation_summary.csv
│   │   ├── 03b_lq_sektor_wilayah.csv
│   │   └── fig_elbow_per_wilayah.png
│   └── geo/
│       ├── dki_wilayah.geojson     # Batas 6 wilayah DKI Jakarta (untuk peta)
│       └── README.md
├── notebooks/
│   ├── 01_eda_and_preprocessing.ipynb
│   ├── 02_kmodes_partitioning.ipynb
│   └── 03_interpretasi_dan_penerapan_ocean.ipynb
└── requirements.txt
```

## Menjalankan Aplikasi di Komputer Sendiri

Semua hasil olahan di `data/processed/` sudah tersedia di repository, jadi aplikasi bisa langsung dijalankan **tanpa** menjalankan notebook terlebih dahulu.

### 1. Prasyarat

- **Python 3.12** (dikembangkan dengan Python 3.12.4)
- **Git**

### 2. Unduh repository

```bash
git clone https://github.com/AdrianoDeshon1012/Program-Skripsi-Segmentasi-UMKM.git
cd Program-Skripsi-Segmentasi-UMKM
```

### 3. Buat virtual environment dan pasang dependensi

Folder `env-skripsi/` di repository adalah environment milik komputer pengembang dan tidak bisa dipakai di komputer lain. Buat environment baru:

**Windows (PowerShell / Command Prompt):**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Jalankan aplikasi

Jalankan dari **folder utama repository** (bukan dari dalam folder `app/`):

```bash
streamlit run app/app.py
```

Browser akan terbuka otomatis di **http://localhost:8501**. Jika tidak, buka alamat itu secara manual. Untuk menghentikan aplikasi, tekan `Ctrl + C` di terminal.

## Menjalankan Ulang Pengolahan Data (Opsional)

Langkah ini hanya diperlukan jika ingin menghasilkan ulang isi `data/processed/` dari data mentah. Jalankan notebook **berurutan**, karena setiap notebook memakai hasil notebook sebelumnya:

| Urutan | Notebook | Hasil |
|---|---|---|
| 1 | `01_eda_and_preprocessing.ipynb` | Pembersihan data mentah dan pembentukan 2 fitur, menghasilkan `01_umkm_clean.csv` |
| 2 | `02_kmodes_partitioning.ipynb` | Kurva Elbow, penentuan k optimal per wilayah, dan model K-Modes final, menghasilkan `02_umkm_kmodes_clustered.csv`, `02b_elbow_costs.csv`, `02c_k_optimal.csv`, `fig_elbow_per_wilayah.png` |
| 3 | `03_interpretasi_dan_penerapan_ocean.ipynb` | Profil klaster, LQ, dan label Ocean, menghasilkan `03_kmodes_evaluation_summary.csv`, `03b_lq_sektor_wilayah.csv` |

Buka lewat Jupyter Lab (sudah termasuk di `requirements.txt`):

```bash
jupyter lab
```

Atau jalankan sekaligus dari terminal:

```bash
cd notebooks
jupyter nbconvert --to notebook --execute --inplace 01_eda_and_preprocessing.ipynb
jupyter nbconvert --to notebook --execute --inplace 02_kmodes_partitioning.ipynb
jupyter nbconvert --to notebook --execute --inplace 03_interpretasi_dan_penerapan_ocean.ipynb
```

Notebook 02 membutuhkan waktu sekitar 1 menit, karena K-Modes dijalankan untuk k = 2 sampai 6 di 6 wilayah.

## Ringkasan Metode

1. **Fitur:** `sektor_makro` (6 sektor) dan `kelompok_tahun_berdiri` (Kelompok A 2020–2021, Kelompok B 2022–2023, Kelompok C 2024).
2. **Clustering:** K-Modes (`init='Cao'`, `n_init=5`, `random_state=42`), dijalankan terpisah untuk tiap wilayah.
3. **Penentuan jumlah klaster (k):** dihitung per wilayah dari kurva Elbow (k = 2..6) dengan aturan *titik terjauh dari garis lurus*. Kedua sumbu dinormalisasi ke 0..1, lalu k optimal adalah titik dengan jarak terbesar ke garis yang menghubungkan titik pertama dan terakhir kurva. Hasilnya: k = 3 untuk Jakarta Pusat, Selatan, dan Timur, serta k = 4 untuk Jakarta Barat, Utara, dan Kep. Seribu.
4. **Klasifikasi Ocean (Location Quotient):** LQ = porsi sektor di suatu wilayah ÷ porsi sektor yang sama se-DKI Jakarta.
   - **Blue Ocean:** LQ < 0,8 (sektor kurang terwakili, ada ruang untuk masuk)
   - **Neutral Ocean:** 0,8 ≤ LQ ≤ 1,25
   - **Red Ocean:** LQ > 1,25 (sektor lebih padat dari rata-rata DKI, kompetitif)

## Kendala Umum

| Masalah | Solusi |
|---|---|
| Muncul pesan berkas `02_umkm_kmodes_clustered.csv` tidak ditemukan | Pastikan `streamlit run app/app.py` dijalankan dari folder utama repository, atau jalankan ulang notebook 02 dan 03 |
| Peta di tab Perbandingan Sektor tidak muncul | Pastikan berkas `data/geo/dki_wilayah.geojson` ada (lihat `data/geo/README.md`) dan paket `folium` serta `streamlit-folium` sudah terpasang |
| `ModuleNotFoundError` saat menjalankan | Pastikan virtual environment sudah aktif, lalu jalankan ulang `pip install -r requirements.txt` |
| Port 8501 sudah dipakai | Jalankan di port lain: `streamlit run app/app.py --server.port 8502` |
