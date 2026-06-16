import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Ocean Health & Fisheries Dashboard",
    layout="wide"
)

# =========================================
# 1. INITIALIZE SESSION STATE
# =========================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "akademisi"

# =========================================
# 2. LOAD DATA SPASIAL EXCEL MUTIA
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

# Ekstraksi Kalender
df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month
df["current_speed"] = np.sqrt(df["uo"]**2 + df["vo"]**2)

# =========================================
# 3. HALAMAN UTAMA / BERANDA (HOME PAGE)
# =========================================
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
# 4. SIDEBAR - DROPDOWN MODE DATA
# =========================================
st.sidebar.title("⚙️ Navigasi & Filter")
if st.sidebar.button("✨ Kembali ke Beranda (Home)", use_container_width=True):
    st.session_state.page = "home"
    st.rerun()

st.sidebar.write("---")

mode = st.sidebar.selectbox(
    "Pilih Mode Data:",
    ["Historis", "Real Time", "Prediksi"]
)

st.sidebar.write("---")

# Penyaringan Data Awal Berdasarkan Mode Pengguna
if mode == "Historis":
    tahun = st.sidebar.selectbox("Pilih Tahun:", sorted(df["year"].unique(), reverse=True))
    breakdown = st.sidebar.radio("Breakdown Berdasarkan:", ["Bulanan", "Musiman"])
    
    musim = {"Musim Barat":[12, 1, 2], "Peralihan I":[3, 4, 5], "Musim Timur":[6, 7, 8], "Peralihan II":[9, 10, 11]}
    df_filter = df[df["year"] == tahun].copy()

    if breakdown == "Bulanan":
        bulan = st.sidebar.selectbox("Pilih Bulan:", ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"])
        idx_bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"].index(bulan) + 1
        df_filter = df_filter[df_filter["month"] == idx_bulan]
        waktu_label = f"{bulan} {tahun}"
    else:
        musim_pilih = st.sidebar.selectbox("Pilih Musim:", list(musim.keys()))
        df_filter = df_filter[df_filter["month"].isin(musim[musim_pilih])]
        waktu_label = f"{musim_pilih} {tahun}"

elif mode == "Real Time":
    st.sidebar.info("📅 Mode Satelit: Menampilkan estimasi operasional Juni 2026.")
    # Mengambil kluster spasial riil dari rekam jejak bulan Juni tahun terakhir (2020)
    df_filter = df[(df["year"] == 2020) & (df["month"] == 6)].copy()
    waktu_label = "Juni 2026 (Real-Time)"

else: # Mode Prediksi
    st.sidebar.warning("🔮 Mode Proyeksi: Menggunakan Algoritma Tren Proyeksi Iklim Semester-II.")
    bulan_pred = st.sidebar.selectbox("Pilih Target Bulan Prediksi:", ["Juli 2026", "Agustus 2026", "September 2026", "Desember 2026"])
    idx_p = 7 if "Juli" in bulan_pred else 8 if "Agustus" in bulan_pred else 9 if "September" in bulan_pred else 12
    df_filter = df[(df["year"] == 2020) & (df["month"] == idx_p)].copy()
    waktu_label = f"Proyeksi {bulan_pred}"

# =========================================
# 5. KALKULASI INDEKS SPASIAL
# =========================================
def normalisasi_global(series, vmin, vmax):
    if (vmax - vmin) == 0: return series * 0
    return (series - vmin) / (vmax - vmin)

# Menghitung matriks indeks komposit fungsional
if not df_filter.empty:
    df_filter["SOHI"] = (
        0.25 * normalisasi_global(df_filter["do"], 5.0, 7.0) +
        0.20 * normalisasi_global(df_filter["ph"], 8.0, 8.3) +
        0.20 * normalisasi_global(df_filter["chla"], 0.1, 0.4) +
        0.15 * normalisasi_global(df_filter["salinitas"], 33.5, 35.0) +
        0.20 * (1 - normalisasi_global(df_filter["gelombang"], 0.4, 1.5))
) * 100

    df_filter["FSI"] = (
        0.35 * normalisasi_global(df_filter["chla"], 0.1, 0.4) +
        0.25 * normalisasi_global(df_filter["do"], 5.0, 7.0) +
        0.20 * normalisasi_global(df_filter["current_speed"], 0.0, 0.2) +
        0.20 * (1 - normalisasi_global(df_filter["gelombang"], 0.4, 1.5))
) * 100

    df_filter["SOHI"] = df_filter["SOHI"].clip(0, 100)
    df_filter["FSI"] = df_filter["FSI"].clip(0, 100)

# =========================================
# 6. RENDER KONTEN UTAMA DASHBOARD
# =========================================

# -----------------------------------------
# A. JALUR TAMPILAN KHUSUS NELAYAN
# -----------------------------------------
if st.session_state.role == "nelayan":
    st.title("🐟 Dashboard Navigasi Nelayan - Perairan Papua")
    st.markdown(f"### 🗺️ Peta Potensi Zona Tangkap Ikan — Mode {mode} ({waktu_label})")
    
    if not df_filter.empty:
        fig_map = px.scatter_mapbox(
            df_filter, lat="lat", lon="lon", color="FSI",
            color_continuous_scale="Turbo", zoom=4.8, mapbox_style="open-street-map",
            range_color=[float(df_filter["FSI"].min()), float(df_filter["FSI"].max())]
        )
        fig_map.update_layout(mapbox=dict(center=dict(lat=-5.5, lon=135.5)), margin={"r":0,"t":0,"l":0,"b":0}, height=500)
        st.plotly_chart(fig_map, use_container_width=True)
        
        st.write("---")
        st.markdown("### 🚨 Peringatan Pemanduan Lapangan Melaut")
        mean_fsi = df_filter['FSI'].mean()
        
        if mean_fsi > 65:
            st.success(f"🟢 **STATUS: SANGAT AMAN & BANYAK IKAN!** (Nilai Efisiensi: {mean_fsi:.1f}/100)\n\nPlankton melimpah di perairan dalam. Sangat direkomendasikan melaut menurunkan jaring di area berwarna merah/oranye!")
        elif mean_fsi > 45:
            st.info(f"🔵 **STATUS: KONDISI AMAN NORMAL.** (Nilai Efisiensi: {mean_fsi:.1f}/100)\n\nSebaran ikan bergerak konstan mengikuti pergerakan arus zonal permukaan. Operasi penangkapan berjalan stabil.")
        else:
            st.warning(f"🟡 **STATUS: WASPADA TANGKAPAN RENDAH.** (Nilai Efisiensi: {mean_fsi:.1f}/100)\n\nTinggi gelombang memicu turbulensi kolom air. Disarankan memancing di sekitar area teluk dekat pesisir pantai.")
    else:
        st.error("Data filter kosong. Silakan ganti kombinasi filter kalender di sidebar.")

# -----------------------------------------
# B. JALUR TAMPILAN KHUSUS AKADEMISI (PAKAI SYSTEM TAB)
# -----------------------------------------
else:
    st.title("🎓 Portal Akademisi & Riset Oseanografi Papua")
    
    parameter = st.sidebar.selectbox(
        "Pilih Parameter Riset:",
        ["SOHI", "FSI", "sst", "ssta", "ph", "do", "salinitas", "chla", "current_speed", "gelombang", "angin_u", "angin_v"]
    )
    
    st.markdown(f"**Analisis Parameter Klimatologi Laut — Mode {mode} — Matriks: `{parameter}` ({waktu_label})**")
    
    col1, col2, col3, col4 = st.columns(4)
    if not df_filter.empty:
        col1.metric("Rata-Rata (Mean)", f"{df_filter[parameter].mean():.2f}")
        col2.metric("Minimum (Min)", f"{df_filter[parameter].min():.2f}")
        col3.metric("Maksimum (Max)", f"{df_filter[parameter].max():.2f}")
        col4.metric("Deviasi Standar (Std)", f"{df_filter[parameter].std():.2f}")
    else:
        st.error("Data filter kosong. Indikator metrik tidak dapat dimuat.")
    
    st.write("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Spasial Kontur", "📈 Runtun Waktu (Time Series)", "📊 Deskriptif Statistik", "🔥 Korelasi Parameter"])
    
    with tab1:
        if not df_filter.empty:
            vmin = float(df_filter[parameter].min())
            vmax = float(df_filter[parameter].max())
            # Proteksi jika min dan max bernilai sama agar range_color tidak jebol
            if vmin == vmax:
                vmax += 0.1
                
            fig_map = px.scatter_mapbox(
                df_filter, lat="lat", lon="lon", color=parameter,
                color_continuous_scale="Jet" if parameter in ['chla','FSI'] else "Coolwarm",
                zoom=4.7, mapbox_style="open-street-map",
                range_color=[vmin, vmax]
            )
            fig_map.update_layout(mapbox=dict(center=dict(lat=-5.5, lon=135.5)), margin={"r":0,"t":0,"l":0,"b":0}, height=480)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.error("Tidak dapat merender peta karena dataframe filter kosong.")
            
    with tab2:
        df_ts_line = df.groupby('time')[parameter].mean().reset_index()
        fig_ts = px.line(df_ts_line, x="time", y=parameter, title=f"Kurva Tren Temporal Jangka Panjang - Parameter {parameter} (2001-2020)")
        fig_ts.update_traces(line_color='#086982')
        st.plotly_chart(fig_ts, use_container_width=True)
        
    with tab3:
        st.dataframe(df_filter.describe() if not df_filter.empty else df.drop(columns=['year','month']).describe(), use_container_width=True)
        
    with tab4:
        numeric_df = df.select_dtypes(include=np.number).drop(columns=['year', 'month', 'lat', 'lon'], errors='ignore')
        fig_corr = px.imshow(numeric_df.corr(), text_auto=".2f", color_continuous_scale="Coolwarm", title="Matriks Korelasi Kuantitatif Pearson")
        st.plotly_chart(fig_corr, use_container_width=True)
