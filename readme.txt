jira_tuleap_sync
│
├── main.py
├── requirements.txt
├── config.yaml
│
├── data
│   ├── jira_export.csv
│   └── tuleap_export.csv
│
├── output
│
└── src
    ├── __init__.py
    ├── config_loader.py
    ├── loader.py
    ├── logger.py
    ├── jira_parser.py
    ├── tuleap_parser.py
    ├── version_utils.py
    ├── sync_update.py
    ├── sync_create.py
    └── report.py


Vision globale du programme
L exécution du main.py produit les étapes suivantes :
1 Charger la configuration
2 Charger les CSV
3 Nettoyer les données Jira
4 Nettoyer les données Tuleap
5 Mettre à jour les tickets Tuleap existants
6 Identifier les tickets Jira manquants
7 Générer les tickets Tuleap à créer
8 Exporter les CSV
9 Générer un rapport
10 Écrire les logs


Explications du .yaml :
type: major → version livrée
type: minor → correctif
status: production → déjà livré
status: future → pas encore livré