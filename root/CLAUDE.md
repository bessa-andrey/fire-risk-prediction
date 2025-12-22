# CLAUDE.md - Guia para Claude Code

Arquivo de orientacao para Claude Code (claude.ai/code) ao trabalhar com este repositorio.

**IMPORTANTE**: Sem emojis ou icones em scripts. Manter codigo limpo e profissional.

---

## PARAMETROS DE DESENVOLVIMENTO - LEITURA OBRIGATORIA

### 1. Desenvolvimento Passo-a-Passo (Step-by-Step)
- **Ao escrever qualquer codigo**: Avançar APENAS quando o usuario disser "avançar" ou equivalente
- **Cada etapa deve ser clara**: Mostrar o que foi feito, explicar antes de prosseguir
- **Aguardar feedback**: NUNCA pultar etapas mesmo que pareça óbvio continuar
- **Exemplos esperados**:
  - "Etapa 1: Estrutura do arquivo" → (aguardar) → "Etapa 2: Importações"
  - Implementar uma função simples → (aguardar) → Implementar teste → (aguardar) → Integração

### 2. Abordagem Didatica e Explicativa
- **Explicar O "POR QUE"**: Nao apenas COMO fazer, mas POR QUE fazer assim
- **Detalhes completos**:
  - Qual biblioteca foi escolhida e por quê (ex: geopandas vs shapely)
  - Por que essa estrutura de dados (ex: GeoDataFrame vs dict)
  - Que problema cada linha de código resolve
- **Contexto teórico**:
  - Conceitos fundamentais por trás das decisões
  - Limitações e alternativas de cada abordagem
  - Trade-offs entre performance, legibilidade e manutenibilidade
- **Exemplos numericos**: Quando relevante, fornecer exemplos com números concretos

### 3. Objetivo: Ensinar, Nao Apenas Executar
- **Foco em aprendizado**: Seu objetivo é aprender cada detalhe, nao ter código rodando
- **Questoes encorajadas**: Responder completamente a "por que?", "como funciona?", "qual é a alternativa?"
- **Sugestões de exercicios**: Após cada conceito importante, sugerir exercícios práticos para consolidar
- **Verificação de compreensão**: Garantir que você entende ANTES de passar para próximo passo
- **Documentação pessoal**: Encorajar que você escreva comentários explicando cada parte do código

### 4. Estilo de Comunicacao: Professor em Sala de Aula
- **Escrever MENOS**: Respostas curtas e focadas, nao textos longos
- **Escrever DEVAGAR**: Um conceito por vez, nunca varios de uma so vez
- **Explicar PROFUNDAMENTE**: Cada conceito com calma, como um professor paciente
- **Aguardar confirmacao**: Perguntar "Entendeu?" ou "Posso continuar?" antes de avancar
- **Ritmo do aluno**: O usuario define quando avancar, nunca o Claude

---

## Dissertacao de Mestrado

**Titulo**: Machine Learning para Deteccao e Propagacao de Fogo em MATOPIBA (Maranhao, Tocantins, Piaui, Bahia)

**Tipo**: Dissertacao de Mestrado em Ciencia de Dados

**Instituicao**: [Universidade]

**Objetivo**: Desenvolver sistema de Machine Learning para:
1. Identificar hotspots espurios (falsos positivos) em deteccoes FIRMS
2. Prever propagacao de fogo um dia a frente (D+1)

**Status**: 75% completo - Modulo A completo, Modulo B em desenvolvimento

**Prazo Final**: Defesa em Dezembro de 2025 (5 semanas)

## Documentacao Projeto

Guias principais:
1. **SETUP_AMBIENTE.md** - Configuracao completa do ambiente e credenciais
2. **PROJETO_SETUP.md** - Definicao completa do projeto (para apresentacoes)
3. **ETAPA1_INGESTAO.md** - Etapa 1: Ingestao de dados
4. **ETAPA2_PROCESSAMENTO.md** - Etapa 2: Processamento e limpeza
5. **ETAPA3_FEATURE_ENGINEERING.md** - Etapa 3: Feature engineering e treino (com GPU)
6. **ETAPA4_VALIDACAO.md** - Etapa 4: Validacao (espacial, temporal, confianca)
7. **MODULO_A_INFERENCIA.md** - Modulo A: Sistema de inferencia em producao
8. **CONTEUDO_PPTX_MELHORADO.md** - Conteudo detalhado para apresentacao (14 slides)
9. **RESUMO_EXPLICACOES.txt** - Explicacoes sintetizadas dos conceitos chave
10. **EXEMPLOS_PRATICOS.txt** - Exemplos numericos e visuais

