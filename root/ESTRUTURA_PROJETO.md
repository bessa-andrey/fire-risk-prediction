# Estrutura do Projeto - Dissertacao de Mestrado

Projeto: Classificacao Automatica de Focos de Incendio com Integracao de Dados Satelitais e Meteorologicos

---

## Estrutura de Diretorios

```
Projeto Mestrado/
│
├── root/                              (Documentacao raiz)
│   ├── README.md                      (Visao geral do projeto)
│   ├── INDEX.md                       (Indice completo)
│   ├── CLAUDE.md                      (Guia para Claude Code)
│   ├── PROJETO_SETUP.md               (Definicao do projeto)
│   ├── STATUS_PROJETO.md              (Status atual)
│   └── ESTRUTURA_PROJETO.md           (Este arquivo)
│
├── src/                               (Codigo-fonte)
│   ├── data_ingest/                   (Etapa 1: Download de dados)
│   │   ├── download_firms.py
│   │   ├── download_mcd64a1.py
│   │   ├── download_mcd64a1_appeears.py
│   │   ├── download_sentinel2.py
│   │   ├── download_sentinel2_pc.py
│   │   ├── download_era5.py
│   │   ├── download_era5_cds.py
│   │   ├── check_mcd64a1.py
│   │   └── run_all_downloads.py
│   │
│   ├── preprocessing/                 (Etapas 2-3: Processamento + Features)
│   │   ├── process_firms.py
│   │   ├── process_mcd64a1.py
│   │   ├── process_sentinel2.py
│   │   ├── process_era5.py
│   │   ├── data_loader.py
│   │   ├── run_all_preprocessing.py
│   │   ├── weak_labeling.py
│   │   ├── feature_engineering.py
│   │   ├── validate_weak_labels.py
│   │   └── run_etapa3.py
│   │
│   ├── models/                        (Etapa 4: ML + Validacao)
│   │   ├── train_module_a.py          (9 modelos + Optuna)
│   │   ├── evaluate_module_a.py       (Validacao espacial/temporal)
│   │   ├── statistical_analysis.py    (Bootstrap, McNemar, Wilcoxon)
│   │   ├── predict_module_a.py        (Inferencia)
│   │   ├── run_module_a_pipeline.py   (Pipeline completo)
│   │   ├── run_etapa4.py              (Master script)
│   │   ├── demo_module_a.py           (Demo)
│   │   └── test_realtime.py           (Teste tempo real)
│   │
│   └── visualization/                 (Mapas e graficos)
│       ├── generate_matopiba_map_v2.py
│       └── map_hotspots.py
│
├── data/                              (Dados - gitignored)
│   ├── raw/                           (Downloads originais)
│   │   ├── firms/
│   │   ├── mcd64a1/
│   │   ├── sentinel2/
│   │   └── era5/
│   ├── processed/                     (Dados processados)
│   │   ├── firms/
│   │   ├── burned_area/
│   │   ├── mcd64a1/
│   │   ├── sentinel2/
│   │   ├── era5/
│   │   └── training/                  (Datasets ML)
│   │       ├── module_a_balanced.csv   (9.198 amostras)
│   │       ├── module_a_dataset.csv
│   │       └── module_a_full.csv
│   └── models/                        (Modelos treinados)
│       └── module_a/
│           ├── module_a_lightgbm.pkl
│           ├── module_a_xgboost.pkl
│           └── scaler.pkl
│
├── Dissertacao/                       (Dissertacao de Mestrado)
│   ├── AVALIACAO-V2.docx              (Feedback do orientador)
│   ├── PPGEE-MODELO-DOUTORADO-MESTRADO-Latex-v4/
│   │   └── capitulos/
│   │       ├── 0-capa_n_contra.tex
│   │       ├── 1-introducao.tex
│   │       ├── 2-fundamentos.tex
│   │       ├── 3-metodologia.tex
│   │       ├── 4-experimentos.tex
│   │       └── 5-conclusao.tex
│   └── journal-paper-workspace/       (Workspace para artigo)
│
├── docs/                              (Documentacao tecnica)
│   ├── setup/                         (Configuracao ambiente)
│   │   ├── SETUP_AMBIENTE.md
│   │   └── SETUP_COMPLETO.md
│   ├── etapas/                        (Guias por etapa do pipeline)
│   │   ├── ETAPA1_INGESTAO.md
│   │   ├── ETAPA2_PROCESSAMENTO.md
│   │   ├── ETAPA3_FEATURE_ENGINEERING.md
│   │   ├── ETAPA4_VALIDACAO.md
│   │   └── CHANGELOG_*.md
│   ├── modulos/                       (Documentacao do Modulo A)
│   │   ├── MODULO_A_INFERENCIA.md
│   │   └── MODULO_A_QUICK_START.txt
│   ├── visual/                        (Graficos, demos, visualizacoes)
│   │   ├── *.png (graficos)
│   │   ├── demo_modulo_a.ipynb
│   │   └── guias visuais (.txt, .md)
│   └── README-fire-open-data-pipeline.md
│
├── obsoleto/                          (Arquivos movidos - nao mais usados)
│   ├── scripts_apresentacao/          (6 scripts Python de slides)
│   ├── scripts_teste/                 (3 scripts de teste de conexao)
│   ├── docs_setup/                    (4 docs de setup supersedidos)
│   ├── docs_guias/                    (5 docs/guias incorporados)
│   ├── mapas_html/                    (16 mapas interativos antigos)
│   └── diversos/                      (4 arquivos diversos)
│
├── artigos/                           (Artigos de referencia)
├── logos/                             (Logos UFAM/PPGEE)
├── Reunioes/                          (Atas de reunioes)
├── CONCEITOS_ESSENCIAIS.md            (Referencia de estudo)
├── README.md                          (README GitHub)
└── requirements.txt                   (Dependencias Python)
```

---

## Contagem de Arquivos

| Categoria | Quantidade | Status |
|-----------|-----------|--------|
| src/data_ingest/ | 9 | Concluido |
| src/preprocessing/ | 10 | Concluido |
| src/models/ | 8 | Concluido |
| src/visualization/ | 2 | Concluido |
| **Total src/** | **29** | - |
| docs/setup/ | 2 | Concluido |
| docs/etapas/ | 10 | Concluido |
| docs/modulos/ | 2 | Concluido |
| docs/visual/ | 11 | Concluido |
| **Total docs/** | **26** | - |
| root/ | 6 | Concluido |
| Dissertacao (capitulos) | 6 | Concluido |

---

## Fluxo de Navegacao

### Primeiro acesso:
1. `root/README.md` - Visao geral
2. `root/STATUS_PROJETO.md` - Onde estamos
3. `root/CLAUDE.md` - Guia tecnico

### Para executar o pipeline:
1. `docs/setup/SETUP_AMBIENTE.md` - Configurar ambiente
2. `docs/etapas/ETAPA1_INGESTAO.md` a `ETAPA4_VALIDACAO.md` - Seguir etapas

### Para a dissertacao:
1. `Dissertacao/PPGEE-MODELO-.../capitulos/` - LaTeX
2. `Dissertacao/AVALIACAO-V2.docx` - Feedback do orientador

---

**Ultima atualizacao**: 12 de fevereiro de 2026
