import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def scabar_chart(df,titre: str="Evolution de MB/MBU", col_region = 'Societe', col_version= 'Versions', col_bar = 'MB', col_point = 'MBU', versions=['N-1', 'Réel', 'Budget'], couleurs=None, largeur_barre=0.22, espace_entre_barres=0.03, taille_figure=(16, 8)):
    """
    Génère un graphique avec barres (somme) et nuage de points (moyenne) par dessus.
    """

    # 1. Paramètres par défaut
    if couleurs is None:
        couleurs = {'N-1': '#ffc000', 'Réel': '#92786b', 'Budget': '#431816'}

    # 2. Agrégations automatiques des données
    df_bars = df.groupby([col_region, col_version], observed = True)[col_bar].sum().unstack().fillna(0)[versions]
    df_mbu = df.groupby([col_region, col_version], observed = True)[col_point].mean().unstack().fillna(0)[versions]

    # 3. Calcul automatique des espacements (la "complexité technique")
    regions = df_bars.index
    x_base = np.arange(len(regions))

    # Calcul du décalage exact pour 3 barres
    decalage = largeur_barre + espace_entre_barres
    offsets = {versions[0]: -decalage, versions[1]: 0, versions[2]: decalage}

    max_bar_height = df_bars.max().max()
    marge_y_points = max_bar_height * 0.08  # Marge dynamique pour les points

    # 4. Création de la figure
    fig, ax = plt.subplots(figsize=taille_figure)

    # 5. Tracé des barres
    for version in versions:
        x_pos = x_base + offsets[version]
        bars = ax.bar(x_pos, df_bars[version],
                      width=largeur_barre,
                      label=f'{col_bar} {version}',
                      color=couleurs[version],
                      edgecolor='white')

        ax.bar_label(bars, fmt='%.1f', padding=4, fontsize=10, color=couleurs[version], fontweight='bold')

    # 6. Tracé des points
    for i, region in enumerate(regions):
        for version in versions:
            x_pos = i + offsets[version]
            y_pos = df_bars.loc[region, version] + marge_y_points
            valeur_point = df_mbu.loc[region, version]

            # Point
            ax.scatter(x_pos, y_pos, color=couleurs[version], marker='o',
                       edgecolor='black', linewidth=0.5, s=60, zorder=5)

            # Label du point
            ax.annotate(f"{valeur_point:.1f}", (x_pos, y_pos),
                        textcoords="offset points", xytext=(0, 8),
                        ha='center', fontsize=10, color=couleurs[version], fontweight='bold')

    # 7. Mise en forme automatique
    ax.set_xticks(x_base)
    ax.set_xticklabels(regions, fontweight='bold', fontsize=11, ha='right')
    ax.set_ylabel(col_bar, fontweight='bold', fontsize=11)
    ax.set_ylim(0, max_bar_height * 1.15)

    ax.set_title(titre, color='black',fontsize=15, pad=20, fontweight='bold')

    handles, labels = ax.get_legend_handles_labels()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.legend(handles[:3], labels[:3], 
               loc='lower center',    # Placé tout en bas au centre
               ncol=3,                # En ligne (3 colonnes)
               frameon=True, 
               fontsize=11)
    
    plt.tight_layout(rect=[0, 0.1, 1, 1])

    return fig, ax

