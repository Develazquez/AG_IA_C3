import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Tuple, Dict

from constants import DIAS, COMIDAS, PALETTE, TOP3_COLORS


def graficar_evolucion(historial: Dict, generaciones: int) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor=PALETTE["bg"])

    ax = axes[0]
    ax.set_facecolor(PALETTE["panel"])
    gens = range(1, len(historial["mejor_fitness"]) + 1)
    ax.plot(gens, historial["mejor_fitness"], color=PALETTE["accent1"], lw=2,
            label="Mejor Fitness")
    ax.plot(gens, historial["promedio_fitness"], color=PALETTE["accent4"], lw=1.5,
            linestyle="--", alpha=0.8, label="Promedio Fitness")
    ax.fill_between(gens, historial["mejor_fitness"], historial["promedio_fitness"],
                    alpha=0.1, color=PALETTE["accent1"])
    ax.set_xlabel("Generación", color=PALETTE["muted"])
    ax.set_ylabel("Fitness (menor = mejor)", color=PALETTE["muted"])
    ax.set_title("Convergencia del Fitness", color=PALETTE["text"],
                 fontsize=12, fontweight="bold")
    ax.tick_params(colors=PALETTE["muted"])
    for sp in ax.spines.values():
        sp.set_color(PALETTE["grid"])
    ax.grid(True, color=PALETTE["grid"], linewidth=0.5, alpha=0.7)
    ax.legend(facecolor=PALETTE["panel"], labelcolor=PALETTE["text"])

                            
    ax2 = axes[1]
    ax2.set_facecolor(PALETTE["panel"])
    ax2.plot(gens, historial["diversidad"], color=PALETTE["accent5"], lw=2)
    ax2.set_xlabel("Generación", color=PALETTE["muted"])
    ax2.set_ylabel("Diversidad (variedad promedio)", color=PALETTE["muted"])
    ax2.set_title("Diversidad Poblacional", color=PALETTE["text"],
                  fontsize=12, fontweight="bold")
    ax2.tick_params(colors=PALETTE["muted"])
    for sp in ax2.spines.values():
        sp.set_color(PALETTE["grid"])
    ax2.grid(True, color=PALETTE["grid"], linewidth=0.5, alpha=0.7)

    fig.tight_layout()
    return fig


def graficar_dashboard_top3(top3: List[Tuple], reqs_filtrados: Dict,
                             edad_rango: Tuple[int, int]) -> plt.Figure:

    nutrientes_labels = {
        "proteina_g": "Proteína (g)", "hierro_mg":  "Hierro (mg)",
        "calcio_mg":  "Calcio (mg)",  "vitA_ug":    "Vit. A (µg)",
        "vitC_mg":    "Vit. C (mg)",  "kcal":       "Energía (kcal)",
    }

    fig = plt.figure(figsize=(16, 10), facecolor=PALETTE["bg"])
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.5, wspace=0.4)
    fig.suptitle(
        f"Dashboard Nutricional — Comparación op-3 Menús\n"
        f"Edad: {edad_rango[0]}-{edad_rango[1]} años | NOM-169-SSA1 / DIF Chiapas",
        color=PALETTE["text"], fontsize=14, fontweight="bold", y=0.98)

    nut_order = ["proteina_g", "hierro_mg", "calcio_mg", "vitA_ug", "vitC_mg", "kcal"]

    for idx, nut in enumerate(nut_order):
        row, col = divmod(idx, 3)
        ax = fig.add_subplot(gs[row, col])
        ax.set_facecolor(PALETTE["panel"])

        rmin, rmax = reqs_filtrados[nut]
        req_mid = (rmin + rmax) / 2

                               
        x_positions = [0, 1]
        ax.bar(x_positions, [rmin, req_mid],
               color=[PALETTE["accent4"], PALETTE["muted"]],
               width=0.35, zorder=3, alpha=0.6)
        ax.axhline(rmax, color=PALETTE["accent3"], lw=1.5, linestyle="--",
                    alpha=0.8, label="Máx NOM" if idx == 0 else "")

                                       
        for rank, (fit_val, ind, metricas) in enumerate(top3):
            nut_daily = metricas["nutricion_diaria"]
            consumo = float(np.mean([d[nut] for d in nut_daily]))
            x = 2.5 + rank * 0.45
            color = TOP3_COLORS[rank]
            if consumo < rmin or consumo > rmax:
                color = "#FF7B72"
            ax.bar(x, consumo, color=color, width=0.4, zorder=3)
            ax.text(x, consumo * 1.02, f"{consumo:.1f}", ha="center",
                    color=PALETTE["text"], fontsize=7, fontweight="bold")

        labels = ["Mín", "Óptimo"] + [f"#{r+1}" for r in range(len(top3))]
        ax.set_xticks(x_positions + [2.5 + r * 0.45 for r in range(len(top3))])
        ax.set_xticklabels(labels, color=PALETTE["muted"], fontsize=7)
        ax.set_title(nutrientes_labels[nut], color=PALETTE["text"],
                     fontsize=10, fontweight="bold")
        ax.tick_params(colors=PALETTE["muted"], labelsize=8)
        for sp in ax.spines.values():
            sp.set_color(PALETTE["grid"])
        ax.grid(True, axis="y", color=PALETTE["grid"], linewidth=0.5, alpha=0.5)

    fig.text(0.5, 0.01,
             "  |  ".join([f"● Menú #{r+1} (fit={top3[r][0]:.4f})"
                           for r in range(len(top3))]),
             ha="center", color=PALETTE["text"], fontsize=10)

    return fig


