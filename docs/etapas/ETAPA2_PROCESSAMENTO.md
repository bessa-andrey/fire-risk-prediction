# Fase 1 - Etapa 2: Processamento de Dados - Guia Prático

**Data de Início**: 11 de novembro de 2025
**Duração**: ~2-3 horas (tempo de execução dos scripts)
**Objetivo**: Processar dados brutos e preparar features para ML

---

## Objetivo Geral da Etapa 2

Transformar dados brutos (CSV, GeoTIFF, NetCDF) em:
1. **Dados limpos e normalizados** (validação de geometria, remoção de outliers)
2. **Agregações temporais** (hotspots agrupados por proximidade)
3. **Índices calculados** (NDVI, umidade relativa, índices de vento)
4. **Features estruturadas** (prontas para ML em Etapa 3)

**Saída de Etapa 2**:
```
data/processed/
├── firms/
│   ├── firms_processed.csv (hotspots limpos + persistência)
│   └── firms_stats.json
│
├── burned_area/
│   ├── mcd64a1_burned_area.nc (série temporal de queimadas)
│   └── mcd64a1_stats.json
│
├── sentinel2/
│   ├── sentinel2_dry_composite.nc (compostos NDVI/RGB)
│   └── sentinel2_stats.json
│
└── era5/
    ├── era5_daily_aggregates.nc (dados horários agregados para dia)
    └── era5_stats.json
```

---

## Pré-requisitos

### Verificar que Etapa 1 foi Completada

```bash
# Confirmar que os dados foram baixados
ls -la data/raw/firms_hotspots/
ls -la data/raw/mcd64a1/
ls -la data/raw/sentinel2/
ls -la data/raw/era5/
```

### Dependências Python

Já instaladas em sessão anterior:
- pandas, numpy, xarray, rasterio, rioxarray
- scikit-learn, lightgbm, xgboost

---

## 📋 Scripts de Processamento

Cada script processa um tipo de dado:

| Script | Input | Output | Tempo |
|--------|-------|--------|-------|
| `process_firms.py` | FIRMS CSV | firms_processed.csv | ~2 min |
| `process_mcd64a1.py` | MCD64A1 GeoTIFF (36 arquivos) | mcd64a1_burned_area.nc | ~5 min |
| `process_sentinel2.py` | Sentinel-2 GeoTIFF (6 arquivos) | sentinel2_*_composite.nc | ~5 min |
| `process_era5.py` | ERA5 NetCDF (12+ arquivos) | era5_daily_aggregates.nc | ~3 min |

**Tempo total**: ~15 minutos (processamento paralelo possível)

---

## 🚀 Como Executar

### Opção 1: Executar Todos os Scripts em Sequência

```bash
cd "c:\Users\bessa\Downloads\Projeto Mestrado"

# Criar diretório de saída
mkdir -p data/processed/firms data/processed/burned_area data/processed/sentinel2 data/processed/era5

# Executar em sequência
python src/preprocessing/process_firms.py
python src/preprocessing/process_mcd64a1.py
python src/preprocessing/process_sentinel2.py
python src/preprocessing/process_era5.py
```

### Opção 2: Executar Scripts Individuais

Se apenas um tipo de dado está pronto:

```bash
# Apenas FIRMS (mais rápido para testes)
python src/preprocessing/process_firms.py

# Apenas MCD64A1
python src/preprocessing/process_mcd64a1.py

# Etc.
```

### Opção 3: Usar Data Loader (Python)

Para carregar dados já processados:

```python
from src.preprocessing.data_loader import DataLoader, FeatureExtractor

# Carregar dados
loader = DataLoader()
datasets = loader.load_all()

# Acessar dados individuais
firms = loader.get_firms()
mcd64a1 = loader.get_mcd64a1()
era5 = loader.get_era5()
sentinel2_dry = loader.get_sentinel2('dry')

# Ver resumo
loader.print_summary()

# Extrair features para ML
extractor = FeatureExtractor(loader)
module_a_features = extractor.create_module_a_dataset()
module_b_features = extractor.create_module_b_dataset()
```

---

## 📊 O Que Cada Script Faz

### 1. process_firms.py

**Entrada**: `data/raw/firms_hotspots/firms_combined_2022-2024.csv` (raw hotspots)

