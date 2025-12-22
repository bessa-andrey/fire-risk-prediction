# Sistema de Detecção de Espúrios e Predição de Propagação de Incêndios (D+1) — **com Dados Abertos**

> **Objetivo do projeto**  
> Entregar (1) um **filtro de espúrios** que reduz falsos positivos em focos de calor de satélite e (2) um **mapa diário de probabilidade de propagação (D+1)** para apoiar o direcionamento de recursos de combate — **sem depender de dados do CENSIPAM**, usando apenas fontes públicas.

---

## Entregáveis (TL;DR)
1. **Módulo A (Espúrios)**: script `filter_spurious.py` que lê CSV de focos (FIRMS/INPE) e devolve `is_spurious`, `score` e `motivo` (`persistência`, `POI`, `flare`, etc.), além de um GeoPackage para inspeção no QGIS.  
2. **Módulo B (Propagação D+1)**: script `predict_spread.py` que gera **GeoTIFF** de probabilidade D+1 e **Shapefile** com áreas de risco ≥ τ (p.ex., 0.6), mais CSV de área por município/UC.  
3. **Relatório/figuras**: mapas temáticos, PR-curves, IoU, Brier score e ablações.

---

## Requisitos
- Python 3.10+ (recomendado), conda/venv.  
- Bibliotecas: `geopandas`, `shapely`, `pyproj`, `rasterio`, `rioxarray`, `xarray`, `dask`, `scikit-learn`, `lightgbm`/`xgboost`, `torch` (opcional p/ DL), `tqdm`.  
- **QGIS** (visualização).  
- Conta **NASA Earthdata** (necessária para alguns downloads).

### Instalação sugerida
```bash
# Ambiente (conda)
conda create -n fireml python=3.10 -y
conda activate fireml

# Geoespacial base
conda install -c conda-forge geopandas rasterio rioxarray pyproj shapely xarray dask -y

# ML
pip install scikit-learn lightgbm xgboost tqdm

# (Opcional) Deep learning e notebooks
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121  # ajuste para sua GPU/CPU
pip install jupyterlab
```

---

## Estrutura de repositório (sugerida para Claude/VS Code)
```
project-root/
  README.md
  requirements.txt
  configs/
    default.yaml            # AOI, datas, resoluções, thresholds, etc.
  data_ingest/              # scripts de download/preparo
  features/                 # engenharia de features (tabulares/rasters)
  models/                   # treino dos modelos
  inference/                # inferência D+1 + export de GeoTIFF/Shapes
  eval/                     # métricas, curvas, tabelas
  notebooks/                # exploração pontual
  assets/                   # figuras para relatório
```

---

## Passo 0 — Definir **AOI + período + resolução**
- **AOI** (área piloto): ex.: Sul do AM ou Leste do PA.  
- **Período**: 2 estações secas (ex.: 2023 e 2024) para treinar/testar sazonalmente.  
- **Resolução-alvo**: 250–500 m (casa com MODIS queimada e torna o fluxo leve).

---

## Passo 1 — **Dados abertos** (links oficiais)

### Focos ativos (hotspots)
- **NASA FIRMS — mapa e download**:  
  - Portal: https://firms.modaps.eosdis.nasa.gov/  
  - Download (histórico/CSV/SHAPE/JSON): https://firms.modaps.eosdis.nasa.gov/download/  
  - Página de produtos ativos: https://firms.modaps.eosdis.nasa.gov/active_fire/  
  - Visão geral em Earthdata: https://www.earthdata.nasa.gov/data/tools/firms

### Área queimada (verdade-terreno histórica)
- **MODIS MCD64A1 v6.1 (500 m, mensal)**:  
  - Catálogo Earthdata: https://www.earthdata.nasa.gov/data/catalog/lpcloud-mcd64a1-061  
  - Guia do usuário (PDF): https://lpdaac.usgs.gov/documents/1006/MCD64_User_Guide_V61.pdf  
  - Dataset no Google Earth Engine (GEE): https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1

### Imagens ópticas de contexto (patches)
- **Sentinel‑2 SR Harmonized (L2A)** no GEE:  
  - Coleção harmonizada (recomendado): https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED  
  - Nota sobre coleções harmonizadas: https://developers.google.com/earth-engine/datasets/catalog/sentinel-2

