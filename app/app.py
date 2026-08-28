import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Peta Segmentasi UMKM DKI Jakarta (K-Modes)",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi CSS Tampilan
st.markdown("""
    <style>
    .main-title {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 15px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DICTIONARY MAPPING NAMA SEGMEN HASIL EDA
# ==========================================
CLUSTER_NAME_MAP = {
    'KAB. ADM. KEP. SERIBU': {
        0: 'Sentra Kuliner & Pariwisata Pesisir',
        1: 'Sentra Perikanan, Kelautan & Pangan (KPKP)',
        2: 'Sentra Kuliner Olahan Khusus (Binaan KPKP)'
    },
    'KOTA ADM. JAKARTA BARAT': {
        0: 'Sentra Kuliner Pokok & Retail Harian',
        1: 'Sentra Industri Pangan Olahan Kemasan',
        2: 'Sentra Industri Kreatif & Fesyen'
    },
    'KOTA ADM. JAKARTA PUSAT': {
        0: 'Sentra Niaga Kuliner & Retail Perkotaan',
        1: 'Sentra Produk Makanan Olahan Siap Saji',
        2: 'Sentra Jasa Vokasi & Ketenagakerjaan (Nakertrans)'
    },
    'KOTA ADM. JAKARTA SELATAN': {
        0: 'Sentra Kuliner Primer & Usaha Retail',
        1: 'Sentra Industri Pangan Olahan Mandiri',
        2: 'Sentra Mode, Tekstil & Fesyen Kreatif'
    },
    'KOTA ADM. JAKARTA TIMUR': {
        0: 'Sentra Kuliner Populer & Kriya Terpadu',
        1: 'Sentra Produksi Pangan Olahan Kemasan',
        2: 'Sentra Niaga Sembako & Bahan Pokok'
    },
    'KOTA ADM. JAKARTA UTARA': {
        0: 'Sentra Kuliner Konsumsi & Aneka Usaha',
        1: 'Sentra Industri Pangan Olahan Pesisir',
        2: 'Sentra Distribusi Sembako & Kebutuhan Pokok'
    }
}

# ==========================================
# 3. PEMUATAN DATA K-MODES (CACHED)
# ==========================================
@st.cache_data(show_spinner=False)
def load_kmodes_data():
    possible_paths = [
        os.path.join("data", "processed", "02_umkm_kmodes_clustered.csv"),
        os.path.join("..", "data", "processed", "02_umkm_kmodes_clustered.csv"),
        "02_umkm_kmodes_clustered.csv"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Pastikan cluster_label bertipe integer
            df['cluster_label'] = df['cluster_label'].astype(str).str.extract(r'(\d+)')[0].astype(int)
            return df
    return None

df_all = load_kmodes_data()

if df_all is None:
    st.error("⚠️ Berkas `02_umkm_kmodes_clustered.csv` tidak ditemukan! Pastikan Anda telah menjalankan notebook 02.")
    st.stop()

# ==========================================
# 4. SIDEBAR: FILTER WILAYAH & PENCARIAN
# ==========================================
st.sidebar.header("📍 Filter Wilayah")

daftar_wilayah = sorted(df_all['wilayah'].unique().tolist())
selected_wilayah = st.sidebar.selectbox("Pilih Kota/Kabupaten Administrasi:", daftar_wilayah)

df_wilayah = df_all[df_all['wilayah'] == selected_wilayah].copy()

# Terapkan pemetaan nama segmen deskriptif
region_map = CLUSTER_NAME_MAP.get(selected_wilayah, {
    0: 'Segmen Usaha Utama', 
    1: 'Segmen Usaha Olahan', 
    2: 'Segmen Usaha Khusus'
})
df_wilayah['nama_segmen'] = df_wilayah['cluster_label'].map(region_map)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Cari Jenis Usaha")
search_query = st.sidebar.text_input("Ketik nama komoditas (misal: Sablon, Ikan, Fesyen):", "")

if search_query:
    df_search = df_wilayah[df_wilayah['jenis_usaha'].str.contains(search_query, case=False, na=False)]
    st.sidebar.info(f"Ditemukan {len(df_search):,} usaha dengan kata kunci '{search_query}'.")

st.sidebar.markdown("---")
st.sidebar.caption("💡 *Sistem Segmentasi UMKM DKI Jakarta Berbasis K-Modes Clustering (Kategorikal Murni).*")

# ==========================================
# 5. HALAMAN UTAMA: KPI & KARTU PROFIL
# ==========================================
st.markdown('<div class="main-title">Peta Segmentasi Jenis Usaha UMKM DKI Jakarta</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Segmentasi Data Terbuka Berbasis K-Modes Clustering | <b>{selected_wilayah}</b></div>', unsafe_allow_html=True)

# KPI Wilayah
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("Total UMKM Terdata", f"{len(df_wilayah):,} Unit")
with kpi2:
    st.metric("Jumlah Ragam Komoditas", f"{df_wilayah['jenis_usaha'].nunique():,} Kategori")
with kpi3:
    st.metric("Komoditas Terbanyak", df_wilayah['jenis_usaha'].mode()[0])

st.markdown("---")

# Kartu Karakteristik Segmen
st.subheader("💡 Ringkasan Karakteristik Segmen Klaster")

unique_cluster_ids = sorted(df_wilayah['cluster_label'].unique())
cols_kartu = st.columns(len(unique_cluster_ids))
warna_border = ["#EF4444", "#3B82F6", "#10B981"]
warna_bg = ["#FEF2F2", "#EFF6FF", "#ECFDF5"]

for idx, c_id in enumerate(unique_cluster_ids):
    sub = df_wilayah[df_wilayah['cluster_label'] == c_id]
    c_name = region_map.get(c_id, f"Klaster {c_id}")
    total_unit = len(sub)
    pct_unit = (total_unit / len(df_wilayah)) * 100
    top_komoditas = sub['jenis_usaha'].mode()[0]
    pct_top = (sub['jenis_usaha'] == top_komoditas).mean() * 100
    top_skpd = sub['skpd'].mode()[0]
    
    # Ringkas nama SKPD
    skpd_singkat = top_skpd.replace("SUKU DINAS ", "SUDIN ").replace("KOTA ADMINISTRASI ", "").replace("KOTA ADM. ", "")
    if len(skpd_singkat) > 38:
        skpd_singkat = skpd_singkat[:35] + "..."

    with cols_kartu[idx]:
        st.markdown(f"""
            <div style="
                background-color: {warna_bg[idx % len(warna_bg)]}; 
                border-left: 5px solid {warna_border[idx % len(warna_border)]}; 
                padding: 14px; 
                border-radius: 8px; 
                min-height: 190px;
            ">
                <h4 style="margin: 0 0 6px 0; color: #111827; font-size: 14.5px;">{c_name}</h4>
                <p style="font-size: 12.5px; margin: 0; color: #374151; line-height: 1.5;">
                    <b>Populasi:</b> {total_unit:,} UMKM ({pct_unit:.1f}%)<br>
                    <b>Komoditas Utama:</b> {top_komoditas} ({pct_top:.1f}%)<br>
                    <b>Instansi Pembina:</b> {skpd_singkat}
                </p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. VISUALISASI INTERAKTIF
# ==========================================
col_viz1, col_viz2 = st.columns([1, 1.3])

with col_viz1:
    st.subheader("Komposisi Segmen UMKM")
    cluster_counts = df_wilayah['nama_segmen'].value_counts().reset_index()
    cluster_counts.columns = ['Segmen', 'Jumlah UMKM']
    
    fig_pie = px.pie(
        cluster_counts, 
        values='Jumlah UMKM', 
        names='Segmen', 
        hole=0.45,
        color_discrete_sequence=['#EF4444', '#3B82F6', '#10B981']
    )
    fig_pie.update_layout(margin=dict(t=20, b=10, l=10, r=10), height=340)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_viz2:
    st.subheader("Komoditas Terbanyak per Segmen")
    pilihan_segmen_chart = st.selectbox("Pilih Segmen untuk Ditinjau:", list(region_map.values()))
    
    df_segmen_sub = df_wilayah[df_wilayah['nama_segmen'] == pilihan_segmen_chart]
    top_jenis = df_segmen_sub['jenis_usaha'].value_counts().head(8).reset_index()
    top_jenis.columns = ['Jenis Usaha', 'Jumlah Unit']
    
    fig_bar = px.bar(
        top_jenis, 
        x='Jumlah Unit', 
        y='Jenis Usaha', 
        orientation='h',
        text='Jumlah Unit',
        color='Jumlah Unit',
        color_continuous_scale='Blues'
    )
    fig_bar.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=20, b=10, l=10, r=10), height=340)
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 7. TABEL EKSPLORASI DAFTAR USAHA
# ==========================================
st.markdown("---")
st.subheader("📋 Eksplorasi Daftar Usaha Tersegmentasi")

