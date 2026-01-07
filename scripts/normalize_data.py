"""
Script pour normaliser les formats de dates et colonnes.

Ce module standardise les données pour faciliter la fusion :
- Convertit les dates en datetime
- Renomme les colonnes pour avoir un format cohérent
- Extrait l'heure de début pour la jointure
"""

import pandas as pd
from datetime import datetime


def normalize_market_data(df):
    """
    Normalise les données de marché.
    
    Args:
        df: DataFrame avec colonnes start_date, end_date, price
    
    Returns:
        DataFrame normalisé avec colonnes: datetime, price_eur_mwh
    """
    print("Normalisation des données marché...")
    
    df = df.copy()
    
    # Convertir start_date en datetime (gérer les timezones)
    df['datetime'] = pd.to_datetime(df['start_date'], utc=True)
    
    # Renommer price en price_eur_mwh pour clarté
    df['price_eur_mwh'] = df['price']
    
    # Garder seulement les colonnes nécessaires
    df_normalized = df[['datetime', 'price_eur_mwh']].copy()
    
    # Trier par datetime
    df_normalized = df_normalized.sort_values('datetime').reset_index(drop=True)
    
    print(f"  [OK] {len(df_normalized)} lignes normalisees")
    print(f"  [OK] Periode: {df_normalized['datetime'].min()} a {df_normalized['datetime'].max()}")
    
    return df_normalized


def normalize_production_data(df):
    """
    Normalise les données de production.
    
    Args:
        df: DataFrame avec colonnes date/production ou datetime/production_mwh
    
    Returns:
        DataFrame normalisé avec colonnes: datetime, production_mwh
    """
    print("Normalisation des données production...")
    
    if len(df) == 0:
        print("  [WARN] Aucune donnee a normaliser")
        return pd.DataFrame(columns=['datetime', 'production_mwh'])
    
    df = df.copy()
    
    # Détecter le nom de la colonne de date
    date_col = None
    for col in ['datetime', 'date', 'start_date', 'timestamp']:
        if col in df.columns:
            date_col = col
            break
    
    if date_col is None:
        raise ValueError("Colonne de date non trouvée. Colonnes disponibles: " + str(list(df.columns)))
    
    # Détecter le nom de la colonne de production
    prod_col = None
    for col in ['production_mwh', 'production', 'value', 'power']:
        if col in df.columns:
            prod_col = col
            break
    
    if prod_col is None:
        raise ValueError("Colonne de production non trouvée. Colonnes disponibles: " + str(list(df.columns)))
    
    # Convertir la date en datetime
    df['datetime'] = pd.to_datetime(df[date_col], utc=True)
    
    # Renommer la production
    df['production_mwh'] = pd.to_numeric(df[prod_col], errors='coerce')
    
    # Garder seulement les colonnes nécessaires
    df_normalized = df[['datetime', 'production_mwh']].copy()
    
    # Supprimer les lignes avec production NaN
    df_normalized = df_normalized.dropna(subset=['production_mwh'])
    
    # Trier par datetime
    df_normalized = df_normalized.sort_values('datetime').reset_index(drop=True)
    
    print(f"  [OK] {len(df_normalized)} lignes normalisees")
    if len(df_normalized) > 0:
        print(f"  [OK] Periode: {df_normalized['datetime'].min()} a {df_normalized['datetime'].max()}")
    
    return df_normalized


if __name__ == "__main__":
    # Test de normalisation
    from load_data import load_market_data, load_production_data
    
    print("=== Test de normalisation ===\n")
    
    market_df = load_market_data()
    market_norm = normalize_market_data(market_df)
    print(f"\nAperçu marché normalisé:\n{market_norm.head()}\n")
    
    production_df = load_production_data()
    production_norm = normalize_production_data(production_df)
    print(f"\nAperçu production normalisé:\n{production_norm.head()}\n")

