import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Ocean Health & Fisheries Dashboard",
    layout="wide"
)

# Inisialisasi Session State Halaman & Peran
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "akademisi"

# =========================================
# 1. LOAD DATA DARI EXCEL LAPTOP MUTIA
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

# Dimensi Waktu & Variabel Turunan
df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month
df["current_speed"] = np.sqrt(df["uo"]**2 + df["vo"]**2)

def normalize(series):
    if series.max() == series.min(): return series * 0
    return (series - series.min()) / (series.max() - series.min())

# Hitung Indeks Utama
df["SOHI"] = (0.25*normalize(df["do"]) + 0.20*normalize(df["ph"]) + 0.20*normalize(df["chla"]) + 0.15*normalize(df["salinitas"]) + 0.10*(1-normalize(abs(df["ssta"]))) + 0.10*(1-normalize(df["gelombang"]))) * 100
df["FSI"] = (0.35*normalize(df["chla"]) + 0.25*normalize(df["do"]) + 0.20*normalize(df["current_speed"]) + 0.10*(1-normalize(abs(df["ssta"]))) + 0.10*(1-normalize(df["gelombang"]))) * 100

# =========================================
# 2. HALAMAN UTAMA / BERANDA (HOME PAGE)
# ==========================================
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align: center; color: #0A3641;'>🌊 Platform Informasi & Prediksi Klimatologi Oseanografi</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Silakan pilih profil pengguna untuk masuk ke dashboard:</p>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/3063/3063822.png' width='130'></div>", unsafe_allow_html=True)
        if st.button("🐟 Masuk Sebagai Nelayan Lokal", use_container_width=True):
            st.session_state.role = "nelayan"
            st.session_state.page = "dashboard"
            st.rerun()
    with c2:
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/3135/3135810.png' width='130'></div>", unsafe_allow_html=True)
        if st.button("🎓 Masuk Sebagai Akademisi / Peneliti", use_container_width=True):
            st.session_state.role = "akademisi"
            st.session_state.page = "dashboard"
            st.rerun()
    st.stop()

# =========================================
# 3. SIDEBAR CONFIGURATION
# =========================================
st.sidebar.title("⚙️ Navigasi & Filter")
if st.sidebar.button("✨ Kembali ke Beranda (Home)", use_container_width=True):
    st.session_state.page = "home"
    st.rerun()

st.sidebar.write("---")

# Filter Waktu Kalender
tahun = st.sidebar.selectbox("Pilih Tahun:", sorted(df["year"].unique(), reverse=True))
breakdown = st.sidebar.radio("Breakdown Berdasarkan:", ["Bulanan", "Musiman"])

musim = {"Musim Barat":[12, 1, 2], "Peralihan I":[3, 4, 5], "Musim Timur":[6, 7, 8], "Peralihan II":[9, 10, 11]}
df_filter = df[df["year"] == tahun]

