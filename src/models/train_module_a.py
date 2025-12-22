# train_module_a.py
"""
Train Module A: Spurious Hotspot Detection Classifier (with GPU acceleration)

Input: module_a_features.csv (from feature_engineering.py)
Output:
  - classifier_model.pkl (trained model)
  - classification_report.json (metrics)
  - pr_curves.png (visualization)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_curve, auc
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import lightgbm as lgb
import xgboost as xgb
import json
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
INPUT_DIR = Path('data/processed/training')
INPUT_FILE = INPUT_DIR / 'module_a_balanced.csv'
OUTPUT_DIR = Path('data/models/module_a')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Feature columns for training
FEATURE_COLS = [
    'brightness', 'confidence', 'frp', 'hotspot_count',
    'persistence_score', 'temperature', 'dewpoint',
    'wind_speed', 'precipitation', 'rh', 'drying_index'
]
TARGET_COL = 'is_reliable'

# GPU Configuration
USE_GPU = True
DEVICE = 'gpu' if USE_GPU else 'cpu'

def check_gpu_availability():
    """Check if GPU is available"""
    try:
        import lightgbm
        print("[INFO] Checking GPU availability...")

        # Try to get CUDA info
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print("[OK] NVIDIA GPU detected")
                print("[OK] GPU acceleration ENABLED")
                return True
        except Exception:
            pass

        print("[WARNING] GPU not detected, falling back to CPU")
        return False

    except Exception as e:
        print(f"[WARNING] Could not check GPU: {e}")
        return False

class ModuleAClassifier:
    """Train and evaluate Module A classifier"""

    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu and check_gpu_availability()
        self.device = 'gpu' if self.use_gpu else 'cpu'
        self.scaler = StandardScaler()
        self.model = None
        self.metrics = {}

    def load_data(self, filepath: Path) -> tuple:
        """Load and prepare data"""
        print(f"[INFO] Loading features from {filepath}...")

        df = pd.read_csv(filepath)
        print(f"[OK] Loaded {len(df)} samples")

        # Remove rows with missing target
        df = df.dropna(subset=[TARGET_COL])
        print(f"[OK] After removing NaN labels: {len(df)} samples")

        # Separate features and target
        y = df[TARGET_COL].values

        # Select only the feature columns that exist
        available_features = [col for col in FEATURE_COLS if col in df.columns]
        X = df[available_features].copy()

        # Handle missing values in features
        X = X.fillna(X.mean())

        print(f"[OK] Features shape: {X.shape}")
        print(f"[OK] Feature names: {list(X.columns)}")

        return X, y, X.columns.tolist()

    def create_lightgbm_model(self) -> lgb.LGBMClassifier:
        """Create LightGBM model with GPU support"""
        print("[INFO] Creating LightGBM classifier...")

        params = {
            'num_leaves': 31,
            'learning_rate': 0.05,
            'max_depth': 10,
            'num_iterations': 100,
            'random_state': 42,
            'verbose': -1,
            'device_type': self.device,  # GPU or CPU
        }

        model = lgb.LGBMClassifier(**params)
        print(f"[OK] LightGBM configured with device: {self.device.upper()}")

        return model

    def create_xgboost_model(self) -> xgb.XGBClassifier:
        """Create XGBoost model with GPU support"""
        print("[INFO] Creating XGBoost classifier...")

        params = {
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'random_state': 42,
            'verbosity': 0,
        }

        if self.use_gpu:
            params['tree_method'] = 'hist'
            params['device'] = 'cuda'  # New XGBoost 3.x syntax
            print("[OK] XGBoost configured with GPU acceleration (CUDA)")
        else:
            params['tree_method'] = 'hist'
            params['device'] = 'cpu'
            print("[OK] XGBoost configured with CPU")

        model = xgb.XGBClassifier(**params)

        return model

    def create_logistic_model(self) -> LogisticRegression:
        """Create Logistic Regression model (baseline)"""
        print("[INFO] Creating Logistic Regression classifier (baseline)...")

        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs',
            class_weight='balanced'
        )
        print("[OK] Logistic Regression configured")

        return model

    def create_tree_model(self) -> DecisionTreeClassifier:
        """Create Decision Tree model (baseline)"""
        print("[INFO] Creating Decision Tree classifier (baseline)...")

        model = DecisionTreeClassifier(
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        print("[OK] Decision Tree configured")

        return model

    def create_random_forest_model(self) -> RandomForestClassifier:
        """Create Random Forest model (baseline)"""
        print("[INFO] Creating Random Forest classifier (baseline)...")

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced',
            n_jobs=-1  # Use all cores
        )
        print("[OK] Random Forest configured")

        return model

    def train_and_evaluate(self, X: np.ndarray, y: np.ndarray, model_type: str = 'lightgbm'):
        """Train model and evaluate"""
        print(f"\n[INFO] Training {model_type.upper()} classifier...")

        # Train-test split with spatial/temporal consideration
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        print(f"[OK] Train set: {len(X_train)} samples")
        print(f"[OK] Test set: {len(X_test)} samples")

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Create and train model
        model_type_lower = model_type.lower()
        if model_type_lower == 'lightgbm':
            model = self.create_lightgbm_model()
        elif model_type_lower == 'xgboost':
            model = self.create_xgboost_model()
        elif model_type_lower == 'logistic':
            model = self.create_logistic_model()
        elif model_type_lower == 'tree':
            model = self.create_tree_model()
        elif model_type_lower == 'randomforest':
            model = self.create_random_forest_model()
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        model.fit(X_train_scaled, y_train)
        print("[OK] Model training complete")

        # Evaluate
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

        # Calculate metrics
        metrics = {
            'accuracy': float((y_pred == y_test).mean()),
            'roc_auc': float(roc_auc_score(y_test, y_pred_proba)),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        }

        # Precision-Recall curve
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        pr_auc = auc(recall, precision)
        metrics['pr_auc'] = float(pr_auc)

        # Classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        metrics['classification_report'] = report

        self.model = model
        self.metrics = metrics

        print(f"[OK] Accuracy: {metrics['accuracy']:.4f}")
        print(f"[OK] ROC-AUC: {metrics['roc_auc']:.4f}")
        print(f"[OK] PR-AUC: {metrics['pr_auc']:.4f}")

        return model, metrics, (X_test_scaled, y_test, y_pred_proba)

    def save_model(self, model, model_type: str = 'lightgbm'):
        """Save trained model"""
        model_path = OUTPUT_DIR / f'module_a_{model_type}.pkl'

        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        print(f"[OK] Model saved to: {model_path}")

        return model_path

    def save_scaler(self):
        """Save the fitted scaler for inference"""
        scaler_path = OUTPUT_DIR / 'scaler.pkl'

        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

        print(f"[OK] Scaler saved to: {scaler_path}")

        return scaler_path

    def save_metrics(self, metrics: dict, model_type: str = 'lightgbm'):
        """Save metrics as JSON"""
        metrics_path = OUTPUT_DIR / f'module_a_{model_type}_metrics.json'

        # Convert numpy types to native Python types for JSON serialization
        def convert_to_native(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(i) for i in obj]
            return obj

        metrics_clean = convert_to_native(metrics)

        with open(metrics_path, 'w') as f:
            json.dump(metrics_clean, f, indent=2)

        print(f"[OK] Metrics saved to: {metrics_path}")

        return metrics_path

def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("MODULE A TRAINING - CLASSIFIER")
    print("="*60)
    print(f"Device: {('GPU' if USE_GPU else 'CPU')}")

    # Step 1: Load data
    if not INPUT_FILE.exists():
        print(f"[ERROR] Features file not found: {INPUT_FILE}")
        print("[INFO] Run feature_engineering.py first")
        return

    classifier = ModuleAClassifier(use_gpu=USE_GPU)
    X, y, feature_names = classifier.load_data(INPUT_FILE)

    print(f"\n[INFO] Label distribution:")
    unique, counts = np.unique(y, return_counts=True)
    for label_val, count in zip(unique, counts):
        print(f"  Label {label_val}: {count} samples ({count/len(y)*100:.1f}%)")

    # Define all models to train
    MODEL_TYPES = [
        ('logistic', 'Logistic Regression (Baseline)'),
        ('tree', 'Decision Tree (Baseline)'),
        ('randomforest', 'Random Forest (Baseline)'),
        ('lightgbm', 'LightGBM'),
        ('xgboost', 'XGBoost'),
    ]

    all_results = {}

    # Train all models
    for model_type, model_name in MODEL_TYPES:
        print("\n" + "-"*60)
        print(f"Training {model_name}")
        print("-"*60)

        model, metrics, eval_data = classifier.train_and_evaluate(X, y, model_type=model_type)

        classifier.save_model(model, model_type=model_type)
        classifier.save_metrics(metrics, model_type=model_type)

        # Save scaler after first model (same scaler for all)
        if model_type == 'logistic':
            classifier.save_scaler()

        all_results[model_type] = {
            'name': model_name,
            'accuracy': metrics['accuracy'],
            'roc_auc': metrics['roc_auc'],
            'pr_auc': metrics['pr_auc']
        }

    # Generate summary
    summary = {
        'training_date': datetime.now().isoformat(),
        'device': 'GPU' if USE_GPU else 'CPU',
        'samples': len(X),
        'features': len(feature_names),
        'feature_names': feature_names,
        'models': all_results
    }

    summary_path = OUTPUT_DIR / 'training_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print final summary table
    print(f"\n{'='*60}")
    print("TRAINING COMPLETE - MODEL COMPARISON")
    print(f"{'='*60}")
    print(f"\n{'Model':<25} {'Accuracy':>10} {'ROC-AUC':>10} {'PR-AUC':>10}")
    print("-"*55)

    for model_type, result in all_results.items():
        print(f"{result['name']:<25} {result['accuracy']:>10.4f} {result['roc_auc']:>10.4f} {result['pr_auc']:>10.4f}")

    # Select best model based on PR-AUC
    best_model_type = max(all_results, key=lambda x: all_results[x]['pr_auc'])
    best_pr_auc = all_results[best_model_type]['pr_auc']

    print("-"*55)
    print(f"\n[INFO] Best model: {all_results[best_model_type]['name']} (PR-AUC: {best_pr_auc:.4f})")

    return summary

if __name__ == '__main__':
    summary = main()
    print("\n[INFO] Models trained and saved successfully!")
    print(f"[INFO] Models location: {OUTPUT_DIR}")
