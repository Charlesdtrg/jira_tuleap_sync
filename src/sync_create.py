"""
Module responsable de la création de tickets Tuleap
à partir de tickets Jira absents.
"""

import pandas as pd
from src.sync_update import get_version_category


def find_missing_jira(jira, tuleap):
    """
    Trouve les tickets Jira qui n'existent pas dans Tuleap.
    """
    tuleap_keys = set(tuleap["jira_key"].dropna())
    return jira[~jira["key"].isin(tuleap_keys)]


def build_tuleap_creation(missing, config):
    """
    Construit le dataframe final pour l'import Tuleap.
    """
    rows = []
    for _, r in missing.iterrows():

        fix_version = r["fix_version"]
        jira_status = r["status"]
        sprint_bool_jira = r["sprint_bool"]

        # déterminer la catégorie de version
        version_category = get_version_category(fix_version, config)

        # Ne pas prendre en compte les Jira au statut "Annulée"
        if (jira_status != config["jira_status"]["cancelled"]) & \
            (r["DevTestOps"] == 0):

            # ------------------------------------------------------------------
            # APPLICATION DES RÈGLES MÉTIER (ordre CRITIQUE)
            # ------------------------------------------------------------------

            # Cas par défaut
            status = config["tuleap_status"]["waiting"]

            # Ticket annulé dans Jira
            if jira_status == config["jira_status"]["cancelled"]:
                status = config["tuleap_status"]["cancelled"]

            # Ticket clos dans Jira
            elif jira_status == config["jira_status"]["closed"]:
                status = config["tuleap_status"]["fixed"]

            else:

                # Version en production
                if version_category == "production":
                    status = config["tuleap_status"]["fixed"]

                # Version future
                elif version_category == "future":
                    status = config["tuleap_status"]["in_progress"]

                # Livraison hors version ou unknown
                else:

                    if sprint_bool_jira:
                        status = config["tuleap_status"]["in_progress"]

            print('hhhhhhhhhhhhhh', r["severity"])

            rows.append({
                "titre": r["summary"],
                "status": status,
                "ads_d_appartenance": config["ads_value"],
                "lien_ticket_jira": r["key"],
                "s__v__rit___dp_roc": r["severity"],
                "bloc": r["component"],
                "version_corrective_111": r["fix_version"],
                "sprint_de_correction_1": r["sprint"],
                "description_du_bug": r["description"],
                "version_de_roc": r["affected_version"]
            })

    dataframe = pd.DataFrame(rows)
    print(dataframe.columns.to_list())

    #empty_titles = dataframe['titre'].apply(lambda x: repr(x))
    #print('il faut regarder ici', empty_titles.to_list())

    return pd.DataFrame(rows)