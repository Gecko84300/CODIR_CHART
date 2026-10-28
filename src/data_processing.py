"""Préparation des données pour les graphiques de reporting.

Fonctions publiques (mêmes noms qu'avant) :
    - generer_donnees_waterfall
    - generer_donnees_scabar
    - generer_donnees_barplot
    - generer_donnees_barline
    - generer_tableau_variations_societes

Règle commune : `filtre_societes` regroupe toutes les sociétés non listées
dans une société « Autres » (sauf barplot / barline, où il sert de filtre,
car ces graphiques n'affichent pas de dimension société).
"""
import unicodedata

import numpy as np
import pandas as pd

from src.config import SOCIETE, ORDRE_SOUHAITE, DATA, MOIS, ANNEE, SS_CATEGORIE

# ==========================================================================
# CONSTANTES
# ==========================================================================
COLONNES_CSV = ['Societe', 'Time', 'Debouches', 'Line_Items', 'Versions',
                'Sous_Especes', 'Volumes', 'CA', 'Marge']
COLONNES_NUM = ['Volumes', 'CA', 'Marge']

MOIS_LABELS = {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin',
               7: 'Juil', 8: 'Aoû', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'}

# Noms de mois acceptés (sans accents, minuscules), français et anglais
_NOMS_MOIS = {
    1: ['jan', 'janv', 'janvier', 'january'],
    2: ['fev', 'fevr', 'fevrier', 'feb', 'february'],
    3: ['mar', 'mars', 'march'],
    4: ['avr', 'avril', 'apr', 'april'],
    5: ['mai', 'may'],
    6: ['jun', 'juin', 'june'],
    7: ['jul', 'juil', 'juillet', 'july'],
    8: ['aout', 'aug', 'august'],
    9: ['sep', 'sept', 'septembre', 'september'],
    10: ['oct', 'octobre', 'october'],
    11: ['nov', 'novembre', 'november'],
    12: ['dec', 'decembre', 'december'],
}
MOIS_NUM = {nom: num for num, noms in _NOMS_MOIS.items() for nom in noms}


# ==========================================================================
# FONCTIONS UTILITAIRES (communes à tous les graphiques)
# ==========================================================================
def _sans_accents(texte):
    """'Févr' -> 'fevr' (minuscules, sans accents)."""
    return unicodedata.normalize('NFKD', str(texte)).encode('ascii', 'ignore').decode().lower().strip()


def _preparer_dates(df):
    """Ajoute les colonnes numériques 'Annee' et 'Mois_Num' à partir de 'Time'.

    Formats acceptés : 'janv-25', 'Jan 2025', 'févr.-25', ...
    Lève une erreur explicite si un format ou un nom de mois est inconnu
    (au lieu de perdre silencieusement les lignes concernées).
    """
    df = df.copy()
    extrait = df['Time'].astype(str).str.extract(r'^\s*([^\W\d_]+)\.?[\s\-/]*(\d{2}|\d{4})\s*$')

    invalides = extrait[extrait.isna().any(axis=1)]
    if not invalides.empty:
        exemples = df.loc[invalides.index, 'Time'].unique()[:5].tolist()
        raise ValueError(f"Format de date non reconnu dans la colonne 'Time' : {exemples}")

    mois_num = extrait[0].map(_sans_accents).map(MOIS_NUM)
    if mois_num.isna().any():
        exemples = df.loc[mois_num.isna(), 'Time'].unique()[:5].tolist()
        raise ValueError(f"Nom de mois inconnu dans la colonne 'Time' : {exemples}")

    annee = extrait[1].astype(int)
    df['Annee'] = annee.where(annee >= 100, annee + 2000)
    df['Mois_Num'] = mois_num.astype(int)
    return df


def _nettoyer_nombres(serie):
    """'1 234,5' (y compris espaces insécables) -> 1234.5"""
    return pd.to_numeric(
        serie.astype(str)
        .str.replace(r'[\s\u00a0\u202f]', '', regex=True)
        .str.replace(',', '.', regex=False)
    )


def _charger_donnees(fichier_csv):
    """Lit le CSV, nomme les colonnes, convertit les nombres et prépare les dates.

    Une FileNotFoundError remonte naturellement si le fichier est absent.
    """
    df = pd.read_csv(fichier_csv, sep=';', encoding='utf-8')
    if df.shape[1] != len(COLONNES_CSV):
        raise ValueError(f"Le CSV doit contenir {len(COLONNES_CSV)} colonnes "
                         f"({COLONNES_CSV}), {df.shape[1]} trouvées.")
    df.columns = COLONNES_CSV
    for col in COLONNES_NUM:
        df[col] = _nettoyer_nombres(df[col])
    return _preparer_dates(df)


def _normaliser_mode(mode):
    """'YTD' -> 'YTD' ; 'MTD' ou 'Mois' -> 'MTD'."""
    m = str(mode).strip().upper()
    if m == 'YTD':
        return 'YTD'
    if m in ('MTD', 'MOIS'):
        return 'MTD'
    raise ValueError(f"mode_analyse invalide : {mode!r} (attendu : 'YTD' ou 'MTD'/'Mois')")


def _masque_mois(df, mois, mode):
    if _normaliser_mode(mode) == 'YTD':
        return df['Mois_Num'] <= mois
    return df['Mois_Num'] == mois


def _filtrer_periode(df, annee, mois, mode):
    return df[(df['Annee'] == annee) & _masque_mois(df, mois, mode)]


def _regrouper_societes(df, filtre_societes):
    """Les sociétés absentes de `filtre_societes` sont regroupées en 'Autres'."""
    if not filtre_societes:
        return df
    return df.assign(Societe=df['Societe'].where(df['Societe'].isin(filtre_societes), 'Autres'))


def _appliquer_filtres(df, debouches=None, line_items=None, sous_especes=None):
    if debouches:
        df = df[df['Debouches'].isin(debouches)]
    if line_items:
        df = df[df['Line_Items'].isin(line_items)]
    if sous_especes:
        df = df[df['Sous_Especes'].isin(sous_especes)]
    return df


def _ordre_final(valeurs, ordre_souhaite):
    """Ordre d'affichage : ordre_souhaite, puis le reste (alphabétique), puis 'Autres' en dernier."""
    valeurs = list(dict.fromkeys(valeurs))
    ordre = [v for v in (ordre_souhaite or []) if v in valeurs and v != 'Autres']
    reste = sorted(v for v in valeurs if v not in ordre and v != 'Autres')
    fin = ['Autres'] if 'Autres' in valeurs else []
    return ordre + reste + fin


def _tableau_mensuel(df, annee, colonnes_prefixes, remplir_zero):
    """Tableau 12 mois : N-1 (réel), Budget N, Réel N.

    colonnes_prefixes : ex. {'Volumes': 'Vol', 'Marge': 'MB'} -> Vol_N-1, MB_N-1, Vol_Budget, ...
    Les mois sans données restent NaN (la courbe s'arrête) sauf si remplir_zero=True.
    """
    res = pd.DataFrame({'Mois': [MOIS_LABELS[m] for m in range(1, 13)]}, index=range(1, 13))
    blocs = [('N-1', annee - 1, 'Actual'), ('Budget', annee, 'Budget'), ('N', annee, 'Actual')]
    for suffixe, an, version in blocs:
        sel = df[(df['Annee'] == an) & (df['Versions'] == version)]
        agg = sel.groupby('Mois_Num')[list(colonnes_prefixes)].sum().reindex(range(1, 13))
        for col, prefixe in colonnes_prefixes.items():
            res[f'{prefixe}_{suffixe}'] = agg[col]
    if remplir_zero:
        res = res.fillna(0)
    return res.reset_index(drop=True)


# ==========================================================================
# WATERFALL
# ==========================================================================
def generer_donnees_waterfall(fichier_csv=DATA, annee_analysee=ANNEE, mois_analyse=MOIS,
                              mode_analyse='YTD', indicateur='Volumes', dimension='Societe',
                              filtre_societes=SOCIETE, ordre_souhaite=ORDRE_SOUHAITE,
                              filtre_debouches=None, filtre_line_items=None,
                              filtre_sous_especes=None, diviseur=1):
    """Budget -> écarts par `dimension` -> Réel. `diviseur` convertit l'unité (ex. 1000 pour K€)."""
    df = _charger_donnees(fichier_csv)
    df = _regrouper_societes(df, filtre_societes)
    df = _filtrer_periode(df, annee_analysee, mois_analyse, mode_analyse)
    df = _appliquer_filtres(df, filtre_debouches, filtre_line_items, filtre_sous_especes)

    df_budget = df[df['Versions'] == 'Budget']
    df_actual = df[df['Versions'] == 'Actual']

    total_budget = df_budget[indicateur].sum() / diviseur
    total_actual = df_actual[indicateur].sum() / diviseur

    ecarts = df_actual.groupby(dimension)[indicateur].sum().sub(
        df_budget.groupby(dimension)[indicateur].sum(), fill_value=0
    ) / diviseur

    lignes = [{'Name': 'Budget', 'Type': 'total', 'Value': total_budget}]
    for nom in _ordre_final(ecarts.index, ordre_souhaite):
        ecart = ecarts[nom]
        if abs(ecart) > 0.001:
            nom_txt = str(nom)
            nom_court = nom_txt[:25] + '...' if len(nom_txt) > 25 else nom_txt
            lignes.append({'Name': nom_court, 'Type': 'variation', 'Value': ecart})
    lignes.append({'Name': 'Réel', 'Type': 'total', 'Value': total_actual})

    return pd.DataFrame(lignes)


# ==========================================================================
# SCABAR
# ==========================================================================
def generer_donnees_scabar(fichier_csv=DATA, annee_analysee=ANNEE, mois_analyse=MOIS,
                           mode_analyse='YTD', filtre_debouches=None, filtre_societes=SOCIETE,
                           ordre_souhaite=ORDRE_SOUHAITE, filtre_line_items=None,
                           filtre_sous_especes=None, colonne_mb='Marge', colonne_volume='Volumes',
                           diviseur_mb=1):
    """MB et MBU par société pour N-1, Réel et Budget. `diviseur_mb` convertit l'unité de MB."""
    df = _charger_donnees(fichier_csv)
    df = _regrouper_societes(df, filtre_societes)

    df_n = _filtrer_periode(df, annee_analysee, mois_analyse, mode_analyse)
    df_n = df_n[df_n['Versions'].isin(['Actual', 'Budget'])].copy()
    df_n['Versions'] = df_n['Versions'].replace({'Actual': 'Réel'})

    df_n1 = _filtrer_periode(df, annee_analysee - 1, mois_analyse, mode_analyse)
    df_n1 = df_n1[df_n1['Versions'] == 'Actual'].copy()
    df_n1['Versions'] = 'N-1'

    df_final = pd.concat([df_n, df_n1], ignore_index=True)
    df_final = _appliquer_filtres(df_final, filtre_debouches, filtre_line_items, filtre_sous_especes)

    # Somme des montants puis ratio : le MBU est pondéré par les volumes (pas une moyenne de ratios)
    df_agg = df_final.groupby(['Societe', 'Versions'], as_index=False)[[colonne_mb, colonne_volume]].sum()
    df_agg['MBU'] = np.where(df_agg[colonne_volume] != 0,
                             df_agg[colonne_mb] / df_agg[colonne_volume], 0)
    df_agg['MB'] = df_agg[colonne_mb] / diviseur_mb

    ordre_societes = _ordre_final(df_agg['Societe'].unique(), ordre_souhaite)
    df_agg['Societe'] = pd.Categorical(df_agg['Societe'], categories=ordre_societes, ordered=True)
    df_agg['Versions'] = pd.Categorical(df_agg['Versions'], categories=['N-1', 'Réel', 'Budget'], ordered=True)
    df_agg = df_agg.sort_values(['Societe', 'Versions']).reset_index(drop=True)

    return df_agg[['Societe', 'Versions', 'MB', 'MBU']]


# ==========================================================================
# BARPLOT (volumes mensuels)
# ==========================================================================
def generer_donnees_barplot(fichier_csv=DATA, annee_analysee=ANNEE, filtre_societes=None,
                            filtre_debouches=None, filtre_line_items=None,
                            filtre_sous_especes=None, diviseur_volume=1, remplir_zero=True):
    """Volumes mensuels N-1 / Budget / N. Ici `filtre_societes` FILTRE (pas de regroupement)."""
    df = _charger_donnees(fichier_csv)
    if filtre_societes:
        df = df[df['Societe'].isin(filtre_societes)]
    df = _appliquer_filtres(df, filtre_debouches, filtre_line_items, filtre_sous_especes)
    df = df.assign(Volumes=df['Volumes'] / diviseur_volume)

    return _tableau_mensuel(df, annee_analysee, {'Volumes': 'Vol'}, remplir_zero)


# ==========================================================================
# BARLINE (volumes en barres + marge en courbe)
# ==========================================================================
def generer_donnees_barline(fichier_csv=DATA, annee_analysee=ANNEE, filtre_societes=None,
                            filtre_debouches=None, filtre_line_items=None,
                            filtre_sous_especes=None, diviseur_volume=1, diviseur_marge=1,
                            remplir_zero=False):
    """Volumes et marge mensuels N-1 / Budget / N.

    Ici `filtre_societes` FILTRE (pas de regroupement).
    Par défaut les mois sans données restent NaN pour que la courbe s'arrête
    au lieu de retomber à 0.
    """
    df = _charger_donnees(fichier_csv)
    if filtre_societes:
        df = df[df['Societe'].isin(filtre_societes)]
    df = _appliquer_filtres(df, filtre_debouches, filtre_line_items, filtre_sous_especes)
    df = df.assign(Volumes=df['Volumes'] / diviseur_volume, Marge=df['Marge'] / diviseur_marge)

    return _tableau_mensuel(df, annee_analysee, {'Volumes': 'Vol', 'Marge': 'MB'}, remplir_zero)


# ==========================================================================
# TABLEAU DES VARIATIONS PAR SOCIÉTÉ
# ==========================================================================
def generer_tableau_variations_societes(fichier_csv=DATA, annee_analysee=ANNEE, mois_analyse=MOIS,
                                        mode_analyse='YTD', indicateur='Volumes',
                                        filtre_societes=SOCIETE, ordre_souhaite=ORDRE_SOUHAITE,
                                        filtre_sous_especes=SS_CATEGORIE, filtre_debouches=None,
                                        filtre_line_items=None):
    """Par sous-espèce : valeurs N-1 / N et variation (N - N-1) par société."""
    df = _charger_donnees(fichier_csv)

    if mois_analyse:
        df = df[_masque_mois(df, mois_analyse, mode_analyse)]

    df = _appliquer_filtres(df, filtre_debouches, filtre_line_items, filtre_sous_especes)
    df = _regrouper_societes(df, filtre_societes)

    df_act = df[df['Versions'].isin(['Actual', 'Réel'])]
    df_n = df_act[df_act['Annee'] == annee_analysee]
    df_n1 = df_act[df_act['Annee'] == annee_analysee - 1]

    # Colonnes globales N-1 et N
    global_n = df_n.groupby('Sous_Especes')[indicateur].sum().rename('N')
    global_n1 = df_n1.groupby('Sous_Especes')[indicateur].sum().rename('N-1')
    df_global = pd.concat([global_n1, global_n], axis=1).fillna(0)

    # Variations par société (alignement automatique des lignes et colonnes)
    def _pivot(d):
        return d.pivot_table(index='Sous_Especes', columns='Societe', values=indicateur,
                             aggfunc='sum', fill_value=0)

    df_variations = _pivot(df_n).sub(_pivot(df_n1), fill_value=0)
    df_variations.columns = [str(soc) for soc in df_variations.columns]
    df_variations = df_variations[_ordre_final(df_variations.columns, ordre_souhaite)]

    tableau = df_global.join(df_variations, how='outer').fillna(0)
    tableau.loc['Total'] = tableau.sum(numeric_only=True)
    return tableau.round(1)