**Processamento**:
```
1. Validação de Geometria
   └─ Remove hotspots fora de MATOPIBA (-15°S-0°N, -65°W--40°W)

2. Parse de Datas
   └─ Converte coluna 'acq_date' para datetime

3. Normalização de Confiança
   └─ Garante que confidence está em 0-100 (já está da NASA)

4. Filtragem por Confiança
   └─ Remove detecções com confidence < 30% (muito ruidosas)

5. Agregação Temporal
   └─ Agrupa hotspots em grade de 0.1° dentro de 3 dias
   └─ Cria 'hotspot_count': quantas detecções no mesmo local/data

6. Cálculo de Persistência
   └─ Para cada hotspot: conta detecções vizinhas em janela 7 dias
   └─ persistence_score = (contagem normalizada) 0-1
   └─ Hotspots persistentes = mais prováveis de serem reais
```

**Saída**:
```
firms_processed.csv:
- latitude, longitude (coordenadas)
- acq_datetime (data/hora da detecção)
- brightness (intensidade do brilho)
- confidence (% confiança 0-100)
- satellite (NOAA20, NOAA21, etc)
- frp (Fire Radiative Power - potência)
- hotspot_count (quantas detecções neste grid/data)
- persistence_count (quantas detecções vizinhas em 7 dias)
- persistence_score (0-1, normalizado)
- year, month (para análise temporal)

firms_stats.json:
- input_records: 708
- output_records: X (após filtragem)
- confidence_stats (média, min, max)
- temporal_range (2022-2024)
```

---

### 2. process_mcd64a1.py

**Entrada**: `data/raw/mcd64a1/MCD64A1_*.tif` (36 arquivos mensais 2022-2024)

**Processamento**:
```
1. Carregamento de Arquivos GeoTIFF
   └─ Lê band 'BurnDate' (dia do ano 1-365 quando queimou, 0=não queimou)
   └─ Extrai metadata (ano, mês) do nome do arquivo

2. Crop para MATOPIBA
   └─ Reduz resolução: 500m x 500m global → apenas MATOPIBA

3. Cálculo de Máscara de Queimada
   └─ burned_mask: 1 onde BurnDate > 0, 0 senão

4. Merge de Camadas Mensais
   └─ Empilha 36 meses em dimensão temporal
   └─ Resultado: (12 meses, altura, largura) em xarray

5. Cálculo de Estatísticas
   └─ Total de pixels queimados em 3 anos
   └─ Área queimada em km² (0.25 km² por pixel 500m)
   └─ Breakdown mensal
```

**Saída**:
```
mcd64a1_burned_area.nc: (xarray Dataset)
- Dimensões: (time: 36, latitude: 600, longitude: 600)
- Banda: BurnDate (dia do ano)
- Atributos: CRS geográfico (EPSG:4326), bounds

mcd64a1_stats.json:
- total_burned_area_km2: X
- total_burned_pixels: X
- temporal_coverage: 2022-01-01 to 2024-12-31
- monthly_breakdown: [
    {year_month: "2022-07", burned_area_km2: Y},
    ...
  ]
```

**Uso em Módulos**:
- **Module A**: Comparar FIRMS hotspots vs MCD64A1 → Verdadeiro positivo?
- **Module B**: Entrada para y_train (onde queimou amanhã?)

---

### 3. process_sentinel2.py

**Entrada**: `data/raw/sentinel2/Sentinel2_*.tif` (6 compostos: 3 anos × dry/wet)

**Processamento**:
```
1. Carregamento de Bandas Espectrais
   └─ B4 (Red): 665nm - vegetação saudável
   └─ B3 (Green): 560nm - verdor
   └─ B2 (Blue): 490nm - absorção de água
   └─ B8 (NIR): 842nm - infravermelho próximo

2. Crop para MATOPIBA
   └─ Reduz de resolução global para 10m x 10m em MATOPIBA

3. Merge por Estação
   └─ Dry season: Jul-Oct (3 anos empilhados)
   └─ Wet season: Nov-Jun (3 anos empilhados)

4. Cálculo de NDVI (se não pré-computado)
   └─ NDVI = (B8 - B4) / (B8 + B4)
   └─ Intervalo: -1 (água) a +1 (floresta densa)
   └─ 0: solo/urbano

5. Estatísticas de Vegetação
   └─ NDVI médio por imagem
   └─ Min/max/std de NDVI
```

