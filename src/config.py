from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed" / "encuestas"

RESPUESTAS_LIMPIAS = DATA_PROCESSED / "respuestas_limpias.csv"
MODEL_READY = DATA_PROCESSED / "model_ready.csv"
MODEL_READY_NO_TEXT = DATA_PROCESSED / "model_ready_no_text.csv"

OUTPUTS = ROOT / "outputs"
OUTPUTS_RUNS = OUTPUTS / "runs"
OUTPUTS_DESCRIPTIVE = OUTPUTS / "descriptive"
OUTPUTS_LATEST = OUTPUTS / "latest"