# Guia de Configuração de Credenciais e Ambiente

**Objetivo**: Configurar acesso às três plataformas essenciais para o projeto

**Tempo estimado**: 15-20 minutos (criação de contas + confirmação de email)

---

## 1. Google Earth Engine (GEE)

### O que você vai usar:
- Acesso a datasets MODIS, Sentinel-2, Landsat, SRTM, ERA5 e MapBiomas
- Processamento em cloud de imagens de satélite
- Python API para programação

### Passo a Passo

#### 1.1 Criar Conta
1. Acesse: https://earthengine.google.com/
2. Clique em **"Sign Up"** (canto superior direito)
3. Use sua conta Google (ou crie uma nova)
4. Leia e aceite os Termos de Serviço
5. **Clique em "Sign Up"** para solicitar acesso

#### 1.2 Aguardar Aprovação
- Normalmente 24-48 horas
- Você receberá um email confirmando acesso
- Verifique spam se não receber em 2 dias

#### 1.3 Instalar Python API
```bash
# Ativar seu ambiente conda/venv
conda activate fireml  # ou source venv/bin/activate

# Instalar ee package
pip install earthengine-api
```

#### 1.4 Autenticar no Python
```bash
# Terminal/PowerShell
earthengine authenticate

# Isso abrirá um navegador para autorizar
# Copie o token fornecido e cole no terminal
```

#### 1.5 Testar Conexão
```python
import ee

# Inicializar
ee.Initialize()

# Testar acesso a um dataset
image = ee.Image('COPERNICUS/S2/20220101T104131_20220101T105140_T32UQD')
print(image.getInfo())
```

**✅ Sucesso**: Se não houver erro, você está conectado!

---

## 2. NASA Earthdata

### O que você vai usar:
- FIRMS hotspots (detecção ativa de fogo)
- MODIS burned area products
- SRTM digital elevation model
- Outros dados NASA

### Passo a Passo

#### 2.1 Criar Conta
1. Acesse: https://urs.earthdata.nasa.gov/users/new
2. Preencha:
   - **Username**: (qualquer nome único)
   - **Email**: (seu email)
   - **Password**: (mínimo 12 caracteres)
3. Clique **"Sign Up"**
4. Confirme seu email (verifique a caixa de entrada)

#### 2.2 Gerar Credenciais de API
1. Faça login em: https://urs.earthdata.nasa.gov/
2. Vá para: **"User Profile"** (canto superior direito) → **"My Applications"**
3. Clique em **"Generate Token"**
4. Copie e guarde seu **Bearer Token** (será usado depois)

#### 2.3 Salvar Credenciais Seguramente

**Opção A: Arquivo .netrc (recomendado para scripts)**
```bash
# Windows: Criar arquivo C:\Users\[SEU_USER]\.netrc
# Linux/Mac: Criar arquivo ~/.netrc

# Conteúdo:
machine urs.earthdata.nasa.gov
    login [SEU_USERNAME]
    password [SUA_PASSWORD]

# Depois no Windows:
# Clic direito no arquivo → Propriedades → Segurança
# Remova acesso de "Outros usuários"
```

**Opção B: Arquivo .env (para desenvolvimento)**
```bash
# Na raiz do seu projeto, criar arquivo .env
EARTHDATA_USERNAME=seu_username
EARTHDATA_PASSWORD=sua_password

# Instalar python-dotenv
pip install python-dotenv

# No seu script Python:
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('EARTHDATA_USERNAME')
password = os.getenv('EARTHDATA_PASSWORD')
```

#### 2.4 Testar Acesso aos Dados FIRMS
```python
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('EARTHDATA_USERNAME')
password = os.getenv('EARTHDATA_PASSWORD')

# Teste: baixar dados FIRMS recentes
url = 'https://firms.modaps.eosdis.nasa.gov/api/area/csv/FIRMS_VIIRS_NRT/-60.5/-58.5/-2/-4.5/1/'

response = requests.get(url, auth=HTTPBasicAuth(username, password))
print(f"Status: {response.status_code}")
print(response.text[:500])  # Primeiras linhas
```

**✅ Sucesso**: Se Status = 200 e você vir dados CSV, está funcionando!

---

## 3. Copernicus Climate Data Store (CDS)

