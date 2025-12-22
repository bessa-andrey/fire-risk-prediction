# Projeto Mestrado - Machine Learning para Fire Detection

Detecção e propagação de fogo em MATOPIBA (Brasil).

---

## Comece Aqui

Primeiro acesso? Leia na ordem:

1. **[INDEX.md](INDEX.md)** - Índice completo e navegação
2. **[PROJETO_SETUP.md](PROJETO_SETUP.md)** - O que é este projeto
3. **[STATUS_PROJETO.md](STATUS_PROJETO.md)** - Progresso atual

---

## Estrutura Rápida

```
docs/
├── setup/     - Configurar ambiente
├── etapas/    - Executar pipelines (Etapa 1-4)
├── modulos/   - Usar Módulo A em produção
└── visual/    - Gráficos e visualizações

src/
├── preprocessing/  - Scripts Etapas 1-3
├── models/         - Scripts Etapas 3-4
└── propagation/    - Módulo B (futuro)

data/
├── raw/       - Downloads originais
├── processed/ - Dados processados
└── models/    - Modelos treinados
```

---

## Início Rápido

### 1. Setup (primeira vez)
```bash
cd "c:\Users\bessa\Downloads\Projeto Mestrado"
# Leia: docs/setup/SETUP_AMBIENTE.md
```

### 2. Executar pipeline
```bash
# Etapa 1-4 sequencialmente
python src/preprocessing/run_all_preprocessing.py
python src/preprocessing/run_etapa2.py
python src/preprocessing/run_etapa3.py
python src/models/run_etapa4.py
```

### 3. Usar Módulo A (produção)
```bash
python src/models/predict_module_a.py --input seus_hotspots.csv
```

### 4. Visualizar (aprender)
```bash
jupyter lab docs/visual/demo_modulo_a.ipynb
```

---

## Módulo A: Detecção de Hotspots Espúrios

Sistema completo para identificar falsos positivos em detecções FIRMS.

Documentação: [docs/modulos/MODULO_A_INFERENCIA.md](docs/modulos/MODULO_A_INFERENCIA.md)

Visualização: [docs/visual/LEIA-ME-VISUAL.txt](docs/visual/LEIA-ME-VISUAL.txt)

---

## Etapas do Projeto

| Etapa | Descrição | Tempo | Status |
|-------|-----------|-------|--------|
| 1 | Ingestão de dados | 1-2h | Pronto |
| 2 | Processamento | 15-60min | Pronto |
| 3 | Features + Training | 30-45min | Pronto |
| 4 | Validação | 1-2min | Pronto |

Total: ~3-5 horas com GPU, 4-5 horas sem GPU

---

## Documentação por Tipo

### Configuração
- [docs/setup/SETUP_AMBIENTE.md](docs/setup/SETUP_AMBIENTE.md) - Setup completo
- [docs/setup/SETUP_COMPLETO.md](docs/setup/SETUP_COMPLETO.md) - Checklist

### Etapas
- [docs/etapas/ETAPA1_INGESTAO.md](docs/etapas/ETAPA1_INGESTAO.md) - Ingesta de dados
- [docs/etapas/ETAPA2_PROCESSAMENTO.md](docs/etapas/ETAPA2_PROCESSAMENTO.md) - Limpeza de dados
- [docs/etapas/ETAPA3_FEATURE_ENGINEERING.md](docs/etapas/ETAPA3_FEATURE_ENGINEERING.md) - Features + training
- [docs/etapas/ETAPA4_VALIDACAO.md](docs/etapas/ETAPA4_VALIDACAO.md) - Validação

### Módulos
- [docs/modulos/MODULO_A_INFERENCIA.md](docs/modulos/MODULO_A_INFERENCIA.md) - Detecção espúrios

### Visual
- [docs/visual/LEIA-ME-VISUAL.txt](docs/visual/LEIA-ME-VISUAL.txt) - Guia visual
- [docs/visual/demo_modulo_a.ipynb](docs/visual/demo_modulo_a.ipynb) - Jupyter com gráficos

### Reference
- [CLAUDE.md](CLAUDE.md) - Para Claude Code
- [INDEX.md](INDEX.md) - Índice completo

---

## Principais Componentes

### Dados Utilizados
- FIRMS: Detecções de hotspots
- MCD64A1: Áreas queimadas confirmadas
- Sentinel-2: Vegetação (NDVI)
- ERA5: Dados meteorológicos

### Modelos
- LightGBM (principal)
- XGBoost (alternativo)

### Features (20+)
- Confiança FIRMS
- Persistência
- Condições meteorológicas
- Índices de vegetação
- Contexto espacial

---

## Performance

### Módulo A
- Acurácia: 82%
- ROC-AUC: 0.86
- PR-AUC: 0.81
- Redução de falsos positivos: 87%

### Velocidade
- Treino: 30-45 min (Etapa 3)
- Validação: 1-2 min (Etapa 4)
- Inferência: ~10s por 1000 hotspots

---

## Próximas Etapas

1. Módulo B (propagação D+1)
2. Integração de módulos
3. Escrita de tese

---

## Contato e Suporte

Para dúvidas técnicas ou sugestões, consulte:
- [CLAUDE.md](CLAUDE.md) - Instruções para Claude Code
- [docs/setup/](docs/setup/) - Problemas de setup

---

**Última atualização**: 11 de novembro de 2025

**Estrutura**: Organizada e pronta para produção

**Status**: Em desenvolvimento - Fase 1 completa, Fase 2 em planejamento
