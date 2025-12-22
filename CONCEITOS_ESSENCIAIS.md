# Conceitos Essenciais - Projeto Mestrado em Fire Detection ML

## Objetivo Desta Lista
Esta lista organiza TODOS os conceitos que você deve compreender para implementar e defender seu projeto de mestrado. Está estruturada em 5 categorias principais, com nível de profundidade para cada conceito.

---

## 1. CONCEITOS DE GEOSPATIAL DATA (Dados Geoespaciais)

### 1.1 Coordinate Reference Systems (CRS) - **CRÍTICO**
- O que é um CRS e por que é importante
- Diferença entre CRS geográfico (lat/lon) vs projetado (metros)
- Principais CRS do projeto:
  - **EPSG:4326** - WGS84 (dados FIRMS originais)
  - **EPSG:3857** - Web Mercator (web mapping)
  - **UTM Zone 23/24** - Para operações em metros (MATOPIBA)
- Como o geopandas lida com CRS
- Reprojeção (`.to_crs()`) e por que é necessária
- **Por quê**: Sem CRS correto, distâncias, áreas e análises espaciais ficam erradas

### 1.2 Vector Data (Dados Vetoriais) - **CRÍTICO**
- Tipos: Points (hotspots), Lines (rios), Polygons (estados, queimadas)
- Estruturas de dados:
  - **GeoDataFrame** - pandas + geometria (biblioteca: geopandas)
  - Colunas: geometry, latitude, longitude, outros atributos
- Operações comuns:
  - Filtering (`.loc`, `.query()`)
  - Spatial joins (`.sjoin()`) - identificar pontos dentro de polígonos
  - Buffer e proximity analysis - distância para POI
  - Convex hull, centroid, boundary
- **Prático**: FIRMS hotspots são Points; MATOPIBA é um Polygon
- **Por quê**: Todo dado geoespacial começa com vetores

### 1.3 Raster Data (Dados Matriciais) - **CRÍTICO**
- Conceito: grid regular de pixels/células
- Características: dimensões (altura, largura), resolução (metros/graus), CRS, valores
- Estruturas de dados:
  - **rasterio** - leitura/escrita de GeoTIFF
  - **rioxarray** (xarray + rasterio) - operações matriciais eficientes
  - **xarray.Dataset** - dados multi-dimensionais (lat, lon, time)
- Exemplos do projeto:
  - **Sentinel-2**: Imagem óptica 10m (NDVI)
  - **MCD64A1**: Burned area 500m (ground truth)
  - **ERA5**: Dados meteorológicos 0.25° daily
- Operações:
  - Resampling (mudar resolução)
  - Reprojection (mudar CRS)
  - Point queries (extrair valor em coordenada)
  - Temporal aggregation (daily → monthly)
- **Por quê**: Satélites geram rasters; ML precisa extrair valores nesses rasters

### 1.4 Spatial Joins e Point-in-Polygon - **IMPORTANTE**
- Identificar qual estado/município cada hotspot está
- Operação: `geopandas.sjoin(hotspots_gdf, states_gdf, how='inner')`
- Resultado: hotspots com atributos de estado anexados
- **Por quê**: Necessário para validação espacial (treinar/testar por região)

### 1.5 Distance Calculations (Cálculo de Distâncias) - **IMPORTANTE**
- Calcular distância mínima entre hotspot e POI (postos de combustível, cidades)
- Transformar em feature para o modelo
- Métodos:
  - Distância Euclidiana (simples, rápida)
  - Distância Haversine (geodésica, mais precisa em esferas)
  - Use `geopandas.GeoDataFrame.distance()` ou `shapely.geometry.Point.distance()`
- **Por quê**: Hotspots perto de infraestrutura → maior chance de ser spurious

### 1.6 Geospatial Data Formats - **IMPORTANTE**
- **Shapefiles (.shp/.dbf/.shx)**: Vetores antigos, limitados, 3 arquivos
- **GeoPackage (.gpkg)**: Vetores modernos, tudo em 1 arquivo, recomendado
- **GeoTIFF (.tif)**: Rasters com metadados geoespaciais
- **NetCDF (.nc)**: Rasters multi-dimensionais (ERA5, Sentinel-2)
- **CSV com lat/lon**: Dados tabulares sem geometria
- **Por quê**: Cada formato tem vantagens; projeto usa GPKG para outputs

---

