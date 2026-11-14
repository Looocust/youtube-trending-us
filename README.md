# Videos en tendencia de YouTube en Estados Unidos

Prueba práctica de ciencia de datos. Una empresa va a lanzar su marca en Estados Unidos y quiere posicionar su canal de YouTube. Este análisis busca entender qué caracteriza a los videos en tendencia para orientar la estrategia de contenido y la eventual elección de sponsors.

El enunciado completo está en [docs/enunciado.pdf](docs/enunciado.pdf).

## Preguntas que responde

1. ¿Qué categorías reciben más vistas y likes?
2. ¿Se pueden encontrar agrupaciones de videos?
3. ¿Qué atributos hacen que un video dure más o llegue más rápido a tendencia?
4. ¿Influye la fecha u hora de publicación?
5. ¿Se pueden predecir las vistas o los likes de un video?

## Metodología

Se sigue CRISP-DM. Cada notebook cubre una etapa:

| Notebook | Etapa CRISP-DM | Contenido |
|---|---|---|
| `01_comprension_negocio_y_datos` | Comprensión del negocio y de los datos | Objetivos, calidad y estructura de los datos |
| `02_preparacion_datos` | Preparación | Limpieza, cruce con categorías, dataset a nivel video |
| `03_analisis_exploratorio` | Comprensión de los datos | Categorías, engagement, efecto de la fecha de publicación |
| `04_clustering` | Modelado | Segmentación de videos |
| `05_modelos_predictivos` | Modelado y evaluación | Predicción de vistas y likes, importancia de variables |
| `06_pronostico_tendencias` | Modelado y evaluación | Pronóstico exploratorio del nivel de la lista a 14 días |

## Entregables

- **Notebooks:** los seis de la tabla anterior, en `notebooks/`, ya ejecutados.
- **Presentación:** [reports/presentacion.pptx](reports/presentacion.pptx), 10 slides con metodología, respuestas, modelos y recomendaciones.

## Estructura

```
├── data/
│   ├── raw/          # datos originales de Kaggle
│   └── processed/    # datasets limpios generados por los notebooks
├── notebooks/        # análisis paso a paso
├── src/              # funciones compartidas de carga y limpieza
├── reports/          # figuras y presentación
└── docs/             # enunciado de la prueba
```

## Datos

Fuente: [Trending YouTube Video Statistics](https://www.kaggle.com/datasets/datasnaek/youtube-new) en Kaggle.

El CSV no se incluye en el repositorio por su tamaño. Para reproducir el análisis, descarga `USvideos.csv` de Kaggle y ponlo en `data/raw/`. El archivo `US_category_id.json` ya está incluido.

## Cómo ejecutar

```bash
pip install -r requirements.txt
```

```bash
jupyter lab
```

Los notebooks se ejecutan en orden numérico.
