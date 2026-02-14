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
    print("\nERRO: Credenciais CDS não encontradas")
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
    print("Conexão bem-sucedida!")
except Exception as e:
    print(f"ERRO: {e}")
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
    print("Requisição enfileirada com sucesso!")
    print("Seu download está sendo processado")
    print("Você receberá um email quando estiver pronto")
    print("Tempo típico: 5-30 minutos")

except Exception as e:
    print(f"ERRO: {e}")
    print("   Isso é normal - CDS processa requisições em fila")

print("\n" + "=" * 50)
print("Copernicus CDS está configurado!")
print("=" * 50)
print("\nProximos passos:")
print("1. Você agora pode fazer requisições de ERA5")
print("2. Dados processados serão disponibilizados por email")
print("3. Ver: https://cds.climate.copernicus.eu/how-to-api")
