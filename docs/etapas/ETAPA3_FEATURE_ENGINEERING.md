# Fase 1 - Etapa 3: Feature Engineering - Guia Prático

**Data de Início**: 11 de novembro de 2025
**Duração**: ~2-3 horas (executar + treinamento)
**Objetivo**: Gerar features para Module A e treinar classificador

---

## Objetivo Geral da Etapa 3

Transformar dados processados em datasets ML-ready com:
1. **Weak Labeling**: Comparar FIRMS vs MCD64A1 → gerar y_train
2. **Feature Extraction**: Extrair features tabulares para Module A e B
3. **Model Training**: Treinar classificador (Module A) com GPU acceleration

**Saída de Etapa 3**:
```
data/processed/
├── module_a/
│   ├── hotspots_labeled.csv (hotspots com labels)
│   ├── hotspots_labeled.gpkg (formato geoespacial)
│   ├── module_a_features.csv (features para ML)
│   └── weak_labeling_stats.json
│
└── module_b/
    └── module_b_features.csv (features grid)

data/models/module_a/
├── module_a_lightgbm.pkl (modelo treinado)
├── module_a_xgboost.pkl (modelo treinado)
├── module_a_lightgbm_metrics.json
├── module_a_xgboost_metrics.json
└── training_summary.json
```

---

## 📋 Scripts de Etapa 3

| Script | Função | Entrada | Saída |
|--------|--------|---------|-------|
| `weak_labeling.py` | Gerar labels | FIRMS + MCD64A1 | Labeled hotspots |
| `feature_engineering.py` | Extrair features | Labels + ERA5 + Sentinel2 | Feature matrix |
| `train_module_a.py` | Treinar modelo | Features | Modelo treinado |
| `run_etapa3.py` | Master script | Todos acima | Resumo |

---

## 🚀 Como Executar

### Opção 1: Master Script (RECOMENDADO)

```bash
cd "c:\Users\bessa\Downloads\Projeto Mestrado"
python src/preprocessing/run_etapa3.py
```

**Tempo total**: ~2-3 horas (com GPU: ~30-45 min)

### Opção 2: Scripts Individuais

```bash
# 1. Weak labeling
python src/preprocessing/weak_labeling.py

# 2. Feature engineering
python src/preprocessing/feature_engineering.py

# 3. Train Module A
python src/models/train_module_a.py
```

### Opção 3: Com GPU Explícito

```bash
# Verificar que GPU está disponível
nvidia-smi

# Executar com GPU
CUDA_VISIBLE_DEVICES=0 python src/preprocessing/run_etapa3.py
```

---

## 📊 O Que Cada Script Faz

### 1. weak_labeling.py

**Objetivo**: Comparar detecções FIRMS contra área queimada MCD64A1

**Processamento**:
```
1. Para cada hotspot FIRMS (lat, lon, data):

2. Buscar MCD64A1 no mesmo local ± 15 dias

3. Aplicar regra de labeling:
   - MCD64A1 > 0 → TRUE_POSITIVE (classe 1)
     Significado: Fogo realmente ocorreu (detectado por satélite de queimada)

   - MCD64A1 == 0 → FALSE_POSITIVE (classe 0)
     Significado: Hotspot detectado mas sem queimada registrada (falso alarme)

   - MCD64A1 == NaN → UNCERTAIN (classe -1)
     Significado: Sem dados de referência (descartado para treinamento)

4. Output: CSV com (lat, lon, data, label, confidence)
```

**Saída Principal**:
```
hotspots_labeled.csv:
- latitude, longitude (coordenadas)
- acq_datetime (data detecção)
- label (0=false_positive, 1=true_positive, -1=uncertain)
- label_numeric (versão numérica)
- label_confidence (certeza do label, 0-1)
- confidence, persistence_score (features FIRMS)

hotspots_labeled.gpkg (GeoPackage):
- Mesmo conteúdo mas em formato geoespacial
- Pode abrir no QGIS para visualizar

weak_labeling_stats.json:
- total_hotspots: X
- false_positives: Y (%)
- true_positives: Z (%)
- mean_confidence_fp: A
- mean_persistence_fp: B
```

**Estatísticas Esperadas**:
- Total: ~700 hotspots
- True positives: ~50-70%
- False positives: ~30-50%
- Falsos positivos tendem a ter confidence mais baixa

---

### 2. feature_engineering.py

**Objetivo**: Extrair features de todos datasets para Module A e B

**Features para Module A**:

```
Hotspot properties:
  - confidence (0-100) - confiança FIRMS
  - persistence_score (0-1) - persistência detectada

Temporal features:
  - month (1-12)
  - dayofyear (1-365)
  - is_dry_season (bool) - julho-outubro?

ERA5 meteorological features:
  - temperature_c (°C)
  - relative_humidity (%)
  - drying_index (%) - inversamente correlado umidade
  - wind_magnitude (m/s)
  - wind_direction (0-360°)
  - precipitation_mm (mm/dia)
  - soil_moisture (m³/m³)

Sentinel-2 vegetation features:
  - ndvi_mean (-1 a +1) - índice vegetação
  - ndvi_max, ndvi_min
  - red_mean (reflectância vermelha)
  - nir_mean (reflectância infravermelho)

Context features:
  - burned_pixels_ratio (0-1) - proporção queimada 3.3km² ao redor
```

**Features para Module B** (grid propagation):
- Similar a Module A, mas para grids de 0.25° em vez de hotspots individuais

**Saída**:
```
module_a_features.csv:
  ~700 linhas × ~20-25 colunas
  Pronto para treinamento ML

module_b_features.csv:
  Grids × timestamps
  Para propagação D+1 (não usada em Etapa 3)

feature_engineering_summary.json:
  - samples: número de amostras
  - features: número de features
  - feature_names: lista de nomes
```

---

### 3. train_module_a.py

**Objetivo**: Treinar classificador com GPU acceleration

**Modelos Treinados**:

1. **LightGBM** (preferido para GPU):
   ```
   device_type='gpu' → NVIDIA CUDA acceleration
   num_leaves: 31
   max_depth: 10
   learning_rate: 0.05
   iterations: 100
   ```

2. **XGBoost** (alternativa com GPU):
   ```
   tree_method='gpu_hist' → GPU histogram generation
   max_depth: 6
   learning_rate: 0.1
   n_estimators: 100
   ```

**Processo**:

```
1. Load features (X, y) from module_a_features.csv

2. Split train/test (80/20) com stratification:
   - Mantém proporção de classes
   - Previne overfitting em classe minoritária

3. Scale features (StandardScaler)
   - Normaliza variáveis com magnitudes diferentes
   - Importante para GBM

4. Train LightGBM on GPU
   - ✓ CUDA acceleration se disponível
   - ✗ CPU fallback se GPU não existir

5. Evaluate:
   - Accuracy: (TP + TN) / Total
   - ROC-AUC: Area under ROC curve (0-1)
   - PR-AUC: Area under Precision-Recall (melhor métrica para classes desbalanceadas!)

6. Same for XGBoost

7. Select best model (higher PR-AUC)
```

**Métricas Esperadas**:
- Accuracy: ~75-85%
- ROC-AUC: ~0.80-0.90
- PR-AUC: ~0.75-0.85 (alvo: ≥0.80)

**Saída**:
```
module_a_lightgbm.pkl: Modelo serializado
module_a_xgboost.pkl: Modelo serializado
module_a_lightgbm_metrics.json: Métricas LightGBM
module_a_xgboost_metrics.json: Métricas XGBoost
training_summary.json: Resumo treino (device usado, scores, etc)

training_summary.json example:
{
  "training_date": "2025-11-11T18:30:00",
  "device": "GPU",
  "samples": 650,
  "features": 22,
  "lightgbm": {
    "accuracy": 0.8234,
    "roc_auc": 0.8567,
    "pr_auc": 0.8123
  },
  "xgboost": {
    "accuracy": 0.8156,
    "roc_auc": 0.8412,
    "pr_auc": 0.7956
  }
}
```

---

## ⚡ GPU Acceleration

### Verificar GPU

```bash
# Listar GPUs disponíveis
nvidia-smi

# Exemplo de output:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 555.00  Driver Version: 555.00                                 |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile |
# | Fan  Temp   Perf   Pwr:Usage/Cap        |         Memory-Usage | GPU-Util |
# |===============================+=====================+======================|
# |   0  NVIDIA RTX 4060      On              | 00:01.0     Off |            |
# |  0%   28C    P8              15W / 130W   |    200MiB / 8192MiB |      0%   |
# +-------------------------------+----------------------+----------------------+
```

### Ativar GPU em Training

O script `train_module_a.py` detecta GPU automaticamente:

```python
# Detecta se GPU está disponível
check_gpu_availability() → True/False

# LightGBM com GPU:
lgb.LGBMClassifier(device_type='gpu')

# XGBoost com GPU:
xgb.XGBClassifier(tree_method='gpu_hist', gpu_id=0)
```

### Ganho de Performance

