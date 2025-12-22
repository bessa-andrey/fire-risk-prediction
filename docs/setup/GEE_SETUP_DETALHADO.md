# Google Earth Engine - Guia Passo a Passo Detalhado

## 1. Acessar Google Earth Engine

### Passo 1.1: Acesse o site
- URL: https://earthengine.google.com/
- Você verá a página inicial (como a imagem que você capturou)

### Passo 1.2: Procure pelo botão "Sign Up"
- **Localização**: Canto superior direito da página
- **Opção 1**: Se você JÁ está logado em uma conta Google
  - Clique diretamente em **"Get Started"** ou **"Sign Up"**
  - Você será direcionado para aceitar os Termos de Serviço
- **Opção 2**: Se você NÃO está logado
  - Clique em **"Sign Up"** → Escolha sua conta Google → Faça login

---

## 2. Solicitar Acesso ao Google Earth Engine

### Passo 2.1: Formulário de Registro
Após clicar em Sign Up, você verá um formulário com:
- **Primeiro Nome**
- **Último Nome**
- **Email** (será o email associado)
- **Afiliação** (ex: "Universidade/Mestrado")
- **País** (Brasil)
- **Descrição do uso** (ex: "Fire detection and propagation ML models for Amazon region")

### Passo 2.2: Aceitar Termos
- [ ] Marque "Concordo com os Termos de Serviço"
- [ ] Clique em **"Sign Up"**

### Passo 2.3: Aguardar Aprovação
- **Tempo típico**: 24-48 horas
- Você receberá **email de confirmação**
- Verifique SPAM se não receber em 2 dias
- **Email esperado**: "Welcome to Google Earth Engine!"

---

## 3. Primeira vez acessando GEE após aprovação

### Passo 3.1: Fazer Login
- Acesse: https://earthengine.google.com/
- Faça login com sua conta Google
- Clique em **"Code Editor"** (canto superior direito)

### Passo 3.2: Interface Code Editor
Você verá:
```
┌─────────────────────────────────────────┐
│  Scripts  │  Docs  │  Asset Manager     │
├─────────────────────────────────────────┤
│                                          │
│  (painel esquerdo)    (editor centro)  │
│                                          │
│  Projects             var image = ...   │
│  ├── default                            │
│  ├── Examples                           │
│                                          │
└─────────────────────────────────────────┘
```

---

## 4. Instalar a Python API do GEE

### Passo 4.1: Abrir Terminal/PowerShell

**No Windows** (recomendado):
```
1. Pressione: Win + X
2. Selecione: Windows PowerShell (Admin) OU
3. Clique em: Terminal
```

**No Linux/Mac**:
```
Abra o Terminal normalmente
```

### Passo 4.2: Ativar seu ambiente Conda
```powershell
# Se você ainda não criou o ambiente, faça agora:
conda create -n fireml python=3.10 -y
conda activate fireml

# Ou se já existe:
conda activate fireml
```

### Passo 4.3: Instalar earthengine-api
```powershell
pip install earthengine-api
```

**Saída esperada**:
```
Successfully installed earthengine-api-0.1.x
```

---

## 5. Autenticar no Python

### Passo 5.1: Executar comando de autenticação
```powershell
# PowerShell/Terminal
earthengine authenticate
```

### Passo 5.2: Seguir o fluxo de autenticação
Você verá:
```
Go to the following URL to authorize this request:
https://accounts.google.com/o/oauth2/auth?...
```

**O QUE FAZER**:
1. Um navegador vai abrir automaticamente
2. **Autorizar** o acesso clicando em "Allow"
3. Você verá uma página com um **código de autorização**
4. **Copie o código COMPLETO** (pode ter caracteres especiais)
5. **Cole no PowerShell/Terminal** e pressione ENTER

### Passo 5.3: Confirmação
Se tudo deu certo, você verá:
```
Successfully saved authorization code to your credentials.
```

---

## 6. Criar Primeiro Script de Teste

### Passo 6.1: Criar arquivo Python
Na pasta do seu projeto, crie um arquivo chamado `test_gee.py`:

```python
# test_gee.py
import ee
import sys

print("=" * 50)
print("Testando Google Earth Engine")
print("=" * 50)

try:
    # Inicializar EE
    print("\n1. Inicializando Earth Engine...")
    ee.Initialize()
    print("   ✅ Inicialização bem-sucedida!")

    # Testar acesso a dataset público
    print("\n2. Acessando dataset MODIS MCD64A1...")
    dataset = ee.ImageCollection('MODIS/006/MCD64A1')
    print(f"   ✅ Dataset encontrado: {dataset.size().getInfo()} imagens")

    # Testar acesso a Sentinel-2
    print("\n3. Acessando Sentinel-2...")
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    print(f"   ✅ Sentinel-2 encontrado: {s2.size().getInfo()} imagens")

    # Testar MapBiomas
    print("\n4. Acessando MapBiomas...")
    mapbiomas = ee.ImageCollection('projects/mapbiomas-workspace/public/collection7/mapbiomas_collection70_integration_v2')
    print(f"   ✅ MapBiomas encontrado!")

    print("\n" + "=" * 50)
    print("🎉 TUDO FUNCIONANDO! Você está pronto para começar!")
    print("=" * 50)

except ee.EEException as e:
    print(f"\n❌ ERRO: {e}")
    print("Possíveis soluções:")
    print("1. Execute novamente: earthengine authenticate")
    print("2. Verifique sua conexão com a internet")
    print("3. Aguarde a aprovação de 24-48h se sua conta for nova")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ ERRO NÃO IDENTIFICADO: {e}")
    sys.exit(1)
```

### Passo 6.2: Executar o script
```powershell
# Certifique-se que o ambiente está ativo
conda activate fireml

# Execute o script
python test_gee.py
```

### Passo 6.3: Resultado esperado
```
==================================================
Testando Google Earth Engine
==================================================

1. Inicializando Earth Engine...
   ✅ Inicialização bem-sucedida!

2. Acessando dataset MODIS MCD64A1...
   ✅ Dataset encontrado: 687 imagens

3. Acessando Sentinel-2...
   ✅ Sentinel-2 encontrado: 15000000 imagens

4. Acessando MapBiomas...
   ✅ MapBiomas encontrado!

==================================================
🎉 TUDO FUNCIONANDO! Você está pronto para começar!
==================================================
```

---

## 7. Script para Baixar Dados Sentinel-2 (Teste)

Uma vez que o GEE está funcionando, você pode criar este script para baixar um composite Sentinel-2 da região MATOPIBA:

```python
# download_sentinel2_test.py
import ee
import numpy as np
from PIL import Image
import io

ee.Initialize()

# Definir bounding box MATOPIBA (simplificado)
# S, W, N, E
aoi = ee.Geometry.Rectangle([-65, -15, -40, 0])

# Filtrar Sentinel-2 para período seco (agosto 2023)
s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
      .filterBounds(aoi)
      .filterDate('2023-08-01', '2023-08-31')
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))  # Menos de 20% nuvem
      .median())

# Selecionar bandas RGB
rgb = s2.select(['B4', 'B3', 'B2'])

# Normalizar para 8-bit (para visualização)
rgb_norm = rgb.unitScale(0, 3000).uint8()

# Gerar URL para download
url = rgb_norm.getThumbURL({'dimensions': 512, 'format': 'png'})
print(f"Imagem gerada! Acesse: {url}")

# Você pode fazer download também:
import requests
response = requests.get(url)
with open('sentinel2_matopiba.png', 'wb') as f:
    f.write(response.content)
print("✅ Imagem salva como 'sentinel2_matopiba.png'")
```

---

## 8. Troubleshooting - Problemas Comuns

### ❌ Erro: "Not Authenticated"
```
Mensagem: ee.EEException: User not authenticated
Solução:
1. Execute: earthengine authenticate
2. Abra o link no navegador
3. Autorize o acesso
4. Copie o CÓDIGO COMPLETO
5. Cole no terminal
6. Reinicie Python
```

### ❌ Erro: "Access denied"
```
Possível causa: Conta ainda não foi aprovada (< 24h)
Solução: Aguarde 24-48h e tente novamente
Verifique seu email (incluindo SPAM)
```

### ❌ Erro: "Command 'earthengine' not found"
```
Possível causa: earthengine-api não instalada ou ambiente incorreto
Solução:
1. Ative o ambiente: conda activate fireml
2. Instale novamente: pip install earthengine-api
3. Reinicie o terminal
```

### ❌ Erro: "Connection timeout"
```
Possível causa: Problema de internet ou servidor do GEE temporariamente indisponível
Solução:
1. Verifique sua conexão internet
2. Aguarde alguns minutos
3. Tente novamente
```

---

## 9. Próximas Etapas

✅ **GEE está configurado!**

Próximo: **Configurar NASA Earthdata** (para FIRMS hotspots)

Veja o arquivo: `CREDENCIAIS_SETUP.md` - Seção 2

---

**Última Atualização**: 11 de novembro de 2025
**Status**: Pronto para uso