## Visao Geral do Projeto

Este eh um projeto de dissertacao de mestrado em Machine Learning para deteccao e modelagem de propagacao de fogo na regiao MATOPIBA (Brasil). O projeto combina fontes de dados geoespaciais abertas com algoritmos de ML classicos e abordagens opcionais de deep learning para:

1. **Modulo A**: Detectar hotspots espurios (falsos positivos em deteccao satelite)
2. **Modulo B**: Prever propagacao de fogo um dia a frente (D+1)

**Status Atual**: 75% completo
- Modulo A: PRONTO para producao (82% acuracia)
- Modulo B: Em desenvolvimento
- Documentacao: Completa e profissional
- Apresentacao: Pronta (PPTX 13 slides)

## Environment Setup

Use Python 3.10+ with Conda (recommended) or venv:

```bash
# Conda setup (recommended)
conda create -n fireml python=3.10 -y
conda activate fireml

# Install geospatial base (conda-forge for compatibility)
conda install -c conda-forge geopandas rasterio rioxarray pyproj shapely xarray dask -y

# Install ML libraries
pip install scikit-learn lightgbm xgboost tqdm

# For deep learning (optional, for ConvLSTM in Module B)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# For notebooks and visualization
pip install jupyterlab
```

## Key Technologies

**Geospatial Data Processing**: geopandas, rasterio, rioxarray, shapely, xarray, dask
**Machine Learning**: scikit-learn, lightgbm, xgboost
**Deep Learning (optional)**: PyTorch + ConvLSTM for advanced fire spread modeling
**External Data Sources**: Google Earth Engine, NASA Earthdata, Copernicus CDS API

## Project Architecture

### Data Ingestion Layer
Pulls from multiple open data sources:
- **FIRMS**: NASA hotspot detection (daily NOAA/MODIS)
- **MCD64A1**: MODIS burned area product (monthly, 500m)
- **Sentinel-2**: Optical imagery (10m, ESA)
- **SRTM/DEM**: Digital elevation model
- **MapBiomas**: Land cover classification (yearly)
- **ERA5/GFS**: Meteorological data (wind, temperature, humidity)
- **OSM/Overpass**: Points of interest (POI)

### Module A: Spurious Fire Detection
Steps 1-7 of the pipeline:
1. Calculate persistence metrics from historical hotspots
2. Apply weak labeling (rule-based heuristics: proximity to POI, persistence, terrain)
3. Generate features: tabular (temporal/spatial context) + patch-based (Sentinel-2 patches)
4. Train baseline classifier (MVP rules + GBM with LightGBM/XGBoost)
5. Optional: Refine with CNN (EfficientNet on Sentinel-2 patches)
6. Validate with spatial/temporal splits, optimize for precision-recall trade-off
7. Output: GeoPackage with labeled hotspots + CSV with confidence scores

**Success Metrics**: PR-AUC curves, precision/recall at different thresholds, confusion matrices by biome/season

### Module B: Fire Propagation Prediction (D+1)
Steps 1-7 of the pipeline:
1. Create regular grid (250-500m cells) over study region
2. Label grid cells using MCD64A1 burned area and BurnDate
3. Extract features: wind direction/speed, temperature, humidity, elevation, slope, fuel type/load
4. Train baseline (logistic cellular automaton)
5. Optional: Deep learning with ConvLSTM (for spatiotemporal patterns)
6. Evaluate with IoU (Intersection over Union), Brier score, ablation studies
7. Output: GeoTIFF probability maps + Shapefile with risk zones

**Success Metrics**: IoU scores, Brier score, spatial/temporal consistency of predictions

### Visualization & Reporting
- QGIS maps and layouts for results
- PR-curves and IoU comparisons
- Municipality and protected area statistics
- Thesis figures and tables

## Data Sources and Credentials

Before starting implementation, ensure you have:
- **Google Earth Engine account** (free, for satellite imagery and datasets)
- **NASA Earthdata account** (free, for FIRMS, MODIS, SRTM)
- **Copernicus CDS account** (free, for ERA5 meteorological data)

Detailed data acquisition instructions are in `README-fire-open-data-pipeline.md`.

## Development Workflow