def barplot_chart(df: pd.DataFrame,titre: str = "Évolution des Volumes (KT)",col_mois: str = 'Mois'):
    """
    Génère un graphique en barres verticales affichant uniquement les Volumes.
    
    Attentes pour le DataFrame (colonnes) :
    - col_mois : Mois de l'année (ex: 'Jan', 'Fév', ...)
    - 'Vol_N-1', 'Vol_Budget', 'Vol_N' : Valeurs de Volumes en KT
    """

    df = df.copy()
    mois = df[col_mois].astype(str).tolist() # Force la conversion en texte

    # Définition des positions pour les barres groupées
    x = np.arange(len(mois))
    width = 0.25  # Largeur des barres

    # Création de la figure et de l'axe unique
    fig, ax = plt.subplots(figsize=(14, 8))

    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    ax.grid(False)

    # Couleurs harmonisées
    color_n1 = '#ffc000'
    color_bud = '#431816'
    color_n = '#92786b'

    # ---------------------------------------------------------
    # 1. GRAPHIQUE À BARRES (Volumes en KT)
    # ---------------------------------------------------------
    ax.bar(x - width, df['Vol_N-1'], width, color=color_n1, edgecolor='none', label='Vol N-1 (KT)')
    ax.bar(x, df['Vol_Budget'], width, color=color_bud, edgecolor='none', label='Vol Budget (KT)')
    bars_n = ax.bar(x + width, df['Vol_N'], width, color=color_n, edgecolor='none', label='Vol N (KT)')

    ax.axhline(0, color='black', linewidth=1)

    # Labels sur la barre N (arrondi au dixième)
    offset_vol = max(df[['Vol_N-1', 'Vol_Budget', 'Vol_N']].max()) * 0.08
    for i, bar in enumerate(bars_n):
        h = bar.get_height()
        if pd.notna(h):
            texte = f"{h:.1f}".replace('.', ',')
            # Positionnement au-dessus de la barre (ou en dessous si valeur négative)
            y_pos = h + offset_vol if h >= 0 else h - offset_vol
            va_align = 'bottom' if h >= 0 else 'top'
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos, texte,
                     ha='center', va=va_align, color=color_n, fontweight='bold', fontsize=11)

    # ---------------------------------------------------------
    # 2. ESTHÉTIQUE ET FORMATAGE
    # ---------------------------------------------------------
    # Formateurs pour séparateur de milliers
    formatter = ticker.FuncFormatter(lambda val, pos: f"{val:,.0f}".replace(',', ' '))
    ax.yaxis.set_major_formatter(formatter)

    # Automatisation de l'espace en haut 
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(top=ymax * 1.25)  # Ajoute 25% d'espace libre au-dessus

    # Gestion des bordures (spines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')

    # Paramétrage des axes X et Y
    ax.set_xticks(x)
    ax.set_xticklabels(mois, rotation=45, ha='right', color='black', fontsize=11)

    ax.set_ylabel("Volumes (KT)", color='black', fontsize=12, fontweight='bold')
    ax.tick_params(axis='y', colors='black', labelsize=10)

    plt.title(titre, fontsize=20, fontweight='bold', color='black', pad=40)

    # ---------------------------------------------------------
    # 3. LÉGENDE
    # ---------------------------------------------------------
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10), ncol=3, frameon=False, fontsize=11)

    fig.subplots_adjust(top=0.85, bottom=0.15, left=0.08, right=0.95)
    return fig, ax

