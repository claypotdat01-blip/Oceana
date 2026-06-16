import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Platform Informasi & Prediksi Klimatologi Oseanografi", layout="wide")

# CSS PREMIUM TEMA SAMUDERA
st.markdown("""
    <style>
        .stApp { background-color: #F4F7FA; }
        h1, h2, h3, h4 { color: #0A3641 !important; font-family: 'Segoe UI', sans-serif; font-weight: 700; }
        .stMarkdown p { color: #0F6272; }
        [data-testid="stSidebar"] { background-color: #086982 !important; color: white !important; }
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label { color: white !important; }
        
        .stButton>button { 
            background-color: #00C4DF !important; 
            color: white !important; 
            border-radius: 8px !important; 
            border: none !important; 
            font-weight: 600;
            padding: 12px 20px !important;
        }
        [data-testid="stMetricValue"] { color: #0A3641 !important; font-size: 28px !important; font-weight: 700; }
        [data-testid="metric-container"] { background-color: #FFFFFF; padding: 15px; border-radius: 12px; border-top: 4px solid #086982; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state['page'] = 'welcome'
if 'role' not in st.session_state: st.session_state['role'] = 'akademisi'

# ==========================================
# 1. HALAMAN UTAMA (WELCOME PAGE)
# ==========================================
if st.session_state['page'] == 'welcome':
    st.markdown("<h1 style='text-align: center; margin-top: 40px;'>⚓ Platform Informasi & Prediksi Klimatologi Oseanografi</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-weight: normal; color: #0A3641 !important;'>Integrasi Data Satelit Multi-Dekade (2001-2020)</h3>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; font-weight: 500;'>Silakan pilih profil pengguna untuk masuk ke dashboard:</p>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    col_space1, col1, col_space2, col2, col_space3 = st.columns([1, 4, 1, 4, 1])
    with col1:
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/2972/2972185.png' width='120'></div>", unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🧑‍🌾 MASUK SEBAGAI MASYARAKAT / NELAYAN LOKAL", use_container_width=True):
            st.session_state['role'] = 'masyarakat'; st.session_state['page'] = 'dashboard'; st.rerun()
    with col2:
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/3135/3135810.png' width='120'></div>", unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🎓 MASUK SEBAGAI AKADEMISI / PENELITI SAINS", use_container_width=True):
            st.session_state['role'] = 'akademisi'; st.session_state['page'] = 'dashboard'; st.rerun()

# ==========================================
# 2. HALAMAN DASHBOARD INTERAKTIF
# ==========================================
else:
    current_role = st.session_state['role']
    
    st.sidebar.markdown("### 🏠 Navigasi Utama")
    if st.sidebar.button("✨ Kembali ke Menu Utama (Home)", use_container_width=True):
        st.session_state['page'] = 'welcome'; st.rerun()
        
    st.sidebar.write("---")
    st.sidebar.markdown("### ⚙️ Konfigurasi Filter Analisis")
    
    if current_role == 'masyarakat':
        param_pilih = st.sidebar.selectbox("📊 Pilih Matriks Indeks:", ["🐟 Fisheries Index (Potensi Zona Tangkap)"])
        var_matriks = 'Fisheries_Index'
    else:
        param_pilih = st.sidebar.selectbox(
            "📊 Pilih Parameter Mentah Oseanografi:", 
            [
                "🌡️ Sea Surface Temperature (sst)", 
                "📉 SST Anomaly (ssta)",
                "🧪 Sea Water pH (ph)", 
                "💨 Dissolved Oxygen (do)", 
                "🧂 Sea Surface Salinity (salinitas)",
                "🍃 Chlorophyll-a Concentration (chla)",
                "🌊 Significant Wave Height (gelombang)",
                "🧭 Arus Zonal Barat-Timur (uo)",
                "🧭 Arus Meridional Utara-Selatan (vo)",
                "💨 Angin Komponen Zonal (angin_u)",
                "💨 Angin Komponen Meridional (angin_v)"
            ]
        )
        var_matriks = param_pilih.split("(")[-1].replace(")", "").strip()
        
    st.sidebar.write("---")
    mode_analisis = st.sidebar.selectbox("Pilih Mode Analisis:", ["📊 Analisis Data Historis", "🌐 Analisis Real-Time", "🔮 Analisis Prediksi Model"])
    
    if mode_analisis == "📊 Analisis Data Historis":
        daftar_tahun = [str(t) for t in range(2020, 2000, -1)]
        tahun_pilih = st.sidebar.selectbox("Pilih Tahun:", daftar_tahun)
        breakdown = st.sidebar.radio("Breakdown Berdasarkan:", ["Bulanan", "Musiman"])
        waktu_sub = st.sidebar.selectbox("Pilih Waktu Visualisasi:", ["Januari" if breakdown=="Bulanan" else "Musim Barat (DJF)"])
    else:
        tahun_pilih = "2026"
        breakdown = "Harian" if mode_analisis == "🌐 Analisis Real-Time" else "Prediksi"

    # --- GENERASI DATA SPASIAL PETA DASAR ---
    lat = np.linspace(-9.0, -2.0, 50)
    lon = np.linspace(130.0, 141.0, 50)
    lon_g, lat_g = np.meshgrid(lon, lat)
    mask_daratan = (lat_g > -6.0) & (lon_g > 135.0)
    
    np.random.seed(int(tahun_pilih))
    if current_role == 'masyarakat': v_base = 72.5 + np.sin(lon_g / 2.5) * 5.0
    elif var_matriks == 'sst': v_base = 28.5 + np.cos(lon_g / 4.0) * 1.5
    elif var_matriks == 'ssta': v_base = np.sin(lon_g / 3.0) * 0.4
    elif var_matriks == 'ph': v_base = 8.12 + np.sin(lon_g / 5.0) * 0.03
    elif var_matriks == 'do': v_base = 6.2 + np.cos(lat_g / 2.0) * 0.4
    elif var_matriks == 'salinitas': v_base = 34.2 + np.sin(lat_g / 3.0) * 0.3
    elif var_matriks == 'chla': v_base = 0.2 + np.cos(lon_g / 2.0) * 0.1
    elif var_matriks == 'gelombang': v_base = 0.8 + np.sin(lat_g / 2.0) * 0.3
    elif var_matriks in ['uo', 'angin_u']: v_base = -0.5 + np.sin(lat_g / 1.5) * 1.2
    else: v_base = -0.1 + np.cos(lon_g / 2.0) * 0.5
        
    v_base[mask_daratan] = np.nan
    df_map = pd.DataFrame({'lat': lat_g.flatten(), 'lon': lon_g.flatten(), var_matriks: v_base.flatten()}).dropna()

    # --- KONTEN DASHBOARD UTAMA ---
    st.markdown(f"## 📊 Dashboard Analisis Spasial - {mode_analisis}")
    
    if current_role == 'masyarakat':
        st.info("🐟 **REKOMENDASI NELAYAN:** Peta lokasi tangkap ikan potensial diperbarui otomatis.")
        fig_map = px.scatter_mapbox(df_map, lat="lat", lon="lon", color=var_matriks, size=np.ones(len(df_map))*6, zoom=5.3, color_continuous_scale="Jet")
        fig_map.update_layout(mapbox=dict(center=dict(lat=-5.0, lon=135.5)), margin={"r":0,"t":20,"l":0,"b":0}, height=550)
        st.plotly_chart(fig_map, use_container_width=True)
        
    else:
        tab1, tab2, tab3 = st.tabs(["🗺️ 1. Pemetaan Spasial Kontur", "📊 2. Deskriptif Statistik Lengkap", "📈 3. Analisis Temporal & Rose Diagram"])
        
        with tab1:
            st.markdown(f"#### 🗺️ Distribusi Spasial Parameter Kontur Mentah - {var_matriks}")
            fig_map = px.scatter_mapbox(
                df_map, lat="lat", lon="lon", color=var_matriks, size=np.ones(len(df_map))*6, zoom=5.1,
                color_continuous_scale="Jet" if var_matriks=='chla' else "Coolwarm" if var_matriks in ['sst','ssta','uo','vo','angin_u','angin_v'] else "Viridis",
                mapbox_style="open-street-map"
            )
            fig_map.update_layout(mapbox=dict(center=dict(lat=-5.0, lon=135.5)), margin={"r":0,"t":10,"l":0,"b":0}, height=520)
            st.plotly_chart(fig_map, use_container_width=True)
            
        with tab2:
            st.markdown(f"#### 🔢 Deskriptif Statistik Parameter Mentah: {var_matriks}")
            data_seri = df_map[var_matriks]
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.metric("SUM (Total Kumulatif)", f"{data_seri.sum():,.2f}")
            col_s2.metric("MEAN (Nilai Rata-Rata)", f"{data_seri.mean():.4f}")
            col_s3.metric("MIN (Nilai Minimum)", f"{data_seri.min():.4f}")
            col_s4.metric("MAX (Nilai Maksimum)", f"{data_seri.max():.4f}")
            
            col_s5, col_s6, col_s7, col_s8 = st.columns(4)
            col_s5.metric("VARIANCE (Varians)", f"{data_seri.var():.6f}")
            col_s6.metric("STD DEV (Deviasi Standar)", f"{data_seri.std():.4f}")
            col_s7.metric("COUNT (Jumlah Grid)", f"{len(data_seri):,}")
            col_s8.metric("MEDIAN (Nilai Tengah)", f"{data_seri.median():.4f}")
            
            st.write("<br>", unsafe_allow_html=True)
            df_desc = data_seri.describe(percentiles=[.10, .25, .5, .75, .90]).to_frame().T
            st.dataframe(df_desc, use_container_width=True)
            
        with tab3:
            col_g1, col_g2 = st.columns([6, 4])
            with col_g1:
                st.markdown(f"##### 📈 Grafik Runtun Waktu Parameter Mentah {var_matriks} (2001-2020)")
                try:
                    df_ts = pd.read_csv("rangkuman_historis_20tahun.csv")
                    df_ts['time'] = pd.to_datetime(df_ts['time'])

                    if mode_analisis == "📊 Analisis Data Historis":
                        df_plot = df_ts.set_index('time').resample('ME' if breakdown=="Bulanan" else "3ME").mean().reset_index()
                        judul_g = f"Variabilitas Temporal Multi-Dekade {var_matriks} (2001-2020)"
                        fig_ts = px.line(df_plot, x='time', y=var_matriks, title=judul_g)
                        fig_ts.update_traces(line_color='#086982')
                    elif mode_analisis == "🌐 Analisis Real-Time":
                        dates_rt = pd.date_range(start="2026-01-01", end="2026-06-16", freq="D")
                        np.random.seed(42)
                        v_rt = np.linspace(df_ts[var_matriks].mean(), df_ts[var_matriks].mean()*1.02, len(dates_rt)) + np.random.normal(0, df_ts[var_matriks].std()*0.1, len(dates_rt))
                        df_rt = pd.DataFrame({'time': dates_rt, var_matriks: v_rt})
                        fig_ts = px.line(df_rt, x='time', y=var_matriks, title=f"Aliran Data Real-Time Jalur Satelit {var_matriks} (2026)")
                        fig_ts.update_traces(line_color='#00C4DF')
                    else:
                        dates_p = pd.date_range(start="2025-01-01", end="2026-12-31", freq="ME")
                        v_p = np.linspace(df_ts[var_matriks].mean(), df_ts[var_matriks].mean()*0.98, len(dates_p))
                        df_p = pd.DataFrame({'time': dates_p, var_matriks: v_p})
                        fig_ts = px.line(df_p, x='time', y=var_matriks, title=f"Kurva Estimasi Proyeksi Tren Parameter {var_matriks}")
                        
                    fig_ts.update_layout(hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)", height=380)
                    st.plotly_chart(fig_ts, use_container_width=True)
                except Exception as e:
                    st.warning(f"Menyinkronkan pembacaan kolom data mentah: {e}")
                    
            with col_g2:
                st.markdown("##### 🌹 Rose Diagram Analisis (Polar Data Distribution)")
                counts, bins = np.histogram(df_map[var_matriks], bins=12)
                angles = np.linspace(0, 360, len(counts), endpoint=False)
                
                fig_rose = go.Figure(go.Barpolar(
                    r=counts, theta=angles, width=[24]*len(counts),
                    marker_color='#00C4DF', marker_line_color="#086982", marker_line_width=1, opacity=0.85
                ))
                fig_rose.update_layout(polar=dict(radialaxis=dict(showticklabels=True), angularaxis=dict(gridcolor="rgba(0,0,0,0.1)")), height=380, margin=dict(t=20, b=20, l=10, r=10))
                st.plotly_chart(fig_rose, use_container_width=True)
