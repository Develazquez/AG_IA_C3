import os
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
warnings.filterwarnings("ignore")

from constants import (
    PATH_USDA_ZIP, PATH_FAO, PATH_PROFECO, PATH_REQS,
    LISTA_TECNICAS, PATRONES_RECETA, PALETTE,
)
from loaders import (
    cargar_usda, cargar_fao, cargar_profeco,
    enriquecer_costos, cargar_requerimientos,
)
from platillos import construir_platillos
from genetic_algorithm import MenuGeneticAlgorithm
from charts import (
    graficar_evolucion,
    graficar_dashboard_top3,
    graficar_descomposicion_fitness,
    imprimir_menu,
)


if __name__ == "__main__":
    print("=" * 65)
    print("  MenuGen-DIF — Sistema de optimización de menús escolares")
    print("=" * 65)
    print("\nCargando datasets reales")

    print("  → USDA Foundation Foods...")
    df_usda = cargar_usda(PATH_USDA_ZIP)
    print(f"     {len(df_usda)} alimentos USDA")

    print("  → FAO INFOODS México...")
    df_fao = cargar_fao(PATH_FAO)
    print(f"     {len(df_fao)} alimentos FAO")

    df_alimentos = pd.concat([df_usda, df_fao], ignore_index=True)
    df_alimentos.index.name = "id"
    print(f"  → Total alimentos: {len(df_alimentos)}")

    print("  → PROFECO precios...")
    precios = cargar_profeco(PATH_PROFECO)
    df_alimentos = enriquecer_costos(df_alimentos, precios)
    print(f"     {len(precios)} productos con precio real")

    print("  → Requerimientos nutricionales DIF...")
    df_reqs = cargar_requerimientos(PATH_REQS)
    print(f"     {len(df_reqs)} registros de requerimientos")


    INGREDIENTES_DISPONIBLES = None  

    print("  → Construyendo catálogo de platillos...")
    df_platillos = construir_platillos(df_alimentos, INGREDIENTES_DISPONIBLES)
    print(f"     {len(df_platillos)} platillos generados dinámicamente desde los datasets")
    print(f"     Patrones de receta activos: {len(PATRONES_RECETA)}")
    print(f"     Técnicas de preparación: {LISTA_TECNICAS}")

    print("\nDatasets listos.\n")

    print("=" * 65)
    print("  Menú")
    print("=" * 65)
    while True:
        try:
            print("\n  Rangos de edad disponibles (NOM-169-SSA1 / DIF):")
            print("    1) 1-3 años   (preescolar temprano)")
            print("    2) 4-5 años   (preescolar)")
            print("    3) 6-9 años   (escolar primaria baja)")
            print("    4) 10-12 años (escolar primaria alta)")
            print("    5) 13-15 años (adolescente)")
            print("    6) Personalizado")
            opcion_edad = input("\n  Seleccione una opción [1-6] (default: 3): ").strip()
            if opcion_edad == "" or opcion_edad == "3":
                EDAD_RANGO = (6, 9)
            elif opcion_edad == "1":
                EDAD_RANGO = (1, 3)
            elif opcion_edad == "2":
                EDAD_RANGO = (4, 5)
            elif opcion_edad == "4":
                EDAD_RANGO = (10, 12)
            elif opcion_edad == "5":
                EDAD_RANGO = (13, 15)
            elif opcion_edad == "6":
                edad_min = int(input("  Edad mínima (años): ").strip())
                edad_max = int(input("  Edad máxima (años): ").strip())
                if edad_min < 1 or edad_max > 18 or edad_min > edad_max:
                    print("  Rango inválido. Debe ser entre 1 y 18 años, min ≤ max.")
                    continue
                EDAD_RANGO = (edad_min, edad_max)
            else:
                print("  Opción no válida.")
                continue
            print(f"   Rango de edad: {EDAD_RANGO[0]}-{EDAD_RANGO[1]} años")
            break
        except ValueError:
            print("  Entrada inválida. Ingrese un número entero.")
    while True:
        try:
            entrada_pres = input(
                f"\n  Presupuesto máximo semanal en MXN (default: 3500): "
            ).strip()
            if entrada_pres == "":
                PRESUPUESTO_MAX = 3500.0
            else:
                PRESUPUESTO_MAX = float(entrada_pres)
                if PRESUPUESTO_MAX <= 0:
                    print("  El presupuesto debe ser mayor a $0.")
                    continue
            print(f"   Presupuesto semanal: ${PRESUPUESTO_MAX:,.2f} MXN")
            break
        except ValueError:
            print("  Entrada inválida. Ingrese un número (ej: 2000 o 1500.50)")

    print(f"\n{'─' * 65}")

    SEXO             = "ambos"
    TAMANO_POBLACION = 100
    GENERACIONES     = 150
    PROB_CRUCE       = 0.85
    PROB_MUTACION    = 0.15
    PESOS            = (0.4, 0.3, 0.2, 0.1)
    SEMILLA          = 42

    ag = MenuGeneticAlgorithm(
        df_alimentos=df_alimentos,
        df_requerimientos=df_reqs,
        df_platillos=df_platillos,
        edad_rango=EDAD_RANGO,
        sexo=SEXO,
        presupuesto_max=PRESUPUESTO_MAX,
        tamano_poblacion=TAMANO_POBLACION,
        generaciones=GENERACIONES,
        prob_cruce=PROB_CRUCE,
        prob_mutacion=PROB_MUTACION,
        pesos=PESOS,
        semilla=SEMILLA,
    )

    mejor_individuo, mejor_metricas, historial = ag.ejecutar()

    print("\n" + "=" * 65)
    print("  Top 3 menús")
    print("=" * 65)

    dfs_menu = []
    for rank, (fit_val, ind, met) in enumerate(ag.top3):
        met["_alimentos_ref"] = df_alimentos
        df_m = imprimir_menu(ind, df_platillos, met, rank=rank + 1)
        dfs_menu.append(df_m)

    fig_evo = graficar_evolucion(historial, GENERACIONES)
    fig_nut = graficar_dashboard_top3(ag.top3, ag.reqs_filtrados, EDAD_RANGO)
    fig_dec = graficar_descomposicion_fitness(ag.top3)

    plt.show()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_graphs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", f"run_{timestamp}", "graphs")
    dir_menus  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", f"run_{timestamp}", "menus")
    os.makedirs(dir_graphs, exist_ok=True)
    os.makedirs(dir_menus, exist_ok=True)

    fig_evo.savefig(os.path.join(dir_graphs, "evolucion_fitness_v2.png"), dpi=150,
                    bbox_inches="tight", facecolor=PALETTE["bg"])
    fig_nut.savefig(os.path.join(dir_graphs, "dashboard_nutricional_top3.png"), dpi=150,
                    bbox_inches="tight", facecolor=PALETTE["bg"])
    fig_dec.savefig(os.path.join(dir_graphs, "descomposicion_fitness.png"), dpi=150,
                    bbox_inches="tight", facecolor=PALETTE["bg"])

    for i, df_m in enumerate(dfs_menu):
        df_m.to_csv(os.path.join(dir_menus, f"menu_semanal_top{i+1}.csv"), index=False)

    print("\n Archivos guardados:")
    print(f"  {os.path.join(dir_graphs, 'evolucion_fitness_v2.png')}")
    print(f"  {os.path.join(dir_graphs, 'dashboard_nutricional_top3.png')}")
    print(f"  {os.path.join(dir_graphs, 'descomposicion_fitness.png')}")
    for i in range(len(dfs_menu)):
        print(f"  {os.path.join(dir_menus, f'menu_semanal_top{i+1}.csv')}")