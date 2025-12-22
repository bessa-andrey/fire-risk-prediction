# run_etapa3.py
"""
Master script for Etapa 3: Feature Engineering
Runs all feature engineering steps in sequence
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

def run_script(script_path: str, description: str) -> bool:
    """Run a script and return success status"""
    print(f"\n{'='*60}")
    print(f"[INFO] {description}")
    print(f"{'='*60}")
    print(f"Running: {script_path}")

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

def verify_etapa2_outputs():
    """Verify that Etapa 2 outputs exist"""
    print("\n" + "="*60)
    print("VERIFYING ETAPA 2 OUTPUTS")
    print("="*60)

    required_files = {
        'FIRMS': Path('data/processed/firms/firms_processed.csv'),
        'MCD64A1': Path('data/processed/burned_area/mcd64a1_burned_area.nc'),
        'Sentinel-2': Path('data/processed/sentinel2/sentinel2_dry_composite.nc'),
        'ERA5': Path('data/processed/era5/era5_daily_aggregates.nc'),
    }

    all_exist = True
    for name, path in required_files.items():
        exists = path.exists()
        status = "[OK]" if exists else "[WARNING]"
        print(f"{status} {name}: {path}")

        if not exists:
            all_exist = False

    return all_exist

def main():
    """Main execution pipeline"""
    print("\n" + "="*60)
    print("ETAPA 3 - FEATURE ENGINEERING (MASTER SCRIPT)")
    print("="*60)
    print(f"Start time: {datetime.now().isoformat()}")

    # Step 1: Verify Etapa 2 outputs
    etapa2_ok = verify_etapa2_outputs()

    if not etapa2_ok:
        print("\n[WARNING] Some Etapa 2 outputs are missing!")
        print("[INFO] Make sure Etapa 2 (preprocessing) is complete")
        print("[INFO] Run: python src/preprocessing/run_all_preprocessing.py")

        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Aborted.")
            return 1

    # Step 2: Run weak labeling
    print("\n" + "-"*60)
    scripts = [
        ('src/preprocessing/weak_labeling.py', 'Step 1/3: Weak Labeling (FIRMS vs MCD64A1)'),
        ('src/preprocessing/feature_engineering.py', 'Step 2/3: Feature Engineering'),
        ('src/models/train_module_a.py', 'Step 3/3: Train Module A Classifier'),
    ]

    results = {}

    for script_path, description in scripts:
        success = run_script(script_path, description)
        script_name = Path(script_path).stem
        results[script_name] = success

        if not success:
            print(f"\n[WARNING] {description} failed!")
            print("[INFO] You can:")
            print("  1. Fix the issue and re-run")
            print("  2. Run the failed script individually for debugging")
            print("  3. Continue with next steps (this script will skip failed ones)")

            response = input("Continue with next script? (y/n): ")
            if response.lower() != 'y':
                print("[INFO] Stopping.")
                break

    # Step 3: Generate summary
    print("\n" + "="*60)
    print("ETAPA 3 - SUMMARY")
    print("="*60)
    print(f"weak_labeling: {'[OK]' if results.get('weak_labeling') else '[FAILED]'}")
    print(f"feature_engineering: {'[OK]' if results.get('feature_engineering') else '[FAILED]'}")
    print(f"train_module_a: {'[OK]' if results.get('train_module_a') else '[FAILED]'}")

    success_count = sum(1 for v in results.values() if v)
    print(f"\nSuccess: {success_count}/{len(results)} steps completed")

    summary = {
        'processing_timestamp': datetime.now().isoformat(),
        'etapa': 'Etapa 3 - Feature Engineering',
        'results': results,
        'all_success': all(results.values())
    }

    if summary['all_success']:
        print("\n[OK] All Etapa 3 steps completed successfully!")
        print("[INFO] Module A classifier is ready!")
    else:
        print("\n[WARNING] Some Etapa 3 steps failed")
        print("[INFO] Review error messages above")

    # Save summary
    summary_file = Path('data/processed/etapa3_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n[OK] Summary saved to: {summary_file}")
    print(f"End time: {datetime.now().isoformat()}")

    return 0 if summary['all_success'] else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
