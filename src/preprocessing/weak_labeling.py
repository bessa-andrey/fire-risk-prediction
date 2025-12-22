# weak_labeling.py
"""
Weak Labeling: Compare FIRMS hotspots against MCD64A1 burned area
Generate labels for Module A (spurious detection classification)

Input: firms_processed.csv + mcd64a1_burned_area.nc
Output: hotspots_labeled.csv + hotspots_labeled.gpkg
"""

import pandas as pd
import xarray as xr
import numpy as np
import geopandas as gpd
from pathlib import Path
from datetime import datetime, timedelta
import json
from tqdm import tqdm

# Configuration
PROCESSED_DIR = Path('data/processed')
INPUT_FIRMS = PROCESSED_DIR / 'firms' / 'firms_processed.csv'
INPUT_MCD64A1 = PROCESSED_DIR / 'burned_area' / 'mcd64a1_burned_area.nc'
OUTPUT_DIR = PROCESSED_DIR / 'module_a'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# MATOPIBA bounds
MATOPIBA_BOUNDS = {
    'north': 0,
    'south': -15,
    'east': -40,
    'west': -65
}

class WeakLabeler:
    """Generate weak labels for Module A (spurious detection)"""

    def __init__(self, firms_df, mcd64a1_data):
        self.firms = firms_df.copy()
        self.mcd64a1 = mcd64a1_data
        self.labels = []

    def get_mcd64a1_value_at_point(self, lat: float, lon: float, date: pd.Timestamp) -> int:
        """
        Get MCD64A1 BurnDate value at specific location and nearest date
        Returns: 0 (not burned), 1-365 (day of year burned), NaN (no data)
        """
        try:
            # Find nearest time in MCD64A1 data
            # Look within 30 days of detection date
            date_range = self.mcd64a1.sel(
                latitude=lat,
                longitude=lon,
                time=slice(date - timedelta(days=15), date + timedelta(days=15)),
                method='nearest'
            )

            if date_range is None or date_range.sizes['time'] == 0:
                return np.nan

            # Get first (nearest) time step
            burn_value = float(date_range.isel(time=0).values)
            return burn_value

        except Exception as e:
            return np.nan

    def label_hotspot(self, row: pd.Series) -> dict:
        """
        Assign weak label to single hotspot based on MCD64A1 ground truth
        """
        lat = row['latitude']
        lon = row['longitude']
        detection_date = pd.to_datetime(row['acq_datetime'])

        # Get MCD64A1 value at location/time
        mcd64a1_value = self.get_mcd64a1_value_at_point(lat, lon, detection_date)

        # Label rules
        label = {
            'firms_id': row.name if hasattr(row, 'name') else None,
            'latitude': lat,
            'longitude': lon,
            'acq_datetime': detection_date,
            'mcd64a1_value': mcd64a1_value,
            'confidence': row.get('confidence', np.nan),
            'persistence_score': row.get('persistence_score', np.nan),
        }

        # Weak labeling rules
        if pd.isna(mcd64a1_value):
            # No MCD64A1 data: uncertain (use confidence as proxy)
            label['label'] = 'uncertain'
            label['label_confidence'] = row.get('confidence', 50) / 100.0
        elif mcd64a1_value > 0:
            # Burned: TRUE POSITIVE (fire actually occurred)
            label['label'] = 'true_positive'
            label['label_confidence'] = 0.95
        else:
            # Not burned: FALSE POSITIVE (no fire despite hotspot)
            label['label'] = 'false_positive'
            label['label_confidence'] = 0.95

        return label

    def label_all(self) -> pd.DataFrame:
        """Label all hotspots"""
        print("[INFO] Assigning weak labels to hotspots...")

        labels_list = []
        for idx, row in tqdm(self.firms.iterrows(), total=len(self.firms), desc="Labeling"):
            label_dict = self.label_hotspot(row)
            labels_list.append(label_dict)

        labels_df = pd.DataFrame(labels_list)

        # Convert label to numeric
        label_mapping = {
            'false_positive': 0,
            'true_positive': 1,
            'uncertain': -1
        }
        labels_df['label_numeric'] = labels_df['label'].map(label_mapping)

        return labels_df

    def summary_statistics(self, labels_df: pd.DataFrame) -> dict:
        """Generate summary statistics"""
        total = len(labels_df)
        false_pos = (labels_df['label'] == 'false_positive').sum()
        true_pos = (labels_df['label'] == 'true_positive').sum()
        uncertain = (labels_df['label'] == 'uncertain').sum()

        stats = {
            'total_hotspots': total,
            'false_positives': int(false_pos),
            'true_positives': int(true_pos),
            'uncertain': int(uncertain),
            'fp_percentage': float(false_pos / total * 100),
            'tp_percentage': float(true_pos / total * 100),
            'uncertain_percentage': float(uncertain / total * 100),
            'mean_confidence_fp': float(labels_df[labels_df['label'] == 'false_positive']['confidence'].mean()),
            'mean_confidence_tp': float(labels_df[labels_df['label'] == 'true_positive']['confidence'].mean()),
            'mean_persistence_fp': float(labels_df[labels_df['label'] == 'false_positive']['persistence_score'].mean()),
            'mean_persistence_tp': float(labels_df[labels_df['label'] == 'true_positive']['persistence_score'].mean()),
        }

        return stats

