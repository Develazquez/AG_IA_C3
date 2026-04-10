# MenuGen-DIF — Sistema de Optimización de Menús Escolares (Version para frontend)

![Aesthetics](https://img.shields.io/badge/Aesthetics-Premium-blueviolet)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**MenuGen-DIF** es una herramienta avanzada que utiliza **Algoritmos Genéticos** para diseñar y optimizar menús escolares semanales. El sistema equilibra los requerimientos nutricionales establecidos por la **NOM-169-SSA1** y el **DIF**, ajustándose a un presupuesto máximo y garantizando la variedad culinaria.

> [!NOTE]
> Para ejecutar el proyecto con frontend, se debe ejecutar el comando `npm run dev` en la carpeta `FE_AG_IA_C3` y `uvicorn api:app --reload` en la carpeta `AG_IA_C3`.   

---

## Características Principales

- **Optimización Multiobjetivo**: Maximiza la adecuación nutricional (calorías, proteínas, hierro, calcio, vitaminas A y C) mientras minimiza el costo.
- **Datasets Reales**: Integra datos de:
  - **USDA Foundation Foods**: Base de datos nutricional global.
  - **FAO INFOODS México**: Datos específicos de alimentos locales.
  - **PROFECO**: Precios actualizados de productos en México.
- **Generación Dinámica**: Crea platillos combinando ingredientes y técnicas de preparación (hervido, asado, vapor, etc.) con penalizaciones por alimentos ultraprocesados.
- **Visualización Premium**: Dashboard automático con la evolución de la salud de la población (fitness) y comparativas de menús.

---

## Requisitos e Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/Develazquez/AG_IA_C3.git
cd AG_IA_C3
git checkout frontendVersion
```

### 2. Configurar el entorno virtual (Recomendado)
En Windows:
```powershell
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## Datasets Necesarios

Los siguientes archivos deben estar en la carpeta `datasets/`:
- `FoodData_Central_foundation_food_csv_2025-12-18.zip` (USDA)
- `TABLAS_ALIMENTOS.csv` (FAO México)
- `11-2025_01.csv` (Precios PROFECO)
- `requerimientos_nutricionales_dif.csv` (Estándares DIF)

---

## Cómo Ejecutar

Para iniciar el proyecto con frontend, simplemente ejecuta:

```bash
uvicorn api:app --reload
```

### Proceso Interactivo:
1.  **Selección de Edad**: El sistema te pedirá elegir un rango de edad (desde preescolar hasta adolescentes) para ajustar los requerimientos nutricionales.
2.  **Presupuesto**: Ingresa el presupuesto máximo semanal (en MXN).
3.  **Ejecución del AG**: El algoritmo genético procesará 150 generaciones para encontrar los 3 mejores menús.
4.  **Resultados**: Se abrirán gráficas interactivas con el análisis de resultados.

---

## Salidas (Outputs)

Cada ejecución genera:
- **`Graficas`**:
  - `evolucion_fitness.png`: Progreso del algoritmo.
  - `dashboard_nutricional.png`: Comparativa nutricional vs requerimientos.
  - `descomposicion_fitness.png`: Análisis de qué factores influyeron en la selección.
- **`Menus`**:
  - `menu_semanal_top1.csv`: El mejor menú encontrado (Lunes a Domingo, Desayuno-comida-cena).
  - `menu_semanal_top2.csv` y `top3.csv`: Alternativas de alta calidad.

---

## Estructura del Código

- `main.py`: Punto de entrada y CLI interactivo.
- `genetic_algorithm.py`: El "cerebro" que maneja la evolución, cruce y mutación.
- `platillos.py`: Lógica para la construcción de recetas y combinaciones de ingredientes.
- `loaders.py`: Limpieza y carga de datos masivos.
- `charts.py`: Generación de gráficos con estética oscura (Matplotlib).
- `constants.py`: Configuración de umbrales, pesos y rutas.
- `api.py`: API REST para la comunicación entre el frontend y el backend.
---

> [!NOTE]
> Este proyecto fue desarrollado para la asignatura de inteligencia artificial 