**Week 1: Data Ingestion**
- Define AOI (pilot region) and time period
- Download all required datasets
- Generate persistency metrics and POI distances
- Output: CSV with initial spurious classification flags

**Week 2: Module A (Spurious Detection)**
- Implement weak labeling rules
- Build baseline GBM classifier
- Optional: Fine-tune EfficientNet CNN on Sentinel-2 patches
- Validate with spatial/temporal splits
- Output: `hotspots_labeled.gpkg` + CSV with confidence scores

**Week 3: Module B (Propagation Modeling)**
- Implement logistic cellular automaton baseline
- Train on historical burned area data
- Generate D+1 probability maps
- Evaluate IoU and Brier score
- Output: `prob_spread_d1.tif` + `risk_zones.shp`

**Week 4: Visualization & Thesis Writing**
- Create QGIS visualizations
- Generate PR-curves, IoU plots, ablation studies
- Write dissertation chapters

## Important Implementation Notes

### Coordinate Reference Systems
- Use **EPSG:4326** (WGS84) for geographic coordinates
- Use **EPSG:3857** (Web Mercator) or local UTM zones for metric-based operations
- Always verify CRS when combining data from different sources using `rasterio` and `geopandas`

### Handling Large Rasters
- Use `dask` for chunked processing of large raster arrays (especially ERA5 and Sentinel-2)
- Prefer `rioxarray` with dask backends for efficient memory usage
- Chunk sizes: typically 256×256 for imagery, 500×500 for meteorological data

### Validation Strategy
- **Spatial split**: Train on sub-regions, test on others (prevents spatial autocorrelation bias)
- **Temporal split**: Train on one dry season, test on another (ensures temporal generalization)
- Always include "naive baseline" comparisons (e.g., persistence classifier for Module A)

### Reproducibility
- Document exact data version/date ranges used (satellite products have versioning)
- Pin dependency versions in `requirements.txt`
- Save random seeds for all ML models (scikit-learn, XGBoost, PyTorch)
- Version control configuration files for GEE, CDS API, and AOI definitions

## Documentation Files

- **`README-fire-open-data-pipeline.md`**: Comprehensive project guide with detailed workflow, data sources, code examples, and bibliography
- **`Mestrado 2025.docx`**: Master's thesis planning document with implementation timeline and delivery expectations
- **External**: Refer to original README for links to all data sources and detailed examples

## When Adding Code

1. **Geospatial operations**: Use `geopandas` for vectors, `rasterio`/`rioxarray` for rasters
2. **Feature engineering**: Document spatial/temporal resolution of each feature
3. **Model training**: Always include validation with spatial/temporal splits—do NOT use random k-fold
4. **Output format**: Use GeoPackage (.gpkg) for vector data, GeoTIFF (.tif) for rasters to preserve CRS/metadata
5. **Progress tracking**: Use `tqdm` for long-running operations (data loading, model training)

## GPU Acceleration

**IMPORTANTE**: Sempre que possível, utilize a GPU da máquina para acelerar processamento.