**Saída**:
```
sentinel2_dry_composite.nc: (xarray Dataset)
sentinel2_wet_composite.nc: (xarray Dataset)
- Dimensões: (time: 3, latitude: 500, longitude: 500)
- Bandas: B4, B3, B2, NDVI (ou apenas NDVI se pré-computado)

vegetation_stats.csv:
- year, season, metric, mean, min, max, std
- Exemplo: 2024, dry, NDVI, 0.65, 0.12, 0.92, 0.18

sentinel2_stats.json:
- files_processed: 6
- years_covered: [2022, 2023, 2024]
- spatial_resolution_m: 10
```

**Uso em Módulos**:
- **Module A**: NDVI como feature (vegetação densa = falso positivo?)
- **Module B**: Densidade de vegetação → velocidade de propagação?

---

### 4. process_era5.py

**Entrada**: `data/raw/era5/ERA5_*.nc` (12+ arquivos mensais 2022-2024)

**Processamento**:
```
1. Carregamento de Dados Horários
   └─ Abre cada arquivo NetCDF com 24 leituras/dia

2. Crop para MATOPIBA
   └─ Seleciona grid cells que cobrem MATOPIBA

3. Agregação para Diário
   └─ Calcula média diária para cada variável
   └─ Exceção: precipitation (soma em vez de média)
   └─ Min/max de temperatura

4. Cálculo de Índices Derivados
   └─ wind_magnitude = sqrt(u² + v²) em m/s
   └─ wind_direction = atan2(v, u) em graus (0-360°)
   └─ relative_humidity = f(temperatura, ponto de orvalho)
   └─ drying_index = 100 - RH (quanto mais seco, maior índice)

5. Merge de Meses
   └─ Empilha 12+ meses em série temporal contínua
```

**Saída**:
```
era5_daily_aggregates.nc: (xarray Dataset)
- Dimensões: (time: 1095, latitude: 60, longitude: 100)
- Variáveis:
  - 2m_temperature (K)
  - relative_humidity (%)
  - wind_magnitude (m/s)
  - wind_direction (graus)
  - total_precipitation (mm)
  - drying_index (%)
  - soil_moisture_0_7cm (m³/m³)
  - surface_solar_radiation_downwards (J/m²)

weather_statistics.csv:
- variable, mean, min, max, std
- Exemplo: wind_magnitude, 3.2, 0.5, 12.1, 2.1

era5_stats.json:
- temporal_coverage: 2022-01-01 to 2024-12-31
- days_covered: 1095
- spatial_resolution_km: 25
```

**Uso em Módulos**:
- **Module A**: Temperatura, umidade → padrões de falsos positivos
- **Module B**: Vento (direção+magnitude), precipitação → propagação D+1

---

## 🔄 Fluxo de Processamento

```
ETAPA 1: Raw Data (Google Drive)
    ↓
[Download to data/raw/]
    ↓
ETAPA 2: Preprocessing (Este guia)
    ├─ process_firms.py         → firms_processed.csv
    ├─ process_mcd64a1.py       → mcd64a1_burned_area.nc
    ├─ process_sentinel2.py     → sentinel2_*_composite.nc
    └─ process_era5.py          → era5_daily_aggregates.nc
    ↓
data/processed/ (Features prontas)
    ↓
ETAPA 3: Feature Engineering (próxima)
    ├─ weak_labeling.py         → hotspots_labeled.gpkg
    ├─ calculate_persistence.py → persistence_features.csv
    ├─ extract_patch_features.py → patch_features.csv
    └─ create_grid_labels.py    → grid_labels.csv
    ↓
Module A: Classification (Falsos Positivos)
Module B: Regression (Propagação D+1)
```

---

## 📊 Estrutura de Dados Processados

### FIRMS Processado (Tabular)

```
DataFrame com 1 linha por hotspot detectado
latitude, longitude, acq_datetime, brightness, confidence, persistence_score, ...

Uso: Entrada para Module A classifier
      Cada linha = candidato a falso positivo
```

### MCD64A1 Processado (Raster Temporal)

```
xarray Dataset (time, latitude, longitude)
- Dimensão time: 36 meses (jan 2022 - dez 2024)
- Cada célula: valor 0-365 (dia do ano quando queimou)

Uso: Ground truth para Module A
      Target para Module B (propagação)
```

### Sentinel-2 Processado (Raster Temporal)

