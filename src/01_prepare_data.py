import pandas as pd
import re
from pathlib import Path

RAW_PATH_XLSX = Path("data/raw/respuestas_forms.xlsx")
RAW_PATH_CSV = Path("data/raw/Encuesta de tesisis.csv")
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed/encuestas")
PROCESSED_PATH = PROCESSED_DIR / "respuestas_limpias.csv"

# Crear carpeta de salida si no existe
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# Leer archivo raw (prioriza CSV si existe)
csv_candidates = sorted(
    RAW_DIR.glob("*.csv"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

if csv_candidates:
    selected_csv = csv_candidates[0]
    df = pd.read_csv(selected_csv, encoding="utf-8-sig")

    # ============================
    # ELIMINAR DATOS PERSONALES (ANONIMIZACIÓN)
    # ============================

    PII_COLS = [
        "Nombre de usuario",   # correo del formulario
    ]

    for col in PII_COLS:
        if col in df.columns:
            df = df.drop(columns=[col])
            print(f"Columna eliminada por anonimización: {col}")

    print(f"Usando CSV detectado automáticamente: {selected_csv}")
elif RAW_PATH_XLSX.exists():
    df = pd.read_excel(RAW_PATH_XLSX)    
    print(f"Usando XLSX legacy: {RAW_PATH_XLSX}")
else:
    raise FileNotFoundError(
        "No se encontró archivo de encuestas. Esperado CSV en data/raw/Encuesta de tesisis*.csv "
        "o XLSX en data/raw/respuestas_forms.xlsx"
    )

# Función para arreglar texto corrupto

def fix_text(x):
    if isinstance(x, str):
        if any(bad in x for bad in ["â", "Ã", "�"]):
            x = x.replace("â€“", "-")
            try:
                return x.encode("latin1").decode("utf-8")
            except Exception:
                return x
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



print("Filas antes de filtros:", len(df))

filas_iniciales = len(df)
filas_post_rol = None
filas_post_quito = None
filas_post_edad = None


if "edad" in df.columns:
    print("\nValores únicos de edad:")
    print(df["edad"].astype(str).value_counts(dropna=False).head(20))

if "reside_quito" in df.columns:
    print("\nValores únicos de reside_quito:")
    print(df["reside_quito"].astype(str).value_counts(dropna=False).head(20))

if "rol_uce" in df.columns:
    print("\nValores únicos de rol_uce:")
    print(df["rol_uce"].astype(str).value_counts(dropna=False).head(20))


# Rol UCE informado
if "rol_uce" in df.columns:
    df["rol_uce"] = df["rol_uce"].astype(str).str.strip()
    df = df[df["rol_uce"].notna() & (df["rol_uce"] != "") & (df["rol_uce"].str.lower() != "nan")].copy()

filas_post_rol = len(df)
print("Filas después de filtro rol_uce:", filas_post_rol)


# Reside en Quito: filtro flexible
if "reside_quito" in df.columns:
    rq = (
        df["reside_quito"]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    df = df[rq.str.contains("sí|si|quito", na=False)].copy()

filas_post_quito = len(df)
print("Filas después de filtro reside_quito:", filas_post_quito)


# ============================
# Filtro de edad: 18 a 64 años
# ============================


valid_ranges = ["18-24", "25-34", "35-44", "45-54", "55-64"]

if "edad" in df.columns:
    # Normalizar formato (por si viene con espacios o guiones raros)
    df["edad"] = (
        df["edad"]
        .astype(str)
        .str.replace("–", "-", regex=False)
        .str.replace("—", "-", regex=False)
        .str.strip()
    )

    # Ver valores inválidos (auditoría)
    invalid = df[~df["edad"].isin(valid_ranges)]
    if len(invalid) > 0:
        print("\n⚠ Edades fuera del catálogo detectadas:")
        print(invalid["edad"].value_counts())

    # Filtrar solo rangos válidos
    df = df[df["edad"].isin(valid_ranges)].copy()

filas_post_edad = len(df)
print("Filas después de filtro edad (rangos válidos):", filas_post_edad)


# Guardar
df.to_csv(PROCESSED_PATH, index=False, encoding="utf-8-sig")

criterios = pd.DataFrame([
    {
        "criterio": "Rol institucional",
        "condicion": "Debe pertenecer a la comunidad universitaria UCE",
        "aplicado_en": "rol_uce"
    },
    {
        "criterio": "Residencia",
        "condicion": "Debe residir actualmente en Quito",
        "aplicado_en": "reside_quito"
    },
    {
        "criterio": "Edad",
        "condicion": "Debe estar entre 18 y 64 años",
        "aplicado_en": "edad"
    },
    {
        "criterio": "Anonimización",
        "condicion": "Se elimina correo o nombre de usuario del formulario",
        "aplicado_en": "Nombre de usuario"
    },
])

criterios.to_csv(
    PROCESSED_DIR / "criterios_limpieza_inclusion.csv",
    index=False,
    encoding="utf-8-sig"
)

# Auditoría de limpieza
audit = pd.DataFrame([{
    "filas_iniciales": int(filas_iniciales),
    "filas_post_rol_uce": int(filas_post_rol),
    "filas_post_reside_quito": int(filas_post_quito),
    "filas_post_edad_18_64": int(filas_post_edad),
    "filas_finales": int(df.shape[0]),
    "columnas_finales": int(df.shape[1]),
    "archivo_salida": str(PROCESSED_PATH),
}])

audit.to_csv(PROCESSED_DIR / "cleaning_audit.csv", index=False, encoding="utf-8-sig")

# Verificación
print("Dataset limpio guardado.")

print("Dimensión:", df.shape)
print("¿Existe confianza_limpieza?", "confianza_limpieza" in df.columns)
print("¿Existe confianza_fraude?", "confianza_fraude" in df.columns)
print("Columnas disponibles:")
print(df.columns.tolist())
