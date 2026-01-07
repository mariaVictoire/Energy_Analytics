"""
Script pour filtrer les données et ne garder qu'un mois complet avec toutes les heures.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime


def find_complete_month(df):
    """
    Trouve un mois complet dans les données.
    Retourne le mois et l'année du premier mois complet trouvé.
    """
    if 'start_date_parsed' not in df.columns:
        df['start_date_parsed'] = pd.to_datetime(df['start_date'], utc=True)
    df['year_month'] = df['start_date_parsed'].dt.to_period('M')
    
    # Compter les heures par mois
    month_counts = {}
    for period in df['year_month'].unique():
        month_data = df[df['year_month'] == period]
        # Extraire l'heure de start_date
        month_data = month_data.copy()
        month_data['hour'] = month_data['start_date_parsed'].dt.hour
        unique_hours = month_data['hour'].nunique()
        unique_days = month_data['start_date_parsed'].dt.date.nunique()
        
        # Vérifier si c'est un mois complet (31 jours max, 24 heures)
        # On accepte un mois avec au moins 28 jours et 24 heures uniques
        if unique_days >= 28 and unique_hours == 24:
            month_counts[period] = {
                'days': unique_days,
                'hours': unique_hours,
                'total_records': len(month_data)
            }
    
    if month_counts:
        # Prendre le premier mois complet trouvé
        best_month = max(month_counts.items(), key=lambda x: x[1]['days'])
        return best_month[0]
    
    return None


def filter_month_data(input_file, output_file=None):
    """
    Filtre les données pour ne garder qu'un mois complet avec toutes les heures.
    """
    input_path = Path(input_file)
    if output_file is None:
        output_file = input_file
    
    print(f"Lecture du fichier {input_path}...")
    df = pd.read_csv(input_path)
    
    print(f"Nombre total de lignes: {len(df)}")
    
    # Garder les dates originales pour l'export
    df_original = df.copy()
    
    # Convertir les dates pour l'analyse (gérer les timezones)
    df['start_date_parsed'] = pd.to_datetime(df['start_date'], utc=True)
    
    # Trouver un mois complet (utiliser la colonne parsée)
    complete_month = find_complete_month(df)
    
    if complete_month is None:
        print("Aucun mois complet trouvé. Analyse des mois disponibles...")
        # Afficher les statistiques par mois
        df['year_month'] = df['start_date_parsed'].dt.to_period('M')
        for period in sorted(df['year_month'].unique()):
            month_data = df[df['year_month'] == period]
            unique_days = month_data['start_date_parsed'].dt.date.nunique()
            unique_hours = month_data['start_date_parsed'].dt.hour.nunique()
            print(f"  {period}: {unique_days} jours, {unique_hours} heures uniques, {len(month_data)} enregistrements")
        
        # Prendre le mois avec le plus de jours
        month_days = {}
        for period in df['year_month'].unique():
            month_data = df[df['year_month'] == period]
            unique_days = month_data['start_date_parsed'].dt.date.nunique()
            month_days[period] = unique_days
        best_month = max(month_days.items(), key=lambda x: x[1])[0]
        print(f"\nSélection du mois {best_month} (le plus complet disponible)")
        complete_month = best_month
    else:
        print(f"Mois complet trouvé: {complete_month}")
    
    # Filtrer les données du mois
    df['year_month'] = df['start_date_parsed'].dt.to_period('M')
    mask = df['year_month'] == complete_month
    filtered_df = df_original[mask].copy()
    
    # Trier par date (utiliser la date parsée pour le tri)
    df_sorted = df[mask].copy()
    sort_order = df_sorted['start_date_parsed'].argsort()
    filtered_df = filtered_df.iloc[sort_order].reset_index(drop=True)
    
    # Garder seulement les colonnes originales
    filtered_df = filtered_df[['start_date', 'end_date', 'value', 'price']]
    
    print(f"\nDonnées filtrées:")
    print(f"  Mois: {complete_month}")
    print(f"  Nombre de lignes: {len(filtered_df)}")
    
    # Sauvegarder
    output_path = Path(output_file)
    filtered_df.to_csv(output_path, index=False)
    print(f"\nDonnees sauvegardees dans {output_path}")
    
    return filtered_df


if __name__ == "__main__":
    input_file = Path(__file__).parent.parent / "data" / "market" / "spot_prices.csv"
    filter_month_data(input_file)

