# Configuracao do Projeto: Classificacao Automatica de Focos de Incendio

**Autor**: Andrey Ruben Ribeiro Bessa
**Instituicao**: PPGEE - Universidade Federal do Amazonas (UFAM)
**Orientador**: Prof. D.Sc. Celso Barbosa Carvalho
**Coorientador**: Prof. D.Sc. Andre Chaves Mendes
**Defesa prevista**: Agosto de 2026

---

## 1. Area de Estudo: MATOPIBA

### Localizacao
- **Estados**: Maranhao, Tocantins, Piaui e Bahia
- **Area Total**: ~73 milhoes de hectares
- **Bioma predominante**: Cerrado (91% da extensao)
- **Periodo de analise**: 2022-2024

### Justificativa
- Elevada incidencia de queimadas (naturais e antropicas)
- Fronteira agricola com uso do fogo para manejo
- Cobertura excelente de dados satelitais
- Diversidade de condicoes (gradiente Amazonia-Cerrado-Caatinga)

---

## 2. Objetivo do Projeto

### Objetivo Geral
Desenvolver e validar um sistema de classificacao automatica de focos de incendio do FIRMS, capaz de distinguir deteccoes reais de espurias, utilizando integracao de dados satelitais e meteorologicos com tecnicas de aprendizado de maquina.

### Objetivos Especificos
1. Pipeline de ingestao e processamento de dados multifonte (FIRMS, MCD64A1, Sentinel-2, ERA5)
2. Metodologia de weak labeling (FIRMS vs MCD64A1, janela +-15 dias)
3. Extracao de 20+ features (temporais, meteorologicas, vegetacao, espaciais)
4. Treinamento e comparacao de modelos (LightGBM, XGBoost, baselines) com otimizacao Optuna
5. Validacao espacial (leave-one-state-out) e temporal (treino 2022-2023, teste 2024)
6. Analise de importancia de features e interpretabilidade

---

## 3. Arquitetura do Sistema

### Pipeline em 4 Etapas

```
Etapa 1: Ingestao
  FIRMS (375m) + MCD64A1 (500m) + Sentinel-2 (10m) + ERA5 (0.25 graus)
      |
Etapa 2: Processamento
  Limpeza, reprojecao, mosaico, interpolacao, NDVI
      |
Etapa 3: Feature Engineering
  Weak labeling + extracao de 20+ features
  Dataset: 9.198 amostras balanceadas (4.599/4.599)
      |
Etapa 4: Modelagem
  9 modelos (Dummy, LR, SVM, DT, RF, LightGBM, XGBoost + Optuna)
  Validacao espacial e temporal
  Analise estatistica (Bootstrap, McNemar, Wilcoxon)
```

### Tecnologias

| Categoria | Ferramentas |
|-----------|------------|
| Geoespacial | geopandas, rasterio, rioxarray, shapely, pyproj, xarray |
| ML | scikit-learn, lightgbm, xgboost, optuna |
| Analise | pandas, numpy, scipy |
| Visualizacao | matplotlib, folium |
| Dados externos | Google Earth Engine, NASA Earthdata, Copernicus CDS |

---

## 4. Fontes de Dados

| Fonte | Resolucao | Temporal | Uso |
|-------|-----------|----------|-----|
| FIRMS (NASA) | 375m (VIIRS) | Diario | Focos de incendio ativo |
| MCD64A1 (MODIS) | 500m | Mensal | Area queimada (rotulagem) |
| Sentinel-2 (ESA) | 10m | 5 dias | NDVI (vegetacao) |
| ERA5 (ECMWF) | 0.25 graus | Horario | Meteorologia (5 variaveis) |

---

## 5. Resultados Alcancados

| Modelo | Acuracia | ROC-AUC | PR-AUC |
|--------|----------|---------|--------|
| DummyClassifier | 70% | 50% | 35% |
| Limiar FIRMS | 72% | 64% | 55% |
| Regressao Logistica | 75% | 78% | 72% |
| SVM (RBF) | 77% | 80% | 74% |
| Random Forest | 79% | 83% | 78% |
| **LightGBM (proposto)** | **82%** | **86%** | **81%** |
| XGBoost | 81% | 85% | 80% |

- **Validacao espacial**: Variacao < 4pp entre 4 estados
- **Validacao temporal**: Degradacao ~5pp (concept drift)
- **Impacto operacional**: 87% reducao de falsos positivos (recall 84%)

---

## 6. Credenciais Necessarias

| Servico | Uso | Status |
|---------|-----|--------|
| Google Earth Engine | Sentinel-2, MCD64A1 | Configurado |
| NASA Earthdata | FIRMS, MCD64A1 | Configurado |
| Copernicus CDS | ERA5 | Configurado |

Detalhes: `docs/setup/SETUP_AMBIENTE.md`

---

## 7. Ambiente Python

```bash
conda create -n fireml python=3.10 -y
conda activate fireml
conda install -c conda-forge geopandas rasterio rioxarray pyproj shapely xarray dask -y
pip install scikit-learn lightgbm xgboost optuna tqdm scipy
```

---

## 8. Cronograma Ate a Defesa (Mar-Ago 2026)

| Atividade | Mar | Abr | Mai | Jun | Jul | Ago |
|-----------|-----|-----|-----|-----|-----|-----|
| Refinamento classificador | X | X | | | | |
| Analise de erros e robustez | X | X | | | | |
| Encadeamento espaco-temporal | | X | X | X | | |
| Avaliacao propagacao | | | X | X | | |
| Consolidacao resultados | | | | X | X | |
| Redacao final | | | | | X | X |
| Defesa | | | | | | X |

---

**Ultima Atualizacao**: 12 de fevereiro de 2026
