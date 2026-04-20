import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
from pyproj import Transformer
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

st.set_page_config(
    page_title="Verkeersongevallen België",
    page_icon="🚗",
    layout="wide"
)

# ── Data laden ────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_csv("../data/processed/ongevallen_cleaned.csv", low_memory=False)

    # Slechte coördinaten filteren (Belgisch Lambert 72 bereik)
    df = df[(df['x'] > 20000) & (df['x'] < 300000) &
            (df['y'] > 20000) & (df['y'] < 270000)]

    # Lambert 72 → WGS84 (lat/lon)
    transformer = Transformer.from_crs("EPSG:31370", "EPSG:4326", always_xy=True)
    coords = df[['x', 'y']].dropna()
    lon, lat = transformer.transform(coords['x'].values, coords['y'].values)
    df.loc[coords.index, 'lat'] = lat
    df.loc[coords.index, 'lon'] = lon

    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────

st.sidebar.title("Filters")

jaren = sorted(df['jaar'].unique())
geselecteerde_jaren = st.sidebar.multiselect(
    "Jaar", jaren, default=jaren
)

provincies = sorted([p for p in df['provincie'].unique() if p != 'Onbekend'])
geselecteerde_provincies = st.sidebar.multiselect(
    "Provincie", provincies, default=provincies
)

wegtypes = sorted(df['wegtype'].dropna().unique())
geselecteerde_wegtypes = st.sidebar.multiselect(
    "Wegtype", wegtypes, default=wegtypes
)

ernst_opties = sorted(df['ernst'].dropna().unique())
geselecteerde_ernst = st.sidebar.multiselect(
    "Ernst", ernst_opties, default=ernst_opties
)

kaart_type = st.sidebar.radio("Kaartweergave", ["Heatmap", "Clusters"])

# ── Data filteren ─────────────────────────────────────────────────────────────

gefilterd = df[
    df['jaar'].isin(geselecteerde_jaren) &
    df['provincie'].isin(geselecteerde_provincies + ['Onbekend']) &
    df['wegtype'].isin(geselecteerde_wegtypes) &
    df['ernst'].isin(geselecteerde_ernst)
]

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🚗 Verkeersongevallen in België 2017–2024")
st.caption("Databron: Statbel — Geolocalisatie van de verkeersongevallen")

# ── KPI's ─────────────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
col1.metric("Totaal ongevallen", f"{len(gefilterd):,}")
col2.metric("Dodelijke ongevallen",
            f"{len(gefilterd[gefilterd['ernst'].str.contains('dod', case=False, na=False)]):,}")
col3.metric("Provincies", len(geselecteerde_provincies))
col4.metric("Jaren", len(geselecteerde_jaren))

st.divider()

# ── Kaart ─────────────────────────────────────────────────────────────────────

st.subheader("Kaart van de ongevallen")

kaart_data = gefilterd[['lat', 'lon', 'ernst', 'provincie', 'jaar']].dropna(subset=['lat', 'lon'])

m = folium.Map(location=[50.5, 4.4], zoom_start=8, tiles="CartoDB positron")

ernst_kleuren = {
    'met lichtgewonden': 'orange',
    'met zwaargewonden': 'red',
    'Met doden':         'darkred',
    'dodelijk gewonden': 'darkred',
}

if kaart_type == "Heatmap":
    heat_data = kaart_data[['lat', 'lon']].values.tolist()
    HeatMap(heat_data, radius=8, blur=10, min_opacity=0.4).add_to(m)
else:
    cluster = MarkerCluster().add_to(m)
    sample = kaart_data.sample(min(5000, len(kaart_data)), random_state=42)
    for _, row in sample.iterrows():
        kleur = ernst_kleuren.get(row['ernst'], 'blue')
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=4,
            color=kleur,
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['ernst']} | {row['provincie']} | {int(row['jaar'])}"
        ).add_to(cluster)

st_folium(m, width="100%", height=500)

st.divider()

# ── Grafieken ─────────────────────────────────────────────────────────────────

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Ongevallen per jaar")
    per_jaar = gefilterd['jaar'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(per_jaar.index, per_jaar.values, color='steelblue')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

with col_b:
    st.subheader("Ongevallen per provincie")
    per_prov = gefilterd[gefilterd['provincie'] != 'Onbekend']['provincie'].value_counts()
    per_prov.index = per_prov.index.str.replace('Provincie ', '')
    fig, ax = plt.subplots(figsize=(6, 4))
    per_prov.sort_values().plot(kind='barh', ax=ax, color='steelblue')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Verdeling ernst")
    per_ernst = gefilterd['ernst'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(per_ernst.values, labels=per_ernst.index, autopct='%1.1f%%',
           colors=['#90CAF9', '#42A5F5', '#1565C0', '#0D2F6E'])
    plt.tight_layout()
    st.pyplot(fig)

with col_d:
    st.subheader("Piekuren")
    per_uur = gefilterd['hour'].dropna().astype(int).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(per_uur.index, per_uur.values, color='steelblue', linewidth=2, marker='o', markersize=3)
    ax.fill_between(per_uur.index, per_uur.values, alpha=0.2, color='steelblue')
    ax.set_xlabel('Uur van de dag')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
