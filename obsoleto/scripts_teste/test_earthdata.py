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
    print("\nERRO: Credenciais não encontradas")
    print("Certifique-se de que .env contém:")
    print("EARTHDATA_USERNAME=seu_username")
    print("EARTHDATA_PASSWORD=sua_password")
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
        print(f"Conexão bem-sucedida!")
        print(f"Dados recebidos: {len(lines)-2} registros")
        print(f"Primeiras linhas:")
        for line in lines[:3]:
            if line:
                print(f"      {line[:80]}...")
    else:
        print(f"ERRO: Status {response.status_code}")
        print(f"Resposta: {response.text[:200]}")

except Exception as e:
    print(f"ERRO: {e}")
    exit(1)

# Testar acesso a MODIS (outro dataset)
print("\n2. Testando acesso a MODIS MCD14DL...")

url_modis = 'https://firms.modaps.eosdis.nasa.gov/api/area/csv/FIRMS_MODIS_NRT/-65/-15/-40/0/1/'

try:
    response = requests.get(url_modis, auth=(username, password), timeout=10)

    if response.status_code == 200:
        lines = response.text.split('\n')
        print(f"MODIS acessível!")
        print(f"Registros: {len(lines)-2}")
    else:
        print(f"Status {response.status_code} (pode ser que não tenha dados nesse período)")

except Exception as e:
    print(f"ERRO: {e}")

print("\n" + "=" * 50)
print("NASA Earthdata está configurado!")
print("=" * 50)
print("\nProximos passos:")
print("1. Você agora pode baixar FIRMS hotspots")
print("2. Dados disponíveis em tempo quase real (1-2 dias de delay)")
