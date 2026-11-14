"""Limpieza de los datos diarios y construcción del dataset a nivel de video.

Cada función implementa una de las decisiones tomadas en el notebook 01.
"""

import numpy as np
import pandas as pd

METRICS = ["views", "likes", "dislikes", "comment_count"]
US_TIMEZONE = "US/Eastern"
OLD_VIDEO_DAYS = 30
DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


# ---------------------------------------------------------------- nivel diario


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Deja una fila por video y día. Si hay varias, conserva la de más vistas (la más reciente)."""
    df = df.drop_duplicates()
    df = df.sort_values(["video_id", "trending_date", "views"])
    return df.drop_duplicates(["video_id", "trending_date"], keep="last").reset_index(drop=True)


def drop_removed_videos(df: pd.DataFrame) -> pd.DataFrame:
    """Excluye por completo los videos que alguna vez aparecen como retirados o con error."""
    removed = df.loc[df["video_error_or_removed"], "video_id"].unique()
    return df[~df["video_id"].isin(removed)].reset_index(drop=True)


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """Etiquetas '[none]' y descripciones nulas pasan a texto vacío."""
    df = df.copy()
    df["tags"] = df["tags"].replace("[none]", "")
    df["description"] = df["description"].fillna("")
    return df


def mask_disabled_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Likes, dislikes y comentarios pasan a faltante cuando el canal desactivó esa función."""
    df = df.copy()
    for col in ["likes", "dislikes"]:
        df[col] = df[col].astype("float").mask(df["ratings_disabled"])
    df["comment_count"] = df["comment_count"].astype("float").mask(df["comments_disabled"])
    return df


def clean_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica toda la limpieza a nivel de fila (video y día)."""
    return (
        df.pipe(drop_duplicates)
        .pipe(drop_removed_videos)
        .pipe(clean_text)
        .pipe(mask_disabled_metrics)
    )


# ---------------------------------------------------------------- nivel video


def missing_days(daily: pd.DataFrame) -> pd.DatetimeIndex:
    """Días del periodo para los que no hay ninguna fila."""
    calendar = pd.date_range(daily["trending_date"].min(), daily["trending_date"].max())
    return calendar.difference(daily["trending_date"].unique())


def build_video_table(daily: pd.DataFrame) -> pd.DataFrame:
    """Una fila por video: atributos del primer día, métricas del primer y último día."""
    ordered = daily.sort_values(["video_id", "trending_date"])
    grouped = ordered.groupby("video_id")

    attributes = [
        "title", "channel_title", "category_id", "category", "publish_time", "tags",
        "description", "comments_disabled", "ratings_disabled",
    ]
    videos = grouped[attributes].first()

    first = grouped[METRICS].first().add_suffix("_first")
    last = grouped[METRICS].last().add_suffix("_last")
    dates = grouped["trending_date"].agg(
        first_trending_date="min", last_trending_date="max", days_trending="nunique"
    )
    videos = videos.join([dates, first, last])

    # Días entre la publicación y la primera aparición en tendencia.
    publish_date = videos["publish_time"].dt.tz_localize(None).dt.normalize()
    videos["days_to_trending"] = (videos["first_trending_date"] - publish_date).dt.days
    videos["is_old_video"] = videos["days_to_trending"] > OLD_VIDEO_DAYS

    # Videos cuya duración en tendencia no se observa completa.
    start, end = daily["trending_date"].min(), daily["trending_date"].max()
    gaps = missing_days(daily)
    one_day = pd.Timedelta(days=1)
    touches_gap = np.zeros(len(videos), dtype=bool)
    for day in gaps:
        touches_gap |= (
            (videos["first_trending_date"] <= day + one_day)
            & (videos["last_trending_date"] >= day - one_day)
        ).to_numpy()
    videos["duration_incomplete"] = (
        (videos["first_trending_date"] == start)
        | (videos["last_trending_date"] == end)
        | touches_gap
    )
    return videos.reset_index()


# ---------------------------------------------------------------- variables


def add_publish_features(videos: pd.DataFrame) -> pd.DataFrame:
    """Momento de publicación en hora del este de EE. UU."""
    videos = videos.copy()
    local = videos["publish_time"].dt.tz_convert(US_TIMEZONE)
    videos["publish_hour"] = local.dt.hour
    videos["publish_dow"] = local.dt.dayofweek
    videos["publish_day_name"] = pd.Categorical(
        local.dt.dayofweek.map(dict(enumerate(DAY_NAMES))), categories=DAY_NAMES, ordered=True
    )
    videos["publish_month"] = local.dt.month
    videos["publish_is_weekend"] = local.dt.dayofweek >= 5
    return videos


def add_text_features(videos: pd.DataFrame) -> pd.DataFrame:
    """Variables simples derivadas de título, etiquetas y descripción."""
    videos = videos.copy()
    title = videos["title"]
    letters = title.str.count(r"[A-Za-z]")
    videos["title_length"] = title.str.len()
    videos["title_words"] = title.str.split().str.len()
    videos["title_upper_ratio"] = (title.str.count(r"[A-Z]") / letters.where(letters > 0)).fillna(0)
    videos["title_has_exclamation"] = title.str.contains("!", regex=False)
    videos["title_has_question"] = title.str.contains("?", regex=False)
    videos["title_has_digit"] = title.str.contains(r"\d")

    videos["n_tags"] = videos["tags"].apply(lambda t: len(t.split("|")) if t else 0)
    videos["description_length"] = videos["description"].str.len()
    videos["description_links"] = videos["description"].str.count(r"https?://")
    return videos


def add_engagement_features(videos: pd.DataFrame) -> pd.DataFrame:
    """Tasas de interacción al último día en tendencia y métricas en logaritmo."""
    videos = videos.copy()
    views = videos["views_last"]
    videos["like_rate"] = videos["likes_last"] / views
    videos["comment_rate"] = videos["comment_count_last"] / views
    ratings = videos["likes_last"] + videos["dislikes_last"]
    videos["dislike_share"] = videos["dislikes_last"] / ratings.where(ratings > 0)
    videos["views_growth"] = videos["views_last"] / videos["views_first"]

    for metric in METRICS:
        for moment in ("first", "last"):
            videos[f"log_{metric}_{moment}"] = np.log1p(videos[f"{metric}_{moment}"])
    return videos


def add_channel_features(videos: pd.DataFrame) -> pd.DataFrame:
    """Número de videos en tendencia del mismo canal dentro del periodo.

    Es una variable descriptiva. En un modelo predictivo debe recalcularse solo con
    los datos de entrenamiento para no filtrar información del futuro.
    """
    videos = videos.copy()
    videos["channel_videos"] = videos.groupby("channel_title")["video_id"].transform("count")
    return videos


def add_features(videos: pd.DataFrame) -> pd.DataFrame:
    return (
        videos.pipe(add_publish_features)
        .pipe(add_text_features)
        .pipe(add_engagement_features)
        .pipe(add_channel_features)
    )
