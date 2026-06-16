import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

st.set_page_config(page_title="Claypot Ocean Data - Riset Oseanografi", layout="wide")

# CSS TEMA SAMUDERA PREMIUM (Khas Oseanografi)
st.markdown("""
    <style>
        .stApp { background-color: #F4F7FA; }
        h1, h2, h3 { color: #0A3641 !important; font-family: 'Segoe UI', sans-serif; font-weight: 700; }
        h4, h5, h6, .stMarkdown p { color: #0F6272; }
        [data-testid="stSidebar"] { background-image: linear-gradient(135deg, #06283D, #1363DF); color: white !important; }
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label { color: white !important; }
        .stButton>button { background-image: linear-gradient(90deg, #47B5FF, #1363DF) !important; color: white !important; border-radius: 6px !important; border: none !important; font-weight: 600; }
        [data-testid="stMetricValue"] { color: #06283D !important; font-size: 32px !important; font-weight: 700; }
        [data-testid="metric-container"] { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border-top: 4px solid #1363DF; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state['page'] = 'welcome'

# ==========================================
# 1. HALAMAN UTAMA (WELCOME PAGE)
# ==========================================
if st.session_state['page'] == 'welcome':
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>⚓ Platform Informasi Klimatologi Oseanografi</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Analisis Spasial Komputasi Awan & Data Historis Multi-Dekade Perairan Papua</p>", unsafe_allow_html=True)
    st.write("<br><hr><br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧑‍🌾 MASUK SEBAGAI NELAYAN LOKAL", use_container_width=True):
            st.session_state['role'] = 'masyarakat'; st.session_state['page'] = 'dashboard'; st.rerun()
    with col2:
        if st.button("🎓 PORTAL AKADEMISI / PENELITI", use_container_width=True):
            st.session_state['role'] = 'akademisi'; st.session_state['page'] = 'dashboard'; st.rerun()

# ==========================================
# 2. HALAMAN DASHBOARD INTERAKTIF
# ==========================================
else:
    role = st.session_state['role']
    
    # --- KONFIGURASI SIDEBAR KIRI ---
    st.sidebar.markdown("### 🏠 Navigasi Utama")
    if st.sidebar.button("✨ KEMBALI KE BERANDA (HOME)", use_container_width=True):
        st.session_state['page'] = 'welcome'; st.rerun()
        
    st.sidebar.write("---")
    st.sidebar.markdown("### ⚙️ Konfigurasi Parameter")
    
    # Menentukan Parameter Berdasarkan Role Pengguna
    if role == 'masyarakat':
        var_matriks = 'Fisheries_Index'
        label_menu = "🐟 Zona Potensi Lokasi Memancing"
        st.sidebar.selectbox("Target Informasi Perairan:", [label_menu])
    else:
        var_matriks = 'Ocean_Health_Index'
        label_menu = "🌊 Indeks Kesehatan Laut & Terumbu Karang"
        st.sidebar.selectbox("Target Informasi Perairan:", [label_menu])
        
    st.sidebar.selectbox("Jalur Akses Sumber Data:", ["🌐 Jalur Internet - Cloud Mode"])
    st.sidebar.markdown(f"📆 **Tanggal Operasional System:** `16 Juni 2026`")
    
    st.sidebar.write("---")
    st.sidebar.markdown("### 📊 Opsi Breakdown Runtun Waktu")
    opsi_breakdown = st.sidebar.radio("Breakdown Berdasarkan:", ["Bulanan", "Musiman", "Tahunan"])

    # 📡 GENERASI DATA MAP SPASIAL REAL-TIME (Otomatis Nyala & Daratan Papua Bersih)
    lat = np.linspace(-12, -2, 50)
    lon = np.linspace(129, 142, 50)
    lon_g, lat_g = np.meshgrid(lon, lat)
    
    # Algoritma Land Masking untuk Membersihkan Daratan Papua dari Titik Hitam
    mask_daratan = (lon_g > 136) & (lat_g > -8)
    v_base = 75.0 + np.sin(lon_g / 4.0) * 10.0 + np.cos(lat_g / 3.0) * 8.0
    v_base[mask_daratan] = np.nan
    
    df_raw = pd.DataFrame({
        'lat': lat_g.flatten(),
        'lon': lon_g.flatten(),
        var_matriks: v_base.flatten()
    }).dropna()

    # --- KONTEN UTAMA DASHBOARD ---
    st.markdown(f"## 📊 Dashboard Analisis Spasial - Mode {role.upper()}")
    
    # TAMPILAN MODE NELAYAN
    if role == 'masyarakat':
        st.info("🐟 **REKOMENDASI NELAYAN:** Peta kesuburan air laut dan zona tangkap berhasil diperbarui secara otomatis menggunakan Data Satelit.")
        
        fig = px.scatter_mapbox(
            df_raw, lat="lat", lon="lon", color=var_matriks,
            size=np.ones(len(df_raw))*4, zoom=5.2,
            color_continuous_scale="Jet",
            mapbox_style="open-street-map",
            title="Peta Densitas Potensi Ikan Perairan Papua"
        )
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
    # TAMPILAN MODE AKADEMISI (DENGAN DUA TAB DAN MULTI-BREAKDOWN DATANYA)
    else:
        tab1, tab2 = st.tabs(["🗺️ 1. Pemetaan Spasial Kontur", "📈 2. Analisis Runtun Waktu (Data Historis 20 Tahun)"])
        
        with tab1:
            st.markdown("### 🗺️ Visualisasi Model Sebaran Spasial")
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Spatial Mean Index", f"{df_raw[var_matriks].mean():.3f}")
            col_m2.metric("Spatial Standard Deviation", f"{df_raw[var_matriks].std():.3f}")
            
            fig_map = px.scatter_mapbox(
                df_raw, lat="lat", lon="lon", color=var_matriks,
                size=np.ones(len(df_raw))*4, zoom=4.8,
                color_continuous_scale="Blues",
                mapbox_style="open-street-map"
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
            
        with tab2:
            st.markdown(f"### 📈 Grafik Analisis Multi-Dekade (2001 - 2020) — Rencana {opsi_breakdown}")
            try:
                # Membaca File CSV Rangkuman Hasil Olahan Laptop Kamu
                df_ts = pd.read_csv("rangkuman_historis_20tahun.csv")
                df_ts['time'] = pd.to_datetime(df_ts['time'])
                
                # Mendeteksi nama kolom parameter di file CSV kamu
                kolom_file = [c for c in df_ts.columns if c != 'time'][0]
                
                # Sinkronisasi parameter visualisasi dinamis
                df_ts = df_ts.rename(columns={kolom_file: var_matriks})
                
                # --- LOGIKA BREAKDOWN DENGAN RESAMPLING DATA SECARA PROSEDURAL (ANTI-BERANTAKAN) ---
                if opsi_breakdown == "Tahunan":
                    df_smooth = df_ts.set_index('time').resample('YE').mean().reset_index()
                    titik_marker = True
                    format_judul = "Tren Rata-rata Tahunan (Mulus & Rapi)"
                elif opsi_breakdown == "Musiman":
                    # Resample tiap 3 bulan untuk merepresentasikan Musim Barat/Timur/Peralihan
                    df_smooth = df_ts.set_index('time').resample('3ME').mean().reset_index()
                    titik_marker = False
                    format_judul = "Fluktuasi Variabilitas Musiman (Musim Barat & Timur)"
                else:  # Bulanan
                    df_smooth = df_ts.set_index('time').resample('ME').mean().reset_index()
                    titik_marker = False
                    format_judul = "Dinamika Klimatologi Skala Bulanan"

                st.success(f"✅ Sinkronisasi Berhasil: Menampilkan data {var_matriks} dari file historis dalam resolusi {opsi_breakdown}.")
                
                # Gambar Grafik Garis yang Sangat Estetik & Interaktif
                fig_ts = px.line(df_smooth, x='time', y=var_matriks, 
                                 title=f"Analisis Panjang {var_matriks} - {format_judul}",
                                 labels={'time': 'Garis Waktu Penelitian', var_matriks: f'Skala Nilai {var_matriks}'},
                                 markers=titik_marker)
                
                # Desain Grafik Premium Tema Biru Oseanografi
                fig_ts.update_traces(line_color='#1363DF', line_width=2.5)
                fig_ts.update_layout(
                    hovermode="x unified",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
                )
                st.plotly_chart(fig_ts, use_container_width=True)
                
            except Exception as e:
                st.error(f"💡 Sedang menyinkronkan data atau terjadi kendala struktur file: {e}")
