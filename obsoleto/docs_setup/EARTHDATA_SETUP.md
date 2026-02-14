# NASA Earthdata - Configuração Detalhada

**Objetivo**: Configurar acesso à API FIRMS (detecção ativa de fogo)

---

## 1. Criar Conta NASA Earthdata

### Passo 1.1: Acesse o site de registro
- URL: https://urs.earthdata.nasa.gov/users/new

### Passo 1.2: Preencha o formulário
- **First Name**: Seu nome
- **Last Name**: Seu sobrenome
- **Email**: Use `andrey.bessa@ufam.edu.br`
- **User Name**: Escolha um username único (ex: `andrey.bessa`, `mestrado25`)
- **Password**: Mínimo 12 caracteres (ex: algo seguro)
  - Dica: Use uma senha forte com maiúsculas, números e caracteres especiais
- **Confirm Password**: Repita a mesma senha
- **Marque**: "I agree to the Terms of Service"

### Passo 1.3: Confirmar email
1. Clique em **"Sign up"**
2. Você receberá um email em `andrey.bessa@ufam.edu.br`
3. **Clique no link** de confirmação no email
4. Pronto! Sua conta está ativa

---

## 2. Gerar Token de API (Bearer Token)

### Passo 2.1: Fazer Login
1. Acesse: https://urs.earthdata.nasa.gov/
2. Faça login com seu **User Name** e **Password**

### Passo 2.2: Gerar Token
1. Clique em **"User Profile"** (canto superior direito)
2. Clique em **"My Applications"** ou **"Application Tokens"**
3. Clique em **"Generate Token"**
4. Uma janela vai aparecer com seu **Bearer Token**
5. **COPIE O TOKEN COMPLETO** (ele começa com um ID de números e dois pontos)

**Exemplo de token**:
```
123456789:abc123def456-ghi789jkl-mnopqrstu
```

---

## 3. Salvar Credenciais no Python

### Opção A: Arquivo `.env` (Recomendado)

Na pasta do seu projeto, crie/edite o arquivo `.env`:

```
# .env
EARTHDATA_USERNAME=seu_username_aqui
EARTHDATA_PASSWORD=sua_password_aqui
EARTHDATA_TOKEN=seu_bearer_token_aqui
```

**IMPORTANTE**: Adicione `.env` ao `.gitignore`:

```
# .gitignore
.env
.cdsapirc
*.credentials
```

### Opção B: Variáveis de Ambiente (Windows)

1. **Win + X** → **System Settings** (Configurações do Sistema)
2. **Advanced System Settings** → **Environment Variables**
3. **New** (User variables):
   - Variable name: `EARTHDATA_USERNAME`
   - Variable value: `seu_username`
4. **New**:
   - Variable name: `EARTHDATA_PASSWORD`
   - Variable value: `sua_password`

---

## 4. Instalar Dependências Python

No seu ambiente `fireml`, instale:

```powershell
pip install requests python-dotenv
```

---

## 5. Criar Script de Teste FIRMS

Crie o arquivo `test_earthdata.py`:

```python
# test_earthdata.py
import requests
import os
from dotenv import load_dotenv

print("=" * 50)
print("Testando NASA Earthdata - FIRMS")
print("=" * 50)

# Carregar credenciais do .env
load_dotenv()
username = os.getenv('EARTHDATA_USERNAME')
password = os.getenv('EARTHDATA_PASSWORD')

if not username or not password:
    print("\n❌ ERRO: Credenciais não encontradas")
    print("Certifique-se de que .env contém:")
    print("  EARTHDATA_USERNAME=seu_username")
    print("  EARTHDATA_PASSWORD=sua_password")
    exit(1)

print(f"\n✓ Usando conta: {username}")

# Testar acesso à API FIRMS
print("\n1. Testando acesso à API FIRMS...")

# Coordenadas de teste: MATOPIBA region
# S, W, N, E
url = 'https://firms.modaps.eosdis.nasa.gov/api/area/csv/FIRMS_VIIRS_NRT/-65/-15/-40/0/1/'

try:
    response = requests.get(url, auth=(username, password), timeout=10)

    if response.status_code == 200:
        lines = response.text.split('\n')
        print(f"   ✅ Conexão bem-sucedida!")
        print(f"   ✅ Dados recebidos: {len(lines)-2} registros")
        print(f"   Primeiras linhas:")
        for line in lines[:3]:
            if line:
                print(f"      {line[:80]}...")
    else:
        print(f"   ❌ ERRO: Status {response.status_code}")
        print(f"   Resposta: {response.text[:200]}")

except Exception as e:
    print(f"   ❌ ERRO: {e}")
    exit(1)

# Testar acesso a MODIS (outro dataset)
print("\n2. Testando acesso a MODIS MCD14DL...")

url_modis = 'https://firms.modaps.eosdis.nasa.gov/api/area/csv/FIRMS_MODIS_NRT/-65/-15/-40/0/1/'

try:
    response = requests.get(url_modis, auth=(username, password), timeout=10)

    if response.status_code == 200:
        lines = response.text.split('\n')
        print(f"   ✅ MODIS acessível!")
        print(f"   ✅ Registros: {len(lines)-2}")
    else:
        print(f"   ⚠️ Status {response.status_code} (pode ser que não tenha dados nesse período)")

except Exception as e:
    print(f"   ❌ ERRO: {e}")

print("\n" + "=" * 50)
print("🎉 NASA Earthdata está configurado!")
print("=" * 50)
print("\nProximos passos:")
print("1. Você agora pode baixar FIRMS hotspots")
print("2. Dados disponíveis em tempo quase real (1-2 dias de delay)")
print("3. Ver: test_firms_download.py para exemplos de download")
```

---

## 6. Testar a Conexão

No terminal, execute:

```powershell
conda activate fireml
python test_earthdata.py
```

**Resultado esperado**:
```
==================================================
Testando NASA Earthdata - FIRMS
==================================================

✓ Usando conta: seu_username

1. Testando acesso à API FIRMS...
   ✅ Conexão bem-sucedida!
   ✅ Dados recebidos: 45 registros
   Primeiras linhas:
      latitude,longitude,brightness,...

2. Testando acesso a MODIS MCD14DL...
   ✅ MODIS acessível!
   ✅ Registros: 120

==================================================
🎉 NASA Earthdata está configurado!
==================================================
```

---

## 7. Troubleshooting

### ❌ Erro: "Credenciais não encontradas"
```
Solução:
1. Verifique se .env existe na pasta do projeto
2. Verifique se contém as 3 linhas de credenciais
3. Se usar variáveis de ambiente, reinicie o terminal
```

### ❌ Erro: 401 Unauthorized
```
Solução:
1. Verifique username e password (case sensitive!)
2. Faça login em https://urs.earthdata.nasa.gov/ para confirmar
3. Tente gerar novo token
4. Aguarde 5 minutos (às vezes há delay)
```

### ❌ Erro: Timeout ou Connection refused
```
Solução:
1. Verifique sua conexão com internet
2. Tente acessar https://firms.modaps.eosdis.nasa.gov/ no navegador
3. Se o site estiver offline, aguarde
```

### ❌ Dados vazios (0 registros)
```
Solução:
1. Pode ser que não haja fogo naquele período/região
2. Tente usar datas mais recentes
3. Tente expandir a bounding box geográfica
```

---

## 8. Dados Disponíveis

### FIRMS (Fire Information and Resource Management System)

**Datasets:**
- `FIRMS_VIIRS_NRT`: NOAA/VIIRS (375m, quase real-time, 1-2 dias delay)
- `FIRMS_MODIS_NRT`: NASA/MODIS (1km, quase real-time)
- `FIRMS_VIIRS`: VIIRS com 1 mês de delay (mas corrigidos)
- `FIRMS_MODIS`: MODIS com 1 mês de delay

**Cobertura Geográfica**: Global

**Resolução Temporal**: Diária (todas as passagens do satélite)

**Formato**: CSV

**Colunas principais**:
```
latitude,longitude,brightness,scan,track,acq_date,acq_time,
satellite,instrument,confidence,version,bright_t31,frp,daynight
```

---

## 9. Próximas Etapas

✅ Depois de validar NASA Earthdata, vamos configurar:

1. **Copernicus CDS** (dados meteorológicos ERA5)
2. **Scripts de ingestão** (baixar dados em massa)
3. **Processamento de dados** (Semana 1)

---

**Última Atualização**: 11 de novembro de 2025