def waterfall_chart(df: pd.DataFrame,titre: str = "Volumes - mensuel vs budget",col_name: str = 'Name',col_type: str = 'Type',col_value: str = 'Value',unite: str = "kt",texte_evolution: str = "Évolution en tonnes"):
    """
    Génère un graphique en cascade (waterfall chart).

    Paramètres :
    - df : Le DataFrame contenant les données.
    - titre : Titre principal du graphique.
    - col_name : Nom de la colonne contenant les libellés de l'axe X.
    - col_type : Nom de la colonne du type de barre (doit contenir 'total' pour les piliers, autre chose pour les variations).
    - col_value : Nom de la colonne contenant les valeurs.
    - unite : L'unité de mesure affichée dans la bulle de variation (ex: 'kt', 'M€').
    - texte_evolution : Texte de la boîte d'information à droite du graphique.
    """
    # 1. Vérification des colonnes
    for col in [col_name, col_type, col_value]:
        if col not in df.columns:
            raise ValueError(f"Erreur : La colonne '{col}' est introuvable dans le DataFrame.")

    df = df.copy()

    # 2. Nettoyage des données
    if df[col_value].dtype == object:
        df[col_value] = df[col_value].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.').astype(float)

    labels = df[col_name].tolist()
    types = df[col_type].str.lower().tolist()
    valeurs = df[col_value].tolist()

    bases, hauteurs, couleurs = [], [], []
    cumul = 0
    base_budget = 1

    # 3. Calcul des piliers et des marches
    for i in range(len(df)):
        val = valeurs[i]
        t = types[i]

        if t == 'total':
            bases.append(0)
            hauteurs.append(val)
            cumul = val
            couleurs.append('#FFD700')
            if i == 0:
                base_budget = val if val != 0 else 1 # Évite la division par zéro plus tard
        else:
            bases.append(cumul)
            hauteurs.append(val)
            cumul += val
            couleurs.append('#FFD700' if val >= 0 else '#6B2723')

    # 4. Calcul des variations globales
    budget_val = valeurs[0]
    reel_val = valeurs[-1]
    var_abs = reel_val - budget_val
    var_pct = (var_abs / budget_val * 100) if budget_val != 0 else 0
    signe = "+" if var_abs > 0 else "-"
    color_text_var = "#00B050" if var_abs >= 0 else "#FF0000"

    # 5. Création du graphique
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    ax.grid(False)

    # Barres
    bars = ax.bar(labels, hauteurs, bottom=bases, color=couleurs, edgecolor='none', width=0.6)
    ax.axhline(0, color='black', linewidth=1)

    # Formateur Y
    formatter = ticker.FuncFormatter(lambda x, pos: f"{x:,.0f}".replace(',', ' '))
    ax.yaxis.set_major_formatter(formatter)

    val_max = max(abs(v) for v in valeurs) if valeurs else 1
    offset = val_max * 0.03

    # 6. Labellisation des barres
    for i, bar in enumerate(bars):
        h = hauteurs[i]
        b = bases[i]
        t = types[i]

        if t == 'total':
            texte = f"{int(h):,}".replace(',', ' ')
            y_pos = h / 2
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos, texte,
                    ha='center', va='center', color='black', fontweight='bold', fontsize=12)
        else:
            texte_val = f"{int(h):,}".replace(',', ' ')
            y_pos_val = max(b, b + h) + offset
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos_val, texte_val,
                    ha='center', va='bottom', color='black', fontweight='bold', fontsize=11)

            pct = (h / base_budget) * 100
            texte_pct = f"{pct:+.1f}%".replace('.', ',')
            couleur_pct = '#00B050' if pct > 0 else '#FF0000'
            y_pos_pct = min(b, b + h) - offset

            ax.text(bar.get_x() + bar.get_width() / 2, y_pos_pct, texte_pct,
                    ha='center', va='top', color=couleur_pct, fontsize=11)

    # 7. Esthétique des axes
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')

    plt.title(titre, fontsize=20, fontweight='bold', color='black', pad=75)
    plt.xticks(rotation=45, ha='right', color='black', fontsize=11)
    plt.yticks(color='black', fontsize=10)

    # 8. Boîtes d'informations supérieures
    text_var = f"{signe}{int(var_abs):,} {unite}\n({signe}{var_pct:.1f}%)".replace(',', ' ')

    # Boîte 1 (à gauche, sur le premier élément)
    ax.text(0, val_max * 1.15, text_var, ha='center', va='center',
            color=color_text_var, fontweight='bold', fontsize=11,
            bbox=dict(boxstyle='ellipse,pad=0.6', facecolor='#F2F2F2', edgecolor='#262626', lw=1.5))

    # Boîte 2 (à droite, dynamiquement placée sur le dernier élément au lieu de "7")
    pos_x_droite = len(labels) - 1
    ax.text(pos_x_droite, val_max * 1.15, texte_evolution, ha='center', va='center',
            color='#000000', fontsize=11,
            bbox=dict(boxstyle='square,pad=0.6', facecolor='#FFFFFF', edgecolor='#ffd700', lw=3))

    fig.subplots_adjust(top=0.75, bottom=0.20, left=0.08, right=0.95)
    return fig, ax

