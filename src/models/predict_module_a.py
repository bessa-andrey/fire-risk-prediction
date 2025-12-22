# predict_module_a.py
"""
Module A Inference: Spurious Hotspot Detection on NEW Data
Classifies new FIRMS hotspots as true/spurious using trained classifier

Input:
  - Trained model (module_a_lightgbm.pkl)
  - NEW hotspots (CSV with: latitude, longitude, confidence, acq_datetime)
  - Auxiliary datasets for feature extraction (ERA5, Sentinel-2, MCD64A1)

Output:
  - predictions.csv (hotspot_id, latitude, longitude, prediction, probability, confidence)
  - predictions_summary.json (statistics, timestamp, model info)
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
import json
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

# Configuration
MODEL_DIR = Path('data/models/module_a')
INPUT_DIR = Path('data/processed/module_a')
OUTPUT_DIR = MODEL_DIR / 'predictions'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class ModuleAPredictor:
    """Production inference for Module A spurious hotspot detection"""

    def __init__(self, model_name: str = 'lightgbm', input_file: str = None):
        """
        Initialize predictor

        Args:
            model_name: 'lightgbm' or 'xgboost'
            input_file: Path to CSV with new hotspots (latitude, longitude, confidence, acq_datetime)
        """
        self.model_name = model_name
        self.input_file = input_file
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.new_hotspots = None
        self.predictions = None

        # Load training data to extract feature names
        self.features_file = INPUT_DIR / 'module_a_features.csv'

    def load_model(self) -> bool:
        """Load trained model from disk"""
        print(f"[INFO] Loading {self.model_name.upper()} model for inference...")

        model_path = MODEL_DIR / f'module_a_{self.model_name}.pkl'
        if not model_path.exists():
            print(f"[ERROR] Model not found: {model_path}")
            return False

        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"[OK] Model loaded: {model_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            return False

    def load_feature_names(self) -> bool:
        """Load feature names from training data"""
        print("[INFO] Loading feature names from training data...")

        if not self.features_file.exists():
            print(f"[ERROR] Features file not found: {self.features_file}")
            return False

        try:
            df_training = pd.read_csv(self.features_file, nrows=1)
            all_columns = df_training.columns.tolist()

            # Remove non-feature columns
            exclude_cols = {
                'label', 'label_text', 'hotspot_id', 'acq_datetime',
                'latitude', 'longitude', 'year', 'month', 'dayofyear'
            }
            self.feature_names = [col for col in all_columns if col not in exclude_cols]

            print(f"[OK] Loaded {len(self.feature_names)} feature names")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load feature names: {e}")
            return False

    def load_new_hotspots(self) -> bool:
        """Load new hotspots from CSV file"""
        print(f"[INFO] Loading new hotspots from {self.input_file}...")

        if not Path(self.input_file).exists():
            print(f"[ERROR] Input file not found: {self.input_file}")
            return False

        try:
            self.new_hotspots = pd.read_csv(self.input_file)

            # Validate required columns
            required_cols = {'latitude', 'longitude', 'confidence', 'acq_datetime'}
            missing_cols = required_cols - set(self.new_hotspots.columns)

            if missing_cols:
                print(f"[ERROR] Missing required columns: {missing_cols}")
                print(f"[ERROR] Required: latitude, longitude, confidence, acq_datetime")
                return False

            # Add hotspot_id if not present
            if 'hotspot_id' not in self.new_hotspots.columns:
                self.new_hotspots['hotspot_id'] = [f"new_hotspot_{i}" for i in range(len(self.new_hotspots))]

            print(f"[OK] Loaded {len(self.new_hotspots)} new hotspots")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load hotspots: {e}")
            return False

    def extract_features(self, hotspot_row: pd.Series) -> Dict[str, float]:
        """
        Extract features for a single hotspot

        For production use, this is a SIMPLIFIED version that fills missing features with zeros.
        For FULL feature extraction, integrate with ERA5/Sentinel-2/MCD64A1 data processing.

        Args:
            hotspot_row: Row from new_hotspots dataframe

        Returns:
            Dictionary with feature_name -> value
        """
        features = {}

        # Extract available features from input
        for fname in self.feature_names:
            if fname in hotspot_row.index:
                features[fname] = hotspot_row[fname]
            else:
                # For missing features, use zero (production fallback)
                # In full implementation, extract from ERA5/Sentinel-2/MCD64A1
                features[fname] = 0.0

        return features

    def extract_all_features(self) -> np.ndarray:
        """Extract features for all new hotspots"""
        print("[INFO] Extracting features for new hotspots...")

        feature_vectors = []

        for idx, row in tqdm(self.new_hotspots.iterrows(), total=len(self.new_hotspots), desc="Extracting features"):
            features_dict = self.extract_features(row)
            feature_vector = [features_dict.get(fname, 0.0) for fname in self.feature_names]
            feature_vectors.append(feature_vector)

        X = np.array(feature_vectors)

        # Scale using fitted scaler (from training)
        # Note: We need to fit scaler on training data first
        # Load scaler from training
        try:
            scaler_path = MODEL_DIR / 'scaler.pkl'
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print("[OK] Loaded scaler from training")
            else:
                # Fit scaler on training data as fallback
                print("[WARNING] Scaler not found, fitting on training data")
                df_training = pd.read_csv(self.features_file)
                X_train = df_training[self.feature_names].fillna(0).values
                self.scaler.fit(X_train)
        except Exception as e:
            print(f"[WARNING] Could not load/fit scaler: {e}")

        X_scaled = self.scaler.transform(X)

        print(f"[OK] Extracted features: shape {X_scaled.shape}")
        return X_scaled

    def make_predictions(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on new hotspots

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            predictions (0/1), probabilities (0-1)
        """
        print("[INFO] Making predictions...")

        try:
            # Predictions (class labels)
            y_pred = self.model.predict(X)

            # Probabilities for both classes
            y_pred_proba = self.model.predict_proba(X)

            # Extract probability for positive class (spurious=1)
            y_pred_proba_positive = y_pred_proba[:, 1]

            print(f"[OK] Made {len(y_pred)} predictions")
            return y_pred, y_pred_proba_positive
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return None, None

    def generate_predictions_df(self, y_pred: np.ndarray, y_pred_proba: np.ndarray) -> pd.DataFrame:
        """
        Generate predictions dataframe with all information

        Args:
            y_pred: Predicted labels (0=real, 1=spurious)
            y_pred_proba: Probabilities for spurious class

        Returns:
            DataFrame with predictions
        """
        print("[INFO] Generating predictions dataframe...")

        predictions_df = self.new_hotspots[['hotspot_id', 'latitude', 'longitude', 'confidence', 'acq_datetime']].copy()

        predictions_df['prediction'] = y_pred
        predictions_df['prediction_label'] = predictions_df['prediction'].map({
            0: 'REAL_HOTSPOT',
            1: 'SPURIOUS_HOTSPOT'
        })
        predictions_df['spurious_probability'] = y_pred_proba
        predictions_df['confidence_score'] = predictions_df['spurious_probability'].apply(
            lambda x: 'HIGH' if x >= 0.7 else ('MEDIUM' if x >= 0.5 else 'LOW')
        )
        predictions_df['prediction_timestamp'] = datetime.now().isoformat()
        predictions_df['model_used'] = self.model_name.upper()

        # Reorder columns for readability
        predictions_df = predictions_df[[
            'hotspot_id', 'latitude', 'longitude', 'confidence',
            'acq_datetime', 'prediction', 'prediction_label',
            'spurious_probability', 'confidence_score',
            'prediction_timestamp', 'model_used'
        ]]

        print(f"[OK] Generated predictions dataframe")
        return predictions_df

    def save_predictions(self, predictions_df: pd.DataFrame) -> str:
        """Save predictions to CSV"""
        output_file = OUTPUT_DIR / f'predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        try:
            predictions_df.to_csv(output_file, index=False)
            print(f"[OK] Predictions saved: {output_file}")
            return str(output_file)
        except Exception as e:
            print(f"[ERROR] Failed to save predictions: {e}")
            return None

    def generate_summary_report(self, predictions_df: pd.DataFrame, output_file: str) -> Dict:
        """Generate summary statistics"""
        print("[INFO] Generating summary report...")

        n_total = len(predictions_df)
        n_spurious = (predictions_df['prediction'] == 1).sum()
        n_real = (predictions_df['prediction'] == 0).sum()

        spurious_rate = n_spurious / n_total * 100
        real_rate = n_real / n_total * 100

        avg_spurious_prob = predictions_df['spurious_probability'].mean()
        max_spurious_prob = predictions_df['spurious_probability'].max()
        min_spurious_prob = predictions_df['spurious_probability'].min()

        report = {
            'prediction_timestamp': datetime.now().isoformat(),
            'model_used': self.model_name,
            'input_file': str(self.input_file),
            'output_file': output_file,
            'statistics': {
                'total_hotspots': int(n_total),
                'spurious_hotspots': int(n_spurious),
                'real_hotspots': int(n_real),
                'spurious_percentage': float(spurious_rate),
                'real_percentage': float(real_rate),
            },
            'probability_stats': {
                'mean_spurious_probability': float(avg_spurious_prob),
                'max_spurious_probability': float(max_spurious_prob),
                'min_spurious_probability': float(min_spurious_prob),
            },
            'confidence_distribution': {
                'high_confidence': int((predictions_df['confidence_score'] == 'HIGH').sum()),
                'medium_confidence': int((predictions_df['confidence_score'] == 'MEDIUM').sum()),
                'low_confidence': int((predictions_df['confidence_score'] == 'LOW').sum()),
            }
        }

        return report

    def save_summary_report(self, report: Dict, predictions_file: str) -> str:
        """Save summary report to JSON"""
        report_file = OUTPUT_DIR / f'predictions_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"[OK] Summary report saved: {report_file}")
            return str(report_file)
        except Exception as e:
            print(f"[ERROR] Failed to save report: {e}")
            return None

    def run(self) -> bool:
        """Execute full inference pipeline"""
        print("\n" + "="*60)
        print("MODULE A - SPURIOUS HOTSPOT DETECTION (INFERENCE)")
        print("="*60)
        print(f"Start time: {datetime.now().isoformat()}\n")

        # Step 1: Load model
        if not self.load_model():
            return False

        # Step 2: Load feature names
        if not self.load_feature_names():
            return False

        # Step 3: Load new hotspots
        if not self.load_new_hotspots():
            return False

        # Step 4: Extract features
        X = self.extract_all_features()
        if X is None:
            return False

        # Step 5: Make predictions
        y_pred, y_pred_proba = self.make_predictions(X)
        if y_pred is None:
            return False

        # Step 6: Generate predictions dataframe
        predictions_df = self.generate_predictions_df(y_pred, y_pred_proba)

        # Step 7: Save predictions
        predictions_file = self.save_predictions(predictions_df)
        if predictions_file is None:
            return False

        # Step 8: Generate summary report
        report = self.generate_summary_report(predictions_df, predictions_file)
        report_file = self.save_summary_report(report, predictions_file)

        # Step 9: Print summary
        print("\n" + "="*60)
        print("INFERENCE SUMMARY")
        print("="*60)
        print(f"Total hotspots analyzed: {report['statistics']['total_hotspots']}")
        print(f"  - Spurious: {report['statistics']['spurious_hotspots']} ({report['statistics']['spurious_percentage']:.1f}%)")
        print(f"  - Real: {report['statistics']['real_hotspots']} ({report['statistics']['real_percentage']:.1f}%)")
        print(f"\nPrediction confidence:")
        print(f"  - High: {report['confidence_distribution']['high_confidence']}")
        print(f"  - Medium: {report['confidence_distribution']['medium_confidence']}")
        print(f"  - Low: {report['confidence_distribution']['low_confidence']}")
        print(f"\nOutputs:")
        print(f"  - Predictions: {predictions_file}")
        print(f"  - Summary: {report_file}")
        print("\n" + "="*60)

        return True


def main():
    """Main execution"""
    import sys
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Module A Spurious Hotspot Detection Inference')
    parser.add_argument(
        '--input',
        type=str,
        required=False,
        default='data/processed/module_a/new_hotspots.csv',
        help='Path to CSV with new hotspots (default: data/processed/module_a/new_hotspots.csv)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='lightgbm',
        choices=['lightgbm', 'xgboost'],
        help='Which model to use (default: lightgbm)'
    )

    args = parser.parse_args()

    # Create predictor
    predictor = ModuleAPredictor(model_name=args.model, input_file=args.input)

    # Run inference
    success = predictor.run()

    return 0 if success else 1


if __name__ == '__main__':
    import sys
    exit_code = main()
    print(f"\nEnd time: {datetime.now().isoformat()}")
    sys.exit(exit_code)
