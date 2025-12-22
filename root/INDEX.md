# Projeto Mestrado - Índice e Navegação

Estrutura organizada do projeto de Machine Learning para detecção e propagação de fogo em MATOPIBA.

---

## Estrutura de Diretórios

```
Projeto Mestrado/
├── docs/                          (Toda documentação)
│   ├── setup/                     (Configuração do ambiente)
│   ├── etapas/                    (Fases 1-4 do pipeline)
│   ├── modulos/                   (Módulo A, B, etc)
│   └── visual/                    (Guias visuais e demos)
├── src/                           (Código-fonte)
│   ├── preprocessing/             (Etapas 1-2)
│   ├── models/                    (Etapas 3-4, Módulo A)
│   └── propagation/               (Módulo B - futuro)
├── data/                          (Dados)
│   ├── raw/                       (Downloads)
│   ├── processed/                 (Processado)
│   └── models/                    (Modelos treinados)
└── INDEX.md                       (Este arquivo)
```

---

## Como Começar

### 1. Configuração do Ambiente
Comece aqui se for a primeira execução:

- [SETUP_AMBIENTE.md](docs/setup/SETUP_AMBIENTE.md) - Guia completo de setup
- [SETUP_COMPLETO.md](docs/setup/SETUP_COMPLETO.md) - Checklist de configuração
- [CREDENCIAIS_SETUP.md](docs/setup/CREDENCIAIS_SETUP.md) - APIs e credenciais

### 2. Entender o Projeto
Visão geral do projeto:

- [PROJETO_SETUP.md](PROJETO_SETUP.md) - Definição geral do projeto
- [STATUS_PROJETO.md](STATUS_PROJETO.md) - Status atual e progresso
- [CLAUDE.md](CLAUDE.md) - Guia para Claude Code

### 3. Executar as Etapas (Sequencial)

#### Etapa 1: Ingestão de Dados
[docs/etapas/ETAPA1_INGESTAO.md](docs/etapas/ETAPA1_INGESTAO.md)

Baixa dados de múltiplas fontes (FIRMS, MCD64A1, Sentinel-2, ERA5)

```bash
python src/preprocessing/run_all_preprocessing.py
```

#### Etapa 2: Processamento
[docs/etapas/ETAPA2_PROCESSAMENTO.md](docs/etapas/ETAPA2_PROCESSAMENTO.md)

Processa e limpa dados crus

```bash
python src/preprocessing/run_etapa2.py
```

#### Etapa 3: Feature Engineering + Training
[docs/etapas/ETAPA3_FEATURE_ENGINEERING.md](docs/etapas/ETAPA3_FEATURE_ENGINEERING.md)

Cria features e treina modelos (com GPU se disponível)

```bash
python src/preprocessing/run_etapa3.py
```

#### Etapa 4: Validação
[docs/etapas/ETAPA4_VALIDACAO.md](docs/etapas/ETAPA4_VALIDACAO.md)

Valida modelos (espacial, temporal, confiança)

```bash
python src/models/run_etapa4.py
```

---

## Módulo A: Identificação de Áreas Espúrias

Sistema completo de detecção de hotspots falsos em produção.

### Documentação
- [docs/modulos/MODULO_A_INFERENCIA.md](docs/modulos/MODULO_A_INFERENCIA.md) - Guia técnico
- [docs/modulos/MODULO_A_QUICK_START.txt](docs/modulos/MODULO_A_QUICK_START.txt) - Quick start

### Usar em Produção
```bash
python src/models/predict_module_a.py --input seus_hotspots.csv
```

### Visualizar Sistema
Veja como funciona visualmente:

- [docs/visual/LEIA-ME-VISUAL.txt](docs/visual/LEIA-ME-VISUAL.txt) - Guia visual rápido
- [docs/visual/VISUAL_GUIDE_MODULO_A.md](docs/visual/VISUAL_GUIDE_MODULO_A.md) - Guia visual detalhado
- [docs/visual/RESUMO_VISUAL_MODULO_A.txt](docs/visual/RESUMO_VISUAL_MODULO_A.txt) - Resumo visual
- [docs/visual/demo_modulo_a.ipynb](docs/visual/demo_modulo_a.ipynb) - Jupyter com gráficos

