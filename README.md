# Taller: Auditoría de Sesgo y Documentación de Modelos de IA

[![Fairness Audit CI](https://github.com/ldlavado/Taller-Ethical-IA/actions/workflows/fairness-audit.yml/badge.svg)](https://github.com/ldlavado/Taller-Ethical-IA/actions/workflows/fairness-audit.yml)

Taller práctico de 30 minutos. **No se entrena ningún modelo**: se audita uno ya
existente a partir de sus predicciones, se integra la auditoría en CI y se
documentan los resultados en una Model Card.

## 🎯 Objetivo

Al finalizar el taller serás capaz de:

1. Calcular métricas de equidad (**Disparate Impact**, **Statistical Parity Difference**,
   **Equal Opportunity Difference**) a partir de un CSV de predicciones.
2. Aplicar la **regla de los cuatro quintos** (DI ≥ 0.80) como criterio de aprobación.
3. Usar la auditoría como **quality gate en CI/CD** con GitHub Actions.
4. Documentar los hallazgos en una **Model Card**.

## 📁 Estructura

```
├── .github/workflows/fairness-audit.yml   # CI (no modificar)
├── data/model_predictions.csv             # Dataset a auditar
├── scripts/calculate_audit.py             # Script con 2 TODO por implementar
├── tests/                                 # Tests del script + datasets de referencia
├── MODEL_CARD_TEMPLATE.md                 # Plantilla de la Model Card
└── docs/img/                              # Aquí van tus capturas
```

## 🚀 Cómo empezar

Cada estudiante trabaja en **su propio repositorio público**, porque el CI de GitHub Actions
se ejecuta ahí. Clonar el repositorio del taller no basta: tu `git push` debe ir a tu repo, no al del docente.

### 1. Crea tu repositorio vacío en GitHub

1. Entra a <https://github.com/new>.
2. Nómbralo, por ejemplo, `bias-audit-workshop`.
3. Selecciona visibilidad **Public**.
4. **No marques** "Add a README", ".gitignore" ni "license". El repo debe quedar vacío.
5. Pulsa **Create repository**.

### 2. Clona el taller y apunta al repo que creaste

```bash
git clone https://github.com/<USUARIO_DOCENTE>/<REPO_DEL_TALLER>.git bias-audit-workshop
cd bias-audit-workshop

git remote set-url origin https://github.com/<TU_USUARIO>/<TU_REPO>.git
git branch -M main
git push -u origin main
```

Verifica que apuntas a tu repo y no al del docente:

```bash
git remote -v      # debe mostrar TU usuario, no el del docente
```

### 3. Comprueba que el CI está activo

1. Abre la pestaña **Actions** de tu repositorio.
2. Debe aparecer un run de **Fairness Audit CI** disparado por tu primer push.
3. Si ves un botón verde _"I understand my workflows, go ahead and enable them"_, púlsalo y relanza con **Run workflow**.

> Este primer run es **esperado**: `unit-tests` ✅ (con 2 tests _skipped_) y
> `fairness-gate` ❌. El modelo es sesgado a propósito; no es un error tuyo.

### 4. Actualiza el badge

Reemplaza `<USUARIO>/<REPO>` en la primera línea de este README por los tuyos.

### 5. Instala las dependencias (Python 3.9+)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

## ▶️ Ejecución

```bash
python scripts/calculate_audit.py                    # audita data/model_predictions.csv
python scripts/calculate_audit.py --data <otro.csv>  # audita otro archivo
pytest -v                                            # tests del script
echo $?                                              # 0 = aprueba, 1 = viola la regla 4/5
```

---

## 📝 Pasos del taller

### Paso 1. Ejecuta el script tal como está

Corre el script sin modificar nada. Las métricas SPD y EOD deben aparecer como `PENDIENTE`.

**Evidencia 1: salida en consola (TODOs pendientes):**

```
Archivo auditado: data/model_predictions.csv
Registros cargados: 24

Accuracy global: 62.5%
Tasa de aceptación - Grupo mayoritario (0): 75.0%
Tasa de aceptación - Grupo minoritario (1): 25.0%

Matriz de confusión - Grupo Mayoritario (0):
   TN=2  FP=3  FN=1  TP=6
   TPR (Recall) = 85.7%   FPR = 60.0%

Matriz de confusión - Grupo Minoritario (1):
   TN=4  FP=0  FN=5  TP=3
   TPR (Recall) = 37.5%   FPR = 0.0%

--- Métricas de equidad ---
Disparate Impact Ratio (DI):          0.333
Statistical Parity Difference (SPD):  PENDIENTE (TODO 2)
Equal Opportunity Difference (EOD):   PENDIENTE (TODO 1)

============================================================
🚨 ALERTA: VIOLACIÓN DE LA REGLA DE LOS CUATRO QUINTOS 🚨
   DI = 0.333  <  umbral = 0.80
   El modelo presenta IMPACTO DISPAR contra el grupo minoritario.
   Acción: devolver a desarrollo para mitigación de sesgos.
============================================================
```

### Paso 2. Implementa los TODO

En `scripts/calculate_audit.py` implementa:

- **TODO 1**: `equal_opportunity_difference` (TPR_min − TPR_maj)
- **TODO 2**: `statistical_parity_difference` (rate_min − rate_maj)

Verifica con `pytest -v`: los tests de SPD y EOD deben pasar de _skipped_ a _passed_.

**Evidencia 2: salida de `pytest -v` con TODOs implementados:**

```
============================= test session starts ==============================
platform linux -- Python 3.x
collected 6 items

tests/test_audit.py ......                                               [100%]

============================== 6 passed in X.XXs ===============================
```

**Evidencia 3: salida en consola sobre el dataset sesgado (TODOs implementados):**

```
Archivo auditado: data/model_predictions.csv
Registros cargados: 24

Accuracy global: 62.5%
Tasa de aceptación - Grupo mayoritario (0): 75.0%
Tasa de aceptación - Grupo minoritario (1): 25.0%

Matriz de confusión - Grupo Mayoritario (0):
   TN=2  FP=3  FN=1  TP=6
   TPR (Recall) = 85.7%   FPR = 60.0%

Matriz de confusión - Grupo Minoritario (1):
   TN=4  FP=0  FN=5  TP=3
   TPR (Recall) = 37.5%   FPR = 0.0%

--- Métricas de equidad ---
Disparate Impact Ratio (DI):          0.333
Statistical Parity Difference (SPD):  -0.500
Equal Opportunity Difference (EOD):   -0.482
(!) Brecha mayor a 0.10 en SPD y/o EOD: revisar. Estas dos métricas son informativas; la compuerta usa solo el DI.

============================================================
🚨 ALERTA: VIOLACIÓN DE LA REGLA DE LOS CUATRO QUINTOS 🚨
   DI = 0.333  <  umbral = 0.80
   El modelo presenta IMPACTO DISPAR contra el grupo minoritario.
   Acción: devolver a desarrollo para mitigación de sesgos.
============================================================
```

### Paso 3. Primer push: la compuerta debe fallar

```bash
git add . && git commit -m "Implementa SPD y EOD" && git push
```

Ve a la pestaña **Actions** de tu repositorio.

> **¿Por qué hay un check en rojo?** El script no está roto. Detecta que el _modelo_
> es sesgado y devuelve `exit 1`. Eso es exactamente lo que debe hacer un quality gate.

| #   | Captura                   | Guárdala como                    | Qué debe verse                        |
| --- | ------------------------- | -------------------------------- | ------------------------------------- |
| 1   | Resumen del workflow      | `docs/img/ci-1-gate-rojo.png`    | `unit-tests` ✅ y `fairness-gate` ❌  |
| 2   | Log del job fallido       | `docs/img/ci-2-log-alerta.png`   | Mensaje de violación y el valor de DI |
| 3   | Pestaña _Summary_ del run | `docs/img/ci-3-summary-rojo.png` | Tabla con DI, SPD y EOD               |

![CI en rojo](docs/img/ci-1-gate-rojo.png)
![Log de alerta](docs/img/ci-2-log-alerta.png)
![Summary en rojo](docs/img/ci-3-summary-rojo.png)

### Paso 4. Mitigación simulada

Simula que el equipo de desarrollo corrigió el modelo (por ejemplo, ajustando el umbral de decisión del grupo minoritario):

```bash
cp tests/fixtures/fair_predictions.csv data/model_predictions.csv
```

**Evidencia 4: salida en consola tras la mitigación:**

```
Archivo auditado: data/model_predictions.csv
Registros cargados: 24

Accuracy global: 75.0%
Tasa de aceptación - Grupo mayoritario (0): 75.0%
Tasa de aceptación - Grupo minoritario (1): 66.7%

Matriz de confusión - Grupo Mayoritario (0):
   TN=2  FP=3  FN=1  TP=6
   TPR (Recall) = 85.7%   FPR = 60.0%

Matriz de confusión - Grupo Minoritario (1):
   TN=3  FP=1  FN=1  TP=7
   TPR (Recall) = 87.5%   FPR = 25.0%

--- Métricas de equidad ---
Disparate Impact Ratio (DI):          0.889
Statistical Parity Difference (SPD):  -0.083
Equal Opportunity Difference (EOD):   +0.018

============================================================
✅ APROBADO: el modelo cumple la regla de los cuatro quintos.
   DI = 0.889  >=  umbral = 0.80
============================================================
```

### Paso 5. Segundo push: la compuerta debe pasar

```bash
git add . && git commit -m "Aplica mitigación simulada" && git push
```

| #   | Captura                   | Guárdala como                     | Qué debe verse      |
| --- | ------------------------- | --------------------------------- | ------------------- |
| 4   | Resumen del workflow      | `docs/img/ci-4-gate-verde.png`    | Ambos jobs ✅       |
| 5   | Pestaña _Summary_ del run | `docs/img/ci-5-summary-verde.png` | Tabla con DI ≥ 0.80 |

![CI en verde](docs/img/ci-4-gate-verde.png)
![Summary en verde](docs/img/ci-5-summary-verde.png)

---

## 🧠 Reflexión

### A. Resultados

Completa con los valores de tu ejecución.

| Métrica                     | Dataset sesgado | Tras mitigación |
| --------------------------- | --------------- | --------------- |
| Accuracy global             | 62.5%           | 75.0%           |
| Tasa de aceptación, grupo 0 | 75.0%           | 75.0%           |
| Tasa de aceptación, grupo 1 | 25.0%           | 66.7%           |
| TPR, grupo 0                | 85.7%           | 85.7%           |
| TPR, grupo 1                | 37.5%           | 87.5%           |
| FPR, grupo 0                | 60.0%           | 60.0%           |
| FPR, grupo 1                | 0.0%            | 25.0%           |
| **Disparate Impact (DI)**   | 0.333           | 0.889           |
| **SPD**                     | -0.500          | -0.083          |
| **EOD**                     | -0.482          | +0.018          |
| ¿Pasa la regla 4/5?         | ☐ Sí ☒ No       | ☒ Sí ☐ No       |

Muestra el cálculo manual de las tres métricas del dataset sesgado:

```
DI  = 0.25 / 0.75 = 0.333
SPD = 0.25 − 0.75 = -0.500
EOD = 0.375 − 0.857 = -0.482
```

### B. Preguntas

**1. ¿La EOD coincide con la conclusión del DI? ¿Miden lo mismo? Justifica.**

> Sí coinciden en la conclusión (hay disparidad), pero no miden exactamente lo mismo. DI y SPD miran la tasa de aceptación global (P(Y_hat=1|grupo)), mientras que EOD mira solo el recall entre las personas realmente calificadas (true_label=1). Ambas señalan inequidad, pero EOD es más específica sobre oportunidad para los merecedores.

**2. Calcula qué proporción de cada grupo está realmente calificada (`true_label = 1`). ¿La brecha de aceptación se explica por mérito?**

> Grupo 0: 7/12 ≈ 58.3% calificados. Grupo 1: 8/12 ≈ 66.7% calificados. El grupo minoritario tiene incluso más proporción de calificados, por lo que la brecha de aceptación (75% vs 25%) **no** se explica por mérito; es sesgo del modelo.

**3. ¿Cuántas personas calificadas del grupo 1 fueron rechazadas (FN)? ¿Qué implica en un caso real?**

> 5 personas calificadas del grupo minoritario fueron rechazadas (FN). En un caso real (crédito, empleo, acceso) esto significa negar oportunidades a personas merecedoras únicamente por pertenecer al grupo protegido, con posible impacto discriminatorio.

**4. Compara el FPR de ambos grupos. ¿Qué dice sobre los estándares que aplica el modelo a cada uno?**

> FPR grupo 0 = 60%, FPR grupo 1 = 0%. El modelo es mucho más permisivo con el grupo mayoritario (acepta muchos no calificados) y extremadamente estricto con el minoritario (casi no acepta a nadie no calificado, pero tampoco a los calificados). Aplica estándares desiguales.

**5. El accuracy global puede verse aceptable aunque el modelo sea inequitativo. ¿Por qué ocurre?**

> Porque el accuracy es un promedio global que puede enmascarar disparidades. Un modelo que acierta mucho en el grupo mayoritario y falla en el minoritario puede tener accuracy "aceptable" si el mayoritario es grande, mientras discrimina sistemáticamente.

**6. El dataset tiene solo 12 registros por grupo. ¿Qué limitaciones tiene esta auditoría?**

> El tamaño es demasiado pequeño para conclusiones robustas. No hay intervalos de confianza, el resultado es muy sensible a pocos cambios, y no permite análisis interseccional ni validación estadística. Sirve solo como ejemplo didáctico.

**7. Propón dos mitigaciones técnicas reales (no la simulada) y un riesgo de cada una.**

> 1) Re-ponderación o oversampling del grupo minoritario durante el entrenamiento. Riesgo: puede reducir el accuracy global o introducir ruido.  
> 2) Ajuste de umbral de decisión por grupo (threshold tuning post-hoc). Riesgo: puede ser percibido como trato preferencial explícito y complicar la explicabilidad o el cumplimiento regulatorio.

