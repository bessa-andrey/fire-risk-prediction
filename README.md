# Fire Risk Prediction - MATOPIBA

Machine Learning pipeline for wildfire detection and spurious hotspot filtering in the MATOPIBA region (Brazil).

## Overview

This project implements a complete pipeline to:
1. **Ingest** satellite data (FIRMS, ERA5, Sentinel-2, MCD64A1)
2. **Process** and create weak labels using burned area products
3. **Train** multiple ML models to classify hotspots as reliable or spurious
4. **Predict** in real-time on new FIRMS detections

### Study Area
MATOPIBA is a Brazilian agricultural frontier spanning 4 states (Maranhão, Tocantins, Piauí, Bahia) - a critical region for fire monitoring.

## Models

The pipeline trains and compares 9 classifiers (5 baselines + 2 default + 2 optimized):

| Model | Type | Description |
|-------|------|-------------|
| DummyClassifier | Baseline | Majority class (reference) |
| Logistic Regression | Baseline | Linear classifier |
| SVM-RBF | Baseline | Support Vector Machine with RBF kernel |
| Decision Tree | Baseline | Single tree |
| Random Forest | Baseline | Ensemble of trees |
| LightGBM | Gradient Boosting | GPU-accelerated (default params) |
| XGBoost | Gradient Boosting | GPU-accelerated (default params) |
| LightGBM (Optuna) | Gradient Boosting | Hyperparameters optimized via Optuna (100 trials, TPE) |
| XGBoost (Optuna) | Gradient Boosting | Hyperparameters optimized via Optuna (100 trials, TPE) |

## Features

The model uses 11 engineered features:

- **FIRMS**: brightness, confidence, FRP
- **Spatial**: hotspot_count, persistence_score
- **Meteorological**: temperature, dewpoint, wind_speed, precipitation, relative humidity
- **Derived**: drying_index

## Installation

```bash
# Clone repository
git clone https://github.com/bessa-andrey/fire-risk-prediction.git
cd fire-risk-prediction

# Create environment
conda create -n fire-risk python=3.10
conda activate fire-risk

# Install dependencies
pip install -r requirements.txt
```

### API Credentials Required

- **NASA EarthData**: For FIRMS and MCD64A1 data
- **Google Earth Engine**: For Sentinel-2 NDVI
- **Copernicus CDS**: For ERA5 meteorological data

See [docs/setup/CREDENCIAIS_SETUP.md](docs/setup/CREDENCIAIS_SETUP.md) for setup instructions.

## Usage

### Full Pipeline

```bash
# 1. Download data (FIRMS 2019-2024, ERA5, Sentinel-2, MCD64A1)
python src/data_ingest/run_all_downloads.py

# 2. Process data
python src/preprocessing/run_all_preprocessing.py

# 3. Feature engineering + weak labeling
python src/preprocessing/run_etapa3.py

# 4. Train models (all 9 classifiers + Optuna optimization)
python src/models/train_module_a.py

# 5. Evaluate (spatial + temporal validation)
python src/models/evaluate_module_a.py

# 6. Statistical analysis (bootstrap CI, McNemar, Wilcoxon)
python src/models/statistical_analysis.py

# 7. Weak label validation (select 200 samples for manual review)
python src/preprocessing/validate_weak_labels.py
```

### Inference Only

```bash
python src/models/predict_module_a.py --input hotspots.csv --output predictions.csv
```

## Project Structure

```
src/
├── data_ingest/        # Download scripts (FIRMS, ERA5, Sentinel-2, MCD64A1)
├── preprocessing/      # Data processing, feature engineering, weak labeling
│   └── validate_weak_labels.py  # Manual validation (200 samples, Cohen's Kappa)
├── models/             # Training, evaluation, and inference
│   ├── train_module_a.py        # 9 classifiers + Optuna optimization
│   ├── evaluate_module_a.py     # Spatial + temporal validation
│   ├── statistical_analysis.py  # Bootstrap CI, McNemar, Wilcoxon tests
│   └── predict_module_a.py      # Real-time inference
└── visualization/      # Mapping and plotting

docs/
├── setup/              # Environment and credentials setup
├── etapas/             # Pipeline stage documentation
├── modulos/            # Module documentation
└── visual/             # Visualizations and notebooks

data/                   # (not in git)
├── raw/                # Downloaded data
├── processed/          # Processed features
└── models/             # Trained models (.pkl)
```

## Statistical Rigor

All model comparisons include:
- **Bootstrap confidence intervals** (1000 resamples, 95% CI)
- **McNemar's test** for pairwise classifier comparison
- **Wilcoxon signed-rank test** on 5-fold CV scores
- **Cohen's Kappa** for weak label quality validation

## Documentation

- [Setup Guide](docs/setup/SETUP_COMPLETO.md)
- [Data Ingestion](docs/etapas/ETAPA1_INGESTAO.md)
- [Feature Engineering](docs/etapas/ETAPA3_FEATURE_ENGINEERING.md)
- [Model Training](docs/etapas/ETAPA4_VALIDACAO.md)
- [Inference Guide](docs/modulos/MODULO_A_INFERENCIA.md)

## Data Sources

| Source | Product | Resolution | Use |
|--------|---------|------------|-----|
| NASA FIRMS | VIIRS/MODIS | 375m/1km | Hotspot detections |
| NASA LP DAAC | MCD64A1 | 500m | Burned area (labels) |
| ESA | Sentinel-2 | 10m | NDVI vegetation index |
| ECMWF | ERA5 | 0.25° | Meteorological variables |

## License

This project is part of a Master's thesis in Electrical Engineering at UFAM (Federal University of Amazonas).

## Author

Andrey Bessa - andrey.bessa@ufam.edu.br
