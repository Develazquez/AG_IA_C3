"""
MenuGen-DIF v2: Construcción del catálogo de platillos
"""

import pandas as pd
from typing import Optional, Set

from constants import GRUPOS_SUSTITUCION


def construir_platillos(df_alimentos: pd.DataFrame,
                        ingredientes_disponibles: Optional[Set[str]] = None
                        ) -> pd.DataFrame:
    """
    Construye catálogo de platillos típicos de comedores DIF Chiapas.
    Cada ingrediente lleva su grupo de sustitución para la variable I_i.
    ingredientes_disponibles: set de keywords permitidos (None = todos).
    """
    def buscar_id(keyword: str) -> Optional[int]:
        mask = df_alimentos["nombre"].str.lower().str.contains(
            keyword.lower(), na=False)
        hits = df_alimentos[mask]
        if len(hits) == 0:
            return None
        # Preferir el match más corto (más específico)
        hits = hits.copy()
        hits["_len"] = hits["nombre"].str.len()
        return int(hits.sort_values("_len").index[0])

    def disponible(keyword: str) -> bool:
        if ingredientes_disponibles is None:
            return True
        return keyword.lower() in {k.lower() for k in ingredientes_disponibles}

    def grupo_de(keyword: str) -> str:
        for grupo, kws in GRUPOS_SUSTITUCION.items():
            if keyword.lower() in [k.lower() for k in kws]:
                return grupo
        return "otro"

    # Recetas: (nombre, [(keyword, gramos, grupo_sustitucion)], tecnicas_permitidas)
    recetas_raw = [
        ("Arroz con pollo",
         [("chicken", 80), ("rice", 100), ("tomato", 30)],
         ["hervido", "guisado"]),
        ("Frijoles de olla",
         [("beans, black", 120), ("tomato", 20)],
         ["hervido", "guisado"]),
        ("Huevos revueltos",
         [("egg", 100), ("tomato", 30)],
         ["frito", "guisado"]),
        ("Avena con leche",
         [("oat", 60), ("milk", 200)],
         ["hervido"]),
        ("Sopa de lentejas",
         [("lentil", 100), ("tomato", 30)],
         ["hervido", "guisado"]),
        ("Pollo asado con brócoli",
         [("chicken", 100), ("broccoli", 80)],
         ["asado", "al_vapor"]),
        ("Tacos de atún",
         [("tuna", 80), ("tortilla", 40)],
         ["guisado"]),
        ("Puré de papa",
         [("potato", 150), ("milk", 30)],
         ["hervido"]),
        ("Carne con calabaza",
         [("beef", 100), ("squash", 80)],
         ["guisado", "hervido"]),
        ("Quesadillas de queso",
         [("cheese", 50), ("tortilla", 60)],
         ["asado", "frito"]),
        ("Fruta mixta",
         [("banana", 80), ("apple", 80)],
         ["crudo"]),
        ("Sopa de verduras",
         [("carrot", 80), ("tomato", 50)],
         ["hervido"]),
        ("Ensalada de espinaca",
         [("spinach", 80), ("tomato", 30)],
         ["crudo", "al_vapor"]),
        ("Lentejas guisadas",
         [("lentil", 120), ("carrot", 40)],
         ["guisado", "hervido"]),
        ("Caldo de res",
         [("beef", 80), ("carrot", 50)],
         ["hervido"]),
        ("Arroz a la mexicana",
         [("rice", 100), ("tomato", 50)],
         ["guisado", "frito"]),
        ("Frijoles negros",
         [("beans, black", 120)],
         ["hervido", "guisado"]),
        ("Tortilla con frijol",
         [("tortilla", 60), ("beans, black", 80)],
         ["asado", "guisado"]),
        ("Pollo en salsa",
         [("chicken", 100), ("tomato", 60)],
         ["guisado", "hervido"]),
        ("Ensalada de zanahoria",
         [("carrot", 100), ("apple", 50)],
         ["crudo"]),
    ]

    filas = []
    for pid, (nombre, ingredientes, tecnicas) in enumerate(recetas_raw):
        ings_resueltos = []
        porcion = 0
        for keyword, gramos in ingredientes:
            if not disponible(keyword):
                continue
            idx = buscar_id(keyword)
            if idx is not None:
                ings_resueltos.append({
                    "id_alimento": idx,
                    "gramos_base": gramos,
                    "keyword":     keyword,
                    "grupo_sust":  grupo_de(keyword),
                })
                porcion += gramos

        if not ings_resueltos:
            continue

        # Construir lista de IDs alternativos por cada ingrediente
        alternativas = []
        for ing in ings_resueltos:
            grupo = ing["grupo_sust"]
            alts = []
            for kw in GRUPOS_SUSTITUCION.get(grupo, []):
                if not disponible(kw):
                    continue
                alt_id = buscar_id(kw)
                if alt_id is not None:
                    alts.append(alt_id)
            if not alts:
                alts = [ing["id_alimento"]]
            alternativas.append(alts)

        filas.append({
            "id_platillo":       pid,
            "nombre":            nombre,
            "ingredientes":      [(d["id_alimento"], d["gramos_base"]) for d in ings_resueltos],
            "alternativas":      alternativas,  # lista de listas de IDs sustitutos
            "tecnicas_permitidas": tecnicas,
            "porcion_base_g":    porcion,
        })

    return pd.DataFrame(filas).set_index("id_platillo")
