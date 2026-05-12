import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

steps = [
    # Preparación de datos
    "src/01_prepare_data.py",
    "src/02_feature_engineering.py",
    "src/02b_descriptive_tables.py",

    # Modelo principal: 5 niveles
    "src/03_modeling.py --target 5",
    "src/03a_ordinal_logit.py --target 5",
    "src/03b_compare_models.py",
    "src/03b_results_table.py",
    "src/04_report_word.py",

    # Modelo complementario: 3 clases
    "src/03_modeling.py --target 3",
    "src/03a_ordinal_logit.py --target 3",
    "src/03b_compare_models.py",
    "src/03b_results_table.py",
    "src/04_report_word.py",
]

for step in steps:
    print("\n" + "=" * 90)
    print(f"Ejecutando: {step}")
    print("=" * 90)

    result = subprocess.run(
        f"{sys.executable} {step}",
        shell=True,
        cwd=ROOT
    )

    if result.returncode != 0:
        raise RuntimeError(f"Falló el paso: {step}")

print("\nPipeline de modelado completo ejecutado correctamente.")
print("Modelo principal: 5 niveles.")
print("Modelo complementario: 3 clases.")