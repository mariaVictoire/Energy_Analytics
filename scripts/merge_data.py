"""
Script pour fusionner les données de marché et de production.

Ce module effectue une jointure sur la colonne datetime pour créer
un dataset unifié prêt pour les calculs financiers.
"""

import pandas as pd


def merge_market_production(market_df, production_df):
    """
    Fusionne les données de marché et de production sur la colonne datetime.
    
    Args:
        market_df: DataFrame normalisé avec colonnes datetime, price_eur_mwh
        production_df: DataFrame normalisé avec colonnes datetime, production_mwh
    
    Returns:
        DataFrame fusionné avec toutes les colonnes
    """
    print("Fusion des données marché et production...")
    
    # Vérifier que les DataFrames ne sont pas vides
    if len(market_df) == 0:
        raise ValueError("Le DataFrame marché est vide")
    
    if len(production_df) == 0:
        print("  [WARN] Aucune donnee de production disponible")
        # Créer un DataFrame avec les colonnes attendues mais vide
        merged_df = market_df.copy()
        merged_df['production_mwh'] = 0.0
        return merged_df
    
    # Fusionner sur datetime (inner join pour garder seulement les dates communes)
    merged_df = pd.merge(
        market_df,
        production_df,
        on='datetime',
        how='inner',
        suffixes=('_market', '_prod')
    )
    
    # Si aucun résultat, essayer un left join pour garder toutes les dates marché
    if len(merged_df) == 0:
        print("  [WARN] Aucune correspondance de dates trouvee, utilisation d'un left join")
        merged_df = pd.merge(
            market_df,
            production_df,
            on='datetime',
            how='left',
            suffixes=('_market', '_prod')
        )
        # Remplacer les NaN par 0
        merged_df['production_mwh'] = merged_df['production_mwh'].fillna(0.0)
    
    # Trier par datetime
    merged_df = merged_df.sort_values('datetime').reset_index(drop=True)
    
    print(f"  [OK] {len(merged_df)} lignes fusionnees")
    print(f"  [OK] Colonnes: {list(merged_df.columns)}")
    
    # Statistiques de base
    if 'production_mwh' in merged_df.columns:
        total_prod = merged_df['production_mwh'].sum()
        avg_price = merged_df['price_eur_mwh'].mean()
        print(f"  [OK] Production totale: {total_prod:.2f} MWh")
        print(f"  [OK] Prix moyen: {avg_price:.2f} EUR/MWh")
    
    return merged_df


if __name__ == "__main__":
    # Test de fusion
    from load_data import load_market_data, load_production_data
    from normalize_data import normalize_market_data, normalize_production_data
    
    print("=== Test de fusion ===\n")
    
    market_df = load_market_data()
    market_norm = normalize_market_data(market_df)
    
    production_df = load_production_data()
    production_norm = normalize_production_data(production_df)
    
    merged_df = merge_market_production(market_norm, production_norm)
    print(f"\nAperçu données fusionnées:\n{merged_df.head(10)}\n")