## 2. CONCEITOS DE MACHINE LEARNING

### 2.1 Classificação Binária vs Regressão - **CRÍTICO**
- **Classificação Binária** (nosso caso):
  - Output: 0 (real) ou 1 (spurious)
  - Probabilidades: P(spurious)
  - Métricas: Accuracy, Precision, Recall, AUC
- **Regressão** (não usamos):
  - Output: valor contínuo
  - Exemplo: prever temperatura, não aplicável aqui
- **Por quê**: Entender que Module A é classificação é fundamental

### 2.2 Feature Engineering - **CRÍTICO**
- O que é: transformar dados brutos em features (variáveis) úteis para ML
- Processo:
  1. Exploração: entender dados disponíveis
  2. Transformação: criar novas variáveis significativas
  3. Seleção: escolher features mais importantes
  4. Escalonamento: normalizar valores (se necessário)
- Exemplos no projeto (20 features):
  - **Temporais**: dia do ano, estação, persistência
  - **Meteorológicas**: temperatura, vento, umidade, índice de secagem
  - **Vegetação**: NDVI (Normalized Vegetation Index)
  - **Espaciais**: latitude, longitude, distância a POI
  - **Confiança FIRMS**: confidence score original
- **Por quê**: "Garbage in, garbage out" - features ruins = modelo ruim

### 2.3 Weak Labeling - **CRÍTICO**
- Conceito: gerar labels (verdade) sem anotação humana manual
- Nosso método:
  - FIRMS hotspot em 2022-2024 → verificar se MCD64A1 detectou queimada ±15 dias
  - **Label = 1** (spurious): FIRMS detectou mas MCD64A1 não → falso positivo
  - **Label = 0** (real): FIRMS e MCD64A1 concordam → detecção verdadeira
  - **Label = ?** (uncertain): sem dados MCD64A1 → descarta
- Vantagem: automático, sem manual labeling
- Desvantagem: MCD64A1 também erra (pequenas queimadas não detecta)
- **Por quê**: Impossível rotular manualmente 708 hotspots; weak labeling é pragmático

### 2.4 Train/Test Split Estratégias - **CRÍTICO**
- **Random Split**: ERRADO para dados geoespaciais (spatial autocorrelation)
- **Spatial Split** (recomendado):
  - Treinar em 3 estados (Maranhão, Tocantins, Piauí)
  - Testar em 1 estado (Bahia)
  - Repetir 4 vezes (leave-one-out)
  - Garante: modelo generaliza para regiões novas
- **Temporal Split**:
  - Treinar em 2022-2023
  - Testar em 2024
  - Garante: modelo generaliza para futuro
- **Stratified Split**: manter proporção de classes (real vs spurious)
- **Por quê**: Dados geoespaciais/temporais têm correlação; split aleatório superestima performance

### 2.5 Métricas de Classificação - **CRÍTICO**
- **Accuracy**: % de previsões corretas (simples, pode enganar)
  - Fórmula: (TP + TN) / (TP + TN + FP + FN)
- **Precision**: dos que previmos spurious, quantos realmente são?
  - Fórmula: TP / (TP + FP)
  - Importante: não queremos gerar alarmes falsos
- **Recall (Sensitivity)**: dos spurious reais, quantos achamos?
  - Fórmula: TP / (TP + FN)
  - Importante: não queremos perder detecções reais
- **F1-Score**: balanço entre Precision e Recall
  - Fórmula: 2 * (Precision * Recall) / (Precision + Recall)
- **ROC-AUC**: curvando Recall vs (1-Specificity) em todos os thresholds
  - Melhor para dados desbalanceados
  - 0.5 = aleatório, 1.0 = perfeito
- **PR-AUC**: curva Precision-Recall (mais relevante quando classes desbalanceadas)
- **Confusion Matrix**: tabela de TP, TN, FP, FN
- **Por quê**: Cada métrica conta uma história diferente; um modelo 82% de accuracy pode ser ruim

### 2.6 Class Imbalance (Desbalanceamento de Classes) - **IMPORTANTE**
- Problema: 90% real, 10% spurious → modelo tira 9 de 10 acertos sempre prevendo real
- Soluções:
  - **Stratified split**: manter proporção em treino/teste
  - **Class weights**: penalizar erros na classe minoritária (recomendado)
  - **Oversampling**: duplicar classe minoritária
  - **Undersampling**: remover amostras classe majoritária
