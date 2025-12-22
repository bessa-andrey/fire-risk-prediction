# Configuração do Projeto: Detecção e Propagação de Incêndios Florestais com ML

**Data de Início**: 11 de novembro de 2025
**Responsável**: Desenvolvedor em Manaus, AM
**Instituição**: Programa de Pós-Graduação (Mestrado)

---

## 1. Definição da Área de Interesse (AOI)

### AOI Selecionada: MATOPIBA

#### 📍 Localização Geográfica
- **Estados Abrangidos**: Maranhão, Tocantins, Piauí e Bahia
- **Área Total**: ~73 milhões de hectares
- **Biomas Predominantes**: Floresta Amazônica (norte), Cerrado, Formações Herbáceas

#### 📊 Justificativa Técnico-Científica

**1. Atividade de Incêndios**
- Aumento de 58% em área queimada em 2024 vs 2023
- Entre 50-200+ eventos de fogo por ano (suficiente para treinamento ML)
- Mix de incêndios: naturais, acidentais e para limpeza de área

**2. Infraestrutura de Dados**
- Cobertura excelente de satélites multissensoriais:
  - GOES-16 ABI (detecção em tempo quase real)
  - Landsat 7/8 (30m, histórico longo)
  - Sentinel-2 (10m, resolução alta)
  - MODIS (1km, resolução térmica)
  - VIIRS (375m, detecção de fogo)

**3. Pesquisa Anterior**
- Modelos ML já desenvolvidos para a região (80% de acurácia comprovada)
- Comunidade ativa de pesquisa
- Dados validados disponíveis

**4. Diversidade de Condições**
- Gradiente de cobertura vegetal (floresta → cerrado → agricultura)
- Variabilidade topográfica
- Múltiplas causas de incêndio (relevante para espúrios vs. reais)

#### 🗓️ Período de Análise
- **Período Completo**: 2022-2024 (3 anos)
- **Foco Principal**: Estações secas (julho-outubro) de cada ano
- **Validação**: Comparação entre períodos para robustez temporal

---

## 2. Objetivos do Projeto

### Objetivo Geral
Desenvolver modelos de machine learning para:
1. **Detecção de Hotspots Espúrios** (Module A): Classificar detecções de fogo como reais ou falsos positivos
2. **Predição de Propagação D+1** (Module B): Prever a expansão de incêndios para o dia seguinte

### Objetivos Específicos

#### Module A: Detecção de Espúrios
- Implementar classifier baseline com regras heurísticas
- Treinar modelo GBM (LightGBM/XGBoost) com ~80% de acurácia
- Refinar com CNN (EfficientNet) em patches Sentinel-2 (opcional)
- Validar com splits espacial/temporal
- Gerar dataset anotado: `hotspots_labeled.gpkg`

#### Module B: Propagação D+1
- Implementar baseline: autômato celular logístico
- Treinar modelos em dados históricos MCD64A1
- Opcional: ConvLSTM para padrões espaço-temporais
- Gerar mapas de probabilidade D+1: `prob_spread_d1.tif`
- Criar zonas de risco: `risk_zones.shp`

---

## 3. Arquitetura Geral do Projeto

### Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE INGESTÃO                       │
├─────────────────────────────────────────────────────────────┤
│  FIRMS (NASA)          │  MCD64A1 (MODIS)                   │
│  Sentinel-2 (ESA)      │  SRTM/DEM (NASA)                   │
│  MapBiomas             │  ERA5/GFS (NOAA)                   │
│  OSM/Overpass (POI)    │                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  MODULE A: ESPÚRIOS                         │
├─────────────────────────────────────────────────────────────┤
│ A.1: Persistência      │ A.5: CNN (opcional)               │
│ A.2: Weak Labeling     │ A.6: Validação PR-curve           │
│ A.3: Feature Eng.      │ A.7: Output (.gpkg + .csv)        │
│ A.4: GBM Baseline      │                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                MODULE B: PROPAGAÇÃO D+1                     │
├─────────────────────────────────────────────────────────────┤
│ B.1: Grid Regular      │ B.5: ConvLSTM (opcional)          │
│ B.2: Labeling          │ B.6: Validação IoU                │
│ B.3: Feature Extract.  │ B.7: Output (.tif + .shp)         │
│ B.4: CA Logístico      │                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               VISUALIZAÇÃO & RELATÓRIO                      │
├─────────────────────────────────────────────────────────────┤
│  QGIS Maps  │  PR-Curves  │  IoU Plots  │  Thesis Figures  │
└─────────────────────────────────────────────────────────────┘
```

### Tecnologias Principais

| Categoria | Ferramentas |
|-----------|------------|
| **Processamento Geoespacial** | GeoPandas, Rasterio, RioXarray, Shapely, PyProj |
| **Análise Dados** | Pandas, NumPy, Xarray, Dask |
| **Machine Learning** | Scikit-learn, LightGBM, XGBoost |
| **Deep Learning** | PyTorch, TorchVision (opcional) |
| **Cloud Computing** | Google Earth Engine, Google Cloud Storage |
| **Visualização** | QGIS, Matplotlib, Folium |
| **Utilities** | TQDM, Requests |

---

## 4. Cronograma de Implementação (Fase 1: Desenvolvimento)

### Etapa 1: Ingestão de Dados
**Objetivo**: Coleta e processamento inicial de dados

**Tarefas**:
1. Definir AOI exata (shapefile MATOPIBA)
2. Baixar FIRMS hotspots (2022-2024)
3. Baixar MCD64A1 burned area (2022-2024)
4. Baixar Sentinel-2 composite (dry season)
5. Baixar SRTM/DEM
6. Baixar dados de POI (OSM)
7. Gerar métricas de persistência
8. **Output**: CSV com classificação inicial de espúrios

### Etapa 2: Module A - Detecção de Espúrios
**Objetivo**: Classificador baseline com 80% acurácia

**Tarefas**:
1. Implementar weak labeling (regras heurísticas)
2. Feature engineering: tabular + patch-based
3. Treinar GBM (LightGBM/XGBoost)
4. Validação: PR-curves, splits espacial/temporal
5. Opcional: Fine-tuning EfficientNet
6. Otimizar threshold de precisão/recall
7. **Output**: `hotspots_labeled.gpkg` + CSV com scores

### Etapa 3: Module B - Propagação D+1
**Objetivo**: Predição de expansão de fogo

**Tarefas**:
1. Criar grid regular (250-500m cells)
2. Labeling: MCD64A1 BurnDate
3. Feature extraction: meteorologia, topografia, combustível
4. Treinar CA logístico baseline
5. Opcional: ConvLSTM
6. Validação: IoU, Brier score
7. **Output**: `prob_spread_d1.tif` + `risk_zones.shp`

### Etapa 4: Visualização & Dissertação
**Objetivo**: Figuras, mapas e documento final

**Tarefas**:
1. Gerar mapas QGIS
2. Criar PR-curves e IoU plots
3. Calcular estatísticas por município/bioma
4. Escrever capítulos de resultados
5. Gerar tabelas comparativas
6. **Output**: Documento de tese completo com figuras

---

## 5. Fontes de Dados

### 5.1 Detecção Ativa de Fogo

| Fonte | Resolução | Cobertura | Acesso | Descrição |
|-------|-----------|-----------|--------|-----------|
| **FIRMS (NASA)** | 1km | Global, daily | NASA Earthdata | Hotspots MODIS/VIIRS, 2000-presente |
| **INPE Queimadas** | 1km | Brasil, daily | Terrabrasilis | 9 sensores, metadados ricos |

**Acessar em**: https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/

### 5.2 Área Queimada

| Fonte | Resolução | Temporal | Acesso | Descrição |
|-------|-----------|----------|--------|-----------|
| **MCD64A1** | 500m | Mensal | Google Earth Engine | MODIS burned area (2000-2024) |
| **MapBiomas Fire** | 30m | Anual | Google Earth Engine | Neural nets, 1985-2020, por bioma |

### 5.3 Dados Auxiliares

| Tipo | Fonte | Resolução | Acesso |
|------|-------|-----------|--------|
| **Imagem Óptica** | Sentinel-2 | 10m | Google Earth Engine, ESA |
| **Imagem Óptica** | Landsat 8 | 30m | Google Earth Engine, USGS |
| **Elevação** | SRTM/DEM | 30m | Google Earth Engine, NASA |
| **Cobertura Terra** | MapBiomas | 30m | Google Earth Engine, Brasil |
| **Meteorologia** | ERA5 | 0.25° | Copernicus CDS |
| **POI** | OpenStreetMap | Variável | Overpass API |

---

## 6. Próximas Etapas: Credenciais e Setup

### ✅ Status: Pronto para Configuração de Credenciais

**A ser feito**:
1. [ ] Criar conta Google Earth Engine
2. [ ] Criar conta NASA Earthdata
3. [ ] Criar conta Copernicus CDS
4. [ ] Configurar Python environment (conda/venv)
5. [ ] Instalar bibliotecas geoespaciais
6. [ ] Testar conexões às APIs

---

## 7. Métricas de Sucesso

### Module A: Detecção de Espúrios
- **PR-AUC** ≥ 0.80
- **Precision @ Recall=0.90** > 0.75
- **Spatial consistency**: IoU entre regiões > 0.70
- **Temporal generalization**: Acurácia 2024 vs treino 2022-2023 > 0.75

### Module B: Propagação D+1
- **IoU (Intersection over Union)** ≥ 0.60
- **Brier Score** < 0.25
- **Spatial correlation** com queimadas reais > 0.65
- **Temporal validation**: Consistent predictions across seasons

---

## 8. Referências e Recursos

### Datasets Utilizados
- INPE FIRM hotspots: https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/
- MapBiomas: https://mapbiomas.org/
- Google Earth Engine: https://earthengine.google.com/

### Documentação Técnica
- Sentinela-2: https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/overview
- MODIS: https://lpdaac.usgs.gov/products/mcd64a1v006/
- ERA5: https://cds.climate.copernicus.eu/

### Literatura Chave
- [Seções adicionadas conforme pesquisa avança]

---

**Última Atualização**: 11 de novembro de 2025