def graficar_descomposicion_fitness(top3: List[Tuple]) -> plt.Figure:

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["panel"])

    componentes = ["f_enom", "f_costo", "f_variedad", "f_dmicro", "pen_presupuesto"]
    labels_comp = ["Error Nutric.", "Costo", "Variedad", "Dens. Micro", "Pen. Presup."]
    colors_comp = [PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent4"],
                   PALETTE["accent5"], PALETTE["accent3"]]

    x = np.arange(len(top3))
    width = 0.5
    bottom = np.zeros(len(top3))

    for ci, comp in enumerate(componentes):
        vals = [t[2].get(comp, 0) for t in top3]
        ax.bar(x, vals, width, bottom=bottom, color=colors_comp[ci],
               label=labels_comp[ci], zorder=3)
        bottom += np.array(vals)

    ax.set_xticks(x)
    ax.set_xticklabels([f"Menú #{i+1}" for i in range(len(top3))],
                       color=PALETTE["text"])
    ax.set_ylabel("Contribución al Fitness", color=PALETTE["muted"])
    ax.set_title("Descomposición del Fitness — Top-3 Menús",
                 color=PALETTE["text"], fontsize=12, fontweight="bold")
    ax.tick_params(colors=PALETTE["muted"])
    for sp in ax.spines.values():
        sp.set_color(PALETTE["grid"])
    ax.grid(True, axis="y", color=PALETTE["grid"], linewidth=0.5, alpha=0.5)
    ax.legend(facecolor=PALETTE["panel"], labelcolor=PALETTE["text"],
              fontsize=8, loc="upper right")

    fig.tight_layout()
    return fig


def imprimir_menu(individuo, df_platillos: pd.DataFrame,
                  metricas: Dict, rank: int = 1) -> pd.DataFrame:

    filas = []
    for dia_idx, dia in enumerate(DIAS):
        for comida_idx, comida in enumerate(COMIDAS):
            gen_idx = dia_idx * 3 + comida_idx
            pid, factor, sust, tecnica = individuo[gen_idx]
            nombre = df_platillos.loc[pid, "nombre"]
            porcion = df_platillos.loc[pid, "porcion_base_g"]
            costo = metricas["costos_comida"][gen_idx]

            row_plat = df_platillos.loc[pid]
            ings_nombres = []
            for i, (id_orig, gr) in enumerate(row_plat["ingredientes"]):
                alts = row_plat["alternativas"][i]
                id_real = alts[sust[i] % len(alts)] if i < len(sust) else id_orig
                if id_real in metricas.get("_alimentos_ref", pd.DataFrame()).index:
                    ings_nombres.append(
                        metricas["_alimentos_ref"].loc[id_real, "nombre"][:20])

            filas.append({
                "Día":         dia,
                "Comida":      comida,
                "Platillo":    nombre,
                "Técnica":     tecnica,
                "Factor":      factor,
                "Gramaje (g)": round(porcion * factor, 1),
                "Costo (MXN)": round(costo, 2),
            })

    df_menu = pd.DataFrame(filas)

    print(f"\n{'═' * 80}")
    print(f"  MENÚ SEMANAL #{rank} — MenuGen-DIF v2")
    print(f"{'═' * 80}")
    print(df_menu.to_string(index=False))
    print(f"{'═' * 80}")
    print(f"  Costo total semanal  : ${metricas['costo_total']:,.2f} MXN")
    print(f"  Variedad platillos   : {metricas['variedad_platillos']:.1%}  "
          f"({int(metricas['variedad_platillos'] * 21)} únicos / 21)")
    print(f"  Variedad ingredientes: {metricas['variedad_ingredientes']:.1%}")
    print(f"  Variedad técnicas    : {metricas['variedad_tecnicas']:.1%}")
    print(f"  Densidad micronut.   : {metricas['densidad_micro']:.3f} "
          f"(1.0 = cubre 100% reqs)")
    print(f"  Fitness total        : {metricas['fitness']:.4f}")
    print(f"{'═' * 80}\n")

    return df_menu
