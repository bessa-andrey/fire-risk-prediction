# validate_weak_labels.py
"""
Weak Label Validation: Manual verification of label quality.

Selects a stratified sample of 200 labeled hotspots for manual verification
against satellite imagery (Google Earth Engine / Sentinel-2).

Methodology:
1. Stratified sampling: proportional to class distribution across states/years
2. Export sample with coordinates and metadata for GEE visual inspection
3. After manual annotation, compute Cohen's Kappa and other agreement metrics
4. Sensitivity analysis: test +-10, +-15, +-20 day windows

Input: hotspots_labeled.csv (from weak_labeling.py)
Output:
  - validation_sample.csv (200 samples for manual review)
  - validation_sample.gpkg (GeoPackage for GIS visualization)
  - validation_gee_script.js (GEE script for visual inspection)
  - validation_results.json (after manual annotation - Cohen's Kappa)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Configuration
PROCESSED_DIR = Path('data/processed')
LABELED_FILE = PROCESSED_DIR / 'module_a' / 'module_a_features.csv'
OUTPUT_DIR = PROCESSED_DIR / 'validation'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

N_SAMPLES = 200
RANDOM_STATE = 42

# MATOPIBA state classification by coordinates (approximate)
STATE_BOUNDS = {
    'MA': {'lat_min': -10.3, 'lat_max': -2.8, 'lon_min': -48.0, 'lon_max': -42.8},
    'TO': {'lat_min': -13.5, 'lat_max': -5.0, 'lon_min': -50.8, 'lon_max': -45.5},
    'PI': {'lat_min': -10.9, 'lat_max': -3.0, 'lon_min': -45.5, 'lon_max': -40.3},
    'BA': {'lat_min': -15.0, 'lat_max': -10.0, 'lon_min': -46.5, 'lon_max': -43.0},
}


def classify_state(lat, lon):
    """Classify a point into a MATOPIBA state based on coordinates"""
    for state, bounds in STATE_BOUNDS.items():
        if (bounds['lat_min'] <= lat <= bounds['lat_max'] and
                bounds['lon_min'] <= lon <= bounds['lon_max']):
            return state
    return 'OTHER'


def select_stratified_sample(df, n_samples=200, random_state=42):
    """
    Select stratified sample maintaining proportional representation of:
    - Label class (real vs spurious)
    - State (MA, TO, PI, BA)
    - Year

    Args:
        df: labeled dataframe with latitude, longitude, label columns
        n_samples: target number of samples

    Returns:
        DataFrame with selected samples
    """
    print(f"[INFO] Selecting {n_samples} stratified samples...")

    # Determine label column
    label_col = None
    for candidate in ['label', 'is_reliable', 'label_text']:
        if candidate in df.columns:
            label_col = candidate
            break

    if label_col is None:
        print("[ERROR] No label column found")
        return pd.DataFrame()

    # Assign state
    df['state'] = df.apply(lambda r: classify_state(r['latitude'], r['longitude']), axis=1)

    # Extract year if datetime available
    for date_col in ['acq_datetime', 'acq_date']:
        if date_col in df.columns:
            df['year'] = pd.to_datetime(df[date_col]).dt.year
            break

    # Build stratification groups
    strat_cols = [label_col]
    if 'state' in df.columns:
        strat_cols.append('state')
    if 'year' in df.columns:
        strat_cols.append('year')

    # Create stratification key
    df['strat_key'] = df[strat_cols].astype(str).agg('_'.join, axis=1)

    # Proportional allocation
    group_counts = df['strat_key'].value_counts()
    total = len(df)

    samples = []
    remaining = n_samples

    for group_key, group_count in group_counts.items():
        # Proportional number of samples from this group
        n_group = max(1, int(round(n_samples * group_count / total)))
        n_group = min(n_group, group_count, remaining)

        if n_group > 0:
            group_df = df[df['strat_key'] == group_key]
            group_sample = group_df.sample(n=n_group, random_state=random_state)
            samples.append(group_sample)
            remaining -= n_group

        if remaining <= 0:
            break

    # If we haven't reached target, add more randomly
    if remaining > 0:
        already_selected = pd.concat(samples).index
        leftover = df.drop(already_selected)
        if len(leftover) > 0:
            extra = leftover.sample(n=min(remaining, len(leftover)), random_state=random_state)
            samples.append(extra)

    sample_df = pd.concat(samples).drop(columns=['strat_key'])

    print(f"[OK] Selected {len(sample_df)} samples")
    print(f"  By label: {sample_df[label_col].value_counts().to_dict()}")
    if 'state' in sample_df.columns:
        print(f"  By state: {sample_df['state'].value_counts().to_dict()}")
    if 'year' in sample_df.columns:
        print(f"  By year: {sample_df['year'].value_counts().to_dict()}")

    return sample_df


def generate_gee_script(sample_df, output_path):
    """
    Generate Google Earth Engine JavaScript for visual inspection.

    Creates a script that:
    - Loads Sentinel-2 imagery for each sample point
    - Displays true color and false color composites
    - Shows NBR (Normalized Burn Ratio) for burn scar detection
    - Allows manual classification via visual inspection
    """
    print("[INFO] Generating GEE inspection script...")

    # Build point features
    points_js = []
    for idx, row in sample_df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        date = row.get('acq_datetime', row.get('acq_date', '2023-01-01'))
        label = row.get('label', row.get('is_reliable', 'unknown'))
        sample_id = row.get('hotspot_id', idx)

        points_js.append(
            f"  ee.Feature(ee.Geometry.Point([{lon}, {lat}]), "
            f"{{'id': '{sample_id}', 'weak_label': {label}, 'date': '{date}'}})"
        )

    points_str = ",\n".join(points_js)

    script = f"""// Weak Label Validation - Visual Inspection Script
