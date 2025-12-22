# map_hotspots.py
"""
Generate maps showing classified hotspots (reliable vs spurious)
Uses the trained Module A model to classify hotspots and visualize on maps.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

# Paths
MODEL_PATH = Path('data/models/module_a/module_a_lightgbm.pkl')
SCALER_PATH = Path('data/models/module_a/scaler.pkl')
DATA_PATH = Path('data/processed/training/module_a_balanced.csv')
OUTPUT_DIR = Path('data/visualizations')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Feature columns
FEATURE_COLS = [
    'brightness', 'confidence', 'frp', 'hotspot_count',
    'persistence_score', 'temperature', 'dewpoint',
    'wind_speed', 'precipitation', 'rh', 'drying_index'
]

# MATOPIBA bounds
MATOPIBA_BOUNDS = {
    'north': -2,
    'south': -15,
    'east': -42,
    'west': -50
}

def load_model_and_scaler():
    """Load trained model and scaler"""
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler

def classify_hotspots(df, model, scaler):
    """Classify all hotspots in dataframe"""
    # Prepare features
    X = df[FEATURE_COLS].values
    X_scaled = scaler.transform(X)

    # Predict
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)[:, 1]

    df = df.copy()
    df['prediction'] = predictions
    df['prob_reliable'] = probabilities
    df['label'] = df['prediction'].map({1: 'CONFIAVEL', 0: 'SUSPEITO'})

    return df

def plot_regional_map(df, title, output_file, bounds=None):
    """
    Plot hotspots on a regional map

    Args:
        df: DataFrame with classified hotspots
        title: Plot title
        output_file: Output file path
        bounds: Dict with north, south, east, west bounds (optional)
    """
    if bounds is None:
        bounds = MATOPIBA_BOUNDS

    fig, ax = plt.subplots(figsize=(12, 10))

    # Separate by classification
    reliable = df[df['prediction'] == 1]
    spurious = df[df['prediction'] == 0]

    # Plot spurious first (background)
    if len(spurious) > 0:
        ax.scatter(
            spurious['longitude'], spurious['latitude'],
            c='red', alpha=0.5, s=20, label=f'Suspeito (n={len(spurious)})',
            marker='x'
        )

    # Plot reliable on top
    if len(reliable) > 0:
        ax.scatter(
            reliable['longitude'], reliable['latitude'],
            c='green', alpha=0.6, s=30, label=f'Confiavel (n={len(reliable)})',
            marker='o'
        )

    # Set bounds
    ax.set_xlim(bounds['west'], bounds['east'])
    ax.set_ylim(bounds['south'], bounds['north'])

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # Labels
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Legend
    ax.legend(loc='upper right', fontsize=10)

    # Add statistics box
    stats_text = (
        f"Total: {len(df)} hotspots\n"
        f"Confiaveis: {len(reliable)} ({100*len(reliable)/len(df):.1f}%)\n"
        f"Suspeitos: {len(spurious)} ({100*len(spurious)/len(df):.1f}%)"
    )
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"[OK] Map saved: {output_file}")
    return output_file

def plot_zoomed_comparison(df, center_lat, center_lon, radius=0.5, title="", output_file=None):
    """
    Plot zoomed view comparing reliable vs spurious hotspots

    Args:
        df: DataFrame with classified hotspots
        center_lat, center_lon: Center coordinates
        radius: Radius in degrees
        title: Plot title
        output_file: Output file path
    """
    # Filter to region
    mask = (
        (df['latitude'] >= center_lat - radius) &
        (df['latitude'] <= center_lat + radius) &
        (df['longitude'] >= center_lon - radius) &
        (df['longitude'] <= center_lon + radius)
    )
    region_df = df[mask].copy()

    if len(region_df) == 0:
        print(f"[WARNING] No hotspots in region ({center_lat}, {center_lon})")
        return None

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    reliable = region_df[region_df['prediction'] == 1]
    spurious = region_df[region_df['prediction'] == 0]

    # Left: All hotspots colored by classification
    ax1 = axes[0]
    if len(spurious) > 0:
        scatter1 = ax1.scatter(
            spurious['longitude'], spurious['latitude'],
            c='red', alpha=0.7, s=50, label='Suspeito', marker='x', linewidths=2
        )
    if len(reliable) > 0:
        scatter2 = ax1.scatter(
            reliable['longitude'], reliable['latitude'],
            c='green', alpha=0.7, s=50, label='Confiavel', marker='o'
        )

    ax1.set_xlim(center_lon - radius, center_lon + radius)
    ax1.set_ylim(center_lat - radius, center_lat + radius)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title('Classificacao por Tipo', fontweight='bold')
    ax1.legend()

    # Right: Hotspots colored by probability
    ax2 = axes[1]
    scatter = ax2.scatter(
        region_df['longitude'], region_df['latitude'],
        c=region_df['prob_reliable'], cmap='RdYlGn',
        alpha=0.8, s=50, vmin=0, vmax=1
    )

    ax2.set_xlim(center_lon - radius, center_lon + radius)
    ax2.set_ylim(center_lat - radius, center_lat + radius)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.set_title('Probabilidade de Fogo Real', fontweight='bold')

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('P(Confiavel)')

    # Main title
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"[OK] Zoomed map saved: {output_file}")

    plt.close()
    return output_file

def plot_feature_distribution(df, output_file):
    """
    Plot feature distributions for reliable vs spurious
    """
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    axes = axes.flatten()

    reliable = df[df['prediction'] == 1]
    spurious = df[df['prediction'] == 0]

    features_to_plot = FEATURE_COLS + ['prob_reliable']

    for idx, feature in enumerate(features_to_plot):
        if idx >= len(axes):
            break

        ax = axes[idx]

        # Plot histograms
        ax.hist(spurious[feature], bins=30, alpha=0.5, color='red',
                label='Suspeito', density=True)
        ax.hist(reliable[feature], bins=30, alpha=0.5, color='green',
                label='Confiavel', density=True)

        ax.set_xlabel(feature)
        ax.set_ylabel('Densidade')
        ax.legend(fontsize=8)
        ax.set_title(feature, fontweight='bold')

    # Hide unused axes
    for idx in range(len(features_to_plot), len(axes)):
        axes[idx].set_visible(False)

    fig.suptitle('Distribuicao das Features por Classificacao', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"[OK] Feature distribution saved: {output_file}")
    return output_file

def generate_demo_maps(n_samples=2000):
    """Generate demonstration maps"""
    print("\n" + "="*60)
    print("GERACAO DE MAPAS - MODULO A")
    print("="*60)

    # Load model and data
    print("\n[1] Carregando modelo e dados...")
    model, scaler = load_model_and_scaler()
    df = pd.read_csv(DATA_PATH)
    print(f"    Loaded {len(df)} samples")

    # Sample for visualization
    if len(df) > n_samples:
        df = df.sample(n=n_samples, random_state=42)
        print(f"    Sampled {n_samples} for visualization")

    # Classify hotspots
    print("\n[2] Classificando hotspots...")
    df = classify_hotspots(df, model, scaler)

    reliable_count = (df['prediction'] == 1).sum()
    spurious_count = (df['prediction'] == 0).sum()
    print(f"    Confiaveis: {reliable_count} ({100*reliable_count/len(df):.1f}%)")
    print(f"    Suspeitos: {spurious_count} ({100*spurious_count/len(df):.1f}%)")

    # Generate maps
    print("\n[3] Gerando mapas...")

    # Map 1: Full MATOPIBA region
    plot_regional_map(
        df,
        title='Classificacao de Hotspots - Regiao MATOPIBA',
        output_file=OUTPUT_DIR / 'mapa_matopiba_classificacao.png'
    )

    # Map 2: Zoomed view - high fire activity area (Tocantins)
    plot_zoomed_comparison(
        df,
        center_lat=-10.0, center_lon=-47.0, radius=1.5,
        title='Zoom: Tocantins - Comparacao de Classificacao',
        output_file=OUTPUT_DIR / 'mapa_zoom_tocantins.png'
    )

    # Map 3: Zoomed view - Maranhao
    plot_zoomed_comparison(
        df,
        center_lat=-5.5, center_lon=-45.0, radius=1.5,
        title='Zoom: Maranhao - Comparacao de Classificacao',
        output_file=OUTPUT_DIR / 'mapa_zoom_maranhao.png'
    )

    # Map 4: Feature distributions
    plot_feature_distribution(
        df,
        output_file=OUTPUT_DIR / 'distribuicao_features.png'
    )

    print("\n" + "="*60)
    print("MAPAS GERADOS COM SUCESSO!")
    print("="*60)
    print(f"\nArquivos salvos em: {OUTPUT_DIR}")

    return df

def generate_single_region_map(lat, lon, radius=1.0, title=None):
    """
    Generate a map for a specific region

    Args:
        lat, lon: Center coordinates
        radius: Radius in degrees
        title: Optional title
    """
    print(f"\n[INFO] Generating map for region ({lat}, {lon})...")

    model, scaler = load_model_and_scaler()
    df = pd.read_csv(DATA_PATH)
    df = classify_hotspots(df, model, scaler)

    if title is None:
        title = f'Hotspots em ({lat:.2f}, {lon:.2f})'

    output_file = OUTPUT_DIR / f'mapa_regiao_{lat:.1f}_{lon:.1f}.png'

    plot_zoomed_comparison(
        df,
        center_lat=lat, center_lon=lon, radius=radius,
        title=title,
        output_file=output_file
    )

    return output_file

if __name__ == '__main__':
    df = generate_demo_maps()
    print("\n[INFO] Visualization complete!")
