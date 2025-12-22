# run_module_a_pipeline.py
"""
Complete Module A Pipeline: Data → Training → Validation → Inference

This master script orchestrates all phases of Module A development:
  1. Feature Engineering (from Etapa 3)
  2. Model Training (from Etapa 3)
  3. Model Validation (from Etapa 4)
  4. Model Inference (NEW - identify spurious hotspots in production)

Supports both full pipeline execution and individual step execution.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json
from argparse import ArgumentParser

def run_script(script_path: str, description: str) -> bool:
    """Run a script and return success status"""
    print(f"\n{'='*60}")
    print(f"[INFO] {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=Path.cwd(),
            capture_output=False
        )

        if result.returncode == 0:
            print(f"\n[OK] {description} completed successfully!")
            return True
        else:
            print(f"\n[ERROR] {description} failed with code {result.returncode}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Exception running {script_path}: {e}")
        return False

def verify_inputs(skip_feature_engineering: bool = False):
    """Verify all required input files exist"""
    print("\n" + "="*60)
    print("VERIFYING INPUTS")
    print("="*60)

    required_files = {
        'Processed FIRMS data': Path('data/processed/module_a/firms_processed.csv'),
        'MCD64A1 burned area': Path('data/processed/module_a/mcd64a1_burned_area.nc'),
        'Sentinel-2 data': Path('data/processed/module_a/sentinel2_data.nc'),
        'ERA5 data': Path('data/processed/module_a/era5_daily_aggregates.nc'),
    }

    all_exist = True
    for name, path in required_files.items():
        exists = path.exists()
        status = "[OK]" if exists else "[WARNING]"
        print(f"{status} {name}: {path}")
        if not exists:
            all_exist = False

    return all_exist

def verify_trained_model():
    """Verify trained model exists"""
    print("\n" + "="*60)
    print("VERIFYING TRAINED MODEL")
    print("="*60)

    model_path = Path('data/models/module_a/module_a_lightgbm.pkl')
    features_path = Path('data/processed/module_a/module_a_features.csv')

    model_exists = model_path.exists()
    features_exist = features_path.exists()

    print(f"{'[OK]' if model_exists else '[WARNING]'} Model: {model_path}")
    print(f"{'[OK]' if features_exist else '[WARNING]'} Features: {features_path}")

    return model_exists and features_exist

def verify_inference_input(input_file: str):
    """Verify inference input file exists"""
    print("\n" + "="*60)
    print("VERIFYING INFERENCE INPUT")
    print("="*60)

    input_path = Path(input_file)
    exists = input_path.exists()

    print(f"{'[OK]' if exists else '[WARNING]'} Input file: {input_path}")

    if not exists:
        print(f"\n[INFO] Expected format: CSV with columns:")
        print(f"  - hotspot_id (optional)")
        print(f"  - latitude")
        print(f"  - longitude")
        print(f"  - confidence")
        print(f"  - acq_datetime")

    return exists

def run_full_pipeline():
    """Run complete pipeline: Feature Engineering → Training → Validation"""
    print("\n" + "="*80)
    print("MODULE A - FULL PIPELINE (FEATURES + TRAINING + VALIDATION)")
    print("="*80)
    print(f"Start time: {datetime.now().isoformat()}\n")

    # Step 1: Verify input data
    if not verify_inputs():
        print("\n[WARNING] Some input files missing!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Aborted.")
            return False

    # Step 2: Feature Engineering
    print("\n" + "-"*60)
    if not run_script(
        'src/preprocessing/feature_engineering.py',
        'Feature Engineering (Etapa 3, Step 2)'
    ):
        print("[ERROR] Feature engineering failed. Cannot continue.")
        return False

    # Step 3: Model Training
    print("\n" + "-"*60)
    if not run_script(
        'src/models/train_module_a.py',
        'Model Training (Etapa 3, Step 3)'
    ):
        print("[ERROR] Model training failed. Cannot continue.")
        return False

    # Step 4: Model Validation
    print("\n" + "-"*60)
    if not run_script(
        'src/models/evaluate_module_a.py',
        'Model Validation (Etapa 4)'
    ):
        print("[ERROR] Model validation failed.")
        return False

    # Step 5: Summary
    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    print("[OK] All steps completed successfully!")
    print("\nOutputs:")
    print("  - Trained models: data/models/module_a/")
    print("  - Validation results: data/models/module_a/validation/")
    print("\nNext steps:")
    print("  - Use trained model for inference on new hotspots")
    print("  - Run: python src/models/predict_module_a.py --input <your_hotspots.csv>")

    return True

def run_training_only():
    """Run only training and validation (assumes features exist)"""
    print("\n" + "="*80)
    print("MODULE A - TRAINING + VALIDATION ONLY")
    print("="*80)
    print(f"Start time: {datetime.now().isoformat()}\n")

    # Step 1: Model Training
    print("\n" + "-"*60)
    if not run_script(
        'src/models/train_module_a.py',
        'Model Training (Etapa 3, Step 3)'
    ):
        print("[ERROR] Model training failed. Cannot continue.")
        return False

    # Step 2: Model Validation
    print("\n" + "-"*60)
    if not run_script(
        'src/models/evaluate_module_a.py',
        'Model Validation (Etapa 4)'
    ):
        print("[ERROR] Model validation failed.")
        return False

    print("\n" + "="*60)
    print("[OK] Training and validation completed!")

    return True

def run_inference(input_file: str, model: str = 'lightgbm'):
    """Run inference on new hotspots"""
    print("\n" + "="*80)
    print("MODULE A - INFERENCE (SPURIOUS HOTSPOT DETECTION)")
    print("="*80)
    print(f"Start time: {datetime.now().isoformat()}\n")

    # Step 1: Verify trained model
    if not verify_trained_model():
        print("\n[ERROR] Trained model not found!")
        print("[INFO] Please run training first:")
        print("[INFO]   python src/models/run_module_a_pipeline.py --mode training")
        return False

    # Step 2: Verify inference input
    if not verify_inference_input(input_file):
        print("\n[ERROR] Inference input file not found!")
        print("[INFO] Please provide a CSV file with columns: latitude, longitude, confidence, acq_datetime")
        return False

    # Step 3: Run inference
    print("\n" + "-"*60)
    cmd = [
        sys.executable,
        'src/models/predict_module_a.py',
        '--input', input_file,
        '--model', model
    ]

    try:
        result = subprocess.run(cmd, cwd=Path.cwd(), capture_output=False)
        if result.returncode == 0:
            print(f"\n[OK] Inference completed successfully!")
            print("\nOutputs in: data/models/module_a/predictions/")
            return True
        else:
            print(f"\n[ERROR] Inference failed with code {result.returncode}")
            return False
    except Exception as e:
        print(f"\n[ERROR] Exception during inference: {e}")
        return False

def main():
    """Main entry point"""
    parser = ArgumentParser(description='Module A Complete Pipeline')
    parser.add_argument(
        '--mode',
        type=str,
        choices=['full', 'training', 'inference'],
        default='full',
        help='Pipeline mode: full (features+training+validation), training (training+validation only), inference (on new data)'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/processed/module_a/new_hotspots.csv',
        help='Input file for inference mode (default: data/processed/module_a/new_hotspots.csv)'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=['lightgbm', 'xgboost'],
        default='lightgbm',
        help='Model to use for inference (default: lightgbm)'
    )

    args = parser.parse_args()

    # Execute based on mode
    if args.mode == 'full':
        success = run_full_pipeline()
    elif args.mode == 'training':
        success = run_training_only()
    elif args.mode == 'inference':
        success = run_inference(args.input, args.model)
    else:
        print(f"[ERROR] Unknown mode: {args.mode}")
        return 1

    # Summary
    print("\n" + "="*80)
    if success:
        print("[COMPLETE] Pipeline executed successfully!")
        return 0
    else:
        print("[FAILED] Pipeline execution failed. Check errors above.")
        return 1

    print(f"End time: {datetime.now().isoformat()}\n")

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
