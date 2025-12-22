# Fase 1 - Etapa 1: Ingestão de Dados - Guia Prático

**Data de Início**: 11 de novembro de 2025
**Duração**: ~1 semana
**Objetivo**: Coletar todos os dados brutos para MATOPIBA (2022-2024)

---

## Objetivo Geral da Etapa 1

Realizar ingestão completa de dados de 4 fontes principais:
1. **FIRMS** (NASA) - Hotspots de fogo
2. **MCD64A1** (MODIS) - Área queimada
3. **Sentinel-2** (ESA) - Imagens ópticas
4. **ERA5** (Copernicus) - Dados meteorológicos

**Período**: 2022-2024 (3 anos, foco: julho-outubro = estação seca)

---

## 📋 Estrutura de Dados

```
data/
├── raw/
│   ├── firms_hotspots/
│   │   ├── firms_viirs_20251111.csv
│   │   ├── firms_modis_20251111.csv
│   │   └── firms_combined_2022-2024.csv
│   │
│   ├── mcd64a1/
│   │   ├── MCD64A1_202207.tif
│   │   ├── MCD64A1_202208.tif
│   │   └── ... (36 monthly files)
│   │
│   ├── sentinel2/
│   │   ├── Sentinel2_2024_dry.tif
│   │   ├── Sentinel2_2023_dry.tif
│   │   └── Sentinel2_2022_dry.tif
│   │
│   ├── era5/
│   │   ├── ERA5_202207.nc
│   │   ├── ERA5_202208.nc
│   │   └── ... (12+ monthly files)
│   │
│   └── aoi/
│       └── matopiba.shp
│
└── processed/
    ├── features_module_a/
    └── features_module_b/
```

---

## 🚀 Como Executar

### Opção 1: Executar Tudo de Uma Vez (Recomendado)

```bash
conda activate fireml
cd "c:\Users\bessa\Downloads\Projeto Mestrado"
python src/data_ingest/run_all_downloads.py
```

**Tempo estimado**: 1-2 horas (FIRMS será rápido, GEE e CDS podem levar mais)

### Opção 2: Executar Scripts Individuais

```bash
# 1. FIRMS (mais rápido - ~5-10 min)
python src/data_ingest/download_firms.py

# 2. MODIS MCD64A1 (vai para Google Drive - ~30 min)
python src/data_ingest/download_mcd64a1.py

# 3. Sentinel-2 (vai para Google Drive - ~30 min)
python src/data_ingest/download_sentinel2.py

# 4. ERA5 (vai para Google Drive - ~30 min)
python src/data_ingest/download_era5.py
```

---

## 📊 Entendendo os Datasets e Seu Propósito

Antes de começar, é IMPORTANTE entender por que cada dataset é necessário:

### **A Pirâmide de Dados do Seu Projeto**

```
         Modelo Treinado
              ↑
        (Module A + B)
              ↑
        ┌─────────────┐
        │   Features  │  ← Dados climáticos e visuais
        │ (ERA5 +     │    que explicam QUANDO fogo ocorre
        │  Sentinel-2)│
        └─────────────┘
              ↑
        ┌─────────────┐
        │Ground Truth │  ← O que REALMENTE queimou
        │ (MCD64A1)   │    (verdade terrestre)
        └─────────────┘
              ↑
        ┌─────────────┐
        │   Entrada   │  ← Hotspots detectados pelo satélite
        │  (FIRMS)    │    (dados brutos)
        └─────────────┘
```

### **Como os Dados Se Conectam**

**Module A - Detecção de Espúrios (Falsos Positivos)**:
1. FIRMS encontra: "Há calor/fogo nesta coordenada"
2. Você compara com MCD64A1: "Mas queimada foi registrada?"
   - SIM + SIM = Verdadeiro positivo ✓
   - SIM + NÃO = Falso positivo (ruído, reflexo urbano) ✗
3. Você adiciona features (Sentinel-2 + ERA5):
   - Vegetação verde? Temperatura? Umidade?
   - Seu modelo aprende: "Com essas features + hotspot FIRMS = 95% chance de ser falso"

