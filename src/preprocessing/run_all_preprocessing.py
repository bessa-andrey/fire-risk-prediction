# run_all_preprocessing.py
"""
Master script to run all Etapa 2 preprocessing steps in sequence
Handles all data transformations: raw → processed
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

def run_script(script_path: str, description: str) -> bool:
    """Run a preprocessing script and return success status"""
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

def verify_inputs() -> bool:
    """Verify that all input data exists before processing"""
    print("\n" + "="*60)
    print("VERIFYING INPUT DATA")
    print("="*60)

    inputs = {
        'FIRMS': Path('data/raw/firms_hotspots/firms_combined_2022-2024.csv'),
        'MCD64A1': Path('data/raw/mcd64a1'),
        'Sentinel-2': Path('data/raw/sentinel2'),
        'ERA5': Path('data/raw/era5')
    }

    all_exist = True
    for name, path in inputs.items():
        exists = path.exists()
        status = "[OK]" if exists else "[WARNING]"
        print(f"{status} {name}: {path}")

        if not exists:
            all_exist = False

    return all_exist

def create_output_directories():
    """Create output directories for processed data"""
    print("\n[INFO] Creating output directories...")

    dirs = [
        'data/processed/firms',
        'data/processed/burned_area',
        'data/processed/sentinel2',
        'data/processed/era5'
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created: {dir_path}")

def generate_summary(results: dict):
    """Generate processing summary"""
    summary = {
        'processing_timestamp': datetime.now().isoformat(),
        'etapa': 'Etapa 2 - Processamento de Dados',
        'results': results,
        'all_success': all(results.values())
    }

    return summary

def main():
    """Main execution pipeline"""
    print("\n" + "="*60)
    print("ETAPA 2 - PROCESSAMENTO DE DADOS (MASTER SCRIPT)")
    print("="*60)
    print(f"Start time: {datetime.now().isoformat()}")

    # Step 1: Verify inputs
    inputs_ok = verify_inputs()

    if not inputs_ok:
        print("\n[WARNING] Some input data is missing!")
        print("[INFO] Make sure Etapa 1 (data ingest) is complete")
        print("[INFO] Expected files:")
        print("  - data/raw/firms_hotspots/firms_combined_2022-2024.csv")
        print("  - data/raw/mcd64a1/MCD64A1_*.tif (36 files)")
        print("  - data/raw/sentinel2/Sentinel2_*.tif (6 files)")
        print("  - data/raw/era5/ERA5_*.nc (12+ files)")

        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Aborted.")
            return

    # Step 2: Create output directories
    create_output_directories()

    # Step 3: Run preprocessing scripts in sequence
    scripts = [
        ('src/preprocessing/process_firms.py', 'Step 1/4: Process FIRMS hotspots'),
        ('src/preprocessing/process_mcd64a1.py', 'Step 2/4: Process MCD64A1 burned area'),
        ('src/preprocessing/process_sentinel2.py', 'Step 3/4: Process Sentinel-2 imagery'),
        ('src/preprocessing/process_era5.py', 'Step 4/4: Process ERA5 meteorological data'),
    ]

    results = {}

    for script_path, description in scripts:
        success = run_script(script_path, description)
        # Extract script name for results
        script_name = Path(script_path).stem
        results[script_name] = success

        if not success:
            print(f"\n[WARNING] {description} failed!")
            print("[INFO] You can:")
            print("  1. Fix the issue and re-run the master script")
            print("  2. Run the failed script individually for debugging")
            print("  3. Continue with other scripts (this script will skip failed ones)")

            response = input("Continue with next script? (y/n): ")
            if response.lower() != 'y':
                print("[INFO] Stopping.")
                break

    # Step 4: Load and verify processed data
    print("\n" + "="*60)
    print("VERIFYING PROCESSED DATA")
    print("="*60)

    from data_loader import DataLoader

    loader = DataLoader()
    all_datasets = loader.load_all()

    # Step 5: Generate summary
    summary = generate_summary(results)

    print("\n" + "="*60)
    print("ETAPA 2 - SUMMARY")
    print("="*60)
    print(f"process_firms: {'[OK]' if results.get('process_firms') else '[FAILED]'}")
    print(f"process_mcd64a1: {'[OK]' if results.get('process_mcd64a1') else '[FAILED]'}")
    print(f"process_sentinel2: {'[OK]' if results.get('process_sentinel2') else '[FAILED]'}")
    print(f"process_era5: {'[OK]' if results.get('process_era5') else '[FAILED]'}")

    success_count = sum(1 for v in results.values() if v)
    print(f"\nSuccess: {success_count}/{len(results)} scripts completed")

    if summary['all_success']:
        print("\n[OK] All preprocessing steps completed successfully!")
        print("[INFO] Processed data is ready for Etapa 3 (Feature Engineering)")
    else:
        print("\n[WARNING] Some preprocessing steps failed")
        print("[INFO] Review error messages above")

    # Save summary
    summary_file = Path('data/processed/processing_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n[OK] Summary saved to: {summary_file}")
    print(f"\nEnd time: {datetime.now().isoformat()}")

    return 0 if summary['all_success'] else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
