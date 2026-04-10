import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Set, Tuple

from constants import UMBRALES_CLASIFICACION, PATRONES_RECETA, MAX_PLATILLOS, PALABRAS_EXCLUIDAS


def _es_ingrediente_valido(nombre: str) -> bool:

    nombre_lower = str(nombre).lower()
    return not any(palabra in nombre_lower for palabra in PALABRAS_EXCLUIDAS)




def _cumple_umbral(valor, minimo, maximo) -> bool:
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return False
    if np.isnan(v):
        return False
    if minimo is not None and v < minimo:
        return False
    if maximo is not None and v > maximo:
        return False
    return True


def clasificar_alimentos(df: pd.DataFrame) -> Dict[str, List[int]]:

    grupos: Dict[str, List[int]] = {cat: [] for cat, _ in UMBRALES_CLASIFICACION}

    for idx, row in df.iterrows():
        for categoria, condiciones in UMBRALES_CLASIFICACION:
            if all(
                _cumple_umbral(row.get(col, np.nan), vmin, vmax)
                for col, (vmin, vmax) in condiciones.items()
            ):
                grupos[categoria].append(int(idx))
                break  
    return grupos


                                                                                
                                                                     
                                                                                

def _score_completitud(row: pd.Series) -> float:

    cols = ["kcal_100g", "proteina_g", "hierro_mg", "calcio_mg", "vitA_ug", "vitC_mg"]
    presentes = sum(1 for c in cols if pd.notna(row.get(c)) and (row.get(c) or 0) > 0)

    prot  = float(row.get("proteina_g", 0) or 0)
    kcal  = float(row.get("kcal_100g",  0) or 0)
    micro = (
        min(float(row.get("hierro_mg", 0) or 0), 20)
        + min(float(row.get("calcio_mg", 0) or 0) / 100, 15)
        + min(float(row.get("vitA_ug",  0) or 0) / 100, 10)
        + min(float(row.get("vitC_mg",  0) or 0) / 10,  10)
    )
    return presentes * 8 + min(prot, 30) + min(kcal / 50, 8) + micro


def _seleccionar_top(ids: List[int], df: pd.DataFrame, n: int) -> List[int]:
    ids_validos = [i for i in ids if i in df.index]
    if not ids_validos:
        return []
    scored = sorted(ids_validos,
                    key=lambda i: _score_completitud(df.loc[i]),
                    reverse=True)
    return scored[:n]


                                                                                
                                           
                                                                                

def construir_platillos(
    df_alimentos: pd.DataFrame,
    ingredientes_disponibles: Optional[Set[str]] = None,
) -> pd.DataFrame:


                                                                                
    if ingredientes_disponibles is not None:
        kws_lower = {k.lower() for k in ingredientes_disponibles}
        mask = df_alimentos["nombre"].str.lower().apply(
            lambda n: any(kw in n for kw in kws_lower)
        )
        df_work = df_alimentos[mask].copy()
    else:
        df_work = df_alimentos.copy()

                                                                                 
    mascara_validos = df_work["nombre"].apply(_es_ingrediente_valido)
    n_antes = len(df_work)
    df_work = df_work[mascara_validos].copy()
    n_excluidos = n_antes - len(df_work)
    if n_excluidos > 0:
        print(f"  [platillos] {n_excluidos} alimentos excluidos por lista de control.")

    if df_work.empty:
        return pd.DataFrame()

                                                                                
    grupos = clasificar_alimentos(df_work)

                                                                                
    patrones_activos = [
        (nombre, cats, gramos, tecnicas)
        for nombre, cats, gramos, tecnicas in PATRONES_RECETA
        if all(len(grupos.get(c, [])) > 0 for c in cats)
    ]

    if not patrones_activos:
        return pd.DataFrame()

                                                                                
    plats_por_patron = max(2, MAX_PLATILLOS // len(patrones_activos))

    filas: List[dict] = []
    pid = 0

    for nombre_patron, categorias, gramos_lista, tecnicas in patrones_activos:
        if len(filas) >= MAX_PLATILLOS:
            break

        cat_prim = categorias[0]

                                                                          
        representantes = _seleccionar_top(grupos[cat_prim], df_work, plats_por_patron)

                                                                         
                                                                           
        pool_alt: List[List[int]] = []
        for cat in categorias:
            pool = _seleccionar_top(grupos[cat], df_work, 30)
            pool_alt.append(pool)

                                                                                
        secundarios: List[Tuple[int, int, int]] = []                                     
        for i, cat_sec in enumerate(categorias[1:], start=1):
            top1 = _seleccionar_top(grupos[cat_sec], df_work, 1)
            gramos_sec = gramos_lista[i] if i < len(gramos_lista) else 80
            if top1:
                secundarios.append((top1[0], gramos_sec, i))

                                                                            
        for id_prim in representantes:
            if len(filas) >= MAX_PLATILLOS:
                break

            ingredientes: List[Tuple[int, int]] = [(id_prim, gramos_lista[0])]
            alternativas: List[List[int]]        = [pool_alt[0]]                                 

            for id_sec, g_sec, cat_i in secundarios:
                ingredientes.append((id_sec, g_sec))
                alternativas.append(pool_alt[cat_i])

                                                                                        
            for i, (id_ing, _) in enumerate(ingredientes):
                if not alternativas[i]:
                    alternativas[i] = [id_ing]

                                                                         
            nombre_raw   = str(df_work.loc[id_prim, "nombre"])
            nombre_corto = nombre_raw[:30] if len(nombre_raw) > 30 else nombre_raw
            nombre_plat  = f"{nombre_patron}: {nombre_corto}"

            filas.append({
                "id_platillo":       pid,
                "nombre":            nombre_plat,
                "ingredientes":      ingredientes,
                "alternativas":      alternativas,
                "tecnicas_permitidas": tecnicas,
                "porcion_base_g":    sum(g for _, g in ingredientes),
            })
            pid += 1

    if not filas:
        return pd.DataFrame()

    return pd.DataFrame(filas).set_index("id_platillo")
