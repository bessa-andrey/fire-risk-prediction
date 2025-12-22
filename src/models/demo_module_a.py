# demo_module_a.py
"""
Demonstration script for Module A - Spurious Detection Classifier

Shows the model making real-time predictions on sample hotspots.
Useful for presentations and thesis defense.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import json

# Paths
MODEL_PATH = Path('data/models/module_a/module_a_lightgbm.pkl')  # Use LightGBM (matches saved scaler)
SCALER_PATH = Path('data/models/module_a/scaler.pkl')
DATA_PATH = Path('data/processed/training/module_a_balanced.csv')

# Feature columns (same order as training)
FEATURE_COLS = [
    'brightness', 'confidence', 'frp', 'hotspot_count',
    'persistence_score', 'temperature', 'dewpoint',
    'wind_speed', 'precipitation', 'rh', 'drying_index'
]

def load_model():
    """Load trained model"""
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    return model

def load_scaler():
    """Load fitted scaler"""
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    return scaler

def predict_single(model, scaler, hotspot_features: dict) -> dict:
    """
    Predict for a single hotspot

    Args:
        model: Trained classifier
        scaler: Fitted StandardScaler
        hotspot_features: Dictionary with feature values

    Returns:
        Dictionary with prediction results
    """
    # Create feature vector
    X = np.array([[hotspot_features.get(col, 0) for col in FEATURE_COLS]])

    # Scale features (IMPORTANT!)
    X_scaled = scaler.transform(X)

    # Predict
    prob = model.predict_proba(X_scaled)[0]
    prediction = model.predict(X_scaled)[0]

    return {
        'prediction': int(prediction),
        'label': 'CONFIAVEL' if prediction == 1 else 'SUSPEITO',
        'probability_reliable': float(prob[1]),
        'probability_spurious': float(prob[0]),
        'confidence_level': 'Alta' if max(prob) > 0.9 else 'Media' if max(prob) > 0.7 else 'Baixa'
    }

def demo_random_samples(n_samples=5):
    """Demo with random samples from the dataset"""
    print("\n" + "="*70)
    print("DEMONSTRACAO - MODULO A: CLASSIFICADOR DE HOTSPOTS")
    print("="*70)

    # Load model and scaler
    print("\n[1] Carregando modelo LightGBM treinado...")
    model = load_model()
    scaler = load_scaler()
    print("    Modelo e scaler carregados com sucesso!")

    # Load sample data
    print("\n[2] Carregando dados de teste...")
    df = pd.read_csv(DATA_PATH)

    # Get random samples (mix of reliable and spurious)
    reliable_samples = df[df['is_reliable'] == 1].sample(n=n_samples//2 + 1, random_state=42)
    spurious_samples = df[df['is_reliable'] == 0].sample(n=n_samples//2, random_state=42)
    samples = pd.concat([reliable_samples, spurious_samples]).sample(frac=1, random_state=123)

    print(f"    Selecionados {len(samples)} hotspots aleatorios\n")

    # Predict each sample
    print("[3] PREDICOES:")
    print("-"*70)

    correct = 0
    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        # Get features
        features = {col: row[col] for col in FEATURE_COLS}
        true_label = int(row['is_reliable'])

        # Predict
        result = predict_single(model, scaler, features)

        # Check if correct
        is_correct = result['prediction'] == true_label
        correct += is_correct
        status = "OK" if is_correct else "ERRO"

        print(f"\n  Hotspot #{idx}")
        print(f"  ├─ Localizacao: ({row['latitude']:.4f}, {row['longitude']:.4f})")
        print(f"  ├─ FRP: {row['frp']:.1f} MW")
        print(f"  ├─ Persistencia: {row['persistence_score']:.2f}")
        print(f"  ├─ Drying Index: {row['drying_index']:.1f}")
        print(f"  ├─ Confianca VIIRS: {row['confidence']:.0f}%")
        print(f"  │")
        print(f"  ├─ PREDICAO: {result['label']} ({result['probability_reliable']*100:.1f}% confiavel)")
        print(f"  ├─ Nivel de certeza: {result['confidence_level']}")
        print(f"  ├─ Verdade: {'CONFIAVEL' if true_label == 1 else 'SUSPEITO'}")
        print(f"  └─ Status: [{status}]")

    print("\n" + "-"*70)
    print(f"RESUMO: {correct}/{len(samples)} predicoes corretas ({100*correct/len(samples):.0f}%)")
    print("-"*70)

def demo_custom_hotspot():
    """Demo with custom user-defined hotspot"""
    print("\n" + "="*70)
    print("DEMO INTERATIVA - INSIRA DADOS DO HOTSPOT")
    print("="*70)

    model = load_model()
    scaler = load_scaler()

    # Get user input
    print("\nInsira os valores do hotspot (ou pressione Enter para usar default):\n")

    defaults = {
        'brightness': 340.0,
        'confidence': 70.0,
        'frp': 25.0,
        'hotspot_count': 2,
        'persistence_score': 0.3,
        'temperature': 28.0,
        'dewpoint': 18.0,
        'wind_speed': 2.5,
        'precipitation': 0.0,
        'rh': 50.0,
        'drying_index': 50.0
    }

    features = {}
    for col in FEATURE_COLS:
        try:
            val = input(f"  {col} [{defaults[col]}]: ")
            features[col] = float(val) if val else defaults[col]
        except ValueError:
            features[col] = defaults[col]

    # Predict
    result = predict_single(model, scaler, features)

    print("\n" + "-"*50)
    print("RESULTADO DA CLASSIFICACAO")
    print("-"*50)
    print(f"  Predicao: {result['label']}")
    print(f"  Probabilidade Confiavel: {result['probability_reliable']*100:.1f}%")
    print(f"  Probabilidade Suspeito: {result['probability_spurious']*100:.1f}%")
    print(f"  Nivel de Certeza: {result['confidence_level']}")
    print("-"*50)

def demo_extreme_cases():
    """Demo showing extreme cases - clearly real vs clearly spurious"""
    print("\n" + "="*70)
    print("DEMO - CASOS EXTREMOS")
    print("="*70)

    model = load_model()
    scaler = load_scaler()

    # Case 1: Clearly real fire
    real_fire = {
        'brightness': 380.0,      # Very hot
        'confidence': 90.0,       # High confidence
        'frp': 150.0,             # Very high FRP
        'hotspot_count': 10,      # Many detections
        'persistence_score': 0.8, # High persistence
        'temperature': 32.0,      # Hot day
        'dewpoint': 12.0,         # Low humidity
        'wind_speed': 4.0,        # Moderate wind
        'precipitation': 0.0,     # No rain
        'rh': 25.0,               # Very dry
        'drying_index': 75.0      # Very dry conditions
    }

    # Case 2: Likely spurious
    spurious = {
        'brightness': 310.0,      # Low temperature
        'confidence': 30.0,       # Low confidence
        'frp': 2.0,               # Very low FRP
        'hotspot_count': 1,       # Single detection
        'persistence_score': 0.05,# No persistence
        'temperature': 22.0,      # Cool day
        'dewpoint': 20.0,         # High humidity
        'wind_speed': 1.0,        # Light wind
        'precipitation': 5.0,     # Recent rain
        'rh': 85.0,               # Very humid
        'drying_index': 15.0      # Wet conditions
    }

    print("\n[CASO 1] Fogo Real Tipico:")
    print("  - FRP muito alto (150 MW)")
    print("  - Alta persistencia (0.8)")
    print("  - Condicoes muito secas (RH=25%)")
    result1 = predict_single(model, scaler, real_fire)
    print(f"\n  >>> PREDICAO: {result1['label']} ({result1['probability_reliable']*100:.1f}% confiavel)")

    print("\n" + "-"*50)

    print("\n[CASO 2] Falso Positivo Tipico:")
    print("  - FRP muito baixo (2 MW)")
    print("  - Sem persistencia (0.05)")
    print("  - Condicoes umidas (RH=85%)")
    result2 = predict_single(model, scaler, spurious)
    print(f"\n  >>> PREDICAO: {result2['label']} ({result2['probability_spurious']*100:.1f}% suspeito)")

    print("\n" + "="*70)

def demo_feature_importance():
    """Show which features are most important"""
    print("\n" + "="*70)
    print("IMPORTANCIA DAS FEATURES")
    print("="*70)

    model = load_model()

    # Get feature importance
    importance = model.feature_importances_

    # Sort by importance
    sorted_idx = np.argsort(importance)[::-1]

    print("\nRanking das features mais importantes:\n")
    for rank, idx in enumerate(sorted_idx, 1):
        bar_len = int(importance[idx] * 50)
        bar = "#" * bar_len
        print(f"  {rank}. {FEATURE_COLS[idx]:20s} {importance[idx]:.3f} {bar}")

def main():
    """Main demo function"""
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "     MODULO A - DETECTOR DE HOTSPOTS ESPURIOS     ".center(68) + "#")
    print("#" + "     Mestrado - Deteccao de Incendios MATOPIBA    ".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)

    while True:
        print("\n" + "-"*50)
        print("MENU DE DEMONSTRACAO")
        print("-"*50)
        print("  1. Testar com amostras aleatorias")
        print("  2. Inserir hotspot customizado")
        print("  3. Ver casos extremos")
        print("  4. Ver importancia das features")
        print("  5. Sair")
        print("-"*50)

        choice = input("\nEscolha uma opcao [1-5]: ")

        if choice == '1':
            n = input("Quantas amostras? [5]: ")
            n = int(n) if n else 5
            demo_random_samples(n_samples=n)
        elif choice == '2':
            demo_custom_hotspot()
        elif choice == '3':
            demo_extreme_cases()
        elif choice == '4':
            demo_feature_importance()
        elif choice == '5':
            print("\nAte logo!")
            break
        else:
            print("Opcao invalida!")

if __name__ == '__main__':
    main()