if breakdown == "Bulanan":
    bulan = st.sidebar.selectbox("Pilih Bulan:", ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"])
    idx_bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"].index(bulan) + 1
    df_filter = df_filter[df_filter["month"] == idx_bulan]
else:
    musim_pilih = st.sidebar.selectbox("Pilih Musim:", list(musim.keys()))
    df_filter = df_filter[df_filter["month"].isin(musim[musim_pilih])]

# =========================================
# 4. KONTEN DASHBOARD (DIPISAH BERDASARKAN PERAN)
# =========================================

# -----------------------------------------
# A. TAMPILAN KHUSUS NELAYAN (SUPER SIMPEL: PETA + PERINGATAN SAJA!)
# -----------------------------------------
if st.session_state.role == "nelayan":
    st.title("🐟 Dashboard Navigasi Nelayan - Perairan Papua")
    st.markdown("### 🗺️ Peta Lokasi Potensi Tangkap Ikan Hari Ini")
    
    if not df_filter.empty:
        # Tampilkan Peta Utama Nelayan
        fig_map = px.scatter_mapbox(
            df_filter, lat="lat", lon="lon", color="FSI",
            color_continuous_scale="Turbo", zoom=4.8, mapbox_style="open-street-map"
        )
        fig_map.update_layout(mapbox=dict(center=dict(lat=-5.5, lon=135.5)), margin={"r":0,"t":0,"l":0,"b":0}, height=500)
        st.plotly_chart(fig_map, use_container_width=True)
        
        # 🚨 PERINGATAN DAN REKOMENDASI NELAYAN NYATA
        st.write("---")
        st.markdown("### 🚨 Peringatan & Panduan Melaut Nelayan")
        mean_fsi = df_filter['FSI'].mean()
        
        if mean_fsi > 75:
            st.success(f"🟢 **STATUS: SANGAT AMAN & BANYAK IKAN!** (Nilai Potensi: {mean_fsi:.1f}/100)\n\nPlankton melimpah dan arus laut sangat mendukung. Sangat direkomendasikan untuk menurunkan jaring di zona merah pada peta!")
        elif mean_fsi > 55:
            st.info(f"🔵 **STATUS: KONDISI NORMAL AMAN.** (Nilai Potensi: {mean_fsi:.1f}/100)\n\nIkan tersebar merata di perairan dalam. Tetap pantau arah angin zonal saat melaut malam hari.")
        else:
            st.warning(f"🟡 **STATUS: PERINGATAN WASPADA TANGKAPAN RENDAH.** (Nilai Potensi: {mean_fsi:.1f}/100)\n\nTinggi gelombang atau perubahan suhu menghambat pergerakan kawanan ikan. Disarankan memancing dekat pesisir pantai saja.")
    else:
        st.warning("Data navigasi nelayan tidak ditemukan untuk bulan/tahun ini.")

# -----------------------------------------
# B. TAMPILAN KHUSUS AKADEMISI / PENELITI (LENGKAP DAN RIBET PAKAI TAB)
# -----------------------------------------
else:
    st.title("🎓 Portal Akademisi & Riset Oseanografi Papua")
    
    # Dropdown pilihan parameter mentah cuma muncul di mode akademisi
    parameter = st.sidebar.selectbox(
        "Pilih Parameter Riset:",
        ["SOHI", "FSI", "sst", "ssta", "ph", "do", "salinitas", "chla", "current_speed", "gelombang", "angin_u", "angin_v"]
    )
    
    st.markdown(f"**Analisis Parameter Fisik-Kimia-Biologi Laut - Matriks Aktif: `{parameter}`**")
    
    # Kartu Metrik Ringkas
    col1, col2, col3, col4 = st.columns(4)
    if not df_filter.empty:
        col1.metric("Mean", f"{df_filter[parameter].mean():.2f}")
        col2.metric("Min", f"{df_filter[parameter].min():.2f}")
        col3.metric("Max", f"{df_filter[parameter].max():.2f}")
        col4.metric("Std Dev", f"{df_filter[parameter].std():.2f}")
    
    st.write("<br>", unsafe_allow_html=True)
    
    # Tampilkan 4 Tab Khusus Peneliti
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Spasial Kontur", "📈 Runtun Waktu (Time Series)", "📊 Deskriptif Statistik", "🔥 Korelasi Parameter"])
    
    with tab1:
        if not df_filter.empty:
            fig_map = px.scatter_mapbox(
                df_filter, lat="lat", lon="lon", color=parameter,
                color_continuous_scale="Viridis" if parameter=='ph' else "Coolwarm",
                zoom=4.7, mapbox_style="open-street-map"
            )
            fig_map.update_layout(mapbox=dict(center=dict(lat=-5.5, lon=135.5)), margin={"r":0,"t":0,"l":0,"b":0}, height=480)
            st.plotly_chart(fig_map, use_container_width=True)
            
    with tab2:
        fig_ts = px.line(df, x="time", y=parameter, title=f"Kurva Tren Temporal Jangka Panjang - Parameter {parameter}")
        fig_ts.update_traces(line_color='#086982')
        st.plotly_chart(fig_ts, use_container_width=True)
        
    with tab3:
        st.dataframe(df_filter.describe() if not df_filter.empty else df.describe(), use_container_width=True)
        
    with tab4:
        numeric_df = df.select_dtypes(include=np.number).drop(columns=['year', 'month', 'lat', 'lon'], errors='ignore')
        fig_corr = px.imshow(numeric_df.corr(), text_auto=".2f", color_continuous_scale="Coolwarm", title="Matriks Korelasi Kuantitatif Pearson")
        st.plotly_chart(fig_corr, use_container_width=True)
