# evaluate_module_a.py
"""
Module A Validation: Spatial, Temporal, and Confidence-based evaluation
Analyzes model performance across different dimensions

Input: Trained models (module_a_lightgbm.pkl, module_a_xgboost.pkl)
       Features and labels (module_a_features.csv)
       Processed data for spatial/temporal context

Output:
  - spatial_validation.csv
  - temporal_validation.csv
  - confidence_analysis.csv
  - roc_curve.png, pr_curve.png, confusion_matrix.png, feature_importance.png
  - validation_report.json
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_curve, auc, precision_recall_curve, confusion_matrix,
    classification_report, roc_auc_score, precision_recall_fscore_support
)
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Configuration
FEATURES_FILE = Path('data/processed/module_a/module_a_features.csv')
MODEL_DIR = Path('data/models/module_a')
OUTPUT_DIR = MODEL_DIR / 'validation'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# MATOPIBA bounds for spatial analysis
REGION_BOUNDS = {
    'maranhao': {'lat_min': -10.3, 'lat_max': -2.8, 'lon_min': -59.0, 'lon_max': -42.8},
    'tocantins': {'lat_min': -10.2, 'lat_max': -0.8, 'lon_min': -63.1, 'lon_max': -48.3},
    'piaui': {'lat_min': -10.5, 'lat_max': -2.8, 'lon_min': -62.5, 'lon_max': -40.3},
    'bahia': {'lat_min': -19.0, 'lat_max': -9.1, 'lon_min': -63.9, 'lon_max': -37.2},
}

class ModuleAValidator:
    """Comprehensive validation of Module A classifier"""

    def __init__(self, model_name: str = 'lightgbm'):
        self.model_name = model_name
        self.model = None
        self.scaler = StandardScaler()
        self.X_test = None
        self.y_test = None
        self.y_pred = None
        self.y_pred_proba = None
        self.X_full = None
        self.y_full = None
        self.features_df = None

    def load_model_and_data(self):
        """Load trained model and test data"""
        print(f"[INFO] Loading {self.model_name.upper()} model...")

        # Load model
        model_path = MODEL_DIR / f'module_a_{self.model_name}.pkl'
        if not model_path.exists():
            print(f"[ERROR] Model not found: {model_path}")
            return False

        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        print(f"[OK] Model loaded")

        # Load features
        if not FEATURES_FILE.exists():
            print(f"[ERROR] Features file not found: {FEATURES_FILE}")
            return False

        self.features_df = pd.read_csv(FEATURES_FILE)
        print(f"[OK] Loaded {len(self.features_df)} samples")

        # Prepare data
        y = self.features_df['label'].values
        X = self.features_df.drop(
            columns=['label', 'label_text', 'hotspot_id', 'acq_datetime', 'latitude', 'longitude'],
            errors='ignore'
        ).fillna(0)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train-test split (same as training)
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        self.X_test = X_test
        self.y_test = y_test
        self.X_full = X_scaled
        self.y_full = y

        # Make predictions
        self.y_pred = self.model.predict(self.X_test)
        self.y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]

        print(f"[OK] Predictions made on {len(self.X_test)} test samples")
        return True

    def spatial_validation(self) -> pd.DataFrame:
        """Evaluate performance by region (spatial splits)"""
        print("[INFO] Running spatial validation...")

        spatial_results = []

        for region_name, bounds in REGION_BOUNDS.items():
            # Filter features by region
            region_mask = (
                (self.features_df['latitude'] >= bounds['lat_min']) &
                (self.features_df['latitude'] <= bounds['lat_max']) &
                (self.features_df['longitude'] >= bounds['lon_min']) &
                (self.features_df['longitude'] <= bounds['lon_max'])
            )

            if region_mask.sum() == 0:
                print(f"[WARNING] No samples in {region_name}")
                continue

            region_indices = region_mask[region_mask].index
            y_region = self.y_full[region_indices]
            X_region = self.X_full[region_indices]

            # Predictions for region
            y_pred_region = self.model.predict(X_region)
            y_pred_proba_region = self.model.predict_proba(X_region)[:, 1]

            # Calculate metrics
            from sklearn.metrics import accuracy_score, roc_auc_score, precision_recall_fscore_support

            accuracy = accuracy_score(y_region, y_pred_region)
            try:
                roc_auc = roc_auc_score(y_region, y_pred_proba_region)
            except:
                roc_auc = np.nan

            precision, recall, f1, _ = precision_recall_fscore_support(
                y_region, y_pred_region, average='weighted', zero_division=0
            )

            spatial_results.append({
                'region': region_name,
                'samples': len(y_region),
                'accuracy': accuracy,
                'roc_auc': roc_auc,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'true_positives': (y_pred_region == 1).sum(),
                'false_positives': ((y_pred_region == 1) & (y_region == 0)).sum(),
            })

            print(f"[OK] {region_name}: {accuracy:.4f} accuracy ({len(y_region)} samples)")

        spatial_df = pd.DataFrame(spatial_results)
        return spatial_df

    def temporal_validation(self) -> pd.DataFrame:
        """Evaluate performance by year (temporal splits)"""
        print("[INFO] Running temporal validation...")

        temporal_results = []

        # Extract year from acq_datetime
        self.features_df['year'] = pd.to_datetime(self.features_df['acq_datetime']).dt.year

        for year in sorted(self.features_df['year'].unique()):
            year_mask = self.features_df['year'] == year
            year_indices = year_mask[year_mask].index

            y_year = self.y_full[year_indices]
            X_year = self.X_full[year_indices]

            if len(y_year) == 0:
                continue

            # Predictions for year
            y_pred_year = self.model.predict(X_year)
            y_pred_proba_year = self.model.predict_proba(X_year)[:, 1]

            # Calculate metrics
            from sklearn.metrics import accuracy_score, roc_auc_score, precision_recall_fscore_support

            accuracy = accuracy_score(y_year, y_pred_year)
            try:
                roc_auc = roc_auc_score(y_year, y_pred_proba_year)
            except:
                roc_auc = np.nan

            precision, recall, f1, _ = precision_recall_fscore_support(
                y_year, y_pred_year, average='weighted', zero_division=0
            )

            temporal_results.append({
                'year': int(year),
                'samples': len(y_year),
                'accuracy': accuracy,
                'roc_auc': roc_auc,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'true_positives': (y_pred_year == 1).sum(),
                'false_positives': ((y_pred_year == 1) & (y_year == 0)).sum(),
            })

            print(f"[OK] Year {year}: {accuracy:.4f} accuracy ({len(y_year)} samples)")

        temporal_df = pd.DataFrame(temporal_results)
        return temporal_df

    def confidence_analysis(self) -> pd.DataFrame:
        """Analyze performance by FIRMS confidence level"""
        print("[INFO] Running confidence analysis...")

        confidence_results = []

        # Confidence bins
        bins = [0, 30, 50, 70, 100]
        labels = ['0-30%', '30-50%', '50-70%', '70-100%']

        if 'confidence' not in self.features_df.columns:
            print("[WARNING] Confidence column not found")
            return pd.DataFrame()

        self.features_df['confidence_bin'] = pd.cut(
            self.features_df['confidence'], bins=bins, labels=labels, include_lowest=True
        )

        for conf_bin in labels:
            bin_mask = self.features_df['confidence_bin'] == conf_bin
            bin_indices = bin_mask[bin_mask].index

            if len(bin_indices) == 0:
                continue

            y_bin = self.y_full[bin_indices]
            X_bin = self.X_full[bin_indices]

            # Predictions
            y_pred_bin = self.model.predict(X_bin)
            y_pred_proba_bin = self.model.predict_proba(X_bin)[:, 1]

            # Calculate metrics
            from sklearn.metrics import accuracy_score, roc_auc_score, precision_recall_fscore_support

            accuracy = accuracy_score(y_bin, y_pred_bin)
            try:
                roc_auc = roc_auc_score(y_bin, y_pred_proba_bin)
            except:
                roc_auc = np.nan

            precision, recall, f1, _ = precision_recall_fscore_support(
                y_bin, y_pred_bin, average='weighted', zero_division=0
            )

            confidence_results.append({
                'confidence_level': conf_bin,
                'samples': len(y_bin),
                'accuracy': accuracy,
                'roc_auc': roc_auc,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
            })

            print(f"[OK] Confidence {conf_bin}: {accuracy:.4f} accuracy ({len(y_bin)} samples)")

        confidence_df = pd.DataFrame(confidence_results)
        return confidence_df

    def plot_roc_curve(self):
        """Plot ROC curve"""
        print("[INFO] Plotting ROC curve...")

        fpr, tpr, _ = roc_curve(self.y_test, self.y_pred_proba)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - Module A ({self.model_name.upper()})')
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)

        plt.savefig(OUTPUT_DIR / 'roc_curve.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] ROC curve saved")

    def plot_pr_curve(self):
        """Plot Precision-Recall curve"""
        print("[INFO] Plotting PR curve...")

        precision, recall, _ = precision_recall_curve(self.y_test, self.y_pred_proba)
        pr_auc = auc(recall, precision)

        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color='blue', lw=2, label=f'PR curve (AUC = {pr_auc:.3f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve - Module A ({self.model_name.upper()})')
        plt.legend(loc="lower left")
        plt.grid(alpha=0.3)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])

        plt.savefig(OUTPUT_DIR / 'pr_curve.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] PR curve saved")

    def plot_confusion_matrix(self):
        """Plot confusion matrix"""
        print("[INFO] Plotting confusion matrix...")

        cm = confusion_matrix(self.y_test, self.y_pred)

        plt.figure(figsize=(8, 6))
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title(f'Confusion Matrix - Module A ({self.model_name.upper()})')
        plt.colorbar()

        tick_marks = np.arange(2)
        plt.xticks(tick_marks, ['False Positive', 'True Positive'])
        plt.yticks(tick_marks, ['False Positive', 'True Positive'])

        # Add text annotations
        thresh = cm.max() / 2.
        for i, j in np.ndindex(cm.shape):
            plt.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")

        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.tight_layout()

        plt.savefig(OUTPUT_DIR / 'confusion_matrix.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[OK] Confusion matrix saved")

    def plot_feature_importance(self):
        """Plot feature importance (if LightGBM)"""
        print("[INFO] Plotting feature importance...")

        try:
            # Only works for LightGBM/XGBoost with feature_importances_
            if not hasattr(self.model, 'feature_importances_'):
                print("[WARNING] Model does not support feature importance")
                return

            importances = self.model.feature_importances_
            indices = np.argsort(importances)[-10:]  # Top 10

            feature_names = self.features_df.drop(
                columns=['label', 'label_text', 'hotspot_id', 'acq_datetime', 'latitude', 'longitude'],
                errors='ignore'
            ).columns.tolist()

            plt.figure(figsize=(10, 6))
            plt.barh(range(len(indices)), importances[indices], color='steelblue')
            plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
            plt.xlabel('Importance')
            plt.title(f'Top 10 Feature Importance - Module A ({self.model_name.upper()})')
            plt.tight_layout()

            plt.savefig(OUTPUT_DIR / 'feature_importance.png', dpi=150, bbox_inches='tight')
            plt.close()
            print(f"[OK] Feature importance saved")
        except Exception as e:
            print(f"[WARNING] Could not plot feature importance: {e}")

    def generate_report(self, spatial_df, temporal_df, confidence_df):
        """Generate validation report"""
        print("[INFO] Generating validation report...")

        # Overall metrics
        from sklearn.metrics import accuracy_score, roc_auc_score, precision_recall_fscore_support

        accuracy = accuracy_score(self.y_test, self.y_pred)
        roc_auc = roc_auc_score(self.y_test, self.y_pred_proba)
        precision, recall, f1, _ = precision_recall_fscore_support(
            self.y_test, self.y_pred, average='weighted'
        )

        precision_recall, recall_pr, _ = precision_recall_curve(self.y_test, self.y_pred_proba)
        pr_auc = auc(recall_pr, precision_recall)

        report = {
            'validation_date': datetime.now().isoformat(),
            'model_name': self.model_name,
            'overall_metrics': {
                'accuracy': float(accuracy),
                'roc_auc': float(roc_auc),
                'pr_auc': float(pr_auc),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'test_samples': int(len(self.y_test)),
            },
            'spatial_validation': spatial_df.to_dict('records') if len(spatial_df) > 0 else [],
            'temporal_validation': temporal_df.to_dict('records') if len(temporal_df) > 0 else [],
            'confidence_analysis': confidence_df.to_dict('records') if len(confidence_df) > 0 else [],
        }

        report_path = OUTPUT_DIR / 'validation_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"[OK] Validation report saved")
        return report

def main():
    """Main validation pipeline"""
    print("\n" + "="*60)
    print("MODULE A VALIDATION - ETAPA 4")
    print("="*60)

    # Step 1: Load model and data
    validator = ModuleAValidator(model_name='lightgbm')

    if not validator.load_model_and_data():
        print("[ERROR] Failed to load model and data")
        return

    # Step 2: Spatial validation
    spatial_df = validator.spatial_validation()
    spatial_path = OUTPUT_DIR / 'spatial_validation.csv'
    spatial_df.to_csv(spatial_path, index=False)
    print(f"[OK] Spatial validation saved to {spatial_path}")

    # Step 3: Temporal validation
    temporal_df = validator.temporal_validation()
    temporal_path = OUTPUT_DIR / 'temporal_validation.csv'
    temporal_df.to_csv(temporal_path, index=False)
    print(f"[OK] Temporal validation saved to {temporal_path}")

    # Step 4: Confidence analysis
    confidence_df = validator.confidence_analysis()
    confidence_path = OUTPUT_DIR / 'confidence_analysis.csv'
    confidence_df.to_csv(confidence_path, index=False)
    print(f"[OK] Confidence analysis saved to {confidence_path}")

    # Step 5: Generate plots
    print("\n[INFO] Generating visualizations...")
    validator.plot_roc_curve()
    validator.plot_pr_curve()
    validator.plot_confusion_matrix()
    validator.plot_feature_importance()

    # Step 6: Generate report
    report = validator.generate_report(spatial_df, temporal_df, confidence_df)

    # Step 7: Print summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"\nOverall Metrics:")
    print(f"  Accuracy: {report['overall_metrics']['accuracy']:.4f}")
    print(f"  ROC-AUC: {report['overall_metrics']['roc_auc']:.4f}")
    print(f"  PR-AUC: {report['overall_metrics']['pr_auc']:.4f}")
    print(f"  F1-Score: {report['overall_metrics']['f1_score']:.4f}")

    if len(spatial_df) > 0:
        print(f"\nSpatial Validation (by region):")
        for _, row in spatial_df.iterrows():
            print(f"  {row['region']}: {row['accuracy']:.4f} ({row['samples']} samples)")

    if len(temporal_df) > 0:
        print(f"\nTemporal Validation (by year):")
        for _, row in temporal_df.iterrows():
            print(f"  {int(row['year'])}: {row['accuracy']:.4f} ({row['samples']} samples)")

    if len(confidence_df) > 0:
        print(f"\nConfidence Analysis:")
        for _, row in confidence_df.iterrows():
            print(f"  {row['confidence_level']}: {row['accuracy']:.4f} ({row['samples']} samples)")

    print(f"\n[OK] All validation outputs saved to {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
    print("\n[INFO] Validation complete! Check OUTPUT_DIR for reports and plots.")