### Relevo
- **SRTM (30 m)**:
  - Earthdata/USGS: https://www.earthdata.nasa.gov/data/instruments/srtm  
  - OpenTopography (GL1 30 m): https://portal.opentopography.org/raster?opentopoID=OTSRTM.082015.4326.1  
  - Downloader (Earthdata login): https://dwtkns.com/srtm30m/

### Uso/Cobertura do solo (combustível) — Brasil
- **MapBiomas** (Coleção 10; plataforma e downloads):  
  - Plataforma: https://plataforma.brasil.mapbiomas.org/  
  - Coleções/GEE assets: https://brasil.mapbiomas.org/en/colecoes-mapbiomas/  
  - Downloads: https://brasil.mapbiomas.org/en/downloads/  
  - MapBiomas 10 m (beta): https://brasil.mapbiomas.org/en/mapbiomas-cobertura-10m/

### Meteorologia (histórico e previsão)
- **ERA5** (reanálise) — Copernicus CDS:  
  - Portal: https://cds.climate.copernicus.eu/  
  - Documentação ERA5 (ECMWF): https://confluence.ecmwf.int/x/wv2NB  
  - Catálogo “ERA5 complete” e instalação da API: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-complete?tab=d_download  
  - Estatísticas diárias derivadas: https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics
- **GFS** (previsão em GRIB2) — NOAA/NCEP:  
  - NOMADS (listas/consulta): https://nomads.ncep.noaa.gov/  
  - Guia rápido de download seletivo (GRIB2): https://nomads.ncep.noaa.gov/info.php?page=fastdownload  
  - Inventário GFS: https://www.nco.ncep.noaa.gov/pmb/products/gfs/

### Pontos de Interesse (POIs) para identificar espúrios
- **OpenStreetMap / Overpass**:  
  - Overpass Turbo: https://overpass-turbo.eu/  
  - Guia Overpass Turbo: https://wiki.openstreetmap.org/wiki/Overpass_turbo  
  - Guia da linguagem Overpass QL: https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
- **Flares (fontes quentes persistentes)**:  
  - VIIRS Nightfire (EOG/Payne Institute): https://eogdata.mines.edu/download_viirs_fire.html  
  - Sobre VNF v4.0: https://eogdata.mines.edu/products/vnf/vnf_v40.html

### Alternativa nacional (opcional/checagem)
- **INPE/Programa Queimadas**:  
  - Portal TerraBrasilis: https://terrabrasilis.dpi.inpe.br/queimadas/portal/  
  - Dados abertos (CSV/KML): https://data.inpe.br/queimadas/pages/secao_downloads/dados-abertos/
  
### Ferramentas de estudo/prática
- **Google Earth Engine (GEE)**:  
  - Visão geral: https://developers.google.com/earth-engine/guides  
  - Get Started: https://developers.google.com/earth-engine/guides/getstarted  
  - Plataforma: https://earthengine.google.com/
- **QGIS** (manual oficial): https://docs.qgis.org/latest/en/docs/training_manual/index.html  
- **Rasterio**: https://rasterio.readthedocs.io/  
- **GeoPandas**: https://geopandas.org/en/stable/docs.html  
- **Xarray** (User Guide): https://docs.xarray.dev/en/stable/user-guide/index.html  
- **rioxarray clip**: https://corteva.github.io/rioxarray/stable/examples/clip_geom.html

---

## Passo 2 — **Checklist de início rápido (60–90 min)**
1. Defina **AOI + período** (duas secas).  
2. Baixe **FIRMS (CSV)** e **MCD64A1 (GeoTIFF)** do AOI.  
3. Gere **persistência** de focos por coordenada e **distâncias a POIs (OSM/Overpass)**.  
4. Marque espúrios com regras iniciais e exporte CSV/GeoPackage.  
5. Monte um **baseline de propagação D+1** (autômato logístico) e exporte **GeoTIFF**; avalie com IoU contra MCD64A1 (dia seguinte).

---

## Módulo A — Classificação de **Espúrios** (7 passos didáticos)

**Meta:** receber CSV de hotspots e devolver `is_spurious` + `score` + `motivo`, sem matar *recall* de focos verdadeiros.

### A.1 Amostragem
- Baixe **hotspots FIRMS** (2 anos) do AOI.  
- Para cada foco, recorte um **patch Sentinel‑2** (ex.: 256×256 m) com bandas `B2,B3,B4,B11,B12` (RGB + SWIR).  
- Guarde atributos tabulares: **FRP**, `confidence`, `daynight`, `lat`, `lon`, `date`.

