# Classificacao Automatica de Focos de Incendio

Dissertacao de Mestrado - PPGEE/UFAM

Sistema de Machine Learning para classificar focos de incendio do FIRMS (NASA) como reais ou espurios na regiao MATOPIBA (2022-2024).

---

## Resultado Principal

- **LightGBM**: 82% acuracia, 86% ROC-AUC, 81% PR-AUC
- **Dataset**: 9.198 amostras balanceadas
- **Reducao de falsos positivos**: 87% (recall 84%)
- **Validacao**: espacial (leave-one-state-out) + temporal (treino 2022-23, teste 2024)

---

## Inicio Rapido

```bash
# 1. Configurar ambiente
conda create -n fireml python=3.10 -y && conda activate fireml
pip install -r requirements.txt

# 2. Executar pipeline completo
python src/data_ingest/run_all_downloads.py
python src/preprocessing/run_all_preprocessing.py
python src/preprocessing/run_etapa3.py
python src/models/run_etapa4.py

# 3. Classificar novos focos
python src/models/predict_module_a.py --input novos_focos.csv
```

---

## Estrutura

```
src/
├── data_ingest/       # Etapa 1: Download (FIRMS, MCD64A1, Sentinel-2, ERA5)
├── preprocessing/     # Etapas 2-3: Processamento + Features + Weak Labeling
├── models/            # Etapa 4: Treinamento + Validacao + Analise Estatistica
└── visualization/     # Mapas

Dissertacao/           # LaTeX (capitulos 0-5)
docs/                  # Documentacao tecnica
root/                  # Documentacao raiz (este diretorio)
```

---

## Documentacao

| Arquivo | Descricao |
|---------|-----------|
| [INDEX.md](INDEX.md) | Indice completo |
| [STATUS_PROJETO.md](STATUS_PROJETO.md) | Status atual |
| [CLAUDE.md](CLAUDE.md) | Guia para Claude Code |
| [PROJETO_SETUP.md](PROJETO_SETUP.md) | Definicao do projeto |
| [ESTRUTURA_PROJETO.md](ESTRUTURA_PROJETO.md) | Arvore de arquivos |

---

## Status

Pipeline de classificacao 100% concluido. Qualificacao aprovada.
Proxima fase: analise espaco-temporal dos focos reais (Mar-Ago 2026).
Defesa prevista: Agosto 2026.

**Repositorio GitHub**: https://github.com/bessa-andrey/fire-risk-prediction

---

**Ultima atualizacao**: 12 de fevereiro de 2026
