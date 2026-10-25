# Data Geospasial: Batas Wilayah DKI Jakarta

Folder ini berisi batas 6 wilayah administrasi DKI Jakarta untuk peta choropleth di tab
"📊 Perbandingan Sektor Lintas Wilayah" pada `app/app.py`.

## Berkas yang diharapkan

- Nama berkas: `data/geo/dki_wilayah.geojson`
- Format: GeoJSON `FeatureCollection`, 6 fitur (Polygon/MultiPolygon), CRS WGS84 (EPSG:4326, lon/lat)
- Setiap fitur wajib memiliki properti `CC_2` berisi kode wilayah BPS:

| `CC_2` | Wilayah (kolom `wilayah` di dataset) |
|---|---|
| 3171 | KOTA ADM. JAKARTA SELATAN |
| 3172 | KOTA ADM. JAKARTA TIMUR |
| 3173 | KOTA ADM. JAKARTA PUSAT |
| 3174 | KOTA ADM. JAKARTA BARAT |
| 3175 | KOTA ADM. JAKARTA UTARA |
| 3101 | KAB. ADM. KEP. SERIBU |

Pencocokan wilayah dilakukan lewat kode `CC_2`, bukan nama, supaya tidak bergantung pada
penulisan nama wilayah. Jika berkas tidak ada, properti `CC_2` tidak ditemukan, atau ada
wilayah yang tidak cocok, aplikasi tetap berjalan: peta diganti pesan informasi, tabel dan
grafik batang tetap tampil.

## Sumber unduhan

Batas administrasi level kabupaten/kota (level 2) untuk Provinsi DKI Jakarta, misalnya dari:

- **BPS** (Badan Pusat Statistik), peta batas wilayah kerja statistik, kode wilayah sama dengan `CC_2`
- **Indonesia Geospasial** (indonesia-geospasial.com), shapefile/GeoJSON batas administrasi
- **GADM** (gadm.org) level 2, Indonesia; berkas GADM sudah memuat properti `CC_2`

Jika sumbernya berupa shapefile, konversi ke GeoJSON WGS84 (misalnya dengan QGIS:
*Export → Save Features As → GeoJSON, CRS EPSG:4326*), saring hanya 6 fitur DKI Jakarta,
lalu simpan sebagai `dki_wilayah.geojson` di folder ini.
