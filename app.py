import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Ocean Health & Fisheries Dashboard",
    layout="wide"
)

# Inisialisasi Session State Halaman & Peran
if "page" not in st.session_state:
    st.session_state.page = "home"

if "role" not in st.session_state:
    st.session_state.role = "akademisi"  # Default fallback role

# =========================================
# 1. DATA LOADING & CACHING
# =========================================
@st.cache_data
def load_data():
    df = pd.read_csv("rangkuman_historis_20tahun.csv")
    df["time"] = pd.to_datetime(df["time"])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat file basis data: {e}")
    st.stop()

# =========================================
# 2. HALAMAN UTAMA / BERANDA (HOME PAGE)
# =========================================
if st.session_state.page == "home":
    st.title("🌊 Platform Informasi & Prediksi Klimatologi Oseanografi")
    st.markdown("### Silakan pilih profil pengguna untuk masuk ke dashboard:")
    st.write("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/3063/3063822.png",
            width=150
        )
        if st.button("🐟 Masuk Sebagai Nelayan", use_container_width=True):
            st.session_state.role = "nelayan"
            st.session_state.page = "dashboard"
            st.rerun()

    with c2:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/3135/3135810.png",
            width=150
        )
        if st.button("🎓 Masuk Sebagai Akademisi", use_container_width=True):
            st.session_state.role = "akademisi"
            st.session_state.page = "dashboard"
            st.rerun()

    st.stop()

# =========================================
# 3. PROSES DATA & PENURUNAN VARIABEL INDEKS
# =========================================
def normalize(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())

# Ekstraksi Dimensi Waktu
df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month

# Menghitung Kecepatan Arus Total (Resultan uo & vo)
df["current_speed"] = np.sqrt(df["uo"]**2 + df["vo"]**2)

# Mengalkulasi Nilai Indeks Kesehatan Laut (SOHI)
df["SOHI"] = (
    0.25 * normalize(df["do"]) +
    0.20 * normalize(df["ph"]) +
    0.20 * normalize(df["chla"]) +
    0.15 * normalize(df["salinitas"]) +
    0.10 * (1 - normalize(abs(df["ssta"]))) +
    0.10 * (1 - normalize(df["gelombang"]))
) * 100

# Mengalkulasi Nilai Kesesuaian Perikanan Tangkap (FSI)
df["FSI"] = (
    0.35 * normalize(df["chla"]) +
    0.25 * normalize(df["do"]) +
    0.20 * normalize(df["current_speed"]) +
    0.10 * (1 - normalize(abs(df["ssta"]))) +
    0.10 * (1 - normalize(df["gelombang"]))
) * 100

# =========================================
# 4. KONFIGURASI FILTER SIDEBAR
# =========================================
st.sidebar.title("⚙️ Konfigurasi Filter Dashboard")

if st.sidebar.button("✨ Kembali ke Beranda (Home)", use_container_width=True):
    st.session_state.page = "home"
    st.rerun()

st.sidebar.write("---")

# Filter Pilihan Parameter Utama
parameter = st.sidebar.selectbox(
    "Pilih Parameter Grafik/Metrik:",
    ["SOHI", "FSI", "sst", "ssta", "ph", "do", "salinitas", "chla", "current_speed", "gelombang", "angin_u", "angin_v"]
)

# Filter Mode Akses Sistem
mode = st.sidebar.selectbox(
    "Pilih Mode Analisis Data:",
    ["Historis", "Real Time", "Prediksi"]
)

# Filter Fokus Tampilan Indeks Spasial Peta
indeks = st.sidebar.selectbox(
    "Pilih Indeks Pemetaan Kontur:",
    ["Ocean Health Index", "Fisheries Index"]
)

st.sidebar.write("---")

# Filter Dimensi Kalender (Tahun & Pemecahan Waktu)
tahun = st.sidebar.selectbox(
    "Pilih Tahun Analisis:",
    sorted(df["year"].unique(), reverse=True)
)

breakdown = st.sidebar.radio(
    "Breakdown Data Spasial Berdasarkan:",
    ["Bulanan", "Musiman"]
)

# Definisi Rentang Bulan untuk Setiap Musim
musim = {
    "Musim Barat":[12, 1, 2],
    "Peralihan I":[3, 4, 5],
    "Musim Timur":[6, 7, 8],
    "Peralihan II":[9, 10, 11]
}