Execute o notebook:
```bash
jupyter lab docs/visual/demo_modulo_a.ipynb
```

---

## Changelogs

Histórico de mudanças por etapa:

- [docs/etapas/CHANGELOG_ETAPA2.md](docs/etapas/CHANGELOG_ETAPA2.md) - Etapa 2
- [docs/etapas/CHANGELOG_ETAPA3.md](docs/etapas/CHANGELOG_ETAPA3.md) - Etapa 3
- [docs/etapas/CHANGELOG_MODULO_A_INFERENCIA.md](docs/etapas/CHANGELOG_MODULO_A_INFERENCIA.md) - Módulo A

---

## Estrutura de Código

### src/preprocessing/
Scripts de Etapas 1-2 (ingestão e processamento)

- `run_all_preprocessing.py` - Master script
- `process_firms.py` - Processa hotspots FIRMS
- `process_mcd64a1.py` - Processa área queimada
- `process_sentinel2.py` - Processa vegetação
- `process_era5.py` - Processa meteorologia
- `data_loader.py` - Carregador de dados
- `weak_labeling.py` - Geração de labels
- `feature_engineering.py` - Extração de features
- `run_etapa3.py` - Master script Etapa 3

### src/models/
Scripts de Etapas 3-4 (ML e validação)

- `train_module_a.py` - Treinamento de modelos
- `evaluate_module_a.py` - Validação espacial/temporal
- `predict_module_a.py` - Inferência em novos dados
- `run_etapa4.py` - Master script Etapa 4
- `run_module_a_pipeline.py` - Pipeline completo

### data/
Estrutura de dados

- `raw/` - Dados brutos (downloads)
- `processed/` - Dados processados
  - `module_a/` - Features e labels
  - `module_b/` - Grid features
- `models/` - Modelos treinados
  - `module_a/` - Modelos, validação, predições

---

## Próximas Ações

### Imediato
1. Setup completo: `docs/setup/SETUP_AMBIENTE.md`
2. Entender projeto: `PROJETO_SETUP.md`
3. Executar Etapa 1: `docs/etapas/ETAPA1_INGESTAO.md`

### Curto Prazo
1. Executar Etapas 2-4 em sequência
2. Visualizar Módulo A: `docs/visual/demo_modulo_a.ipynb`
3. Usar em produção: `python src/models/predict_module_a.py --input dados.csv`

### Longo Prazo
1. Módulo B (propagação D+1)
2. Integração de módulos
3. Escrita de tese

---

## Referência Rápida

| Necessidade | Arquivo |
|-----------|---------|
| Setup inicial | docs/setup/SETUP_AMBIENTE.md |
| Visão geral | PROJETO_SETUP.md |
| Status | STATUS_PROJETO.md |
| Guia Claude | CLAUDE.md |
| Etapa 1 | docs/etapas/ETAPA1_INGESTAO.md |
| Etapa 2 | docs/etapas/ETAPA2_PROCESSAMENTO.md |
| Etapa 3 | docs/etapas/ETAPA3_FEATURE_ENGINEERING.md |
| Etapa 4 | docs/etapas/ETAPA4_VALIDACAO.md |
| Módulo A | docs/modulos/MODULO_A_INFERENCIA.md |
| Visual | docs/visual/LEIA-ME-VISUAL.txt |
| Demo | docs/visual/demo_modulo_a.ipynb |

---

## Arquivo Descontinuado

[ARQUIVOS_DESCONTINUADOS.md](ARQUIVOS_DESCONTINUADOS.md) - Lista de arquivos não mais utilizados

---

**Última atualização**: 11 de novembro de 2025
**Status**: Estrutura organizada e pronta para uso