### O que você vai usar:
- ERA5: Dados meteorológicos históricos (temperatura, precipitação, vento, umidade)
- Resolução: 0.25° (~25km), horário
- Cobertura: 1950-presente (praticamente real-time com 5 dias de delay)

### Passo a Passo

#### 3.1 Criar Conta
1. Acesse: https://cds.climate.copernicus.eu/user/register
2. Preencha:
   - **Email**: (seu email)
   - **Password**: (mínimo 8 caracteres)
3. Aceite Termos de Serviço
4. Clique **"Register"**
5. **Confirme seu email** (check inbox)

#### 3.2 Gerar Credenciais de API
1. Faça login em: https://cds.climate.copernicus.eu/
2. Vá para: **"Profile"** (canto superior direito)
3. Clique em **"Copy credentials snippet"**
4. Você verá algo como:
   ```
   URL: https://cds.climate.copernicus.eu/api/v2
   KEY: 123456:abcdef-1234567890-abcdef
   ```

#### 3.3 Salvar Credenciais

**Opção A: Arquivo .cdsapirc (recomendado)**
```bash
# Linux/Mac: ~/.cdsapirc
# Windows: C:\Users\[SEU_USER]\.cdsapirc

# Conteúdo (copiar do passo anterior):
url: https://cds.climate.copernicus.eu/api/v2
key: [sua-chave-aqui]
```

**Opção B: Arquivo .env**
```bash
# .env (mesmo que Earthdata)
CDS_URL=https://cds.climate.copernicus.eu/api/v2
CDS_KEY=sua-chave-aqui
```

#### 3.4 Instalar Cliente CDS
```bash
pip install cdsapi
```

#### 3.5 Testar Acesso
```python
import cdsapi

client = cdsapi.Client()

# Fazer requisição de teste (pequena, rápida)
request = {
    'product_type': 'reanalysis',
    'variable': ['2m_temperature'],
    'year': '2023',
    'month': '08',
    'day': '01',
    'time': '00:00',
    'format': 'netcdf',
    'area': [-4, -60, -2, -58],  # S, W, N, E (MATOPIBA subset)
}

# Isso fará download de um arquivo pequeno (~500KB)
result = client.retrieve('reanalysis-era5-single-levels', request)
result.download('test_era5.nc')
print("Download completo!")
```

**✅ Sucesso**: Se o arquivo foi baixado sem erros, está funcionando!

---

## 4. Configuração do Ambiente Python

### 4.1 Criar Ambiente Conda
```bash
# Criar ambiente
conda create -n fireml python=3.10 -y
conda activate fireml

# Atualizar pip
pip install --upgrade pip
```

### 4.2 Instalar Dependências Geoespaciais
```bash
# Instalar do conda-forge (melhor compatibilidade)
conda install -c conda-forge \
    geopandas \
    rasterio \
    rioxarray \
    pyproj \
    shapely \
    xarray \
    dask \
    -y
```

### 4.3 Instalar ML e Utilities
```bash
pip install \
    scikit-learn \
    lightgbm \
    xgboost \
    pandas \
    numpy \
    tqdm \
    requests \
    python-dotenv
```

### 4.4 Instalar APIs
```bash
pip install \
    earthengine-api \
    cdsapi
```

### 4.5 (Opcional) Instalar Deep Learning
```bash
# Se quiser usar PyTorch para Module B (ConvLSTM)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install jupyterlab  # Para notebooks
```

### 4.6 Criar requirements.txt
```bash
# Gerar arquivo de dependências
pip freeze > requirements.txt

# Depois, qualquer um pode instalar com:
# pip install -r requirements.txt
```

---

## 5. Estrutura de Pastas Recomendada