**Module B - Propagação D+1 (Amanhã)**:
1. FIRMS hoje: "Detectou fogo em XY"
2. MCD64A1 amanhã: "Propagou para onde?"
3. ERA5 (previsão): "Vento amanhã vai ser forte?" "Vai chover?"
4. Sentinel-2: "Qual a densidade de vegetação ao redor?"
5. Seu modelo prevê: "Fogo vai se propagar para NORDESTE amanhã"

---

## 📊 Dados: O Que Você Vai Baixar

### 1. FIRMS Hotspots ✅ (CONCLUÍDO)
**Fonte**: NASA Earthdata (login: andrey.bessa)
**Datasets**: VIIRS NRT + MODIS NRT
**Resolução**: 375m (VIIRS), 1km (MODIS)
**Formato**: CSV (tabela)
**Tamanho**: 16.6 KB
**Status**: Baixado com sucesso
**O que é**: Coordenadas (lat, lon) e datas de pixels detectados como FOGO
**Por que precisa**: Dados de ENTRADA para seus modelos - cada linha é um hotspot potencial

**Colunas**:
```
latitude, longitude, brightness, scan, track,
acq_date, acq_time, satellite, instrument, confidence,
version, bright_t31, frp, daynight, dataset
```

**Exemplo de linha**:
```
-5.123, -62.456, 315, 1.5, 1.2, 2024-09-15, 14:23, NOAA20, VIIRS, 85, 1.0, 295, 150, D, VIIRS
```

---

### 2. MODIS MCD64A1 (Burned Area) - IMAGEM RASTER
**Fonte**: Google Earth Engine (project: mestrado25)
**Dataset**: MODIS/061/MCD64A1
**Resolução**: 500m × 500m (cada pixel)
**Formato**: GeoTIFF (imagem georreferenciada)
**Tamanho**: ~5-10 MB por mês (~60-120 MB para 36 meses)
**Tempo**: ~5 min (export) + 30 min (Google Drive processing)
**Destino**: Google Drive pasta 'fireml_data/'
**O que é**: IMAGEM mostrando QUANDO cada pixel foi queimado (dia do ano 1-365) ou 0=não queimado
**Por que precisa**: VERDADE TERRESTRE (ground truth) para Module A
- Compara "FIRMS detectou fogo" vs "MCD64A1 registrou queimada"
- Se FIRMS=SIM mas MCD64A1=NÃO → Falso positivo (treina seu modelo a rejeitar)
- Se FIRMS=SIM e MCD64A1=SIM → Verdadeiro positivo (modelo aprende a aceitar)

**Exemplo visual**:
```
Imagem MCD64A1 (500m resolução):
Valor 0    = pixel não queimado (cor escura)
Valor 152  = queimou no dia 152 do ano
Valor 365  = queimou no dia 365 do ano

┌──────────────────────┐
│   0   152   0   0    │
│   0   152   0 365    │
│   0    0    0 365    │
│   0    0    0   0    │
└──────────────────────┘
```

**Tarefas exportadas**: 36 (3 anos × 12 meses)

---

### 3. Sentinel-2 (Optical Imagery) - IMAGEM COLORIDA + INFRAVERMELHO
**Fonte**: Google Earth Engine / Copernicus (ESA)
**Dataset**: COPERNICUS/S2_SR_HARMONIZED (Level 2A)
**Resolução**: 10m × 10m (muito detalhado - praticamente foto aérea)
**Formato**: GeoTIFF com múltiplas bandas
**Tamanho**: ~200-500 MB por composite
**Tempo**: ~5 min (export) + 30-60 min (Google Drive processing)
**Destino**: Google Drive pasta 'fireml_data/'
**O que é**: IMAGEM colorida de satélite (como foto aérea) + medições de infravermelho
**Por que precisa**: FEATURES VISUAIS para seus modelos (Module A e B)
- Vegetação verde densa (NDVI alto) vs área queimada (NDVI baixo)
- Cores diferentes indicam tipo de terreno (floresta, pastagem, urbano)
- Infravermelho detecta calor residual após queimada
- Seu modelo usa isso para: "Região com muita vegetação = maior risco de propagação"

