"""
Script pour mettre à jour automatiquement les données de marché spot.
Télécharge les dernières données depuis le dépôt GitHub.
"""

import urllib.request
import os
from pathlib import Path


def update_market_data():
    """
    Télécharge et met à jour le fichier spot_prices.csv avec les dernières données.
    """
    url = "https://raw.githubusercontent.com/mariaVictoire/ElectricityMarket/refs/heads/main/data/marche_spot.csv"
    output_path = Path(__file__).parent.parent / "data" / "market" / "spot_prices.csv"
    
    try:
        print(f"Téléchargement des données depuis {url}...")
        urllib.request.urlretrieve(url, output_path)
        print(f"✓ Données mises à jour avec succès dans {output_path}")
        
        # Afficher le nombre de lignes
        with open(output_path, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        print(f"  Nombre de lignes: {line_count}")
        
    except Exception as e:
        print(f"✗ Erreur lors de la mise à jour: {e}")
        return False
    
    return True


if __name__ == "__main__":
    update_market_data()

