#!/usr/bin/env python3
"""
Auditoría de Sesgo - Taller de 30 minutos
=========================================

Audita un modelo ya entrenado usando únicamente sus predicciones
(NO se entrena nada) y decide si supera la regla de los cuatro quintos.

Uso:
    python scripts/calculate_audit.py
    python scripts/calculate_audit.py --data otra_ruta.csv --threshold 0.8

Código de salida:
    0 -> el modelo pasa la regla de los 4/5
    1 -> violación detectada (el CI marca el check en rojo)

TU TRABAJO: implementar los dos TODO marcados más abajo
(statistical_parity_difference y equal_opportunity_difference).
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix

# --------------------------------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------------------------------
DEFAULT_DATA = Path(__file__).resolve().parent.parent / "data" / "model_predictions.csv"

MAJORITY_GROUP = 0  # valor de `protected_group` para el grupo mayoritario
MINORITY_GROUP = 1  # valor de `protected_group` para el grupo minoritario
DI_THRESHOLD = 0.80  # regla de los cuatro quintos (80%)
GAP_WARNING = 0.10  # |SPD| o |EOD| mayores a esto se marcan como brecha relevante

REQUIRED_COLUMNS = {"id", "true_label", "predicted_label", "protected_group"}


# --------------------------------------------------------------------------
# PASO 1: CARGA DE DATOS
# --------------------------------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    """Carga el CSV de predicciones y valida que tenga las columnas esperadas."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en el CSV: {sorted(missing)}")
    return df


# --------------------------------------------------------------------------
# PASO 2: MÉTRICAS POR GRUPO
# --------------------------------------------------------------------------
def selection_rate(df: pd.DataFrame, group: int) -> float:
    """Tasa de aceptación de un grupo: P(Y_hat = 1 | grupo)."""
    group_df = df[df["protected_group"] == group]
    if group_df.empty:
        raise ValueError(f"No hay registros para el grupo {group}")
    return float(group_df["predicted_label"].mean())


def group_confusion(df: pd.DataFrame, group: int) -> dict:
    """Matriz de confusión de un grupo, más TPR (recall) y FPR."""
    group_df = df[df["protected_group"] == group]
    tn, fp, fn, tp = confusion_matrix(
        group_df["true_label"],
        group_df["predicted_label"],
        labels=[0, 1],  # fuerza matriz 2x2 aunque falte una clase
    ).ravel()
    tn, fp, fn, tp = int(tn), int(fp), int(fn), int(tp)

    tpr = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
    fpr = fp / (fp + tn) if (fp + tn) > 0 else float("nan")
    return {"TN": tn, "FP": fp, "FN": fn, "TP": tp, "TPR": tpr, "FPR": fpr}


# --------------------------------------------------------------------------
# PASO 3: MÉTRICAS DE EQUIDAD
# --------------------------------------------------------------------------
def disparate_impact_ratio(rate_minority: float, rate_majority: float) -> float:
    """
    DI = P(Y_hat=1 | Grupo Minoritario) / P(Y_hat=1 | Grupo Mayoritario)

        DI = 1.0  -> paridad perfecta
        DI < 0.8  -> posible discriminación (regla de los 4/5)
    """
    if rate_majority == 0:
        raise ZeroDivisionError(
            "La tasa del grupo mayoritario es 0; el DI no está definido."
        )
    return rate_minority / rate_majority


def statistical_parity_difference(rate_minority: float, rate_majority: float) -> float:
    """
    Statistical Parity Difference.

        SPD = P(Y_hat=1 | minoritario) - P(Y_hat=1 | mayoritario)

    Valor ideal: 0. Un valor negativo indica que el grupo minoritario
    es aceptado con menor frecuencia.
    """
    return rate_minority - rate_majority


def equal_opportunity_difference(tpr_minority: float, tpr_majority: float) -> float:
    """
    Equal Opportunity Difference.

        EOD = TPR_min - TPR_maj

    Valor ideal: 0. Compara solo a las personas realmente calificadas
    (true_label = 1) de cada grupo.
    """
    return tpr_minority - tpr_majority


# --------------------------------------------------------------------------
# PASO 4: VALIDACIÓN Y ALERTA
# --------------------------------------------------------------------------
def check_four_fifths_rule(di: float, threshold: float = DI_THRESHOLD) -> bool:
    """Imprime el veredicto en consola. Devuelve True si el modelo pasa."""
    print("\n" + "=" * 60)
    if di < threshold:
        print("🚨 ALERTA: VIOLACIÓN DE LA REGLA DE LOS CUATRO QUINTOS 🚨")
        print(f"   DI = {di:.3f}  <  umbral = {threshold:.2f}")
        print("   El modelo presenta IMPACTO DISPAR contra el grupo minoritario.")
        print("   Acción: devolver a desarrollo para mitigación de sesgos.")
        print("=" * 60)
        return False

    print("✅ APROBADO: el modelo cumple la regla de los cuatro quintos.")
    print(f"   DI = {di:.3f}  >=  umbral = {threshold:.2f}")
    print("=" * 60)
    return True


