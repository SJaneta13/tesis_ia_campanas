# src/06_visualization/dashboard_news.py
import argparse
from pathlib import Path
import pandas as pd

import plotly.express as px

ORDER = ["negativo", "neutral", "positivo"]

def read_scored(path: str, case_id: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["case_id"] = case_id
    df["is_ai_related"] = df["is_ai_related"].astype(bool)
    # date robusto
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["date"] = pd.to_datetime(df.get("published_at", ""), errors="coerce")
    return df

def pct_table(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    # asegura categorías
    df = df.copy()
    df["sentiment_label"] = df["sentiment_label"].astype(str).str.lower().str.strip()
    # conteos
    ct = df.groupby(group_cols + ["sentiment_label"]).size().reset_index(name="count")
    # completa categorías faltantes
    # pivot->reindex->melt para garantizar ORDER
    pivot = ct.pivot_table(index=group_cols, columns="sentiment_label", values="count", fill_value=0)
    for lab in ORDER:
        if lab not in pivot.columns:
            pivot[lab] = 0
    pivot = pivot[ORDER]
    pivot["total"] = pivot.sum(axis=1)
    pct = (pivot[ORDER].div(pivot["total"], axis=0) * 100).round(1)
    out = pct.reset_index().melt(id_vars=group_cols, value_vars=ORDER, var_name="sentiment_label", value_name="pct")
    return out

def save_png(fig, out_png: Path):
    # requiere kaleido
    try:
        fig.write_image(str(out_png), scale=2)
    except Exception:
        print("[WARN] No se pudo exportar PNG. Instala: pip install -U kaleido")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case1", required=True, help="path a outputs/text_analysis/case1_es/news_sentiment_scored.csv")
    p.add_argument("--case2", required=True, help="path a outputs/text_analysis/case2_en/news_sentiment_scored.csv")
    p.add_argument("--case3", required=True, help="path a outputs/text_analysis/case3_ec_media/news_sentiment_scored.csv")
    p.add_argument("--outdir", default="outputs/visualization/news")
    p.add_argument("--topics1", default="", help="opcional: news_topics_docs.csv case1")
    p.add_argument("--topics2", default="", help="opcional: news_topics_docs.csv case2")
    p.add_argument("--topics3", default="", help="opcional: news_topics_docs.csv case3")
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df1 = read_scored(args.case1, "case1_es")
    df2 = read_scored(args.case2, "case2_en")
    df3 = read_scored(args.case3, "case3_ec_media")
    df = pd.concat([df1, df2, df3], ignore_index=True)

    # =========================
    # 1) Sentimiento por caso (%)
    # =========================
    pct_case = pct_table(df, ["case_id"])
    pct_case.to_csv(outdir / "sentiment_by_case.csv", index=False, encoding="utf-8-sig")
    fig1 = px.bar(
        pct_case, x="case_id", y="pct", color="sentiment_label",
        category_orders={"sentiment_label": ORDER},
        title="Distribución de sentimiento por caso (%)",
        barmode="stack",
    )
    fig1.write_html(outdir / "sentiment_by_case.html")
    save_png(fig1, outdir / "sentiment_by_case.png")

    # =========================
    # 2) IA vs No IA por caso (%)
    # =========================
    df["ai_group"] = df["is_ai_related"].map({True: "IA", False: "No IA"})
    pct_ai = pct_table(df, ["case_id", "ai_group"])
    pct_ai.to_csv(outdir / "ai_vs_non_ai_by_case.csv", index=False, encoding="utf-8-sig")
    fig2 = px.bar(
        pct_ai, x="ai_group", y="pct", color="sentiment_label",
        facet_col="case_id",
        category_orders={"sentiment_label": ORDER, "ai_group": ["No IA", "IA"]},
        title="Sentimiento: IA vs No IA por caso (%)",
        barmode="stack",
    )
    fig2.write_html(outdir / "ai_vs_non_ai_by_case.html")
    save_png(fig2, outdir / "ai_vs_non_ai_by_case.png")

    # =========================
    # 3) Serie temporal semanal (% negativo)
    # =========================
    dft = df.dropna(subset=["date"]).copy()
    dft["week"] = dft["date"].dt.to_period("W").dt.start_time
    weekly = (
        dft.groupby(["case_id", "week", "ai_group", "sentiment_label"])
           .size().reset_index(name="count")
    )
    tot = weekly.groupby(["case_id", "week", "ai_group"])["count"].sum().reset_index(name="total")
    weekly = weekly.merge(tot, on=["case_id","week","ai_group"], how="left")
    weekly["pct"] = (weekly["count"] / weekly["total"] * 100).round(1)
    neg = weekly[weekly["sentiment_label"].str.lower() == "negativo"].copy()

    neg.to_csv(outdir / "sentiment_timeseries_weekly.csv", index=False, encoding="utf-8-sig")

    fig3 = px.line(
        neg, x="week", y="pct", color="ai_group", facet_col="case_id",
        title="% Negativo semanal (IA vs No IA)",
        markers=True
    )
    fig3.write_html(outdir / "sentiment_timeseries_weekly.html")
    save_png(fig3, outdir / "sentiment_timeseries_weekly.png")

    # =========================
    # 4) Tópicos por caso (opcional)
    # =========================
    topics_files = {
        "case1_es": args.topics1,
        "case2_en": args.topics2,
        "case3_ec_media": args.topics3,
    }
    topic_rows = []
    for cid, f in topics_files.items():
        if f and Path(f).exists():
            td = pd.read_csv(f)
            if "dominant_topic" in td.columns:
                c = td["dominant_topic"].value_counts().sort_index()
                for k, v in c.items():
                    topic_rows.append({"case_id": cid, "topic": int(k), "count": int(v)})

    if topic_rows:
        tdf = pd.DataFrame(topic_rows)
        fig4 = px.bar(
            tdf, x="topic", y="count", facet_col="case_id",
            title="Distribución de tópicos (LDA) por caso"
        )
        fig4.write_html(outdir / "topics_distribution_by_case.html")
        save_png(fig4, outdir / "topics_distribution_by_case.png")

    print(f"[DONE] Visualizaciones guardadas en: {outdir}")
    print(" - sentiment_by_case.html/.png")
    print(" - ai_vs_non_ai_by_case.html/.png")
    print(" - sentiment_timeseries_weekly.html/.png")
    if topic_rows:
        print(" - topics_distribution_by_case.html/.png")

if __name__ == "__main__":
    main()
