"""Render the interactive world map (``interactive_map.html``).

Reads ``final_data.csv`` (see ``build_dataset.py``) and the vendored world
geometry ``data/world-countries.json`` (features keyed by ISO-3 ``id``), then
builds a Folium map with:

* Day (light) and Night (dark) base layers.
* One toggleable choropleth per indicator (energy, GDP, life expectancy,
  CO2 per capita, electricity access) -- switch them from the layer control.
* A hover tooltip showing every indicator for the country under the cursor.

Usage
-----
    python build_dataset.py     # once, to produce final_data.csv
    python build_map.py                 # -> interactive_map.html (year 2020)
    python build_map.py --year 2015 --out map_2015.html
"""
from __future__ import annotations

import argparse
import json

import folium
import pandas as pd

WORLD = "data/world-countries.json"

# (column, human label, colour ramp, value formatter)
METRICS = [
    ("energy_per_capita", "Energy use per capita (kWh)", "YlOrRd", "{:,.0f}"),
    ("gdp_per_capita", "GDP per capita (PPP, $)", "Greens", "{:,.0f}"),
    ("life_expectancy", "Life expectancy (years)", "PuBu", "{:.1f}"),
    ("co2_per_capita", "CO₂ per capita (t)", "OrRd", "{:.2f}"),
    ("electricity_access_pct", "Electricity access (%)", "BuGn", "{:.1f}"),
]
TOOLTIP_FIELDS = [
    ("life_expectancy", "Life expectancy (yr)", "{:.1f}"),
    ("life_exp_female", "  - female (yr)", "{:.1f}"),
    ("life_exp_male", "  - male (yr)", "{:.1f}"),
    ("gdp_per_capita", "GDP/capita (PPP $)", "{:,.0f}"),
    ("energy_per_capita", "Energy/capita (kWh)", "{:,.0f}"),
    ("electricity_access_pct", "Electricity access (%)", "{:.1f}"),
    ("co2_per_capita", "CO2/capita (t)", "{:.2f}"),
    ("gini", "Gini", "{:.1f}"),
    ("night_lights", "Night-lights index", "{:,.0f}"),
]


def _fmt(value, spec: str) -> str:
    if pd.isna(value):
        return "n/a"
    try:
        return spec.format(value)
    except (ValueError, TypeError):
        return str(value)


def build_map(year: int, out: str) -> None:
    df = pd.read_csv("final_data.csv")
    df = df[df["year"] == year].copy()
    with open(WORLD, encoding="utf-8") as fh:
        world = json.load(fh)

    by_iso = df.set_index("iso3").to_dict("index")

    # Enrich each geometry with formatted indicator strings for the tooltip.
    for feat in world["features"]:
        row = by_iso.get(feat["id"], {})
        props = feat["properties"]
        for col, _label, spec in TOOLTIP_FIELDS:
            props[col] = _fmt(row.get(col), spec)

    m = folium.Map(location=[20, 0], zoom_start=2, tiles=None,
                   world_copy_jump=True, min_zoom=2)
    folium.TileLayer("cartodbpositron", name="Day (light)").add_to(m)
    folium.TileLayer("cartodbdark_matter", name="Night (dark)").add_to(m)

    for i, (col, label, ramp, _spec) in enumerate(METRICS):
        folium.Choropleth(
            geo_data=world, data=df, columns=["iso3", col], key_on="feature.id",
            fill_color=ramp, nan_fill_color="#33333322", nan_fill_opacity=0.3,
            fill_opacity=0.8, line_opacity=0.3, legend_name=f"{label} — {year}",
            name=label, show=(i == 0), highlight=True,
        ).add_to(m)

    # Transparent overlay carrying the hover tooltip over every country.
    folium.GeoJson(
        world, name="Country details (hover)",
        style_function=lambda _f: {"fillColor": "#00000000", "color": "#00000000", "weight": 0},
        highlight_function=lambda _f: {"weight": 1.5, "color": "#222"},
        tooltip=folium.GeoJsonTooltip(
            fields=["name"] + [c for c, _l, _s in TOOLTIP_FIELDS],
            aliases=[f"{year} —"] + [l for _c, l, _s in TOOLTIP_FIELDS],
            sticky=True, localize=True,
        ),
    ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    title = (f'<div style="position:fixed;top:10px;left:50px;z-index:9999;'
             f'background:rgba(255,255,255,.85);padding:6px 12px;border-radius:6px;'
             f'font-family:sans-serif;font-size:14px;">'
             f'<b>Global Energy, Development &amp; Inequality — {year}</b><br>'
             f'<span style="font-size:11px">Hover a country for details · toggle indicators, right</span></div>')
    m.get_root().html.add_child(folium.Element(title))
    m.save(out)
    n = df["iso3"].nunique()
    print(f"Wrote {out} for {year} ({n} countries with data, {len(METRICS)} indicators).")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year", type=int, default=2020)
    p.add_argument("--out", default="index.html")
    args = p.parse_args(argv)
    build_map(args.year, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
