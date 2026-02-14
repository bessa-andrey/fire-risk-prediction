# Projeto Mestrado - Indice e Navegacao

Classificacao Automatica de Focos de Incendio com Integracao de Dados Satelitais e Meteorologicos.

---

## Estrutura de Diretorios

```
Projeto Mestrado/
├── src/                           (Codigo-fonte Python)
│   ├── data_ingest/               (Etapa 1: Download)
│   ├── preprocessing/             (Etapas 2-3: Processamento + Features)
│   ├── models/                    (Etapa 4: ML + Validacao)
│   └── visualization/             (Mapas)
├── data/                          (Dados brutos, processados, modelos)
├── Dissertacao/                   (LaTeX da dissertacao)
├── docs/                          (Documentacao tecnica)
├── root/                          (Documentacao raiz - este diretorio)
└── obsoleto/                      (Arquivos descontinuados)
```

---

## Documentacao Raiz (root/)

| Arquivo | Descricao |
|---------|-----------|
| README.md | Visao geral e inicio rapido |
| INDEX.md | Este indice |
| CLAUDE.md | Guia para Claude Code |
| STATUS_PROJETO.md | Status atual do projeto |
| PROJETO_SETUP.md | Definicao e configuracao do projeto |
| ESTRUTURA_PROJETO.md | Arvore completa de arquivos |

---

## Executar o Pipeline

### Etapa 1: Ingestao de Dados
Guia: `docs/etapas/ETAPA1_INGESTAO.md`
```bash
python src/data_ingest/run_all_downloads.py
```

### Etapa 2: Processamento
Guia: `docs/etapas/ETAPA2_PROCESSAMENTO.md`
```bash
python src/preprocessing/run_all_preprocessing.py
```

### Etapa 3: Feature Engineering + Weak Labeling
Guia: `docs/etapas/ETAPA3_FEATURE_ENGINEERING.md`
```bash
python src/preprocessing/run_etapa3.py
```

### Etapa 4: Treinamento + Validacao
Guia: `docs/etapas/ETAPA4_VALIDACAO.md`
```bash
python src/models/run_etapa4.py
```

---

## Usar Modulo A (Inferencia)

Classificar novos focos de incendio como reais ou espurios:

```bash
python src/models/predict_module_a.py --input novos_focos.csv
```

Documentacao: `docs/modulos/MODULO_A_INFERENCIA.md`
Quick start: `docs/modulos/MODULO_A_QUICK_START.txt`

---

## Analise Estatistica

```bash
python src/models/statistical_analysis.py
```

Inclui: Bootstrap CI (1000 reamostras), teste de McNemar, teste de Wilcoxon.

---

## Codigo-fonte (src/)

### data_ingest/ - Download de dados
| Script | Funcao |
|--------|--------|
| download_firms.py | Focos de incendio (API FIRMS) |
| download_mcd64a1.py | Area queimada (NASA) |
| download_sentinel2.py | Imagens opticas (ESA) |
| download_era5.py | Meteorologia (CDS/ECMWF) |
| run_all_downloads.py | Master script |

### preprocessing/ - Processamento e features
| Script | Funcao |
|--------|--------|
| process_firms.py | Limpeza, filtragem, persistencia |
| process_mcd64a1.py | Mosaico, reprojecao, GeoTIFF |
| process_sentinel2.py | NDVI, cloud masking |
| process_era5.py | Interpolacao espacial/temporal |
| weak_labeling.py | Rotulagem FIRMS vs MCD64A1 (+-15 dias) |
| feature_engineering.py | Extracao de 20+ features |
| validate_weak_labels.py | Validacao Cohen's Kappa (200 amostras) |
| data_loader.py | Carregamento unificado |
| run_etapa3.py | Master script |

### models/ - Treinamento e validacao
| Script | Funcao |
|--------|--------|
| train_module_a.py | 9 modelos (Dummy, LR, SVM, DT, RF, LightGBM, XGBoost + Optuna) |
| evaluate_module_a.py | Validacao espacial e temporal |
| statistical_analysis.py | Bootstrap, McNemar, Wilcoxon |
| predict_module_a.py | Inferencia em novos dados |
| run_module_a_pipeline.py | Pipeline completo |
| run_etapa4.py | Master script |

### visualization/ - Mapas
| Script | Funcao |
|--------|--------|
| generate_matopiba_map_v2.py | Mapa da regiao MATOPIBA |
| map_hotspots.py | Mapa interativo de focos |

---

## Documentacao Tecnica (docs/)

### Configuracao
| Arquivo | Descricao |
|---------|-----------|
| docs/setup/SETUP_AMBIENTE.md | Configuracao completa do ambiente |
| docs/setup/SETUP_COMPLETO.md | Checklist de configuracao |

### Etapas do Pipeline
| Arquivo | Descricao |
|---------|-----------|
| docs/etapas/ETAPA1_INGESTAO.md | Guia da Etapa 1 |
| docs/etapas/ETAPA2_PROCESSAMENTO.md | Guia da Etapa 2 |
| docs/etapas/ETAPA3_FEATURE_ENGINEERING.md | Guia da Etapa 3 |
| docs/etapas/ETAPA4_VALIDACAO.md | Guia da Etapa 4 |

### Modulo A
| Arquivo | Descricao |
|---------|-----------|
| docs/modulos/MODULO_A_INFERENCIA.md | Documentacao completa |
| docs/modulos/MODULO_A_QUICK_START.txt | Inicio rapido |

### Visualizacoes
| Arquivo | Descricao |
|---------|-----------|
| docs/visual/demo_modulo_a.ipynb | Jupyter notebook com graficos |
| docs/visual/*.png | Graficos do projeto |

---

## Dissertacao

Localizada em `Dissertacao/PPGEE-MODELO-DOUTORADO-MESTRADO-Latex-v4/capitulos/`:

| Capitulo | Conteudo |
|----------|---------|
| 0-capa_n_contra.tex | Capa, resumo (PT/EN), agradecimentos |
| 1-introducao.tex | Problema, objetivos, justificativa, contribuicoes |
| 2-fundamentos.tex | Sensoriamento remoto, ML, trabalhos relacionados |
| 3-metodologia.tex | Pipeline, weak labeling, features, algoritmos, validacao |
| 4-experimentos.tex | Resultados, validacao, analise erros, baselines |
| 5-conclusao.tex | Conclusoes, limitacoes, proximos passos, cronograma |

---

## Referencia Rapida

| Necessidade | Arquivo |
|-------------|---------|
| Visao geral | root/README.md |
| Status atual | root/STATUS_PROJETO.md |
| Configurar ambiente | docs/setup/SETUP_AMBIENTE.md |
| Executar pipeline | docs/etapas/ETAPA1-4 |
| Usar Modulo A | docs/modulos/MODULO_A_INFERENCIA.md |
| Dissertacao | Dissertacao/.../capitulos/ |

---

**Ultima atualizacao**: 12 de fevereiro de 2026
