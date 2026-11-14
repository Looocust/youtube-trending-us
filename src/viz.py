"""Estilo común de los gráficos del proyecto."""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Paleta categórica en orden fijo (no reordenar: el color sigue a la entidad).
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE = PALETTE[0]
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e6e5e1"


def set_style() -> None:
    """Aplica el estilo del proyecto a matplotlib."""
    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "figure.dpi": 110,
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
            "axes.prop_cycle": plt.cycler(color=PALETTE),
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": GRID,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.labelsize": 10,
            "axes.labelcolor": INK_SECONDARY,
            "text.color": INK,
            "xtick.color": INK_SECONDARY,
            "ytick.color": INK_SECONDARY,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "lines.linewidth": 2,
            "legend.frameon": False,
            "font.family": "sans-serif",
        }
    )


def _compact(x, _pos=None) -> str:
    for limit, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(x) >= limit:
            value = x / limit
            return f"{value:.0f}{suffix}" if value == int(value) else f"{value:.1f}{suffix}"
    return f"{x:.0f}"


COMPACT = FuncFormatter(_compact)
