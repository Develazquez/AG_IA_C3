import os


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PATH_USDA_ZIP = os.path.join(_BASE_DIR, "datasets", "FoodData_Central_foundation_food_csv_2025-12-18.zip")
PATH_FAO      = os.path.join(_BASE_DIR, "datasets", "TABLAS_ALIMENTOS.csv")
PATH_PROFECO  = os.path.join(_BASE_DIR, "datasets", "11-2025_01.csv")
PATH_REQS     = os.path.join(_BASE_DIR, "datasets", "requerimientos_nutricionales_dif.csv")


USDA_NUT_IDS = {
    1008: "kcal_100g",
    1003: "proteina_g",
    1089: "hierro_mg",
    1087: "calcio_mg",
    1106: "vitA_ug",
    1162: "vitC_mg",
}

NUTRIENTES = ["kcal", "proteina_g", "hierro_mg", "calcio_mg", "vitA_ug", "vitC_mg"]
DIAS    = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
COMIDAS = ["Desayuno", "Comida", "Cena"]


TECNICAS_PREPARACION = {
    "crudo": {
        "kcal": 1.00, "proteina_g": 1.00, "hierro_mg": 1.00,
        "calcio_mg": 1.00, "vitA_ug": 1.00, "vitC_mg": 1.00,
        "costo_extra": 0.0,
    },
    "hervido": {
        "kcal": 0.95, "proteina_g": 0.95, "hierro_mg": 0.90,
        "calcio_mg": 0.85, "vitA_ug": 0.85, "vitC_mg": 0.50,
        "costo_extra": 0.5,
    },
    "asado": {
        "kcal": 0.90, "proteina_g": 0.98, "hierro_mg": 0.95,
        "calcio_mg": 0.95, "vitA_ug": 0.90, "vitC_mg": 0.70,
        "costo_extra": 1.0,
    },
    "frito": {
        "kcal": 1.30, "proteina_g": 0.95, "hierro_mg": 0.90,
        "calcio_mg": 0.90, "vitA_ug": 0.80, "vitC_mg": 0.45,
        "costo_extra": 1.5,
    },
    "al_vapor": {
        "kcal": 0.97, "proteina_g": 0.98, "hierro_mg": 0.95,
        "calcio_mg": 0.92, "vitA_ug": 0.92, "vitC_mg": 0.80,
        "costo_extra": 0.5,
    },
    "guisado": {
        "kcal": 1.10, "proteina_g": 0.96, "hierro_mg": 0.92,
        "calcio_mg": 0.88, "vitA_ug": 0.85, "vitC_mg": 0.55,
        "costo_extra": 1.0,
    },
}
LISTA_TECNICAS = list(TECNICAS_PREPARACION.keys())


GRUPOS_SUSTITUCION = {
    "proteina_animal": ["chicken", "beef", "tuna", "egg"],
    "leguminosa":      ["beans, black", "lentil"],
    "cereal":          ["rice", "oat", "tortilla"],
    "verdura_a":       ["broccoli", "spinach", "squash"],
    "verdura_b":       ["tomato", "carrot"],
    "fruta":           ["banana", "apple"],
    "lacteo":          ["milk", "cheese"],
    "tuberculo":       ["potato"],
}

PALETTE = {
    "bg":      "#0D1117", "panel":   "#161B22",
    "accent1": "#58A6FF", "accent2": "#3FB950",
    "accent3": "#F78166", "accent4": "#D2A8FF",
    "accent5": "#FFA657", "text":    "#E6EDF3",
    "muted":   "#8B949E", "grid":    "#21262D",
}

TOP3_COLORS = [PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent3"]]
