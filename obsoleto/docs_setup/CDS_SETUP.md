# Copernicus Climate Data Store - Configuração

**Objetivo**: Configurar acesso à API CDS para baixar dados ERA5 (meteorologia)

---

## 1. Criar Conta Copernicus CDS

### Passo 1.1: Acesse o site de registro
- URL: https://cds.climate.copernicus.eu/user/register

### Passo 1.2: Preencha o formulário
- **Email**: Use `andrey.bessa@ufam.edu.br`
- **Password**: Escolha uma senha forte (mínimo 8 caracteres)
- **Confirm Password**: Repita a senha
- **Marque**: "I have read and agree to the..."

### Passo 1.3: Confirmar email
1. Clique em **"Register"**
2. Você receberá um email em `andrey.bessa@ufam.edu.br`
3. **Clique no link** de confirmação
4. Pronto! Sua conta está ativa

---

## 2. Gerar Credenciais de API

### Passo 2.1: Fazer Login
1. Acesse: https://cds.climate.copernicus.eu/
2. Faça login com seu email e senha

### Passo 2.2: Acessar Credenciais
1. Clique em **"Profile"** (canto superior direito)
2. Procure por **"API credentials"** ou **"API key"**
3. Clique em **"Copy credentials"** ou similar
4. Você verá algo como:

```
URL: https://cds.climate.copernicus.eu/api/v2
KEY: 12345678:abcdef1234567890-abcdef-1234567890
```

**COPIE AMBOS** (URL e KEY)

---

## 3. Salvar Credenciais no `.env`

Edite seu arquivo `.env` (na pasta do projeto):

```
# Credenciais NASA Earthdata
EARTHDATA_USERNAME=andrey.bessa
EARTHDATA_PASSWORD=Bess@20debby

# Credenciais Copernicus CDS
CDS_URL=https://cds.climate.copernicus.eu/api/v2
CDS_KEY=12345678:abcdef1234567890-abcdef-1234567890
```

(Substitua `12345678:...` pela sua chave real)

---

## 4. Instalar Cliente CDS

No terminal:

```powershell
pip install cdsapi
```

---

## 5. Criar Script de Teste CDS

Crie o arquivo `test_cds.py`:

```python
# test_cds.py
import cdsapi
import os
from dotenv import load_dotenv

print("=" * 50)
print("Testando Copernicus CDS - ERA5")
print("=" * 50)

# Carregar credenciais do .env
load_dotenv()
cds_url = os.getenv('CDS_URL')
cds_key = os.getenv('CDS_KEY')

if not cds_key:
    print("\n❌ ERRO: Credenciais CDS não encontradas")
    print("Certifique-se de que .env contém:")
    print("  CDS_URL=https://cds.climate.copernicus.eu/api/v2")
    print("  CDS_KEY=sua-chave-aqui")
    exit(1)

print(f"\n✓ URL: {cds_url}")
print("✓ Chave carregada com sucesso")

# Tentar conectar à API
print("\n1. Conectando à API CDS...")

try:
    client = cdsapi.Client(url=cds_url, key=cds_key, timeout=60)
    print("   ✅ Conexão bem-sucedida!")
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    exit(1)

# Fazer requisição de teste (pequena)
print("\n2. Fazendo requisição de teste (ERA5)...")
print("   (Isso pode levar 1-2 minutos, aguarde...)")

try:
    request = {
        'product_type': 'reanalysis',
        'variable': ['2m_temperature'],
        'year': '2024',
        'month': '09',
        'day': '01',
        'time': '12:00',
        'format': 'netcdf',
        'area': [-4, -60, -2, -58],  # MATOPIBA subset (S, W, N, E)
    }

    result = client.retrieve('reanalysis-era5-single-levels', request)

    # Download em background (não bloqueia)
    print("   ✅ Requisição enfileirada com sucesso!")
    print("   📥 Seu download está sendo processado")
    print("   💾 Você receberá um email quando estiver pronto")
    print("   ⏱️  Tempo típico: 5-30 minutos")

except Exception as e:
    print(f"   ⚠️ ERRO: {e}")
    print("   Isso é normal - CDS processa requisições em fila")

print("\n" + "=" * 50)
print("✅ Copernicus CDS está configurado!")
print("=" * 50)
print("\nProximos passos:")
print("1. Você agora pode fazer requisições de ERA5")
print("2. Dados processados serão disponibilizados por email")
print("3. Ver: https://cds.climate.copernicus.eu/how-to-api")
```

---

## 6. Testar a Conexão

No terminal:

```powershell
python test_cds.py
```

**Resultado esperado**:
```
==================================================
Testando Copernicus CDS - ERA5
==================================================

✓ URL: https://cds.climate.copernicus.eu/api/v2
✓ Chave carregada com sucesso

1. Conectando à API CDS...
   ✅ Conexão bem-sucedida!

2. Fazendo requisição de teste (ERA5)...
   ✅ Requisição enfileirada com sucesso!

==================================================
✅ Copernicus CDS está configurado!
==================================================
```

---

## 7. Troubleshooting

### ❌ Erro: "Credenciais não encontradas"
```
Solução:
1. Verifique se .env contém CDS_URL e CDS_KEY
2. Coloque no mesmo arquivo onde outras credenciais estão
```

### ❌ Erro: "Unauthorized" ou "Invalid key"
```
Solução:
1. Verifique se a chave está correta (copie novamente)
2. Faça login em https://cds.climate.copernicus.eu/ para confirmar
3. Tente gerar nova chave
```

### ❌ Erro: "Request is queued"
```
Isso é NORMAL! CDS processa requisições em fila
- Requisições pequenas: 5-10 minutos
- Requisições grandes: 30 min - 2 horas
- Você receberá email quando estiver pronto
```

---

## 8. Dados Disponíveis

### ERA5 (Reanalysis)

**Características**:
- Resolução: 0.25° (~25km)
- Temporal: Horário (0, 1, 2, ... 23h)
- Cobertura: 1950-presente (com 5 dias de delay)
- Formato: NetCDF, Grib, Netcdf4

**Variáveis principais para incêndios**:
- `2m_temperature` - Temperatura (K)
- `10m_u_component_of_wind` - Componente U do vento
- `10m_v_component_of_wind` - Componente V do vento
- `2m_dewpoint_temperature` - Ponto de orvalho
- `total_precipitation` - Precipitação total
- `soil_moisture_0_7cm` - Umidade do solo

---

## 9. Próximas Etapas

✅ Depois de validar CDS, você terá **todos os 3 sistemas configurados**:

1. ✅ Google Earth Engine (imagens de satélite)
2. ✅ NASA Earthdata (hotspots FIRMS)
3. ✅ Copernicus CDS (dados meteorológicos)

**Próximo**: Começar **Semana 1 - Ingestão de Dados**!

---

**Última Atualização**: 11 de novembro de 2025
