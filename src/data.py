"""Carga de los datos originales de videos en tendencia de YouTube (EE. UU.)."""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "reports" / "figures"


def load_categories(path: Path = RAW_DIR / "US_category_id.json") -> pd.DataFrame:
    """Lee el JSON de categorías y lo devuelve como tabla (category_id, category, assignable)."""
    with open(path, encoding="utf-8") as f:
        items = json.load(f)["items"]
    return pd.DataFrame(
        {
            "category_id": [int(i["id"]) for i in items],
            "category": [i["snippet"]["title"] for i in items],
            "assignable": [i["snippet"]["assignable"] for i in items],
        }
    )


def load_videos(path: Path = RAW_DIR / "USvideos.csv") -> pd.DataFrame:
    """Lee el CSV original con fechas ya convertidas. No elimina ni corrige filas."""
    df = pd.read_csv(path)
    df["trending_date"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m")
    df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
    return df


def load_raw() -> pd.DataFrame:
    """Videos con el nombre de su categoría (cruce CSV + JSON)."""
    videos = load_videos()
    categories = load_categories()[["category_id", "category"]]
    return videos.merge(categories, on="category_id", how="left", validate="m:1")
