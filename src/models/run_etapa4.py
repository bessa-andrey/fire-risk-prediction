# run_etapa4.py
"""
Master script for Etapa 4: Validation
Runs comprehensive evaluation of Module A classifier
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

def verify_etapa3_outputs():
    """Verify that Etapa 3 outputs exist"""
    print("\n" + "="*60)
    print("VERIFYING ETAPA 3 OUTPUTS")
    print("="*60)

    required_files = {
        'Features': Path('data/processed/module_a/module_a_features.csv'),
        'LightGBM Model': Path('data/models/module_a/module_a_lightgbm.pkl'),
        'XGBoost Model': Path('data/models/module_a/module_a_xgboost.pkl'),
        'Training Summary': Path('data/models/module_a/training_summary.json'),
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
    print("ETAPA 4 - VALIDAÇÃO (MASTER SCRIPT)")
    print("="*60)
    print(f"Start time: {datetime.now().isoformat()}")

    # Step 1: Verify Etapa 3 outputs
    etapa3_ok = verify_etapa3_outputs()

    if not etapa3_ok:
        print("\n[WARNING] Some Etapa 3 outputs are missing!")
        print("[INFO] Make sure Etapa 3 (training) is complete")
        print("[INFO] Run: python src/preprocessing/run_etapa3.py")

        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Aborted.")
            return 1

    # Step 2: Run validation
    print("\n" + "-"*60)
    success = run_script(
        'src/models/evaluate_module_a.py',
        'Module A Comprehensive Validation'
    )

    # Step 3: Generate summary
    print("\n" + "="*60)
    print("ETAPA 4 - SUMMARY")
    print("="*60)

    if success:
        print("[OK] Validation completed successfully!")

        # Check if outputs exist
        output_dir = Path('data/models/module_a/validation')
        if output_dir.exists():
            outputs = list(output_dir.glob('*'))
            print(f"\n[OK] Generated {len(outputs)} output files:")
            for output in sorted(outputs):
                size_kb = output.stat().st_size / 1024
                print(f"  - {output.name} ({size_kb:.1f} KB)")

        print("\n[INFO] Validation outputs available at:")
        print(f"  {output_dir}")

        print("\n[INFO] Key outputs:")
        print("  - spatial_validation.csv (performance by region)")
        print("  - temporal_validation.csv (performance by year)")
        print("  - confidence_analysis.csv (performance by confidence level)")
        print("  - roc_curve.png (visualization)")
        print("  - pr_curve.png (visualization)")
        print("  - confusion_matrix.png (visualization)")
        print("  - feature_importance.png (visualization)")
        print("  - validation_report.json (complete report)")

        # Save metadata
        metadata = {
            'validation_date': datetime.now().isoformat(),
            'etapa': 'Etapa 4 - Validação',
            'status': 'success',
            'outputs_generated': len(outputs)
        }

        summary_path = Path('data/models/module_a/validation/validation_metadata.json')
        with open(summary_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n[OK] Validation complete and successful!")
        return 0

    else:
        print("\n[ERROR] Validation failed!")
        print("[INFO] Check error messages above")
        return 1

if __name__ == '__main__':
    exit_code = main()
    print(f"\nEnd time: {datetime.now().isoformat()}")
    sys.exit(exit_code)
