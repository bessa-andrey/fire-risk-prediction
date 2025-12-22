# Setup Completo - Projeto Fire Detection & Propagation

**Data de Conclusão**: 11 de novembro de 2025
**Status**: ✅ **PRONTO PARA COMEÇAR**

---

## ✅ Configurações Validadas

### 1. Google Earth Engine
- **Status**: ✅ Funcionando
- **Project ID**: mestrado25
- **Datasets acessíveis**:
  - MODIS MCD64A1 (burned area): 266 imagens
  - Sentinel-2 (optical): ✓
  - MapBiomas (land cover): ✓

**Teste executado**: `python test_gee_fixed.py`
```
✅ Inicialização bem-sucedida!
✅ Dataset encontrado: 266 imagens
✅ Sentinel-2 encontrado!
✅ MapBiomas encontrado!
```

---

### 2. NASA Earthdata
- **Status**: ✅ Funcionando
- **Account**: andrey.bessa
- **Datasets acessíveis**:
  - FIRMS VIIRS NRT (hotspots, 375m, ~1-2 dias delay)
  - FIRMS MODIS NRT (hotspots, 1km, ~1-2 dias delay)

**Teste executado**: `python test_earthdata.py`
```
✅ Conexão bem-sucedida!
✅ Dados recebidos: 2 registros
✅ MODIS acessível!
```

---

### 3. Copernicus CDS
- **Status**: ✅ Funcionando
- **API Endpoint**: https://cds.climate.copernicus.eu/api
- **Datasets acessíveis**:
  - ERA5 (temperature, wind, humidity, precipitation)
  - Resolução: 0.25° (~25km)
  - Temporal: Horário

**Teste executado**: `python test_cds.py`
```
✅ Conexão bem-sucedida!
✅ Request ID: 6c7cd90b-694c-470f-8e92-a2ab197bfe30
✅ Status: successful
✅ Requisição processada!
```

---

## 📋 Arquivos de Configuração

### `.env` (Credenciais)
```
EARTHDATA_USERNAME=andrey.bessa
EARTHDATA_PASSWORD=Bess@20debby

CDS_URL=https://cds.climate.copernicus.eu/api
CDS_KEY=f39f775f-f7e2-4768-884a-52dee3779a8d
```

### `requirements.txt` (Dependências)
```
earthengine-api==1.7.0
cdsapi==0.7.7
requests==2.32.5
python-dotenv==1.2.1
pandas==2.x.x
geopandas==0.14.x
rasterio==1.3.x
rioxarray==0.14.x
xarray==2024.x.x
dask==2024.x.x
scikit-learn==1.3.x
lightgbm==4.x.x
xgboost==2.x.x
```

---

## 🚀 Próximas Etapas: SEMANA 1 - Ingestão de Dados

### Timeline
- **Semana 1**: Data Ingestion (agora!)
  - [ ] Definir shapefile MATOPIBA
  - [ ] Baixar FIRMS hotspots (2022-2024)
  - [ ] Baixar MCD64A1 burned area (2022-2024)
  - [ ] Baixar Sentinel-2 composite (dry season)
  - [ ] Baixar SRTM/DEM
  - [ ] Baixar MapBiomas
  - [ ] Baixar ERA5 (temperature, wind, humidity, precipitation)
  - [ ] Gerar métricas de persistência
  - [ ] Output: CSV com classificação inicial

### Scripts a Criar
1. `download_firms.py` - Baixar hotspots FIRMS
2. `download_mcd64a1.py` - Baixar MCD64A1 via GEE
3. `download_sentinel2.py` - Baixar Sentinel-2 via GEE
4. `download_era5.py` - Baixar ERA5 via CDS
5. `calculate_persistence.py` - Calcular persistência de fogo
6. `weak_labeling.py` - Aplicar regras heurísticas iniciais

---

## 📊 AOI Selecionada: MATOPIBA

**Coordenadas**:
- North: 0°
- South: -15°
- East: -40°
- West: -65°

**Biomas**: Amazônia (norte), Cerrado, Formações herbáceas
**Estados**: Maranhão, Tocantins, Piauí, Bahia
**Período**: 2022-2024 (foco: julho-outubro)