// Generated: {datetime.now().isoformat()}
// Total samples: {len(sample_df)}
//
// Instructions:
// 1. Run this script in Google Earth Engine Code Editor
// 2. Click on each point to inspect the Sentinel-2 imagery
// 3. Compare RGB + NBR composites to determine if burn scar is visible
// 4. Record your classification in the spreadsheet
// 5. Manual label: 0 = Real fire (burn scar visible), 1 = Spurious (no evidence)

// Sample points
var samples = ee.FeatureCollection([
{points_str}
]);

// Function to get Sentinel-2 imagery around a date
function getS2Composite(point, dateStr) {{
  var date = ee.Date(dateStr);
  var geometry = point.geometry().buffer(1000);  // 1km buffer

  // Pre-fire: 30-60 days before
  var preFire = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(geometry)
    .filterDate(date.advance(-60, 'day'), date.advance(-30, 'day'))
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
    .median()
    .clip(geometry);

  // Post-fire: 0-30 days after
  var postFire = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(geometry)
    .filterDate(date, date.advance(30, 'day'))
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
    .median()
    .clip(geometry);

  return {{pre: preFire, post: postFire}};
}}

// Visualization parameters
var rgbVis = {{bands: ['B4', 'B3', 'B2'], min: 0, max: 3000}};
var nbr_vis = {{min: -0.5, max: 0.5, palette: ['red', 'yellow', 'green']}};

// Add NBR (Normalized Burn Ratio)
function addNBR(image) {{
  var nbr = image.normalizedDifference(['B8', 'B12']).rename('NBR');
  return image.addBands(nbr);
}}

// Display first sample as example
var firstSample = ee.Feature(samples.first());
var firstDate = firstSample.get('date').getInfo();
var firstPoint = firstSample.geometry();

Map.centerObject(firstPoint, 13);

var imagery = getS2Composite(firstSample, firstDate);
var preWithNBR = addNBR(imagery.pre);
var postWithNBR = addNBR(imagery.post);

Map.addLayer(imagery.pre, rgbVis, 'Pre-fire RGB');
Map.addLayer(imagery.post, rgbVis, 'Post-fire RGB');
Map.addLayer(preWithNBR.select('NBR'), nbr_vis, 'Pre-fire NBR');
Map.addLayer(postWithNBR.select('NBR'), nbr_vis, 'Post-fire NBR');

// dNBR (difference) - positive values indicate burn scars
var dNBR = preWithNBR.select('NBR').subtract(postWithNBR.select('NBR')).rename('dNBR');
Map.addLayer(dNBR, {{min: -0.3, max: 0.6, palette: ['green', 'yellow', 'orange', 'red']}}, 'dNBR (burn severity)');

// Add all sample points
Map.addLayer(samples, {{color: 'red'}}, 'Validation Samples');

// Click handler
Map.onClick(function(coords) {{
  var point = ee.Geometry.Point([coords.lon, coords.lat]);
  var nearest = samples.filterBounds(point.buffer(5000)).first();

  if (nearest) {{
    var info = nearest.getInfo();
    print('Sample ID:', info.properties.id);
    print('Weak Label:', info.properties.weak_label);
    print('Date:', info.properties.date);
    print('---');
    print('Inspect RGB and dNBR layers above.');
    print('Record manual label in validation spreadsheet.');
  }}
}});

print('=== WEAK LABEL VALIDATION ===');
print('Total samples:', samples.size());
print('Click on points to inspect.');
print('Layers: Pre/Post RGB, NBR, dNBR');
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(script)

    print(f"[OK] GEE script saved to: {output_path}")


