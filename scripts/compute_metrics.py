"""
Script pour calculer les indicateurs financiers clés.

Ce module calcule :
- Revenu horaire et total
- Pertes liées aux prix négatifs
- Statistiques sur les heures à prix négatif
- Agrégations mensuelles
"""

import pandas as pd
import numpy as np


def compute_hourly_revenue(merged_df):
    """
    Calcule le revenu horaire pour chaque ligne.
    
    Args:
        merged_df: DataFrame fusionné avec datetime, price_eur_mwh, production_mwh
    
    Returns:
        DataFrame avec colonne supplémentaire: revenue_eur
    """
    df = merged_df.copy()
    
    # Revenu horaire = production * prix
    df['revenue_eur'] = df['production_mwh'] * df['price_eur_mwh']
    
    return df


def compute_negative_price_losses(merged_df):
    """
    Calcule les pertes liées aux prix négatifs.
    
    Args:
        merged_df: DataFrame avec colonnes price_eur_mwh, production_mwh
    
    Returns:
        DataFrame avec colonnes supplémentaires:
        - negative_price_loss_eur: perte si prix < 0
        - is_negative_price: booléen indiquant si prix < 0
    """
    df = merged_df.copy()
    
    # Identifier les heures à prix négatif
    df['is_negative_price'] = df['price_eur_mwh'] < 0
    
    # Calculer la perte : production * abs(prix) si prix négatif
    df['negative_price_loss_eur'] = np.where(
        df['is_negative_price'],
        df['production_mwh'] * abs(df['price_eur_mwh']),
        0.0
    )
    
    return df


def compute_monthly_aggregates(merged_df):
    """
    Calcule les agrégations mensuelles.
    
    Args:
        merged_df: DataFrame avec toutes les métriques calculées
    
    Returns:
        DataFrame avec une ligne par mois contenant les agrégations
    """
    df = merged_df.copy()
    
    # Extraire l'année-mois
    df['year_month'] = df['datetime'].dt.to_period('M')
    
    # Agrégations mensuelles
    monthly = df.groupby('year_month').agg({
        'revenue_eur': 'sum',
        'negative_price_loss_eur': 'sum',
        'is_negative_price': 'sum',  # Nombre d'heures à prix négatif
        'production_mwh': 'sum',
        'price_eur_mwh': ['mean', 'min', 'max'],
    }).reset_index()
    
    # Aplatir les noms de colonnes
    monthly.columns = [
        'year_month',
        'total_revenue_eur',
        'total_negative_loss_eur',
        'hours_negative_price',
        'total_production_mwh',
        'avg_price_eur_mwh',
        'min_price_eur_mwh',
        'max_price_eur_mwh'
    ]
    
    # Calculer la production pendant les heures négatives
    negative_hours_prod = df[df['is_negative_price']].groupby('year_month')['production_mwh'].sum().reset_index()
    negative_hours_prod.columns = ['year_month', 'production_during_negative_mwh']
    
    monthly = pd.merge(monthly, negative_hours_prod, on='year_month', how='left')
    monthly['production_during_negative_mwh'] = monthly['production_during_negative_mwh'].fillna(0.0)
    
    # Calculer le pourcentage de perte par rapport au revenu
    monthly['loss_percentage'] = (monthly['total_negative_loss_eur'] / 
                                   monthly['total_revenue_eur'].abs() * 100).fillna(0.0)
    
    return monthly


def compute_all_metrics(merged_df):
    """
    Calcule toutes les métriques en une seule fonction.
    
    Args:
        merged_df: DataFrame fusionné avec datetime, price_eur_mwh, production_mwh
    
    Returns:
        Tuple (merged_df_with_metrics, monthly_aggregates)
    """
    print("Calcul des métriques...")
    
    # Calculer le revenu horaire
    df = compute_hourly_revenue(merged_df)
    
    # Calculer les pertes prix négatifs
    df = compute_negative_price_losses(df)
    
    # Calculer les agrégations mensuelles
    monthly = compute_monthly_aggregates(df)
    
    print(f"  [OK] Revenu total: {df['revenue_eur'].sum():.2f} EUR")
    print(f"  [OK] Pertes prix negatifs: {df['negative_price_loss_eur'].sum():.2f} EUR")
    print(f"  [OK] Heures a prix negatif: {df['is_negative_price'].sum()}")
    
    return df, monthly


if __name__ == "__main__":
    # Test des calculs
    from load_data import load_market_data, load_production_data
    from normalize_data import normalize_market_data, normalize_production_data
    from merge_data import merge_market_production
    
    print("=== Test des calculs de métriques ===\n")
    
    market_df = load_market_data()
    market_norm = normalize_market_data(market_df)
    
    production_df = load_production_data()
    production_norm = normalize_production_data(production_df)
    
    merged_df = merge_market_production(market_norm, production_norm)
    
    # Si pas de production, créer des données de test
    if len(production_norm) == 0:
        print("\n[WARN] Creation de donnees de production de test...")
        merged_df['production_mwh'] = np.random.uniform(10, 50, len(merged_df))
    
    metrics_df, monthly_df = compute_all_metrics(merged_df)
    
    print(f"\nAperçu métriques horaires:\n{metrics_df.head(10)}\n")
    print(f"\nAgrégations mensuelles:\n{monthly_df}\n")