```
Projeto Mestrado/
├── CLAUDE.md                    # Guia para Claude Code
├── PROJETO_SETUP.md             # Este arquivo (configuração)
├── CREDENCIAIS_SETUP.md         # Setup de credenciais
├── README-fire-open-data-pipeline.md
├── .env                         # ⚠️ NÃO COMMITAR NO GIT
├── .gitignore                   # Incluir .env, .cdsapirc
├── requirements.txt             # Dependências Python
│
├── data/
│   ├── raw/                     # Dados brutos baixados
│   │   ├── firms_hotspots/      # Hotspots FIRMS (2022-2024)
│   │   ├── mcd64a1/             # MODIS burned area
│   │   ├── sentinel2/           # Composites Sentinel-2
│   │   ├── dem/                 # SRTM elevation
│   │   └── era5/                # Dados meteorológicos
│   │
│   ├── processed/               # Dados processados
│   │   ├── features_module_a/   # Features para Module A
│   │   ├── features_module_b/   # Features para Module B
│   │   └── labels/              # Ground truth labels
│   │
│   └── aoi/
│       └── matopiba.shp         # Shapefile da AOI
│
├── src/
│   ├── __init__.py
│   ├── data_ingest.py           # Scripts de ingestão
│   ├── preprocessing.py         # Processamento de dados
│   ├── feature_engineering.py   # Feature engineering
│   ├── module_a/                # Detecção de espúrios
│   │   ├── weak_labeling.py
│   │   ├── training.py
│   │   └── inference.py
│   └── module_b/                # Propagação D+1
│       ├── grid_generation.py
│       ├── training.py
│       └── inference.py
│
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_module_a_development.ipynb
│   └── 03_module_b_development.ipynb
│
├── outputs/
│   ├── models/                  # Modelos treinados
│   ├── results/                 # Resultados (mapas, CSVs)
│   └── figures/                 # Figuras para tese
│
└── docs/
    └── references.bib           # Referências bibliográficas
```

---

## 6. Checklist de Configuração

### Antes de Começar
- [ ] Criar contas nas 3 plataformas (GEE, NASA Earthdata, CDS)
- [ ] Obter credenciais e salvar seguramente
- [ ] Instalar Conda ou venv
- [ ] Criar ambiente Python 3.10
- [ ] Instalar bibliotecas principais
- [ ] Criar estrutura de pastas

### Validação
- [ ] `earthengine authenticate` funcionando
- [ ] NASA Earthdata retornando dados FIRMS
- [ ] CDS API fazendo download de ERA5
- [ ] `requirements.txt` gerado
- [ ] `.env` em `.gitignore`

### Pronto para Começar
- [ ] Ambiente Python testado e validado
- [ ] Todos os credenciais funcionando
- [ ] Estrutura de pastas criada
- [ ] Primeiro script de teste executado com sucesso

---

## 7. Troubleshooting

### GEE: Erro "Not Authenticated"
```python
# Solução:
# 1. Terminal: earthengine authenticate
# 2. Copie o token COMPLETO (incluindo colchetes se houver)
# 3. Cole no terminal
# 4. Reinicie Python
```

### NASA Earthdata: Erro 401 (Unauthorized)
```python
# Solução:
# 1. Verifique credenciais em .env ou .netrc
# 2. Tente criar novas credenciais no site
# 3. Aguarde 5 minutos (às vezes há delay)
```

### CDS: Erro "Request is queued"
```
Solução: Requisições grandes são enfileiradas
- Comece com data/área pequena para testar
- CDS pode levar horas para processar, verificar email
```

### Problema: Módulos Python não encontrados
```bash
# Verificar ambiente ativo:
conda activate fireml
# Ou:
source venv/bin/activate

# Reinstalar:
pip install --force-reinstall geopandas
```

---

## 8. Segurança: Boas Práticas

### ✅ DO:
- [ ] Salvar credenciais em `.env` ou arquivo local `.netrc`
- [ ] Adicionar `.env` ao `.gitignore`
- [ ] Usar variáveis de ambiente em scripts
- [ ] Rotacionar tokens/credenciais periodicamente
- [ ] Nunca commitar credenciais no Git

### ❌ DON'T:
- [ ] Hardcoding de credenciais no código
- [ ] Compartilhar `.env` ou `.netrc`
- [ ] Fazer upload de credenciais em repositórios públicos
- [ ] Usar credenciais de produção em desenvolvimento

---

## 9. Próximas Etapas

Após completar este setup:

1. **Semana 1**: Começar ingestão de dados
   - Script para baixar FIRMS hotspots
   - Script para acessar Sentinel-2 via GEE
   - Script para baixar ERA5 via CDS

2. **Semana 2**: Module A (detecção de espúrios)
3. **Semana 3**: Module B (propagação D+1)
4. **Semana 4**: Visualização e dissertação

---

**Tempo total estimado**: 15-20 minutos de trabalho manual + 24-48 horas de espera por aprovação

**Após aprovação**: Pronto para começar a ingestão de dados! 🚀

---

**Última Atualização**: 11 de novembro de 2025
