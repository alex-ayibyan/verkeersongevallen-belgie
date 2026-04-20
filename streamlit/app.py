from pathlib import Path
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
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Achtergrond */
    .stApp { background-color: #0f1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1d27; }

    /* Header */
    .hero {
        background: linear-gradient(135deg, #1a1d27 0%, #12151f 100%);
        border: 1px solid #2a2d3a;
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
    }
    .hero h1 { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0 0 0.3rem 0; }
    .hero p  { color: #7a8099; margin: 0; font-size: 0.9rem; }

    /* KPI kaarten */
    .kpi-card {
        background: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .kpi-label { font-size: 0.78rem; color: #7a8099; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem; }
    .kpi-value { font-size: 1.9rem; font-weight: 700; color: #4f8ef7; }
    .kpi-value.red   { color: #e05c5c; }
    .kpi-value.green { color: #4caf82; }

    /* Sectietitels */
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #c0c8e0;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #2a2d3a;
    }

    /* Divider */
    hr { border-color: #2a2d3a !important; }

    /* Verberg Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "ongevallen_cleaned.parquet"

@st.cache_data
def load_data():
    df = pd.read_parquet(DATA_PATH)
    df = df[(df['x'] > 20000) & (df['x'] < 300000) &
            (df['y'] > 20000) & (df['y'] < 270000)]
    # DT_TIME is het uur rechtstreeks (0-23)
    df['hour'] = pd.to_numeric(df['DT_TIME'], errors='coerce')

    transformer = Transformer.from_crs("EPSG:31370", "EPSG:4326", always_xy=True)
    coords = df[['x', 'y']].dropna()
    lon, lat = transformer.transform(coords['x'].values, coords['y'].values)
    df.loc[coords.index, 'lat'] = lat
    df.loc[coords.index, 'lon'] = lon
    return df

with st.spinner("Data laden..."):
    df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Filters")
    st.markdown("---")

    jaren = sorted(df['jaar'].unique())
    geselecteerde_jaren = st.multiselect("Jaar", jaren, default=jaren)

    provincies = sorted([p for p in df['provincie'].unique() if p != 'Onbekend'])
    geselecteerde_provincies = st.multiselect("Provincie", provincies, default=provincies)

    wegtypes = sorted(df['wegtype'].dropna().unique())
    geselecteerde_wegtypes = st.multiselect("Wegtype", wegtypes, default=wegtypes)

    ernst_opties = sorted(df['ernst'].dropna().unique())
    geselecteerde_ernst = st.multiselect("Ernst", ernst_opties, default=ernst_opties)

    st.markdown("---")
    kaart_type = st.radio("Kaartweergave", ["Heatmap", "Clusters"])

# ── Filter ────────────────────────────────────────────────────────────────────

gefilterd = df[
    df['jaar'].isin(geselecteerde_jaren) &
    df['provincie'].isin(geselecteerde_provincies + ['Onbekend']) &
    df['wegtype'].isin(geselecteerde_wegtypes) &
    df['ernst'].isin(geselecteerde_ernst)
]

dodelijk = gefilterd[gefilterd['ernst'].str.contains('dod', case=False, na=False)]

# ── Hero ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>Verkeersongevallen in België</h1>
    <p>Analyse van 289.532 verkeersongevallen · 2017–2024 · Bron: Statbel</p>
</div>
""", unsafe_allow_html=True)

# ── KPI's ─────────────────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Totaal ongevallen</div>
        <div class="kpi-value">{len(gefilterd):,}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Dodelijke ongevallen</div>
        <div class="kpi-value red">{len(dodelijk):,}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    pct = round(len(dodelijk) / len(gefilterd) * 100, 2) if len(gefilterd) > 0 else 0
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">% Dodelijk</div>
        <div class="kpi-value red">{pct}%</div>
    </div>""", unsafe_allow_html=True)

with c4:
    piekuur = int(gefilterd['hour'].dropna().mode()[0]) if len(gefilterd) > 0 else "-"
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Piekuur</div>
        <div class="kpi-value">{piekuur}u</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Kaart van de ongevallen</div>", unsafe_allow_html=True)

# ── Kaart ─────────────────────────────────────────────────────────────────────

kaart_data = gefilterd[['lat', 'lon', 'ernst', 'provincie', 'jaar']].dropna(subset=['lat', 'lon'])

m = folium.Map(
    location=[50.5, 4.4],
    zoom_start=8,
    tiles="CartoDB dark_matter"
)

ernst_kleuren = {
    'met lichtgewonden': '#f5a623',
    'met zwaargewonden': '#e05c5c',
    'Met doden':         '#c0392b',
    'dodelijk gewonden': '#c0392b',
}

if kaart_type == "Heatmap":
    heat_data = kaart_data[['lat', 'lon']].values.tolist()
    HeatMap(heat_data, radius=7, blur=12, min_opacity=0.4,
            gradient={0.4: '#4f8ef7', 0.65: '#f5a623', 1: '#e05c5c'}).add_to(m)
else:
    cluster = MarkerCluster(
        options={"maxClusterRadius": 40, "disableClusteringAtZoom": 13}
    ).add_to(m)
    sample = kaart_data.sample(min(5000, len(kaart_data)), random_state=42)
    for _, row in sample.iterrows():
        kleur = ernst_kleuren.get(row['ernst'], '#4f8ef7')
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=4,
            color=kleur,
            fill=True,
            fill_color=kleur,
            fill_opacity=0.8,
            weight=0,
            popup=folium.Popup(
                f"<b>{row['ernst']}</b><br>{row['provincie']}<br>{int(row['jaar'])}",
                max_width=200
            )
        ).add_to(cluster)

st_folium(m, width="100%", height=480, returned_objects=[])

st.markdown("<div class='section-title'>Analyse</div>", unsafe_allow_html=True)

# ── Grafieken ─────────────────────────────────────────────────────────────────

DARK_BG   = "#1a1d27"
GRID_COL  = "#2a2d3a"
TEXT_COL  = "#c0c8e0"
BLUE      = "#4f8ef7"
RED       = "#e05c5c"

def dark_fig(figsize=(6, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=TEXT_COL)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    ax.title.set_color(TEXT_COL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(color=GRID_COL, linewidth=0.5)
    return fig, ax

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("<div style='color:#c0c8e0;font-weight:600;margin-bottom:0.5rem'>Ongevallen per jaar</div>", unsafe_allow_html=True)
    per_jaar = gefilterd['jaar'].value_counts().sort_index()
    fig, ax = dark_fig()
    x_pos = range(len(per_jaar))
    bars = ax.bar(x_pos, per_jaar.values, color=BLUE, width=0.5, edgecolor='none')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(per_jaar.index)
    ax.bar_label(bars, fmt=lambda x: f'{int(x):,}', color=TEXT_COL, fontsize=8, padding=3)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

with col_b:
    st.markdown("<div style='color:#c0c8e0;font-weight:600;margin-bottom:0.5rem'>Provincie</div>", unsafe_allow_html=True)
    per_prov = gefilterd[gefilterd['provincie'] != 'Onbekend']['provincie'].value_counts()
    per_prov.index = per_prov.index.str.replace('Provincie ', '', regex=False)
    fig, ax = dark_fig()
    colors = [RED if i == 0 else BLUE for i in range(len(per_prov))]
    per_prov.sort_values().plot(kind='barh', ax=ax, color=colors[::-1], edgecolor='none')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

col_c, col_d = st.columns(2)

with col_c:
    st.markdown("<div style='color:#c0c8e0;font-weight:600;margin-bottom:0.5rem'>Ernst van de ongevallen</div>", unsafe_allow_html=True)
    per_ernst = gefilterd['ernst'].value_counts()
    fig, ax = dark_fig()
    kleuren = ['#4f8ef7', '#f5a623', '#e05c5c', '#c0392b']
    wedges, texts, autotexts = ax.pie(
        per_ernst.values,
        labels=None,
        autopct=None,
        colors=kleuren[:len(per_ernst)],
        startangle=90,
        wedgeprops=dict(width=0.6)
    )
    totaal = per_ernst.values.sum()
    labels_pct = [f"{lbl}  {v/totaal*100:.1f}%" for lbl, v in zip(per_ernst.index, per_ernst.values)]
    ax.legend(wedges, labels_pct, loc='lower center',
              bbox_to_anchor=(0.5, -0.2), ncol=1,
              fontsize=8, frameon=False,
              labelcolor=TEXT_COL)
    plt.tight_layout()
    st.pyplot(fig)

with col_d:
    st.markdown("<div style='color:#c0c8e0;font-weight:600;margin-bottom:0.5rem'>Piekuren</div>", unsafe_allow_html=True)
    per_uur = gefilterd['hour'].dropna().astype(int).value_counts().sort_index()
    fig, ax = dark_fig()
    ax.plot(per_uur.index, per_uur.values, color=BLUE, linewidth=2.5, zorder=3)
    ax.fill_between(per_uur.index, per_uur.values, alpha=0.15, color=BLUE)
    ax.set_xlabel('Uur van de dag')
    ax.set_xticks(range(0, 24, 2))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#4a4f66;font-size:0.8rem'>"
    "Data: Statbel · Verkeersongevallen België 2017–2024</p>",
    unsafe_allow_html=True
)
