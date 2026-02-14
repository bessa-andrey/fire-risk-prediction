# CLAUDE.md - Guia para Claude Code

Arquivo de orientacao para Claude Code ao trabalhar com este repositorio.

**IMPORTANTE**: Sem emojis em scripts. Manter codigo limpo e profissional.

---

## Projeto

**Titulo**: Classificacao Automatica de Focos de Incendio com Integracao de Dados Satelitais e Meteorologicos

**Tipo**: Dissertacao de Mestrado em Engenharia Eletrica (PPGEE)

**Instituicao**: Universidade Federal do Amazonas (UFAM)

**Autor**: Andrey Ruben Ribeiro Bessa

**Orientador**: Prof. D.Sc. Celso Barbosa Carvalho

**Coorientador**: Prof. D.Sc. Andre Chaves Mendes

**Status**: Pipeline de classificacao 100% concluido. Qualificacao aprovada. Proxima fase: analise espaco-temporal.

**Defesa prevista**: Agosto de 2026

**Repositorio**: https://github.com/bessa-andrey/fire-risk-prediction

---

## O que o Projeto Faz

Sistema de Machine Learning para classificar focos de incendio do FIRMS (NASA) como reais ou espurios (falsos positivos), utilizando integracao de 4 fontes de dados geoespaciais na regiao MATOPIBA (MA, TO, PI, BA), periodo 2022-2024.

### Pipeline em 4 Etapas
1. **Ingestao**: Download automatizado de FIRMS, MCD64A1, Sentinel-2, ERA5
2. **Processamento**: Limpeza, reprojecao, mosaico, interpolacao
3. **Feature Engineering**: Weak labeling (FIRMS vs MCD64A1, +-15 dias) + extracao de 20+ features
4. **Modelagem**: 9 modelos (Dummy, LR, SVM, DT, RF, LightGBM, XGBoost + versoes Optuna)

### Resultados
- **LightGBM**: 82% acuracia, 86% ROC-AUC, 81% PR-AUC
- **Dataset**: 9.198 amostras balanceadas (4.599/4.599)
- **Validacao**: leave-one-state-out (espacial) + treino 2022-2023/teste 2024 (temporal)
- **Impacto operacional**: 87% reducao de falsos positivos (recall 84%)

---

## Estrutura do Projeto

```
Projeto Mestrado/
├── src/
│   ├── data_ingest/          # Etapa 1: Download de dados
│   ├── preprocessing/        # Etapas 2-3: Processamento + features
│   ├── models/               # Etapa 4: Treinamento + validacao + analise
│   └── visualization/        # Mapas e visualizacoes
├── data/
│   ├── raw/                  # Dados brutos (gitignored)
│   ├── processed/            # Dados processados
│   │   └── training/         # Datasets para ML
│   └── models/               # Modelos treinados (.pkl)
├── Dissertacao/              # LaTeX da dissertacao
│   └── PPGEE-MODELO-.../     # Template UFAM
│       └── capitulos/        # Cap 0-5
├── docs/                     # Documentacao
│   ├── setup/                # Configuracao ambiente
│   ├── etapas/               # Guias por etapa
│   ├── modulos/              # Documentacao Modulo A
│   └── visual/               # Graficos e demos
├── root/                     # Documentacao raiz (este diretorio)
├── obsoleto/                 # Arquivos movidos (nao mais usados)
└── requirements.txt
```

---

## Scripts Principais

### Ingestao (src/data_ingest/)
- `download_firms.py` - API FIRMS
- `download_mcd64a1.py` - Tiles MCD64A1
- `download_sentinel2.py` - Imagens Sentinel-2
- `download_era5.py` - Dados ERA5 via CDS
- `run_all_downloads.py` - Master script

### Processamento (src/preprocessing/)
- `process_firms.py` - Filtragem, persistencia
- `process_mcd64a1.py` - Mosaico, reprojecao
- `process_sentinel2.py` - NDVI, cloud masking
- `process_era5.py` - Interpolacao espacial/temporal
- `weak_labeling.py` - Rotulagem FIRMS vs MCD64A1
- `feature_engineering.py` - Extracao de features
- `validate_weak_labels.py` - Validacao Cohen's Kappa
- `data_loader.py` - Carregamento unificado

### Modelos (src/models/)
- `train_module_a.py` - Treinamento de 9 modelos (inclui Optuna 100 trials)
- `evaluate_module_a.py` - Validacao espacial e temporal
- `statistical_analysis.py` - Bootstrap CI, McNemar, Wilcoxon
- `predict_module_a.py` - Inferencia em novos dados
- `run_module_a_pipeline.py` - Pipeline completo

### Visualizacao (src/visualization/)
- `generate_matopiba_map_v2.py` - Mapa da regiao MATOPIBA
- `map_hotspots.py` - Mapa interativo de focos

---

## Dissertacao LaTeX

Localizada em `Dissertacao/PPGEE-MODELO-DOUTORADO-MESTRADO-Latex-v4/capitulos/`:
- `0-capa_n_contra.tex` - Capa, resumo, abstract
- `1-introducao.tex` - Introducao, objetivos, justificativa
- `2-fundamentos.tex` - Fundamentos teoricos, trabalhos relacionados
- `3-metodologia.tex` - Pipeline, weak labeling, features, algoritmos
- `4-experimentos.tex` - Resultados, validacao, analise de erros, baselines
- `5-conclusao.tex` - Conclusoes, limitacoes, proximos passos, cronograma

**Convencao**: Alteracoes da AVALIACAO-V2 estao marcadas com `{\color{blue} ...}`

---

## Tecnologias

| Categoria | Ferramentas |
|-----------|------------|
| Geoespacial | geopandas, rasterio, rioxarray, shapely, pyproj, xarray |
| ML | scikit-learn, lightgbm, xgboost, optuna |
| Analise | pandas, numpy, scipy |
| Visualizacao | matplotlib, folium |
| Dados externos | Google Earth Engine, NASA Earthdata, Copernicus CDS |

---

## Execucao Rapida

```bash
# Pipeline completo
python src/data_ingest/run_all_downloads.py
python src/preprocessing/run_all_preprocessing.py
python src/preprocessing/run_etapa3.py
python src/models/run_etapa4.py

# Inferencia em novos dados
python src/models/predict_module_a.py --input novos_focos.csv

# Analise estatistica
python src/models/statistical_analysis.py
```

---

## Proximos Passos (cronograma Mar-Ago 2026)

1. Refinamento do classificador e ampliacao da analise de erros (Mar-Abr)
2. Encadeamento espaco-temporal dos focos reais (Abr-Jun)
3. Avaliacao experimental de propagacao D+1 (Mai-Jun)
4. Consolidacao dos resultados (Jun-Jul)
5. Redacao final e defesa (Jul-Ago)

---

**Ultima Atualizacao**: 12 de fevereiro de 2026