if search_query:
    st.markdown(f"**Hasil Pencarian untuk:** `{search_query}`")
    st.dataframe(df_search[['jenis_usaha', 'skpd', 'nama_segmen', 'wilayah']], use_container_width=True)
else:
    list_segmen_names = list(region_map.values())
    tab_objects = st.tabs([f"📂 {name}" for name in list_segmen_names])
    
    for idx_tab, tab_obj in enumerate(tab_objects):
        target_segmen = list_segmen_names[idx_tab]
        with tab_obj:
            df_tab_data = df_wilayah[df_wilayah['nama_segmen'] == target_segmen]
            
            rekap_usaha = df_tab_data.groupby('jenis_usaha').agg(
                Jumlah_Usaha=('jenis_usaha', 'count'),
                Instansi_Pembina_Utama=('skpd', lambda x: x.mode()[0] if not x.empty else '-')
            ).reset_index().sort_values(by='Jumlah_Usaha', ascending=False)
            
            rekap_usaha['Porsi di Segmen (%)'] = (
                (rekap_usaha['Jumlah_Usaha'] / len(df_tab_data)) * 100
            ).round(2)
            
            st.dataframe(
                rekap_usaha,
                column_config={
                    "jenis_usaha": "Jenis Komoditas Usaha",
                    "Jumlah_Usaha": st.column_config.NumberColumn("Jumlah Unit", format="%d unit"),
                    "Porsi di Segmen (%)": st.column_config.NumberColumn("Porsi di Segmen", format="%.2f %%"),
                    "Instansi_Pembina_Utama": "Instansi Pembina Utama (SKPD)"
                },
                use_container_width=True,
                hide_index=True
            )

# ==========================================
# 8. UNDUH HASIL SEGMENTASI
# ==========================================
csv_export = df_wilayah[['wilayah', 'skpd', 'jenis_usaha', 'nama_segmen']].to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"📥 Unduh Data Segmentasi {selected_wilayah} (CSV)",
    data=csv_export,
    file_name=f"segmentasi_{selected_wilayah.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Aplikasi Segmentasi UMKM DKI Jakarta")