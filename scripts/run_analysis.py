"""
Script principal pour exécuter l'analyse complète du marché de l'électricité.

Ce script orchestre tout le pipeline :
1. Chargement des données
2. Normalisation
3. Fusion
4. Calcul des métriques
5. Génération du rapport
"""

import sys
from pathlib import Path

# Ajouter le dossier scripts au path pour les imports
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from load_data import load_market_data, load_production_data
from normalize_data import normalize_market_data, normalize_production_data
from merge_data import merge_market_production
from compute_metrics import compute_all_metrics
from generate_report import generate_markdown_report, generate_html_report


def run_full_analysis():
    """
    Exécute l'analyse complète du marché de l'électricité.
    """
    print("=" * 60)
    print("ANALYSE DU MARCHÉ DE L'ÉLECTRICITÉ")
    print("=" * 60)
    print()
    
    try:
        # 1. Chargement des données
        print("ÉTAPE 1: Chargement des données")
        print("-" * 60)
        market_df = load_market_data()
        production_df = load_production_data()
        print()
        
        # 2. Normalisation
        print("ÉTAPE 2: Normalisation des données")
        print("-" * 60)
        market_norm = normalize_market_data(market_df)
        production_norm = normalize_production_data(production_df)
        print()
        
        # 3. Fusion
        print("ÉTAPE 3: Fusion des datasets")
        print("-" * 60)
        merged_df = merge_market_production(market_norm, production_norm)
        print()
        
        # 4. Calcul des métriques
        print("ÉTAPE 4: Calcul des métriques financières")
        print("-" * 60)
        metrics_df, monthly_df = compute_all_metrics(merged_df)
        print()
        
        # 5. Génération du rapport
        print("ÉTAPE 5: Génération du rapport")
        print("-" * 60)
        report_path = generate_markdown_report(metrics_df, monthly_df)
        html_report_path = generate_html_report(metrics_df, monthly_df)
        print()
        
        # Résumé final
        print("=" * 60)
        print("ANALYSE TERMINEE AVEC SUCCES")
        print("=" * 60)
        print(f"Rapport Markdown: {str(report_path)}")
        print(f"Rapport HTML: {str(html_report_path)}")
        print()
        
        return metrics_df, monthly_df, report_path, html_report_path
        
    except Exception as e:
        print()
        print("=" * 60)
        print("ERREUR LORS DE L'ANALYSE")
        print("=" * 60)
        print(f"Erreur: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_full_analysis()

