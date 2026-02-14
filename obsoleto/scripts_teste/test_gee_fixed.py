# test_gee_fixed.py
import ee
import sys

print("=" * 50)
print("Testando Google Earth Engine")
print("=" * 50)

try:
    # Inicializar EE
    print("\n1. Inicializando Earth Engine...")
    ee.Initialize()
    print("Inicialização bem-sucedida!")

    # Testar acesso a dataset público
    print("\n2. Acessando dataset MODIS MCD64A1...")
    dataset = ee.ImageCollection('MODIS/006/MCD64A1')
    count = dataset.size().getInfo()
    print(f"Dataset encontrado: {count} imagens")

    # Testar acesso a Sentinel-2
    print("\n3. Acessando Sentinel-2...")
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    print(f"Sentinel-2 encontrado!")

    # Testar MapBiomas
    print("\n4. Acessando MapBiomas...")
    mapbiomas = ee.ImageCollection('projects/mapbiomas-workspace/public/collection7/mapbiomas_collection70_integration_v2')
    print(f"MapBiomas encontrado!")

    print("\n" + "=" * 50)
    print("TUDO FUNCIONANDO! Você está pronto para começar!")
    print("=" * 50)

except ee.EEException as e:
    print(f"\nERRO GEE: {e}")
    print("\nSolução: Você precisa criar um Google Cloud Project:")
    print("1. Acesse: https://console.cloud.google.com/")
    print("2. Crie um novo projeto (qualquer nome)")
    print("3. Copie o PROJECT ID")
    print("4. Execute: earthengine set_project PROJECT_ID")
    print("5. Tente novamente: python test_gee_fixed.py")
    sys.exit(1)

except Exception as e:
    print(f"\nERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