### A.2 Rotulagem fraca (rápida e eficaz)
- **Persistência**: mesmo ponto acende **vários dias seguidos** (ex.: ≥10 dias/mês) → suspeito de espúrio.  
- **POIs**: distância ≤ **1–2 km** de `power=plant + source=solar`, `refinery=*`, `industrial=*`, `man_made=works`, `port=*`.  
- **Flares**: coincidência com **VIIRS Nightfire** → espúrio confirmado.  
- Faça **checagem visual amostral** no Sentinel‑2 para corrigir casos limítrofes.

### A.3 Features
- **Tabular:** FRP, confidence, **nº dias consecutivos**, distâncias a POIs, classe de uso do solo (MapBiomas), distância a áreas urbanas/rodovias.  
- **Patch (opcional):** entrada para CNN (EfficientNet-B0/B2 com 5 canais).

### A.4 Baselines
- **Regra (MVP):** `is_spurious = (persistência ≥ 10) OR (dist_POI ≤ 1km) OR (em_catálogo_flare)`  
- **GBM (rápido e forte):** LightGBM/XGBoost só com features tabulares.

### A.5 CNN opcional (híbrido)
- Fine‑tuning de EfficientNet com 5 canais; combine escores: `score_final = α·score_CNN + (1−α)·score_tabular`.

### A.6 Validação (o que importa)
- Foque em **precision da classe espúrio** (evitar descartar fogo real).  
- **Split espacial** (treina em sub‑regiões, testa em outras) para provar generalização.  
- Relate **PR‑curve/AUPRC** e matriz de confusão por bioma/estação.

### A.7 Saídas
- `hotspots_labeled.gpkg` para QGIS e um CSV com `is_spurious`, `score`, `motivo`.

#### Exemplo de consulta Overpass (usinas solares no Pará)
```ql
[out:json][timeout:25];
area[name="Pará"]->.a;
(
  node[power=plant][source=solar](area.a);
  way[power=plant][source=solar](area.a);
  relation[power=plant][source=solar](area.a);
);
out center;
```

#### Esboço de código para persistência e distância a POIs
```python
import pandas as pd, geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer

# 1) Carregar focos (lat, lon, date, frp, confidence...)
df = pd.read_csv("fires.csv", parse_dates=["acq_date"])
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")

# 2) Calcular persistência por célula (agrupa por ~100 m, ou por lat/lon arredondado)
df["lat_r"] = df["latitude"].round(3)
df["lon_r"] = df["longitude"].round(3)
persist = df.groupby(["lat_r","lon_r","acq_date"]).size().groupby(level=[0,1]).size()
# persistência aproximada (dias distintos com foco)
df = df.merge(persist.rename("persistence").reset_index()[["lat_r","lon_r","persistence"]], on=["lat_r","lon_r"], how="left")

# 3) Distância a POIs (ex.: usinas/refinarias) já em GeoDataFrame "pois" (projetar para metros)
gdf_m = gdf.to_crs(3857)
pois = gpd.read_file("pois.geojson").to_crs(3857)
gdf_m["dist_poi_m"] = gdf_m.geometry.apply(lambda p: pois.distance(p).min())

# 4) Regra MVP
gdf_m["is_spurious"] = (gdf_m["persistence"]>=10) | (gdf_m["dist_poi_m"]<=1000.0)
gdf_m.to_file("hotspots_labeled.gpkg", driver="GPKG")
```

---

## Módulo B — **Predição de Propagação D+1** (7 passos didáticos)

**Meta:** gerar **GeoTIFF** diário de probabilidade de queima em D+1 + **shapefile** com áreas de maior risco (p≥τ).

### B.1 Grid base
- Construa uma **grade regular** (p.ex., 250 m).

### B.2 Alvo (y)
- A partir do **MCD64A1 (BurnDate)**, marque se **cada célula queimou em D+1** (binário).

### B.3 Entradas (X) no dia D
- **Estado anterior** (vizinhança com fogo ativo).  
- **Meteorologia**: vento 10 m (u,v), temperatura, umidade, precipitação (ERA5 histórico; GFS para previsão).  
- **Relevo**: declividade/aspecto (SRTM).  
- **Combustível**: uso do solo (MapBiomas) e umidade da vegetação (NDMI de Sentinel‑2, opcional).

