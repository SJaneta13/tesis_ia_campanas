"""
src/04_report_word.py


- Target principal: detecta automáticamente si el run sklearn fue 3 clases (confianza_3) o 5 niveles.
- Modelos principales: Random Forest, SVM-RBF, Ordinal (logit/probit por QWK).
- Incluye baselines si existen.
- Incluye estabilidad por seed.
- Incluye importancia de variables (RF) si existe.
- Incluye proporcional odds (po_check.csv) si existe.
- No depende de archivos “tabla_resumen_tesis.csv” o “metrics_compare_all_models.csv”.

Requisitos:
pip install python-docx
"""

from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from src.plotting_style import prettify_and_shorten


# =========================
# CONFIG
# =========================
RUNS_DIR = Path("outputs") / "runs"
DATA_PATH = Path("data") / "processed" / "encuestas" / "model_ready.csv"

SEEDS_EXPECTED = [0, 7, 13, 21, 42]


# =========================
# Helpers: docx styling
# =========================
def set_cell_shading(cell, color_hex: str):
    tc_pr = cell._element.get_or_add_tcPr()
    shd = tc_pr.makeelement(
        qn("w:shd"),
        {
            qn("w:val"): "clear",
            qn("w:color"): "auto",
            qn("w:fill"): color_hex,
        },
    )
    tc_pr.append(shd)


def add_styled_table(doc, headers, rows, col_widths_cm=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(str(h))
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, "595959")

    # Data rows
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            run.font.size = Pt(9)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if i % 2 == 0:
                set_cell_shading(cell, "F2F2F2")

    # Column widths
    if col_widths_cm:
        for row in table.rows:
            for j, w in enumerate(col_widths_cm):
                row.cells[j].width = Cm(float(w))

    return table


def fmt_num(x, decimals=3):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    try:
        return f"{float(x):.{decimals}f}"
    except Exception:
        return str(x)


def fmt_pm(mean, std, decimals=3):
    if mean is None or (isinstance(mean, float) and np.isnan(mean)):
        return "—"
    if std is None or (isinstance(std, float) and np.isnan(std)):
        return fmt_num(mean, decimals)
    return f"{float(mean):.{decimals}f} ± {float(std):.{decimals}f}"


def safe_read_csv(path: Path, encoding="utf-8-sig"):
    if path.exists():
        return pd.read_csv(path, encoding=encoding)
    return None


def latest_file(dir_path: Path, pattern: str):
    files = sorted(dir_path.glob(pattern))
    return files[-1] if files else None


# =========================
# Locate latest run
# =========================
runs = sorted(RUNS_DIR.glob("run_*"))
if not runs:
    raise FileNotFoundError("No hay runs en outputs/runs.")
RUN_DIR = runs[-1]
RUN_ID = RUN_DIR.name.replace("run_", "")

TABLES_DIR = RUN_DIR / "tables"
FIG_DIR = RUN_DIR / "figures"
ORD_DIR = RUN_DIR / "ordinal"
ORD_FIG_DIR = RUN_DIR / "figures" / "ordinal"

# Load sklearn metrics
sk_run_path = latest_file(TABLES_DIR, "metrics_run_*.csv")
sk_seed_path = latest_file(TABLES_DIR, "metrics_by_seed_*.csv")
df_run = safe_read_csv(sk_run_path) if sk_run_path else None
df_seed = safe_read_csv(sk_seed_path) if sk_seed_path else None

# Load ordinal metrics
ord_run = safe_read_csv(ORD_DIR / "metrics.csv")
ord_seed = safe_read_csv(ORD_DIR / "metrics_by_seed.csv")

# Load optional artifacts
fi_path = latest_file(TABLES_DIR, "rf_feature_importance_*.csv")
fi_df = safe_read_csv(fi_path) if fi_path else None

po_files = sorted(ORD_DIR.glob("po_check_*.csv"))
po_check_path = po_files[-1] if po_files else None
po_df = safe_read_csv(po_check_path) if po_check_path else None

# Model comparison (optional; if exists we will use it)
mc_path_3 = TABLES_DIR / "tabla_modelos_tesis_confianza_3.csv"
mc_path_5 = TABLES_DIR / "tabla_modelos_tesis_confianza_idx_round.csv"

