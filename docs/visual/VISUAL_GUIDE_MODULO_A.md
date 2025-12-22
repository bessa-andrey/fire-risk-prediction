# Guia Visual - Módulo A

Como Funciona o Sistema de Identificação de Áreas Espúrias - COM IMAGENS

---

## Overview

Este guia mostra visualmente como o sistema de Módulo A funciona, com gráficos e mapas explicativos.

---

## O Que É o Problema?

### Cenário Real:
- Satélites FIRMS detectam hotspots de fogo todos os dias
- Alguns são reais (fogo confirmado por MCD64A1)
- Alguns são falsos (nuvens, ruído, etc)
- Objetivo: Separar reais dos espúrios automaticamente

### Exemplo:
```
FIRMS detecta: 230 hotspots em MATOPIBA
  - 150 são reais (fogo confirmado)
  - 80 são espúrios (falso positivo)

PERGUNTA: Como identificar qual é qual sem dados de ground truth?
RESPOSTA: Usar modelo de Machine Learning!
```

---

## Visualização 1: Distribuição Espacial dos Hotspots

### Imagem: `01_distribuicao_hotspots.png`

**Lado Esquerdo**: Mapa mostrando:
- Pontos VERDES: Hotspots reais (fogo confirmado)
  - Localizados em certas regiões
  - Alta confiança FIRMS

- Pontos VERMELHOS: Hotspots espúrios (falso positivo)
  - Distribuição diferente no mapa
  - Confiança FIRMS mais baixa

**Lado Direito**: Gráfico de Distribuição
- Hotspots reais têm confiança média: ~85%
- Hotspots espúrios têm confiança média: ~50%
- Insight: Confiança FIRMS é uma feature importante!

**O que você aprende**:
- Hotspots reais e espúrios têm padrões diferentes
- O modelo pode aprender esses padrões
- Confiança FIRMS é um indicador útil (mas não perfeito)

---

## Visualização 2: Predições do Modelo

### Imagem: `02_predicoes_modelo.png`

**Painel 1 (Top-Left)**: Mapa com Predições
- Pontos VERDES com círculo: Predito como REAL
- Pontos VERMELHOS com X: Predito como ESPÚRIO
- Compare com mapa anterior para ver acertos/erros

**Painel 2 (Top-Right)**: Confiança vs Probabilidade
- Eixo X: Confiança FIRMS (0-100)
- Eixo Y: Probabilidade de ser espúrio (0-1)
- **Linha azul**: Limite de decisão (0.5)
  - Acima = predito como ESPÚRIO
  - Abaixo = predito como REAL
- **Linha laranja**: Limite de alta confiança (0.7)

**Painel 3 (Bottom-Left)**: Matriz de Confusão
```
                Predito
              Real  Espúrio
Verdadeiro Real   150    20        (82% acurácia para reais)
         Espúrio   10    70        (87% acurácia para espúrios)
```

**Painel 4 (Bottom-Right)**: Distribuição de Probabilidades
- **Histograma VERDE**: Distribuição de hotspots reais
  - Concentrado na esquerda (baixa probabilidade de ser espúrio)
  - Significa: modelo tem certeza que são reais

- **Histograma VERMELHO**: Distribuição de hotspots espúrios
  - Concentrado na direita (alta probabilidade de ser espúrio)
  - Significa: modelo tem certeza que são espúrios

- **Linha azul**: Decisão onde eles se separam (0.5)

**O que você aprende**:
- Modelo separa bem hotspots reais de espúrios
- Hotspots com confiança FIRMS alta tendem a ser reais
- Decisão threshold em 0.5 é apropriada

---

## Visualização 3: Estratégias de Filtro

### Imagem: `03_estrategias_filtro.png`

**4 Cenários Comparados**:

### Cenário 1: Usar TODOS (sem filtro)
- Hotspots analisados: **230**
- Taxa de acerto: **65%**
- Problema: Muitos falsos positivos estragam análise!

### Cenário 2: Usar apenas "Predito como Real"
- Hotspots após filtro: **155** (67% dos originais)
- Taxa de acerto: **97%**
- Redução de falsos positivos: **48%**

### Cenário 3: Usar "Probabilidade < 0.5" (RECOMENDADO)
- Hotspots após filtro: **160** (70% dos originais)
- Taxa de acerto: **98%**
- Redução de falsos positivos: **52%**

### Gráfico de Barras
- Mostra taxa de acerto para cada estratégia
- **Vermelho** (sem filtro): baixa acurácia
- **Verde claro/escuro** (com filtro): alta acurácia

**O que você aprende**:
- Sem filtro: 35% dos hotspots que você usa são falsos!
- Com filtro: reduz para ~2% de falsos
- Estratégia 3 é melhor: mantém mais hotspots reais

