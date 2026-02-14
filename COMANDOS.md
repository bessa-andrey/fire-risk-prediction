# Comandos para Executar o Sistema

## Ambiente

```bash
conda activate fireml
```

---

## Pipeline Completo (Etapas 1-4)

```bash
# Etapa 1: Download de dados (FIRMS, MCD64A1, Sentinel-2, ERA5)
python src/data_ingest/run_all_downloads.py

# Etapa 2: Processamento (limpeza, reprojecao, mosaico, NDVI, interpolacao)
python src/preprocessing/run_all_preprocessing.py

# Etapa 3: Weak Labeling + Feature Engineering
python src/preprocessing/run_etapa3.py

# Etapa 4: Treinamento + Validacao + Analise Estatistica
python src/models/run_etapa4.py
```

---

## Scripts Individuais

### Download (Etapa 1)
```bash
python src/data_ingest/download_firms.py
python src/data_ingest/download_mcd64a1.py
python src/data_ingest/download_sentinel2.py
python src/data_ingest/download_era5.py
```

### Processamento (Etapa 2)
```bash
python src/preprocessing/process_firms.py
python src/preprocessing/process_mcd64a1.py
python src/preprocessing/process_sentinel2.py
python src/preprocessing/process_era5.py
```

### Feature Engineering (Etapa 3)
```bash
python src/preprocessing/weak_labeling.py
python src/preprocessing/feature_engineering.py
python src/preprocessing/validate_weak_labels.py
```

### Modelagem (Etapa 4)
```bash
python src/models/train_module_a.py
python src/models/evaluate_module_a.py
python src/models/statistical_analysis.py
```

---

## Inferencia (classificar novos focos)

```bash
python src/models/predict_module_a.py --input novos_focos.csv
```

---

## Teste em Tempo Real (mapa interativo)

```bash
# Modo demo (dados historicos - sempre funciona)
python src/models/test_realtime.py --demo
python src/models/test_realtime.py --lat -10.5 --lon -46.5 --demo

# Tempo real (busca FIRMS API - precisa de hotspots ativos)
python src/models/test_realtime.py --lat -10.5 --lon -46.5
python src/models/test_realtime.py --lat -12.0 --lon -43.5 --radius 100

# Coordenadas uteis na MATOPIBA:
#   Tocantins: --lat -10.5 --lon -48.3
#   Bahia:     --lat -12.0 --lon -43.5
#   Maranhao:  --lat -5.0  --lon -44.0
#   Piaui:     --lat -8.0  --lon -43.0
```

---

## Visualizacao (mapas estaticos)

```bash
python src/visualization/generate_matopiba_map_v2.py
python src/visualization/map_hotspots.py
```

---

## Pipeline Completo do Modulo A (alternativo)

```bash
python src/models/run_module_a_pipeline.py
```
