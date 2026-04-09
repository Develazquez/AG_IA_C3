from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from constants import PATH_USDA_ZIP, PATH_FAO, PATH_PROFECO, PATH_REQS, PALETTE
from loaders import cargar_usda, cargar_fao, cargar_profeco, enriquecer_costos, cargar_requerimientos
from platillos import construir_platillos
from genetic_algorithm import MenuGeneticAlgorithm
from charts import graficar_evolucion, graficar_dashboard_top3, graficar_descomposicion_fitness, imprimir_menu

# Variable global para mantener los datasets en memoria y no recargarlos en cada petición
app_data = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación. Se ejecuta al arrancar el servidor."""
    print("\nInicializando servidor... Cargando datasets reales, esto tomará unos segundos.")
    df_usda = cargar_usda(PATH_USDA_ZIP)
    df_fao = cargar_fao(PATH_FAO)
    df_alimentos = pd.concat([df_usda, df_fao], ignore_index=True)
    df_alimentos.index.name = "id"
    precios = cargar_profeco(PATH_PROFECO)
    df_alimentos = enriquecer_costos(df_alimentos, precios)
    df_reqs = cargar_requerimientos(PATH_REQS)
    
    app_data["df_alimentos"] = df_alimentos
    app_data["df_reqs"] = df_reqs
    app_data["precios"] = precios
    
    # Creamos un catálogo de platillos por defecto (con todos los ingredientes)
    app_data["df_platillos_default"] = construir_platillos(df_alimentos, None)
    
    print("✓ Datasets cargados en memoria. Servidor listo.")
    yield
    # Limpieza al apagar el servidor
    app_data.clear()

app = FastAPI(lifespan=lifespan, title="API de MenuGen-DIF v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorios si no existen y montarlos para que el frontend pueda acceder a las imágenes/CSVs
dir_base = os.path.dirname(os.path.abspath(__file__))
dir_outputs = os.path.join(dir_base, "outputs")
os.makedirs(os.path.join(dir_outputs, "graphs"), exist_ok=True)
os.makedirs(os.path.join(dir_outputs, "menus"), exist_ok=True)

app.mount("/outputs", StaticFiles(directory=dir_outputs), name="outputs")


# Estructura del JSON que el frontend debe enviar
class MenuRequest(BaseModel):
    edad_min: int = 6
    edad_max: int = 9
    presupuesto_max: float = 2000.0
    ingredientes_disponibles: Optional[List[str]] = None
    sexo: str = "ambos"
    tamano_poblacion: int = 100
    generaciones: int = 150


@app.post("/api/generar-menus")
def generar_menus(req: MenuRequest):
    df_alimentos = app_data["df_alimentos"]
    df_reqs = app_data["df_reqs"]
    
    # Si el usuario especifica ingredientes, reconstruimos el catálogo solo para esta petición
    if req.ingredientes_disponibles is not None:
        df_platillos = construir_platillos(df_alimentos, set(req.ingredientes_disponibles))
    else:
        df_platillos = app_data["df_platillos_default"]
        
    ag = MenuGeneticAlgorithm(
        df_alimentos=df_alimentos,
        df_requerimientos=df_reqs,
        df_platillos=df_platillos,
        edad_rango=(req.edad_min, req.edad_max),
        sexo=req.sexo,
        presupuesto_max=req.presupuesto_max,
        tamano_poblacion=req.tamano_poblacion,
        generaciones=req.generaciones,
    )
    
    # Ejecutamos el algoritmo
    mejor_individuo, mejor_metricas, historial = ag.ejecutar()
    
    dfs_menu = []
    tops_response = []
    
    # Procesar el Top 3 y extraer información para el JSON
    for rank, (fit_val, ind, met) in enumerate(ag.top3):
        met["_alimentos_ref"] = df_alimentos
        df_m = imprimir_menu(ind, df_platillos, met, rank=rank + 1)
        dfs_menu.append(df_m)
        
        # Convertimos el dataframe del menú a una lista de diccionarios para el frontend
        tops_response.append({
            "rank": rank + 1,
            "fitness": round(fit_val, 4),
            "costo": round(met["costo_total"], 2),
            "variedad_platillos": round(met["variedad_platillos"], 2),
            "densidad_micro": round(met["densidad_micro"], 3),
            "menu_diario": df_m.to_dict(orient="records")
        })

    # Generamos los gráficos
    fig_evo = graficar_evolucion(historial, req.generaciones)
    fig_nut = graficar_dashboard_top3(ag.top3, ag.reqs_filtrados, (req.edad_min, req.edad_max))
    fig_dec = graficar_descomposicion_fitness(ag.top3)
    
    dir_graphs = os.path.join(dir_outputs, "graphs")
    dir_menus  = os.path.join(dir_outputs, "menus")

    path_evo = os.path.join(dir_graphs, "evolucion_fitness_v2.png")
    path_nut = os.path.join(dir_graphs, "dashboard_nutricional_top3.png")
    path_dec = os.path.join(dir_graphs, "descomposicion_fitness.png")
    
    # Guardamos físicamente los PNGs
    fig_evo.savefig(path_evo, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    fig_nut.savefig(path_nut, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    fig_dec.savefig(path_dec, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    
    # Importante: Limpiar memoria de matplotlib en servidores para evitar fugas de RAM
    plt.close('all')

    menus_csv_paths = []
    for i, df_m in enumerate(dfs_menu):
        path = os.path.join(dir_menus, f"menu_semanal_top{i+1}.csv")
        df_m.to_csv(path, index=False)
        menus_csv_paths.append(f"/outputs/menus/menu_semanal_top{i+1}.csv")
        
    return {
        "status": "success",
        "parametros": req.dict(),
        "top_menus": tops_response,
        "imagenes_urls": {
            "evolucion": "/outputs/graphs/evolucion_fitness_v2.png",
            "dashboard": "/outputs/graphs/dashboard_nutricional_top3.png",
            "descomposicion": "/outputs/graphs/descomposicion_fitness.png"
        },
        "menus_csv_urls": menus_csv_paths
    }
