# feature_engineering.py
"""
Feature Engineering: Extract ML-ready features from processed datasets
Generates feature matrices for Module A and Module B

Input:
  - hotspots_labeled.csv (from weak_labeling.py)
  - Processed datasets (ERA5, Sentinel-2, MCD64A1)

Output:
  - module_a_features.csv (classification features)
  - module_b_features.csv (propagation features)
"""

import pandas as pd
import numpy as np
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta
import json
from tqdm import tqdm

# Configuration
PROCESSED_DIR = Path('data/processed')
INPUT_LABELS = PROCESSED_DIR / 'module_a' / 'hotspots_labeled.csv'
INPUT_ERA5 = PROCESSED_DIR / 'era5' / 'era5_daily_aggregates.nc'
INPUT_SENTINEL2_DRY = PROCESSED_DIR / 'sentinel2' / 'sentinel2_dry_composite.nc'
INPUT_MCD64A1 = PROCESSED_DIR / 'burned_area' / 'mcd64a1_burned_area.nc'
OUTPUT_DIR = PROCESSED_DIR / 'module_a'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class FeatureEngineer:
    """Extract features for Module A and B"""

    def __init__(self):
        self.era5 = None
        self.sentinel2 = None
        self.mcd64a1 = None

    def load_data(self):
        """Load all required datasets"""
        print("[INFO] Loading processed datasets...")

        if INPUT_ERA5.exists():
            self.era5 = xr.open_dataset(INPUT_ERA5)
            print(f"[OK] Loaded ERA5")
        else:
            print(f"[WARNING] ERA5 not found: {INPUT_ERA5}")

        if INPUT_SENTINEL2_DRY.exists():
            self.sentinel2 = xr.open_dataset(INPUT_SENTINEL2_DRY)
            print(f"[OK] Loaded Sentinel-2")
        else:
            print(f"[WARNING] Sentinel-2 not found: {INPUT_SENTINEL2_DRY}")

        if INPUT_MCD64A1.exists():
            self.mcd64a1 = xr.open_dataset(INPUT_MCD64A1)
            print(f"[OK] Loaded MCD64A1")
        else:
            print(f"[WARNING] MCD64A1 not found: {INPUT_MCD64A1}")

    def extract_era5_features(self, lat: float, lon: float, date: pd.Timestamp) -> dict:
        """Extract ERA5 features for a location and date"""
        features = {}

        if self.era5 is None:
            return features

        try:
            # Select nearest grid cell and time
            point_data = self.era5.sel(
                latitude=lat,
                longitude=lon,
                time=date,
                method='nearest'
            )

            # Temperature (K to C)
            if '2m_temperature' in point_data.data_vars:
                temp_k = float(point_data['2m_temperature'].values)
                features['temperature_c'] = temp_k - 273.15
                features['temperature_k'] = temp_k

            # Relative humidity
            if 'relative_humidity' in point_data.data_vars:
                features['relative_humidity'] = float(point_data['relative_humidity'].values)

            # Drying index
            if 'drying_index' in point_data.data_vars:
                features['drying_index'] = float(point_data['drying_index'].values)

            # Wind magnitude
            if 'wind_magnitude' in point_data.data_vars:
                features['wind_magnitude'] = float(point_data['wind_magnitude'].values)

            # Wind direction
            if 'wind_direction' in point_data.data_vars:
                features['wind_direction'] = float(point_data['wind_direction'].values)

            # Precipitation
            if 'total_precipitation' in point_data.data_vars:
                features['precipitation_mm'] = float(point_data['total_precipitation'].values)

            # Soil moisture
            if 'soil_moisture_0_7cm' in point_data.data_vars:
                features['soil_moisture'] = float(point_data['soil_moisture_0_7cm'].values)

        except Exception as e:
            pass  # Silently skip if extraction fails

        return features

    def extract_sentinel2_features(self, lat: float, lon: float) -> dict:
        """Extract Sentinel-2 features for a location"""
        features = {}

        if self.sentinel2 is None:
            return features

        try:
            # Select nearest grid cell (average across time if multiple)
            point_data = self.sentinel2.sel(
                latitude=lat,
                longitude=lon,
                method='nearest'
            )

            # NDVI if available
            if 'NDVI' in point_data.data_vars:
                ndvi_values = point_data['NDVI'].values
                if hasattr(ndvi_values, '__iter__'):
                    features['ndvi_mean'] = float(np.nanmean(ndvi_values))
                    features['ndvi_max'] = float(np.nanmax(ndvi_values))
                    features['ndvi_min'] = float(np.nanmin(ndvi_values))
                else:
                    features['ndvi_mean'] = float(ndvi_values)

            # Red band (B4)
            if 'B4' in point_data.data_vars:
                b4_values = point_data['B4'].values
                features['red_mean'] = float(np.nanmean(b4_values) if hasattr(b4_values, '__iter__') else b4_values)

            # NIR band (B8)
            if 'B8' in point_data.data_vars:
                b8_values = point_data['B8'].values
                features['nir_mean'] = float(np.nanmean(b8_values) if hasattr(b8_values, '__iter__') else b8_values)

        except Exception as e:
            pass  # Silently skip if extraction fails

        return features

    def extract_mcd64a1_features(self, lat: float, lon: float, date: pd.Timestamp) -> dict:
        """Extract MCD64A1 features (context around hotspot)"""
        features = {}

        if self.mcd64a1 is None:
            return features

        try:
            # Get 3x3 window around point
            lat_range = slice(lat - 0.03, lat + 0.03)  # ~3.3 km
            lon_range = slice(lon - 0.03, lon + 0.03)

            window = self.mcd64a1.sel(
                latitude=lat_range,
                longitude=lon_range,
                time=date,
                method='nearest'
            )

            if window is not None and window.sizes.get('latitude', 0) > 0:
                # Count burned pixels in window
                burn_data = window.values
                burned_pixels = (burn_data > 0).sum()
                total_pixels = burn_data.size
                features['burned_pixels_ratio'] = float(burned_pixels / max(total_pixels, 1))

        except Exception as e:
            pass

        return features

    def create_module_a_features(self, hotspots_df: pd.DataFrame) -> pd.DataFrame:
        """Create feature matrix for Module A (classification)"""
        print("[INFO] Extracting Module A features...")

        feature_list = []

        for idx, row in tqdm(hotspots_df.iterrows(), total=len(hotspots_df), desc="Module A"):
            lat = row['latitude']
            lon = row['longitude']
            date = pd.to_datetime(row['acq_datetime'])

            features = {
                'hotspot_id': idx,
                'latitude': lat,
                'longitude': lon,
                'acq_datetime': date,
            }

            # Add label if available
            if 'label_numeric' in row.index:
                features['label'] = row['label_numeric']
            if 'label' in row.index:
                features['label_text'] = row['label']

            # Hotspot properties
            if 'confidence' in row.index:
                features['confidence'] = row['confidence']
            if 'persistence_score' in row.index:
                features['persistence_score'] = row['persistence_score']

            # Temporal features
            features['month'] = date.month
            features['dayofyear'] = date.dayofyear
            features['is_dry_season'] = date.month in [7, 8, 9, 10]

            # ERA5 features
            era5_feats = self.extract_era5_features(lat, lon, date)
            features.update(era5_feats)

            # Sentinel-2 features
            sent2_feats = self.extract_sentinel2_features(lat, lon)
            features.update(sent2_feats)

            # MCD64A1 context features
            mcd_feats = self.extract_mcd64a1_features(lat, lon, date)
            features.update(mcd_feats)

            feature_list.append(features)

        features_df = pd.DataFrame(feature_list)
        print(f"[OK] Extracted {len(features_df)} feature vectors")
        print(f"[OK] Features shape: {features_df.shape}")

        return features_df

    def create_module_b_features(self, grid_spacing: float = 0.25) -> pd.DataFrame:
        """Create feature matrix for Module B (propagation prediction)"""
        print("[INFO] Extracting Module B features...")

        if self.era5 is None:
            print("[ERROR] ERA5 data required for Module B features")
            return None

        # Create regular grid
        lats = np.arange(0, -15 - grid_spacing, -grid_spacing)
        lons = np.arange(-65, -40 + grid_spacing, grid_spacing)

        feature_list = []

        # Sample grid points and dates (for testing, use subset)
        dates = self.era5.time.values[:100]  # First 100 time steps

        print(f"[INFO] Creating grid: {len(lats)} lat × {len(lons)} lon × {len(dates)} dates")

        for date in tqdm(dates, desc="Module B dates"):
            date_pd = pd.Timestamp(date)

            # Subsample grid for speed (every other point)
            for lat in lats[::2]:
                for lon in lons[::2]:
                    features = {
                        'latitude': lat,
                        'longitude': lon,
                        'date': date_pd,
                        'month': date_pd.month,
                        'dayofyear': date_pd.dayofyear,
                        'is_dry_season': date_pd.month in [7, 8, 9, 10]
                    }

                    # ERA5 features
                    era5_feats = self.extract_era5_features(lat, lon, date_pd)
                    features.update(era5_feats)

                    # Sentinel-2 features
                    sent2_feats = self.extract_sentinel2_features(lat, lon)
                    features.update(sent2_feats)

                    feature_list.append(features)

        features_df = pd.DataFrame(feature_list)
        print(f"[OK] Created {len(features_df)} grid feature vectors")

        return features_df

