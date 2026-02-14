"""
Gera mapa da regiao MATOPIBA com fronteiras reais dos estados para a dissertacao.

Usa cartopy + Natural Earth shapefiles (admin_1_states_provinces) para
desenhar os limites reais dos 4 estados MATOPIBA com cores distintas,
contexto do Brasil e informacoes da regiao.

Dependencias:
    pip install cartopy matplotlib geopandas shapely

Uso:
    python src/visualization/generate_matopiba_map.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

# ============================================================================
# CONFIGURACAO
# ============================================================================

# Estados MATOPIBA com cores e siglas
MATOPIBA_STATES = {
    'Maranhão':  {'abbr': 'MA', 'color': '#E53935', 'alpha': 0.45, 'label_lat': -5.5,  'label_lon': -45.3},
    'Tocantins': {'abbr': 'TO', 'color': '#1E88E5', 'alpha': 0.45, 'label_lat': -10.2, 'label_lon': -48.3},
    'Piauí':     {'abbr': 'PI', 'color': '#43A047', 'alpha': 0.45, 'label_lat': -7.0,  'label_lon': -42.8},
    'Bahia':     {'abbr': 'BA', 'color': '#FB8C00', 'alpha': 0.45, 'label_lat': -12.5, 'label_lon': -41.5},
}

# Extent do mapa principal (um pouco mais amplo que MATOPIBA)
MAP_EXTENT = [-52, -38, -16, 1]  # [west, east, south, north]

# Extent do Brasil para inset
BRAZIL_EXTENT = [-75, -34, -34, 6]

# Diretorios de saida
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIGURAS_DIR = PROJECT_ROOT / "Dissertação" / "PPGEE-MODELO-DOUTORADO-MESTRADO-Latex-v4" / "figuras"
OUTPUT_PDF = FIGURAS_DIR / "mapa_matopiba.pdf"
OUTPUT_PNG = FIGURAS_DIR / "mapa_matopiba.png"


def get_brazil_states():
    """
    Carrega geometrias dos estados brasileiros via Natural Earth.
    Retorna dict {nome_estado: geometry}
    """
    # Natural Earth admin_1 (states/provinces) 10m resolution
    shapefile = shpreader.natural_earth(
        resolution='10m',
        category='cultural',
        name='admin_1_states_provinces'
    )
    reader = shpreader.Reader(shapefile)

    states = {}
    for record in reader.records():
        # Filtrar apenas Brasil
        if record.attributes.get('admin', '') == 'Brazil':
            name = record.attributes.get('name', '')
            states[name] = record.geometry
    return states


def add_north_arrow(ax, x=0.95, y=0.95, size=0.06):
    """Adiciona seta norte ao mapa."""
    ax.annotate('N', xy=(x, y), xycoords='axes fraction',
                fontsize=12, fontweight='bold', ha='center', va='center',
                color='#333333')
    ax.annotate('', xy=(x, y - 0.01), xycoords='axes fraction',
                xytext=(x, y - size), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='#333333', lw=1.5))


def add_scale_bar(ax, lon, lat, length_km, transform):
    """Adiciona barra de escala aproximada."""
    # 1 grau de longitude ~ 111 km * cos(lat)
    lat_rad = np.radians(lat)
    km_per_deg = 111.0 * np.cos(lat_rad)
    length_deg = length_km / km_per_deg

    ax.plot([lon, lon + length_deg], [lat, lat], 'k-', linewidth=3,
            transform=transform, zorder=10)
    ax.plot([lon, lon + length_deg], [lat, lat], 'w-', linewidth=1,
            transform=transform, zorder=10)

    # Ticks nas extremidades
    tick_h = 0.15
    for x in [lon, lon + length_deg]:
        ax.plot([x, x], [lat - tick_h, lat + tick_h], 'k-', linewidth=2,
                transform=transform, zorder=10)

    ax.text(lon + length_deg / 2, lat - 0.5, f'{length_km} km',
            ha='center', va='top', fontsize=8, fontweight='bold',
            transform=transform, zorder=10,
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.8, edgecolor='none'))


def generate_map():
    """Gera mapa MATOPIBA com fronteiras reais dos estados."""
    print("[INFO] Gerando mapa MATOPIBA...")
    print("[INFO] Carregando shapefiles Natural Earth (10m)...")

    brazil_states = get_brazil_states()
    print(f"[OK] {len(brazil_states)} estados brasileiros carregados")

    # Verificar quais estados MATOPIBA foram encontrados
    for state_name in MATOPIBA_STATES:
        if state_name in brazil_states:
            print(f"  [OK] {state_name}")
        else:
            print(f"  [WARNING] {state_name} nao encontrado no shapefile")

    # ===== CRIAR FIGURA =====
    fig = plt.figure(figsize=(14, 10), facecolor='white')

    # Painel principal
    ax = fig.add_axes([0.05, 0.05, 0.62, 0.88], projection=ccrs.PlateCarree())
    ax.set_extent(MAP_EXTENT, crs=ccrs.PlateCarree())

    # ===== BASEMAP: features naturais =====
    # Fundo terrestre e maritimo
    ax.add_feature(cfeature.OCEAN, facecolor='#D6EAF8', zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='#F0EDE5', edgecolor='none', zorder=1)

    # Estados vizinhos (todos os brasileiros, cinza claro)
    for name, geom in brazil_states.items():
        if name not in MATOPIBA_STATES:
            ax.add_geometries([geom], ccrs.PlateCarree(),
                              facecolor='#E8E8E8', edgecolor='#AAAAAA',
                              linewidth=0.5, zorder=2)

    # ===== ESTADOS MATOPIBA (coloridos) =====
    for state_name, info in MATOPIBA_STATES.items():
        if state_name in brazil_states:
            geom = brazil_states[state_name]
            ax.add_geometries([geom], ccrs.PlateCarree(),
                              facecolor=info['color'], alpha=info['alpha'],
                              edgecolor=info['color'], linewidth=1.5,
                              zorder=3)

    # Rios principais
    ax.add_feature(cfeature.RIVERS, edgecolor='#5B9BD5', linewidth=0.4, zorder=4)

    # Fronteira do Brasil
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, edgecolor='#555555',
                   linestyle='--', zorder=5)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='#555555', zorder=5)

    # ===== LABELS DOS ESTADOS =====
    text_effects = [pe.withStroke(linewidth=3, foreground='white')]

    for state_name, info in MATOPIBA_STATES.items():
        ax.text(info['label_lon'], info['label_lat'],
                f"{info['abbr']}",
                fontsize=16, fontweight='bold', color=info['color'],
                ha='center', va='center',
                transform=ccrs.PlateCarree(), zorder=8,
                path_effects=text_effects)
        ax.text(info['label_lon'], info['label_lat'] - 0.7,
                f"({state_name})",
                fontsize=8, fontstyle='italic', color='#333333',
                ha='center', va='top',
                transform=ccrs.PlateCarree(), zorder=8,
                path_effects=text_effects)

    # ===== GRIDLINES =====
    gl = ax.gridlines(draw_labels=True, linewidth=0.4, color='gray',
                       alpha=0.4, linestyle='--', zorder=6)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 9, 'color': '#333333'}
    gl.ylabel_style = {'size': 9, 'color': '#333333'}

    # ===== ELEMENTOS CARTOGRAFICOS =====
    add_north_arrow(ax)
    add_scale_bar(ax, -50, -15.2, 200, ccrs.PlateCarree())

    ax.set_title('Regiao MATOPIBA - Area de Estudo',
                  fontsize=15, fontweight='bold', pad=12, color='#222222')

    # ===== INSET: MAPA DO BRASIL =====
    ax_inset = fig.add_axes([0.70, 0.52, 0.28, 0.42], projection=ccrs.PlateCarree())
    ax_inset.set_extent(BRAZIL_EXTENT, crs=ccrs.PlateCarree())

    # Brasil cinza
    ax_inset.add_feature(cfeature.OCEAN, facecolor='#D6EAF8')
    for name, geom in brazil_states.items():
        if name in MATOPIBA_STATES:
            fc = MATOPIBA_STATES[name]['color']
            alpha = 0.5
        else:
            fc = '#E0E0E0'
            alpha = 1.0
        ax_inset.add_geometries([geom], ccrs.PlateCarree(),
                                 facecolor=fc, alpha=alpha,
                                 edgecolor='#999999', linewidth=0.3)

    ax_inset.add_feature(cfeature.COASTLINE, linewidth=0.4, edgecolor='#666666')

    # Retangulo destacando a area do mapa principal
    from matplotlib.patches import Rectangle
    rect = Rectangle((MAP_EXTENT[0], MAP_EXTENT[2]),
                      MAP_EXTENT[1] - MAP_EXTENT[0],
                      MAP_EXTENT[3] - MAP_EXTENT[2],
                      linewidth=2, edgecolor='red', facecolor='none',
                      transform=ccrs.PlateCarree(), zorder=10)
    ax_inset.add_patch(rect)

    ax_inset.set_title('Brasil', fontsize=10, fontweight='bold', color='#333333')

    # ===== PAINEL DE INFORMACOES =====
    ax_info = fig.add_axes([0.70, 0.05, 0.28, 0.42])
    ax_info.axis('off')

    info_text = (
        "MATOPIBA\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Area: ~73 milhoes ha\n"
        "Municipios: 337\n"
        "Bioma: Cerrado (91%)\n\n"
        "Coordenadas:\n"
        "  Lat:  15°S a 0°\n"
        "  Lon: 50°W a 40°W\n\n"
        "Fronteira agricola com\n"
        "alta incidencia de\n"
        "incendios florestais\n"
        "e queimadas agricolas."
    )
    ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes,
                 fontsize=9.5, verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFDE7',
                           alpha=0.95, edgecolor='#CCCCCC'))

    # Legenda dos estados
    legend_handles = [
        mpatches.Patch(facecolor=info['color'], alpha=info['alpha'],
                       edgecolor=info['color'], linewidth=1.5,
                       label=f"{info['abbr']} - {name}")
        for name, info in MATOPIBA_STATES.items()
    ]
    ax_info.legend(handles=legend_handles, loc='lower left', fontsize=9,
                   framealpha=0.95, edgecolor='#CCCCCC', title='Estados',
                   title_fontsize=10)

    # ===== SALVAR =====
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    fig.savefig(str(OUTPUT_PDF), format='pdf', dpi=300,
                bbox_inches='tight', facecolor='white')
    print(f"[OK] PDF salvo: {OUTPUT_PDF}")

    fig.savefig(str(OUTPUT_PNG), format='png', dpi=300,
                bbox_inches='tight', facecolor='white')
    print(f"[OK] PNG salvo: {OUTPUT_PNG}")

    plt.close(fig)
    print("[OK] Mapa gerado com sucesso!")


if __name__ == '__main__':
    generate_map()