### B.4 Baseline interpretável (Autômato Logístico)
- Probabilidade **p = σ(βᵀx)**, onde `x` inclui:  
  - Presença de fogo nas **8 vizinhas**,  
  - **Vento na direção** da célula,  
  - **Declividade** a favor do avanço,  
  - **Chuvas/umidade** (efeito negativo),  
  - **Tipo de vegetação** (peso por combustível).
- Ajuste **β por regressão logística** (treino 1–2 anos; teste no ano seguinte).

### B.5 Deep Learning (opcional)
- **ConvLSTM/UNet-LSTM** com pilhas de 3–5 dias de variáveis. Use como experimento complementar.

### B.6 Avaliação
- **IoU (Jaccard)** entre previsto vs. queimado observado.  
- **Brier score** e **reliability diagram** (calibração).  
- **Ablations**: sem vento, sem slope, etc.

### B.7 Saídas
- `prob_spread_d1.tif` (0–1), `risk_zones.shp` (p≥τ) e CSV com área por município/UC.

#### Pseudocódigo do autômato logístico (treino/inferência)
```python
# X[t] : features por célula no dia t (vizinhança fogo, vento proj., slope, chuva, classe de uso...)
# y[t+1]: 1 se queimou em t+1 (derivado de MCD64A1)
# Treino (regressão logística)
beta = fit_logistic(X_train, y_train, sample_weight=None)

# Inferência para D+1
p = sigmoid(X_D @ beta)   # probabilidade por célula
save_geotiff("prob_spread_d1.tif", p, profile=grid_profile)
save_shapes("risk_zones.shp", p>=0.6)
```

---

## Visualização no QGIS
1. Abra `hotspots_labeled.gpkg` e `prob_spread_d1.tif`.  
2. Estilize o raster com paleta contínua (0–1) e sobreponha **setas de vento** (vetor) para contexto.  
3. Exporte **mapas** (Layout) e **tabelas** (áreas p≥τ por município).  
4. Salve suas simbologias (`.qml`) em `assets/` para reuso.

---

## Validação e relato
- **Espúrios**: foque em *precision* da classe negativa (espúrio) e mantenha *recall* de “fogo real”.  
- **Propagação**: reporte **IoU**, **Brier score**, **calibração** e **ablação** por variável.  
- **Generalização**: faça **splits espaciais/temporais** (biomas diferentes; estação chuvosa vs. seca).

---

## Escrever a dissertação (sugestão de seções)
1. **Dados e Licenças** (fontes, versões, limitações).  
2. **Metodologia**: Módulo A (heurísticas + GBM + CNN), Módulo B (CA logístico + DL opcional).  
3. **Resultados**: tabelas/figuras por bioma/estação; mapas de risco; curvas PR/IoU.  
4. **Discussão**: erros típicos (ex.: fumaça fina/nuven, queimadas agrícolas); sensibilidade a vento/combustível.  
5. **Validação externa**: quando/SE dados CENSIPAM forem liberados (como *hold‑out* extra).

---