# --------------------------------------------------------------------------
# UTILIDAD CI: resumen en la pestaña "Summary" de GitHub Actions
# --------------------------------------------------------------------------
def _fmt(value, spec: str) -> str:
    """Formatea un número, o devuelve 'pendiente' si el TODO no está resuelto."""
    return "pendiente" if value is None else format(value, spec)


def write_github_summary(results: dict, passed: bool) -> None:
    """Si corre dentro de GitHub Actions, añade una tabla Markdown al resumen del job."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    verdict = "✅ Aprobado" if passed else "❌ Violación de la regla 4/5"
    lines = [
        "## Auditoría de equidad",
        f"**Veredicto:** {verdict}",
        "",
        "| Métrica | Valor |",
        "| :--- | ---: |",
        f"| Accuracy global | {results['accuracy']:.1%} |",
        f"| Tasa de aceptación (mayoritario) | {results['rate_maj']:.1%} |",
        f"| Tasa de aceptación (minoritario) | {results['rate_min']:.1%} |",
        f"| Disparate Impact (DI) | {results['di']:.3f} |",
        f"| Statistical Parity Difference | {_fmt(results['spd'], '+.3f')} |",
        f"| Equal Opportunity Difference | {_fmt(results['eod'], '+.3f')} |",
        "",
    ]
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))


# --------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# --------------------------------------------------------------------------
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Auditoría de sesgo (regla 4/5).")
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
        help="CSV con id, true_label, predicted_label, protected_group",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DI_THRESHOLD,
        help="Umbral mínimo de DI (por defecto 0.80)",
    )
    args = parser.parse_args(argv)

    df = load_data(args.data)
    print(f"Archivo auditado: {args.data}")
    print(f"Registros cargados: {len(df)}")

    # --- Rendimiento global ---
    accuracy = accuracy_score(df["true_label"], df["predicted_label"])
    print(f"\nAccuracy global: {accuracy:.1%}")

    # --- Tasas de aceptación por grupo ---
    rate_maj = selection_rate(df, MAJORITY_GROUP)
    rate_min = selection_rate(df, MINORITY_GROUP)
    print(f"Tasa de aceptación - Grupo mayoritario ({MAJORITY_GROUP}): {rate_maj:.1%}")
    print(f"Tasa de aceptación - Grupo minoritario ({MINORITY_GROUP}): {rate_min:.1%}")

    # --- Matrices de confusión por grupo ---
    conf = {}
    for label, group in [
        ("Mayoritario", MAJORITY_GROUP),
        ("Minoritario", MINORITY_GROUP),
    ]:
        m = group_confusion(df, group)
        conf[group] = m
        print(f"\nMatriz de confusión - Grupo {label} ({group}):")
        print(f"   TN={m['TN']}  FP={m['FP']}  FN={m['FN']}  TP={m['TP']}")
        print(f"   TPR (Recall) = {m['TPR']:.1%}   FPR = {m['FPR']:.1%}")

    # --- Métricas de equidad ---
    di = disparate_impact_ratio(rate_min, rate_maj)

    try:
        spd = statistical_parity_difference(rate_min, rate_maj)
    except NotImplementedError:
        spd = None
    try:
        eod = equal_opportunity_difference(
            conf[MINORITY_GROUP]["TPR"], conf[MAJORITY_GROUP]["TPR"]
        )
    except NotImplementedError:
        eod = None

    print("\n--- Métricas de equidad ---")
    print(f"Disparate Impact Ratio (DI):          {di:.3f}")
    print(
        f"Statistical Parity Difference (SPD):  "
        f"{'PENDIENTE (TODO 2)' if spd is None else f'{spd:+.3f}'}"
    )
    print(
        f"Equal Opportunity Difference (EOD):   "
        f"{'PENDIENTE (TODO 1)' if eod is None else f'{eod:+.3f}'}"
    )

    if (spd is not None and abs(spd) > GAP_WARNING) or (
        eod is not None and abs(eod) > GAP_WARNING
    ):
        print(
            f"(!) Brecha mayor a {GAP_WARNING:.2f} en SPD y/o EOD: revisar. "
            "Estas dos métricas son informativas; la compuerta usa solo el DI."
        )

    # --- Veredicto (determina el código de salida) ---
    passed = check_four_fifths_rule(di, args.threshold)

    write_github_summary(
        {
            "accuracy": accuracy,
            "rate_maj": rate_maj,
            "rate_min": rate_min,
            "di": di,
            "spd": spd,
            "eod": eod,
        },
        passed,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
