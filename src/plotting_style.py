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
        "font.size": 8,
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
def shorten(text: str, max_len: int = 60) -> str:
    text = str(text)
    if max_len <= 1:
        return text[:max_len]
    return text if len(text) <= max_len else text[:max_len - 1].rstrip() + "…"

def prettify_feature_name(name: str, mapping: dict[str, str] | None = None) -> str:

    s = str(name)

    if mapping and s in mapping:
        return mapping[s]

    # Limpieza base
    s = s.replace("_", " ")
    s = s.replace("¿", "").replace("?", "")
    s = re.sub(r"\s+", " ", s).strip()

    # Casos comunes de variables cortas
    direct_map = {
        "edad": "Edad",
        "genero": "Género",
        "rol uce": "Rol en la UCE",
        "conoce ia": "Conocimiento sobre IA",
        "percibe automatizacion": "Percepción de automatización",
        "identifica ia": "Identificación de contenido IA",
        "longitud recomendacion": "Longitud de recomendación abierta",
        "palabras recomendacion": "Número de palabras en recomendación",
        "confianza idx round": "Confianza electoral (5 niveles)",
        "confianza 3": "Confianza electoral (3 clases)",
        "limpieza num": "Percepción de transparencia electoral",
        "fraude rev": "Percepción inversa de fraude",
    }


    s_lower = s.lower()
    if s_lower in direct_map:
        return direct_map[s_lower]

    # Preguntas largas resumidas
    replacements = [
        (
            "Percepción sobre IA en campañas",
            "Percepción IA campañas"
        ),
        (
            "Cambio de confianza por bots/deepfakes",
            "Cambio confianza bots/deepfakes"
        ),
        (
            "Influencia de IA en decisión de voto",
            "Influencia IA en voto"
        ),
        (
            "Verificación de información antes de compartir",
            "Verificación antes de compartir"
        ),
        (
            "Conocimiento sobre regulación de IA",
            "Conocimiento regulación IA"
        ),
        (
            "Apoyo a regulación de IA en campañas",
            "Apoyo regulación IA"
        ),
        (
            "Dispositivo principal de acceso a internet",
            "Dispositivo de acceso"
        ),
        (
            "Exposición a contenido político falso o IA",
            "Exposición a contenido falso/IA"
        ),
    ]

    for old, new in replacements:
        s = s.replace(old, new)

    # Si viene codificado como "pregunta respuesta"
    # intenta separar en "Pregunta: Respuesta"
    option_tokens = [
        "Sí", "No", "A veces", "Siempre", "Nunca", "Rara vez",
        "No sé", "No sé/no aplica",
        "Sí, lo he notado claramente",
        "Tal vez, pero no estoy seguro/a",
        "Sí, fácilmente",
        "No estoy seguro/a",
        "Sí, ahora confío menos",
        "Sí, ahora confío más",
        "Smartphone", "Computadora",
        "Smartphone;Computadora",
        "Estudiante de pregrado",
        "Estudiante de posgrado",
        "Personal administrativo",
        "Docente",
        "Daniel Noboa",
        "Luisa González",
        "No voté",
        "Prefiero no responder"
    ]

    for tok in option_tokens:
        if s.endswith(" " + tok):
            base = s[: -len(tok)].strip(" :-")
            return f"{base}: {tok}"

    return s



def prettify_and_shorten(name: str, max_len: int = 40, mapping: dict[str, str] | None = None) -> str:    
    s = prettify_feature_name(name, mapping=mapping)
    return shorten(s, max_len=max_len)