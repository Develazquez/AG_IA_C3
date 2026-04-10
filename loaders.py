import zipfile
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional

from constants import USDA_NUT_IDS


def cargar_usda(path_zip: str) -> pd.DataFrame:
 
    with zipfile.ZipFile(path_zip) as z:
        log_file = [n for n in z.namelist() if "food_update_log_entry" in n][0]
        fn_file  = [n for n in z.namelist() if "food_nutrient.csv" in n][0]
        with z.open(log_file) as f:
            fule = pd.read_csv(f)
        with z.open(fn_file) as f:
            fn = pd.read_csv(f, low_memory=False,
                             usecols=["fdc_id", "nutrient_id", "amount"])

    fule = (fule.sort_values("last_updated")
                .drop_duplicates("id", keep="last")
                .rename(columns={"id": "fdc_id", "description": "nombre"}))

    fn_fil = fn[fn["nutrient_id"].isin(USDA_NUT_IDS.keys())].copy()
    fn_fil["nutrient_id"] = fn_fil["nutrient_id"].map(USDA_NUT_IDS)
    pivot = fn_fil.groupby(["fdc_id", "nutrient_id"])["amount"].mean().unstack()
    pivot = pivot.reindex(columns=list(USDA_NUT_IDS.values()))

    df = fule.merge(pivot, on="fdc_id", how="inner").dropna(subset=["kcal_100g"])
    df["fuente"] = "USDA"
    df["grupo"]  = "general"
    df["costo_por_100g"] = 40.0
    df = df.reset_index(drop=True)
    df.index.name = "id"
    return df[["nombre", "grupo", "fuente", "costo_por_100g",
               "kcal_100g", "proteina_g", "hierro_mg",
               "calcio_mg", "vitA_ug", "vitC_mg"]]


def cargar_fao(path_csv: str) -> pd.DataFrame:
    
    df = pd.read_csv(path_csv, encoding="latin1")
    df = df.rename(columns={
        "Descripcion_alimento": "nombre",
        "Tipo":                 "grupo",
        "Energia_kcal":         "kcal_100g",
        "Proteina_bruta_g":     "proteina_g",
        "Fe_mg":                "hierro_mg",
        "Ca_mg":                "calcio_mg",
        "VitA_ug_RAE":          "vitA_ug",
        "Ac_ascorbico_mg":      "vitC_mg",
    })
    for col in ["kcal_100g", "proteina_g", "hierro_mg",
                "calcio_mg", "vitA_ug", "vitC_mg"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["fuente"] = "FAO_Mexico"
    df["costo_por_100g"] = 40.0
    df = df.dropna(subset=["kcal_100g"]).reset_index(drop=True)
    df.index.name = "id"
    return df[["nombre", "grupo", "fuente", "costo_por_100g",
               "kcal_100g", "proteina_g", "hierro_mg",
               "calcio_mg", "vitA_ug", "vitC_mg"]]


def _parse_gramos(presentacion: str) -> Optional[float]:
  
    if not isinstance(presentacion, str):
        return None
                                          
    m = re.search(r"(\d[\d,\.]*)\s*(?:Gr|Kg|gr|kg|g\b)", presentacion, re.IGNORECASE)
    if not m:
                                                      
        m_l = re.search(r"(\d[\d,\.]*)\s*(?:Lt?|lt?|ml)\b", presentacion, re.IGNORECASE)
        if m_l:
            val = float(m_l.group(1).replace(",", ""))
            if "ml" in presentacion.lower():
                return val if val > 0 else None
            return val * 1000 if val > 0 else None
        return None
    val = float(m.group(1).replace(",", ""))
    if re.search(r"Kg|kg", presentacion):
        val *= 1000
    return val if val > 0 else None


def cargar_profeco(path_csv: str) -> Dict[str, float]:
    
    cats = [
        "Hortalizas Frescas", "Frutas Frescas", "Derivados de Leche",
        "Leche Procesada", "Arroz y Cereales Preparados", "Legumbres Secas",
        "Carnes y Aves Frescas", "Pescados y Mariscos Frescos",
        "Huevo", "Aceites y Grasas Veg. Comestibles", "Pan",
    ]
    df = pd.read_csv(path_csv, encoding="utf-8-sig", low_memory=False,
                     usecols=["producto", "presentacion", "precio", "categoria"])
    df = df[df["categoria"].isin(cats)].copy()
    df["gramos"] = df["presentacion"].apply(_parse_gramos)

    mask = df["gramos"].notna() & (df["gramos"] > 0)
    df.loc[mask, "precio_100g"] = df.loc[mask, "precio"] / df.loc[mask, "gramos"] * 100

    mask_kg = df["gramos"].isna() & df["presentacion"].str.contains("1 Kg", na=False)
    df.loc[mask_kg, "precio_100g"] = df.loc[mask_kg, "precio"] / 10.0

    precios = (
        df.dropna(subset=["precio_100g"])
        .groupby("producto")["precio_100g"]
        .median()
        .to_dict()
    )
    return {k.lower(): v for k, v in precios.items()}


def enriquecer_costos(df_alimentos: pd.DataFrame,
                      precios_profeco: Dict[str, float]) -> pd.DataFrame:
   
    df = df_alimentos.copy()

    profeco_tokens: Dict[str, List[Tuple[str, float]]] = {}
    for prod_key, precio in precios_profeco.items():
        tokens = set(prod_key.split())
        for t in tokens:
            if len(t) >= 3:
                profeco_tokens.setdefault(t, []).append((prod_key, precio))

    for idx, row in df.iterrows():
        nombre_lower = str(row["nombre"]).lower()
        nombre_tokens = set(nombre_lower.split())
        mejor_match = None
        mejor_score = 0
        for t in nombre_tokens:
            if len(t) < 3:
                continue
            for prod_key, precio in profeco_tokens.get(t, []):
                prod_tokens = set(prod_key.split())
                score = len(nombre_tokens & prod_tokens)
                if score > mejor_score:
                    mejor_score = score
                    mejor_match = precio
        if mejor_match is not None and mejor_score >= 1:
            df.at[idx, "costo_por_100g"] = round(mejor_match, 4)
    return df


def cargar_requerimientos(path_csv: str) -> pd.DataFrame:
    df = pd.read_csv(path_csv)
    filas = []
    nutrientes_map = {
        "kcal":       "energia_kcal_dia",
        "proteina_g": "proteina_g_dia",
        "hierro_mg":  "hierro_mg_dia",
        "calcio_mg":  "calcio_mg_dia",
        "vitA_ug":    "vitamina_a_mcg_dia",
        "vitC_mg":    "vitamina_c_mg_dia",
    }
    for _, row in df.iterrows():
        for nut_key, col in nutrientes_map.items():
            val = float(row[col])
            filas.append({
                "edad_min":    int(row["edad_min"]),
                "edad_max":    int(row["edad_max"]),
                "sexo":        str(row["sexo"]),
                "nutriente":   nut_key,
                "rmin_diario": round(val * 0.80, 2),
                "rmax_diario": round(val * 1.20, 2),
            })
    return pd.DataFrame(filas)
