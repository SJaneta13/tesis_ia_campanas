import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN_ID_NEWS = "run_final_tesis"


def run(cmd: str) -> None:
    print("\n" + "=" * 90)
    print(f"Ejecutando: {cmd}")
    print("=" * 90)

    result = subprocess.run(
        f"{sys.executable} {cmd}",
        shell=True,
        cwd=ROOT
    )

    if result.returncode != 0:
        raise RuntimeError(f"Falló el comando: {cmd}")


news_cases = [
    {
        "case_id": "case1_es",
        "lang_api": "ES",
        "lang_text": "Spanish",
        "extra": "",
        "sleep": "1.2",
    },
    {
        "case_id": "case2_en",
        "lang_api": "EN",
        "lang_text": "English",
        "extra": "",
        "sleep": "1.5",
    },
    {
        "case_id": "case3_ec_media",
        "lang_api": "ES",
        "lang_text": "Spanish",
        "extra": "--only-ec-media",
        "sleep": "1.8",
    },
]


for case in news_cases:
    case_id = case["case_id"]

    raw_dir = f"data/external/news_gdelt/cases/{case_id}/{RUN_ID_NEWS}"
    clean_file = (
        f"data/processed/news_gdelt/cases/{case_id}/"
        f"{RUN_ID_NEWS}/digital_content_clean.csv"
    )
    analysis_dir = f"outputs/text_analysis/{case_id}"

    run(
        f'src/04_scraping/scrape_news_gdelt.py '
        f'--outdir "{raw_dir}" '
        f'--lang "{case["lang_api"]}" '
        f'--start "20250201000000" '
        f'--end "20250501000000" '
        f'--pages 6 '
        f'--page-size 250 '
        f'--sleep {case["sleep"]} '
        f'{case["extra"]}'
    )

    run(
        f'src/04_scraping/enrich_news_text.py '
        f'--indir "{raw_dir}" '
        f'--outdir "{raw_dir}" '
        f'--sleep {case["sleep"]} '
        f'--max-rows 0'
    )

    run(
        f'src/04_scraping/clean_scraped_data.py '
        f'--newsdir "{raw_dir}" '
        f'--case-id "{case_id}" '
        f'--run-id "{RUN_ID_NEWS}" '
        f'--out "{clean_file}"'
    )

    run(
        f'src/05_text_analysis/frequency_analysis.py '
        f'--input "{clean_file}" '
        f'--text-col text '
        f'--lang "{case["lang_text"]}" '
        f'--outdir "{analysis_dir}" '
        f'--outfile "frequency_top_terms.csv"'
    )

    run(
        f'src/05_text_analysis/topic_modeling.py '
        f'--input "{clean_file}" '
        f'--text-col text '
        f'--lang "{case["lang_text"]}" '
        f'--topics 5 '
        f'--top-words 10 '
        f'--outdir "{analysis_dir}" '
        f'--prefix news'
    )

    run(
        f'src/05_text_analysis/sentiment_analysis.py '
        f'--input "{clean_file}" '
        f'--text-col text '
        f'--outdir "{analysis_dir}" '
        f'--prefix news '
        f'--lang "{case["lang_text"]}"'
    )

    run(
    f'-c "import pandas as pd; '
    f'df=pd.read_csv(r\'{clean_file}\'); '
    f'print(\'N=\', len(df), '
    f'\'unique=\', df[\'url\'].nunique(), '
    f'\'dup=\', df[\'url\'].duplicated().sum())"'
    )


run(
    'src/06_visualization/dashboard_news.py '
    '--case1 "outputs/text_analysis/case1_es/news_sentiment_scored.csv" '
    '--case2 "outputs/text_analysis/case2_en/news_sentiment_scored.csv" '
    '--case3 "outputs/text_analysis/case3_ec_media/news_sentiment_scored.csv" '
    '--outdir "outputs/visualization/news" '
    '--topics1 "outputs/text_analysis/case1_es/news_topics_docs.csv" '
    '--topics2 "outputs/text_analysis/case2_en/news_topics_docs.csv" '
    '--topics3 "outputs/text_analysis/case3_ec_media/news_topics_docs.csv"'
)

run("src/07_publish_artifacts.py --publish-news")

print("\nPipeline de noticias ejecutado correctamente.")
print("Casos: case1_es, case2_en, case3_ec_media.")