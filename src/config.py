"""Paramètres du reporting CODIR.

Seules ANNEE et MOIS sont à modifier d'un mois sur l'autre :
tout le reste (nom du mois, chemins) en est déduit.
"""
from pathlib import Path

# --- Chemins (indépendants du dossier depuis lequel on lance le script) ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / 'data' / 'DATA.csv'

# --- Période analysée ---
ANNEE = 2026
MOIS = 8

MOIS_NOMS = {
    1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
    7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre',
}
MOIS_NOMS_COURTS = {
    1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin',
    7: 'Juil', 8: 'Aoû', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc',
}
MOIS_NOM = MOIS_NOMS[MOIS]

# --- Modes d'analyse ---
MTD = 'MTD'  # Month To Date : le mois analysé uniquement
YTD = 'YTD'  # Year To Date : de janvier au mois analysé

# --- Périmètre ---
SOCIETE = ['Société A', 'Société B', 'Société C', 'Société D', 'Société E']
ORDRE_SOUHAITE = list(SOCIETE)

# Doivent correspondre exactement aux libellés de la colonne « Sous Espèces » du CSV
SS_CATEGORIE = ['Céréales', 'Laitier', 'Porc', 'Basse Cour', 'Poule pondeuse', 'Canard', 'Poulet']

# --- Échelles d'unités (1.0 = valeurs déjà exprimées dans l'unité affichée) ---
# Ex. : si le CSV est en tonnes et que les graphiques affichent des KT, mettre 1 / 1000.
ECHELLE_VOLUMES = 1.0
ECHELLE_MARGE = 1.0