- LightGBM tem `scale_pos_weight` para isso
- **Por quê**: Ignorar desbalanceamento leva a modelos inúteis

### 2.7 Gradient Boosting (LightGBM, XGBoost) - **CRÍTICO**
- Conceito: ensemble de árvores de decisão, cada uma corrigindo erros da anterior
- Vantagens:
  - Excelente performance em tabular data (melhor que Deep Learning aqui)
  - Rápido de treinar
  - Interpetável (feature importance)
  - Suporta GPU (NVIDIA CUDA)
  - Lida bem com features categóricas
- LightGBM vs XGBoost:
  - **LightGBM**: mais rápido, usa menos memória, cresce árvores folha-a-folha
  - **XGBoost**: mais estável, melhor para competições Kaggle
  - No projeto usamos LightGBM por padrão
- Hiperparâmetros:
  - `num_leaves`: complexidade da árvore (mais = mais overfitting)
  - `learning_rate`: quão rápido aprende (mais lento = mais preciso)
  - `n_estimators`: quantas árvores (mais = melhor até ponto)
  - `max_depth`: profundidade máxima
- **Por quê**: State-of-the-art para tabulares; ideal para nosso caso com 20 features

### 2.8 Overfitting vs Underfitting - **IMPORTANTE**
- **Overfitting**: modelo aprende o ruído dos dados, piora em dados novos
  - Sintoma: train accuracy 99%, test accuracy 60%
  - Solução: regularização, early stopping, validação cruzada
- **Underfitting**: modelo muito simples, não captura padrões
  - Sintoma: train e test accuracy ambos baixos
  - Solução: aumentar complexidade (mais features, mais árvores)
- Balanço: aumentar complexidade até plateau de validação, depois parar
- **Por quê**: Não queremos modelo que memoriza, queremos que generalize

### 2.9 Feature Importance (Importância de Features) - **IMPORTANTE**
- Por que feature é importante:
  - Aparece em muitas árvores
  - Reduz erro/impureza
- Métodos:
  - **Gain/Split**: contribuição da feature para reduzir erro
  - **Coverage**: quantas amostras usam essa feature
  - **Frequência**: quantas vezes feature aparece
  - **SHAP values**: contribuição média de cada feature para cada predição
- **Por quê**: Saber quais features o modelo usa ajuda na interpretabilidade (tese)

### 2.10 Validation Cruzada (Cross-Validation) - **IMPORTANTE**
- Conceito: dividir dados em K partes, treinar K vezes, validar em cada leave-one-out
- Tipos:
  - **K-Fold**: aleatório (NÃO para geospatial)
  - **Stratified K-Fold**: mantém proporção de classes
  - **Time Series Split**: treina passado, testa futuro
  - **Spatial K-Fold**: treina região A, testa região B (recomendado para nós)
- Vantagem: estima performance com mais confiança
- **Por quê**: Uma única divisão treino/teste é instável

---

## 3. CONCEITOS DE PROCESSAMENTO DE DADOS METEOROLÓGICOS E SATÉLITES

### 3.1 ERA5 (Meteorological Data) - **CRÍTICO**
- O que é: Reanalysis de dados meteorológicos globais com resolução 0.25°
- Variáveis chave no projeto:
  - **2m_temperature**: temperatura a 2m de altura (em Kelvin)
  - **relative_humidity**: umidade relativa (0-100%)
  - **u_component_of_wind** / **v_component_of_wind**: velocidade vento (m/s)
  - **total_precipitation**: precipitação acumulada (mm)
- Frequência: disponível a cada 6 horas (ou diários no nosso download)
- Cobertura: 3 anos (2022-2024) em MATOPIBA
- Operações:
  - Conversão Kelvin → Celsius: `temp_celsius = temp_kelvin - 273.15`
  - Calcular magnitude vento: `sqrt(u^2 + v^2)`
  - Calcular direção vento: `atan2(u, v)` em radianos
  - Agregação 6h → diária: média, máximo, mínimo
  - Índices de secagem: CDD, VPD (vapor pressure deficit)
- **Por quê**: Vento aviva fogo, temperatura/umidade afeta propagação

### 3.2 Sentinel-2 (Optical Imagery) - **CRÍTICO**
- Satélite europeu (ESA) com 13 bandas espectrais
- Bandas principais:
  - **Band 4 (Red)**: comprimento 665 nm
  - **Band 8 (NIR)**: comprimento 842 nm (infravermelho próximo)
  - **Band 11 (SWIR)**: comprimento 1610 nm (infravermelho médio)