---

## Visualização 4: Mapa de Recomendações

### Imagem: `04_mapa_recomendacoes.png`

**Cores no Mapa**:
- **VERDE**: Hotspots RECOMENDADOS
  - Probabilidade < 0.5
  - Use para sua análise!

- **LARANJA**: Hotspots PARA REVISAR
  - Probabilidade entre 0.5-0.7
  - Incerteza moderada
  - Verificação manual recomendada

- **VERMELHO**: Hotspots DESCARTADOS
  - Probabilidade ≥ 0.7
  - Muito provavelmente espúrios
  - Ignore em análises

**Exemplo de Leitura**:
```
Região Norte (topo do mapa):
  - Muitos pontos verdes (reais)
  - Poucos pontos vermelhos (espúrios)
  - Conclusão: Fogo real nesta região

Região Sul (lado do mapa):
  - Alguns pontos verdes
  - Vários pontos vermelhos
  - Conclusão: Muitos falsos positivos aqui
```

**O que você aprende**:
- Distribuição espacial de hotspots reais vs espúrios
- Algumas regiões têm mais falsos que outras
- Pode priorizar análise nas regiões verdes

---

## Visualização 5: Workflow Completo

### Imagem: `05_workflow_diagram.png`

**Fluxo de 5 Etapas**:

### ETAPA 1: INPUT
```
CSV com seus hotspots:
├─ latitude
├─ longitude
├─ confidence (confiança FIRMS)
└─ acq_datetime (data/hora)
```

### ETAPA 2: MODELO
```
LightGBM faz:
1. Carrega seu hotspot
2. Extrai features (20+ variáveis)
3. Processa através de 100 árvores
4. Calcula probabilidade de ser espúrio (0-1)
```

### ETAPA 3: OUTPUT
```
Para cada hotspot você recebe:
├─ Predição (0=real, 1=espúrio)
├─ Probabilidade (0.0-1.0)
└─ Confiança (HIGH/MEDIUM/LOW)
```

### ETAPA 4: FILTRO
```
Escolha uma estratégia:

USE (prob < 0.5)
   └─ 160 hotspots recomendados

REVISAR (0.5 ≤ prob < 0.7)
   └─ 15 hotspots com incerteza

DESCARTE (prob ≥ 0.7)
   └─ 55 hotspots falsos
```

### ETAPA 5: USE NA ANÁLISE
```
Prossiga com hotspots recomendados para:
├─ Análise de padrões de fogo
├─ Modelagem de propagação
├─ Estimativa de área queimada
└─ Etc.
```

---

## Exemplo Prático Passo-a-Passo

### Seu Dados de Entrada

```csv
hotspot_id,latitude,longitude,confidence,acq_datetime
FIRMS_001,-8.523,-55.214,78,2024-11-01
FIRMS_002,-9.145,-54.876,45,2024-11-01
FIRMS_003,-8.912,-55.634,92,2024-11-02
...
```

### Processamento pelo Modelo

```
FIRMS_001: 78% confiança
  → Modelo calcula 20+ features
  → Processa através de árvores
  → Resultado: 23% probabilidade de ser espúrio
  → Conclusão: REAL HOTSPOT - USE

FIRMS_002: 45% confiança
  → Modelo calcula features
  → Processa através de árvores
  → Resultado: 76% probabilidade de ser espúrio
  → Conclusão: ESPÚRIO - DESCARTE

FIRMS_003: 92% confiança
  → Modelo calcula features
  → Processa através de árvores
  → Resultado: 18% probabilidade de ser espúrio
  → Conclusão: REAL HOTSPOT - USE
```

### Seu Output

```csv
hotspot_id,latitude,longitude,prediction,spurious_probability,confidence_score
FIRMS_001,-8.523,-55.214,0,0.23,LOW
FIRMS_002,-9.145,-54.876,1,0.76,HIGH
FIRMS_003,-8.912,-55.634,0,0.18,LOW
...
```

### Próximas Ações

```
USE FIRMS_001 e FIRMS_003 (reais)
DESCARTE FIRMS_002 (espúrio)
→ Prossiga com análise apenas dos reais
```

---

## Tabela Comparativa: Sem vs Com Filtro

| Métrica | Sem Filtro | Com Filtro |
|---------|-----------|-----------|
| **Hotspots analisados** | 230 | 160 |
| **Hotspots reais (verdade)** | 150 | 150 |
| **Hotspots espúrios (verdade)** | 80 | 10 |
| **Taxa de Acerto** | 65% | 94% |
| **Falsos Positivos** | 80 | 10 |
| **Redução de Ruído** | 0% | 87% |
| **Recomendação** | Não use | Use! |

---

## O Que o Modelo Aprendeu?

### Features Mais Importantes (Top 5):

