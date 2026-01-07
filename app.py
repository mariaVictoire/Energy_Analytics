"""
Application web Flask pour l'analyse du marché de l'électricité.

Permet de :
- Choisir un mois
- Charger un CSV de données de production
- Générer un rapport HTML
- Télécharger le rapport
"""

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import sys
import json

# Ajouter le dossier scripts au path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from load_data import load_market_data
from normalize_data import normalize_market_data, normalize_production_data
from merge_data import merge_market_production
from compute_metrics import compute_all_metrics
from generate_report import generate_html_report, create_charts

app = Flask(__name__)
app.secret_key = 'energy_analytics_secret_key_2024'  # Changez cela en production
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Créer les dossiers nécessaires
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
reports_dir = Path(__file__).parent / 'reports'
reports_dir.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_available_months():
    """
    Récupère les mois disponibles dans les données de marché.
    """
    try:
        market_df = load_market_data()
        market_norm = normalize_market_data(market_df)
        market_norm['year_month'] = market_norm['datetime'].dt.to_period('M')
        months = sorted(market_norm['year_month'].unique())
        return [str(m) for m in months]
    except Exception as e:
        print(f"Erreur lors de la récupération des mois: {e}")
        return []


@app.route('/')
def index():
    """Page d'accueil avec le formulaire."""
    months = get_available_months()
    return render_template('index.html', months=months)


@app.route('/analyze', methods=['POST'])
def analyze():
    """Traite l'analyse et génère le rapport."""
    try:
        # Vérifier que le fichier est présent
        if 'production_file' not in request.files:
            flash('Aucun fichier fourni', 'error')
            return redirect(url_for('index'))
        
        file = request.files['production_file']
        selected_month = request.form.get('month')
        
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(url_for('index'))
        
        if not selected_month:
            flash('Aucun mois sélectionné', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('Format de fichier non autorisé. Utilisez un fichier CSV.', 'error')
            return redirect(url_for('index'))
        
        # Sauvegarder le fichier uploadé
        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(str(filepath))
        
        # Charger et normaliser les données de marché
        market_df = load_market_data()
        market_norm = normalize_market_data(market_df)
        
        # Filtrer par mois sélectionné
        market_norm['year_month'] = market_norm['datetime'].dt.to_period('M')
        market_filtered = market_norm[market_norm['year_month'].astype(str) == selected_month].copy()
        
        if len(market_filtered) == 0:
            flash(f'Aucune donnee de marche trouvee pour le mois {selected_month}', 'error')
            return redirect(url_for('index'))
        
        # Retirer la colonne year_month qui n'est plus nécessaire
        market_filtered = market_filtered[['datetime', 'price_eur_mwh']].copy()
        
        # Charger et normaliser les données de production
        production_df = pd.read_csv(filepath)
        production_norm = normalize_production_data(production_df)
        
        if len(production_norm) == 0:
            flash('Le fichier de production est vide ou invalide', 'error')
            return redirect(url_for('index'))
        
        # Vérifier que les dates de production correspondent au mois sélectionné
        production_norm['year_month'] = production_norm['datetime'].dt.to_period('M')
        production_months = production_norm['year_month'].unique()
        production_months_str = [str(m) for m in production_months]
        
        # Filtrer les données de production pour ne garder que le mois sélectionné
        production_filtered = production_norm[
            production_norm['year_month'].astype(str) == selected_month
        ].copy()
        
        # Vérifier si des données existent pour le mois sélectionné
        if len(production_filtered) == 0:
            months_list = ', '.join(sorted(production_months_str))
            flash(
                f'Les donnees de production ne correspondent pas au mois selectionne ({selected_month}). '
                f'Mois trouves dans le fichier: {months_list}. '
                f'Veuillez charger un fichier avec des donnees pour le mois {selected_month}.',
                'error'
            )
            filepath.unlink()  # Nettoyer le fichier uploadé
            return redirect(url_for('index'))
        
        # Garder seulement les colonnes nécessaires
        production_filtered = production_filtered[['datetime', 'production_mwh']].copy()
        
        # Fusionner les données
        merged_df = merge_market_production(market_filtered, production_filtered)
        
        # Calculer les métriques
        metrics_df, monthly_df = compute_all_metrics(merged_df)
        
        # Période analysée (pour sauvegarder dans JSON)
        start_date = metrics_df['datetime'].min()
        end_date = metrics_df['datetime'].max()
        
        # Générer le rapport HTML
        report_filename = f"report_{selected_month.replace('-', '_')}.html"
        report_path = reports_dir / report_filename
        
        # Créer les graphiques
        charts = create_charts(metrics_df, reports_dir)
        
        # Générer le rapport HTML avec l'URL de base
        generate_html_report(metrics_df, monthly_df, output_path=report_path, base_url=request.host_url.rstrip('/'))
        
        # Sauvegarder les charts en JSON pour la page dynamique
        charts_data = {
            'month': selected_month,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'charts': charts
        }
        charts_json_path = reports_dir / f"charts_{selected_month.replace('-', '_')}.json"
        with open(charts_json_path, 'w', encoding='utf-8') as f:
            json.dump(charts_data, f)
        
        # Nettoyer le fichier uploadé
        filepath.unlink()
        
        # Retourner directement le fichier HTML pour téléchargement
        return send_file(
            str(report_path),
            as_attachment=True,
            download_name=report_filename,
            mimetype='text/html'
        )
        
    except Exception as e:
        flash(f'Erreur lors de l\'analyse: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('index'))


@app.route('/download/<filename>')
def download(filename):
    """Télécharge le rapport HTML généré."""
    try:
        filepath = reports_dir / filename
        if not filepath.exists():
            flash('Fichier non trouvé', 'error')
            return redirect(url_for('index'))
        
        return send_file(
            str(filepath),
            as_attachment=True,
            download_name=filename,
            mimetype='text/html'
        )
    except Exception as e:
        flash(f'Erreur lors du téléchargement: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/visualizations/<month>')
def visualizations(month):
    """Affiche la page de visualisations dynamique avec onglets pour un mois donné."""
    try:
        # Charger les données des graphiques depuis le JSON
        charts_json_path = reports_dir / f"charts_{month.replace('-', '_')}.json"
        
        if not charts_json_path.exists():
            flash(f'Visualisations non disponibles pour le mois {month}', 'error')
            return redirect(url_for('index'))
        
        with open(charts_json_path, 'r', encoding='utf-8') as f:
            charts_data = json.load(f)
        
        # Rendre le template avec les données
        return render_template('visualizations.html', 
                             month=month,
                             start_date=charts_data['start_date'],
                             end_date=charts_data['end_date'],
                             charts=charts_data['charts'])
    except Exception as e:
        flash(f'Erreur lors du chargement des visualisations: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    print("=" * 60)
    print("APPLICATION WEB ENERGY ANALYTICS")
    print("=" * 60)
    print(f"Interface disponible sur: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

