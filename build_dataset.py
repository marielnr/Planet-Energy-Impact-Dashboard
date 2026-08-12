"""Build the merged country-year dataset for the Global Energy & Development map.

All raw sources live in ``data/`` and are joined on **ISO-3166 alpha-3 country
codes** (``iso3``) plus ``year`` -- a far more robust key than country names.
The original one-off script used absolute Windows paths and a hand-maintained
name-mapping table; this version is portable and reproducible.

Output: ``final_data.csv`` (one row per country-year) in the repo root.

Key years: 2001, 2005, 2010, 2015, 2020 (the years with broad cross-source
coverage; VIIRS night-lights only begin in 2012, so they populate 2015/2020).
"""
from __future__ import annotations

import os

import pandas as pd

DATA = "data"
KEY_YEARS = [2001, 2005, 2010, 2015, 2020]


def _wb_wide_to_long(path: str, value_name: str) -> pd.DataFrame:
    """Melt a World Bank wide CSV (Country Code + year columns) to long form."""
    df = pd.read_csv(path)
    id_cols = ["Country Name", "Country Code", "Indicator Name", "Indicator Code"]
    year_cols = [c for c in df.columns if c.strip().isdigit()]
    long = df.melt(id_vars=[c for c in id_cols if c in df.columns],
                   value_vars=year_cols, var_name="year", value_name=value_name)
    long["year"] = pd.to_numeric(long["year"], errors="coerce").astype("Int64")
    long = long.rename(columns={"Country Code": "iso3"})
    return long[["iso3", "year", value_name]].dropna(subset=["iso3"])


def load_energy() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA}/owid-energy-data.csv",
                     usecols=["iso_code", "year", "energy_per_capita"])
    return df.rename(columns={"iso_code": "iso3", "energy_per_capita": "energy_per_capita"})


def load_co2() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA}/owid-co2-data.csv",
                     usecols=["iso_code", "year", "co2", "co2_per_capita"])
    return df.rename(columns={"iso_code": "iso3"})


def load_owid_entity(path: str, value_col: str, out: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={"Code": "iso3", "Year": "year", value_col: out})
    return df[["iso3", "year", out]]


def load_nightlights() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA}/viirs-nighttime-lights-country.csv")
    # Monthly nlsum -> a representative yearly value (mean across months).
    yearly = df.groupby(["iso", "year"], as_index=False)["nlsum"].mean()
    return yearly.rename(columns={"iso": "iso3", "nlsum": "night_lights"})


def build() -> pd.DataFrame:
    frames = {
        "energy_per_capita": load_energy(),
        "co2": load_co2(),
        "life_expectancy": load_owid_entity(
            f"{DATA}/life-expectancy.csv", "Period life expectancy at birth",
            "life_expectancy"),
        "gdp_per_capita": load_owid_entity(
            f"{DATA}/gdp-per-capita-worldbank.csv",
            "GDP per capita, PPP (constant 2021 international $)", "gdp_per_capita"),
        "gini": load_owid_entity(
            f"{DATA}/economic-inequality-gini-index.csv",
            "Gini coefficient (2021 prices)", "gini"),
        "night_lights": load_nightlights(),
        "electricity_access": _wb_wide_to_long(
            f"{DATA}/API_acceso_electricidad.csv", "electricity_access_pct"),
        "life_exp_female": _wb_wide_to_long(
            f"{DATA}/API_SP.DYN.LE00.FE.IN_DS2_en_csv_v2_8069.csv", "life_exp_female"),
        "life_exp_male": _wb_wide_to_long(
            f"{DATA}/API_SP.DYN.LE00.MA.IN_DS2_en_csv_v2_126205.csv", "life_exp_male"),
    }

    merged = None
    for name, df in frames.items():
        df = df.dropna(subset=["iso3"])
        df = df[df["iso3"].astype(str).str.len() == 3]           # drop OWID region rows
        df = df[df["year"].isin(KEY_YEARS)]
        df = df.groupby(["iso3", "year"], as_index=False).first()  # de-duplicate
        merged = df if merged is None else merged.merge(df, on=["iso3", "year"], how="outer")

    return merged.sort_values(["iso3", "year"]).reset_index(drop=True)


def main() -> int:
    if not os.path.isdir(DATA):
        print(f"'{DATA}/' not found -- run from the repo root.")
        return 1
    df = build()
    df.to_csv("final_data.csv", index=False)
    print(f"Wrote final_data.csv: {len(df):,} country-year rows, "
          f"{df['iso3'].nunique()} countries, years {sorted(df['year'].dropna().unique())}")
    print("Non-null coverage by column:")
    print((df.notna().mean() * 100).round(1).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
