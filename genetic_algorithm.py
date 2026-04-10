import numpy as np
import pandas as pd
import random as rng
from copy import deepcopy
from typing import List, Tuple, Dict, Optional

from constants import (
    NUTRIENTES, TECNICAS_PREPARACION, LISTA_TECNICAS,
)


Gen = Tuple[int, float, Tuple[int, ...], str]
Individuo = List[Gen]


class MenuGeneticAlgorithm:

    def __init__(
        self,
        df_alimentos:      pd.DataFrame,
        df_requerimientos: pd.DataFrame,
        df_platillos:      pd.DataFrame,
        edad_rango:        Tuple[int, int] = (6, 9),
        sexo:              str = "ambos",
        presupuesto_max:   float = 3500.0,
        tamano_poblacion:  int = 100,
        generaciones:      int = 150,
        prob_cruce:        float = 0.85,
        prob_mutacion:     float = 0.15,
        pesos:             Tuple[float, float, float, float] = (0.4, 0.3, 0.2, 0.1),
        semilla:           Optional[int] = 42,
    ):
        if semilla is not None:
            np.random.seed(semilla)
            rng.seed(semilla)

        self.alimentos      = df_alimentos
        self.reqs           = df_requerimientos
        self.platillos      = df_platillos
        self.edad_rango     = edad_rango
        self.sexo           = sexo
        self.presupuesto_max = presupuesto_max
        self.pop_size       = tamano_poblacion
        self.generaciones   = generaciones
        self.prob_cruce     = prob_cruce
        self.prob_mutacion  = prob_mutacion
        self.w1, self.w2, self.w3, self.w4 = pesos

        self.ids_platillos = list(self.platillos.index)
        self.n_platillos   = len(self.ids_platillos)

        self.reqs_filtrados = self._filtrar_requerimientos()
        self._max_costo_posible = self._estimar_costo_maximo()

        self.top3: List[Tuple[float, Individuo, Dict]] = []

    def _filtrar_requerimientos(self) -> Dict[str, Tuple[float, float]]:
        edad_mid = (self.edad_rango[0] + self.edad_rango[1]) / 2
        resultado: Dict[str, Tuple[float, float]] = {}
        for nut in NUTRIENTES:
            sub = self.reqs[self.reqs["nutriente"] == nut]
            if "sexo" in sub.columns:
                sub = sub[sub["sexo"].isin([self.sexo, "ambos"])]
            fila = sub[
                (sub["edad_min"] <= edad_mid) & (sub["edad_max"] >= edad_mid)
            ]
            if fila.empty:
                fila = sub.iloc[[0]] if len(sub) > 0 else pd.DataFrame(
                    [{"rmin_diario": 0, "rmax_diario": 9999}])
            resultado[nut] = (
                float(fila["rmin_diario"].mean()),
                float(fila["rmax_diario"].mean()),
            )
        return resultado

    def _estimar_costo_maximo(self) -> float:
        costos = []
        for pid in self.ids_platillos:
            tecnicas = self.platillos.loc[pid, "tecnicas_permitidas"]
            max_extra = max(TECNICAS_PREPARACION[t]["costo_extra"] for t in tecnicas)
            c = self._costo_platillo_base(pid, 2.0) + max_extra
            costos.append(c)
        return 21 * max(costos) if costos else 1.0

    def _costo_platillo_base(self, id_platillo: int, factor: float,
                              sustituciones: Optional[Tuple[int, ...]] = None) -> float:
        row_plat = self.platillos.loc[id_platillo]
        ingredientes = row_plat["ingredientes"]
        alternativas = row_plat["alternativas"]
        costo = 0.0
        for i, (id_al_orig, gramos_base) in enumerate(ingredientes):
                                              
            if sustituciones is not None and i < len(sustituciones):
                alts = alternativas[i]
                id_al = alts[sustituciones[i] % len(alts)]
            else:
                id_al = id_al_orig
            if id_al in self.alimentos.index:
                gramos = gramos_base * factor
                costo += (gramos / 100.0) * float(self.alimentos.loc[id_al, "costo_por_100g"])
        return costo

    def _costo_comida(self, gen: Gen) -> float:
        pid, factor, sust, tecnica = gen
        base = self._costo_platillo_base(pid, factor, sust)
        extra = TECNICAS_PREPARACION[tecnica]["costo_extra"]
        return base + extra

    def _nutricion_platillo(self, pid: int, factor: float,
                             sustituciones: Optional[Tuple[int, ...]] = None,
                             tecnica: str = "hervido") -> Dict[str, float]:
        row_plat = self.platillos.loc[pid]
        ingredientes = row_plat["ingredientes"]
        alternativas = row_plat["alternativas"]

        col_map = {
            "kcal":       "kcal_100g",
            "proteina_g": "proteina_g",
            "hierro_mg":  "hierro_mg",
            "calcio_mg":  "calcio_mg",
            "vitA_ug":    "vitA_ug",
            "vitC_mg":    "vitC_mg",
        }
        nut = {k: 0.0 for k in NUTRIENTES}

        for i, (id_al_orig, gramos_base) in enumerate(ingredientes):
            if sustituciones is not None and i < len(sustituciones):
                alts = alternativas[i]
                id_al = alts[sustituciones[i] % len(alts)]
            else:
                id_al = id_al_orig

            if id_al in self.alimentos.index:
                gramos = gramos_base * factor
                row = self.alimentos.loc[id_al]
                for k, col in col_map.items():
                    val = row.get(col, 0)
                    if pd.notna(val):
                        nut[k] += (gramos / 100.0) * float(val)

        ret = TECNICAS_PREPARACION[tecnica]
        for k in nut:
            nut[k] *= ret.get(k, 1.0)

        return nut


    def _rand_gen(self) -> Gen:
        pid = rng.choice(self.ids_platillos)
        factor = round(rng.uniform(0.5, 2.0), 2)
        row_plat = self.platillos.loc[pid]
        n_ings = len(row_plat["ingredientes"])
        sust = tuple(
            rng.randint(0, max(0, len(row_plat["alternativas"][i]) - 1))
            for i in range(n_ings)
        )
        tecnica = rng.choice(row_plat["tecnicas_permitidas"])
        return (pid, factor, sust, tecnica)

    def crear_individuo(self) -> Individuo:
        return [self._rand_gen() for _ in range(21)]

    def decodificar(self, individuo: Individuo) -> Dict:
        nutricion_diaria = []
        costos_comida = []
        costo_total = 0.0
        platillos_usados = []
        ingredientes_usados = []
        tecnicas_usadas = []

        for dia in range(7):
            nut_dia = {k: 0.0 for k in NUTRIENTES}
            for comida in range(3):
                idx = dia * 3 + comida
                pid, factor, sust, tecnica = individuo[idx]
                nut_c = self._nutricion_platillo(pid, factor, sust, tecnica)
                for k in nut_dia:
                    nut_dia[k] += nut_c[k]
                c = self._costo_comida(individuo[idx])
                costos_comida.append(c)
                costo_total += c
                platillos_usados.append(pid)
                tecnicas_usadas.append(tecnica)

                row_plat = self.platillos.loc[pid]
                for i, (id_orig, _) in enumerate(row_plat["ingredientes"]):
                    alts = row_plat["alternativas"][i]
                    id_real = alts[sust[i] % len(alts)] if i < len(sust) else id_orig
                    ingredientes_usados.append(id_real)

            nutricion_diaria.append(nut_dia)

        variedad_platillos = len(set(platillos_usados)) / 21.0
        variedad_ingredientes = len(set(ingredientes_usados)) / max(len(ingredientes_usados), 1)
        variedad_tecnicas = len(set(tecnicas_usadas)) / max(len(LISTA_TECNICAS), 1)

        kcal_total = sum(d["kcal"] for d in nutricion_diaria)
        densidad_scores = []
        for nut_key in ["hierro_mg", "calcio_mg", "vitA_ug", "vitC_mg"]:
            rmin, rmax = self.reqs_filtrados[nut_key]
            req_mid = (rmin + rmax) / 2.0
            consumo_total = sum(d[nut_key] for d in nutricion_diaria)
            consumo_diario = consumo_total / 7.0
           
            if req_mid > 0:
                densidad_scores.append(min(consumo_diario / req_mid, 1.5))
            else:
                densidad_scores.append(1.0)
        densidad_micro = float(np.mean(densidad_scores))

        return {
            "nutricion_diaria":      nutricion_diaria,
            "costo_total":           costo_total,
            "costos_comida":         costos_comida,
            "variedad_platillos":    variedad_platillos,
            "variedad_ingredientes": variedad_ingredientes,
            "variedad_tecnicas":     variedad_tecnicas,
            "densidad_micro":        densidad_micro,
            "platillos_usados":      platillos_usados,
            "tecnicas_usadas":       tecnicas_usadas,
        }

    def _error_nutricional(self, nutricion_diaria: List[Dict]) -> float:
        errores = []
        for nut_dia in nutricion_diaria:
            for nut, (rmin, rmax) in self.reqs_filtrados.items():
                req_medio = (rmin + rmax) / 2.0
                consumo = nut_dia.get(nut, 0.0)
                err = abs(consumo - req_medio) / max(req_medio, 1.0)
                if consumo < rmin:
                    err += 2.0 * (rmin - consumo) / max(rmin, 1.0)
                elif consumo > rmax:
                    err += 2.0 * (consumo - rmax) / max(rmax, 1.0)
                errores.append(err)
        raw = float(np.mean(errores))
        return 2.0 / (1.0 + np.exp(-raw)) - 1.0                  

    def _penalizacion_variedad(self, platillos_usados: List[int]) -> float:
        pen = 0.0
        conteo: Dict[int, int] = {}
        for pid in platillos_usados:
            conteo[pid] = conteo.get(pid, 0) + 1
                                
        for pid, cnt in conteo.items():
            if cnt > 2:
                pen += (cnt - 2)
                                              
        for dia in range(6):
            s1 = set(platillos_usados[dia * 3:dia * 3 + 3])
            s2 = set(platillos_usados[(dia + 1) * 3:(dia + 1) * 3 + 3])
            pen += len(s1 & s2)
                                       
        return min(pen / 39.0, 1.0)

    def _penalizacion_culinaria_y_ultraprocesados(self, individuo: Individuo) -> float:
        penalizacion = 0.0
        
                                                               
        listos_para_comer = [
            "queso", "cheese", "pan ", "bread", "jamon", "ham", "salchicha", "sausage", 
            "yogurt", "leche", "milk", "totopo", "tostada", "cracker", "cereal"
        ]
        crudos_obligatorios = [
            "raw chicken", "raw beef", "raw pork", "raw meat", "raw fish", "pollo crudo", 
            "carne cruda", "pescado crudo", "cerdo crudo", "raw egg", "huevo crudo", 
            "flour", "harina", "frijol crudo", "raw bean", "lenteja cruda", "raw lentil", "raw turkey"
        ]
        
        for pid, factor, sust, tecnica in individuo:
            row_plat = self.platillos.loc[pid]
            ingredientes = row_plat["ingredientes"]
            alternativas = row_plat["alternativas"]
            
            for i, (id_orig, _) in enumerate(ingredientes):
                if i < len(sust):
                    alts = alternativas[i]
                    id_real = alts[sust[i] % len(alts)]
                else:
                    id_real = id_orig
                    
                if id_real not in self.alimentos.index:
                    continue
                    
                row_al = self.alimentos.loc[id_real]
                nombre_lower = str(row_al["nombre"]).lower()
                
                                                                               
                                                     
                if tecnica in ["hervido", "asado", "frito", "guisado", "al_vapor"]:
                    if any(kw in nombre_lower for kw in listos_para_comer):
                        penalizacion += 10.0                                    
                        
                                                                                         
                if tecnica == "crudo":
                    if any(kw in nombre_lower for kw in crudos_obligatorios):
                        penalizacion += 15.0                    
                        
                                                                                          
                                                  
                kcal = row_al.get("kcal_100g", 0) or 0
                prot = row_al.get("proteina_g", 0) or 0
                hrro = row_al.get("hierro_mg", 0) or 0
                calc = row_al.get("calcio_mg", 0) or 0
                vitA = row_al.get("vitA_ug", 0) or 0
                vitC = row_al.get("vitC_mg", 0) or 0
                
                                                                                        
                                                                                            
                                                                          
                if kcal > 400.0 and prot < 5.0 and hrro < 1.0 and calc < 40.0 and vitA < 50.0 and vitC < 5.0:
                    penalizacion += 8.0 
                    
        return penalizacion

    def fitness(self, individuo: Individuo) -> Tuple[float, Dict]:
        dec = self.decodificar(individuo)

                                                 
        f_enom = self._error_nutricional(dec["nutricion_diaria"])

                                       
        f_costo = min(dec["costo_total"] / max(self._max_costo_posible, 1.0), 1.0)

                                        
        variedad_raw = (
            0.6 * dec["variedad_platillos"]
            + 0.25 * dec["variedad_ingredientes"]
            + 0.15 * dec["variedad_tecnicas"]
        )
        pen_var = self._penalizacion_variedad(dec["platillos_usados"])
        f_variedad = 1.0 - variedad_raw + 0.3 * pen_var
        f_variedad = min(max(f_variedad, 0.0), 1.0)

                                               
        f_dmicro = 1.0 - min(dec["densidad_micro"], 1.0)

                                                      
        pen_pres = 0.0
        if dec["costo_total"] > self.presupuesto_max:
            exceso = (dec["costo_total"] - self.presupuesto_max) / self.presupuesto_max
            pen_pres = min(exceso * 3.0, 1.0)                     

                                                       
        pen_culinaria = self._penalizacion_culinaria_y_ultraprocesados(individuo)
        f = (self.w1 * f_enom
             + self.w2 * f_costo
             + self.w3 * f_variedad
             + self.w4 * f_dmicro
             + pen_pres
             + pen_culinaria)

        metricas = {
            "f_enom":              f_enom,
            "f_costo":             f_costo,
            "f_variedad":          f_variedad,
            "f_dmicro":            f_dmicro,
            "pen_presupuesto":     pen_pres,
            "enom_raw":            f_enom,
            "costo_total":         dec["costo_total"],
            "costos_comida":       dec["costos_comida"],
            "variedad_platillos":  dec["variedad_platillos"],
            "variedad_ingredientes": dec["variedad_ingredientes"],
            "variedad_tecnicas":   dec["variedad_tecnicas"],
            "densidad_micro":      dec["densidad_micro"],
            "nutricion_diaria":    dec["nutricion_diaria"],
            "platillos_usados":    dec["platillos_usados"],
            "tecnicas_usadas":     dec["tecnicas_usadas"],
            "fitness":             f,
        }
        return f, metricas


    def _seleccion_torneo(self, poblacion: List[Individuo],
                           fitnesses: List[float], k: int = 3) -> Individuo:
        candidatos = rng.sample(range(len(poblacion)), k)
        ganador = min(candidatos, key=lambda i: fitnesses[i])
        return deepcopy(poblacion[ganador])

    def cruzar(self, p1: Individuo, p2: Individuo) -> Tuple[Individuo, Individuo]:
        if rng.random() > self.prob_cruce:
            return deepcopy(p1), deepcopy(p2)
                                                            
        pt1 = rng.randint(0, 20)
        pt2 = rng.randint(pt1 + 1, 21)
        h1 = p1[:pt1] + p2[pt1:pt2] + p1[pt2:]
        h2 = p2[:pt1] + p1[pt1:pt2] + p2[pt2:]
        return deepcopy(h1), deepcopy(h2)

    def mutar(self, individuo: Individuo) -> Individuo:
        nuevo = deepcopy(individuo)
        for i in range(len(nuevo)):
            if rng.random() < self.prob_mutacion:
                pid, factor, sust, tecnica = nuevo[i]
                r = rng.random()
                if r < 0.30:
                                             
                    nuevo[i] = self._rand_gen()
                elif r < 0.50:
                                                  
                    delta = rng.uniform(-0.3, 0.3)
                    nuevo[i] = (pid, round(max(0.5, min(2.0, factor + delta)), 2),
                                sust, tecnica)
                elif r < 0.70:
                                                
                    row_plat = self.platillos.loc[pid]
                    n_ings = len(row_plat["ingredientes"])
                    if n_ings > 0:
                        ing_idx = rng.randint(0, n_ings - 1)
                        n_alts = len(row_plat["alternativas"][ing_idx])
                        sust_list = list(sust)
                        sust_list[ing_idx] = rng.randint(0, max(0, n_alts - 1))
                        nuevo[i] = (pid, factor, tuple(sust_list), tecnica)
                else:
                                                        
                    tecnicas_perm = self.platillos.loc[pid, "tecnicas_permitidas"]
                    nuevo[i] = (pid, factor, sust, rng.choice(tecnicas_perm))
        return nuevo

    def _reparar(self, individuo: Individuo) -> Individuo:
        resultado = deepcopy(individuo)
        conteo: Dict[int, List[int]] = {}
        for i, (pid, _, _, _) in enumerate(resultado):
            conteo.setdefault(pid, []).append(i)

        for pid, posiciones in conteo.items():
            if len(posiciones) > 2:
                for pos in posiciones[2:]:
                    ca: Dict[int, int] = {}
                    for (p, _, _, _) in resultado:
                        ca[p] = ca.get(p, 0) + 1
                    candidatos = [p for p in self.ids_platillos if ca.get(p, 0) < 2]
                    if not candidatos:
                        candidatos = self.ids_platillos
                    new_pid = rng.choice(candidatos)
                                                               
                    row_plat = self.platillos.loc[new_pid]
                    n_ings = len(row_plat["ingredientes"])
                    sust = tuple(
                        rng.randint(0, max(0, len(row_plat["alternativas"][j]) - 1))
                        for j in range(n_ings)
                    )
                    tecnica = rng.choice(row_plat["tecnicas_permitidas"])
                    resultado[pos] = (new_pid, resultado[pos][1], sust, tecnica)
        return resultado


    def _actualizar_top3(self, fitness_val: float, individuo: Individuo,
                          metricas: Dict):
        entry = (fitness_val, deepcopy(individuo), deepcopy(metricas))
        if len(self.top3) < 3:
            self.top3.append(entry)
            self.top3.sort(key=lambda x: x[0])
        elif fitness_val < self.top3[-1][0]:
            plats = tuple(metricas["platillos_usados"])
            for _, _, m in self.top3:
                if tuple(m["platillos_usados"]) == plats:
                    return
            self.top3[-1] = entry
            self.top3.sort(key=lambda x: x[0])

                       

    def ejecutar(self) -> Tuple[Individuo, Dict, Dict]:
        poblacion = [self.crear_individuo() for _ in range(self.pop_size)]
        historial = {"mejor_fitness": [], "promedio_fitness": [],
                     "diversidad": []}
        mejor_individuo = None
        mejor_fitness = float("inf")
        mejor_metricas: Dict = {}
        elite_size = max(2, int(0.1 * self.pop_size))

        print(f"\n{'─' * 65}")
        print(f"  MenuGen-DIF | Pob: {self.pop_size} | Gen: {self.generaciones}")
        print(f"  Edad: {self.edad_rango} | Presupuesto: ${self.presupuesto_max:,.0f} MXN")
        print(f"  Variables: P_i (platillo) + G_i (porción) + I_i (ingrediente) + M_i (técnica)")
        print(f"{'─' * 65}")
        print(f"{'Gen':>5} │ {'Mejor':>8} │ {'Prom':>8} │ {'Costo':>10} │ "
              f"{'Var.P':>6} │ {'Var.I':>6} │ {'Div':>5}")
        print(f"{'─' * 65}")

        for gen in range(self.generaciones):
            evaluaciones = [self.fitness(ind) for ind in poblacion]
            fitnesses    = [e[0] for e in evaluaciones]
            metricas_pop = [e[1] for e in evaluaciones]

                                     
            divs = [m["variedad_platillos"] for m in metricas_pop]
            diversidad = float(np.mean(divs))

            idx_mejor = int(np.argmin(fitnesses))
            if fitnesses[idx_mejor] < mejor_fitness:
                mejor_fitness   = fitnesses[idx_mejor]
                mejor_individuo = deepcopy(poblacion[idx_mejor])
                mejor_metricas  = metricas_pop[idx_mejor]

                              
            for i in range(len(poblacion)):
                self._actualizar_top3(fitnesses[i], poblacion[i], metricas_pop[i])

            prom = float(np.mean(fitnesses))
            historial["mejor_fitness"].append(mejor_fitness)
            historial["promedio_fitness"].append(prom)
            historial["diversidad"].append(diversidad)

            if gen % 10 == 0 or gen == self.generaciones - 1:
                vp = mejor_metricas.get("variedad_platillos", 0)
                vi = mejor_metricas.get("variedad_ingredientes", 0)
                print(f"{gen + 1:>5} │ {mejor_fitness:>8.4f} │ {prom:>8.4f} │ "
                      f"${mejor_metricas.get('costo_total', 0):>9.2f} │ "
                      f"{vp:>5.1%} │ {vi:>5.1%} │ {diversidad:>5.2f}")

            if gen == self.generaciones - 1:
                break

            idx_elite = sorted(range(len(fitnesses)),
                               key=lambda i: fitnesses[i])[:elite_size]
            nueva_pob = [deepcopy(poblacion[i]) for i in idx_elite]

            while len(nueva_pob) < self.pop_size:
                p1 = self._seleccion_torneo(poblacion, fitnesses)
                p2 = self._seleccion_torneo(poblacion, fitnesses)
                h1, h2 = self.cruzar(p1, p2)
                h1 = self._reparar(self.mutar(h1))
                h2 = self._reparar(self.mutar(h2))
                nueva_pob.append(h1)
                if len(nueva_pob) < self.pop_size:
                    nueva_pob.append(h2)

            poblacion = nueva_pob

        print(f"{'─' * 65}")
        print(f"\n Evolución completada. Mejor fitness: {mejor_fitness:.4f}")
        print(f"  Top 3 fitness: {[round(t[0], 4) for t in self.top3]}")

        return mejor_individuo, mejor_metricas, historial
