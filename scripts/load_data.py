"""
Script pour charger les données de marché et de production depuis les CSV.

Ce module charge les fichiers CSV et retourne des DataFrames pandas
prêts pour le traitement.
"""

import pandas as pd
from pathlib import Path


def load_market_data(csv_path=None):
    """
    Charge les données de prix spot du marché.
    
    Args:
        csv_path: Chemin vers le fichier CSV. Si None, utilise le chemin par défaut.
    
    Returns:
        DataFrame avec les colonnes: start_date, end_date, price
    """
    if csv_path is None:
        csv_path = Path(__file__).parent.parent / "data" / "market" / "spot_prices.csv"
    
    print(f"Chargement des données marché depuis {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"  [OK] {len(df)} lignes chargees")
        print(f"  [OK] Colonnes: {list(df.columns)}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier non trouvé: {csv_path}")
    except Exception as e:
        raise Exception(f"Erreur lors du chargement: {e}")


def load_production_data(csv_path=None):
    """
    Charge les données de production du client.
    
    Args:
        csv_path: Chemin vers le fichier CSV. Si None, utilise le chemin par défaut.
    
    Returns:
        DataFrame avec les colonnes: date, production (ou datetime, production_mwh)
    """
    if csv_path is None:
        csv_path = Path(__file__).parent.parent / "data" / "client" / "production.csv"
    
    print(f"Chargement des données production depuis {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
        
        # Vérifier si le fichier est vide (seulement l'en-tête)
        if len(df) == 0:
            print("  [WARN] Fichier vide ou seulement l'en-tete")
            return df
        
        print(f"  [OK] {len(df)} lignes chargees")
        print(f"  [OK] Colonnes: {list(df.columns)}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier non trouvé: {csv_path}")
    except Exception as e:
        raise Exception(f"Erreur lors du chargement: {e}")


if __name__ == "__main__":
    # Test du chargement
    print("=== Test de chargement des données ===\n")
    
    market_df = load_market_data()
    print(f"\nAperçu données marché:\n{market_df.head()}\n")
    
    production_df = load_production_data()
    print(f"\nAperçu données production:\n{production_df.head()}\n")

