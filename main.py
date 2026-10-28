import os
import matplotlib.pyplot as plt

from src.config import ANNEE, MOIS, MOIS_NOM, MTD, YTD
from src.data_processing import (
    generer_donnees_barplot, 
    generer_donnees_barline,
    generer_donnees_waterfall,
    generer_donnees_scabar,
    generer_tableau_variations_societes
)
from src.chart import (
    barplot_chart, 
    barline_chart,
    waterfall_chart,
    scabar_chart,
    tableau_variations
)

from src.ppt_builder import construire_presentation_avec_trame

config_graphiques = [
    
    {
        "id": "barplot_MTD",
        "titre_graph": "Évolution des volumes (KT)",
        "titre_slide": "Evolution Mensuelle",
        "data_func": lambda: generer_donnees_barplot(),
        "chart_func": barplot_chart,
        "filename": "barplot.png"
    },

    {
        "id": "waterfall_MTD",
        "titre_graph": "Ecart de volumes N vs Budget - MTD",
        "titre_slide": "Evolution MTD",
        "data_func": lambda: generer_donnees_waterfall(indicateur='Volumes',mode_analyse='MTD'),
        "chart_func": waterfall_chart,
        "filename": "waterfall_chart_MTD.png"
    },

    {
        "id": "scabar_MTD",
        "titre_graph": "Evolution de MB/MBU - MTD",
        "titre_slide": "Evolution MTD",
        "data_func": lambda: generer_donnees_scabar(mode_analyse='MTD'),
        "chart_func": scabar_chart,
        "filename": "scabar_chart_MTD.png"
    },

    {
        "id": "waterfall_YTD",
        "titre_graph": "Ecart de volumes N vs Budget - YTD",
        "titre_slide": "Evolution YTD",
        "data_func": lambda: generer_donnees_waterfall(indicateur='Volumes',mode_analyse='YTD'),
        "chart_func": waterfall_chart,
        "filename": "waterfall_chart_YTD.png"
    },

    {
        "id": "scabar_YTD",
        "titre_graph": "Evolution de MB/MBU - YTD",
        "titre_slide": "Evolution YTD",
        "data_func": lambda: generer_donnees_scabar(mode_analyse='YTD'),
        "chart_func": scabar_chart,
        "filename": "scabar_chart_YTD.png"
    }
]

def exporter_graphiques_codir():
    dossier_images = "export/img"
    os.makedirs(dossier_images, exist_ok=True)
    
    resultats_generation = [] # On stocke un dictionnaire complet pour faciliter le PPT
    
    print("--- Démarrage de la génération des graphiques ---")
    
    for config in config_graphiques:
        print(f"Traitement : {config['id']}...")
        df = config["data_func"]()
        
        if df is not None and not df.empty:
            # Génération
            resultats = config["chart_func"](df, titre=config["titre_graph"])
            fig = resultats[0] if isinstance(resultats, tuple) else resultats
            
            # Sauvegarde
            chemin_fig = f"{dossier_images}/{config['filename']}"
            fig.savefig(chemin_fig, dpi=300, bbox_inches='tight', transparent=True)
            plt.close(fig)
            
            # On sauvegarde les infos utiles pour le PowerPoint
            resultats_generation.append({
                "titre_slide": config["titre_slide"],
                "image": chemin_fig
            })
        else:
            print(f"  ⚠️ Aucune donnée pour {config['id']}.")
            
    return resultats_generation

if __name__ == "__main__":
    images_generees = exporter_graphiques_codir()
    
    # 1. Slide de Titre (Page de garde)
    mes_slides_codir = [
        {
            'titre': f"{MOIS_NOM} {ANNEE}", 
            'image': None,
            'index_masque': 0 
        }
    ]
    
    # 2. Ajout dynamique de toutes les slides générées avec succès
    for item in images_generees:
        mes_slides_codir.append({
            'titre': item["titre_slide"], 
            'image': item["image"], 
            'index_masque': 1
        })

    # 3. Génération du PPT
    if len(mes_slides_codir) > 1:
        construire_presentation_avec_trame(
            graphiques=mes_slides_codir,
            chemin_modele="export/template/trame.pptx",
            chemin_sortie=f"export/Rapport_CODIR_{ANNEE}_{MOIS}.pptx"
        )