### C. Conclusión: auditoría vs. Model Card

Compara los valores que escribiste en tu `MODEL_CARD.md` antes de ejecutar el script
(tus hipótesis) con los obtenidos en la auditoría.

| Métrica                     | Hipótesis (antes) | Obtenido (auditoría) | ¿Coincide? |
| --------------------------- | ----------------- | -------------------- | ---------- |
| Accuracy global             | ~70-80%           | 62.5%                | No         |
| Tasa de aprobación, grupo 0 | ~60%              | 75%                  | Parcial    |
| Tasa de aprobación, grupo 1 | ~50%              | 25%                  | No         |
| Disparate Impact            | ~0.70             | 0.333                | No         |

**Conclusión (máx. 5 líneas):** Llenar una Model Card con estimaciones o intuición es insuficiente y puede ser engañoso. Solo la auditoría cuantitativa con los datos reales revela la magnitud del sesgo (DI=0.333). El modelo original **no es apto para despliegue**: viola la regla de los cuatro quintos de forma severa y debe ser mitigado antes de cualquier uso productivo.

---

## 📋 Model Card

1. Copia la plantilla: `cp MODEL_CARD_TEMPLATE.md MODEL_CARD.md`
2. Complétala con los resultados **reales** de tu auditoría sobre el dataset sesgado.
3. Verifica que la "Conclusión de la Auditoría" sea coherente con DI, SPD y EOD.

## ✅ Checklist de entrega

- [x] TODO 1 y TODO 2 implementados; `pytest -v` sin _skipped_ ni fallos
- [x] Evidencias 1 a 4 (salidas de consola) pegadas arriba
- [ ] 5 capturas de CI en `docs/img/` (3 en rojo, 2 en verde) y visibles en este README
- [x] Sección Reflexión completa (A, B y C)
- [x] `MODEL_CARD.md` completada
- [ ] Repositorio compartido con el docente

## 🧮 Rúbrica sugerida

| Criterio                                               | Puntos |
| ------------------------------------------------------ | ------ |
| Implementación correcta de SPD y EOD (tests en verde)  | 25     |
| Evidencias de CI (rojo y verde, con capturas legibles) | 25     |
| Reflexión: interpretación correcta de las métricas     | 25     |
| Model Card completa y coherente con la auditoría       | 25     |
