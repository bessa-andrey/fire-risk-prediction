# Estrutura do Projeto - Dissertacao de Mestrado

Projeto: Machine Learning para Deteccao e Propagacao de Fogo em MATOPIBA

Organizacao profissional e hierarquica dos arquivos e diretorios.

---

## Estrutura de Diretorios

```
Projeto Mestrado/
│
├── root/                          (Documentacao raiz - 6 arquivos)
│   ├── README.md                  (Visao geral do projeto)
│   ├── INDEX.md                   (Indice completo)
│   ├── CLAUDE.md                  (Guia para Claude Code)
│   ├── PROJETO_SETUP.md           (Definicao do projeto)
│   ├── STATUS_PROJETO.md          (Status atual)
│   └── ARQUIVOS_DESCONTINUADOS.md (Arquivos nao usados)
│
├── docs/                          (Toda documentacao - 40+ arquivos)
│   │
│   ├── setup/                     (Configuracao ambiente - 6 arquivos)
│   │   ├── SETUP_AMBIENTE.md
│   │   ├── SETUP_COMPLETO.md
│   │   ├── CREDENCIAIS_SETUP.md
│   │   ├── EARTHDATA_SETUP.md
│   │   ├── CDS_SETUP.md
│   │   └── GEE_SETUP_DETALHADO.md
│   │
│   ├── etapas/                    (Pipeline Etapas 1-4 - 10 arquivos)
│   │   ├── ETAPA1_INGESTAO.md
│   │   ├── ETAPA2_PROCESSAMENTO.md
│   │   ├── ETAPA3_FEATURE_ENGINEERING.md
│   │   ├── ETAPA4_VALIDACAO.md
│   │   ├── CHANGELOG_ETAPA2.md
│   │   ├── CHANGELOG_ETAPA3.md
│   │   ├── CHANGELOG_MODULO_A_INFERENCIA.md
│   │   └── [Outros arquivos etapas]
│   │
│   ├── modulos/                   (Documentacao Modulos A, B - 4 arquivos)
│   │   ├── MODULO_A_INFERENCIA.md
│   │   ├── MODULO_A_QUICK_START.txt
│   │   ├── MODULO_B_PROPAGACAO.md (FUTURO)
│   │   └── MODULO_B_QUICK_START.txt (FUTURO)
│   │
│   ├── visual/                    (Graficos e demos - 4 arquivos)
│   │   ├── LEIA-ME-VISUAL.txt
│   │   ├── VISUAL_GUIDE_MODULO_A.md
│   │   ├── RESUMO_VISUAL_MODULO_A.txt
│   │   └── demo_modulo_a.ipynb
│   │
│   ├── guia/                      (Guias estrategicos - 3 arquivos)
│   │   ├── ANALISE_MELHORIAS.txt
│   │   ├── CHECKLIST_FINALIZACAO.md (NOVO)
│   │   └── TIMELINE_5_SEMANAS.md (NOVO)
│   │
│   ├── conceptos/                 (Explicacoes conceituais - 3 arquivos)
│   │   ├── RESUMO_EXPLICACOES.txt
│   │   ├── EXEMPLOS_PRATICOS.txt
│   │   └── WEAK_LABELING_DEEP_DIVE.md (NOVO)
│   │
│   ├── apresentacao/              (PPTX e conteudo - 2 arquivos)
│   │   ├── CONTEUDO_PPTX_MELHORADO.md
│   │   └── Finalizando_o_Projeto.pptx
│   │
│   └── recursos/                  (Documentos externos - 1 arquivo)
│       └── README-fire-open-data-pipeline.md
│
├── src/                           (Codigo-fonte)
│   │
│   ├── preprocessing/             (Scripts Etapas 1-3)
│   │   ├── run_all_preprocessing.py
│   │   ├── run_etapa2.py
│   │   ├── run_etapa3.py
│   │   ├── process_firms.py
│   │   ├── process_mcd64a1.py
│   │   ├── process_sentinel2.py
│   │   ├── process_era5.py
│   │   ├── data_loader.py
│   │   ├── weak_labeling.py
│   │   └── feature_engineering.py
│   │
│   ├── models/                    (Scripts Etapas 3-4 + Modulos A, B)
│   │   ├── train_module_a.py
│   │   ├── evaluate_module_a.py
│   │   ├── predict_module_a.py (PRODUCAO)
│   │   ├── run_module_a_pipeline.py (ORQUESTRACAO)
│   │   ├── run_etapa4.py
│   │   ├── train_module_b.py (FUTURO)
│   │   ├── predict_module_b.py (FUTURO)
│   │   └── run_integrated_pipeline.py (FUTURO)
│   │
│   ├── propagation/               (Modulo B - futuro)
│   │   ├── grid_creator.py (FUTURO)
│   │   ├── propagation_features.py (FUTURO)
│   │   └── propagation_validator.py (FUTURO)
│   │
│   ├── tests/                     (Testes automatizados - FUTURO)
│   │   ├── test_feature_engineering.py
│   │   ├── test_models.py
│   │   └── test_inference.py
│   │
│   ├── utils/                     (Utilitarios comuns)
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── geo_utils.py
│   │
│   ├── scripts_dev/               (Scripts de desenvolvimento/teste)
│   │   ├── create_presentation.py
│   │   ├── test_cds.py
│   │   ├── test_earthdata.py
│   │   └── test_gee_fixed.py
│   │
│   └── notebooks/                 (Jupyter notebooks educacionais)
│       ├── demo_modulo_a.ipynb
│       ├── demo_modulo_b.ipynb (FUTURO)
│       └── exploratory_analysis.ipynb (FUTURO)
│
├── data/                          (Dados - .gitignored)
│   │
│   ├── raw/                       (Downloads originais - GRANDES)
│   │   ├── firms/
│   │   ├── mcd64a1/
│   │   ├── sentinel2/
│   │   └── era5/
│   │
│   ├── processed/                 (Dados processados)
│   │   ├── module_a/
│   │   │   ├── features_train.csv
│   │   │   ├── labels.csv
│   │   │   └── features_test.csv
│   │   │
│   │   └── module_b/
│   │       ├── grid_features.tif
│   │       └── grid_labels.tif
│   │
│   └── models/                    (Modelos treinados)
│       ├── module_a/
│       │   ├── model_lightgbm.pkl
│       │   ├── model_xgboost.pkl
│       │   ├── feature_names.pkl
│       │   └── scaler.pkl
│       │
│       └── module_b/
│           ├── model_propagation.pkl
│           └── feature_names_b.pkl
│
├── results/                       (Resultados e saidas)
│   │
│   ├── validacao/                 (Metricas e relatorios)
│   │   ├── RELATORIO_VALIDACAO_FINAL.pdf (FUTURO)
│   │   ├── confusion_matrix.csv
│   │   ├── metrics.json
│   │   └── validation_plots/
│   │
│   ├── predicoes/                 (Outputs de predicao)
│   │   ├── predictions_module_a.csv
│   │   └── predictions_module_b.tif
│   │
│   └── graficos/                  (Graficos finais tese)
│       ├── figura_01_overview.png
│       ├── figura_02_validacao.png
│       └── [Outros graficos]
│
├── .gitignore                     (Ignorar arquivos grandes)
├── requirements.txt               (Dependencias Python)
├── environment.yml                (Ambiente Conda)
└── setup.py                       (Setup para instalacao)

```