mc_df = safe_read_csv(mc_path_3)
if mc_df is None or mc_df.empty:
    mc_df = safe_read_csv(mc_path_5)
if mc_df is None or mc_df.empty:
    mc_df = safe_read_csv(TABLES_DIR / "model_comparison.csv")


# =========================
# Decide target principal (3 vs 5) based on sklearn run
# =========================
def detect_target_from_run(df_run: pd.DataFrame):
    # Prefer explicit target column if exists
    if df_run is None or df_run.empty or "target" not in df_run.columns:
        return "confianza_3", 3, "ordinal_logit_3clases"  # safe fallback

    targets = set(df_run["target"].astype(str).tolist())
    if "confianza_3" in targets:
        return "confianza_3", 3, "ordinal_logit_3clases"
    if "confianza_idx_round" in targets:
        return "confianza_idx_round", 5, "ordinal_logit_5niveles"

    # fallback: pick first
    t0 = df_run["target"].iloc[0]
    # heuristic
    if "3" in str(t0):
        return str(t0), 3, "ordinal_logit_3clases"
    return str(t0), 5, "ordinal_logit_5niveles"


TARGET_SK, N_CLASSES, TARGET_ORD = detect_target_from_run(df_run)

suffix = "5niveles" if N_CLASSES == 5 else "3clases"
OUT_DOCX = Path("outputs") / f"Resultados_Modelado_Tesis_{suffix}_{RUN_ID}.docx"

# =========================
# Build dataset class distribution (optional)
# =========================
class_rows = None
n_total = None
if DATA_PATH.exists():
    dfd = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    dfd = dfd.dropna(subset=["confianza_idx_round"]).copy()
    dfd["confianza_idx_round"] = dfd["confianza_idx_round"].astype(int)
    n_total = len(dfd)

    if N_CLASSES == 3:
        def to_3(x):
            if x <= 2: return 1
            if x == 3: return 2
            return 3
        dfd["confianza_3"] = dfd["confianza_idx_round"].apply(to_3).astype(int)
        dist = dfd["confianza_3"].value_counts().sort_index()
        labels = {1: "1 — Baja", 2: "2 — Media", 3: "3 — Alta"}
        class_rows = []
        total = int(dist.sum())
        for k in [1, 2, 3]:
            n = int(dist.get(k, 0))
            pct = (n / total * 100) if total else 0.0
            tr = int(round(n * 0.70))
            te = n - tr
            class_rows.append([labels[k], n, f"{pct:.1f}%", tr, te])
        class_rows.append(["Total", total, "100.0%", int(round(total * 0.70)), total - int(round(total * 0.70))])
    else:
        dist = dfd["confianza_idx_round"].value_counts().sort_index()
        class_rows = []
        total = int(dist.sum())
        for k in [1, 2, 3, 4, 5]:
            n = int(dist.get(k, 0))
            pct = (n / total * 100) if total else 0.0
            tr = int(round(n * 0.70))
            te = n - tr
            class_rows.append([str(k), n, f"{pct:.1f}%", tr, te])
        class_rows.append(["Total", total, "100.0%", int(round(total * 0.70)), total - int(round(total * 0.70))])


# =========================
# Build “3 modelos” summary table (from metrics, if model_comparison missing)
# =========================
MODEL_LABELS = {
    "random_forest": "Random Forest",
    "svm_rbf": "SVM-RBF",
    "ordinal_logit": "Reg. Logística Ordinal",
    "baseline_majority": "Baseline Mayoría",
    "baseline_stratified": "Baseline Estratificado",
    "log_reg": "Logistic Regression",
    "hist_gradient_boosting": "HistGradientBoosting",
    "voting_ensemble": "Voting Ensemble",
}

INTERPRETABILITY = {
    "ordinal_logit": "Alta (OR + IC95%)",
    "random_forest": "Media (importancias)",
    "svm_rbf": "Baja (caja negra)",
    "baseline_majority": "—",
    "baseline_stratified": "—",
}