def compute_agreement_metrics(sample_df, manual_label_col='manual_label'):
    """
    Compute agreement metrics between weak labels and manual labels.

    Metrics:
    - Cohen's Kappa: chance-corrected agreement
    - Overall agreement (accuracy)
    - Per-class agreement
    - Confusion matrix

    Cohen's Kappa interpretation:
    - < 0.20: Poor
    - 0.21-0.40: Fair
    - 0.41-0.60: Moderate
    - 0.61-0.80: Substantial
    - 0.81-1.00: Almost perfect

    Args:
        sample_df: DataFrame with weak labels and manual labels
        manual_label_col: column name with manual annotations

    Returns:
        dict with agreement metrics
    """
    if manual_label_col not in sample_df.columns:
        print(f"[WARNING] Column '{manual_label_col}' not found.")
        print("[INFO] After manual annotation, add the column and re-run.")
        return None

    # Determine weak label column
    weak_label_col = None
    for candidate in ['label', 'is_reliable']:
        if candidate in sample_df.columns:
            weak_label_col = candidate
            break

    if weak_label_col is None:
        print("[ERROR] No weak label column found")
        return None

    weak = sample_df[weak_label_col].values
    manual = sample_df[manual_label_col].values

    # Remove NaN
    valid_mask = ~(pd.isna(weak) | pd.isna(manual))
    weak = weak[valid_mask].astype(int)
    manual = manual[valid_mask].astype(int)

    n = len(weak)
    if n == 0:
        print("[ERROR] No valid paired labels")
        return None

    # Overall agreement
    agreement = (weak == manual).sum() / n

    # Confusion matrix
    from sklearn.metrics import confusion_matrix, cohen_kappa_score

    cm = confusion_matrix(manual, weak, labels=[0, 1])
    kappa = cohen_kappa_score(manual, weak)

    # Per-class metrics
    tp = cm[1, 1]  # True positive (both say spurious)
    tn = cm[0, 0]  # True negative (both say real)
    fp = cm[0, 1]  # Weak says spurious, manual says real
    fn = cm[1, 0]  # Weak says real, manual says spurious

    results = {
        'n_samples': int(n),
        'overall_agreement': float(agreement),
        'cohens_kappa': float(kappa),
        'kappa_interpretation': interpret_kappa(kappa),
        'confusion_matrix': {
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
        },
        'weak_label_accuracy': {
            'class_0_correct': float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0,
            'class_1_correct': float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0,
        },
        'estimated_noise': float(1 - agreement),
    }

    print(f"\n{'='*50}")
    print("WEAK LABEL VALIDATION RESULTS")
    print(f"{'='*50}")
    print(f"  Samples validated: {n}")
    print(f"  Overall agreement: {agreement:.3f} ({agreement*100:.1f}%)")
    print(f"  Cohen's Kappa:     {kappa:.3f} ({results['kappa_interpretation']})")
    print(f"  Estimated noise:   {results['estimated_noise']:.3f} ({results['estimated_noise']*100:.1f}%)")
    print(f"\n  Confusion Matrix (manual x weak):")
    print(f"                    Weak=Real  Weak=Spurious")
    print(f"  Manual=Real       {tn:>8}  {fp:>12}")
    print(f"  Manual=Spurious   {fn:>8}  {tp:>12}")

    return results


def interpret_kappa(kappa):
    """Interpret Cohen's Kappa value"""
    if kappa < 0.20:
        return "Poor"
    elif kappa < 0.40:
        return "Fair"
    elif kappa < 0.60:
        return "Moderate"
    elif kappa < 0.80:
        return "Substantial"
    else:
        return "Almost perfect"


def sensitivity_analysis(df, windows=[10, 15, 20]):
    """
    Analyze label sensitivity to temporal window size.

    Reports how many labels would change with different windows.
    This is informative even without manual labels.

    Args:
        df: labeled dataframe
        windows: list of window sizes (days) to test
    """
    print(f"\n{'='*50}")
    print("SENSITIVITY ANALYSIS - TEMPORAL WINDOW")
    print(f"{'='*50}")

    # Determine label column
    label_col = None
    for candidate in ['label', 'is_reliable']:
        if candidate in df.columns:
            label_col = candidate
            break

    if label_col is None:
        print("[WARNING] Cannot perform sensitivity analysis without label column")
        return {}

    results = {}
    total = len(df)
    current_labels = df[label_col].value_counts().to_dict()

    print(f"  Current labels (window=+-15 days): {current_labels}")
    print(f"  Total samples: {total}")
    print()

    # For each alternative window, report expected changes
    for window in windows:
        # We can estimate the sensitivity by looking at the temporal gap
        # between FIRMS detection and MCD64A1 burn date
        if 'temporal_gap_days' in df.columns:
            would_change = df[abs(df['temporal_gap_days']) > window]
            n_changed = len(would_change)
            pct_changed = n_changed / total * 100

            results[f'window_{window}'] = {
                'window_days': window,
                'samples_affected': n_changed,
                'pct_affected': float(pct_changed),
            }
            print(f"  Window +-{window} days: {n_changed} samples would change ({pct_changed:.1f}%)")
        else:
            print(f"  Window +-{window} days: temporal_gap_days column not available")
            results[f'window_{window}'] = {
                'window_days': window,
                'note': 'temporal_gap_days column not available for analysis',
            }

    return results