---

## Contagem de Arquivos por Categoria

| Categoria | Quantidade | Status |
|-----------|-----------|--------|
| root/ | 6 | Completo |
| docs/setup | 6 | Completo |
| docs/etapas | 10 | Completo |
| docs/modulos | 2 | Parcial (B falta) |
| docs/visual | 4 | Completo |
| docs/guia | 2 | Novo |
| docs/conceptos | 2 | Novo |
| docs/apresentacao | 2 | Novo (PPTX criado) |
| docs/recursos | 1 | Completo |
| **Total docs** | **29** | - |
| src/preprocessing | 10 | Ja existia |
| src/models | 7 | Parcial |
| src/propagation | 0 | Futuro |
| src/tests | 0 | Futuro |
| src/utils | 3 | Basico |
| src/scripts_dev | 4 | Novo |
| src/notebooks | 1 | Novo |
| **Total src** | **25** | - |
| data/ | Variavel | Gitignored |
| results/ | Variavel | Novo |

**Total arquivos documentacao: 34 arquivos**

---

## Fluxo de Navegacao Recomendado

### Para Primeiro Acesso:
1. Leia: `root/README.md`
2. Entenda: `root/CLAUDE.md`
3. Explore: `root/INDEX.md`

### Para Setup:
1. Consulte: `docs/setup/SETUP_AMBIENTE.md`
2. Siga: `docs/setup/SETUP_COMPLETO.md`