## Referências de estudo (essenciais)
- **FIRMS (NASA LANCE/Active Fire)**: https://firms.modaps.eosdis.nasa.gov/ | https://firms.modaps.eosdis.nasa.gov/download/ | https://firms.modaps.eosdis.nasa.gov/active_fire/ | https://www.earthdata.nasa.gov/data/tools/firms  
- **MCD64A1 v6.1 (Burned Area)**: https://www.earthdata.nasa.gov/data/catalog/lpcloud-mcd64a1-061 | https://lpdaac.usgs.gov/documents/1006/MCD64_User_Guide_V61.pdf | https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1  
- **Sentinel‑2 SR (HARMONIZED)**: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED | https://developers.google.com/earth-engine/datasets/catalog/sentinel-2  
- **ERA5 (CDS/ECMWF)**: https://cds.climate.copernicus.eu/ | https://confluence.ecmwf.int/x/wv2NB | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-complete?tab=d_download  
- **GFS (NOAA/NCEP)**: https://nomads.ncep.noaa.gov/ | https://nomads.ncep.noaa.gov/info.php?page=fastdownload | https://www.nco.ncep.noaa.gov/pmb/products/gfs/  
- **SRTM (USGS/NASA)**: https://www.earthdata.nasa.gov/data/instruments/srtm | https://portal.opentopography.org/raster?opentopoID=OTSRTM.082015.4326.1 | https://dwtkns.com/srtm30m/  
- **MapBiomas**: https://plataforma.brasil.mapbiomas.org/ | https://brasil.mapbiomas.org/en/colecoes-mapbiomas/ | https://brasil.mapbiomas.org/en/downloads/ | https://brasil.mapbiomas.org/en/mapbiomas-cobertura-10m/  
- **INPE/Queimadas**: https://terrabrasilis.dpi.inpe.br/queimadas/portal/ | https://data.inpe.br/queimadas/pages/secao_downloads/dados-abertos/  
- **Overpass/OSM**: https://overpass-turbo.eu/ | https://wiki.openstreetmap.org/wiki/Overpass_turbo | https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide  
- **VIIRS Nightfire (EOG)**: https://eogdata.mines.edu/download_viirs_fire.html | https://eogdata.mines.edu/products/vnf/vnf_v40.html  
- **GEE (Docs/Start)**: https://developers.google.com/earth-engine/guides | https://developers.google.com/earth-engine/guides/getstarted | https://earthengine.google.com/  
- **Ferramentas**: QGIS https://docs.qgis.org/latest/en/docs/training_manual/index.html | Rasterio https://rasterio.readthedocs.io/ | GeoPandas https://geopandas.org/en/stable/docs.html | Xarray https://docs.xarray.dev/en/stable/user-guide/index.html | rioxarray clip https://corteva.github.io/rioxarray/stable/examples/clip_geom.html  

### Papers-base (para fundamentação teórica)
- **ConvLSTM** (Shi et al., NeurIPS 2015): https://proceedings.neurips.cc/paper/5955-convolutional-lstm-network-a-machine-learningapproach-for-precipitation-nowcasting.pdf  
- **U‑Net** (Ronneberger et al., 2015): https://arxiv.org/pdf/1505.04597  
- **FARSITE** (modelo físico, USFS): https://research.fs.usda.gov/treesearch/4617 (doc) | https://www.frames.gov/documents/behaveplus/publications/Finney_1998_RMRS-RP-4.pdf

---

## Receitas rápidas

### (R1) Baixar FIRMS (CSV histórico)
- Portal: https://firms.modaps.eosdis.nasa.gov/download/ (requer login Earthdata ou código por e‑mail).  
- Filtre por país/ano/sensor e exporte CSV.

### (R2) MCD64A1 no Google Earth Engine
- Dataset: `MODIS/061/MCD64A1` (banda `BurnDate`).  
- Use `reduceRegion`/`clip` para seu AOI e exporte GeoTIFF.

### (R3) Sentinel‑2 SR (GEE)
- Dataset: `COPERNICUS/S2_SR_HARMONIZED`.  
- Use `SCL`/CloudScore+ (se disponível) para máscara de nuvem; gere mosaicos mensais e exporte **patches**.

### (R4) ERA5 (CDS API)
- Instale e configure a **CDS API**, baixe **u10, v10, t2m, tp** agregados diários na sua região.

### (R5) SRTM → declividade/aspecto
- Derive com `gdaldem` ou via `rioxarray`/`richdem` e salve como GeoTIFF.

### (R6) Overpass (POIs)
- Use a consulta de exemplo (acima) para extrair usinas solares, refinarias e parques industriais; exporte GeoJSON.

---

## Cronograma enxuto (4 semanas sugeridas)
- **Sem 1:** ingestão (FIRMS, MCD64A1, SRTM, MapBiomas, ERA5) + AOI.  
- **Sem 2:** Módulo A (regras + GBM) → matriz de confusão por bioma.  
- **Sem 3:** Módulo B (autômato logístico) → mapas D+1 + IoU/Brier.  
- **Sem 4:** ablações, figuras, escrita e discussão.

---

## Notas de licença e citação
- Respeite as licenças de cada provedora (NASA/NOAA/ESA/MapBiomas/INPE).  
- Cite **datasets e versões** usadas (ex.: “MODIS MCD64A1 v6.1, LP‑DAAC”).  
- Para VIIRS Nightfire, siga as instruções de crédito do **Earth Observation Group, Payne Institute**.

---

**Pronto.** Este README é “drop‑in” para o seu repositório (Claude/VS Code) e já contém o passo‑a‑passo, consultas, pseudocódigos e **links oficiais** para você executar os dois módulos e escrever a dissertação.
