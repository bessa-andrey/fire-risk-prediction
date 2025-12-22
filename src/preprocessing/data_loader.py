# data_loader.py
"""
Unified data loader for preprocessed datasets
Provides convenient interface for loading processed data from Etapa 2
"""

import pandas as pd
import xarray as xr
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Tuple

class DataLoader:
    """Unified data loader for fire ML project"""

    def __init__(self):
        self.data_dir = Path('data/processed')
        self.raw_dir = Path('data/raw')

        self.firms_data = None
        self.mcd64a1_data = None
        self.sentinel2_data = {}
        self.era5_data = None

    def load_firms(self) -> Optional[pd.DataFrame]:
        """Load processed FIRMS hotspots"""
        firms_file = self.data_dir / 'firms' / 'firms_processed.csv'

        if not firms_file.exists():
            print(f"[WARNING] FIRMS file not found: {firms_file}")
            return None

        try:
            self.firms_data = pd.read_csv(firms_file)
            print(f"[OK] Loaded FIRMS data: {len(self.firms_data)} records")
            return self.firms_data
        except Exception as e:
            print(f"[ERROR] Failed to load FIRMS: {e}")
            return None

    def load_mcd64a1(self) -> Optional[xr.Dataset]:
        """Load processed MCD64A1 burned area data"""
        mcd64a1_file = self.data_dir / 'burned_area' / 'mcd64a1_burned_area.nc'

        if not mcd64a1_file.exists():
            print(f"[WARNING] MCD64A1 file not found: {mcd64a1_file}")
            return None

        try:
            self.mcd64a1_data = xr.open_dataset(mcd64a1_file)
            print(f"[OK] Loaded MCD64A1 data: shape {self.mcd64a1_data.dims}")
            return self.mcd64a1_data
        except Exception as e:
            print(f"[ERROR] Failed to load MCD64A1: {e}")
            return None

    def load_sentinel2(self, season: str = 'dry') -> Optional[xr.Dataset]:
        """Load processed Sentinel-2 data"""
        sentinel2_file = self.data_dir / 'sentinel2' / f'sentinel2_{season}_composite.nc'

        if not sentinel2_file.exists():
            print(f"[WARNING] Sentinel-2 file not found: {sentinel2_file}")
            return None

        try:
            sentinel2_data = xr.open_dataset(sentinel2_file)
            self.sentinel2_data[season] = sentinel2_data
            print(f"[OK] Loaded Sentinel-2 {season} data: shape {sentinel2_data.dims}")
            return sentinel2_data
        except Exception as e:
            print(f"[ERROR] Failed to load Sentinel-2: {e}")
            return None

    def load_era5(self) -> Optional[xr.Dataset]:
        """Load processed ERA5 meteorological data"""
        era5_file = self.data_dir / 'era5' / 'era5_daily_aggregates.nc'

        if not era5_file.exists():
            print(f"[WARNING] ERA5 file not found: {era5_file}")
            return None

        try:
            self.era5_data = xr.open_dataset(era5_file)
            print(f"[OK] Loaded ERA5 data: shape {self.era5_data.dims}")
            return self.era5_data
        except Exception as e:
            print(f"[ERROR] Failed to load ERA5: {e}")
            return None

    def load_all(self) -> Dict:
        """Load all available datasets"""
        print("[INFO] Loading all processed datasets...")
        print("="*60)

        datasets = {
            'firms': self.load_firms(),
            'mcd64a1': self.load_mcd64a1(),
            'sentinel2_dry': self.load_sentinel2('dry'),
            'sentinel2_wet': self.load_sentinel2('wet'),
            'era5': self.load_era5()
        }

        print("="*60)
        loaded_count = sum(1 for v in datasets.values() if v is not None)
        print(f"[OK] Successfully loaded {loaded_count}/{len(datasets)} datasets")

        return datasets

    def get_firms(self) -> Optional[pd.DataFrame]:
        """Get FIRMS data (lazy load)"""
        if self.firms_data is None:
            self.load_firms()
        return self.firms_data

    def get_mcd64a1(self) -> Optional[xr.Dataset]:
        """Get MCD64A1 data (lazy load)"""
        if self.mcd64a1_data is None:
            self.load_mcd64a1()
        return self.mcd64a1_data

    def get_sentinel2(self, season: str = 'dry') -> Optional[xr.Dataset]:
        """Get Sentinel-2 data (lazy load)"""
        if season not in self.sentinel2_data:
            self.load_sentinel2(season)
        return self.sentinel2_data.get(season)

    def get_era5(self) -> Optional[xr.Dataset]:
        """Get ERA5 data (lazy load)"""
        if self.era5_data is None:
            self.load_era5()
        return self.era5_data

    def summary(self) -> Dict:
        """Print data summary"""
        summary = {}

        if self.firms_data is not None:
            summary['FIRMS'] = {
                'type': 'DataFrame',
                'shape': self.firms_data.shape,
                'columns': list(self.firms_data.columns)
            }

        if self.mcd64a1_data is not None:
            summary['MCD64A1'] = {
                'type': 'xarray.Dataset',
                'dimensions': dict(self.mcd64a1_data.dims),
                'variables': list(self.mcd64a1_data.data_vars)
            }

        for season, data in self.sentinel2_data.items():
            summary[f'Sentinel-2 ({season})'] = {
                'type': 'xarray.Dataset',
                'dimensions': dict(data.dims),
                'variables': list(data.data_vars)
            }

        if self.era5_data is not None:
            summary['ERA5'] = {
                'type': 'xarray.Dataset',
                'dimensions': dict(self.era5_data.dims),
                'variables': list(self.era5_data.data_vars)
            }

        return summary

    def print_summary(self):
        """Print formatted data summary"""
        summary = self.summary()

        print("\n" + "="*60)
        print("DATA SUMMARY")
        print("="*60)

        for dataset_name, info in summary.items():
            print(f"\n{dataset_name}:")
            print(f"  Type: {info['type']}")
            if 'shape' in info:
                print(f"  Shape: {info['shape']}")
            if 'dimensions' in info:
                print(f"  Dimensions: {info['dimensions']}")
            if 'variables' in info:
                print(f"  Variables: {len(info['variables'])} variables")


