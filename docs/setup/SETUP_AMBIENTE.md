# Setup do Ambiente - Guia Completo

**Data**: 11 de novembro de 2025
**Status**: Pronto para começar

---

## 1. Ambiente Python

### Criar Ambiente
```bash
conda create -n fireml python=3.10 -y
conda activate fireml
```

### Instalar Dependências Geoespaciais
```bash
conda install -c conda-forge geopandas rasterio rioxarray pyproj shapely xarray dask -y
```

### Instalar Machine Learning
```bash
pip install scikit-learn lightgbm xgboost pandas numpy tqdm
```

### Instalar APIs
```bash
pip install earthengine-api cdsapi python-dotenv requests
```

### Verificar Instalação (Opcional)
```bash
python -c "import ee, cdsapi; print('OK')"
```

---

## 2. Credenciais

Criar arquivo `.env` na pasta do projeto:

```
# NASA Earthdata
EARTHDATA_USERNAME=seu_username
EARTHDATA_PASSWORD=sua_password

# Copernicus CDS
CDS_URL=https://cds.climate.copernicus.eu/api
CDS_KEY=sua-chave-aqui
```

**Importante**: Adicione `.env` ao `.gitignore`

---

## 3. Google Earth Engine

### Passo 1: Criar Conta
Acesse: https://earthengine.google.com/

### Passo 2: Criar Projeto Google Cloud
Acesse: https://console.cloud.google.com/

1. Crie novo projeto
2. Copie o PROJECT ID

### Passo 3: Configurar Localmente
```bash
earthengine authenticate
# Siga o fluxo (abrirá navegador)

earthengine set_project SEU_PROJECT_ID
```

### Passo 4: Validar
```bash
python test_gee_fixed.py
```

---

## 4. NASA Earthdata

### Passo 1: Criar Conta
Acesse: https://urs.earthdata.nasa.gov/users/new

1. Preencha email
2. Escolha username e senha forte
3. Confirme email

### Passo 2: Salvar Credenciais
Adicione ao arquivo `.env`:
```
EARTHDATA_USERNAME=seu_username
EARTHDATA_PASSWORD=sua_password
```

### Passo 3: Validar
```bash
python test_earthdata.py
```

---

## 5. Copernicus CDS

### Passo 1: Criar Conta
Acesse: https://cds.climate.copernicus.eu/user/register

1. Preencha email
2. Escolha senha
3. Confirme email

### Passo 2: Gerar Credenciais
1. Faça login em https://cds.climate.copernicus.eu/
2. Vá em Profile > API credentials
3. Copie URL e KEY

### Passo 3: Salvar Credenciais
Adicione ao arquivo `.env`:
```
CDS_URL=https://cds.climate.copernicus.eu/api
CDS_KEY=sua-chave-aqui
```

### Passo 4: Aceitar Licença
Acesse: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download#manage-licences

Clique em "Accept licence"

### Passo 5: Validar
```bash
python test_cds.py
```

---

## 6. Estrutura de Diretórios

Criar estrutura recomendada:

```
Projeto Mestrado/
├── .env
├── .gitignore
├── requirements.txt
│
├── data/
│   ├── raw/
│   │   ├── firms_hotspots/
│   │   ├── mcd64a1/
│   │   ├── sentinel2/
│   │   ├── era5/
│   │   └── aoi/
│   └── processed/
│
├── src/
│   ├── data_ingest/
│   ├── preprocessing/
│   ├── module_a/
│   └── module_b/
│
├── notebooks/
├── outputs/
└── docs/
```

---

## 7. Verificação Final

Execute todos os testes:

```bash
python test_gee_fixed.py
python test_earthdata.py
python test_cds.py
```

Resultado esperado: Todos passando

---

## 8. Próxima Etapa

Começar SEMANA 1 - Ingestão de Dados:

```bash
python src/data_ingest/run_all_downloads.py
```

---

**Tempo total**: ~30 minutos (sem esperar aprovações)
**Aprovações**: 24-48 horas para GEE (depende)