def main():
    """Main weak labeling pipeline"""
    print("\n" + "="*60)
    print("WEAK LABELING - MODULE A - ETAPA 3")
    print("="*60)

    # Step 1: Load data
    print("[INFO] Loading processed data...")

    if not INPUT_FIRMS.exists():
        print(f"[ERROR] FIRMS file not found: {INPUT_FIRMS}")
        print("[INFO] Run Etapa 2 first: python src/preprocessing/process_firms.py")
        return

    if not INPUT_MCD64A1.exists():
        print(f"[ERROR] MCD64A1 file not found: {INPUT_MCD64A1}")
        print("[INFO] Run Etapa 2 first: python src/preprocessing/process_mcd64a1.py")
        return

    firms_df = pd.read_csv(INPUT_FIRMS)
    print(f"[OK] Loaded {len(firms_df)} FIRMS hotspots")

    mcd64a1_data = xr.open_dataset(INPUT_MCD64A1)
    print(f"[OK] Loaded MCD64A1 data: {mcd64a1_data.dims}")

    # Step 2: Create weak labels
    labeler = WeakLabeler(firms_df, mcd64a1_data)
    labels_df = labeler.label_all()

    # Step 3: Generate statistics
    stats = labeler.summary_statistics(labels_df)

    # Step 4: Save outputs
    print("\n[INFO] Saving outputs...")

    # CSV output
    csv_path = OUTPUT_DIR / 'hotspots_labeled.csv'
    labels_df.to_csv(csv_path, index=False)
    print(f"[OK] Labeled hotspots saved to: {csv_path}")

    # GeoPackage output (requires geopandas)
    try:
        gdf = gpd.GeoDataFrame(
            labels_df.drop(columns=['latitude', 'longitude']),
            geometry=gpd.points_from_xy(labels_df['longitude'], labels_df['latitude']),
            crs='EPSG:4326'
        )

        gpkg_path = OUTPUT_DIR / 'hotspots_labeled.gpkg'
        gdf.to_file(gpkg_path, driver='GPKG')
        print(f"[OK] GeoPackage saved to: {gpkg_path}")
    except Exception as e:
        print(f"[WARNING] Could not save GeoPackage: {e}")

    # Statistics JSON
    stats['processing_date'] = datetime.now().isoformat()
    stats_path = OUTPUT_DIR / 'weak_labeling_stats.json'
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"[OK] Statistics saved to: {stats_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("LABELING SUMMARY")
    print(f"{'='*60}")
    print(f"Total hotspots: {stats['total_hotspots']}")
    print(f"True positives: {stats['true_positives']} ({stats['tp_percentage']:.1f}%)")
    print(f"False positives: {stats['false_positives']} ({stats['fp_percentage']:.1f}%)")
    print(f"Uncertain: {stats['uncertain']} ({stats['uncertain_percentage']:.1f}%)")
    print(f"\nConfidence analysis:")
    print(f"  True positives (mean): {stats['mean_confidence_tp']:.1f}%")
    print(f"  False positives (mean): {stats['mean_confidence_fp']:.1f}%")
    print(f"\nPersistence analysis:")
    print(f"  True positives (mean): {stats['mean_persistence_tp']:.2f}")
    print(f"  False positives (mean): {stats['mean_persistence_fp']:.2f}")

    return labels_df

if __name__ == '__main__':
    labels = main()
    print("\n[INFO] Next step: Extract features for Module A")
    print("[INFO] Run: python src/preprocessing/feature_engineering.py")