def main():
    """Main feature engineering pipeline"""
    print("\n" + "="*60)
    print("FEATURE ENGINEERING - ETAPA 3")
    print("="*60)

    # Step 1: Load weak labels
    if not INPUT_LABELS.exists():
        print(f"[ERROR] Labels file not found: {INPUT_LABELS}")
        print("[INFO] Run weak_labeling.py first")
        return

    hotspots_df = pd.read_csv(INPUT_LABELS)
    print(f"[OK] Loaded {len(hotspots_df)} labeled hotspots")

    # Step 2: Initialize feature engineer
    engineer = FeatureEngineer()
    engineer.load_data()

    # Step 3: Create Module A features
    module_a_features = engineer.create_module_a_features(hotspots_df)

    # Save Module A features
    csv_path_a = OUTPUT_DIR / 'module_a_features.csv'
    module_a_features.to_csv(csv_path_a, index=False)
    print(f"[OK] Module A features saved to: {csv_path_a}")

    # Step 4: Create Module B features
    module_b_features = engineer.create_module_b_features()

    if module_b_features is not None:
        output_dir_b = PROCESSED_DIR / 'module_b'
        output_dir_b.mkdir(parents=True, exist_ok=True)

        csv_path_b = output_dir_b / 'module_b_features.csv'
        module_b_features.to_csv(csv_path_b, index=False)
        print(f"[OK] Module B features saved to: {csv_path_b}")

    # Step 5: Generate summary
    summary = {
        'processing_date': datetime.now().isoformat(),
        'module_a': {
            'samples': len(module_a_features),
            'features': len(module_a_features.columns),
            'feature_names': list(module_a_features.columns)
        }
    }

    if module_b_features is not None:
        summary['module_b'] = {
            'samples': len(module_b_features),
            'features': len(module_b_features.columns),
            'feature_names': list(module_b_features.columns)
        }

    summary_path = OUTPUT_DIR / 'feature_engineering_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print("FEATURE ENGINEERING SUMMARY")
    print(f"{'='*60}")
    print(f"Module A samples: {len(module_a_features)}")
    print(f"Module A features: {len(module_a_features.columns)}")
    if module_b_features is not None:
        print(f"Module B samples: {len(module_b_features)}")
        print(f"Module B features: {len(module_b_features.columns)}")

    return module_a_features, module_b_features

if __name__ == '__main__':
    a_features, b_features = main()
    print("\n[INFO] Next step: Train Module A classifier")
    print("[INFO] Run: python src/models/train_module_a.py")