def barline_chart(df: pd.DataFrame,titre: str = "Évolution Marge Brute (M€) et Volumes (KT)",col_mois: str = 'Mois'):
    """
    Génère un graphique combiné (barres + courbes) reprenant la charte graphique spécifiée.

    Attentes pour le DataFrame (colonnes) :
    - col_mois : Mois de l'année (ex: 'Jan', 'Fév', ...)
    - 'MB_N-1', 'MB_Budget', 'MB_N' : Valeurs de Marge Brute en M€
    - 'Vol_N-1', 'Vol_Budget', 'Vol_N' : Valeurs de Volumes en KT
    """

    df = df.copy()
    mois = df[col_mois].astype(str).tolist() # Force la conversion en texte

    # Définition des positions pour les barres groupées
    x = np.arange(len(mois))
    width = 0.25  # Largeur des barres

    # Création de la figure et des axes (axe principal pour MB, axe secondaire pour Volumes)
    fig, ax1 = plt.subplots(figsize=(14, 8))
    ax2 = ax1.twinx()

    fig.patch.set_facecolor('#ffffff')
    ax1.set_facecolor('#ffffff')
    ax1.grid(False)
    ax2.grid(False)

    # ---------------------------------------------------------
    # 1. GRAPHIQUE À BARRES (Marge Brute en M€) sur ax1
    # ---------------------------------------------------------
    # Couleurs harmonisées avec l'ancien code : Gris pour le passé/budget, Jaune pour le réel (N)
    color_n1 = '#ffc000'
    color_bud = '#431816'
    color_n = '#92786b'

    bars_n1 = ax1.bar(x - width, df['MB_N-1'], width, color=color_n1, edgecolor='none', label='MB N-1 (M€)')
    bars_bud = ax1.bar(x, df['MB_Budget'], width, color=color_bud, edgecolor='none', label='MB Budget (M€)')
    bars_n = ax1.bar(x + width, df['MB_N'], width, color=color_n, edgecolor='none', label='MB N (M€)')

    ax1.axhline(0, color='black', linewidth=1)

    # Labels sur la barre N (arrondi au dixième)
    offset_mb = max(df[['MB_N-1', 'MB_Budget', 'MB_N']].max()) * 0.02
    for i, bar in enumerate(bars_n):
        h = bar.get_height()
        if pd.notna(h):
            texte = f"{h:.1f}".replace('.', ',')
            # Positionnement au-dessus de la barre (ou en dessous si valeur négative)
            y_pos = h + offset_mb if h >= 0 else h - offset_mb
            va_align = 'bottom' if h >= 0 else 'top'
            ax1.text(bar.get_x() + bar.get_width() / 2, y_pos, texte,
                     ha='center', va=va_align, color='black', fontweight='bold', fontsize=10)

    # ---------------------------------------------------------
    # 2. GRAPHIQUE EN COURBES (Volumes en KT) sur ax2
    # ---------------------------------------------------------

    ax2.plot(x, df['Vol_N-1'], linestyle='--', color=color_n1, linewidth=2, label='Vol N-1 (KT)')
    ax2.plot(x, df['Vol_Budget'], linestyle='--', color=color_bud, linewidth=2, label='Vol Budget (KT)')
    ax2.plot(x, df['Vol_N'], marker='o', linestyle='-', color=color_n, linewidth=2.5, markersize=7, label='Vol N (KT)')

    # Labels sur les points de la courbe N (arrondi au dixième)
    offset_vol = max(df[['Vol_N-1', 'Vol_Budget', 'Vol_N']].max()) * 0.03
    for i, val in enumerate(df['Vol_N']):
        if pd.notna(val):
            texte = f"{val:.1f}".replace('.', ',')
            ax2.text(x[i], val + offset_vol, texte,
                     ha='center', va='bottom', color=color_n, fontweight='bold', fontsize=11)

    # ---------------------------------------------------------
    # 3. ESTHÉTIQUE ET FORMATAGE
    # ---------------------------------------------------------
    # Formateurs pour séparateur de milliers
    formatter = ticker.FuncFormatter(lambda val, pos: f"{val:,.0f}".replace(',', ' '))
    ax1.yaxis.set_major_formatter(formatter)
    ax2.yaxis.set_major_formatter(formatter)

    # Automatisation de l'espace en haut pour ax1 (Marge Brute)
    ymin1, ymax1 = ax1.get_ylim()
    ax1.set_ylim(top=ymax1 * 1.60)  # Ajoute 20% d'espace libre au-dessus

    ax2.set_ylim(bottom=0)

    # Gestion des bordures (spines)
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)

    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)

    ax1.spines['left'].set_color('#cccccc')
    ax1.spines['bottom'].set_color('#cccccc')
    ax2.spines['right'].set_color('#cccccc')

    # Paramétrage des axes X et Y
    ax1.set_xticks(x)
    ax1.set_xticklabels(mois, rotation=45, ha='right', color='black', fontsize=11)

    ax1.set_ylabel("Marge Brute (M€)", color='black', fontsize=12, fontweight='bold')
    ax2.set_ylabel("Volumes (KT)", color=color_n, fontsize=12, fontweight='bold')

    ax1.tick_params(axis='y', colors='black', labelsize=10)
    ax2.tick_params(axis='y', colors=color_n, labelsize=10)

    plt.title(titre, fontsize=20, fontweight='bold', color='black', pad=40)

    # ---------------------------------------------------------
    # 4. LÉGENDE COMMUNE
    # ---------------------------------------------------------
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center',
               bbox_to_anchor=(0.5, 1.10), ncol=3, frameon=False, fontsize=11)

    fig.subplots_adjust(top=0.80, bottom=0.15, left=0.08, right=0.92)
    return fig, ax1, ax2

