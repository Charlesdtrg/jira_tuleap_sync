"""
Module responsable du chargement de la configuration.

La configuration contient :
- la version de production
- les statuts Tuleap
- le statut Jira "Clos"
- la valeur du champ ADS

Ces règles sont stockées dans config.yaml afin
de pouvoir modifier les règles métier sans toucher au code.
"""

import yaml


def load_config(path="config.yml"):
    """
    Charge le fichier YAML de configuration.

    Paramètres
    ----------
    path : str
        chemin du fichier de configuration

    Retour
    ------
    dict
        dictionnaire Python contenant toute la configuration
    """

    # ouvrir le fichier YAML en mode lecture
    with open(path, "r", encoding="utf-8") as f:

        # transformer le YAML en dictionnaire Python
        config = yaml.safe_load(f)

    return config