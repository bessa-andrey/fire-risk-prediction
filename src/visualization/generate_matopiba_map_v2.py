"""
Gera mapa da regiao MATOPIBA (v2) - estados recortados pelo limite MATOPIBA.

Diferente da v1 (estados completos), esta versao recorta (clip) as geometrias
dos estados usando o poligono da regiao MATOPIBA, mostrando apenas a porcao
que faz parte da fronteira agricola.

Dependencias:
    pip install cartopy matplotlib shapely

Uso:
    python src/visualization/generate_matopiba_map_v2.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from pathlib import Path
from shapely.geometry import box as shapely_box

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

# ============================================================================
# CONFIGURACAO
# ============================================================================

# Limite da regiao MATOPIBA (bounding box expandido +20% em todos os lados)
# Base: west=-50, east=-41, south=-15, north=-2 (H=9°, V=13°)
# +20%: H*0.20=1.8°, V*0.20=2.6°
MATOPIBA_BOUNDS = {
    'west': -52.5,
    'east': -35,
    'south': -19,
    'north':   1,
}

# Poligono de recorte MATOPIBA (shapely box)
MATOPIBA_CLIP = shapely_box(
    MATOPIBA_BOUNDS['west'],
    MATOPIBA_BOUNDS['south'],
    MATOPIBA_BOUNDS['east'],
    MATOPIBA_BOUNDS['north']
)

# Estados MATOPIBA com cores e posicoes de label ajustadas para a versao recortada
MATOPIBA_STATES = {
    'Maranhão':  {'abbr': 'MA', 'color': '#D32F2F', 'alpha': 0.40,
                  'label_lat': -5.5,  'label_lon': -45.0},
    'Tocantins': {'abbr': 'TO', 'color': '#1565C0', 'alpha': 0.40,
                  'label_lat': -10.5, 'label_lon': -48.0},
    'Piauí':     {'abbr': 'PI', 'color': '#2E7D32', 'alpha': 0.40,
                  'label_lat': -7.5,  'label_lon': -42.5},
    'Bahia':     {'abbr': 'BA', 'color': '#EF6C00', 'alpha': 0.40,
                  'label_lat': -13.0, 'label_lon': -43.5},
}

# Extent do mapa - ajustado ao recorte MATOPIBA com margem
MAP_EXTENT = [
    MATOPIBA_BOUNDS['west'] - 1.5,
    MATOPIBA_BOUNDS['east'] + 0.6,
    MATOPIBA_BOUNDS['south'] - 1.5,
    MATOPIBA_BOUNDS['north'] + 1.5,
]

BRAZIL_EXTENT = [-75, -34, -34, 6]

# Saida
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIGURAS_DIR = PROJECT_ROOT / "Dissertação" / "PPGEE-MODELO-DOUTORADO-MESTRADO-Latex-v4" / "figuras"
OUTPUT_PDF = FIGURAS_DIR / "mapa_matopiba_v2.pdf"
OUTPUT_PNG = FIGURAS_DIR / "mapa_matopiba_v2.png"


def get_brazil_states():
    """Carrega geometrias dos estados brasileiros via Natural Earth."""
    shapefile = shpreader.natural_earth(
        resolution='10m', category='cultural', name='admin_1_states_provinces'
    )
    reader = shpreader.Reader(shapefile)
    states = {}
    for record in reader.records():
        if record.attributes.get('admin', '') == 'Brazil':
            name = record.attributes.get('name', '')
            states[name] = record.geometry
    return states


def clip_geometry(geometry, clip_polygon):
    """Recorta uma geometria pelo poligono de clip."""
    try:
        clipped = geometry.intersection(clip_polygon)
        if clipped.is_empty:
            return None
        return clipped
    except Exception:
        return None


def add_north_arrow(ax, x=0.90, y=0.90, size=0.06):
    """Adiciona seta norte."""
    ax.annotate('N', xy=(x, y), xycoords='axes fraction',
                fontsize=13, fontweight='bold', ha='center', va='center',
                color='#333333')
    ax.annotate('', xy=(x, y - 0.01), xycoords='axes fraction',
                xytext=(x, y - size), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='#333333', lw=1.5))


def add_scale_bar(ax, lon, lat, length_km, transform):
    """Barra de escala aproximada."""
    lat_rad = np.radians(lat)
    km_per_deg = 111.0 * np.cos(lat_rad)
    length_deg = length_km / km_per_deg

    # Barra principal
    ax.plot([lon, lon + length_deg], [lat, lat], 'k-', linewidth=4,
            transform=transform, zorder=10)
    # Barra interna branca
    ax.plot([lon, lon + length_deg / 2], [lat, lat], 'w-', linewidth=2,
            transform=transform, zorder=10)

    # Ticks
    for x in [lon, lon + length_deg / 2, lon + length_deg]:
        ax.plot([x, x], [lat - 0.15, lat + 0.15], 'k-', linewidth=2,
                transform=transform, zorder=10)

    # Labels
    ax.text(lon, lat - 0.5, '0', ha='center', va='top', fontsize=7,
            fontweight='bold', transform=transform, zorder=10)
    ax.text(lon + length_deg, lat - 0.5, f'{length_km}', ha='center', va='top',
            fontsize=7, fontweight='bold', transform=transform, zorder=10)
    ax.text(lon + length_deg / 2, lat - 0.9, 'km', ha='center', va='top',
            fontsize=7, transform=transform, zorder=10)


def generate_map_v2():
    """Gera mapa MATOPIBA v2 com estados recortados pelo limite da regiao."""
    print("[INFO] Gerando mapa MATOPIBA v2 (recorte por regiao)...")
    print("[INFO] Carregando shapefiles Natural Earth (10m)...")

    brazil_states = get_brazil_states()
    print(f"[OK] {len(brazil_states)} estados brasileiros carregados")

    # Recortar estados MATOPIBA pelo poligono
    clipped_states = {}
    for state_name in MATOPIBA_STATES:
        if state_name in brazil_states:
            clipped = clip_geometry(brazil_states[state_name], MATOPIBA_CLIP)
            if clipped:
                clipped_states[state_name] = clipped
                print(f"  [OK] {state_name} recortado")
            else:
                print(f"  [WARNING] {state_name} nao intersecta o limite MATOPIBA")

    # ===== FIGURA =====
    fig = plt.figure(figsize=(12, 10), facecolor='white')

    # Painel principal
    ax = fig.add_axes([0.05, 0.05, 0.62, 0.88], projection=ccrs.PlateCarree())
    ax.set_extent(MAP_EXTENT, crs=ccrs.PlateCarree())

    # ===== BASEMAP =====
    ax.add_feature(cfeature.OCEAN, facecolor='#D6EAF8', zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='#F5F2EB', edgecolor='none', zorder=1)

    # Estados vizinhos (cinza claro, como contexto)
    for name, geom in brazil_states.items():
        if name not in MATOPIBA_STATES:
            ax.add_geometries([geom], ccrs.PlateCarree(),
                              facecolor='#ECECEC', edgecolor='#BBBBBB',
                              linewidth=0.4, zorder=2)

    # Partes dos estados MATOPIBA FORA do recorte (cinza mais claro)
    for state_name in MATOPIBA_STATES:
        if state_name in brazil_states:
            full_geom = brazil_states[state_name]
            try:
                outside = full_geom.difference(MATOPIBA_CLIP)
                if not outside.is_empty:
                    ax.add_geometries([outside], ccrs.PlateCarree(),
                                      facecolor='#E0E0E0', edgecolor='#BBBBBB',
                                      linewidth=0.4, zorder=2)
            except Exception:
                pass

    # ===== ESTADOS MATOPIBA RECORTADOS (coloridos) =====
    for state_name, info in MATOPIBA_STATES.items():
        if state_name in clipped_states:
            ax.add_geometries([clipped_states[state_name]], ccrs.PlateCarree(),
                              facecolor=info['color'], alpha=info['alpha'],
                              edgecolor=info['color'], linewidth=1.8,
                              zorder=3)

    # ===== CONTORNO DO RECORTE MATOPIBA =====
    rect_lons = [MATOPIBA_BOUNDS['west'], MATOPIBA_BOUNDS['east'],
                 MATOPIBA_BOUNDS['east'], MATOPIBA_BOUNDS['west'],
                 MATOPIBA_BOUNDS['west']]
    rect_lats = [MATOPIBA_BOUNDS['south'], MATOPIBA_BOUNDS['south'],
                 MATOPIBA_BOUNDS['north'], MATOPIBA_BOUNDS['north'],
                 MATOPIBA_BOUNDS['south']]
    ax.plot(rect_lons, rect_lats, color='#333333', linewidth=2.5,
            linestyle='-', transform=ccrs.PlateCarree(), zorder=5,
            label='Limite MATOPIBA')

    # Rios
    ax.add_feature(cfeature.RIVERS, edgecolor='#5B9BD5', linewidth=0.3, zorder=4)

    # Costa e fronteiras
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor='#666666', zorder=5)

    # ===== LABELS =====
    text_effects = [pe.withStroke(linewidth=3, foreground='white')]

    for state_name, info in MATOPIBA_STATES.items():
        if state_name in clipped_states:
            # Centralizar label no centroide da geometria recortada
            centroid = clipped_states[state_name].centroid
            lx, ly = centroid.x, centroid.y

            ax.text(lx, ly, info['abbr'],
                    fontsize=18, fontweight='bold', color=info['color'],
                    ha='center', va='center',
                    transform=ccrs.PlateCarree(), zorder=8,
                    path_effects=text_effects)

    # ===== GRIDLINES =====
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray',
                       alpha=0.4, linestyle='--', zorder=6)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 9, 'color': '#333333'}
    gl.ylabel_style = {'size': 9, 'color': '#333333'}

    # ===== CARTOGRAFIA =====
    add_north_arrow(ax)
    add_scale_bar(ax, -49.5, -15.8, 200, ccrs.PlateCarree())

    ax.set_title('Regiao MATOPIBA - Area de Estudo',
                  fontsize=15, fontweight='bold', pad=12, color='#222222')

    # ===== INSET: BRASIL =====
    ax_inset = fig.add_axes([0.70, 0.52, 0.28, 0.42], projection=ccrs.PlateCarree())
    ax_inset.set_extent(BRAZIL_EXTENT, crs=ccrs.PlateCarree())

    ax_inset.add_feature(cfeature.OCEAN, facecolor='#D6EAF8')
    for name, geom in brazil_states.items():
        if name in MATOPIBA_STATES:
            # Mostrar estado inteiro com cor leve, recorte mais intenso
            ax_inset.add_geometries([geom], ccrs.PlateCarree(),
                                     facecolor='#E0E0E0', alpha=1.0,
                                     edgecolor='#999999', linewidth=0.3)
            if name in clipped_states:
                ax_inset.add_geometries([clipped_states[name]], ccrs.PlateCarree(),
                                         facecolor=MATOPIBA_STATES[name]['color'],
                                         alpha=0.6,
                                         edgecolor='none', linewidth=0)
        else:
            ax_inset.add_geometries([geom], ccrs.PlateCarree(),
                                     facecolor='#E0E0E0', alpha=1.0,
                                     edgecolor='#999999', linewidth=0.3)

    ax_inset.add_feature(cfeature.COASTLINE, linewidth=0.4, edgecolor='#666666')

    # Retangulo de extent do mapa principal
    from matplotlib.patches import Rectangle
    rect = Rectangle((MAP_EXTENT[0], MAP_EXTENT[2]),
                      MAP_EXTENT[1] - MAP_EXTENT[0],
                      MAP_EXTENT[3] - MAP_EXTENT[2],
                      linewidth=1.5, edgecolor='red', facecolor='none',
                      transform=ccrs.PlateCarree(), zorder=10)
    ax_inset.add_patch(rect)
    ax_inset.set_title('Brasil', fontsize=10, fontweight='bold', color='#333333')

    # ===== PAINEL INFO =====
    ax_info = fig.add_axes([0.68, 0.05, 0.28, 0.42])
    ax_info.axis('off')

    info_text = (
        "MATOPIBA\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Area: ~73 milhoes ha\n"
        "Municipios: 337\n"
        "Bioma: Cerrado (91%)\n\n"
        "Limite do recorte:\n"
        f"  Lat: {abs(MATOPIBA_BOUNDS['south'])}°S"
        f" a {abs(MATOPIBA_BOUNDS['north'])}°S\n"
        f"  Lon: {abs(MATOPIBA_BOUNDS['west'])}°W"
        f" a {abs(MATOPIBA_BOUNDS['east'])}°W\n\n"
        "Fronteira agricola com alta incidencia de\n" "incendios florestais e queimadas agricolas."
    )
    ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes,
                 fontsize=9.5, verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFDE7',
                           alpha=0.95, edgecolor='#CCCCCC'))

    # Legenda
    legend_handles = [
        mpatches.Patch(facecolor=info['color'], alpha=info['alpha'],
                       edgecolor=info['color'], linewidth=1.5,
                       label=f"{info['abbr']} - {name}")
        for name, info in MATOPIBA_STATES.items()
    ]
    legend_handles.append(
        plt.Line2D([0], [0], color='#333333', linewidth=2.5,
                   label='Limite MATOPIBA')
    )
    ax_info.legend(handles=legend_handles, loc='lower left', fontsize=8.5,
                   framealpha=0.95, edgecolor='#CCCCCC', title='Legenda',
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
    print("[OK] Mapa v2 gerado com sucesso!")


if __name__ == '__main__':
    generate_map_v2()