def tableau_variations(df, titre="Analyse des Variations par Société"):
    """
    Génère une figure Matplotlib affichant le DataFrame sous forme de tableau formaté.
    Applique une coloration conditionnelle sur les colonnes contenant le mot 'Écart'.
    """
    # Ajustement dynamique de la taille de la figure en fonction du nombre de lignes et colonnes
    hauteur_fig = len(df) * 0.4 + 1.5
    largeur_fig = len(df.columns) * 1.5 + 2
    
    fig, ax = plt.subplots(figsize=(largeur_fig, hauteur_fig))
    fig.patch.set_facecolor('#ffffff')
    ax.axis('off')  # Masquer les axes du graphique

    # Formatage des nombres (séparateur de milliers et 1 décimale)
    cell_text = []
    for i in range(len(df)):
        row = []
        for col in df.columns:
            val = df.iloc[i][col]
            if pd.isna(val):
                row.append("-")
            else:
                row.append(f"{val:,.1f}".replace(',', ' '))
        cell_text.append(row)

    # Création du tableau Matplotlib
    table = ax.table(cellText=cell_text,
                     rowLabels=df.index,
                     colLabels=df.columns,
                     cellLoc='right',
                     loc='center')

    # Ajustement global de la taille et de la police
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)  # Espacement des cellules (largeur, hauteur)

    # Couleurs basées sur la charte (ex: Budget/Entêtes en marron foncé)
    couleur_entete = '#431816'
    couleur_index = '#f2f2f2'
    couleur_ligne_paire = '#f9f9f9'
    couleur_ligne_impaire = '#ffffff'

    # Parcours des cellules pour appliquer le style
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#dddddd') # Bordures discrètes
        
        # Ligne d'en-tête (colonnes)
        if row == 0:
            cell.set_facecolor(couleur_entete)
            cell.set_text_props(color='white', weight='bold', ha='center')
        
        # Colonne d'index (Sous-espèces ou Total)
        elif col == -1:
            cell.set_facecolor(couleur_index)
            cell.set_text_props(weight='bold', color='black', ha='left')
            # Si c'est la ligne Total (dernière ligne)
            if row == len(df):
                cell.set_facecolor('#d9d9d9')
        
        # Cellules de données
        else:
            # Ligne Total (dernière ligne)
            if row == len(df):
                cell.set_facecolor('#d9d9d9')
                cell.set_text_props(weight='bold')
            # Alternance des couleurs de lignes (Zebra striping)
            elif row % 2 == 0:
                cell.set_facecolor(couleur_ligne_paire)
            else:
                cell.set_facecolor(couleur_ligne_impaire)

            # Mise en forme conditionnelle pour les écarts
            col_name = df.columns[col]
            if "Écart" in str(col_name):
                val = df.iloc[row-1][col_name]
                if val < 0:
                    cell.set_text_props(color='#FF0000', weight='bold') # Rouge
                elif val > 0:
                    cell.set_text_props(color='#00B050', weight='bold') # Vert
                    
    # Titre du tableau
    plt.title(titre, fontsize=16, fontweight='bold', color='black', pad=20)
    plt.tight_layout()
    
    return fig, ax