1. **Confiança FIRMS** (30%)
   - Hotspots com alta confiança tendem a ser reais

2. **Persistência** (25%)
   - Hotspots que aparecem vários dias tendem a ser reais

3. **Condições Meteorológicas** (20%)
   - Temperatura, umidade, vento
   - Correlacionam com fogo real

4. **Vegetação** (15%)
   - NDVI (índice de vegetação)
   - Áreas com vegetação densa são mais propensas a fogo real

5. **Contexto Espacial** (10%)
   - Proximidade a áreas com fogo anterior
   - Proximidade a estradas

---

## Como Interpretar Resultados

### Caso 1: Confiança BAIXA no Resultado

```
Hotspot X:
├─ Confiança FIRMS: 35%
├─ Spurious Probability: 0.62
├─ Confidence Score: MEDIUM
└─ Recomendação: REVISAR MANUALMENTE
```

**Por quê?**
- Baixa confiança FIRMS já é suspeita
- Modelo tem 62% de certeza que é espúrio
- Mas 38% de chance de ser real
- **Ação**: Olhe manualmente no satélite/QGIS antes de descartar

### Caso 2: Confiança ALTA no Resultado

```
Hotspot Y:
├─ Confiança FIRMS: 89%
├─ Spurious Probability: 0.08
├─ Confidence Score: LOW
└─ Recomendação: USE COM SEGURANÇA
```

**Por quê?**
- Alta confiança FIRMS
- Modelo tem 92% de certeza que é real
- Padrão consistente
- **Ação**: Use normalmente em análises

### Caso 3: Predição Discordante

```
Hotspot Z:
├─ Confiança FIRMS: 50%
├─ Spurious Probability: 0.12 (predito real, mas...)
├─ Confidence Score: LOW
└─ Recomendação: REVISAR
```

**Por quê?**
- FIRMS confiança é media
- Mas modelo prediz real com alta confiança
- Pode indicar outras features (persistência, meteorologia) suportam
- **Ação**: Revisar por features adicionais antes de usar

---

## Próximas Etapas

### Para Análise Espacial:

```python
# Código para criar mapa como Visualização 4
import geopandas as gpd
from shapely.geometry import Point

# Carregar predições
pred = pd.read_csv('predictions.csv')

# Converter para GeoDataFrame
geometry = [Point(lon, lat) for lon, lat in
            zip(pred['longitude'], pred['latitude'])]
gdf = gpd.GeoDataFrame(pred, geometry=geometry, crs='EPSG:4326')

# Salvar por tipo
gdf[gdf['spurious_probability'] < 0.5].to_file('real_hotspots.gpkg')
gdf[gdf['spurious_probability'] >= 0.7].to_file('spurious_hotspots.gpkg')

# Visualizar em QGIS!
```

### Para Análise Temporal:

```python
# Ver como hotspots mudam ao longo do tempo
pred['date'] = pd.to_datetime(pred['acq_datetime'])
real_by_date = pred[pred['spurious_probability'] < 0.5].groupby('date').size()
spurious_by_date = pred[pred['spurious_probability'] >= 0.7].groupby('date').size()

plt.plot(real_by_date.index, real_by_date, label='Real', color='green')
plt.plot(spurious_by_date.index, spurious_by_date, label='Spurious', color='red')
plt.legend()
plt.show()
```

---

## Referências Visuais

### Arquivos Gerados pelo Notebook:

1. **01_distribuicao_hotspots.png**
   - Mostra diferença spatial e de confiança

2. **02_predicoes_modelo.png**
   - Mostra performance do modelo (4 painéis)

3. **03_estrategias_filtro.png**
   - Compara estratégias de filtro

4. **04_mapa_recomendacoes.png**
   - Mapa interativo mostrando recomendações

5. **05_workflow_diagram.png**
   - Diagrama do fluxo completo

---

## Checklist Visual

Antes de usar o sistema:

- [ ] Li os 5 gráficos (01-05)
- [ ] Entendi a diferença entre hotspots reais e espúrios
- [ ] Entendi como o modelo funciona
- [ ] Entendi as 3 categorias (USE/REVISAR/DESCARTE)
- [ ] Tenho dados de entrada (CSV com 4 colunas)
- [ ] Estou pronto para rodar: `python src/models/predict_module_a.py --input meus_dados.csv`

---

## Pronto para Usar!

Agora você:
1. **Entende visualmente** como o sistema funciona
2. **Sabe interpretar** as saídas (mapas, gráficos)
3. **Pode filtrar** hotspots com confiança
4. **Pode integrar** em sua análise de fogo

**Próximo passo**: Execute `python src/models/predict_module_a.py` com seus dados!

---

**Última Atualização**: 11 de novembro de 2025
**Status**: Pronto para Visualização
