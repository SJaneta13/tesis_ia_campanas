import pandas as pd
from scipy.stats import spearmanr

RUTA = "data/processed/encuestas/model_ready.csv"
df = pd.read_csv(RUTA)

col_identifica = "identifica_ia"
col_verifica = "¿Realiza alguna verificación (chequea fuentes, busca noticias, consulta otras personas) de la información política digital antes de compartirla?"

# Revisar valores originales
print("\nVALORES ORIGINALES - IDENTIFICACIÓN")
print(df[col_identifica].value_counts(dropna=False))

print("\nVALORES ORIGINALES - VERIFICACIÓN")
print(df[col_verifica].value_counts(dropna=False))

# Codificación ordinal
map_identifica = {
    "Sí, fácilmente": 3,
    "A veces": 2,
    "No, me resulta difícil distinguirlo": 1,
}

map_verifica = {
    "Siempre": 4,
    "A veces": 3,
    "Rara vez": 2,
    "Nunca": 1,
}

df["identifica_ia_num_calc"] = df[col_identifica].map(map_identifica)
df["verifica_info_num_calc"] = df[col_verifica].map(map_verifica)

cols_alfmed = ["identifica_ia_num_calc", "verifica_info_num_calc"]

items = df[cols_alfmed].dropna()

# Alfa de Cronbach
k = items.shape[1]
var_items = items.var(axis=0, ddof=1).sum()
var_total = items.sum(axis=1).var(ddof=1)

alpha = (k / (k - 1)) * (1 - (var_items / var_total))

# Spearman entre ambos ítems
rho, p = spearmanr(items["identifica_ia_num_calc"], items["verifica_info_num_calc"])

print("\nCOLUMNAS USADAS PARA ALFABETIZACIÓN / VERIFICACIÓN")
print("-", col_identifica)
print("-", col_verifica)

print("\nAlfa de Cronbach")
print("alpha =", round(alpha, 3))
print("n =", len(items))

print("\nSpearman entre identificación IA y verificación informativa")
print("rho =", round(rho, 3))
print("p =", round(p, 5))