import pandas as pd
import re
from pathlib import Path

RAW_PATH_XLSX = Path("data/raw/respuestas_forms.xlsx")
RAW_PATH_CSV = Path("data/raw/Encuesta de tesisis.csv")
PROCESSED_DIR = Path("data/processed/encuestas")
PROCESSED_PATH = PROCESSED_DIR / "respuestas_limpias.csv"

# Crear carpeta de salida si no existe
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# Leer archivo raw (prioriza CSV si existe)
if RAW_PATH_CSV.exists():
    df = pd.read_csv(RAW_PATH_CSV, encoding="utf-8-sig")
elif RAW_PATH_XLSX.exists():
    df = pd.read_excel(RAW_PATH_XLSX)
else:
    raise FileNotFoundError(
        "No se encontró archivo de encuestas. Esperado CSV en data/raw/Encuesta de tesisis.csv "
        "o XLSX en data/raw/respuestas_forms.xlsx"
    )

# Función para arreglar texto corrupto

def fix_text(x):
    if isinstance(x, str):
        x = x.replace("â€“", "-")
        try:
            return x.encode("latin1").decode("utf-8")
        except Exception:
            return x
    return x

# Arreglar texto en columnas tipo objeto
obj_cols = df.select_dtypes(include="object").columns
df[obj_cols] = df[obj_cols].apply(lambda col: col.map(fix_text))

# Limpiar nombres de columnas (SIN romper acentos)
def clean_colname(s: str) -> str:
    s = fix_text(s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

df.columns = [clean_colname(c) if isinstance(c, str) else c for c in df.columns]

rename_dict = {
    "¿Cuál es tu edad?": "edad",
    "¿Cuál es tu género?": "genero",
    "¿Cuál es su rol dentro de la Universidad Central del Ecuador?": "rol_uce",
    "¿Reside actualmente en la ciudad de Quito?": "reside_quito",

    "¿Ha escuchado hablar sobre inteligencia artificial aplicada a campañas políticas digitales?": "conoce_ia",
    "¿Reconoció o notó el uso de herramientas automatizadas (bots, anuncios personalizados, deepfakes, etc.) en la campaña digital de Noboa o González?": "percibe_automatizacion",
    "¿Sabe identificar cuándo un mensaje, imagen, video o audio político ha sido generado por inteligencia artificial?": "identifica_ia",

    "Confianza Electoral   [Confío en que las elecciones nacionales en Ecuador se realizan de forma justa y transparente.]": "confianza_limpieza",
    "Confianza Electoral   [Creo que existe fraude o manipulación en el proceso electoral.]": "confianza_fraude"
}

# Normaliza también las llaves del diccionario
rename_dict = {clean_colname(k): v for k, v in rename_dict.items()}

df = df.rename(columns=rename_dict)

# Guardar
df.to_csv(PROCESSED_PATH, index=False, encoding="utf-8-sig")

# Verificación
print("Dataset limpio guardado.")
print("Dimensión:", df.shape)
print("¿Existe confianza_limpieza?", "confianza_limpieza" in df.columns)
print("¿Existe confianza_fraude?", "confianza_fraude" in df.columns)
print("Columnas disponibles:")
print(df.columns.tolist())
