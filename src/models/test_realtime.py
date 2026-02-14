# test_realtime.py
"""
Script para testar o modelo com dados em tempo real ou historicos.

Dado uma coordenada (lat, lon):
1. Busca hotspots da NASA FIRMS API (tenta multiplas fontes)
2. Busca dados meteorologicos atuais da Open-Meteo API
3. Combina os dados e testa no modelo treinado
4. Gera mapa interativo com os resultados

Modos de operacao:
  - Tempo real: busca dados NRT da FIRMS (ultimos 10 dias)
  - Demo: usa dados historicos do dataset local (sempre funciona)

Uso:
    python src/models/test_realtime.py --lat -10.5 --lon -46.5
    python src/models/test_realtime.py --lat -10.5 --lon -46.5 --radius 100
    python src/models/test_realtime.py --lat -10.5 --lon -46.5 --demo
    python src/models/test_realtime.py --demo
"""

import requests
import pandas as pd
import numpy as np
import pickle
import argparse
import json
from pathlib import Path
from datetime import datetime
from io import StringIO
import os
import webbrowser
import base64
from dotenv import load_dotenv

try:
    import folium
    from folium.plugins import HeatMap
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Aviso: folium não instalado. Mapas não serão gerados.")

# Carregar credenciais
load_dotenv()
FIRMS_MAP_KEY = os.getenv('FIRMS_MAP_KEY')

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
MODEL_PATH = BASE_DIR / 'data/models/module_a/module_a_lightgbm.pkl'
SCALER_PATH = BASE_DIR / 'data/models/module_a/scaler.pkl'
LOGOS_DIR = BASE_DIR / 'logos'
AREAS_ESPURIAS_PATH = BASE_DIR / 'data/areas_espurias.json'
MATOPIBA_GEOJSON_PATH = BASE_DIR / 'data/matopiba_limites.geojson'
DATASET_PATH = BASE_DIR / 'data/processed/training/module_a_balanced.csv'
RAW_FIRMS_PATH = BASE_DIR / 'data/raw/firms_hotspots/firms_viirs_2022-2024.csv'

# Features do modelo (mesma ordem do treinamento)
FEATURE_COLS = [
    'brightness', 'confidence', 'frp', 'hotspot_count',
    'persistence_score', 'temperature', 'dewpoint',
    'wind_speed', 'precipitation', 'rh', 'drying_index'
]

# Fontes FIRMS para busca (tenta em ordem ate encontrar dados)
FIRMS_SOURCES = [
    ('VIIRS_NOAA20_NRT', 'VIIRS NOAA-20 (NRT)'),
    ('VIIRS_SNPP_NRT', 'VIIRS Suomi-NPP (NRT)'),
    ('VIIRS_NOAA21_NRT', 'VIIRS NOAA-21 (NRT)'),
    ('MODIS_NRT', 'MODIS Terra/Aqua (NRT)'),
    ('VIIRS_NOAA20_SP', 'VIIRS NOAA-20 (Standard)'),
    ('VIIRS_SNPP_SP', 'VIIRS Suomi-NPP (Standard)'),
]


def load_model():
    """Carrega modelo e scaler"""
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler


def load_areas_espurias():
    """
    Carrega areas conhecidas por gerar falsos positivos

    Returns:
        dict com categorias e areas, ou None se arquivo nao existir
    """
    if not AREAS_ESPURIAS_PATH.exists():
        return None

    with open(AREAS_ESPURIAS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def load_matopiba_geojson():
    """
    Carrega limites do MATOPIBA do arquivo GeoJSON com fronteiras estaduais

    Returns:
        dict com dados GeoJSON ou None se arquivo nao existir
    """
    if not MATOPIBA_GEOJSON_PATH.exists():
        return None

    with open(MATOPIBA_GEOJSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def get_firms_hotspots(lat, lon, radius_km=25, days=10):
    """
    Busca hotspots recentes da NASA FIRMS API, tentando multiplas fontes.

    Args:
        lat: Latitude central
        lon: Longitude central
        radius_km: Raio de busca em km
        days: Dias para tras (max 10 para NRT)

    Returns:
        DataFrame com hotspots ou None se nao houver
    """
    print(f"\n[1] Buscando hotspots FIRMS...")
    print(f"    Centro: ({lat}, {lon})")
    print(f"    Raio: {radius_km} km")
    print(f"    Periodo: ultimos {days} dias")

    if not FIRMS_MAP_KEY:
        print("    ! FIRMS_MAP_KEY nao configurada no .env")
        return None

    # Converter raio para graus (~111 km por grau)
    delta = radius_km / 111.0

    # Bounding box
    west = lon - delta
    east = lon + delta
    south = lat - delta
    north = lat + delta

    all_hotspots = []

    for source_id, source_name in FIRMS_SOURCES:
        url = (
            f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
            f"{FIRMS_MAP_KEY}/{source_id}/"
            f"{west},{south},{east},{north}/{days}"
        )

        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200 and 'latitude' in response.text:
                df = pd.read_csv(StringIO(response.text))
                print(f"    + {source_name}: {len(df)} hotspots")
                all_hotspots.append(df)
            else:
                print(f"    - {source_name}: sem dados")

        except Exception as e:
            print(f"    - {source_name}: erro ({e})")

    if not all_hotspots:
        print(f"    ! Nenhum hotspot em nenhuma fonte FIRMS")
        return None

    # Combinar todas as fontes e remover duplicatas
    combined = pd.concat(all_hotspots, ignore_index=True)

    # Remover duplicatas por coordenada + data/hora
    if 'acq_date' in combined.columns and 'acq_time' in combined.columns:
        combined = combined.drop_duplicates(
            subset=['latitude', 'longitude', 'acq_date', 'acq_time'],
            keep='first'
        )

    print(f"    Total (sem duplicatas): {len(combined)} hotspots")
    return combined


def get_demo_hotspots(lat, lon, radius_km=50, n_samples=50):
    """
    Carrega hotspots historicos do dataset local para demonstracao.
    Filtra pela regiao de interesse (lat/lon + raio).

    Args:
        lat: Latitude central
        lon: Longitude central
        radius_km: Raio de busca em km
        n_samples: Numero maximo de amostras

    Returns:
        DataFrame com hotspots do dataset ou None
    """
    print(f"\n[1] Carregando hotspots historicos (modo demo)...")

    # Tentar o dataset balanceado primeiro
    data_path = DATASET_PATH if DATASET_PATH.exists() else RAW_FIRMS_PATH

    if not data_path.exists():
        print(f"    ! Dataset nao encontrado: {data_path}")
        return None

    print(f"    Fonte: {data_path.name}")

    df = pd.read_csv(data_path)

    # Filtrar pela regiao se tiver lat/lon
    if 'latitude' in df.columns and 'longitude' in df.columns:
        delta = radius_km / 111.0
        mask = (
            (df['latitude'] >= lat - delta) &
            (df['latitude'] <= lat + delta) &
            (df['longitude'] >= lon - delta) &
            (df['longitude'] <= lon + delta)
        )
        df_region = df[mask]

        if len(df_region) == 0:
            # Se nao tem dados na regiao exata, pegar os mais proximos
            print(f"    ! Sem dados exatos na regiao. Buscando mais proximos...")
            df['_dist'] = np.sqrt(
                (df['latitude'] - lat)**2 + (df['longitude'] - lon)**2
            )
            df_region = df.nsmallest(n_samples, '_dist').drop(columns=['_dist'])

        df = df_region

    # Limitar amostras
    if len(df) > n_samples:
        df = df.sample(n=n_samples, random_state=42)

    # Garantir colunas necessarias para o mapa
    if 'acq_date' not in df.columns and 'acq_datetime' in df.columns:
        df['acq_date'] = pd.to_datetime(df['acq_datetime']).dt.strftime('%Y-%m-%d')
        df['acq_time'] = pd.to_datetime(df['acq_datetime']).dt.strftime('%H%M')

    if 'bright_ti4' not in df.columns and 'brightness' in df.columns:
        df['bright_ti4'] = df['brightness']

    print(f"    Encontrados {len(df)} hotspots historicos na regiao")
    return df


def get_weather_data(lat, lon):
    """
    Busca dados meteorológicos atuais da Open-Meteo API (gratuita, sem API key)

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Dict com dados meteorológicos
    """
    print(f"\n[2] Buscando dados meteorológicos (Open-Meteo)...")

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,dew_point_2m,"
        f"precipitation,wind_speed_10m"
        f"&timezone=America/Sao_Paulo"
    )

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        current = data['current']

        weather = {
            'temperature': current.get('temperature_2m', 25.0),
            'rh': current.get('relative_humidity_2m', 50.0),
            'dewpoint': current.get('dew_point_2m', 15.0),
            'precipitation': current.get('precipitation', 0.0),
            'wind_speed': current.get('wind_speed_10m', 2.0)
        }

        # Calcular drying index (simplificado)
        # Baseado em temperatura alta + umidade baixa + sem chuva
        temp_factor = min(max((weather['temperature'] - 20) / 20, 0), 1)  # 0-1
        rh_factor = 1 - (weather['rh'] / 100)  # 0-1 (maior quando mais seco)
        precip_factor = 1 if weather['precipitation'] == 0 else 0.3
        weather['drying_index'] = (temp_factor * 0.3 + rh_factor * 0.5 + precip_factor * 0.2) * 100

        print(f"    ✓ Dados obtidos:")
        print(f"      Temperatura: {weather['temperature']:.1f}°C")
        print(f"      Umidade: {weather['rh']:.0f}%")
        print(f"      Vento: {weather['wind_speed']:.1f} m/s")
        print(f"      Precipitação: {weather['precipitation']:.1f} mm")
        print(f"      Drying Index: {weather['drying_index']:.1f}")

        return weather

    except Exception as e:
        print(f"    ✗ Erro: {e}")
        # Valores default se falhar
        return {
            'temperature': 28.0,
            'rh': 50.0,
            'dewpoint': 17.0,
            'precipitation': 0.0,
            'wind_speed': 2.5,
            'drying_index': 50.0
        }


def process_hotspot(hotspot_row, weather, count_nearby=1):
    """
    Processa um hotspot do FIRMS e combina com dados meteorológicos

    Args:
        hotspot_row: Linha do DataFrame FIRMS
        weather: Dict com dados meteorológicos
        count_nearby: Número de hotspots próximos

    Returns:
        Dict com features para o modelo
    """
    # Mapear confiança categórica para numérica
    confidence_map = {'l': 30, 'n': 70, 'h': 90}
    conf = hotspot_row.get('confidence', 70)
    if isinstance(conf, str):
        conf = confidence_map.get(conf.lower(), 70)

    # Brightness pode ser 'bright_ti4' no VIIRS
    brightness = hotspot_row.get('bright_ti4', hotspot_row.get('brightness', 330))

    features = {
        'brightness': brightness,
        'confidence': conf,
        'frp': hotspot_row.get('frp', 10.0),
        'hotspot_count': count_nearby,
        'persistence_score': 0.3,  # Assumir médio para dados novos
        'temperature': weather['temperature'],
        'dewpoint': weather['dewpoint'],
        'wind_speed': weather['wind_speed'],
        'precipitation': weather['precipitation'],
        'rh': weather['rh'],
        'drying_index': weather['drying_index']
    }

    return features


def predict_hotspot(model, scaler, features):
    """
    Faz predição para um hotspot

    Returns:
        Dict com resultado da predição
    """
    X = np.array([[features.get(col, 0) for col in FEATURE_COLS]])
    X_scaled = scaler.transform(X)

    prob = model.predict_proba(X_scaled)[0]
    prediction = model.predict(X_scaled)[0]

    return {
        'prediction': int(prediction),
        'label': 'CONFIAVEL' if prediction == 1 else 'SUSPEITO',
        'prob_confiavel': float(prob[1]),
        'prob_suspeito': float(prob[0]),
        'certeza': 'Alta' if max(prob) > 0.9 else 'Media' if max(prob) > 0.7 else 'Baixa'
    }


def create_map(center_lat, center_lon, radius_km, hotspots_df, results, weather):
    """
    Cria mapa interativo com os hotspots classificados

    Args:
        center_lat: Latitude central da busca
        center_lon: Longitude central da busca
        radius_km: Raio da busca em km
        hotspots_df: DataFrame com hotspots do FIRMS
        results: Lista de dicts com resultados das predições
        weather: Dict com dados meteorológicos

    Returns:
        Path do arquivo HTML gerado
    """
    if not FOLIUM_AVAILABLE:
        print("    ✗ Folium não disponível, mapa não gerado")
        return None

    print("\n[4] Gerando mapa interativo...")

    # Contar resultados
    n_confiaveis = sum(1 for r in results if r['prediction'] == 1)
    n_suspeitos = len(results) - n_confiaveis

    # Criar mapa centrado na área de busca
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles='OpenStreetMap'
    )

    # Adicionar camada de satélite como opção
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satelite',
        overlay=False
    ).add_to(m)

    # Adicionar limites do MATOPIBA com fronteiras estaduais
    matopiba_group = folium.FeatureGroup(name='Limites MATOPIBA', show=False)
    matopiba_data = load_matopiba_geojson()

    if matopiba_data:
        # Adicionar cada feature do GeoJSON (estados individuais)
        for feature in matopiba_data.get('features', []):
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})

            # Obter cor do estado ou usar verde padrão
            color = props.get('color', '#4CAF50')
            name = props.get('name', 'MATOPIBA')

            # Converter coordenadas GeoJSON [lon, lat] para Folium [lat, lon]
            if geom.get('type') == 'Polygon':
                coords = geom.get('coordinates', [[]])[0]
                locations = [[coord[1], coord[0]] for coord in coords]

                popup_text = f'''
                    <div style="font-family: Arial; padding: 5px;">
                        <b>{name}</b><br>
                        {props.get("description", "")}
                    </div>
                '''

                folium.Polygon(
                    locations=locations,
                    color=color,
                    weight=3,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.15,
                    popup=folium.Popup(popup_text, max_width=200)
                ).add_to(matopiba_group)
    else:
        # Fallback: polígono simplificado se GeoJSON não existir
        fallback_coords = [
            [-2.5, -46.0], [-2.5, -44.5], [-3.0, -44.0], [-15.5, -46.0],
            [-15.5, -47.0], [-15.0, -48.0], [-2.5, -46.0]
        ]
        folium.Polygon(
            locations=fallback_coords,
            color='green',
            weight=3,
            fill=True,
            fillColor='green',
            fillOpacity=0.1,
            popup='Região MATOPIBA'
        ).add_to(matopiba_group)

    matopiba_group.add_to(m)

    # Adicionar areas espurias conhecidas
    areas_data = load_areas_espurias()
    if areas_data:
        areas_group = folium.FeatureGroup(name='Areas Espurias Conhecidas', show=False)
        categories = areas_data.get('categories', {})

        for area in areas_data.get('areas', []):
            cat = area.get('category', 'unknown')
            cat_info = categories.get(cat, {'color': '#999999', 'description': 'Desconhecido'})
            color = cat_info.get('color', '#999999')

            # Popup com informacoes da area
            area_popup = f'''
                <div style="width: 200px; font-family: Arial, sans-serif;">
                    <h4 style="margin: 0; padding: 5px; background: {color}; color: white; border-radius: 3px;">
                        {area.get("name", "Area Espuria")}
                    </h4>
                    <div style="padding: 8px;">
                        <b>Categoria:</b> {cat_info.get("description", cat)}<br>
                        <b>Descricao:</b> {area.get("description", "N/A")}<br>
                        <b>Fonte:</b> {area.get("source", "N/A")}
                    </div>
                </div>
            '''

            if area.get('type') == 'circle':
                coords = area.get('coordinates', [0, 0])
                radius = area.get('radius_km', 1) * 1000  # km para metros
                folium.Circle(
                    location=coords,
                    radius=radius,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.3,
                    weight=2,
                    popup=folium.Popup(area_popup, max_width=250)
                ).add_to(areas_group)

            elif area.get('type') == 'polygon':
                coords = area.get('coordinates', [])
                if coords:
                    folium.Polygon(
                        locations=coords,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.3,
                        weight=2,
                        popup=folium.Popup(area_popup, max_width=250)
                    ).add_to(areas_group)

        areas_group.add_to(m)

    # Adicionar círculo mostrando área de busca
    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius_km * 1000,  # metros
        color='blue',
        fill=False,
        weight=2,
        dash_array='5',
        popup=f'Area de busca: {radius_km} km'
    ).add_to(m)

    # Marcador do centro
    folium.Marker(
        location=[center_lat, center_lon],
        popup=f'''
            <b>Centro da Busca</b><br>
            Lat: {center_lat:.4f}<br>
            Lon: {center_lon:.4f}<br>
            <hr>
            <b>Condicoes Atuais:</b><br>
            Temp: {weather["temperature"]:.1f} C<br>
            Umidade: {weather["rh"]:.0f}%<br>
            Vento: {weather["wind_speed"]:.1f} m/s<br>
            Drying Index: {weather["drying_index"]:.0f}
        ''',
        icon=folium.Icon(color='blue', icon='crosshairs', prefix='fa')
    ).add_to(m)

    # Criar grupos para cada tipo
    confiaveis_group = folium.FeatureGroup(name=f'Confiaveis ({n_confiaveis})')
    suspeitos_group = folium.FeatureGroup(name=f'Suspeitos ({n_suspeitos})')

    # Preparar dados para heatmap
    heat_data_confiaveis = []

    # Agrupar hotspots por data
    dates_found = set()

    # Adicionar cada hotspot
    for idx, (_, row) in enumerate(hotspots_df.iterrows()):
        result = results[idx]
        lat = row['latitude']
        lon = row['longitude']
        frp = row.get('frp', 0)
        date = row.get('acq_date', 'N/A')
        time = row.get('acq_time', '')
        dates_found.add(date)

        # Cor baseada na classificação
        if result['prediction'] == 1:
            color = 'red'
            group = confiaveis_group
            heat_data_confiaveis.append([lat, lon, min(frp, 100)])
        else:
            color = 'orange'
            group = suspeitos_group

        # Tamanho do marcador baseado no FRP
        radius = max(5, min(20, frp / 5))

        # Popup com informações
        popup_html = f'''
            <div style="width: 220px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0; padding: 5px; background: {"#dc3545" if result["prediction"]==1 else "#fd7e14"}; color: white; border-radius: 3px;">
                    {"CONFIAVEL" if result["prediction"]==1 else "SUSPEITO"}
                </h4>
                <div style="padding: 8px;">
                    <b>Localizacao:</b> {lat:.4f}, {lon:.4f}<br>
                    <b>Data:</b> {date} {time}<br>
                    <b>FRP:</b> {frp:.2f} MW<br>
                    <hr style="margin: 8px 0;">
                    <b>Probabilidades:</b><br>
                    <div style="background: #f0f0f0; border-radius: 3px; padding: 5px; margin-top: 5px;">
                        Confiavel: <b>{result["prob_confiavel"]*100:.1f}%</b><br>
                        Suspeito: <b>{result["prob_suspeito"]*100:.1f}%</b>
                    </div>
                    <div style="margin-top: 5px;">
                        Certeza: <span style="color: {"green" if result["certeza"]=="Alta" else "orange"};">
                            <b>{result["certeza"]}</b>
                        </span>
                    </div>
                </div>
            </div>
        '''

        # Usar CircleMarker para visualização proporcional ao FRP
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(group)

    # Adicionar grupos de pontos ao mapa
    confiaveis_group.add_to(m)
    suspeitos_group.add_to(m)

    # Adicionar Heatmap dos confiáveis (fogos reais)
    if heat_data_confiaveis:
        heatmap_confiaveis = folium.FeatureGroup(name='Mapa de Calor - Confiaveis', show=False)
        HeatMap(
            heat_data_confiaveis,
            radius=25,
            blur=15,
            gradient={'0.4': 'yellow', '0.65': 'orange', '1': 'red'}
        ).add_to(heatmap_confiaveis)
        heatmap_confiaveis.add_to(m)

    # Adicionar Heatmap de todos os hotspots
    all_heat_data = [[row['latitude'], row['longitude'], row.get('frp', 10)]
                     for _, row in hotspots_df.iterrows()]
    if all_heat_data:
        heatmap_all = folium.FeatureGroup(name='Mapa de Calor - Todos', show=False)
        HeatMap(
            all_heat_data,
            radius=20,
            blur=15,
            gradient={'0.2': 'blue', '0.4': 'lime', '0.6': 'yellow', '0.8': 'orange', '1': 'red'}
        ).add_to(heatmap_all)
        heatmap_all.add_to(m)

    # Adicionar controle de camadas
    folium.LayerControl(collapsed=False).add_to(m)

    # Adicionar legenda melhorada
    legend_html = '''
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background-color: white; padding: 15px; border-radius: 8px;
                border: 2px solid #333; font-size: 12px; font-family: Arial, sans-serif;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3); max-height: 400px; overflow-y: auto;">
        <h4 style="margin: 0 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Legenda - Hotspots</h4>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: red; border-radius: 50%; margin-right: 8px;"></span>
            Confiavel (Fogo Real)
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: orange; border-radius: 50%; margin-right: 8px;"></span>
            Suspeito (Falso Positivo)
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: blue; border-radius: 50%; margin-right: 8px;"></span>
            Centro da Busca
        </div>
        <h4 style="margin: 10px 0 8px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Estados MATOPIBA</h4>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #E91E63; margin-right: 6px;"></span>
            Maranhao (MA)
        </div>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #4CAF50; margin-right: 6px;"></span>
            Tocantins (TO)
        </div>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #2196F3; margin-right: 6px;"></span>
            Piaui (PI)
        </div>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #FF9800; margin-right: 6px;"></span>
            Bahia (BA)
        </div>
        <h4 style="margin: 10px 0 8px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Areas Espurias</h4>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #9C27B0; margin-right: 6px;"></span>
            Industrial
        </div>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #FFC107; margin-right: 6px;"></span>
            Usina Solar
        </div>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #607D8B; margin-right: 6px;"></span>
            Area Urbana
        </div>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #00BCD4; margin-right: 6px;"></span>
            Aeroporto
        </div>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #795548; margin-right: 6px;"></span>
            Mineracao
        </div>
        <div style="margin: 4px 0; font-size: 11px;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #2196F3; margin-right: 6px;"></span>
            Reservatorio (reflexo)
        </div>
        <hr style="margin: 8px 0;">
        <small>Tamanho do circulo = FRP</small>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Adicionar painel de resumo
    dates_str = ', '.join(sorted(dates_found)[-3:]) if dates_found else 'N/A'
    summary_html = f'''
    <div style="position: fixed; top: 10px; left: 50px; z-index: 1000;
                background-color: white; padding: 15px; border-radius: 8px;
                border: 2px solid #333; font-size: 13px; max-width: 350px;
                font-family: Arial, sans-serif; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
        <h3 style="margin: 0 0 10px 0; color: #333;">Modulo A - Classificacao de Hotspots</h3>
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between;">
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 24px; font-weight: bold; color: red;">{n_confiaveis}</div>
                    <div style="font-size: 11px;">Confiaveis</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 24px; font-weight: bold; color: orange;">{n_suspeitos}</div>
                    <div style="font-size: 11px;">Suspeitos</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 24px; font-weight: bold; color: #333;">{len(results)}</div>
                    <div style="font-size: 11px;">Total</div>
                </div>
            </div>
        </div>
        <div style="font-size: 12px; color: #666;">
            <b>Data analise:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}<br>
            <b>Centro:</b> ({center_lat:.4f}, {center_lon:.4f})<br>
            <b>Raio:</b> {radius_km} km<br>
            <b>Datas dos hotspots:</b> {dates_str}
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(summary_html))

    # Adicionar mini painel de condições meteorológicas (posicionado abaixo do controle de camadas)
    weather_html = f'''
    <div style="position: fixed; top: 220px; right: 10px; z-index: 999;
                background-color: white; padding: 12px; border-radius: 8px;
                border: 2px solid #333; font-size: 12px;
                font-family: Arial, sans-serif; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
        <h4 style="margin: 0 0 8px 0;">Condicoes Meteorologicas</h4>
        <div>Temp: <b>{weather["temperature"]:.1f} C</b></div>
        <div>Umidade: <b>{weather["rh"]:.0f}%</b></div>
        <div>Vento: <b>{weather["wind_speed"]:.1f} m/s</b></div>
        <div>Precipitacao: <b>{weather["precipitation"]:.1f} mm</b></div>
        <hr style="margin: 5px 0;">
        <div>Drying Index: <b style="color: {"red" if weather["drying_index"] > 60 else "orange" if weather["drying_index"] > 30 else "green"};">{weather["drying_index"]:.0f}</b></div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(weather_html))

    # Adicionar logos das instituições no canto inferior direito
    logos_html = '''
    <div style="position: fixed; bottom: 30px; right: 10px; z-index: 1000;
                background-color: white; padding: 10px; border-radius: 8px;
                border: 2px solid #333; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                display: flex; align-items: center; gap: 10px;">
    '''

    # Carregar logos como base64
    logo_files = [
        ('logo_ufam.png', 'UFAM'),
        ('ppge.png', 'PPGE'),
        ('politecnico de portalegre.png', 'IPPortalegre')
    ]

    for logo_file, alt_text in logo_files:
        logo_path = LOGOS_DIR / logo_file
        if logo_path.exists():
            with open(logo_path, 'rb') as f:
                logo_b64 = base64.b64encode(f.read()).decode('utf-8')
            logos_html += f'''
                <img src="data:image/png;base64,{logo_b64}"
                     alt="{alt_text}"
                     style="height: 45px; width: auto;"
                     title="{alt_text}">
            '''

    logos_html += '</div>'
    m.get_root().html.add_child(folium.Element(logos_html))

    # Salvar mapa
    output_dir = BASE_DIR / 'outputs' / 'maps'
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f'hotspots_map_{timestamp}.html'

    m.save(str(output_file))
    print(f"    Mapa salvo em: {output_file}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Testar modelo de classificacao de hotspots',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Tempo real (busca FIRMS API)
  python src/models/test_realtime.py --lat -10.5 --lon -46.5
  python src/models/test_realtime.py --lat -12.0 --lon -43.5 --radius 100

  # Demo (dados historicos do dataset local - sempre funciona)
  python src/models/test_realtime.py --demo
  python src/models/test_realtime.py --lat -10.5 --lon -46.5 --demo

  # Coordenadas uteis na MATOPIBA:
  #   Tocantins (TO): --lat -10.5 --lon -48.3
  #   Bahia (BA):     --lat -12.0 --lon -43.5
  #   Maranhao (MA):  --lat -5.0  --lon -44.0
  #   Piaui (PI):     --lat -8.0  --lon -43.0
        """
    )
    parser.add_argument('--lat', type=float, default=-10.5,
                        help='Latitude (default: -10.5 Tocantins)')
    parser.add_argument('--lon', type=float, default=-46.5,
                        help='Longitude (default: -46.5 Tocantins)')
    parser.add_argument('--radius', type=float, default=50,
                        help='Raio de busca em km (default: 50)')
    parser.add_argument('--days', type=int, default=10,
                        help='Dias para buscar NRT (max: 10)')
    parser.add_argument('--demo', action='store_true',
                        help='Usar dados historicos do dataset local')
    parser.add_argument('--samples', type=int, default=50,
                        help='Numero de amostras no modo demo (default: 50)')
    parser.add_argument('--no-browser', action='store_true',
                        help='Nao abrir mapa no navegador')

    args = parser.parse_args()

    mode = "DEMO (dados historicos)" if args.demo else "TEMPO REAL (FIRMS API)"

    print("\n" + "="*70)
    print(f"MODULO A - CLASSIFICACAO DE HOTSPOTS")
    print(f"Modo: {mode}")
    print("="*70)
    print(f"Coordenadas: ({args.lat}, {args.lon})")
    print(f"Raio: {args.radius} km")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Carregar modelo
    print("\n[0] Carregando modelo...")
    try:
        model, scaler = load_model()
        print("    Modelo carregado!")
    except Exception as e:
        print(f"    Erro ao carregar modelo: {e}")
        return

    # Buscar hotspots
    if args.demo:
        hotspots = get_demo_hotspots(args.lat, args.lon, args.radius, args.samples)
    else:
        hotspots = get_firms_hotspots(args.lat, args.lon, args.radius, args.days)

        # Fallback automatico para demo se NRT nao retornar dados
        if hotspots is None or len(hotspots) == 0:
            print("\n    Sem dados NRT. Ativando fallback para dados historicos...")
            print("    (use --demo para ir direto ao modo demo)")
            hotspots = get_demo_hotspots(args.lat, args.lon, args.radius, args.samples)

    # Buscar meteorologia
    weather = get_weather_data(args.lat, args.lon)

    # Processar resultados
    print("\n" + "="*70)
    print("RESULTADOS")
    print("="*70)

    if hotspots is None or len(hotspots) == 0:
        print("\n! Nenhum hotspot disponivel (nem NRT nem historico).")
        print("  Verifique as coordenadas ou tente um raio maior.")
        return

    # Processar cada hotspot
    count_total = len(hotspots)
    confiaveis = 0
    suspeitos = 0
    all_results = []

    print(f"\n[3] Classificando {count_total} hotspots...\n")

    for idx, (_, row) in enumerate(hotspots.iterrows(), 1):
        features = process_hotspot(row, weather, count_total)
        result = predict_hotspot(model, scaler, features)
        all_results.append(result)

        if result['prediction'] == 1:
            confiaveis += 1
        else:
            suspeitos += 1

        # Imprimir detalhes apenas para os primeiros 10
        if idx <= 10:
            status_ = "REAL" if result['prediction'] == 1 else "SUSP"
            print(f"  [{status_}] #{idx:3d}  "
                  f"({row['latitude']:.4f}, {row['longitude']:.4f})  "
                  f"FRP={row.get('frp', row.get('bright_ti4', 'N/A'))}  "
                  f"-> {result['label']} ({result['prob_confiavel']*100:.0f}%)")

    if count_total > 10:
        print(f"  ... e mais {count_total - 10} hotspots")

    # Resumo
    print(f"\n" + "-"*70)
    print(f"RESUMO:")
    print(f"  Confiaveis (fogo real):       {confiaveis:4d} ({confiaveis/count_total*100:.0f}%)")
    print(f"  Suspeitos (falso positivo):   {suspeitos:4d} ({suspeitos/count_total*100:.0f}%)")
    print(f"  Total:                        {count_total:4d}")
    print("-"*70)

    # Gerar mapa
    map_file = create_map(
        args.lat, args.lon, args.radius,
        hotspots, all_results, weather
    )

    if map_file and not args.no_browser:
        print(f"\n Abrindo mapa no navegador...")
        webbrowser.open(f'file://{map_file.absolute()}')

    print("\n Concluido!")
    print("="*70)


if __name__ == '__main__':
    main()