def extract_run_row(df, model, target):
    if df is None or df.empty:
        return None
    sub = df[(df["model"] == model) & (df["target"].astype(str) == str(target))]
    if sub.empty:
        # fallback: try without target match
        sub = df[df["model"] == model]
    return sub.iloc[0].to_dict() if not sub.empty else None


def build_main_model_table():
    # Preferred: use pre-built model_comparison*.csv if present
    if mc_df is not None and not mc_df.empty and "Modelo" in mc_df.columns:
        # Already formatted
        return mc_df.copy()

    rows = []
    # Ordinal from ord_run
    if ord_run is not None and not ord_run.empty:
        sub = ord_run[ord_run["target"].astype(str) == str(TARGET_ORD)]
        if not sub.empty:
            r = sub.iloc[0]
            rows.append({
                "Modelo": "ordinal_logit",
                "Accuracy": fmt_pm(r.get("accuracy_mean"), r.get("accuracy_std")),
                "F1_weighted": fmt_pm(r.get("f1_weighted_mean"), r.get("f1_weighted_std")),
                "QWK": fmt_pm(r.get("kappa_qw_mean"), r.get("kappa_qw_std")),
                "MAE_ordinal": fmt_pm(r.get("mae_ordinal_mean"), r.get("mae_ordinal_std")),
                "AUC_OVR": fmt_pm(r.get("auc_ovr_mean"), r.get("auc_ovr_std")),
                "Tiempo(s)": fmt_pm(r.get("time_seconds_mean"), r.get("time_seconds_std"), decimals=1),
                "Interpretabilidad": INTERPRETABILITY.get("ordinal_logit", "—")
            })

    # RF + SVM from sklearn run
    for m in ["random_forest", "svm_rbf"]:
        r = extract_run_row(df_run, m, TARGET_SK)
        if r:
            rows.append({
                "Modelo": m,
                "Accuracy": fmt_pm(r.get("accuracy_mean"), r.get("accuracy_std")),
                "F1_weighted": fmt_pm(r.get("f1_weighted_mean"), r.get("f1_weighted_std")),
                "QWK": fmt_pm(r.get("kappa_qw_mean"), r.get("kappa_qw_std")),
                "MAE_ordinal": fmt_pm(r.get("mae_ordinal_mean"), r.get("mae_ordinal_std")),
                "AUC_OVR": fmt_pm(r.get("auc_ovr_mean"), r.get("auc_ovr_std")),
                "Tiempo(s)": fmt_pm(r.get("time_seconds_mean"), r.get("time_seconds_std"), decimals=1),
                "Interpretabilidad": INTERPRETABILITY.get(m, "—")
            })

    out = pd.DataFrame(rows)
    if not out.empty:
        # nicer names in Word
        out["Modelo"] = out["Modelo"].map(lambda x: MODEL_LABELS.get(x, x))
    return out


df_main_models = build_main_model_table()


# =========================
# Build report
# =========================
doc = Document()

# Base style
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)

# ---- Cover ----
doc.add_paragraph()
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
t = title.add_run("RESULTADOS DEL MODELADO PREDICTIVO")
t.bold = True
t.font.size = Pt(16)
t.font.color.rgb = RGBColor(0, 0, 0)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
s = sub.add_run("Percepción ciudadana: confianza y uso de IA en campañas políticas digitales")
nota = doc.add_paragraph()
nota.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = nota.add_run(
    "Documento generado automáticamente como anexo técnico del pipeline de análisis reproducible."
)
run.italic = True
run.font.size = Pt(10)
s.font.size = Pt(13)
s.font.color.rgb = RGBColor(0x59, 0x56, 0x59)

doc.add_paragraph()
meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta.add_run("Run ID: ").bold = True
meta.add_run(f"{RUN_ID}\n")
meta.add_run("Fecha: ").bold = True
meta.add_run(datetime.now().strftime("%d/%m/%Y") + "\n")
meta.add_run("Split: ").bold = True
meta.add_run("70% entrenamiento / 30% validación\n")
meta.add_run("Semillas: ").bold = True
meta.add_run(str(SEEDS_EXPECTED) + "\n")
meta.add_run("Target principal: ").bold = True
meta.add_run(f"{TARGET_SK} ({N_CLASSES} clases)\n")
meta.add_run("N total: ").bold = True
meta.add_run(f"{n_total}" if n_total else "—")