def main():
    """Main validation pipeline"""
    print("\n" + "=" * 60)
    print("WEAK LABEL VALIDATION")
    print("=" * 60)

    # Step 1: Load labeled data
    if not LABELED_FILE.exists():
        # Try alternate path
        alt_path = PROCESSED_DIR / 'training' / 'module_a_balanced.csv'
        if alt_path.exists():
            input_file = alt_path
        else:
            print(f"[ERROR] Labeled data not found: {LABELED_FILE}")
            print("[INFO] Run weak_labeling.py and feature_engineering.py first")
            return
    else:
        input_file = LABELED_FILE

    print(f"[INFO] Loading labeled data from {input_file}...")
    df = pd.read_csv(input_file)
    print(f"[OK] Loaded {len(df)} samples")

    # Step 2: Select stratified sample
    sample_df = select_stratified_sample(df, n_samples=N_SAMPLES, random_state=RANDOM_STATE)

    # Step 3: Add columns for manual annotation
    sample_df['manual_label'] = np.nan  # To be filled manually
    sample_df['manual_confidence'] = np.nan  # Annotator confidence (1-5)
    sample_df['manual_notes'] = ''  # Free text notes
    sample_df['gee_burn_evidence'] = np.nan  # 0=no evidence, 1=possible, 2=clear

    # Step 4: Save sample for review
    sample_csv = OUTPUT_DIR / 'validation_sample.csv'
    sample_df.to_csv(sample_csv, index=False)
    print(f"[OK] Validation sample saved to: {sample_csv}")

    # Step 5: Save as GeoPackage (if geopandas available)
    try:
        import geopandas as gpd
        from shapely.geometry import Point

        geometry = [Point(row['longitude'], row['latitude']) for _, row in sample_df.iterrows()]
        gdf = gpd.GeoDataFrame(sample_df, geometry=geometry, crs='EPSG:4326')
        gpkg_path = OUTPUT_DIR / 'validation_sample.gpkg'
        gdf.to_file(gpkg_path, driver='GPKG')
        print(f"[OK] GeoPackage saved to: {gpkg_path}")
    except ImportError:
        print("[WARNING] geopandas not installed, skipping GeoPackage export")

    # Step 6: Generate GEE script
    gee_script_path = OUTPUT_DIR / 'validation_gee_script.js'
    generate_gee_script(sample_df, gee_script_path)

    # Step 7: Sensitivity analysis
    sensitivity_results = sensitivity_analysis(df)

    # Step 8: Check if manual labels already exist
    manual_file = OUTPUT_DIR / 'validation_sample_annotated.csv'
    if manual_file.exists():
        print(f"\n[INFO] Found annotated file: {manual_file}")
        annotated_df = pd.read_csv(manual_file)
        if 'manual_label' in annotated_df.columns and annotated_df['manual_label'].notna().sum() > 0:
            results = compute_agreement_metrics(annotated_df)
            if results:
                results['sensitivity_analysis'] = sensitivity_results
                results_path = OUTPUT_DIR / 'validation_results.json'
                with open(results_path, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"[OK] Validation results saved to: {results_path}")
    else:
        print(f"\n[INFO] Manual annotation not yet done.")
        print(f"[INFO] Steps to complete validation:")
        print(f"  1. Open {sample_csv}")
        print(f"  2. Use the GEE script at {gee_script_path}")
        print(f"  3. For each sample, inspect Sentinel-2 RGB + dNBR")
        print(f"  4. Fill 'manual_label' column: 0=Real fire, 1=Spurious")
        print(f"  5. Save as 'validation_sample_annotated.csv' in same directory")
        print(f"  6. Re-run this script to compute agreement metrics")

    # Save metadata
    metadata = {
        'generation_date': datetime.now().isoformat(),
        'total_labeled_samples': len(df),
        'validation_sample_size': len(sample_df),
        'stratification': {
            'by_label': sample_df[sample_df.columns[sample_df.columns.isin(['label', 'is_reliable'])]].iloc[:, 0].value_counts().to_dict() if any(c in sample_df.columns for c in ['label', 'is_reliable']) else {},
            'by_state': sample_df['state'].value_counts().to_dict() if 'state' in sample_df.columns else {},
            'by_year': sample_df['year'].value_counts().to_dict() if 'year' in sample_df.columns else {},
        },
        'sensitivity_analysis': sensitivity_results,
    }
    metadata_path = OUTPUT_DIR / 'validation_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    print(f"[OK] Metadata saved to: {metadata_path}")


if __name__ == '__main__':
    main()
