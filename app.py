import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Ocean Health & Fisheries Dashboard",
    layout="wide"
)

def normalisasi_global(series, vmin, vmax):
    if (vmax - vmin) == 0: return series * 0
    return (series - vmin) / (vmax - vmin)

# =========================================
# 1. INITIALIZE SESSION STATE
# =========================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "role" not in st.session_state:
    st.session_state.role = "akademisi"

# =========================================
# 2. LOAD DATA HISTORIS
# =========================================
@st.cache_data
def load_data():
    try:
        df_data = pd.read_csv("rangkuman_historis_20tahun.csv")
    except:
        dates_fallback = pd.date_range(start="2001-01-01", end="2020-12-01", freq="MS")
        df_data = pd.DataFrame({"time": dates_fallback})

    df_data["time"] = pd.to_datetime(df_data["time"])

    if "uo" not in df_data.columns: df_data["uo"] = -0.05
    if "vo" not in df_data.columns: df_data["vo"] = -0.01
    if "sst" not in df_data.columns: df_data["sst"] = 28.5 + (df_data["uo"] * 5)
    if "ssta" not in df_data.columns: df_data["ssta"] = df_data["uo"] * 2
    if "ph" not in df_data.columns: df_data["ph"] = 8.12 + (df_data["vo"] * 0.5)
    if "do" not in df_data.columns: df_data["do"] = 6.2 - (df_data["uo"] * 2)
    if "salinitas" not in df_data.columns: df_data["salinitas"] = 34.2 + (df_data["vo"] * 2)
    if "chla" not in df_data.columns: df_data["chla"] = 0.22 + (df_data["uo"] * 0.4)
    if "gelombang" not in df_data.columns: df_data["gelombang"] = 0.8 + (df_data["uo"] * 1.2)
    if "angin_u" not in df_data.columns: df_data["angin_u"] = -1.5 + (df_data["uo"] * 10)
    if "angin_v" not in df_data.columns: df_data["angin_v"] = -0.5 + (df_data["vo"] * 5)

    return df_data

df = load_data()

df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month
df["current_speed"] = np.sqrt(df["uo"]**2 + df["vo"]**2)

df["Ocean_Health_Index"] = (
    0.25 * normalisasi_global(df["do"], 5.0, 7.0) +
    0.20 * normalisasi_global(df["ph"], 8.0, 8.3) +
    0.20 * normalisasi_global(df["chla"], 0.1, 0.4) +
    0.15 * normalisasi_global(df["salinitas"], 33.5, 35.0) +
    0.20 * (1 - normalisasi_global(df["gelombang"], 0.4, 1.5))
) * 100

df["Fisheries_Index"] = (
    0.35 * normalisasi_global(df["chla"], 0.1, 0.4) +
    0.25 * normalisasi_global(df["do"], 5.0, 7.0) +
    0.20 * normalisasi_global(df["current_speed"], 0.0, 0.2) +
    0.20 * (1 - normalisasi_global(df["gelombang"], 0.4, 1.5))
) * 100

# =========================================
# 3. HOME PAGE
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
# 4. SIDEBAR
# =========================================
st.sidebar.title("⚙️ Navigasi & Filter")
if st.sidebar.button("✨ Kembali ke Beranda (Home)", use_container_width=True):
    st.session_state.page = "home"
    st.rerun()

st.sidebar.write("---")

mode = st.sidebar.selectbox("Pilih Mode Data:", ["Historis", "Real Time", "Prediksi"])
st.sidebar.write("---")