doc.add_page_break()

# ---- Methodology ----
doc.add_heading("1. Configuración Metodológica", level=1)
doc.add_paragraph(
    "Se evaluaron modelos supervisados para predecir el nivel de confianza electoral "
    "a partir de variables sociodemográficas y percepciones sobre IA en campañas digitales. "
    "El diseño usa split 70/30 estratificado y evaluación por 5 semillas para estabilidad."
)

doc.add_heading("1.1 Modelos Evaluados", level=2)
p = doc.add_paragraph()
p.add_run("Random Forest: ").bold = True
p.add_run("captura relaciones no lineales e interacciones; reporta importancias de variables.")
p = doc.add_paragraph()
p.add_run("SVM-RBF: ").bold = True
p.add_run("modelo no lineal en alta dimensión; fuerte capacidad predictiva pero menor interpretabilidad.")
p = doc.add_paragraph()
p.add_run("Regresión Logística Ordinal: ").bold = True
p.add_run(
    "modelo de enlace acumulativo. En entrenamiento, una validación cruzada interna (k=5) seleccionó la distribución logit o probit según el mayor valor de Kappa cuadrático ponderado (QWK), en coherencia con la naturaleza ordinal de la escala Likert."
)
doc.add_paragraph()

doc.add_page_break()

# ---- Class distribution ----
doc.add_heading("2. Distribución de Clases", level=1)
if class_rows:
    add_styled_table(
        doc,
        ["Clase", "N Total", "%", "Train (70%)", "Test (30%)"],
        class_rows,
        col_widths_cm=[3.0, 2.2, 2.2, 2.5, 2.5],
    )
    doc.add_paragraph()
    if N_CLASSES == 3:
        doc.add_paragraph(
            "Nota: Baja = niveles 1–2, Media = nivel 3, Alta = niveles 4–5 (escala original de 5 puntos)."
        )
else:
    doc.add_paragraph("No se pudo calcular la distribución de clases desde el dataset.")

doc.add_page_break()

# ---- Main results table ----
doc.add_heading("3. Resultados Comparativos", level=1)
doc.add_paragraph(
    "La tabla resume el rendimiento promedio ± desviación estándar sobre 5 semillas. "
    "Se incluyen métricas ordinales (QWK y MAE) además de métricas clásicas."
)

if df_main_models is not None and not df_main_models.empty:
    rows = []
    for _, r in df_main_models.iterrows():

        rows.append([
            r.get("Modelo", "—"),
            r.get("Exactitud", r.get("Accuracy", "—")),
            r.get("F1 ponderado", r.get("F1_weighted", "—")),
            r.get("Kappa cuadrático ponderado", r.get("QWK", "—")),
            r.get("MAE ordinal", r.get("MAE_ordinal", "—")),
            r.get("AUC OvR", r.get("AUC_OVR", "—")),
            r.get("Tiempo de ejecución (s)", r.get("Tiempo(s)", "—")),
            r.get("Interpretabilidad", "—"),
        ])
    add_styled_table(
        doc,
        ["Modelo", "Exactitud", "F1 ponderado", "QWK", "MAE ordinal", "AUC OvR", "Tiempo (s)", "Interpretabilidad"],
        rows,
        col_widths_cm=[4.2, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 3.2],
    )
else:
    doc.add_paragraph("No se encontraron métricas para construir la tabla comparativa.")

doc.add_page_break()

# ---- Stability by seed (sklearn) ----
doc.add_heading("4. Estabilidad por Semilla (Sklearn)", level=1)
if df_seed is None or df_seed.empty:
    doc.add_paragraph("No se encontró metrics_by_seed_*.csv para este run.")
