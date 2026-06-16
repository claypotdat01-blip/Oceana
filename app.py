import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Ocean Health & Fisheries Dashboard",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("rangkuman_historis_20tahun.csv")
    df["time"] = pd.to_datetime(df["time"])
    return df

df = load_data()

# =========================
# NORMALIZATION
# =========================
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

# =========================
# DERIVED VARIABLES
# =========================
df["current_speed"] = np.sqrt(df["uo"]**2 + df["vo"]**2)

# Ocean Health Index
df["SOHI"] = (
    0.25 * normalize(df["do"]) +
    0.20 * normalize(df["ph"]) +
    0.20 * normalize(df["chla"]) +
    0.15 * normalize(df["salinitas"]) +
    0.10 * (1 - normalize(abs(df["ssta"]))) +
    0.10 * (1 - normalize(df["gelombang"]))
) * 100

# Fisheries Suitability Index
df["FSI"] = (
    0.35 * normalize(df["chla"]) +
    0.25 * normalize(df["do"]) +
    0.20 * normalize(df["current_speed"]) +
    0.10 * (1 - normalize(abs(df["ssta"]))) +
    0.10 * (1 - normalize(df["gelombang"]))
) * 100

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Konfigurasi")

parameter = st.sidebar.selectbox(
    "Pilih Parameter",
    [
        "SOHI",
        "FSI",
        "sst",
        "ssta",
        "ph",
        "do",
        "salinitas",
        "chla",
        "current_speed",
        "gelombang",
        "angin_u",
        "angin_v"
    ]
)

# =========================
# HEADER
# =========================
st.title("🌊 Ocean Health & Fisheries Monitoring Dashboard")
st.markdown("Analisis data oseanografi 2001–2020")

# =========================
# METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Mean", f"{df[parameter].mean():.2f}")
col2.metric("Min", f"{df[parameter].min():.2f}")
col3.metric("Max", f"{df[parameter].max():.2f}")
col4.metric("Std", f"{df[parameter].std():.2f}")

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Time Series",
        "📊 Statistics",
        "🔥 Correlation",
        "🌊 Ocean Health"
    ]
)

# =========================
# TAB 1
# =========================
with tab1:
    fig = px.line(
        df,
        x="time",
        y=parameter,
        title=f"Time Series {parameter}"
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# TAB 2
# =========================
with tab2:
    st.dataframe(df.describe())

# =========================
# TAB 3
# =========================
with tab3:
    numeric_df = df.select_dtypes(include=np.number)

    corr = numeric_df.corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        title="Correlation Matrix"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# TAB 4
# =========================
with tab4:

    col_a, col_b = st.columns(2)

    with col_a:
        fig_sohi = px.line(
            df,
            x="time",
            y="SOHI",
            title="Ocean Health Index"
        )
        st.plotly_chart(fig_sohi, use_container_width=True)

    with col_b:
        fig_fsi = px.line(
            df,
            x="time",
            y="FSI",
            title="Fisheries Suitability Index"
        )
        st.plotly_chart(fig_fsi, use_container_width=True)

    st.subheader("Kategori Kondisi Laut")

    latest_sohi = df["SOHI"].iloc[-1]
    latest_fsi = df["FSI"].iloc[-1]

    if latest_sohi > 80:
        st.success("Ocean Health: Sangat Baik")
    elif latest_sohi > 60:
        st.info("Ocean Health: Baik")
    elif latest_sohi > 40:
        st.warning("Ocean Health: Sedang")
    else:
        st.error("Ocean Health: Buruk")

    if latest_fsi > 80:
        st.success("Fisheries Potential: Sangat Potensial")
    elif latest_fsi > 60:
        st.info("Fisheries Potential: Potensial")
    elif latest_fsi > 40:
        st.warning("Fisheries Potential: Cukup Potensial")
    else:
        st.error("Fisheries Potential: Rendah")