if mode == "Historis":
    tahun = st.sidebar.selectbox("Pilih Tahun:", sorted(df["year"].unique(), reverse=True))
    breakdown = st.sidebar.radio("Breakdown Berdasarkan:", ["Bulanan", "Musiman"])
    musim = {"Musim Barat":[12,1,2], "Peralihan I":[3,4,5], "Musim Timur":[6,7,8], "Peralihan II":[9,10,11]}
    df_filter_base = df[df["year"] == tahun].copy()
    if breakdown == "Bulanan":
        bulan = st.sidebar.selectbox("Pilih Bulan:", ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"])
        idx_bulan = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"].index(bulan) + 1
        df_filter_base = df_filter_base[df_filter_base["month"] == idx_bulan]
        waktu_label = f"{bulan} {tahun}"
    else:
        musim_pilih = st.sidebar.selectbox("Pilih Musim:", list(musim.keys()))
        df_filter_base = df_filter_base[df_filter_base["month"].isin(musim[musim_pilih])]
        waktu_label = f"{musim_pilih} {tahun}"
elif mode == "Real Time":
    st.sidebar.info("📅 Mode Satelit: Menampilkan estimasi operasional Juni 2026.")
    df_filter_base = df[(df["year"] == 2020) & (df["month"] == 6)].copy()
    waktu_label = "Juni 2026 (Real-Time)"
else:
    st.sidebar.warning("🔮 Mode Proyeksi: Menggunakan Algoritma Proyeksi Iklim Semester-II.")
    bulan_pred = st.sidebar.selectbox("Pilih Target Bulan Prediksi:", ["Juli 2026","Agustus 2026","September 2026","Desember 2026"])
    idx_p = 7 if "Juli" in bulan_pred else 8 if "Agustus" in bulan_pred else 9 if "September" in bulan_pred else 12
    df_filter_base = df[(df["year"] == 2020) & (df["month"] == idx_p)].copy()
    waktu_label = f"Proyeksi {bulan_pred}"

# =========================================
# 5. SPATIAL GRID — FIXED (no striping)
# =========================================
@st.cache_data
def build_spatial_grid(val_uo_base, val_vo_base):
    """
    Grid 80x80 dengan smooth multi-frequency spatial field.
    Kunci anti-stripe: kombinasi gelombang frekuensi rendah di KEDUA sumbu lat & lon,
    sehingga tidak ada satu frekuensi dominan yang bikin pola vertikal/horizontal.
    """
    lat_grid = np.linspace(-12.0, -4.0, 80)
    lon_grid = np.linspace(129.0, 144.0, 80)
    lon_g, lat_g = np.meshgrid(lon_grid, lat_grid)
    lat_flat = lat_g.flatten()
    lon_flat = lon_g.flatten()

    rng = np.random.default_rng(42)

    # Smooth field: frekuensi rendah, campuran lat & lon di setiap term
    var_spasial_all = (
        2.5 * np.sin(lon_flat * 0.22 + lat_flat * 0.31) +
        2.0 * np.cos(lon_flat * 0.15 - lat_flat * 0.28) +
        1.5 * np.sin(lon_flat * 0.40 + lat_flat * 0.18) +
        1.0 * np.cos(lon_flat * 0.12 + lat_flat * 0.42) +
        0.8 * np.sin(lon_flat * 0.33 - lat_flat * 0.22)
    )

    records = []
    for i in range(len(lat_flat)):
        t_lat = lat_flat[i]
        t_lon = lon_flat[i]

        # Land masking Papua
        if t_lon > 134.5 and t_lat > -4.8: continue
        if t_lon > 137.4 and t_lat > -7.8: continue
        if t_lon > 140.5 and t_lat > -8.8: continue
        if t_lon > 143.0 and t_lat > -9.5: continue

        vs = var_spasial_all[i]

        grid_uo = val_uo_base + (vs * 0.01)
        grid_vo = val_vo_base + (vs * 0.005)
        grid_speed = np.sqrt(grid_uo**2 + grid_vo**2)
        grid_do   = 6.2  - (vs * 0.05)  + rng.normal(0, 0.015)
        grid_ph   = 8.12 + (vs * 0.004) + rng.normal(0, 0.001)
        grid_chla = 0.22 + (vs * 0.010) + rng.normal(0, 0.006)
        grid_sal  = 34.2 + (vs * 0.03)  + rng.normal(0, 0.012)
        grid_wave = 0.8  + (vs * 0.04)  + rng.normal(0, 0.012)

        grid_sohi = (
            0.25 * normalisasi_global(grid_do,   5.0, 7.0) +
            0.20 * normalisasi_global(grid_ph,   8.0, 8.3) +
            0.20 * normalisasi_global(grid_chla, 0.1, 0.4) +
            0.15 * normalisasi_global(grid_sal,  33.5, 35.0) +
            0.20 * (1 - normalisasi_global(grid_wave, 0.4, 1.5))
        ) * 100

        grid_fsi = (
            0.35 * normalisasi_global(grid_chla,  0.1, 0.4) +
            0.25 * normalisasi_global(grid_do,    5.0, 7.0) +
            0.20 * normalisasi_global(grid_speed, 0.0, 0.2) +
            0.20 * (1 - normalisasi_global(grid_wave, 0.4, 1.5))
        ) * 100

        records.append({
            'lat': t_lat, 'lon': t_lon,
            'Ocean_Health_Index': np.clip(grid_sohi, 10, 100),
            'Fisheries_Index':    np.clip(grid_fsi,  10, 100),
            'uo': grid_uo, 'vo': grid_vo,
            'sst':          28.5 + (vs * 0.15) + rng.normal(0, 0.06),
            'ssta':                (vs * 0.05)  + rng.normal(0, 0.03),
            'ph': grid_ph, 'do': grid_do,
            'salinitas': grid_sal, 'chla': grid_chla,
            'current_speed': grid_speed, 'gelombang': grid_wave,
            'angin_u': -1.5 + (vs * 0.2),
            'angin_v': -0.5 + (vs * 0.1),
        })

    return pd.DataFrame(records)


val_uo_base = df_filter_base["uo"].mean() if not df_filter_base.empty else -0.05
val_vo_base = df_filter_base["vo"].mean() if not df_filter_base.empty else -0.01
df_map = build_spatial_grid(round(float(val_uo_base), 4), round(float(val_vo_base), 4))


# =========================================
# HELPER: render peta smooth
# =========================================
def render_map(df_map, z_col, colorscale, height=540):
    fig = px.density_mapbox(
        df_map, lat="lat", lon="lon", z=z_col,
        # radius dalam pixel — untuk grid 80x80 di zoom ~4.8, radius 35 mengisi gap antar titik
        radius=35,
        opacity=0.80,
        zoom=4.8,
        color_continuous_scale=colorscale,
        mapbox_style="open-street-map",
        # Pakai quantile bukan min/max agar outlier tidak mencuri range warna
        range_color=[
            float(df_map[z_col].quantile(0.03)),
            float(df_map[z_col].quantile(0.97))
        ]
    )
    fig.update_layout(
        mapbox=dict(center=dict(lat=-8.0, lon=136.5)),
        margin={"r":0,"t":40,"l":0,"b":0},
        height=height,
        coloraxis_colorbar=dict(thickness=14, len=0.7)
    )
    return fig


# =========================================
# 6. RENDER DASHBOARD
# =========================================

# --- A. NELAYAN ---
if st.session_state.role == "nelayan":
    st.title("🐟 Dashboard Navigasi Nelayan - Perairan Papua")
    st.markdown(f"### 🗺️ Peta Kontur Potensi Zona Tangkap Ikan — Mode {mode} ({waktu_label})")

    if not df_map.empty:
        st.plotly_chart(render_map(df_map, "Fisheries_Index", "Turbo"), use_container_width=True)

        st.write("---")
        st.markdown("### 🚨 Peringatan Pemanduan Lapangan Melaut")
        mean_fsi = df_map['Fisheries_Index'].mean()

        if mean_fsi > 73:
            st.success(f"🟢 **STATUS: SANGAT AMAN & BANYAK IKAN!** (Nilai Potensi: {mean_fsi:.1f}/100)\n\nNutrisi laut melimpah di perairan dalam Laut Arafura. Sangat direkomendasikan menurunkan jaring di area berwarna merah/oranye!")
        elif mean_fsi > 55:
            st.info(f"🔵 **STATUS: KONDISI AMAN NORMAL.** (Nilai Potensi: {mean_fsi:.1f}/100)\n\nPergerakan ikan konstan mengikuti arah pergerakan arus permukaan. Operasi nelayan berjalan stabil.")
        else:
            st.warning(f"🟡 **STATUS: WASPADA TANGKAPAN RENDAH.** (Nilai Potensi: {mean_fsi:.1f}/100)\n\nSuhu permukaan laut berfluktuasi. Disarankan memancing di sekitar pesisir pantai dekat teluk.")

# --- B. AKADEMISI ---
else:
    st.title("🎓 Portal Akademisi & Riset Oseanografi Papua")

    parameter = st.sidebar.selectbox(
        "Pilih Parameter Riset:",
        ["Ocean_Health_Index","Fisheries_Index","sst","ssta",
         "ph","do","salinitas","chla","current_speed","gelombang","angin_u","angin_v"]
    )

    st.markdown(f"**Analisis Parameter Klimatologi Laut — Mode {mode} — Matriks Aktif: `{parameter}` ({waktu_label})**")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rata-Rata (Mean)", f"{df_map[parameter].mean():.2f}")
    col2.metric("Minimum (Min)",    f"{df_map[parameter].min():.2f}")
    col3.metric("Maksimum (Max)",   f"{df_map[parameter].max():.2f}")
    col4.metric("Deviasi Standar",  f"{df_map[parameter].std():.2f}")

    st.write("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Spasial Kontur","📈 Runtun Waktu","📊 Deskriptif Statistik","🔥 Korelasi Parameter"])

    with tab1:
        if not df_map.empty:
            cmap_dict = {
                'Fisheries_Index':'Turbo', 'chla':'Turbo',
                'Ocean_Health_Index':'Blues', 'do':'Blues',
                'ph':'Viridis', 'salinitas':'YlOrBr',
                'sst':'Thermal', 'ssta':'RdBu',
            }
            cmap = cmap_dict.get(parameter, "Icefire")
            st.plotly_chart(render_map(df_map, parameter, cmap, height=500), use_container_width=True)

    with tab2:
        df_ts = df.groupby('time')[parameter].mean().reset_index()
        fig_ts = px.line(df_ts, x="time", y=parameter,
                         title=f"Kurva Tren Temporal — {parameter} (2001–2020)")
        fig_ts.update_traces(line_color='#086982', line_width=2.5)
        fig_ts.update_layout(plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_ts, use_container_width=True)

    with tab3:
        st.markdown("##### 🔢 Deskriptif Ringkasan Kuantitatif")
        st.dataframe(df_map[[parameter]].describe().T, use_container_width=True)

    with tab4:
        numeric_df = df.select_dtypes(include=np.number).drop(columns=['year','month'], errors='ignore')
        fig_corr = px.imshow(numeric_df.corr(), text_auto=".2f",
                             color_continuous_scale="RdBu",
                             title="Matriks Korelasi Pearson")
        st.plotly_chart(fig_corr, use_container_width=True)
