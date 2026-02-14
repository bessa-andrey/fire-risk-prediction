# statistical_analysis.py
"""
Statistical Analysis for Module A Model Comparison

Implements three statistical methods described in the methodology:
1. Bootstrap Confidence Intervals (1000 resamples) for all metrics
2. McNemar's Test for pairwise model comparison
3. Wilcoxon Signed-Rank Test for cross-validation fold comparison

Input: Trained models (.pkl) + features dataset
Output:
  - bootstrap_ci.json (confidence intervals for each model)
  - mcnemar_results.json (pairwise p-values)
  - wilcoxon_results.json (cross-validation comparison)
  - statistical_summary.json (combined report)
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, roc_auc_score, precision_score, recall_score,
    f1_score, precision_recall_curve, auc
)
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuration
INPUT_FILE = Path('data/processed/training/module_a_balanced.csv')
MODEL_DIR = Path('data/models/module_a')
OUTPUT_DIR = MODEL_DIR / 'statistical_analysis'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = [
    'brightness', 'confidence', 'frp', 'hotspot_count',
    'persistence_score', 'temperature', 'dewpoint',
    'wind_speed', 'precipitation', 'rh', 'drying_index'
]
TARGET_COL = 'is_reliable'

# Models to analyze
MODEL_NAMES = [
    'dummy', 'logistic', 'svm', 'tree', 'randomforest',
    'lightgbm', 'xgboost', 'lightgbm_optuna', 'xgboost_optuna'
]


def load_data():
    """Load and prepare dataset"""
    print("[INFO] Loading dataset...")
    df = pd.read_csv(INPUT_FILE)
    df = df.dropna(subset=[TARGET_COL])

    available_features = [col for col in FEATURE_COLS if col in df.columns]
    X = df[available_features].fillna(df[available_features].mean())
    y = df[TARGET_COL].values

    print(f"[OK] Loaded {len(X)} samples, {len(available_features)} features")
    return X, y


def load_models():
    """Load all trained models"""
    models = {}
    for name in MODEL_NAMES:
        model_path = MODEL_DIR / f'module_a_{name}.pkl'
        if model_path.exists():
            with open(model_path, 'rb') as f:
                models[name] = pickle.load(f)
            print(f"[OK] Loaded model: {name}")
        else:
            print(f"[WARNING] Model not found: {name}")
    return models


def bootstrap_confidence_intervals(models, X, y, n_bootstrap=1000, alpha=0.05):
    """
    Compute bootstrap confidence intervals for all metrics.

    Method: Non-parametric bootstrap with stratified resampling.
    For each bootstrap iteration:
      1. Resample test set with replacement (maintaining class ratio)
      2. Compute metrics on resampled data
      3. After all iterations, compute percentile-based CI

    Args:
        models: dict of trained models
        X: feature matrix
        y: labels
        n_bootstrap: number of bootstrap resamples (default 1000)
        alpha: significance level (default 0.05 for 95% CI)

    Returns:
        dict with CI for each model and metric
    """
    print(f"\n{'='*60}")
    print(f"BOOTSTRAP CONFIDENCE INTERVALS ({n_bootstrap} resamples)")
    print(f"{'='*60}")

    # Same train-test split as training
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}
    metrics_list = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'pr_auc']

    for model_name, model in models.items():
        print(f"\n[INFO] Bootstrapping {model_name}...")

        # Get predictions on full test set
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

        # Store bootstrap samples for each metric
        bootstrap_metrics = {m: [] for m in metrics_list}

        np.random.seed(42)
        for i in range(n_bootstrap):
            # Stratified bootstrap: resample indices with replacement
            indices = np.arange(len(y_test))
            boot_indices = np.random.choice(indices, size=len(indices), replace=True)

            y_boot = y_test[boot_indices]
            y_pred_boot = y_pred[boot_indices]
            y_proba_boot = y_pred_proba[boot_indices]

            # Skip if only one class in bootstrap sample
            if len(np.unique(y_boot)) < 2:
                continue

            bootstrap_metrics['accuracy'].append(accuracy_score(y_boot, y_pred_boot))
            bootstrap_metrics['precision'].append(precision_score(y_boot, y_pred_boot, zero_division=0))
            bootstrap_metrics['recall'].append(recall_score(y_boot, y_pred_boot, zero_division=0))
            bootstrap_metrics['f1'].append(f1_score(y_boot, y_pred_boot, zero_division=0))

            try:
                bootstrap_metrics['roc_auc'].append(roc_auc_score(y_boot, y_proba_boot))
            except ValueError:
                pass

            try:
                prec_curve, rec_curve, _ = precision_recall_curve(y_boot, y_proba_boot)
                bootstrap_metrics['pr_auc'].append(auc(rec_curve, prec_curve))
            except Exception:
                pass

        # Compute confidence intervals
        model_ci = {}
        for metric in metrics_list:
            values = np.array(bootstrap_metrics[metric])
            if len(values) == 0:
                continue

            lower = np.percentile(values, (alpha / 2) * 100)
            upper = np.percentile(values, (1 - alpha / 2) * 100)
            mean = np.mean(values)
            std = np.std(values)

            model_ci[metric] = {
                'mean': float(mean),
                'std': float(std),
                'ci_lower': float(lower),
                'ci_upper': float(upper),
                'ci_level': float(1 - alpha),
            }

            print(f"  {metric}: {mean:.4f} [{lower:.4f}, {upper:.4f}]")

        results[model_name] = model_ci

    return results


def mcnemar_test(models, X, y):
    """
    McNemar's test for pairwise comparison of classifiers.

    Tests whether two models make the same type of errors.
    Uses the contingency table of correct/incorrect predictions.

    Null hypothesis: Both models have the same error rate.
    If p < 0.05, the models are significantly different.

    The test statistic is:
        chi2 = (|b - c| - 1)^2 / (b + c)
    where b = cases model1 correct & model2 wrong,
          c = cases model1 wrong & model2 correct.

    Args:
        models: dict of trained models
        X: feature matrix
        y: labels

    Returns:
        dict with pairwise test results
    """
    print(f"\n{'='*60}")
    print("McNEMAR'S TEST - PAIRWISE MODEL COMPARISON")
    print(f"{'='*60}")

    # Same split as training
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Get predictions for each model
    predictions = {}
    for name, model in models.items():
        predictions[name] = model.predict(X_test_scaled)

    # Pairwise McNemar tests
    model_names = list(models.keys())
    results = {}

    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            name_i = model_names[i]
            name_j = model_names[j]

            pred_i = predictions[name_i]
            pred_j = predictions[name_j]

            # Contingency table
            # correct_i & correct_j (a), correct_i & wrong_j (b),
            # wrong_i & correct_j (c), wrong_i & wrong_j (d)
            correct_i = (pred_i == y_test)
            correct_j = (pred_j == y_test)

            b = np.sum(correct_i & ~correct_j)  # i correct, j wrong
            c = np.sum(~correct_i & correct_j)  # i wrong, j correct

            # McNemar statistic with continuity correction
            if (b + c) == 0:
                chi2 = 0.0
                p_value = 1.0
            else:
                chi2 = ((abs(b - c) - 1) ** 2) / (b + c)
                p_value = float(1 - stats.chi2.cdf(chi2, df=1))

            pair_key = f"{name_i}_vs_{name_j}"
            results[pair_key] = {
                'model_1': name_i,
                'model_2': name_j,
                'b_count': int(b),
                'c_count': int(c),
                'chi2_statistic': float(chi2),
                'p_value': p_value,
                'significant': p_value < 0.05,
            }

            sig = "*" if p_value < 0.05 else ""
            print(f"  {name_i} vs {name_j}: chi2={chi2:.3f}, p={p_value:.4f} {sig}")

    return results


def wilcoxon_crossval(models, X, y, n_folds=5):
    """
    Wilcoxon signed-rank test using cross-validation fold scores.

    Compares pairs of models across K-fold CV performance.
    Non-parametric alternative to paired t-test - appropriate when
    we cannot assume normal distribution of differences.

    Null hypothesis: median difference between paired observations is zero.

    Args:
        models: dict of trained models (will be retrained per fold)
        X: feature matrix
        y: labels
        n_folds: number of CV folds

    Returns:
        dict with pairwise test results and fold scores
    """
    print(f"\n{'='*60}")
    print(f"WILCOXON SIGNED-RANK TEST ({n_folds}-FOLD CV)")
    print(f"{'='*60}")

    # We need to import the model creation classes to retrain per fold
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.dummy import DummyClassifier
    from sklearn.svm import SVC
    import lightgbm as lgb
    import xgboost as xgb

    # Model factories - recreate models for each fold
    model_factories = {
        'dummy': lambda: DummyClassifier(strategy='most_frequent', random_state=42),
        'logistic': lambda: LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs', class_weight='balanced'),
        'svm': lambda: SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42, class_weight='balanced'),
        'tree': lambda: DecisionTreeClassifier(max_depth=10, min_samples_split=5, min_samples_leaf=2, random_state=42, class_weight='balanced'),
        'randomforest': lambda: RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced', n_jobs=-1),
        'lightgbm': lambda: lgb.LGBMClassifier(num_leaves=31, learning_rate=0.05, max_depth=10, num_iterations=100, random_state=42, verbose=-1),
        'xgboost': lambda: xgb.XGBClassifier(max_depth=6, learning_rate=0.1, n_estimators=100, random_state=42, verbosity=0),
    }

    # Load Optuna best params if available
    for opt_model in ['lightgbm', 'xgboost']:
        optuna_path = MODEL_DIR / f'optuna_{opt_model}.json'
        if optuna_path.exists():
            with open(optuna_path, 'r') as f:
                optuna_results = json.load(f)
            best_params = optuna_results['best_params']

            if opt_model == 'lightgbm':
                params = {**best_params, 'random_state': 42, 'verbose': -1}
                model_factories['lightgbm_optuna'] = lambda p=params: lgb.LGBMClassifier(**p)
            elif opt_model == 'xgboost':
                params = {**best_params, 'random_state': 42, 'verbosity': 0}
                model_factories['xgboost_optuna'] = lambda p=params: xgb.XGBClassifier(**p)

    # Only use models that have factories
    available_models = [name for name in MODEL_NAMES if name in model_factories]
    print(f"[INFO] Models for Wilcoxon test: {available_models}")

    # Collect fold scores for each model
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    fold_scores = {name: [] for name in available_models}

    for fold_idx, (train_idx, test_idx) in enumerate(cv.split(X, y)):
        X_train_fold = X.iloc[train_idx] if hasattr(X, 'iloc') else X[train_idx]
        X_test_fold = X.iloc[test_idx] if hasattr(X, 'iloc') else X[test_idx]
        y_train_fold = y[train_idx]
        y_test_fold = y[test_idx]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_fold)
        X_test_scaled = scaler.transform(X_test_fold)

        for name in available_models:
            model = model_factories[name]()
            model.fit(X_train_scaled, y_train_fold)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

            try:
                prec, rec, _ = precision_recall_curve(y_test_fold, y_pred_proba)
                pr_auc_score = auc(rec, prec)
            except Exception:
                pr_auc_score = 0.0

            fold_scores[name].append(pr_auc_score)

        print(f"  Fold {fold_idx + 1}/{n_folds} complete")

    # Print fold scores
    print(f"\n{'Model':<25} " + " ".join([f"{'Fold '+str(i+1):>8}" for i in range(n_folds)]) + f" {'Mean':>8}")
    print("-" * (25 + 9 * (n_folds + 1)))
    for name in available_models:
        scores = fold_scores[name]
        row = f"{name:<25} " + " ".join([f"{s:>8.4f}" for s in scores]) + f" {np.mean(scores):>8.4f}"
        print(row)

    # Pairwise Wilcoxon tests
    results = {'fold_scores': {name: [float(s) for s in scores] for name, scores in fold_scores.items()}}
    pairwise = {}

    for i in range(len(available_models)):
        for j in range(i + 1, len(available_models)):
            name_i = available_models[i]
            name_j = available_models[j]

            scores_i = np.array(fold_scores[name_i])
            scores_j = np.array(fold_scores[name_j])

            # Wilcoxon signed-rank test
            # Requires at least 6 paired observations for reliability
            # With 5 folds, this is marginal but still informative
            try:
                if np.all(scores_i == scores_j):
                    stat, p_value = 0.0, 1.0
                else:
                    stat, p_value = stats.wilcoxon(scores_i, scores_j, alternative='two-sided')
                    p_value = float(p_value)
            except Exception:
                stat, p_value = np.nan, np.nan

            pair_key = f"{name_i}_vs_{name_j}"
            pairwise[pair_key] = {
                'model_1': name_i,
                'model_2': name_j,
                'mean_1': float(np.mean(scores_i)),
                'mean_2': float(np.mean(scores_j)),
                'diff_mean': float(np.mean(scores_i) - np.mean(scores_j)),
                'statistic': float(stat) if not np.isnan(stat) else None,
                'p_value': p_value if not np.isnan(p_value) else None,
                'significant': bool(p_value < 0.05) if not np.isnan(p_value) else False,
            }

    results['pairwise_tests'] = pairwise

    # Print significant differences
    print(f"\nSignificant pairwise differences (p < 0.05):")
    any_significant = False
    for pair_key, res in pairwise.items():
        if res['significant']:
            print(f"  {res['model_1']} vs {res['model_2']}: p={res['p_value']:.4f}, diff={res['diff_mean']:+.4f}")
            any_significant = True
    if not any_significant:
        print("  None found (note: Wilcoxon with 5 folds has limited power)")

    return results


def generate_summary(bootstrap_results, mcnemar_results, wilcoxon_results):
    """Generate combined statistical summary"""
    summary = {
        'analysis_date': datetime.now().isoformat(),
        'methods': {
            'bootstrap': {
                'description': 'Non-parametric bootstrap confidence intervals',
                'n_resamples': 1000,
                'ci_level': 0.95,
            },
            'mcnemar': {
                'description': "McNemar's test for pairwise classifier comparison",
                'correction': 'continuity correction applied',
                'null_hypothesis': 'Both models have the same error rate',
            },
            'wilcoxon': {
                'description': 'Wilcoxon signed-rank test on CV fold scores',
                'n_folds': 5,
                'metric': 'PR-AUC',
                'null_hypothesis': 'Median difference between paired observations is zero',
            },
        },
        'bootstrap_ci': bootstrap_results,
        'mcnemar_tests': mcnemar_results,
        'wilcoxon_tests': wilcoxon_results,
    }
    return summary


def main():
    """Run complete statistical analysis"""
    print("\n" + "=" * 60)
    print("STATISTICAL ANALYSIS - MODULE A")
    print("=" * 60)

    # Load data and models
    X, y = load_data()
    models = load_models()

    if len(models) < 2:
        print("[ERROR] Need at least 2 trained models for comparison")
        print("[INFO] Run train_module_a.py first")
        return

    # 1. Bootstrap Confidence Intervals
    bootstrap_results = bootstrap_confidence_intervals(models, X, y, n_bootstrap=1000)
    bootstrap_path = OUTPUT_DIR / 'bootstrap_ci.json'
    with open(bootstrap_path, 'w') as f:
        json.dump(bootstrap_results, f, indent=2)
    print(f"\n[OK] Bootstrap CI saved to: {bootstrap_path}")

    # 2. McNemar's Test
    mcnemar_results = mcnemar_test(models, X, y)
    mcnemar_path = OUTPUT_DIR / 'mcnemar_results.json'
    with open(mcnemar_path, 'w') as f:
        json.dump(mcnemar_results, f, indent=2)
    print(f"[OK] McNemar results saved to: {mcnemar_path}")

    # 3. Wilcoxon Signed-Rank Test
    wilcoxon_results = wilcoxon_crossval(models, X, y, n_folds=5)
    wilcoxon_path = OUTPUT_DIR / 'wilcoxon_results.json'
    with open(wilcoxon_path, 'w') as f:
        json.dump(wilcoxon_results, f, indent=2, default=str)
    print(f"[OK] Wilcoxon results saved to: {wilcoxon_path}")

    # 4. Combined Summary
    summary = generate_summary(bootstrap_results, mcnemar_results, wilcoxon_results)
    summary_path = OUTPUT_DIR / 'statistical_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[OK] Combined summary saved to: {summary_path}")

    # Final summary table
    print(f"\n{'='*70}")
    print("STATISTICAL ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"\n{'Model':<25} {'PR-AUC':>10} {'95% CI':>20}")
    print("-" * 55)
    for model_name in models:
        if model_name in bootstrap_results and 'pr_auc' in bootstrap_results[model_name]:
            ci = bootstrap_results[model_name]['pr_auc']
            print(f"{model_name:<25} {ci['mean']:>10.4f} [{ci['ci_lower']:.4f}, {ci['ci_upper']:.4f}]")

    # Count significant McNemar comparisons
    sig_mcnemar = sum(1 for v in mcnemar_results.values() if v.get('significant', False))
    total_mcnemar = len(mcnemar_results)
    print(f"\nMcNemar: {sig_mcnemar}/{total_mcnemar} significant pairwise comparisons")

    # Count significant Wilcoxon comparisons
    if 'pairwise_tests' in wilcoxon_results:
        sig_wilcoxon = sum(1 for v in wilcoxon_results['pairwise_tests'].values() if v.get('significant', False))
        total_wilcoxon = len(wilcoxon_results['pairwise_tests'])
        print(f"Wilcoxon: {sig_wilcoxon}/{total_wilcoxon} significant pairwise comparisons")

    print(f"\n[OK] All outputs saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