- NDVI (Normalized Difference Vegetation Index) - **ESSENCIAL**:
  - Fórmula: `NDVI = (NIR - Red) / (NIR + Red)`
  - Valor: -1 a +1
  - Interpretação:
    - < 0: água, asfalto
    - 0-0.3: solo árido, pouca vegetação
    - 0.3-0.6: vegetação moderada
    - > 0.6: floresta densa
  - **Por quê**: vegetação verde = menos propenso a fogo
- Resolução: 10m (melhor do Sentinel-2)
- Revisita: 5 dias (com dois satélites)
- Composites sazonais: secar/úmida (média temporal)
- **Por quê**: Tipo de vegetação é feature crucial para detectar spurious

### 3.3 MCD64A1 (Burned Area Product) - **CRÍTICO**
- Produto MODIS que detecta área queimada
- Resolução: 500m (relativamente grosso)
- Frequência: mensal (fim de cada mês)
- Variáveis:
  - **Burn Date**: dia do mês (1-366) que foi queimado
  - **Confidence**: confiança da detecção (0-100%)
  - Máscara: pixels queimados vs não-queimados
- Limitações:
  - Não detecta queimadas < 500m²
  - Atraso de 8-16 dias após queimada
  - Nuvens podem mascarar
- Uso no projeto:
  - Ground truth para weak labeling
  - Comparar FIRMS vs MCD64A1 ±15 dias
- **Por quê**: É nosso rótulo de verdade (imperfeito, mas o melhor disponível)

### 3.4 FIRMS (Fire Information for Resource Management System) - **CRÍTICO**
- Satélites NOAA (aqui no Brasil: GOES-16, NOAA 20/21)
- Detecta hotspots (pontos quentes) em tempo real
- Dados:
  - Latitude, longitude
  - Data/hora detecção (UTC)
  - Confidence (0-100%): confiança do sensor
  - Radiative Power (MW): potência térmica
  - Instrument: qual satélite detectou
  - FRP (Fire Radiative Power)
- Limitações (source de spurious):
  - Confunde fogo com reflexos (vulcões, campos geotérmicos)
  - Confunde com fábricas (queimadores industriais)
  - Confunde com queimadas agrícolas intensa/controlada com fogo florestal
  - Detecta mesmo queimadas muito pequenas (< MCD64A1)
- **Por quê**: FIRMS gera alertas em tempo real; Module A filtra os falsos

### 3.5 Xarray e Dask - **IMPORTANTE**
- **xarray**: extensão do pandas para dados multi-dimensionais (lat, lon, time)
- Vantagens:
  - Operações vetorizadas em 3D
  - Preserva metadados (CRS, unidades)
  - Integração com rasterio (rioxarray)
- **Dask**: computação paralela/lazy com arrays grandes
- Operações:
  - Seleção: `data.sel(latitude=-10, longitude=-50, method='nearest')`
  - Agregação temporal: `data.resample(time='D').mean()`
  - Operações vetorizadas: `(data['b8'] - data['b4']) / (data['b8'] + data['b4'])`
- **Por quê**: ERA5 tem 1095 dias × 360 lats × 720 lons = muitos dados

### 3.6 Índices Derivados (Derived Indices) - **IMPORTANTE**
- **NDVI**: vegetação
- **NDMI** (Normalized Difference Moisture Index): umidade da vegetação
  - Fórmula: `(NIR - SWIR) / (NIR + SWIR)`
- **NDBI** (Normalized Difference Built-up Index): áreas urbanas
- **SPI** (Standardized Precipitation Index): seca
- **VPD** (Vapor Pressure Deficit): efeito evaporativo
- **CDD** (Consecutive Dry Days): dias secos seguidos
- **Por quê**: Cada índice captura aspecto diferente relevante para fogo

---

## 4. CONCEITOS DE DADOS E PIPELINE

