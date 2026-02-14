# Status do Projeto - Classificacao Automatica de Focos de Incendio

**Data da Ultima Atualizacao**: 12 de fevereiro de 2026
**Responsavel**: Andrey Ruben Ribeiro Bessa
**Instituicao**: PPGEE - Universidade Federal do Amazonas (UFAM)
**Fase Atual**: Classificacao concluida. Qualificacao aprovada. Proximo: analise espaco-temporal.

---

## Resumo Executivo

| Item | Status | Progresso |
|------|--------|-----------|
| Etapa 1 - Ingestao de Dados | Concluido | 100% |
| Etapa 2 - Processamento de Dados | Concluido | 100% |
| Etapa 3 - Feature Engineering + Weak Labeling | Concluido | 100% |
| Etapa 4 - Treinamento, Validacao e Analise | Concluido | 100% |
| Dissertacao (qualificacao) | Concluido | 100% |
| Correcoes pos-qualificacao (AVALIACAO-V2) | Concluido | 100% |
| Analise espaco-temporal (propagacao) | Planejado | 0% |
| Redacao final e defesa | Planejado | 0% |
| **Pipeline Completo** | **100% Concluido** | **100%** |

---

## Etapa 1: Ingestao de Dados (CONCLUIDO)

### Dados Obtidos

| Dataset | Descricao | Resolucao | Periodo |
|---------|-----------|-----------|---------|
| FIRMS | Focos de incendio ativo (VIIRS 375m) | 375m | 2022-2024 |
| MCD64A1 | Area queimada MODIS | 500m | 2022-2024 |
| Sentinel-2 | Imagens opticas (NDVI) | 10m | 2022-2024 |
| ERA5 | Reanalise meteorologica (5 variaveis) | 0.25 graus | 2022-2024 |

### Scripts
- `src/data_ingest/download_firms.py`
- `src/data_ingest/download_mcd64a1.py` / `download_mcd64a1_appeears.py`
- `src/data_ingest/download_sentinel2.py` / `download_sentinel2_pc.py`
- `src/data_ingest/download_era5.py` / `download_era5_cds.py`
- `src/data_ingest/run_all_downloads.py`

---

## Etapa 2: Processamento de Dados (CONCLUIDO)

### Scripts
- `src/preprocessing/process_firms.py` - Limpeza, filtragem, persistencia
- `src/preprocessing/process_mcd64a1.py` - Mosaico, reprojecao, GeoTIFF
- `src/preprocessing/process_sentinel2.py` - NDVI, cloud masking
- `src/preprocessing/process_era5.py` - Interpolacao, derivacao de variaveis
- `src/preprocessing/data_loader.py` - Data loader unificado
- `src/preprocessing/run_all_preprocessing.py` - Master script

---

## Etapa 3: Feature Engineering + Weak Labeling (CONCLUIDO)

### Scripts
- `src/preprocessing/weak_labeling.py` - Rotulagem automatizada FIRMS vs MCD64A1 (+-15 dias)
- `src/preprocessing/feature_engineering.py` - Extracao de 20+ features
- `src/preprocessing/validate_weak_labels.py` - Validacao com Cohen's Kappa (200 amostras)
- `src/preprocessing/run_etapa3.py` - Master script

### Dataset Gerado
- `data/processed/training/module_a_balanced.csv` - 9.198 amostras (4.599 real / 4.599 espurio)
- 20+ features: temporais, meteorologicas, vegetacao (NDVI), espaciais

---

## Etapa 4: Treinamento e Validacao (CONCLUIDO)

### Scripts
- `src/models/train_module_a.py` - 9 modelos (Dummy, LR, SVM, DT, RF, LightGBM, XGBoost, LightGBM_Optuna, XGBoost_Optuna)
- `src/models/evaluate_module_a.py` - Validacao espacial (leave-one-state-out) e temporal
- `src/models/statistical_analysis.py` - Bootstrap CI (1000x), McNemar, Wilcoxon
- `src/models/predict_module_a.py` - Inferencia em novos dados
- `src/models/run_module_a_pipeline.py` - Pipeline completo
- `src/models/run_etapa4.py` - Master script

### Resultados Principais

| Modelo | Acuracia | ROC-AUC | PR-AUC |
|--------|----------|---------|--------|
| DummyClassifier | 70% | 50% | 35% |
| Regressao Logistica | 75% | 78% | 72% |
| SVM (RBF) | 77% | 80% | 74% |
| Random Forest | 79% | 83% | 78% |
| **LightGBM (proposto)** | **82%** | **86%** | **81%** |
| XGBoost | 81% | 85% | 80% |

### Validacao
- **Espacial (leave-one-state-out)**: Variacao < 4pp entre 4 estados
- **Temporal (treino 2022-2023, teste 2024)**: Degradacao ~5pp (concept drift)
- **Impacto operacional**: Reducao de 87% dos falsos positivos (recall 84%)

### Modelos Treinados
- `data/models/module_a/module_a_lightgbm.pkl`
- `data/models/module_a/module_a_xgboost.pkl`

---

## Dissertacao (QUALIFICACAO APROVADA)

### Capitulos
- Cap 1: Introducao (objetivos, justificativa, contribuicoes)
- Cap 2: Fundamentos Teoricos (sensoriamento remoto, ML, trabalhos relacionados)
- Cap 3: Metodologia (pipeline, weak labeling, features, algoritmos, validacao)
- Cap 4: Experimentos e Resultados (metricas, validacao, analise de erros, baselines)
- Cap 5: Conclusao (contribuicoes, limitacoes, proximos passos, cronograma)

### Correcoes AVALIACAO-V2 (CONCLUIDO)
Todas as 8 correcoes do orientador implementadas e marcadas em azul:
1. Titulo atualizado (sem "previsao de trajetoria")
2. Resumo/Abstract revisados (baselines, recall, leave-one-state-out)
3. Introducao (contexto operacional INPE)
4. Objetivos especificos detalhados (6 objetivos com metricas)
5. Separacao Fundamentacao vs Metodologia
6. Justificativas na Metodologia (janela +-15d, MCD64A1, LightGBM vs DL, features, classes)
7. Resultados expandidos (matriz confusao por estado, analise erros, baselines)
8. Conclusao preliminar e cronograma (Mar-Ago 2026)

### Localizacao
`Dissertacao/PPGEE-MODELO-DOUTORADO-MESTRADO-Latex-v4/`

---

## Cronograma Ate a Defesa

| Atividade | Mar | Abr | Mai | Jun | Jul | Ago |
|-----------|-----|-----|-----|-----|-----|-----|
| Refinamento do classificador | X | X | | | | |
| Ampliacao da analise de erros | X | X | | | | |
| Encadeamento espaco-temporal | | X | X | X | | |
| Avaliacao experimental propagacao | | | X | X | | |
| Consolidacao dos resultados | | | | X | X | |
| Redacao final | | | | | X | X |
| Defesa | | | | | | X |

---

## Repositorio GitHub

**URL**: https://github.com/bessa-andrey/fire-risk-prediction
**Status**: Publico, codigo aberto

---

**Ultima Atualizacao**: 12 de fevereiro de 2026
**Proxima Revisao**: Apos inicio da analise espaco-temporal