**Bandas Espectrais**:
```
B2 (Azul)   : 490nm   - absorção de água
B3 (Verde)  : 560nm   - vegetação verde
B4 (Vermelho): 665nm  - vegetação saudável
B8 (NIR)    : 842nm   - INFRAVERMELHO próximo (vegetação)
NDVI (calc) : (B8-B4)/(B8+B4)
             Intervalo -1 a +1
             +1   = floresta densa (verde escura)
             0    = terreno urbano/solo exposto
             -0.5 = água
```

**Exemplo visual**:
```
Sentinel-2 RGB (cores naturais):
Verde escura = floresta intacta
Marrom/cinza = área queimada
Amarelo/bege = pastagem/agricultura

[Imagem mostrando MATOPIBA em cores reais - floresta vs queimada]

Sentinel-2 NDVI (índice de vegetação):
Vermelho escuro = NDVI alto (floresta densa)
Marrom claro = NDVI baixo (área queimada)
Azul = água
```

**Tarefas exportadas**: 6 (3 anos × dry season, 1 composite por estação)

---

### 4. ERA5 (Meteorology) - DADOS CLIMÁTICOS EM GRADE
**Fonte**: Copernicus CDS (European Center for Medium-Range Weather Forecasts)
**Dataset**: reanalysis-era5-single-levels
**Resolução**: 0.25° (~25km) - grade global
**Temporal**: Dados horários (24 leituras por dia)
**Formato**: NetCDF (tipo especial de arquivo científico)
**Tamanho**: ~50-100 MB por mês (~500 MB-1 GB para 12 meses)
**Tempo**: ~10-30 min por mês (CDS queue processing)
**O que é**: DADOS CLIMÁTICOS em formato de grade - não é foto, é números
**Por que precisa**: FEATURES CLIMÁTICAS que EXPLICAM quando fogo ocorre (Module A e B)
- Temperatura alta → fogo mais fácil de iniciar/propagar
- Vento forte → fogo se propaga mais rápido em certa direção
- Chuva → fogo é extinto/impedido
- Umidade do solo baixa → combustível mais seco, queima mais
- Seu modelo aprende: "Temperatura >30°C + vento forte NE + sem chuva = fogo vai se propagar para leste"

**Variáveis Climáticas Incluídas**:
```
Temperatura:
- 2m_temperature (K) - temperatura do ar a 2m de altura

Umidade:
- 2m_dewpoint_temperature (K) - ponto de orvalho (indica umidade)
- soil_moisture_0_7cm (m³/m³) - umidade do solo (0-7cm)

Vento (2 componentes):
- 10m_u_component_of_wind (m/s) - vento leste-oeste
- 10m_v_component_of_wind (m/s) - vento norte-sul
- (Combinados: magnitude = sqrt(u² + v²))

Radiação Solar:
- surface_solar_radiation_downwards (J/m²) - energia solar chegando

Chuva:
- total_precipitation (mm) - quantidade de chuva em 24h
```

**Exemplo visual**:
```
ERA5 - Temperatura MATOPIBA em 2024-09-15 13:00 (horário)
Grid com espaçamento 25km:

┌─────────────────────────────────┐
│ 32.5°C  32.1°C  31.8°C  31.5°C  │
│ 31.9°C  31.5°C  31.2°C  30.9°C  │
│ 30.8°C  30.4°C  30.1°C  29.8°C  │
│ 29.5°C  29.2°C  28.9°C  28.6°C  │
└─────────────────────────────────┘
(cada célula representa área de ~625 km²)

ERA5 - Velocidade do Vento (magnitude):
┌────────────────────────────┐
│  4.2 m/s  4.5 m/s  4.8 m/s │
│  3.9 m/s  4.1 m/s  4.4 m/s │
│  3.6 m/s  3.8 m/s  4.0 m/s │
└────────────────────────────┘
(vento forte = fogo se propaga + rápido)
```

**Tarefas**: 12+ (4 meses × 3 anos de estação seca)

---

## ⏱️ Timeline Estimada

| Tarefa | Tempo | Status |
|--------|-------|--------|
| FIRMS | 5-10 min | Local |
| MCD64A1 export | 5 min + 30 min GDrive | Google Drive |
| Sentinel-2 export | 5 min + 30-60 min GDrive | Google Drive |
| ERA5 | 30-60 min | Local (CDS queue) |
| **Total** | **~2 horas** | Parallelizable |