class FeatureExtractor:
    """Extract features from processed datasets for ML models"""

    def __init__(self, loader: DataLoader):
        self.loader = loader

    def extract_hotspot_features(self, hotspot_row: pd.Series) -> Dict:
        """
        Extract features for a single hotspot (Module A)
        Returns dictionary of features for classification
        """
        features = {}

        # Basic hotspot properties
        features['latitude'] = hotspot_row['latitude']
        features['longitude'] = hotspot_row['longitude']
        features['confidence'] = hotspot_row['confidence']
        features['brightness'] = hotspot_row.get('brightness', np.nan)
        features['persistence_score'] = hotspot_row.get('persistence_score', 0)

        # Add spatial/temporal context if available
        if 'acq_datetime' in hotspot_row:
            features['dayofyear'] = pd.to_datetime(hotspot_row['acq_datetime']).dayofyear

        return features

    def extract_grid_features(self, lat: float, lon: float, date: pd.Timestamp) -> Dict:
        """
        Extract features for a grid cell (Module B)
        Returns dictionary of features for propagation prediction
        """
        features = {}

        # Spatial location
        features['latitude'] = lat
        features['longitude'] = lon

        # Temporal features
        features['month'] = date.month
        features['dayofyear'] = date.dayofyear
        features['is_dry_season'] = date.month in [7, 8, 9, 10]

        # Extract from ERA5 if available
        era5 = self.loader.get_era5()
        if era5 is not None:
            try:
                # Get nearest grid cell and time
                era5_point = era5.sel(
                    latitude=lat,
                    longitude=lon,
                    time=date,
                    method='nearest'
                )

                # Temperature (K to C)
                if '2m_temperature' in era5_point.data_vars:
                    temp_k = float(era5_point['2m_temperature'].values)
                    features['temperature_c'] = temp_k - 273.15

                # Relative humidity
                if 'relative_humidity' in era5_point.data_vars:
                    features['relative_humidity'] = float(era5_point['relative_humidity'].values)

                # Wind magnitude
                if 'wind_magnitude' in era5_point.data_vars:
                    features['wind_magnitude'] = float(era5_point['wind_magnitude'].values)

                # Precipitation
                if 'total_precipitation' in era5_point.data_vars:
                    features['precipitation_mm'] = float(era5_point['total_precipitation'].values)

            except Exception as e:
                pass  # Silently skip if extraction fails

        return features

    def create_module_a_dataset(self) -> Optional[pd.DataFrame]:
        """
        Create feature matrix for Module A (Spurious Detection Classification)
        """
        firms = self.loader.get_firms()
        if firms is None:
            print("[ERROR] FIRMS data not loaded")
            return None

        print(f"[INFO] Extracting features for {len(firms)} hotspots...")

        features_list = []
        for idx, row in firms.iterrows():
            features = self.extract_hotspot_features(row)
            features_list.append(features)

        features_df = pd.DataFrame(features_list)
        print(f"[OK] Extracted {len(features_df)} feature vectors")

        return features_df

    def create_module_b_dataset(self, grid_size_degrees: float = 0.25) -> Optional[pd.DataFrame]:
        """
        Create feature matrix for Module B (Fire Propagation Prediction D+1)
        """
        era5 = self.loader.get_era5()
        if era5 is None:
            print("[ERROR] ERA5 data not loaded")
            return None

        print(f"[INFO] Creating grid features with {grid_size_degrees} degree resolution...")

        # Create regular grid over MATOPIBA
        lats = np.arange(0, -15 - grid_size_degrees, -grid_size_degrees)
        lons = np.arange(-65, -40 + grid_size_degrees, grid_size_degrees)

        features_list = []

        # For each grid cell and each day in era5 data
        dates = era5.time.values

        for date in dates[:len(dates)//2]:  # Limit to subset for testing
            date_pd = pd.Timestamp(date)

            for lat in lats[::2]:  # Subsample grid
                for lon in lons[::2]:
                    features = self.extract_grid_features(lat, lon, date_pd)
                    features_list.append(features)

        features_df = pd.DataFrame(features_list)
        print(f"[OK] Created {len(features_df)} grid feature vectors")

        return features_df


if __name__ == '__main__':
    # Example usage
    loader = DataLoader()
    loader.load_all()
    loader.print_summary()

    # Extract features
    extractor = FeatureExtractor(loader)
    module_a_features = extractor.create_module_a_dataset()
    if module_a_features is not None:
        print(f"\nModule A features shape: {module_a_features.shape}")