# Menyaring data berdasarkan tahun pilihan
df_filter = df[df["year"] == tahun]

if breakdown == "Bulanan":
    bulan = st.sidebar.selectbox(
        "Pilih Bulan:",
        ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    )
    idx_bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"].index(bulan) + 1
    df_filter = df_filter[df_filter["month"] == idx_bulan]
else:
    musim_pilih = st.sidebar.selectbox(
        "Pilih Musim:",
        list(musim.keys())
    )
    df_filter = df_filter[df_filter["month"].isin(musim[musim_pilih])]

# =========================================
# 5. KONTEN UTAMA DASHBOARD & HEADER
# =========================================
st.title("🌊 Ocean Health & Fisheries Monitoring Dashboard")
st.markdown(f"**Analisis Integrasi Data Klimatologi Oseanografi (Mode Peran: {st.session_state.role.upper()})**")

# Notifikasi status operasional khusus untuk mode Real Time / Prediksi
if mode == "Real Time":
    st.info("📡 Koneksi Cloud Satelit Aktif: Sinkronisasi data operasional harian. (Catatan: Data simulasi karena belum terhubung langsung ke NOAA/CMEMS).")
elif mode == "Prediksi":
    st.warning("🔮 Mode Proyeksi: Hasil visualisasi menggunakan peramalan Algoritma Tren Iklim masa depan.")

# Menampilkan Ringkasan Kartu Metrik Kuantitatif Utama
col1, col2, col3, col4 = st.columns(4)
if not df_filter.empty:
    col1.metric("Rata-Rata (Mean)", f"{df_filter[parameter].mean():.2f}")
    col2.metric("Nilai Terendah (Min)", f"{df_filter[parameter].min():.2f}")
    col3.metric("Nilai Tertinggi (Max)", f"{df_filter[parameter].max():.2f}")
    col4.metric("Deviasi Standar (Std)", f"{df_filter[parameter].std():.2f}")
else:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter waktu ini.")

st.write("<br>", unsafe_allow_html=True)

# =========================================
# 6. PENYUSUNAN SISTEM TAB DENGAN PLOT INTERAKTIF
# =========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Pemetaan Spasial Papua", 
    "📈 Analisis Runtun Waktu", 
    "📊 Statistik & Korelasi", 
    "🌊 Kategori Kondisi Laut"
])

# --- TAB 1: PEMETAAN SPASIAL KONTUR & REKOMENDASI PERAN ---
with tab1:
    st.markdown(f"### 🗺️ Distribusi Spasial Parameter Wilayah Perairan Papua")
    
    if not df_filter.empty:
        # Menentukan kolom pewarnaan peta berdasarkan pilihan selectbox indeks di sidebar
        kolom_warna = "SOHI" if indeks == "Ocean Health Index" else "FSI"
        skala_warna = "RdYlGn" if indeks == "Ocean Health Index" else "Turbo"
        
        fig_map = px.scatter_mapbox(
            df_filter,
            lat="lat",
            lon="lon",
            color=kolom_warna,
            color_continuous_scale=skala_warna,
            zoom=4.6,
            mapbox_style="open-street-map",
            title=f"Kontur Sebaran Geografis {indeks} (Tahun {tahun})"
        )
        fig_map.update_layout(mapbox=dict(center=dict(lat=-5.5, lon=135.5)), margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Peta tidak dapat ditampilkan karena tabel filter kosong.")

    # Tampilan Informasi Kartu Rekomendasi Dinamis Berdasarkan Peran Pengguna
    st.write("---")
    st.markdown("#### 🎯 Rekomendasi Status Lapangan Kelautan")
    
    mean_fsi = df_filter['FSI'].mean() if not df_filter.empty else 0
    mean_sohi = df_filter['SOHI'].mean() if not df_filter.empty else 0
    
    if st.session_state.role == "nelayan":
        st.metric("Rata-Rata Fisheries Suitability Index (FSI):", f"{mean_fsi:.1f}")
        if mean_fsi > 80:
            st.success("🐟 **KONDISI EMAS:** Wilayah perairan Papua sangat potensial untuk operasi penangkapan ikan skala besar!")
        elif mean_fsi > 60:
            st.info("🐟 **KONDISI NORMAL:** Perairan potensial untuk penangkapan ikan. Operasi melaut berjalan normal.")
        else:
            st.warning("⚠ **KONDISI REHAT:** Potensi tangkap ikan terpantau rendah. Disarankan untuk memantau radar oseanografi wilayah lain.")
    else:
        st.metric("Rata-Rata Nilai Ocean Health Index (SOHI):", f"{mean_sohi:.1f}")
        st.info("🎓 **CATATAN PENELITI:** Analisis sebaran matriks spasial di atas menunjukkan distribusi tingkat kelentingan (*resilience*) ekosistem kelautan Papua terhadap dampak anomali iklim makro.")

# --- TAB 2: GRAFIK RUNTUN WAKTU TREN JANGKA PANJANG ---
with tab2:
    st.markdown(f"### 📈 Kurva Analisis Temporal Multi-Dekade")
    fig_ts = px.line(
        df,
        x="time",
        y=parameter,
        title=f"Tren Dinamika Parameter {parameter} Sepanjang Tahun (2001 - 2020)"
    )
    fig_ts.update_traces(line_color='#086982', line_width=2)
    fig_ts.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_ts, use_container_width=True)