### 4.1 ETL (Extract, Transform, Load) - **CRÍTICO**
- **Extract**: Baixar dados (FIRMS CSV, ERA5 NetCDF, Sentinel-2 GeoTIFF)
- **Transform**: Limpar, processar, validar, agregar
- **Load**: Salvar em formato processado (CSV, NetCDF, GPKG)
- Pipeline do projeto:
  1. **Stage 1 (Extract)**: `src/data_ingest/` → raw data
  2. **Stage 2 (Transform)**: `src/preprocessing/` → processado
  3. **Stage 3 (Load+Features)**: `src/preprocessing/feature_engineering.py` → ML-ready
  4. **Stage 4 (Validate)**: `src/models/` → métricas
- **Por quê**: Dados desorganizados = projeto fraco

### 4.2 Data Validation (Validação de Dados) - **IMPORTANTE**
- Verificações necessárias:
  - Valores fora de range (lat -90 a +90, lon -180 a +180)
  - Missing values (NaN, None)
  - Duplicatas
  - Tipos de dados incorretos
  - Timestamps inválidos
  - Geometrias inválidas (shapely)
- Exemplo: FIRMS latitude deve estar em [-15, 0] para MATOPIBA
- **Por quê**: 1 erro de dados = modelo aprende padrão falso

### 4.3 Data Aggregation (Agregação de Dados) - **IMPORTANTE**
- Combinar múltiplas medições em uma:
  - FIRMS: 3 hotspots no mesmo dia/local → agregar em 1 (soma radiativa power)
  - ERA5: 4 medições 6-horarias → média diária
  - Sentinel-2: 6 imagens do mês → composto mediano (remove nuvens)
- **Por quê**: Reduz ruído, aumenta clareza do sinal

### 4.4 Reproducibilidade (Reprodutibilidade) - **CRÍTICO**
- Conceito: outro pesquisador deve conseguir reproduzir exatos resultados
- Elementos:
  - **Versionamento**: pip freeze ou requirements.txt com versões exatas
  - **Random seeds**: `np.random.seed(42)`, `lgb.seed(42)`
  - **Data snapshots**: versão data de download (ERA5, FIRMS mudam)
  - **Documentação**: exatas instruções de como rodar
  - **Git commits**: rastrear mudanças código
- **Por quê**: Tese exige reproducibilidade; sem ela não é ciência válida

### 4.5 Data Leakage - **CRÍTICO**
- Conceito: informação do futuro/teste vaza para treinamento
- Exemplos ruins:
  - Feature engineered no TODA dataset antes de split
  - Escalonamento (StandardScaler) fitado em train+test juntos
  - Usar tempo futuro para prever passado
- Correto:
  1. Split treino/teste
  2. Fit transformer SÓ em treino
  3. Aplicar em teste (`.fit_transform(train)`, `.transform(test)`)
- **Por quê**: Data leakage inflata métricas; modelo falha em produção

### 4.6 Feature Scaling/Normalization - **IMPORTANTE**
- LightGBM é agnóstico (não precisa scaling)
- Redes neurais precisam (não usamos aqui, mas bom saber)
- Tipos:
  - **Standardization**: `(x - mean) / std`
  - **Min-Max**: `(x - min) / (max - min)`
  - **Log transform**: `log(x)` para distribuições skewed
- **Por quê**: Algumas libs assumem dados normalizados

---

## 5. CONCEITOS DE MODELAGEM E PRODUÇÃO

### 5.1 Model Serialization (Serialização de Modelos) - **IMPORTANTE**
- Salvar modelo treinado em disco para usar depois
- Formatos:
  - **Pickle** (`.pkl`): padrão Python, suporta qualquer classe
  - **Joblib** (`.joblib`): otimizado para sklearn, LightGBM
  - **ONNX**: formato aberto, deploy multiplataforma
- Código:
  ```python
  import joblib
  joblib.dump(model, 'model.joblib')
  model = joblib.load('model.joblib')
  ```
- **Por quê**: Treinar é caro; reusar modelo é barato

### 5.2 Prediction vs Probability - **IMPORTANTE**
- **Prediction**: classe (0 ou 1)
  - `pred = (prob_spurious > 0.5).astype(int)`
- **Probability**: confiança (0 a 1)
  - `prob = model.predict_proba(X)[:, 1]`
- Threshold:
  - Padrão: 0.5 (igual chance real/spurious)
  - Customizável: se quisermos ser conservador (poucos alarms) → 0.7
  - Se quisermos catching tudo → 0.3
- Tradeoff:
  - Threshold alto → Precision sobe, Recall desce
  - Threshold baixo → Precision desce, Recall sobe
- **Por quê**: Diferentes aplicações precisam de diferentes thresholds

