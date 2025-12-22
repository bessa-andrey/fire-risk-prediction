# run_all_downloads.py
"""
Master script to run all data ingestion downloads for MATOPIBA (2022-2024)

This script coordinates downloading from:
1. NASA FIRMS (hotspot detection)
2. Google Earth Engine (MODIS MCD64A1, Sentinel-2)
3. Copernicus CDS (ERA5 meteorology)

Each script can also be run independently.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_script(script_name, description):
    """
    Run a download script with error handling

    Args:
        script_name: str - script filename
        description: str - human-readable description
    """
    print(f"\n{'='*60}")
    print(f"STARTING: {description}")
    print(f"{'='*60}")

    script_path = Path(__file__).parent / script_name

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            timeout=3600  # 1 hour timeout per script
        )

        if result.returncode == 0:
            print(f"{description} - COMPLETED")
            return True
        else:
            print(f"{description} - FINISHED WITH WARNINGS")
            return False

    except subprocess.TimeoutExpired:
        print(f"{description} - TIMEOUT (exceeded 1 hour)")
        return False
    except Exception as e:
        print(f"{description} - ERROR: {e}")
        return False

def main():
    """Main coordinator function"""
    print("\n" + "="*70)
    print(" " * 10 + "MATOPIBA DATA INGESTION - ALL DOWNLOADS")
    print(" " * 20 + "(2022-2024)")
    print("="*70)

    start_time = datetime.now()
    print(f"\nStart time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # 1. Download FIRMS hotspots
    print("\n" + "-"*70)
    print("STEP 1/4: NASA FIRMS Hotspots")
    print("-"*70)
    results['firms'] = run_script(
        'download_firms.py',
        'NASA FIRMS Hotspot Download'
    )

    # 2. Download MODIS MCD64A1
    print("\n" + "-"*70)
    print("STEP 2/4: MODIS MCD64A1 Burned Area")
    print("-"*70)
    print("NOTE: This exports to Google Drive for download")
    print("-"*70)
    results['mcd64a1'] = run_script(
        'download_mcd64a1.py',
        'MODIS MCD64A1 Download (GEE Export)'
    )

    # 3. Download Sentinel-2
    print("\n" + "-"*70)
    print("STEP 3/4: Sentinel-2 Optical Imagery")
    print("-"*70)
    print("NOTE: This exports to Google Drive for download")
    print("-"*70)
    results['sentinel2'] = run_script(
        'download_sentinel2.py',
        'Sentinel-2 Download (GEE Export)'
    )

    # 4. Download ERA5
    print("\n" + "-"*70)
    print("STEP 4/4: Copernicus ERA5 Meteorology")
    print("-"*70)
    results['era5'] = run_script(
        'download_era5.py',
        'ERA5 Meteorology Download'
    )

    # Summary
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)

    for dataset, success in results.items():
        status = "COMPLETED" if success else "⚠️ WITH ISSUES"
        print(f"{dataset.upper():15} {status}")

    print(f"\nTotal time: {duration}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)

    if results['firms']:
        print("FIRMS: Data downloaded locally")
        print("   → Ready for processing")

    if results['mcd64a1'] or results['sentinel2']:
        print("\nGEE EXPORTS: Tasks submitted to Google Drive")
        print("   1. Wait 5-30 minutes for processing")
        print("   2. Check Google Drive: https://drive.google.com")
        print("   3. Download files from 'fireml_data/' folder")
        print("   4. Place GeoTIFF files in: data/raw/mcd64a1/ and data/raw/sentinel2/")

    if results['era5']:
        print("\nERA5: Data downloaded locally")
        print("   → Ready for processing")

    print("\n" + "="*70)
    print("PROCESSING NEXT")
    print("="*70)
    print("After all downloads complete, run preprocessing scripts:")
    print("  python src/preprocessing/process_firms.py")
    print("  python src/preprocessing/process_mcd64a1.py")
    print("  python src/preprocessing/process_sentinel2.py")
    print("  python src/preprocessing/process_era5.py")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
