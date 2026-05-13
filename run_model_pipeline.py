import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


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


steps = [
    "src/01_prepare_data.py",
    "src/02_feature_engineering.py",
    "src/02b_descriptive_tables.py",

    # Modelo principal: 5 niveles
    "-m src.03_modeling --target 5 --input data/processed/encuestas/model_ready_no_text.csv",
    "-m src.03a_ordinal_logit --target 5 --input data/processed/encuestas/model_ready_no_text.csv",
    "-m src.03b_compare_models",
    "-m src.03b_results_table",
    "-m src.04_report_word",

    # Modelo complementario: 3 clases
    "-m src.03_modeling --target 3 --input data/processed/encuestas/model_ready_no_text.csv",
    "-m src.03a_ordinal_logit --target 3 --input data/processed/encuestas/model_ready_no_text.csv",
    "-m src.03b_compare_models",
    "-m src.03b_results_table",
    "-m src.04_report_word",

    # Publicar encuestas al backend
    "-m src.07_publish_artifacts --publish-surveys --clean",
]


for step in steps:
    run(step)

print("\nPipeline de modelos ejecutado correctamente.")
print("Principal: 5 niveles.")
print("Complementario: 3 clases.")