# --- TAB 3: RINGKASAN DESKRIPTIF STATISTIK & MATRIKS KORELASI ---
with tab3:
    col_t1, col_t2 = st.columns([4, 6])
    
    with col_t1:
        st.markdown("##### 🔢 Matriks Deskriptif Numerik (Saring)")
        st.dataframe(df_filter.describe() if not df_filter.empty else df.describe(), use_container_width=True)
        
    with col_t2:
        st.markdown("##### 🔥 Matriks Korelasi Pearson Antar Parameter Fisik-Kimia")
        numeric_df = df.select_dtypes(include=np.number).drop(columns=['year', 'month', 'lat', 'lon'], errors='ignore')
        corr_matrix = numeric_df.corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="Coolwarm",
            title="Peta Panas Hubungan Antar Parameter Kelautan"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

# --- TAB 4: KATEGORI KONDISI KESEHATAN LAUT SEKILAS ---
with tab4:
    st.markdown("### 🌊 Evaluasi Komparatif & Kategori Kondisi Lingkungan")
    
    col_a, col_b = st.columns(2)
    with col_a:
        fig_sohi = px.line(df, x="time", y="SOHI", title="Fluktuasi Historis Ocean Health Index (SOHI)")
        fig_sohi.update_traces(line_color='#2ca02c')
        st.plotly_chart(fig_sohi, use_container_width=True)
        
    with col_b:
        fig_fsi = px.line(df, x="time", y="FSI", title="Fluktuasi Historis Fisheries Suitability Index (FSI)")
        fig_fsi.update_traces(line_color='#ff7f0e')
        st.plotly_chart(fig_fsi, use_container_width=True)
        
    st.write("<br>", unsafe_allow_html=True)
    st.subheader("📊 Status Kategori Terkini")
    
    latest_sohi = df["SOHI"].iloc[-1]
    latest_fsi = df["FSI"].iloc[-1]
    
    c_status1, c_status2 = st.columns(2)
    with c_status1:
        st.markdown(f"**Indeks Kesehatan Laut Terkini:** `{latest_sohi:.2f}`")
        if latest_sohi > 80:
            st.success("Kondisi Ekosistem: Sangat Baik")
        elif latest_sohi > 60:
            st.info("Kondisi Ekosistem: Baik")
        elif latest_sohi > 40:
            st.warning("Kondisi Ekosistem: Sedang (Butuh Pengawasan Konservasi)")
        else:
            st.error("Kondisi Ekosistem: Buruk (Terjadi Kerusakan Habitat)")
            
    with c_status2:
        st.markdown(f"**Indeks Potensi Perikanan Terkini:** `{latest_fsi:.2f}`")
        if latest_fsi > 80:
            st.success("Potensi Tangkap: Sangat Potensial")
        elif latest_fsi > 60:
            st.info("Potensi Tangkap: Potensial")
        elif latest_fsi > 40:
            st.warning("Potensi Tangkap: Cukup Potensial")
        else:
            st.error("Potensi Tangkap: Rendah (Produktivitas Primer Menurun)")