### 5.3 Inference Pipeline (Pipeline de Inferência) - **CRÍTICO**
- Processo de usar modelo treinado em dados novos:
  1. Carregar modelo serializado
  2. Carregar dados novos (hotspots FIRMS, por ex.)
  3. Feature engineering: extrair mesmas 20 features
  4. Normalização: aplicar MESMAS transformações de treino
  5. Predição: `model.predict_proba(X_new)`
  6. Pós-processamento: adicionar confiança, interpretação
  7. Salvar resultados
- **Por quê**: Production exige pipeline automático, robusto, rápido

### 5.4 Model Monitoring (Monitoramento de Modelo) - **IMPORTANTE**
- Em produção, performance pode degradar (data drift, concept drift)
- Monitoramento:
  - Rastrear acurácia ao longo do tempo
  - Alertar se accuracy cai > threshold
  - Recolher amostras para retreinamento
  - Versionamento modelo (v1.0 → v1.1 → v2.0)
- **Por quê**: Modelos não vivem para sempre; precisam manutenção

### 5.5 API REST para Modelos - **IMPORTANTE**
- Envolver modelo em server web (Flask, FastAPI)
- Client envia JSON com hotspots
- Server retorna JSON com predições
- Exemplo:
  ```
  POST /predict
  {"hotspots": [{"lat": -10, "lon": -50, "confidence": 85}]}

  Response:
  {"predictions": [{"spurious_prob": 0.23, "prediction": 0}]}
  ```
- **Por quê**: Permite usar modelo sem Python (web, mobile, etc.)

### 5.6 Hyperparameter Tuning - **IMPORTANTE**
- Encontrar melhores valores para:
  - `num_leaves`, `learning_rate`, `n_estimators`, `max_depth`, etc.
- Métodos:
  - **Grid Search**: testar todas combinações (lento)
  - **Random Search**: testar aleatório (mais rápido)
  - **Bayesian Optimization**: inteligente, busca direciona para promissor
- Ferramentas: scikit-learn `GridSearchCV`, Optuna
- Trade-off: tuning melhor = modelo melhor, mas tempo maior
- **Por quê**: Default hiperparâmetros raramente são ótimos

---

## MAPA MENTAL: FLUXO DO PROJETO

```
STAGE 1: INGESTÃO
├─ Baixar FIRMS (CSV)
├─ Baixar MCD64A1 (NetCDF/GeoTIFF)
├─ Baixar Sentinel-2 (GeoTIFF)
└─ Baixar ERA5 (NetCDF)

STAGE 2: PROCESSAMENTO
├─ Validar geometrias (lat/lon, CRS)
├─ Agregar FIRMS em grid
├─ Processar MCD64A1 (merge 36 meses)
├─ Calcular NDVI Sentinel-2
└─ Transformar ERA5 (6h → diário, K → C)

STAGE 3: FEATURE ENGINEERING + LABELING
├─ Weak Labeling: FIRMS vs MCD64A1 ±15 dias
├─ Extract Features:
│  ├─ Temporal (dia do ano, persistência)
│  ├─ Meteorológicas (temp, umidade, vento, secagem)
│  ├─ Vegetação (NDVI, tipo cobertura)
│  └─ Espaciais (lat, lon, distância POI)
└─ Resultado: matriz features + labels

STAGE 4: MODELAGEM
├─ Split: Spatial (4 regiões) + Temporal (3 anos)
├─ Treinar LightGBM com class_weights (desbalanceamento)
├─ Validação Cruzada: Spatial + Temporal
├─ Tuning Hiperparâmetros
├─ Feature Importance + SHAP
└─ Resultado: Model 82% accuracy

MODULE A (Production Inference)
├─ Carregar modelo treinado
├─ Novos hotspots FIRMS (entrada)
├─ Feature engineering (mesmas 20 features)
├─ Predição: P(spurious)
├─ Threshold: > 0.5 = alerta spurious
└─ Output: CSV/JSON predictions

MODULE B (Fire Propagation - Futuro)
├─ Grid regular 250-500m
├─ Label: MCD64A1 D+1 (queimou amanhã?)
├─ Features: meteorológicas + terrain
├─ Modelo: LightGBM regression/classification
├─ Validação: IoU, Brier score
└─ Output: Probability maps (GeoTIFF)
```

---

## CHECKLIST: O QUE ESTUDAR ANTES DE COMEÇAR

