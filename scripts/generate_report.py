"""
Script pour générer le rapport mensuel d'analyse énergétique en Markdown et HTML.

Ce module crée un rapport structuré avec :
- Résumé exécutif
- Chiffres clés
- Analyse des pertes
- Heures critiques
- Recommandations
- Graphiques et visualisations (version HTML)
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import base64
import io
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend non-interactif
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def format_currency(amount):
    """Formate un montant en euros avec séparateurs."""
    return f"{amount:,.2f} €".replace(",", " ")


def format_mwh(amount):
    """Formate une quantité en MWh."""
    return f"{amount:,.2f} MWh".replace(",", " ")


def get_critical_hours(metrics_df, n=10):
    """
    Récupère les heures les plus critiques (prix négatifs avec production).
    
    Args:
        metrics_df: DataFrame avec toutes les métriques
        n: Nombre d'heures à retourner
    
    Returns:
        DataFrame avec les n heures les plus critiques
    """
    # Filtrer les heures à prix négatif avec production
    negative_hours = metrics_df[
        (metrics_df['is_negative_price']) & 
        (metrics_df['production_mwh'] > 0)
    ].copy()
    
    if len(negative_hours) == 0:
        return pd.DataFrame()
    
    # Trier par perte décroissante
    negative_hours = negative_hours.sort_values('negative_price_loss_eur', ascending=False)
    
    # Garder seulement les colonnes pertinentes
    critical = negative_hours[['datetime', 'price_eur_mwh', 'production_mwh', 'negative_price_loss_eur']].head(n)
    
    return critical


def generate_markdown_report(metrics_df, monthly_df, output_path=None):
    """
    Génère un rapport Markdown complet.
    
    Args:
        metrics_df: DataFrame avec toutes les métriques horaires
        monthly_df: DataFrame avec les agrégations mensuelles
        output_path: Chemin de sortie. Si None, utilise le chemin par défaut.
    
    Returns:
        String contenant le rapport Markdown
    """
    if output_path is None:
        output_path = Path(__file__).parent.parent / "reports" / "monthly_report.md"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculer les totaux globaux
    total_revenue = metrics_df['revenue_eur'].sum()
    total_loss = metrics_df['negative_price_loss_eur'].sum()
    total_production = metrics_df['production_mwh'].sum()
    hours_negative = metrics_df['is_negative_price'].sum()
    total_hours = len(metrics_df)
    
    # Prix moyens et extrêmes
    avg_price = metrics_df['price_eur_mwh'].mean()
    min_price = metrics_df['price_eur_mwh'].min()
    max_price = metrics_df['price_eur_mwh'].max()
    
    # Production pendant heures négatives
    prod_during_negative = metrics_df[metrics_df['is_negative_price']]['production_mwh'].sum()
    
    # Période analysée
    start_date = metrics_df['datetime'].min()
    end_date = metrics_df['datetime'].max()
    
    # Heures critiques
    critical_hours = get_critical_hours(metrics_df, n=10)
    
    # Construire le rapport
    report = []
    
    # En-tête
    report.append("# Rapport d'Analyse Énergétique")
    report.append("")
    report.append(f"**Période analysée:** {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}")
    report.append(f"**Date de génération:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report.append("")
    report.append("---")
    report.append("")
    
    # Résumé exécutif
    report.append("## Résumé Exécutif")
    report.append("")
    report.append("Ce rapport présente l'analyse financière de la production d'énergie renouvelable")
    report.append("sur le marché spot de l'électricité. Les indicateurs clés incluent les revenus générés,")
    report.append("les pertes liées aux prix négatifs, et les opportunités d'optimisation.")
    report.append("")
    
    # Chiffres clés
    report.append("## Chiffres Clés")
    report.append("")
    report.append("| Indicateur | Valeur |")
    report.append("|------------|--------|")
    report.append(f"| **Revenu total** | {format_currency(total_revenue)} |")
    report.append(f"| **Production totale** | {format_mwh(total_production)} |")
    report.append(f"| **Prix moyen** | {format_currency(avg_price)} / MWh |")
    report.append(f"| **Prix minimum** | {format_currency(min_price)} / MWh |")
    report.append(f"| **Prix maximum** | {format_currency(max_price)} / MWh |")
    report.append(f"| **Pertes prix négatifs** | {format_currency(total_loss)} |")
    report.append(f"| **Heures à prix négatif** | {hours_negative} / {total_hours} ({hours_negative/total_hours*100:.1f}%) |")
    report.append(f"| **Production pendant prix négatifs** | {format_mwh(prod_during_negative)} |")
    report.append("")
    
    # Analyse mensuelle
    if len(monthly_df) > 0:
        report.append("## Analyse Mensuelle")
        report.append("")
        report.append("| Mois | Revenu | Pertes | Production | Prix moyen | Heures nég. |")
        report.append("|------|--------|--------|------------|------------|-------------|")
        
        for _, row in monthly_df.iterrows():
            month_str = str(row['year_month'])
            report.append(
                f"| {month_str} | {format_currency(row['total_revenue_eur'])} | "
                f"{format_currency(row['total_negative_loss_eur'])} | "
                f"{format_mwh(row['total_production_mwh'])} | "
                f"{format_currency(row['avg_price_eur_mwh'])} | "
                f"{int(row['hours_negative_price'])} |"
            )
        report.append("")
    
    # Analyse des pertes
    report.append("## Analyse des Pertes")
    report.append("")
    
    if total_loss > 0:
        loss_percentage = (total_loss / abs(total_revenue)) * 100 if total_revenue != 0 else 0
        report.append(f"Les pertes liées aux prix négatifs représentent **{format_currency(total_loss)}**")
        report.append(f"soit **{loss_percentage:.2f}%** du revenu total.")
        report.append("")
        report.append("Ces pertes surviennent lorsque le marché de l'électricité affiche des prix négatifs,")
        report.append("c'est-à-dire que les producteurs doivent payer pour injecter de l'électricité sur le réseau.")
        report.append("Cela se produit généralement lors de périodes de forte production renouvelable")
        report.append("et de faible demande.")
        report.append("")
    else:
        report.append("Aucune perte liée aux prix négatifs n'a été enregistrée sur cette période.")
        report.append("")
    
    # Heures critiques
    report.append("## Heures Critiques")
    report.append("")
    
    if len(critical_hours) > 0:
        report.append("Les heures suivantes présentent les pertes les plus importantes")
        report.append("(prix négatifs avec production) :")
        report.append("")
        report.append("| Date et heure | Prix (€/MWh) | Production (MWh) | Perte (€) |")
        report.append("|---------------|-------------|------------------|-----------|")
        
        for _, row in critical_hours.iterrows():
            dt_str = row['datetime'].strftime('%d/%m/%Y %H:%M')
            report.append(
                f"| {dt_str} | {format_currency(row['price_eur_mwh'])} | "
                f"{format_mwh(row['production_mwh'])} | "
                f"{format_currency(row['negative_price_loss_eur'])} |"
            )
        report.append("")
    else:
        report.append("Aucune heure critique identifiée (pas de prix négatifs avec production).")
        report.append("")
    
    # Recommandations
    report.append("## Recommandations")
    report.append("")
    report.append("### Optimisation de la production")
    report.append("")
    report.append("- **Surveillance des prix spot** : Mettre en place un système d'alerte")
    report.append("  pour les périodes de prix négatifs afin de réduire la production si possible.")
    report.append("")
    report.append("- **Stockage d'énergie** : Envisager l'investissement dans des solutions")
    report.append("  de stockage (batteries) pour décaler la production vers des heures plus rentables.")
    report.append("")
    report.append("- **Contrats de long terme** : Diversifier les revenus avec des contrats")
    report.append("  d'achat d'électricité (PPA) pour réduire l'exposition aux prix spot négatifs.")
    report.append("")
    report.append("### Analyse continue")
    report.append("")
    report.append("- Suivre l'évolution mensuelle des pertes pour identifier des tendances.")
    report.append("- Analyser les corrélations entre conditions météorologiques et prix négatifs.")
    report.append("- Comparer les performances avec d'autres producteurs du secteur.")
    report.append("")
    
    # Footer
    report.append("---")
    report.append("")
    report.append("*Rapport généré automatiquement par le système d'analyse énergétique*")
    report.append("")
    
    # Joindre toutes les lignes
    report_text = "\n".join(report)
    
    # Sauvegarder
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"Rapport généré: {output_path}")
    
    return report_text


def create_charts(metrics_df, output_dir):
    """
    Crée des graphiques et retourne leurs encodages base64.
    
    Args:
        metrics_df: DataFrame avec toutes les métriques
        output_dir: Répertoire pour sauvegarder les images
    
    Returns:
        Dict avec les encodages base64 des graphiques
    """
    if not HAS_MATPLOTLIB:
        return {}
    
    charts = {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Style moderne
    plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
    
    # 1. Graphique des prix au fil du temps
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(metrics_df['datetime'], metrics_df['price_eur_mwh'], 
            linewidth=0.8, alpha=0.7, color='#5a9fd4')
    ax.axhline(y=0, color='#e88a8a', linestyle='--', linewidth=1, alpha=0.6, label='Prix zéro')
    ax.fill_between(metrics_df['datetime'], 0, metrics_df['price_eur_mwh'], 
                     where=(metrics_df['price_eur_mwh'] < 0), 
                     color='#f5a5a5', alpha=0.3, label='Prix négatifs')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Prix (€/MWh)', fontsize=12)
    ax.set_title('Évolution des Prix Spot', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Sauvegarder en base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    charts['price_evolution'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # 2. Graphique de production au fil du temps
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(metrics_df['datetime'], metrics_df['production_mwh'], 
            linewidth=1, color='#7bc8a4', alpha=0.7)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Production (MWh)', fontsize=12)
    ax.set_title('Évolution de la Production', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    charts['production_evolution'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # 3. Graphique des revenus horaires
    fig, ax = plt.subplots(figsize=(14, 6))
    colors = ['#f5a5a5' if x < 0 else '#7bc8a4' for x in metrics_df['revenue_eur']]
    ax.bar(range(len(metrics_df)), metrics_df['revenue_eur'], 
           color=colors, alpha=0.7, width=1)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Heure', fontsize=12)
    ax.set_ylabel('Revenu (€)', fontsize=12)
    ax.set_title('Revenus Horaires', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    charts['revenue_hourly'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # 4. Distribution des prix
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(metrics_df['price_eur_mwh'], bins=50, color='#5a9fd4', alpha=0.7, edgecolor='#b8d4e8')
    ax.axvline(x=0, color='#e88a8a', linestyle='--', linewidth=2, label='Prix zéro')
    ax.set_xlabel('Prix (€/MWh)', fontsize=12)
    ax.set_ylabel('Fréquence', fontsize=12)
    ax.set_title('Distribution des Prix Spot', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    charts['price_distribution'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # 5. Graphique en camembert : Heures à prix positif vs négatif
    positive_hours = (metrics_df['price_eur_mwh'] >= 0).sum()
    negative_hours = (metrics_df['price_eur_mwh'] < 0).sum()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    sizes = [positive_hours, negative_hours]
    labels = ['Prix Positifs', 'Prix Négatifs']
    colors_pie = ['#7bc8a4', '#f5a5a5']
    explode = (0, 0.1) if negative_hours > 0 else (0, 0)
    
    ax.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
           autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 12})
    ax.set_title('Répartition des Heures\n(Prix Positifs vs Négatifs)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    charts['price_pie'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return charts


def generate_visualizations_page(metrics_df, monthly_df, charts, month, output_path=None):
    """
    Génère une page HTML avec onglets dynamiques pour les visualisations.
    
    Args:
        metrics_df: DataFrame avec toutes les métriques horaires
        monthly_df: DataFrame avec les agrégations mensuelles
        charts: Dict avec les encodages base64 des graphiques
        month: Mois analysé (format YYYY-MM)
        output_path: Chemin de sortie. Si None, utilise le chemin par défaut.
    
    Returns:
        String contenant le HTML de la page de visualisations
    """
    if output_path is None:
        output_path = Path(__file__).parent.parent / "reports" / f"visualizations_{month.replace('-', '_')}.html"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Période analysée
    start_date = metrics_df['datetime'].min()
    end_date = metrics_df['datetime'].max()
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualisations - {month}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #e0e6ed;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #5a9fd4 0%, #4a8bc2 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            font-size: 1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .tabs {{
            display: flex;
            border-bottom: 2px solid #e0e6ed;
            margin-bottom: 30px;
            overflow-x: auto;
        }}
        
        .tab-button {{
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            color: #6b8a9a;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        
        .tab-button:hover {{
            color: #2c5f7c;
            background: #f8fafb;
        }}
        
        .tab-button.active {{
            color: #2c5f7c;
            border-bottom-color: #5a9fd4;
            background: #f8fafb;
        }}
        
        .tab-content {{
            display: none;
            animation: fadeIn 0.3s;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .chart-wrapper {{
            text-align: center;
            background: linear-gradient(135deg, #f8fafb 0%, #f0f4f7 100%);
            padding: 30px;
            border-radius: 8px;
            border: 1px solid #e0e6ed;
            margin-bottom: 20px;
        }}
        
        .chart-wrapper h3 {{
            color: #2c5f7c;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        
        .chart-wrapper img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #5a9fd4;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}
        
        .back-link:hover {{
            color: #4a8bc2;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Visualisations - {month}</h1>
            <div class="meta">
                <p>Période: {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}</p>
            </div>
        </div>
        
        <div class="content">
            <a href="javascript:history.back()" class="back-link">← Retour</a>
            
            <div class="tabs">
"""
    
    # Créer les onglets
    tab_data = [
        ('price_evolution', 'Évolution des Prix', 'Évolution des Prix Spot'),
        ('production_evolution', 'Évolution Production', 'Évolution de la Production'),
        ('revenue_hourly', 'Revenus Horaires', 'Revenus Horaires'),
        ('price_distribution', 'Distribution Prix', 'Distribution des Prix Spot'),
        ('price_pie', 'Répartition', 'Répartition des Heures (Prix Positifs vs Négatifs)')
    ]
    
    for i, (chart_key, tab_label, chart_title) in enumerate(tab_data):
        active_class = 'active' if i == 0 else ''
        html += f'                <button class="tab-button {active_class}" onclick="showTab(\'{chart_key}\')">{tab_label}</button>\n'
    
    html += """            </div>
"""
    
    # Créer le contenu des onglets
    for i, (chart_key, tab_label, chart_title) in enumerate(tab_data):
        active_class = 'active' if i == 0 else ''
        if chart_key in charts:
            html += f"""
            <div id="tab-{chart_key}" class="tab-content {active_class}">
                <div class="chart-wrapper">
                    <h3>{chart_title}</h3>
                    <img src="data:image/png;base64,{charts[chart_key]}" alt="{chart_title}">
                </div>
            </div>
"""
        else:
            html += f"""
            <div id="tab-{chart_key}" class="tab-content {active_class}">
                <div class="chart-wrapper">
                    <p>Graphique non disponible</p>
                </div>
            </div>
"""
    
    html += """        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            // Masquer tous les contenus d'onglets
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => {
                content.classList.remove('active');
            });
            
            // Désactiver tous les boutons
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(button => {
                button.classList.remove('active');
            });
            
            // Afficher l'onglet sélectionné
            document.getElementById('tab-' + tabName).classList.add('active');
            
            // Activer le bouton correspondant
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""
    
    # Sauvegarder
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Page de visualisations generee: {output_path}")
    
    return html


def generate_html_report(metrics_df, monthly_df, output_path=None, base_url="http://localhost:5000"):
    """
    Génère un rapport HTML complet avec graphiques et mise en forme moderne.
    
    Args:
        metrics_df: DataFrame avec toutes les métriques horaires
        monthly_df: DataFrame avec les agrégations mensuelles
        output_path: Chemin de sortie. Si None, utilise le chemin par défaut.
        base_url: URL de base du serveur Flask pour les liens (défaut: http://localhost:5000)
    
    Returns:
        String contenant le rapport HTML
    """
    if output_path is None:
        output_path = Path(__file__).parent.parent / "reports" / "monthly_report.html"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculer les totaux globaux
    total_revenue = metrics_df['revenue_eur'].sum()
    total_loss = metrics_df['negative_price_loss_eur'].sum()
    total_production = metrics_df['production_mwh'].sum()
    hours_negative = metrics_df['is_negative_price'].sum()
    total_hours = len(metrics_df)
    
    # Prix moyens et extrêmes
    avg_price = metrics_df['price_eur_mwh'].mean()
    min_price = metrics_df['price_eur_mwh'].min()
    max_price = metrics_df['price_eur_mwh'].max()
    
    # Production pendant heures négatives
    prod_during_negative = metrics_df[metrics_df['is_negative_price']]['production_mwh'].sum()
    
    # Période analysée
    start_date = metrics_df['datetime'].min()
    end_date = metrics_df['datetime'].max()
    
    # Heures critiques
    critical_hours = get_critical_hours(metrics_df, n=10)
    
    # Créer les graphiques
    charts = create_charts(metrics_df, output_path.parent)
    
    # Calculer le pourcentage de perte
    loss_percentage = (total_loss / abs(total_revenue)) * 100 if total_revenue != 0 else 0
    
    # HTML avec CSS moderne
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Analyse Énergétique</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #e0e6ed;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #5a9fd4 0%, #4a8bc2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .meta {{
            font-size: 1.1em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section h2 {{
            color: #2c5f7c;
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #7bb3d9;
        }}
        
        .section h3 {{
            color: #4a8bc2;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .kpi-card {{
            background: linear-gradient(135deg, #5a9fd4 0%, #4a8bc2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(90, 159, 212, 0.2);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(90, 159, 212, 0.3);
        }}
        
        .kpi-card.negative {{
            background: linear-gradient(135deg, #f5a5a5 0%, #e88a8a 100%);
        }}
        
        .kpi-card.positive {{
            background: linear-gradient(135deg, #7bc8a4 0%, #6ab894 100%);
        }}
        
        .kpi-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .kpi-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: linear-gradient(135deg, #5a9fd4 0%, #4a8bc2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .chart-container {{
            margin: 30px 0;
            text-align: center;
            background: linear-gradient(135deg, #f8fafb 0%, #f0f4f7 100%);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e6ed;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        
        .recommendations {{
            background: linear-gradient(135deg, #f8fafb 0%, #f0f4f7 100%);
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid #7bb3d9;
            margin: 20px 0;
            border: 1px solid #e0e6ed;
        }}
        
        .recommendations ul {{
            margin-left: 20px;
            margin-top: 10px;
        }}
        
        .recommendations li {{
            margin: 10px 0;
        }}
        
        .footer {{
            background: #f8fafb;
            padding: 20px;
            text-align: center;
            color: #6b8a9a;
            font-size: 0.9em;
            border-top: 1px solid #e0e6ed;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .badge.success {{
            background: #4facfe;
            color: white;
        }}
        
        .badge.warning {{
            background: #f5576c;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Rapport d'Analyse Énergétique</h1>
            <div class="meta">
                <p><strong>Période analysée:</strong> {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}</p>
                <p><strong>Date de génération:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Résumé Exécutif</h2>
                <p style="font-size: 1.1em; line-height: 1.8;">
                    Ce rapport présente l'analyse financière de la production d'énergie renouvelable
                    sur le marché spot de l'électricité. Les indicateurs clés incluent les revenus générés,
                    les pertes liées aux prix négatifs, et les opportunités d'optimisation.
                </p>
            </div>
            
            <div class="section">
                <h2>💰 Chiffres Clés</h2>
                <div class="kpi-grid">
                    <div class="kpi-card positive">
                        <div class="kpi-label">Revenu Total</div>
                        <div class="kpi-value">{format_currency(total_revenue)}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Production Totale</div>
                        <div class="kpi-value">{format_mwh(total_production)}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Prix Moyen</div>
                        <div class="kpi-value">{format_currency(avg_price)}</div>
                    </div>
                    <div class="kpi-card negative">
                        <div class="kpi-label">Pertes Prix Négatifs</div>
                        <div class="kpi-value">{format_currency(total_loss)}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Prix Minimum</div>
                        <div class="kpi-value">{format_currency(min_price)}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Prix Maximum</div>
                        <div class="kpi-value">{format_currency(max_price)}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Heures à Prix Négatif</div>
                        <div class="kpi-value">{hours_negative} / {total_hours}</div>
                        <div style="margin-top: 10px; font-size: 0.8em;">({hours_negative/total_hours*100:.1f}%)</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Production Pendant Prix Négatifs</div>
                        <div class="kpi-value">{format_mwh(prod_during_negative)}</div>
                    </div>
                </div>
            </div>
"""
    
    # Ajouter les visualisations directement dans le rapport avec onglets
    if charts:
        html += """
            <div class="section">
                <h2>📈 Visualisations</h2>
                <div style="margin: 20px 0;">
                    <div class="tabs" style="display: flex; border-bottom: 2px solid #e0e6ed; margin-bottom: 20px; overflow-x: auto;">
"""
        # Créer les onglets
        tab_data = [
            ('price_evolution', 'Évolution des Prix', 'Évolution des Prix Spot'),
            ('production_evolution', 'Évolution Production', 'Évolution de la Production'),
            ('revenue_hourly', 'Revenus Horaires', 'Revenus Horaires'),
            ('price_distribution', 'Distribution Prix', 'Distribution des Prix Spot'),
            ('price_pie', 'Répartition', 'Répartition des Heures (Prix Positifs vs Négatifs)')
        ]
        
        for i, (chart_key, tab_label, _) in enumerate(tab_data):
            active_class = 'active' if i == 0 else ''
            html += f"""
                        <button class="tab-btn" onclick="showChartTab('{chart_key}')" id="btn-{chart_key}" style="padding: 12px 24px; background: none; border: none; cursor: pointer; font-size: 1em; font-weight: 500; color: {'#2c5f7c' if i == 0 else '#6b8a9a'}; border-bottom: 3px solid {'#5a9fd4' if i == 0 else 'transparent'}; transition: all 0.2s; white-space: nowrap; {'background: #f8fafb;' if i == 0 else ''}">
                            {tab_label}
                        </button>
"""
        
        html += """
                    </div>
"""
        
        # Créer le contenu des onglets
        for i, (chart_key, _, chart_title) in enumerate(tab_data):
            active_class = 'active' if i == 0 else ''
            if chart_key in charts:
                html += f"""
                    <div id="chart-{chart_key}" class="chart-tab-content" style="display: {'block' if i == 0 else 'none'}; animation: fadeIn 0.3s;">
                        <div class="chart-container">
                            <h3 style="color: #2c5f7c; margin-bottom: 20px; font-size: 1.3em;">{chart_title}</h3>
                            <img src="data:image/png;base64,{charts[chart_key]}" alt="{chart_title}" style="max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        </div>
                    </div>
"""
            else:
                html += f"""
                    <div id="chart-{chart_key}" class="chart-tab-content" style="display: {'block' if i == 0 else 'none'};">
                        <div class="chart-container">
                            <p style="text-align: center; color: #6b8a9a; padding: 40px;">Graphique non disponible</p>
                        </div>
                    </div>
"""
        
        html += """
                </div>
            </div>
            
            <style>
                .tab-btn:hover {
                    color: #2c5f7c;
                    background: #f8fafb !important;
                }
                .tab-btn.active {
                    color: #2c5f7c;
                    border-bottom-color: #5a9fd4 !important;
                    background: #f8fafb !important;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
            
            <script>
                function showChartTab(tabName) {
                    // Masquer tous les contenus
                    const contents = document.querySelectorAll('.chart-tab-content');
                    contents.forEach(content => {
                        content.style.display = 'none';
                    });
                    
                    // Désactiver tous les boutons
                    const buttons = document.querySelectorAll('.tab-btn');
                    buttons.forEach(button => {
                        button.classList.remove('active');
                        button.style.color = '#6b8a9a';
                        button.style.borderBottomColor = 'transparent';
                        button.style.background = 'none';
                    });
                    
                    // Afficher l'onglet sélectionné
                    document.getElementById('chart-' + tabName).style.display = 'block';
                    
                    // Activer le bouton correspondant
                    const btn = document.getElementById('btn-' + tabName);
                    btn.classList.add('active');
                    btn.style.color = '#2c5f7c';
                    btn.style.borderBottomColor = '#5a9fd4';
                    btn.style.background = '#f8fafb';
                }
            </script>
"""
    
    # Analyse mensuelle
    if len(monthly_df) > 0:
        html += """
            <div class="section">
                <h2>📅 Analyse Mensuelle</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Mois</th>
                            <th>Revenu</th>
                            <th>Pertes</th>
                            <th>Production</th>
                            <th>Prix Moyen</th>
                            <th>Heures Nég.</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for _, row in monthly_df.iterrows():
            month_str = str(row['year_month'])
            html += f"""
                        <tr>
                            <td><strong>{month_str}</strong></td>
                            <td>{format_currency(row['total_revenue_eur'])}</td>
                            <td style="color: #e88a8a;">{format_currency(row['total_negative_loss_eur'])}</td>
                            <td>{format_mwh(row['total_production_mwh'])}</td>
                            <td>{format_currency(row['avg_price_eur_mwh'])}</td>
                            <td>{int(row['hours_negative_price'])}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </div>
"""
    
    # Analyse des pertes
    html += f"""
            <div class="section">
                <h2>⚠️ Analyse des Pertes</h2>
"""
    if total_loss > 0:
        html += f"""
                <div class="recommendations">
                    <p style="font-size: 1.1em; margin-bottom: 15px;">
                        Les pertes liées aux prix négatifs représentent <strong>{format_currency(total_loss)}</strong>
                        soit <strong>{loss_percentage:.2f}%</strong> du revenu total.
                    </p>
                    <p>
                        Ces pertes surviennent lorsque le marché de l'électricité affiche des prix négatifs,
                        c'est-à-dire que les producteurs doivent payer pour injecter de l'électricité sur le réseau.
                        Cela se produit généralement lors de périodes de forte production renouvelable
                        et de faible demande.
                    </p>
                </div>
"""
    else:
        html += """
                <div class="recommendations">
                    <p style="font-size: 1.1em;">
                        ✅ Aucune perte liée aux prix négatifs n'a été enregistrée sur cette période.
                    </p>
                </div>
"""
    html += """
            </div>
"""
    
    # Heures critiques
    html += """
            <div class="section">
                <h2>🚨 Heures Critiques</h2>
"""
    if len(critical_hours) > 0:
        html += """
                <p style="margin-bottom: 20px;">
                    Les heures suivantes présentent les pertes les plus importantes
                    (prix négatifs avec production) :
                </p>
                <table>
                    <thead>
                        <tr>
                            <th>Date et Heure</th>
                            <th>Prix (€/MWh)</th>
                            <th>Production (MWh)</th>
                            <th>Perte (€)</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for _, row in critical_hours.iterrows():
            dt_str = row['datetime'].strftime('%d/%m/%Y %H:%M')
            html += f"""
                        <tr>
                            <td>{dt_str}</td>
                            <td style="color: #e88a8a; font-weight: bold;">{format_currency(row['price_eur_mwh'])}</td>
                            <td>{format_mwh(row['production_mwh'])}</td>
                            <td style="color: #e88a8a; font-weight: bold;">{format_currency(row['negative_price_loss_eur'])}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
"""
    else:
        html += """
                <div class="recommendations">
                    <p style="font-size: 1.1em;">
                        ✅ Aucune heure critique identifiée (pas de prix négatifs avec production).
                    </p>
                </div>
"""
    html += """
            </div>
"""
    
    # Recommandations
    html += """
            <div class="section">
                <h2>💡 Recommandations</h2>
                <div class="recommendations">
                    <h3>Optimisation de la production</h3>
                    <ul>
                        <li><strong>Surveillance des prix spot</strong> : Mettre en place un système d'alerte
                            pour les périodes de prix négatifs afin de réduire la production si possible.</li>
                        <li><strong>Stockage d'énergie</strong> : Envisager l'investissement dans des solutions
                            de stockage (batteries) pour décaler la production vers des heures plus rentables.</li>
                        <li><strong>Contrats de long terme</strong> : Diversifier les revenus avec des contrats
                            d'achat d'électricité (PPA) pour réduire l'exposition aux prix spot négatifs.</li>
                    </ul>
                    
                    <h3>Analyse continue</h3>
                    <ul>
                        <li>Suivre l'évolution mensuelle des pertes pour identifier des tendances.</li>
                        <li>Analyser les corrélations entre conditions météorologiques et prix négatifs.</li>
                        <li>Comparer les performances avec d'autres producteurs du secteur.</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Rapport généré automatiquement par le système d'analyse énergétique</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Sauvegarder
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Rapport HTML genere: {output_path}")
    
    return html


if __name__ == "__main__":
    # Test de génération de rapport
    from load_data import load_market_data, load_production_data
    from normalize_data import normalize_market_data, normalize_production_data
    from merge_data import merge_market_production
    from compute_metrics import compute_all_metrics
    import numpy as np
    
    print("=== Génération du rapport ===\n")
    
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
    
    report = generate_markdown_report(metrics_df, monthly_df)
    print("\n[OK] Rapport Markdown genere avec succes")
    
    # Générer aussi le rapport HTML
    html_report, charts_report = generate_html_report(metrics_df, monthly_df)
    print("[OK] Rapport HTML genere avec succes")
