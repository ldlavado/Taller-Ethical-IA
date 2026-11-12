# Model Card: Clasificador Binario de Aprobación (Taller Ethical IA)

> Plantilla basada en _Model Cards for Model Reporting_ (Mitchell et al., 2019).

## Model Details

- **Developed by:** Luis Daniel Lavado Carreño
- **Model Date:** 2026-11-12
- **Model Version:** v1.0.0 (auditoría sobre predicciones preexistentes)
- **Model Type:** Clasificador Binario (auditoría de predicciones; no se entrena modelo)
- **License:** MIT
- **Contact:** https://github.com/ldlavado/Taller-Ethical-IA

## Intended Use

- **Primary Intended Uses:** Automatización inicial de filtrado o aprobación de solicitudes (ej. crédito, acceso, contratación).
- **Primary Intended Users:** Analistas de riesgo o equipos de operaciones que revisan decisiones automáticas.
- **Out-of-Scope Uses:** Decisiones finales sin supervisión humana, diagnósticos médicos, decisiones judiciales o cualquier uso que excluya completamente la revisión humana.

## Training & Evaluation Data

- **Dataset Overview:** Dataset de predicciones sintéticas de 24 registros (12 por grupo protegido) utilizado para la auditoría de equidad. No se entrena modelo; se evalúan predicciones ya generadas.
- **Protected Attributes:** `protected_group` (0 = grupo mayoritario, 1 = grupo minoritario).
- **Group Definition:** Grupo 0 = mayoritario; Grupo 1 = minoritario.

## Quantitative Performance & Fairness Audit

_Resultados obtenidos sobre el dataset sesgado original (`data/model_predictions.csv` antes de la mitigación):_

| Métrica                                    | Valor Obtenido | Umbral Objetivo |
| :----------------------------------------- | :------------- | :-------------- |
| **Accuracy Global**                        | 62.5%          | > 85%           |
| **Tasa de Aprobación (Grupo Mayoritario)** | 75.0%          | -               |
| **Tasa de Aprobación (Grupo Minoritario)** | 25.0%          | -               |
| **TPR / Recall (Grupo Mayoritario)**       | 85.7%          | -               |
| **TPR / Recall (Grupo Minoritario)**       | 37.5%          | -               |
| **Disparate Impact Ratio (DI)**            | 0.333          | **≥ 0.80**     |
| **Statistical Parity Difference (SPD)**    | -0.500         | ~0              |
| **Equal Opportunity Difference (EOD)**     | -0.482         | ~0              |

- **Resultado de la regla de los 4/5:** [x] Violación detectada
- **Conclusión de la Auditoría:** El modelo viola la regla de los cuatro quintos (DI = 0.333 < 0.80). Presenta impacto dispar severo contra el grupo minoritario tanto en tasa de aceptación (SPD = -0.500) como en oportunidad para los realmente calificados (EOD = -0.482). Debe devolverse a desarrollo para mitigación de sesgos antes de cualquier despliegue.

## Ethical Considerations & Limitations

- **Known Biases:** El dataset muestra una fuerte disparidad: el grupo minoritario tiene tasa de aceptación mucho menor y menor recall, incluso cuando la proporción de personas realmente calificadas es similar o mayor.
- **Limitations of this Audit:** Tamaño de muestra muy pequeño (solo 12 registros por grupo), un único atributo protegido, sin análisis interseccional ni validación estadística de intervalos de confianza.
- **Mitigations Applied / Recommended:** Mitigación simulada aplicada en el taller (ajuste de umbral que eleva la tasa del grupo minoritario). Recomendaciones reales: re-ponderación o re-muestreo del dataset, ajuste de umbrales por grupo, regularización de fairness durante entrenamiento, o supervisión humana obligatoria en casos del grupo minoritario.

## Sign-off

- **Auditor:** Luis Daniel Lavado Carreño
- **Audit Date:** 2026-11-12
- **Decision:** [x] Devuelto a desarrollo
