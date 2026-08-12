# Global Energy, Development & Inequality — Interactive World Map

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Folium](https://img.shields.io/badge/Folium-Leaflet-77B829)](https://python-visualization.github.io/folium/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive world map that explores how **energy use, human development, CO₂ emissions
and inequality** relate across countries — inspired by Scott Tinker's *"An Honest & Sensible
Conversation about Global Energy"*, but driven purely by open data.

**▶ Live demo:** https://marielnr.github.io/Planet-Energy-Impact-Dashboard/

> Hover any country for a full indicator card; use the layer control (top-right) to switch
> between indicators and between the *Day* (light) and *Night* (dark) base maps.

---

## What it shows

For each country in a chosen year, the map exposes:

| Indicator | Source |
| :-- | :-- |
| Energy use per capita | Our World in Data (OWID) — energy |
| GDP per capita (PPP) | World Bank / OWID |
| Life expectancy (total, female, male) | OWID + World Bank |
| CO₂ emissions per capita | OWID — CO₂ |
| Electricity access (% of population) | World Bank |
| Gini coefficient | OWID |
| Night-time lights (economic-activity proxy) | NASA/NOAA VIIRS |

Everything is keyed on **ISO-3166 alpha-3 country codes**, which is what makes the merge
across seven differently-formatted sources reliable (the earlier version relied on a
hand-maintained country-name mapping).

## How it's built

```
data/*.csv ──▶ build_dataset.py ──▶ final_data.csv ──▶ build_map.py ──▶ index.html
   (raw)          (merge on iso3+year)   (tidy)            (Folium)      (the map)
```

## Reproduce it

```bash
pip install -r requirements.txt
python build_dataset.py     # merge the raw sources  → final_data.csv
python build_map.py         # render the map         → index.html
# open index.html in a browser, or:
python build_map.py --year 2015 --out map_2015.html   # any key year
```

Key years with broad cross-source coverage: **2001, 2005, 2010, 2015, 2020**
(VIIRS night-lights begin in 2012, so they populate 2015 and 2020).

## Repository structure

```text
.
├── build_dataset.py      # merge raw sources → final_data.csv (pandas only)
├── build_map.py          # final_data.csv + geometry → index.html (Folium)
├── final_data.csv        # tidy country-year output (1,450 rows, 290 countries)
├── index.html            # the interactive map (also the GitHub Pages site)
├── data/
│   ├── owid-energy-data.csv, owid-co2-data.csv
│   ├── life-expectancy.csv, gdp-per-capita-worldbank.csv
│   ├── economic-inequality-gini-index.csv
│   ├── API_acceso_electricidad.csv           (World Bank, wide format)
│   ├── API_SP.DYN.LE00.{FE,MA}.IN_*.csv       (life expectancy by sex)
│   ├── viirs-nighttime-lights-country.csv
│   └── world-countries.json                   (ISO-3 keyed geometry, vendored)
├── requirements.txt
└── LICENSE
```

## Notes & limitations

- Data sources are committed as a **fixed snapshot** so the map is reproducible; refresh
  the CSVs from the providers to update it.
- The by-source electricity **generation/capacity** breakdown (Ember) is out of scope for
  this snapshot — the indicators above are what the committed data supports.

## Author

**Mariel Nava Rodríguez** — released under the [MIT License](LICENSE).
