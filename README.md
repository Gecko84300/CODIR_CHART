# CODIR CHART

**CODIR CHART** est un pipeline d'automatisation en Python conçu pour générer des rapports de Comité de Direction (CODIR) au format PowerPoint (.pptx) à partir de données brutes au format CSV.

Ce projet permet de traiter les données financières ou de performance, de générer automatiquement les graphiques correspondants (Waterfall, Barplots, etc.) et de les intégrer dans un template PowerPoint pré-défini.

## 🚀 Fonctionnalités

*   **Traitement de données** : Nettoyage et préparation des données via `pandas`.
*   **Génération de graphiques** : Création de visualisations (Marge, Volumes, MTD, YTD) prêtes pour l'export.
*   **Création de Présentations** : Intégration automatisée des graphiques et des KPI dans un template `.pptx`.
*   **Architecture Modulaire** : Code structuré pour séparer la configuration, le traitement, la visualisation et la génération du rapport.

## 📂 Structure du projet

```text
CODIR_CHART/
├── data/
│   └── DATA.csv                # Fichier de données source (utiliser des données factices en public)
├── export/
│   ├── img/                    # Dossier temporaire pour les graphiques générés
│   ├── template/
│   │   └── trame.pptx          # Template PowerPoint de base
│   └── Rapport_CODIR_xxx.pptx  # Rapport final généré
├── src/
│   ├── __init__.py
│   ├── chart.py                # Fonctions de génération de graphiques
│   ├── config.py               # Fichier de configuration (chemins, paramètres)
│   ├── data_processing.py      # Logique de traitement des données CSV
│   └── ppt_builder.py          # Logique d'assemblage du fichier PowerPoint
├── .gitignore                  # Fichiers et dossiers ignorés par Git (ex: __pycache__)
├── main.py                     # Script principal pour lancer le pipeline
├── requirements.txt            # Dépendances Python du projet
├── README.md                   # Documentation du projet
└── LICENSE                     # Licence du projet
```

## 🛠️ Installation

1. Clonez ce dépôt sur votre machine locale :
   ```bash
   git clone https://github.com/votre-nom-utilisateur/CODIR_CHART.git
   cd CODIR_CHART
   ```

2. (Recommandé) Créez et activez un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Linux/Mac
   venv\Scripts\activate     # Sur Windows
   ```

3. Installez les dépendances requises :
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Utilisation

1. Placez votre fichier de données (avec la structure attendue) dans le dossier `data/` et nommez-le `DATA.csv`.
2. Assurez-vous que votre template PowerPoint se trouve bien dans `export/template/trame.pptx`.
3. Lancez le script principal :
   ```bash
   python main.py
   ```
4. Le rapport généré sera disponible dans le dossier `export/`.

## ⚠️ Sécurité et Confidentialité

**Attention :** Ce dépôt public ne doit contenir **aucune donnée confidentielle**. Le fichier `data/DATA.csv` fourni ici ne contient que des données factices (dummy data) à des fins de démonstration. Ne commitez jamais les rapports générés contenant des données réelles de votre entreprise.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une *Issue* pour signaler un bug ou proposer une fonctionnalité, ou à soumettre une *Pull Request*.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.