import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Peta Segmentasi UMKM DKI Jakarta",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

FEATURES = ['sektor_makro', 'jenis_instansi_pembina', 'kelompok_tahun_berdiri']

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
# 2. PEMUATAN DATA (CACHED)
# ==========================================
def _find_path(filename):
    possible_paths = [
        os.path.join("data", "processed", filename),
        os.path.join("..", "data", "processed", filename),
        filename
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

@st.cache_data(show_spinner=False)
def load_kmodes_data():
    """Memuat dataset terklasterisasi (k=3, 3 fitur) dari direktori data."""
    path = _find_path("02_umkm_kmodes_clustered.csv")
    if path is None:
        return None
    df = pd.read_csv(path)
    df['cluster'] = df['cluster'].astype(int)
    return df

@st.cache_data(show_spinner=False)
def load_elbow_data():
    """Memuat ringkasan biaya Elbow (Cost vs k, k=2..6) per wilayah."""
    path = _find_path("02b_elbow_costs.csv")
    if path is None:
        return None
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_evaluation_summary():
    """Memuat ringkasan Purity Index per klaster per wilayah (k final=3)."""
    path = _find_path("03_kmodes_evaluation_summary.csv")
    if path is None:
        return None
    return pd.read_csv(path)

def buat_nama_segmen(top_sektor, top_usia, usia_pct, c):
    """Penamaan segmen bisnis komunikatif berbasis profil dominan aktual (bukan tebakan)."""
    if usia_pct >= 60:
        deskriptor_usia = top_usia.split(' (')[0]
        return f"{top_sektor} — Segmen {deskriptor_usia} (Klaster {c})"
    return f"{top_sektor} (Klaster {c})"

def generate_cluster_profiles(df_region, profile_region):
    """Menyusun profil klaster 3-dimensi (sektor, instansi pembina, usia usaha)
    berbasis tabel Purity Index (03_kmodes_evaluation_summary.csv), lalu
    menyematkan nama segmen ke data mentah wilayah tsb."""
    df = df_region.copy()
    cluster_profiles = {}
    label_map = {}

    warna_border = ["#EF4444", "#3B82F6", "#10B981"]
    warna_bg = ["#FEF2F2", "#EFF6FF", "#ECFDF5"]

    profile_region = profile_region.sort_values('cluster')

    for idx, row in enumerate(profile_region.itertuples()):
        c = int(row.cluster)
        nama_segmen = buat_nama_segmen(
            row.sektor_makro_dominan, row.kelompok_tahun_berdiri_dominan,
            row.kelompok_tahun_berdiri_pct, c
        )

        label_map[c] = nama_segmen
        cluster_profiles[nama_segmen] = {
            'id': c,
            'total': int(row.n),
            'pct': row.pct_n,
            'top_sektor': row.sektor_makro_dominan,
            'top_sektor_pct': row.sektor_makro_pct,
            'top_instansi': row.jenis_instansi_pembina_dominan,
            'top_instansi_pct': row.jenis_instansi_pembina_pct,
            'top_usia': row.kelompok_tahun_berdiri_dominan,
            'top_usia_pct': row.kelompok_tahun_berdiri_pct,
            'purity_index': row.purity_index,
            'border': warna_border[idx % 3],
            'bg': warna_bg[idx % 3]
        }

    df['nama_segmen'] = df['cluster'].map(label_map)
    return df, cluster_profiles

# Memuat data
df_all = load_kmodes_data()
df_elbow_all = load_elbow_data()
df_eval_all = load_evaluation_summary()

if df_all is None:
    st.error("⚠️ Berkas `02_umkm_kmodes_clustered.csv` tidak ditemukan! Jalankan `notebooks/02_kmodes_partitioning.ipynb` terlebih dahulu.")
    st.stop()

if df_eval_all is None:
    st.error("⚠️ Berkas `03_kmodes_evaluation_summary.csv` tidak ditemukan! Jalankan `notebooks/03_kmodes_evaluation.ipynb` terlebih dahulu.")
    st.stop()

# ==========================================
# 3. SIDEBAR: FILTER WILAYAH & PENCARIAN
# ==========================================
st.sidebar.image("https://satudata.jakarta.go.id/assets/images/logo-dark.png", width=180)
st.sidebar.header("📍 Filter Wilayah")

daftar_wilayah = sorted(df_all['wilayah'].unique().tolist())
selected_wilayah = st.sidebar.selectbox("Pilih Kota/Kabupaten Administrasi:", daftar_wilayah)

df_wilayah_raw = df_all[df_all['wilayah'] == selected_wilayah].copy()
profile_wilayah = df_eval_all[df_eval_all['wilayah'] == selected_wilayah].copy()
df_wilayah, profiles = generate_cluster_profiles(df_wilayah_raw, profile_wilayah)

elbow_wilayah = df_elbow_all[df_elbow_all['wilayah'] == selected_wilayah].sort_values('k') if df_elbow_all is not None else None
purity_rata_wilayah = (profile_wilayah['purity_index'] * profile_wilayah['n']).sum() / profile_wilayah['n'].sum()

st.sidebar.markdown("---")
st.sidebar.header("🔍 Cari Komoditas Usaha")
search_query = st.sidebar.text_input("Ketik jenis usaha (misal: Sablon, Ikan, Fesyen):", "")

if search_query:
    df_search = df_wilayah[
        df_wilayah['jenis_usaha'].str.contains(search_query, case=False, na=False) |
        df_wilayah['sektor_makro'].str.contains(search_query, case=False, na=False) |
        df_wilayah['jenis_instansi_pembina'].str.contains(search_query, case=False, na=False)
    ]
    st.sidebar.info(f"Ditemukan {len(df_search):,} data dengan kata kunci '{search_query}'.")

st.sidebar.markdown("---")
st.sidebar.caption("💡 *Sistem Segmentasi UMKM DKI Jakarta - Algoritma K-Modes Clustering (3 Fitur: Sektor, Instansi Pembina, Usia Usaha).*")

# ==========================================
# 4. HALAMAN UTAMA: KPI WILAYAH
# ==========================================
st.markdown('<div class="main-title">Peta Segmentasi Jenis Usaha UMKM DKI Jakarta</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Segmentasi Data Terbuka Berbasis K-Modes Clustering (Periode 2024) | <b>{selected_wilayah}</b></div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Total UMKM Terdata", f"{len(df_wilayah):,} Unit")
with kpi2:
    st.metric("Ragam Jenis Usaha", f"{df_wilayah['jenis_usaha'].nunique():,} Kategori")
with kpi3:
    st.metric("Sektor Terbesar", df_wilayah['sektor_makro'].mode()[0])
with kpi4:
    st.metric("Purity Index Rata-rata", f"{purity_rata_wilayah:.1f}%", help="Rata-rata (terbobot ukuran klaster) persentase kategori termayoritas pada tiap fitur, di tiap klaster. Murni berbasis frekuensi kategori, tanpa ukuran jarak apa pun.")

st.markdown("---")

# ==========================================
# 5. KARTU PROFIL KLASTER MULTIDIMENSI
# ==========================================
st.subheader("💡 Profil Klaster Multidimensi (Sektor × Instansi Pembina × Usia Usaha)")
cols_kartu = st.columns(len(profiles))

for idx, (c_name, info) in enumerate(profiles.items()):
    with cols_kartu[idx]:
        st.markdown(f"""
            <div style="
                background-color: {info['bg']};
                border-left: 5px solid {info['border']};
                padding: 14px;
                border-radius: 8px;
                min-height: 230px;
            ">
                <h4 style="margin: 0 0 6px 0; color: #111827; font-size: 14.5px;">{c_name}</h4>
                <p style="font-size: 12.5px; margin: 0; color: #374151; line-height: 1.6;">
                    <b>Populasi:</b> {info['total']:,} UMKM ({info['pct']:.1f}%)<br>
                    <b>Sektor Dominan:</b> {info['top_sektor']} ({info['top_sektor_pct']:.1f}%)<br>
                    <b>Instansi Pembina Dominan:</b> {info['top_instansi']} ({info['top_instansi_pct']:.1f}%)<br>
                    <b>Usia Usaha Dominan:</b> {info['top_usia']} ({info['top_usia_pct']:.1f}%)<br>
                    <b>Purity Index Klaster:</b> {info['purity_index']:.1f}%
                </p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. EVALUASI KLASTER: KURVA ELBOW & PURITY INDEX
# ==========================================
st.markdown("---")
st.subheader("📈 Evaluasi Klaster: Kurva Elbow & Purity Index")
col_eval1, col_eval2 = st.columns([1.2, 1])

with col_eval1:
    st.caption(f"Kurva Elbow (Cost vs k) — {selected_wilayah}. k final = 3 dipilih berdasarkan kombinasi penurunan cost dan Purity Index (lihat `03_kmodes_evaluation.ipynb`).")
    if elbow_wilayah is not None and not elbow_wilayah.empty:
        fig_elbow = go.Figure()
        fig_elbow.add_trace(go.Scatter(
            x=elbow_wilayah['k'], y=elbow_wilayah['cost'],
            mode='lines+markers', line=dict(color='#2563EB', width=3), marker=dict(size=9)
        ))
        fig_elbow.add_vline(x=3, line_dash="dash", line_color="#EF4444", annotation_text="k final = 3")
        fig_elbow.update_layout(
            xaxis_title="Jumlah Klaster (k)", yaxis_title="Nilai Cost",
            margin=dict(t=20, b=10, l=10, r=10), height=300
        )
        st.plotly_chart(fig_elbow, width='stretch')
    else:
        st.info("Berkas `02b_elbow_costs.csv` tidak ditemukan — jalankan `notebooks/02_kmodes_partitioning.ipynb`.")

with col_eval2:
    st.caption(f"Purity Index per Klaster — {selected_wilayah} (murni berbasis frekuensi kategori, tanpa ukuran jarak apa pun).")
    df_purity_chart = profile_wilayah[['cluster', 'purity_index']].copy()
    df_purity_chart['Klaster'] = df_purity_chart['cluster'].map(lambda c: f"Klaster {c}")
    fig_purity = px.bar(
        df_purity_chart, x='Klaster', y='purity_index', text='purity_index',
        color='purity_index', color_continuous_scale='Blues', range_y=[0, 100]
    )
    fig_purity.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_purity.update_layout(yaxis_title="Purity Index (%)", margin=dict(t=20, b=10, l=10, r=10), height=300, coloraxis_showscale=False)
    st.plotly_chart(fig_purity, width='stretch')

# ==========================================
# 7. VISUALISASI KOMPOSISI & KOMODITAS
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
    st.plotly_chart(fig_pie, width='stretch')

with col_viz2:
    st.subheader("Komoditas Terbanyak per Segmen")
    pilihan_segmen_chart = st.selectbox("Pilih Segmen untuk Ditinjau:", list(profiles.keys()), key=f"segmen_select_{selected_wilayah}")

    df_sub = df_wilayah[df_wilayah['nama_segmen'] == pilihan_segmen_chart]
    top_jenis = df_sub['jenis_usaha'].value_counts().head(8).reset_index()
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
    fig_bar.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=20, b=10, l=10, r=10), height=340, coloraxis_showscale=False)
    st.plotly_chart(fig_bar, width='stretch')

# ==========================================
# 8. PANEL PEMBANDING: PROFIL KLASTER VS FREKUENSI SEDERHANA
# ==========================================
with st.expander("📊 Bandingkan dengan Distribusi Frekuensi Sektor Sederhana (nilai tambah clustering 3 fitur)"):
    freq_dist = (df_wilayah['sektor_makro'].value_counts(normalize=True) * 100).reset_index()
    freq_dist.columns = ['Sektor Makro', 'Persentase Populasi (%)']

    col_cmp1, col_cmp2 = st.columns(2)
    with col_cmp1:
        st.markdown("**Baseline: Frekuensi `sektor_makro` saja**")
        st.dataframe(freq_dist.round(2), width='stretch', hide_index=True)
    with col_cmp2:
        st.markdown("**Profil Klaster Multivariat (Sektor × Instansi × Usia)**")
        tabel_profil = profile_wilayah[[
            'cluster', 'pct_n', 'sektor_makro_dominan', 'sektor_makro_pct',
            'kelompok_tahun_berdiri_dominan', 'kelompok_tahun_berdiri_pct'
        ]].copy().round(2)
        tabel_profil.columns = ['Klaster', 'Populasi (%)', 'Sektor Dominan', 'Sektor (%)', 'Usia Dominan', 'Usia (%)']
        st.dataframe(tabel_profil, width='stretch', hide_index=True)
    st.caption("Klaster dengan kombinasi sektor × usia usaha yang spesifik (mis. sektor tertentu didominasi usaha rintisan baru) tidak terlihat dari tabel frekuensi sektor saja di sisi kiri.")

# ==========================================
# 9. TABEL EKSPLORASI DAFTAR USAHA
# ==========================================
st.markdown("---")
st.subheader("📋 Eksplorasi Daftar Usaha Tersegmentasi")

kolom_tampil = ['jenis_usaha', 'sektor_makro', 'jenis_instansi_pembina', 'kelompok_tahun_berdiri', 'nama_segmen']

if search_query:
    st.markdown(f"**Hasil Pencarian untuk:** `{search_query}`")
    st.dataframe(df_search[kolom_tampil + ['wilayah']], width='stretch')
else:
    list_names = list(profiles.keys())
    tabs = st.tabs([f"📂 {name}" for name in list_names])

    for idx_tab, tab_obj in enumerate(tabs):
        target_name = list_names[idx_tab]
        with tab_obj:
            df_tab_data = df_wilayah[df_wilayah['nama_segmen'] == target_name]

            rekap_usaha = df_tab_data.groupby(['jenis_usaha', 'sektor_makro']).agg(
                Jumlah_Usaha=('jenis_usaha', 'count'),
                Instansi_Pembina_Utama=('jenis_instansi_pembina', lambda x: x.mode()[0] if not x.empty else '-'),
                Usia_Usaha_Utama=('kelompok_tahun_berdiri', lambda x: x.mode()[0] if not x.empty else '-')
            ).reset_index().sort_values(by='Jumlah_Usaha', ascending=False)

            rekap_usaha['Porsi di Segmen (%)'] = (
                (rekap_usaha['Jumlah_Usaha'] / len(df_tab_data)) * 100
            ).round(2)

            st.dataframe(
                rekap_usaha,
                column_config={
                    "jenis_usaha": "Jenis Usaha",
                    "sektor_makro": "Sektor Makro",
                    "Jumlah_Usaha": st.column_config.NumberColumn("Jumlah Unit", format="%d unit"),
                    "Porsi di Segmen (%)": st.column_config.NumberColumn("Porsi di Segmen", format="%.2f %%"),
                    "Instansi_Pembina_Utama": "Instansi Pembina",
                    "Usia_Usaha_Utama": "Usia Usaha"
                },
                width='stretch',
                hide_index=True
            )

# ==========================================
# 10. UNDUH DATA
# ==========================================
csv_export = df_wilayah[['wilayah'] + kolom_tampil].to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"📥 Unduh Data Segmentasi {selected_wilayah} (CSV)",
    data=csv_export,
    file_name=f"segmentasi_{selected_wilayah.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Aplikasi Analitik Segmentasi UMKM DKI Jakarta | K-Modes Clustering (Sektor Makro × Instansi Pembina × Usia Usaha) | Evaluasi: Elbow Cost Curve & Purity Index")
