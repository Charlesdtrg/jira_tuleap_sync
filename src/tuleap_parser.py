"""
Module responsable de la normalisation de l'export Tuleap.

Les exports Tuleap peuvent contenir des noms de colonnes
variables selon la configuration du tracker.

Ce module standardise les noms utilisés dans le script.
"""


def parse_tuleap(df):
    """
    Renomme certaines colonnes Tuleap pour simplifier leur utilisation.

    Exemple :

    lien_ticket_jira → jira_key

    Paramètres
    ----------
    df : DataFrame

    Retour
    ------
    DataFrame normalisé
    """

    return df.rename(columns={

        # identifiant interne Tuleap
        "aid": "aid",

        # statut du ticket
        "status": "status",

        # clé du ticket Jira associé
        "lien_ticket_jira": "jira_key"

    })