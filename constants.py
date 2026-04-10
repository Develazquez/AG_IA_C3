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


                                                    
MAX_PLATILLOS = 70

                                                                                     
                                                                           
                                                                          
PALABRAS_EXCLUIDAS = {
                                                                               
    "flour", "pastry", "cookie", "cookies", "cake", "pie",
    "muffin", "donut", "brownie", "waffle", "cracker", "biscuit",
                                                                               
    "harina", "pastel", "galleta", "dona", "panque", "barquillo",
                                                                               
    "breaded", "par frie", "par-frie", "battered",
                                                                               
    "empanizado", "capeado", "rebozado",
                                                                               
    "paste", "powder", "powdered", "dry mix", "instant",
    "freeze-dried", "dehydrated", "unprepared, dry",
                                                                               
    "polvo", "deshidratado", "instantaneo", "instantáneo", "reconstituido",
                                                                               
    "ring", "rings", "chip", "chips", "snack", "pretzel",
                                                                               
    "frituras", "papas fritas",
                                                                               
    "sauce", "dressing", "ketchup", "mustard", "mayonnaise",
    "seasoning", "spice", "extract", "syrup", "condiment",
                                                                               
    "salsa", "aderezo", "catsup", "mostaza", "mayonesa",
    "sazonador", "extracto", "jarabe", "condimento",
                                                                                
    "baby", "infant", "formula",
                                                                                
    "papilla", "colada", "colado", "sopa con",
                                                                               
    "oil", "fat", "lard", "shortening", "margarine", "butter",
                                                                               
    "aceite", "manteca", "mantequilla", "margarina",
                                                                               
    "alcohol", "beer", "wine", "spirit", "liquor", "drink", "beverage", "juice",
                                                                               
    "bebida", "jugo", "nectar", "néctar", "cerveza", "vino",
    "aguardiente", "tepache", "pulque",
                                                                               
    "candy", "sugar", "pudding", "dessert", "ice cream", "gelatin", "jell",
                                                                               
    "dulce", "azucar", "azúcar", "postre", "helado", "gelatina",
    "paleta", "caramelo", "natilla",
                                                                               
    "overripe", "imitation", "canned", "restaurant", "fast food",
                                                                               
    "enlatado", "restaurante", "comida rapida", "comida rápida", "precocido",
                                                                                
    "otin",
}

                                                                             
                                                                  
 
                                            
                                                                          
                                                                  
                                                           
                                                                        
                                                                            
                                               
                                                                              
                                                 
UMBRALES_CLASIFICACION = [
                                                                                    
    ("lacteo",          {"calcio_mg": (100, None), "proteina_g": (2, 25),  "kcal_100g": (20, 500)}),
                                                                                        
                                                                
                                                                                      
                                                                                         
    ("proteina_animal", {"proteina_g": (10, None), "kcal_100g": (50, 550), "calcio_mg": (None, 80)}),
                                                                            
    ("leguminosa",      {"proteina_g": (5, 18),   "kcal_100g": (80, 400), "hierro_mg": (0.8, None)}),
                                         
    ("cereal",          {"kcal_100g": (170, None), "proteina_g": (2, 18)}),
                                                                                
    ("verdura_a",       {"kcal_100g": (None, 70),  "vitA_ug": (15, None)}),
                                                                                
    ("fruta",           {"kcal_100g": (20,  110),  "proteina_g": (None, 4), "vitC_mg": (5, None)}),
                                                      
    ("tuberculo",       {"kcal_100g": (65,  250),  "proteina_g": (None, 5)}),
                                                     
    ("verdura_b",       {"kcal_100g": (None, 80),  "proteina_g": (None, 5)}),
]

                                                         
                                                                              
PATRONES_RECETA = [
    ("Proteína con Cereal",     ["proteina_animal", "cereal"],     [100, 100], ["guisado", "hervido", "asado"]),
    ("Proteína con Verdura",    ["proteina_animal", "verdura_a"],  [100,  80], ["asado", "al_vapor", "guisado"]),
    ("Proteína con Tubérculo",  ["proteina_animal", "tuberculo"],  [ 80, 150], ["guisado", "hervido"]),
    ("Leguminosa de olla",      ["leguminosa"],                    [120],      ["hervido", "guisado"]),
    ("Leguminosa con Verdura",  ["leguminosa", "verdura_b"],       [100,  50], ["hervido", "guisado"]),
    ("Cereal con Lácteo",       ["cereal", "lacteo"],              [ 80, 200], ["hervido", "crudo"]),
    ("Cereal con Verdura",      ["cereal", "verdura_b"],           [100,  60], ["guisado", "frito"]),
    ("Verdura mixta",           ["verdura_a", "verdura_b"],        [ 80,  50], ["hervido", "al_vapor", "crudo"]),
    ("Fruta sola",              ["fruta"],                         [150],      ["crudo"]),
    ("Lácteo con Cereal",       ["lacteo", "cereal"],              [200,  60], ["crudo", "hervido"]),
    ("Tubérculo con Lácteo",    ["tuberculo", "lacteo"],           [150,  30], ["hervido"]),
    ("Proteína con Leguminosa", ["proteina_animal", "leguminosa"], [ 80,  80], ["guisado", "hervido"]),
]

PALETTE = {
    "bg":      "#0D1117", "panel":   "#161B22",
    "accent1": "#58A6FF", "accent2": "#3FB950",
    "accent3": "#F78166", "accent4": "#D2A8FF",
    "accent5": "#FFA657", "text":    "#E6EDF3",
    "muted":   "#8B949E", "grid":    "#21262D",
}

TOP3_COLORS = [PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent3"]]
