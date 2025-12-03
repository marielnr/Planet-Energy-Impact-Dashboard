# Global Energy, Development, and Inequality (2001–2024)

### Interactive Visualization Inspired by “An Honest & Sensible Conversation about Global Energy” – Scott Tinker

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-000000?style=for-the-badge&logoColor=white)](https://geopandas.org/)
[![Folium](https://img.shields.io/badge/Folium-000000?style=for-the-badge&logoColor=white)](https://python-visualization.github.io/folium/quickstart.html)

---

## Project Description

This project features an **interactive world map** that explores the complex relationships between **per capita energy consumption**, **human development** (life expectancy, GDP per capita), **inequality** (Gini coefficient), gender perspectives, $\text{CO}_2$ emissions, and the **energy transition** (renewables vs. fossils) from 2001 to 2024.

Inspired by Scott Tinker's 2022 talk, this visualization is updated to 2024, enriched with new variables (gender-disaggregated data, Gini, $\text{CO}_2$), and remains bias-free: driven purely by data.

## Key Features

* Over **80 variables** per country and year.
* **6 key years:** 2001 • 2005 • 2010 • 2015 • 2020 • 2024.
* **VIIRS nighttime lights** (NASA/NOAA) as a proxy for nighttime economic activity.
* Life expectancy **disaggregated by gender** (World Bank).
* Gini coefficient (OWID).
* Total and per capita $\text{CO}_2$ emissions (OWID).
* Capacity and generation by source (coal, gas, hydro, solar, wind, nuclear, bioenergy…).
* Map with Day/Night layers (OpenStreetMap + CartoDB Dark Matter).
* **Interactive tooltip** with all key indicators.

**Live demo (once deployed):**
→ `https://your-username.github.io/your-repo/interactive_map.html`

## Data Sources (All Updated to 2024)

| Source | Main Variables | Last Update |
| :--- | :--- | :--- |
| Our World in Data (OWID) | Energy, $\text{CO}_2$, Gini, renewables, GDP per capita | 2024 |
| World Bank | Electricity access, life expectancy by gender | 2023-2024 |
| Ember | Detailed electricity capacity and generation data | 2024 |
| NASA/NOAA VIIRS | Nighttime lights (`nlsum`) | 2024 |
| Natural Earth | Country geometries (110m) | – |

## Repository Structure

```text
.
├── data/
│   ├── raw/               ← Original CSVs (not uploaded due to size)
│   └── processed/
│       ├── data.geojson   ← Final file for the map
│       └── final_data.xlsx
├── notebooks/
│   └── 01_preprocessing.ipynb   ← Full code for merging and cleaning
├── interactive_map.html         ← Final visualization (open in browser!)
├── requirements.txt
└── README.md