### Semana 1: Fundamentos Geospatial
- [ ] Entender CRS (WGS84, UTM, transformações)
- [ ] Geopandas: GeoDataFrame, geometrias, operações espaciais
- [ ] Rasterio/Rioxarray: abrir, ler, manipular rasters
- [ ] Sentir-se confortável com EPSG:4326 vs EPSG:3857
- [ ] Spatial join: atribuir estado a hotspots

### Semana 2: Dados do Projeto
- [ ] Explorar FIRMS: estrutura, campos, valores típicos
- [ ] Explorar MCD64A1: resolução, BurnDate, limites
- [ ] Explorar Sentinel-2: bandas, NDVI, composites
- [ ] Explorar ERA5: variáveis chave, conversões (K→C, componentes vento)
- [ ] Visualizar dados em QGIS

### Semana 3: Machine Learning
- [ ] Classificação binária: métricas (accuracy, precision, recall, AUC)
- [ ] Feature engineering: conceitos e exemplos
- [ ] Weak labeling: lógica do projeto
- [ ] Train/test splits: por quê não random em geospatial
- [ ] Desbalanceamento de classes: impacto e soluções

### Semana 4: LightGBM e Validação
- [ ] Gradient boosting: conceitos básicos
- [ ] LightGBM: treinamento, hiperparâmetros, GPU
- [ ] Validação cruzada: estratégias (spatial, temporal, stratified)
- [ ] Interpretabilidade: feature importance, SHAP
- [ ] Confusion matrix, ROC curve, PR curve

### Semana 5: Prático
- [ ] Rodar Stage 1-4 do projeto (end-to-end)
- [ ] Entender saídas em cada stage
- [ ] Modificar features e ver impacto
- [ ] Plotar validação (maps, curves)
- [ ] Prever em novos hotspots

### Bônus: Produção
- [ ] Model serialization (joblib)
- [ ] Inference pipeline
- [ ] API REST (Flask/FastAPI) - opcional
- [ ] Data leakage: evitar
- [ ] Reproducibilidade: seeds, versionamento

---

## RECURSOS RECOMENDADOS

### Documentação Projeto (Leia em Ordem):
1. `docs/setup/SETUP_AMBIENTE.md` - Ambiente
2. `docs/etapas/ETAPA1_INGESTAO.md` - Dados
3. `docs/etapas/ETAPA2_PROCESSAMENTO.md` - Limpeza
4. `docs/etapas/ETAPA3_FEATURE_ENGINEERING.md` - Features
5. `docs/etapas/ETAPA4_VALIDACAO.md` - Métricas
6. `docs/modulos/MODULO_A_INFERENCIA.md` - Produção
7. `docs/visual/demo_modulo_a.ipynb` - Jupyter interativo
8. `docs/conceptos/RESUMO_EXPLICACOES.txt` - Conceitos

### Tutoriais Externos:
- **Geospatial**: Geopandas docs, Rasterio docs
- **Satélites**: Sentinel-2 Band Math, MODIS tutorials
- **Meteorologia**: ERA5 documentation
- **ML**: Scikit-learn tutorials, LightGBM docs, SHAP documentation
- **Fires**: NASA FIRMS documentation, GFED datasets

### Livros (Referência):
- "Python for Data Analysis" - Wes McKinney (pandas, geospatial)
- "Hands-On Machine Learning" - Aurélien Géron (ML, validation)
- "Remote Sensing and GIS" - Campbell & Wynne (conceitos geoespaciais)

---

## PRÓXIMOS PASSOS

1. **Imediato**: Leia este documento inteiro (1h)
2. **Dia 1-2**: Leia documentação do projeto (SETUP, ETAPA1-2)
3. **Dia 3-7**: Execute Stage 1-2 você mesmo, explorar dados
4. **Semana 2**: Estude feature engineering (ETAPA3)
5. **Semana 3**: Estude ML e validação (ETAPA4)
6. **Semana 4+**: Modifique código, experimente, aprenda

---

## Dúvidas? Perguntas?

Este documento serve como **índice** de tudo que você precisa aprender. Quando tiver dúvida em um conceito, volte aqui e estude a seção relevante com ajuda de Claude.

**Lembre-se**: Compreensão profunda > velocidade de implementação. Melhor gastar 2 semanas aprendendo bem do que 1 semana rápido e 3 semanas consertando.