```
xarray Dataset (time, latitude, longitude)
- Dimensão time: 3 anos (1 imagem dry + 1 wet por ano)
- Bandas: NDVI principalmente
- Resolução: 10m x 10m

Uso: Feature visual para Module A e B
      Indica densidade de vegetação
```

### ERA5 Processado (Grade de Tempo)

```
xarray Dataset (time, latitude, longitude)
- Dimensão time: 1095 dias (3 anos)
- Grid: 0.25° = ~25km de espaçamento
- Variáveis: temperatura, umidade, vento, chuva, etc

Uso: Features climáticas para Module A e B
      Explica padrões de fogo e propagação
```

---

## ⚙️ Parâmetros Ajustáveis

Se precisar modificar comportamento dos scripts:

### process_firms.py

```python
# Linha ~27: Thresholds de confiança
min_confidence = 30  # Padrão: 30% (aumente para ser mais seletivo)

# Linha ~100: Tamanho da grade de agregação
grid_size = 0.1  # Padrão: 0.1° (menor = mais granular)

# Linha ~116: Janela temporal de persistência
window_days = 7  # Padrão: 7 dias (aumente para agregar mais)
```

### process_mcd64a1.py

```python
# Nenhum parâmetro crítico (dados já processados pela NASA)
# Ajustes possíveis na função crop_to_matopiba() se mudar AOI
```

### process_sentinel2.py

```python
# Nenhum parâmetro crítico (compostos já criados pelo GEE)
```

### process_era5.py

```python
# Nenhum parâmetro crítico (agrupa todos os dados disponíveis)
```

---

## 🐛 Troubleshooting

### Erro: "FileNotFoundError: data/raw/firms_hotspots/firms_combined_2022-2024.csv"

**Solução**:
1. Confirmar que Etapa 1 completou com sucesso
2. Verificar que arquivo está em `data/raw/firms_hotspots/`
3. Se arquivo não existe, re-rodar: `python src/data_ingest/download_firms.py`

### Erro: "ModuleNotFoundError: No module named 'rasterio'"

**Solução**:
```bash
pip install rasterio rioxarray xarray
```

### Erro: "No MCD64A1 GeoTIFF files found"

**Solução**:
1. Confirmar que GEE exports completaram em Etapa 1
2. Baixar arquivos de Google Drive (pasta 'fireml_data/')
3. Colocar em `data/raw/mcd64a1/`
4. Re-rodar: `python src/preprocessing/process_mcd64a1.py`

### Erro: "GDAL/Rasterio cannot read file"

**Causa comum**: Arquivo corrompido no download

**Solução**:
1. Re-baixar arquivo de Google Drive
2. Tentar com arquivo diferente para testar
3. Se problema persistir, usar formato NetCDF alternativo

---

## ✅ Checklist de Conclusão

- [ ] Verificar que `data/raw/` contém todos os 4 tipos de dados
- [ ] Criar diretório `data/processed/` com subdiretorias
- [ ] Executar `process_firms.py` → verificar `firms_processed.csv`
- [ ] Executar `process_mcd64a1.py` → verificar `.nc` file
- [ ] Executar `process_sentinel2.py` → verificar compostos dry/wet
- [ ] Executar `process_era5.py` → verificar dados diários
- [ ] Rodar `data_loader.py` → verificar que LoadAll() carrega 5+ datasets
- [ ] Comparar tamanhos de arquivos com estatísticas geradas
- [ ] Documentar qualquer ajuste de parâmetros realizado
- [ ] Backupar `data/processed/` em pasta externa (segurança)

---

## 📈 Próximas Etapas

Quando Etapa 2 estiver completa:

### Etapa 3: Feature Engineering
```bash
python src/preprocessing/weak_labeling.py      # Gera y_train para Module A
python src/preprocessing/feature_engineering.py # Cria X_train para ML
```

### Etapa 4: Treinamento de Modelos
```bash
python src/module_a/train_classifier.py        # Module A: Classificador
python src/module_b/train_propagation.py       # Module B: Preditor
```

---

## 📚 Referências

- **Rasterio/rioxarray**: https://corteva.github.io/rioxarray/
- **Xarray**: https://docs.xarray.dev/
- **Pandas**: https://pandas.pydata.org/docs/
- **NumPy**: https://numpy.org/doc/

---

**Última Atualização**: 11 de novembro de 2025
**Status**: Pronto para executar!