---

## 🔒 Segurança & Boas Práticas

✅ `.env` está em `.gitignore`
✅ Credenciais não commitadas no Git
✅ Variáveis de ambiente carregadas via `load_dotenv()`
✅ APIs testadas e validadas

---

## 📚 Documentação Criada

1. **CLAUDE.md** - Guia para Claude Code
2. **PROJETO_SETUP.md** - Definição do projeto completo
3. **CREDENCIAIS_SETUP.md** - Setup de credenciais
4. **GEE_SETUP_DETALHADO.md** - Google Earth Engine passo-a-passo
5. **EARTHDATA_SETUP.md** - NASA Earthdata detalhado
6. **CDS_SETUP.md** - Copernicus CDS detalhado
7. **SETUP_COMPLETO.md** - Este arquivo
8. **PROJETO_SETUP.md** - Utilizado para apresentações/publicações

---

## 🎯 Métricas de Sucesso (Baseline)

### Module A: Spurious Detection
- PR-AUC ≥ 0.80
- Precision @ Recall=0.90 > 0.75
- Spatial consistency IoU > 0.70

### Module B: Propagation Prediction
- IoU ≥ 0.60
- Brier Score < 0.25
- Spatial correlation > 0.65

---

## 💾 Estrutura de Diretórios

```
Projeto Mestrado/
├── .env                          # Credenciais (NÃO commitar)
├── .gitignore                    # Exclusões Git
├── CLAUDE.md                     # Guia para Claude Code
├── PROJETO_SETUP.md              # Documento de projeto
├── SETUP_COMPLETO.md             # Este arquivo
│
├── data/
│   ├── raw/
│   │   ├── firms_hotspots/       # FIRMS CSV
│   │   ├── mcd64a1/              # MODIS burned area
│   │   ├── sentinel2/            # Sentinel-2 GeoTIFF
│   │   ├── dem/                  # SRTM elevation
│   │   ├── era5/                 # ERA5 NetCDF
│   │   └── aoi/
│   │       └── matopiba.shp      # AOI shapefile
│   │
│   └── processed/
│       ├── features_module_a/
│       └── features_module_b/
│
├── src/
│   ├── data_ingest/
│   │   ├── download_firms.py
│   │   ├── download_mcd64a1.py
│   │   ├── download_sentinel2.py
│   │   ├── download_era5.py
│   │   └── download_dem.py
│   │
│   ├── preprocessing/
│   │   ├── persistence_metrics.py
│   │   ├── weak_labeling.py
│   │   └── feature_engineering.py
│   │
│   ├── module_a/
│   │   ├── training.py
│   │   └── inference.py
│   │
│   └── module_b/
│       ├── training.py
│       └── inference.py
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_module_a.ipynb
│   └── 03_module_b.ipynb
│
├── outputs/
│   ├── models/
│   ├── results/
│   └── figures/
│
└── tests/
    ├── test_gee.py ✅
    ├── test_earthdata.py ✅
    └── test_cds.py ✅
```

---

## 🎓 Próximas Ações

**Imediato** (hoje):
1. ✅ Validar todas as APIs (DONE!)
2. [ ] Criar shapefile MATOPIBA
3. [ ] Fazer primeiro download FIRMS

**Curto prazo** (próximos dias):
4. [ ] Implementar scripts de ingestão
5. [ ] Processar dados (Semana 1)
6. [ ] Treinar Module A (Semana 2)

**Médio prazo** (próximas semanas):
7. [ ] Treinar Module B (Semana 3)
8. [ ] Gerar visualizações (Semana 4)
9. [ ] Escrever dissertação

---

## 📧 Suporte & Referências

- **GEE Docs**: https://developers.google.com/earth-engine
- **FIRMS API**: https://firms.modaps.eosdis.nasa.gov/
- **CDS API**: https://cds.climate.copernicus.eu/how-to-api
- **MapBiomas**: https://mapbiomas.org/

---

**Versão**: 1.0
**Data**: 11 de novembro de 2025
**Status**: ✅ Pronto para iniciar Semana 1

---

🚀 **VAMOS COMEÇAR A SEMANA 1: INGESTÃO DE DADOS!**