---

## 🔧 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'X'"
```bash
pip install requests pandas geopandas rasterio rioxarray xarray dask scikit-learn lightgbm xgboost geemap
```

### ❌ FIRMS: Conexão recusada
```
Solução:
1. Verifique credenciais em .env
2. Tente novamente (às vezes a API tem instabilidade)
3. Tente usar VPN se estiver em região bloqueada
```

### ❌ GEE: "Geometry is empty"
```
Solução:
1. Verifique que as coordenadas MATOPIBA estão corretas
2. Verifique que o projeto está com permissões suficientes
3. Tente novamente
```

### ❌ CDS: "Request is queued"
```
Solução (NORMAL!):
1. Isso é esperado - CDS processa em fila
2. Aguarde 5-30 minutos
3. Você receberá email quando estiver pronto
4. Download será disponibilizado na página CDS
```

---

## 📥 Próximas Etapas (Depois de Baixar)

Quando todos os dados estiverem prontos:

### 1. Verificar Downloads
```bash
# Contar arquivos
ls -la data/raw/firms_hotspots/
ls -la data/raw/mcd64a1/
ls -la data/raw/sentinel2/
ls -la data/raw/era5/
```

### 2. Próxima Etapa (Etapa 2): Processar Dados
```bash
python src/preprocessing/process_firms.py
python src/preprocessing/process_mcd64a1.py
python src/preprocessing/process_sentinel2.py
python src/preprocessing/process_era5.py
```

### 3. Próxima Etapa (Etapa 3): Gerar Features
```bash
python src/preprocessing/calculate_persistence.py
python src/preprocessing/weak_labeling.py
python src/preprocessing/feature_engineering.py
```

### 4. Output Final (Etapa 3)
```
data/processed/
├── features_module_a/
│   ├── hotspots_with_features.csv
│   ├── persistence_metrics.csv
│   └── weak_labels.csv
│
└── features_module_b/
    ├── grid_cells_with_features.csv
    └── burned_area_labels.csv
```

---

## 📊 Documentação Gerada (Etapa 1)

Cada script gera arquivo JSON com metadata:

```
data/raw/firms_hotspots/
  └── (metadata em output do script)

data/raw/mcd64a1/
  └── mcd64a1_export_metadata.json

data/raw/sentinel2/
  └── sentinel2_export_metadata.json

data/raw/era5/
  └── era5_download_metadata.json
```

---

## 💾 Requisitos de Espaço em Disco

| Dataset | Tamanho Estimado | Necessário |
|---------|------------------|-----------|
| FIRMS | 50 MB | Sim |
| MCD64A1 (36 meses) | 100-150 MB | Sim |
| Sentinel-2 (6 composites) | 1-3 GB | Sim |
| ERA5 (12+ meses) | 500 MB - 1 GB | Sim |
| **Total** | **~2-4 GB** | ✅ |

💡 **Dica**: Use `C:\Users\bessa\Downloads` que tem bastante espaço

---

## ✅ Checklist de Conclusão

- [ ] Verificar que todas as credenciais estão funcionando (todos test_*.py passando)
- [ ] Criar diretório `data/raw/` e subdiretorias
- [ ] Executar `run_all_downloads.py`
- [ ] Verificar que FIRMS foi baixado em `data/raw/firms_hotspots/`
- [ ] Confirmar que GEE e CDS tasks foram submetidas
- [ ] Aguardar 30-60 minutos para processamento
- [ ] Baixar arquivos GeoTIFF de Google Drive
- [ ] Verificar que ERA5 foi baixado em `data/raw/era5/`
- [ ] Executar scripts de processamento
- [ ] Gerar features finais para Module A e B

---

## 📚 Referências

- **FIRMS API**: https://firms.modaps.eosdis.nasa.gov/api/area/csv/
- **GEE Datasets**: https://developers.google.com/earth-engine/datasets
- **CDS ERA5**: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
- **MODIS MCD64A1**: https://lpdaac.usgs.gov/products/mcd64a1v006/

---

**Próxima Etapa**: Fase 1 - Etapa 2 - Processamento de Dados

**Status**: 🚀 Pronto para começar a Etapa 2!