| Operação | CPU | GPU | Speedup |
|----------|-----|-----|---------|
| Feature scaling | 0.5s | 0.1s | 5x |
| LightGBM train (100 iter) | 30s | 5-8s | 4-6x |
| XGBoost train (100 est) | 25s | 4-6s | 4-6x |
| **Total Etapa 3** | **2.5h** | **30-45m** | **4-5x** |

---

## 🔧 Parâmetros Ajustáveis

### weak_labeling.py

```python
# Linha ~50: Janela temporal de busca em MCD64A1
date_range = timedelta(days=15)  # ±15 dias (padrão)

# Linha ~80: Labels e seus confidence scores
label_confidence: 0.95 para TP/FP, depende de confidence FIRMS para uncertain
```

### feature_engineering.py

```python
# Linha ~120: Grid spacing para Module B
grid_spacing = 0.25  # 0.25° = ~25km (padrão)

# Linha ~180: Número de time steps para Module B
dates = self.era5.time.values[:100]  # Primeiros 100 dias (para teste)
# Aumentar para len(self.era5.time) para dataset completo
```

### train_module_a.py

```python
# Linha ~60: Parâmetros LightGBM
'num_leaves': 31        # Maior = mais complex
'learning_rate': 0.05   # Menor = mais lento mas mais acurado
'max_depth': 10         # Limita profundidade árvore
'num_iterations': 100   # Número de árvores

# Linha ~80: Parâmetros XGBoost
'max_depth': 6          # Menor que LightGBM
'learning_rate': 0.1    # Maior que LightGBM
'n_estimators': 100     # Número de boosting rounds

# Linha ~110: Split parameters
test_size=0.2           # 20% test, 80% train (padrão)
random_state=42         # Seed para reproducibilidade
```

---

## 🐛 Troubleshooting

### Erro: "label file not found"

```
[ERROR] Labels file not found: data/processed/module_a/hotspots_labeled.csv
```

**Solução**:
1. Run weak_labeling.py first
2. Verify file exists: `ls -la data/processed/module_a/`

### Erro: "Features file not found"

```
[ERROR] Features file not found: data/processed/module_a/module_a_features.csv
```

**Solução**:
1. Run feature_engineering.py first
2. Verify: `ls -la data/processed/module_a/`

### GPU não detectada durante treinamento

```
[WARNING] GPU not detected, falling back to CPU
```

**Solução**:
1. Verificar: `nvidia-smi`
2. Se nenhuma GPU aparecer:
   - Instalar NVIDIA drivers: https://www.nvidia.com/Download/driverDetails.aspx
   - Instalar CUDA Toolkit: https://developer.nvidia.com/cuda-toolkit
   - Reiniciar computador

3. Se GPU aparece mas não está sendo usada:
   - LightGBM pode requerer compilação com suporte GPU
   - Solução: `pip install lightgbm --GPU` (se disponível)

### Memória insuficiente

```
[ERROR] CUDA out of memory
```

**Solução**:
1. Reduzir batch_size (automático em LightGBM)
2. Usar CPU em vez de GPU (fallback automático)
3. Reduzir `num_leaves` ou `max_depth`

### Classes desbalanceadas

Se há muito mais falsos positivos que verdadeiros:

```python
# Adicionar ao LightGBMClassifier:
'is_unbalance': True,
'scale_pos_weight': len(y_neg) / len(y_pos)
```

---

## ✅ Checklist de Conclusão

- [ ] Verificar que Etapa 2 outputs existem em data/processed/
- [ ] Executar `python src/preprocessing/run_etapa3.py` ou scripts individuais
- [ ] Verificar weak_labeling output (label distribution OK?)
- [ ] Verificar feature_engineering output (features corretas?)
- [ ] Verificar treinamento completou (modelos salvos em data/models/module_a/)
- [ ] Revisar métricas (PR-AUC ≥ 0.80?)
- [ ] Documentar device usado (GPU ou CPU)
- [ ] Backupar modelos treinados

---

## 📊 Próximas Etapas

### Etapa 4: Avaliação e Validação

```bash
python src/models/evaluate_module_a.py  # Validação espacial/temporal
```

### Etapa 5: Module B (Propagação D+1)

```bash
python src/preprocessing/feature_engineering.py --module_b
python src/models/train_module_b.py
```

---

## 📚 Referências

- **Weak Labeling**: https://en.wikipedia.org/wiki/Weak_supervision
- **LightGBM GPU**: https://lightgbm.readthedocs.io/en/latest/GPU-Targets.html
- **XGBoost GPU**: https://xgboost.readthedocs.io/en/latest/tutorials/gpu.html
- **Precision-Recall**: https://en.wikipedia.org/wiki/Precision_and_recall

---

**Última Atualização**: 11 de novembro de 2025
**Status**: Pronto para executar!

