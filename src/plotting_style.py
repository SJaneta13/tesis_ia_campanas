# src/plotting_style.py
from __future__ import annotations
from pathlib import Path
import re
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# ---------- 1) Estilo tipo paper ----------
def set_paper_style():
    """
    Estilo sobrio tipo Nature/IEEE:
    - fuente sans (compatible Word)
    - líneas finas
    - ticks discretos
    """
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",   # alternativa: "Arial" si la tienes instalada
        "font.size": 9,
        "axes.titlesize": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.linewidth": 0.8,
        "grid.linewidth": 0.6,
        "lines.linewidth": 1.2,
        "savefig.dpi": 300,
        "figure.dpi": 120,
        "figure.constrained_layout.use": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

# ---------- 2) Guardado en alta calidad ----------
def save_figure(fig, out_base: Path, *,
                dpi: int = 600,
                save_png: bool = True,
                save_pdf: bool = True,
                save_svg: bool = True,
                transparent: bool = False):
    """
    out_base: Path sin extensión (ej: figures/cm_random_forest)
    Genera: PNG (raster), PDF/SVG (vector)
    """
    out_base.parent.mkdir(parents=True, exist_ok=True)

    if save_pdf:
        fig.savefig(str(out_base.with_suffix(".pdf")), bbox_inches="tight", transparent=transparent)
    if save_svg:
        fig.savefig(str(out_base.with_suffix(".svg")), bbox_inches="tight", transparent=transparent)
    if save_png:
        fig.savefig(str(out_base.with_suffix(".png")), bbox_inches="tight", dpi=dpi, transparent=transparent)

# ---------- 3) Utilidades de texto ----------
def shorten(text: str, max_len: int = 42) -> str:
    text = str(text)
    return text if len(text) <= max_len else text[:max_len-1] + "…"

def prettify_feature_name(name: str, mapping: dict[str, str] | None = None) -> str:
    """
    Convierte nombres feos a nombres de paper:
    - aplica mapping manual si existe
    - limpia prefijos de OneHot (col=valor)
    - reemplaza '_' por espacios
    """
    s = str(name)

    if mapping and s in mapping:
        s = mapping[s]

    # OneHotEncoder suele dar "col_val" o "col=val" según versión.
    s = s.replace("=", ": ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("_", " ")

    # Limpieza de tokens frecuentes
    s = s.replace("¿", "").replace("?", "")
    s = s.replace("  ", " ")

    return s