else:
    for m in ["random_forest", "svm_rbf"]:
        sub = df_seed[(df_seed["model"] == m) & (df_seed["target"].astype(str) == str(TARGET_SK))]
        if sub.empty:
            continue
        doc.add_heading(MODEL_LABELS.get(m, m), level=2)

        seed_rows = []
        for _, r in sub.iterrows():
            seed_rows.append([
                int(r.get("seed", -1)),
                fmt_num(r.get("accuracy")),
                fmt_num(r.get("f1_weighted")),
                fmt_num(r.get("kappa_qw")),
                fmt_num(r.get("auc_ovr")),
                fmt_num(r.get("time_seconds"), 1),
            ])

        # Add mean row from df_run
        rr = None
        if df_run is not None and not df_run.empty:
            rr = df_run[(df_run["model"] == m) & (df_run["target"].astype(str) == str(TARGET_SK))]
            if rr.empty:
                rr = df_run[df_run["model"] == m]
        if rr is not None and not rr.empty:
            r0 = rr.iloc[0]
            seed_rows.append([
                "MEDIA",
                fmt_num(r0.get("accuracy_mean")),
                fmt_num(r0.get("f1_weighted_mean")),
                fmt_num(r0.get("kappa_qw_mean")),
                fmt_num(r0.get("auc_ovr_mean")),
                fmt_num(r0.get("time_seconds_mean"), 1),
            ])

        add_styled_table(
            doc,
            ["Seed", "Acc", "F1-w", "QWK", "AUC", "Tiempo (s)"],
            seed_rows,
            col_widths_cm=[2.0, 2.3, 2.3, 2.3, 2.3, 2.6],
        )
        doc.add_paragraph()

doc.add_page_break()

# ---- Ordinal seed details ----
doc.add_heading("5. Modelo Ordinal (detalle por semilla)", level=1)
doc.add_paragraph(
    "Para cada semilla, la CV interna (k=5) selecciona logit/probit por mejor QWK en entrenamiento."
)

if ord_seed is None or ord_seed.empty:
    doc.add_paragraph("No se encontraron métricas ordinales (metrics_by_seed.csv).")
else:
    sub = ord_seed[ord_seed["target"].astype(str) == str(TARGET_ORD)]
    if sub.empty:
        # fallback: show all
        sub = ord_seed.copy()

    rows = []
    for _, r in sub.iterrows():
        rows.append([
            int(r.get("seed", -1)),
            int(r.get("n_classes", N_CLASSES)),
            str(r.get("distribution", "—")),
            fmt_num(r.get("accuracy")),
            fmt_num(r.get("f1_weighted")),
            fmt_num(r.get("kappa_qw")),
            fmt_num(r.get("auc_ovr")),
            fmt_num(r.get("time_seconds"), 1),
        ])
    add_styled_table(
        doc,
        ["Seed", "Clases", "Distr.", "Acc", "F1-w", "QWK", "AUC", "Tiempo"],
        rows,
        col_widths_cm=[1.6, 1.6, 1.8, 2.0, 2.0, 2.0, 2.0, 2.4],
    )

doc.add_paragraph()

# ---- Proportional odds exploratory check ----
doc.add_heading("5.1 Chequeo Exploratorio: Proportional Odds", level=2)
doc.add_paragraph(
    "Se reporta un chequeo exploratorio del supuesto de proportional odds estimando "
    "logits binarios por umbral (y≤k vs y>k). Este análisis es descriptivo y se considera "
    "una limitación/validación exploratoria (no confirmatoria)."
)

if po_df is None or po_df.empty:
    doc.add_paragraph("No se encontró po_check.csv en el directorio ordinal.")
else:
    top = po_df.sort_values("max_abs_diff", ascending=False).head(12).copy()
    rows = []
    thr_cols = [c for c in top.columns if c.startswith("thr_")]
    # Show max_abs_diff + first thresholds (up to 3)
    show_thr = thr_cols[: min(3, len(thr_cols))]
    for _, r in top.iterrows():
        term_pretty = prettify_and_shorten(r.get("term", ""), max_len=55)
        row = [term_pretty, fmt_num(r.get("max_abs_diff"), 3)]
        for c in show_thr:
            row.append(fmt_num(r.get(c), 3))
        rows.append(row)

    headers = ["Variable", "max_abs_diff"] + show_thr
    add_styled_table(doc, headers, rows, col_widths_cm=[7.0, 2.6] + [2.4] * len(show_thr))
    doc.add_paragraph("Interpretación: valores altos de max_abs_diff sugieren posibles diferencias de coeficientes entre umbrales.")

