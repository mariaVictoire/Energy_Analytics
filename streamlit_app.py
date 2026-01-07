"""
Application Streamlit pour l'analyse du marché de l'électricité.
Déployée sur Streamlit Community Cloud.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
import json

# Configuration de la page
st.set_page_config(
    page_title="Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajouter le dossier scripts au path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from load_data import load_market_data
from normalize_data import normalize_market_data, normalize_production_data
from merge_data import merge_market_production
from compute_metrics import compute_all_metrics
from generate_report import generate_html_report, create_charts

# Dossiers
reports_dir = Path(__file__).parent / "reports"
reports_dir.mkdir(exist_ok=True)
uploads_dir = Path(__file__).parent / "uploads"
uploads_dir.mkdir(exist_ok=True)

# CSS personnalisé
st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #5a9fd4 0%, #4a8bc2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .kpi-card {
            background: linear-gradient(135deg, #f8fafb 0%, #f0f4f7 100%);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e0e6ed;
            text-align: center;
        }
        .stButton>button {
            background: linear-gradient(135deg, #5a9fd4 0%, #4a8bc2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 2rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(90, 159, 212, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

def get_available_months():
    """Récupère la liste des mois disponibles dans les données de marché."""
    try:
        market_df = load_market_data()
        if market_df.empty:
            return []
        
        market_norm = normalize_market_data(market_df)
        market_norm['year_month'] = market_norm['datetime'].dt.to_period('M')
        months = sorted(market_norm['year_month'].unique())
        return [str(m) for m in months]
    except Exception as e:
        st.error(f"Erreur lors de la récupération des mois: {e}")
        return []

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>⚡ Energy Analytics</h1>
            <p style="font-size: 1.2em; margin-top: 0.5rem;">Analyse du marché de l'électricité</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Configuration")
        st.markdown("---")
        
        # Sélection du mois
        months = get_available_months()
        if not months:
            st.error("Aucune donnée de marché disponible. Vérifiez le fichier data/market/spot_prices.csv")
            return
        
        selected_month = st.selectbox(
            "Sélectionner un mois :",
            options=[""] + months,
            format_func=lambda x: "-- Choisir un mois --" if x == "" else x
        )
        
        st.markdown("---")
        
        # Upload de fichier
        st.header("📁 Fichier de production")
        uploaded_file = st.file_uploader(
            "Charger un fichier CSV de production",
            type=['csv'],
            help="Format attendu : CSV avec colonnes 'date' (ou 'datetime') et 'production' (ou 'production_mwh')"
        )
        
        st.markdown("---")
        
        # Instructions
        st.info("""
        **Instructions :**
        1. Sélectionnez le mois à analyser
        2. Chargez votre fichier CSV de production
        3. Cliquez sur "Lancer l'analyse"
        4. Le rapport HTML sera généré et téléchargeable
        """)
    
    # Contenu principal
    if not selected_month or selected_month == "":
        st.info("👈 Veuillez sélectionner un mois dans la barre latérale pour commencer.")
        return
    
    if uploaded_file is None:
        st.warning("⚠️ Veuillez charger un fichier CSV de production.")
        return
    
    # Bouton d'analyse
    if st.button("🚀 Lancer l'analyse", type="primary", use_container_width=True):
        with st.spinner("Analyse en cours..."):
            try:
                # Sauvegarder le fichier uploadé
                filepath = uploads_dir / uploaded_file.name
                with open(filepath, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Charger les données
                market_df = load_market_data()
                market_norm = normalize_market_data(market_df)
                
                # Filtrer le marché pour le mois sélectionné
                market_norm['year_month'] = market_norm['datetime'].dt.to_period('M')
                market_filtered = market_norm[market_norm['year_month'].astype(str) == selected_month].copy()
                
                if market_filtered.empty:
                    st.error(f"Aucune donnée de marché disponible pour le mois {selected_month}")
                    filepath.unlink()
                    return
                
                # Charger et normaliser les données de production
                production_df = pd.read_csv(filepath)
                production_norm = normalize_production_data(production_df)
                
                # Vérifier que les dates de production correspondent au mois sélectionné
                production_norm['year_month'] = production_norm['datetime'].dt.to_period('M')
                production_months = production_norm['year_month'].unique()
                
                if not any(str(m) == selected_month for m in production_months):
                    months_list = ', '.join(sorted([str(m) for m in production_months]))
                    st.error(
                        f"Les données de production ne correspondent pas au mois sélectionné ({selected_month}). "
                        f"Mois trouvés dans le fichier: {months_list}. "
                        f"Veuillez charger un fichier avec des données pour le mois {selected_month}."
                    )
                    filepath.unlink()
                    return
                
                # Filtrer les données de production pour le mois sélectionné
                production_filtered = production_norm[production_norm['year_month'].astype(str) == selected_month].copy()
                
                # Fusionner les données
                merged_df = merge_market_production(market_filtered, production_filtered)
                
                # Calculer les métriques
                metrics_df, monthly_df = compute_all_metrics(merged_df)
                
                # Période analysée
                start_date = metrics_df['datetime'].min()
                end_date = metrics_df['datetime'].max()
                
                # Générer le rapport HTML
                report_filename = f"report_{selected_month.replace('-', '_')}.html"
                report_path = reports_dir / report_filename
                
                # Créer les graphiques
                charts = create_charts(metrics_df, reports_dir)
                
                # Générer le rapport HTML
                # Sur Streamlit Cloud, on utilise une URL relative
                generate_html_report(metrics_df, monthly_df, output_path=report_path, base_url="")
                
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
                
                # Afficher les résultats
                st.success("✅ Analyse terminée avec succès !")
                
                # Afficher les KPIs
                st.markdown("---")
                st.header("📊 Chiffres Clés")
                
                col1, col2, col3, col4 = st.columns(4)
                
                total_revenue = metrics_df['revenue_eur'].sum()
                total_loss = metrics_df['negative_price_loss_eur'].sum()
                total_production = metrics_df['production_mwh'].sum()
                hours_negative = metrics_df['is_negative_price'].sum()
                
                with col1:
                    st.metric("Revenu Total", f"{total_revenue:,.2f} €")
                
                with col2:
                    st.metric("Production Totale", f"{total_production:,.2f} MWh")
                
                with col3:
                    st.metric("Pertes Prix Négatifs", f"{total_loss:,.2f} €")
                
                with col4:
                    st.metric("Heures à Prix Négatif", f"{hours_negative}")
                
                # Télécharger le rapport
                st.markdown("---")
                st.header("📥 Télécharger le rapport")
                
                with open(report_path, 'rb') as f:
                    st.download_button(
                        label="📄 Télécharger le rapport HTML",
                        data=f.read(),
                        file_name=report_filename,
                        mime="text/html",
                        type="primary",
                        use_container_width=True
                    )
                
                # Aperçu du rapport
                with st.expander("👁️ Aperçu du rapport (premières lignes)"):
                    st.markdown(f"**Période analysée :** {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}")
                    st.markdown(f"**Mois :** {selected_month}")
                    st.markdown(f"**Fichier généré :** {report_filename}")
                
            except Exception as e:
                st.error(f"Erreur lors de l'analyse: {str(e)}")
                import traceback
                with st.expander("Détails de l'erreur"):
                    st.code(traceback.format_exc())
                if filepath.exists():
                    filepath.unlink()

if __name__ == "__main__":
    main()