- **LightGBM**: Use `device_type='gpu'` em modelos GBM (NVIDIA CUDA requerido)
- **XGBoost**: Use `tree_method='gpu_hist'` para tree_method (NVIDIA CUDA requerido)
- **CuPy/CuDF**: Considere para operações numéricas massivas em arrays grandes
- **Verificar GPU**: `nvidia-smi` no terminal para confirmar disponibilidade e uso
- **CUDA Toolkit**: Deve estar instalado para aproveitamento de GPU (http://developer.nvidia.com/cuda-toolkit)

Preferência: GPU > CPU > Multiprocessing paralelo

## Module A Production System

**Status**: ✅ COMPLETE - Ready for operational use

The Module A inference system provides production-ready spurious hotspot detection:

### Scripts:
- **`predict_module_a.py`** (~450 lines) - Main inference script for classifying new hotspots
- **`run_module_a_pipeline.py`** (~320 lines) - Master orchestration script with modes: full, training, inference

### Key Features:
1. **Load trained models**: LightGBM (default) or XGBoost
2. **Process new hotspots**: CSV input with latitude, longitude, confidence, acq_datetime
3. **Make predictions**: Outputs spurious probability and confidence score
4. **Generate reports**: CSV predictions + JSON summary statistics

### Quick Usage:
```bash
# Infer on new hotspots
python src/models/predict_module_a.py --input new_hotspots.csv

# Or with XGBoost model
python src/models/predict_module_a.py --input new_hotspots.csv --model xgboost

# Full pipeline (training + validation + inference)
python src/models/run_module_a_pipeline.py --mode full

# Inference only (assumes trained model exists)
python src/models/run_module_a_pipeline.py --mode inference --input new_hotspots.csv
```

### Input Requirements:
CSV file with required columns:
- **latitude** (-15 to 0 for MATOPIBA)
- **longitude** (-65 to -40 for MATOPIBA)
- **confidence** (0-100, FIRMS confidence level)
- **acq_datetime** (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)

Optional:
- **hotspot_id** (if not provided, auto-generated)

### Output:
- **predictions_YYYYMMDD_HHMMSS.csv**: Predictions with columns:
  - prediction (0=real, 1=spurious)
  - spurious_probability (0.0-1.0)
  - confidence_score (HIGH/MEDIUM/LOW)

- **predictions_summary_YYYYMMDD_HHMMSS.json**: Statistics summary

### Performance:
- **Speed**: ~1-10 seconds per 100-1000 hotspots
- **Memory**: ~500MB-1GB depending on quantity
- **Accuracy**: PR-AUC 0.81, ROC-AUC 0.86, Overall 82%

### Recommendations for Production:
- Use predictions where `spurious_probability < 0.5` (recommended threshold)
- Filter out `spurious_probability >= 0.7` (high confidence spurious)
- Review MEDIUM confidence (0.5-0.7) predictions manually

See **MODULO_A_INFERENCIA.md** for complete documentation.

---

## Analise de Melhorias no Conteudo Atual

### Pontos Fortes Atuais

1. **Modulo A Completo**: Sistema de inferencia em producao funcional (82% acuracia)
2. **Documentacao Estruturada**: Organizacao clara em docs/{setup,etapas,modulos,visual}
3. **Validacao Multipla**: Espacial (4 regioes), temporal (3 anos), por confianca
4. **Exemplos Praticos**: Dados numericos concretos com metricas reais
5. **Apresentacao Visual**: PPTX moderna com 13 slides
6. **Reproducibilidade**: Codigo comentado, features documentadas, random seeds

### Areas para Melhoria - Prioridade Alta

#### 1. Modulo B (Propagacao D+1) - CRITICO PARA DISSERTACAO
**Status**: Nao iniciado
**Impacto**: Necessario para tese completa
**Acao Recomendada**:
- Criar script run_etapa_modulo_b.py
- Implementar modelo de propagacao (LightGBM + features meteorologicas)
- Treinar em dados historicos 2020-2023
- Validar com IoU (Intersection over Union)
- Documentar em docs/modulos/MODULO_B_PROPAGACAO.md
- Prazo: Semanas 2-3 do plano 5 semanas

#### 2. Pipeline Integrado (A + B)
**Status**: Nao existe
**Impacto**: Necessario para producao final
**Acao Recomendada**:
- Criar run_integrated_pipeline.py
- Input: hotspots FIRMS atuais
- Output: Classificacao (real/espurio) + predicao propagacao D+1
- Incluir API REST ou interface CLI
- Prazo: Semana 4

#### 3. Relatorio de Validacao Final
**Status**: Parcial (resultados em CSV)
**Impacto**: Critico para defesa
**Acao Recomendada**:
- Gerar relatorio executivo (PDF/HTML)
- Incluir: Metricas completas, graficos PR/ROC, confusion matrices
- Validacao espacial/temporal/confianca compiladas
- Comparacao com baselines
- Secao de limitacoes e trabalhos futuros
- Prazo: Semana 1

### Areas para Melhoria - Prioridade Media

#### 4. Features Adicionais para Modulo A
**Potencial**: +2-3% acuracia
**Acao Recomendada**:
- Testar SPI (Standardized Precipitation Index)
- Adicionar tipo de bioma/vegetacao
- Incluir anomalia de temperatura (vs media historica)
- Validar importancia via SHAP values
- Prazo: Semana 1 (paralelo com validacao)

#### 5. Interpretabilidade do Modelo
**Potencial**: Melhor compreensao para dissertacao
**Acao Recomendada**:
- Gerar SHAP plots (feature importance)
- Partial dependence plots para top 5 features
- Exemplos de predicoes certas/erradas
- Analise de limiar otimo (curva Precision-Recall)
- Incluir em docs/visual/INTERPRETABILIDADE.md
- Prazo: Semana 4

#### 6. Generalizacao para Outras Regioes
**Potencial**: Demonstra escalabilidade
**Acao Recomendada**:
- Testar Modulo A em regiao adjacente (ex: Cerrado global)
- Verificar performance em novo dominio
- Documentar transfer learning approach
- Incluir em discussao tese
- Prazo: Semana 5 (opcional)

### Areas para Melhoria - Prioridade Baixa

#### 7. Interface Grafica (GUI)
**Potencial**: Facilita uso para nao-programadores
**Acao Recomendada**:
- Criar app web simples (Streamlit/Flask)
- Upload CSV hotspots
- Visualizacao resultados em mapa interativo
- Download predicoes
- Prazo: Post-defesa (se tempo)

#### 8. Testes Automatizados
**Potencial**: Qualidade codigo
**Acao Recomendada**:
- Criar test suite (pytest)
- Testar: feature extraction, modelo, output formats
- CI/CD basico
- Prazo: Post-defesa (se tempo)

#### 9. Documentacao em Ingles
**Potencial**: Publicacao internacional
**Acao Recomendada**:
- Traduzir docs principais para ingles
- Preparar para submissao em revistas (Remote Sensing)
- README em bilingual
- Prazo: Post-defesa

---

## Checklist de Finalizacao (Proximo 5 Semanas)

### Semana 1 - Validacao Final (Nov 11-17)
- [ ] Executar Etapa 4 completa com todos dados
- [ ] Gerar relatorio validacao (espacial, temporal, confianca)
- [ ] Validar features adicionais (SPI, bioma, anomalia temp)
- [ ] Criar PDF relatorio executivo
- [ ] Atualizar metricas em documentacao

### Semana 2-3 - Modulo B (Nov 18-Dec 1)
- [ ] Preparar dataset propagacao (FIRMS -> MCD64A1 D+1)
- [ ] Extrair features meteorologicas (ERA5)
- [ ] Treinar modelo propagacao (LightGBM)
- [ ] Validacao cruzada temporal
- [ ] Documentar MODULO_B_PROPAGACAO.md

### Semana 4 - Integracao (Dec 2-8)
- [ ] Criar run_integrated_pipeline.py
- [ ] Testar A + B em conjunto
- [ ] Gerar relatorios integrados
- [ ] Criar documentacao API
- [ ] Preparar exemplos uso

### Semana 5 - Defesa (Dec 9-15)
- [ ] Finalizar capitulos tese
- [ ] Gerar figuras e tabelas finais
- [ ] Preparar slides apresentacao
- [ ] Ensaiar defesa
- [ ] Correcoes finais

---

## Estrutura Recomendada para Tese

### Capitulo 1: Introducao
- Contexto (fogo em MATOPIBA)
- Problema (hotspots espurios)
- Objetivo geral e especifico
- Contribuicoes esperadas

### Capitulo 2: Revisao Bibliografica
- Estado da arte em fire detection
- ML para sensoriamento remoto
- Dados geoespaciais abertos
- Weak labeling

### Capitulo 3: Metodologia
- Modulo A (deteccao espurios)
  - Weak labeling via MCD64A1
  - Features (20+)
  - Modelo LightGBM
  - Validacao multipla
- Modulo B (propagacao)
  - Grid regular
  - Features meteorologicas
  - Modelo propagacao
  - Metricas (IoU, Brier)

### Capitulo 4: Resultados
- Modulo A: 82% acuracia, ROC-AUC 0.86, PR-AUC 0.81
- Validacao espacial: 79-84% (4 regioes)
- Validacao temporal: 78-85% (3 anos)
- Validacao confianca: 75-89% (3 faixas)
- Modulo B: [Resultados] (TBD)

### Capitulo 5: Discussao
- Interpretacao resultados
- Comparacao com trabalhos relacionados
- Limitacoes metodologia
- Implicacoes praticas
- Trabalhos futuros

### Capitulo 6: Conclusao
- Resumo contribuicoes
- Impacto potencial
- Recomendacoes para pesquisas futuras

---

## Contato e Suporte

Para duvidas sobre:
- **Setup/ambiente**: Consulte SETUP_AMBIENTE.md
- **Etapas pipeline**: Consulte docs/etapas/
- **Modulo A**: Consulte MODULO_A_INFERENCIA.md
- **Apresentacao**: Consulte CONTEUDO_PPTX_MELHORADO.md
- **Conceitos**: Consulte RESUMO_EXPLICACOES.txt ou EXEMPLOS_PRATICOS.txt