doc.add_page_break()

# ---- RF feature importance ----
doc.add_heading("6. Importancia de Variables (Random Forest)", level=1)
if fi_df is None or fi_df.empty:
    doc.add_paragraph("No se encontró rf_feature_importance_*.csv para este run.")
else:
    top = fi_df.sort_values("importance", ascending=False).head(15).copy()
    rows = []
    for i, (_, r) in enumerate(top.iterrows(), 1):
        feat = prettify_and_shorten(r.get("feature", ""), max_len=65)
        rows.append([i, feat, fmt_num(r.get("importance"), 4)])
    add_styled_table(doc, ["#", "Variable", "Importancia"], rows, col_widths_cm=[1.0, 12.0, 3.0])

doc.add_page_break()

# ---- Figures ----
doc.add_heading("7. Visualizaciones", level=1)

# Confusion matrices from sklearn figs
doc.add_heading("7.1 Matriz de confusión del modelo principal", level=2)
rf_cm = sorted(FIG_DIR.glob("cm_random_forest*.png"))
if rf_cm:
    doc.add_picture(str(rf_cm[-1]), width=Inches(4.4))
    doc.add_paragraph(
    "La matriz de confusión muestra que el modelo Random Forest concentra la mayor proporción de aciertos en las categorías intermedias, con menor precisión en las clases extremas."
    )
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
else:
    doc.add_paragraph("No se encontró la matriz de confusión del modelo Random Forest.")

# Confusion matrices from ordinal figs
doc.add_heading("7.2 Matriz de confusión del modelo ordinal", level=2)
ord_cm = sorted(ORD_FIG_DIR.glob("cm_*.png"))
if ord_cm:
    doc.add_picture(str(ord_cm[-1]), width=Inches(4.4))
    doc.add_paragraph(
    "El modelo ordinal reproduce parcialmente la estructura ordenada de la variable dependiente, aunque conserva dificultades para discriminar completamente entre niveles adyacentes."
    )
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

# RF importance fig
rf_fig = sorted(FIG_DIR.glob("rf_feature_importance_top10_*.png"))
if rf_fig:
    doc.add_heading("7.3 Importancia de variables del modelo Random Forest", level=2)
    doc.add_picture(str(rf_fig[-1]), width=Inches(6.2))
    doc.add_paragraph(
    "La figura resume las diez variables con mayor contribución al modelo Random Forest, útiles para identificar los factores más influyentes en la predicción de la confianza electoral."
    )
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
else:
    doc.add_paragraph("No se encontró la figura top 10 de importancia de variables.")


# Ordinal figs
or_fig = sorted(ORD_FIG_DIR.glob("or_top_*.png"))
if or_fig:
    doc.add_heading("7.4 Efectos principales del modelo ordinal", level=2)
    doc.add_picture(str(or_fig[-1]), width=Inches(6.2))
    doc.add_paragraph(
    "El gráfico de odds ratios presenta los efectos principales estimados por el modelo ordinal junto con sus intervalos de confianza al 95%, facilitando la interpretación sustantiva de las asociaciones."
    )
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
else:
    doc.add_paragraph("No se encontraron figuras ordinales.")

doc.add_page_break()

# ---- Conclusions ----
doc.add_heading("8. Síntesis técnica para anexos", level=1)
concs = [
    "El pipeline permite reproducir la limpieza, transformación, modelado y evaluación de los datos.",
    "Los modelos fueron evaluados con partición estratificada 70/30 y cinco semillas para estimar estabilidad.",
    "Las métricas QWK y MAE ordinal se incluyeron para respetar la naturaleza ordinal de la variable dependiente.",
    "El reporte constituye un anexo técnico y no reemplaza la redacción analítica del capítulo de resultados.",
]
for c in concs:
    doc.add_paragraph(c, style="List Bullet")

# Save
OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(OUT_DOCX))

print("OK -> Documento generado:", OUT_DOCX.name)