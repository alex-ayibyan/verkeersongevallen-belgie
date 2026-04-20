# Verkeersongevallen in België — Data Analyse

End-to-end data project op basis van officiële Statbel-data over verkeersongevallen in België.

## Stack
- **Python** (Pandas, Matplotlib, Seaborn) - data cleaning & exploratory analysis
- **PostgreSQL** - data opslag en SQL analyse
- **Power BI** - interactief dashboard
- **Streamlit** - publieke webapplicatie met interactieve kaart en filters op provincie, jaar en wegtype

## Business vragen
1. Wanneer gebeuren de meeste ongevallen? (uur, dag, maand)
2. Welke provincies en gemeentes zijn het gevaarlijkst?
3. Hoe evolueert het aantal ongevallen over de jaren?
4. Wat zijn de meest voorkomende oorzaken en wegtypen?
5. Welke leeftijdsgroepen zijn het meest betrokken?

## Projectstructuur
```
data/
  raw/          → originele Statbel bestanden
  processed/    → gecleande data klaar voor database
notebooks/      → Jupyter notebooks (EDA)
sql/            → SQL queries per business vraag
powerbi/        → Power BI screenshots en exports
streamlit/      → Streamlit app (app.py)
```

## Data source
Statbel — Verkeersongevallen
https://statbel.fgov.be/nl/open-data/geolocalisatie-van-de-verkeersongevallen-2017-2024