### Para Entender Conceitos:
1. Leia: `docs/conceptos/RESUMO_EXPLICACOES.txt`
2. Estude: `docs/conceptos/EXEMPLOS_PRATICOS.txt`
3. Approfunde: `docs/guia/ANALISE_MELHORIAS.txt`

### Para Executar Pipeline:
1. Etapa 1: `docs/etapas/ETAPA1_INGESTAO.md`
2. Etapa 2: `docs/etapas/ETAPA2_PROCESSAMENTO.md`
3. Etapa 3: `docs/etapas/ETAPA3_FEATURE_ENGINEERING.md`
4. Etapa 4: `docs/etapas/ETAPA4_VALIDACAO.md`

### Para Usar Modulo A:
1. Quick Start: `docs/modulos/MODULO_A_QUICK_START.txt`
2. Detalhado: `docs/modulos/MODULO_A_INFERENCIA.md`
3. Visual: `docs/visual/LEIA-ME-VISUAL.txt`
4. Demo: `docs/visual/demo_modulo_a.ipynb`

### Para Apresentacao:
1. Conteudo: `docs/apresentacao/CONTEUDO_PPTX_MELHORADO.md`
2. PPTX: `docs/apresentacao/Finalizando_o_Projeto.pptx`

### Para Finalizacao (Proximas 5 Semanas):
1. Timeline: `docs/guia/TIMELINE_5_SEMANAS.md` (NOVO)
2. Checklist: `docs/guia/CHECKLIST_FINALIZACAO.md` (NOVO)
3. Melhorias: `docs/guia/ANALISE_MELHORIAS.txt`

---

## Principios de Organizacao

### 1. Estrutura Limpa
- **root/**: Apenas documentacao raiz (README, INDEX, STATUS)
- **docs/**: Toda documentacao organizada por topico
- **src/**: Codigo organizado por funcionalidade
- **data/**: Dados grandes (gitignored)
- **results/**: Outputs e resultados

### 2. Nomes Claros
- Maiusculas: Arquivos principais (README, INDEX, CLAUDE)
- Underscores: Arquivos descritivos (SETUP_AMBIENTE, ETAPA1_INGESTAO)
- Lowercase: Scripts Python (train_module_a.py, process_firms.py)

### 3. Subdiretorios Logicos
- **setup/**: Configuracao inicial
- **etapas/**: Pipeline stages
- **modulos/**: Sistemas principais (A, B)
- **visual/**: Graficos e demos
- **guia/**: Estrategia e planejamento
- **conceptos/**: Explicacoes teoricas
- **apresentacao/**: Slides e PPTX
- **recursos/**: Documentos externos

### 4. Hierarquia Profissional
- Nivel 0: Raiz (root/)
- Nivel 1: Categorias (setup, etapas, modulos, etc)
- Nivel 2: Arquivos especificos
- Nivel 3: Dados/resultados (data/, results/)

---

## Como Adicionar Novos Arquivos

**Novo doc de setup?** -> `docs/setup/`
**Novo guide/tutorial?** -> `docs/guia/`
**Novo conceito explicado?** -> `docs/conceptos/`
**Novo codigo pipeline?** -> `src/preprocessing/` ou `src/models/`
**Novo modelo?** -> `data/models/`
**Novo resultado?** -> `results/`
**Nova figura tese?** -> `results/graficos/`

---

## Status de Completude

| Modulo | Status | % Completo |
|--------|--------|-----------|
| Modulo A (Deteccao) | COMPLETO | 100% |
| Modulo B (Propagacao) | PLANEJADO | 0% |
| Documentacao | ESTRUTURADA | 85% |
| Apresentacao | PRONTA | 100% |
| Tese | PLANEJADA | 0% |
| **TOTAL PROJETO** | **75% Completo** | - |

---

**Ultima atualizacao**: 11 de Novembro de 2025
**Estrutura**: Profissional, escalavel e bem organizada
**Proxima revisao**: Apos conclusao Modulo B
