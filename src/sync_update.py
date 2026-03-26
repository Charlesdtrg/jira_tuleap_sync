"""
Module : sync_update.py

Ce module est responsable de la mise à jour des tickets Tuleap existants
à partir des informations contenues dans les tickets Jira.

Principe général
----------------

On parcourt les tickets Tuleap existants.

Pour chaque ticket Tuleap :
    1. on récupère la clé du ticket Jira associé
    2. on cherche ce ticket dans l'extract Jira
    3. on récupère la version corrective (fix_version)
    4. on détermine la catégorie de cette version
    5. on met à jour le statut Tuleap selon les règles métier

Les règles métier sont :

- si la version corrective correspond à une version en production
  → statut Tuleap = "Corrigé en production"

- si la version corrective correspond à une version future
  → statut Tuleap = "En cours de résolution et de qualification"

- si aucune version corrective n'est renseignée
  → statut Tuleap = "En attente de prise en compte dans l’usine logicielle"

- si le ticket Jira est "Clos"
  → statut Tuleap = "Corrigé en production"

Le résultat est un DataFrame contenant uniquement :

    aid | status

Ce fichier sera ensuite exporté en CSV et importé dans Tuleap.
"""

import pandas as pd

# fonction permettant de déterminer la catégorie d'une version
from src.version_utils import get_version_category


def update_tuleap_status(tuleap_df, jira_df, config):
    """
    Met à jour les statuts des tickets Tuleap à partir des tickets Jira.

    Principe
    --------
    Pour chaque ticket Tuleap :
        - on récupère le ticket Jira associé
        - on analyse la version corrective
        - on applique les règles métier pour déterminer le nouveau statut

    Paramètres
    ----------
    tuleap_df : DataFrame
        tickets Tuleap

    jira_df : DataFrame
        tickets Jira (normalisés)

    config : dict
        configuration (statuts + référentiel versions)

    Retour
    ------
    DataFrame
        colonnes : aid | status
    """

    # ------------------------------------------------------------------
    # Création d'un accès rapide aux tickets Jira via leur clé
    # (optimisation importante : évite des recherches coûteuses)
    # ------------------------------------------------------------------
    jira_map = jira_df.set_index("key")

    updates = []

    # ------------------------------------------------------------------
    # Parcours des tickets Tuleap
    # ------------------------------------------------------------------
    for _, t in tuleap_df.iterrows():

        aid = t.get("aid")
        jira_key = t.get("jira_key")
        current_status = t.get("status")

        # ignorer si pas de lien Jira
        if not jira_key:
            continue

        # ignorer si ticket Jira absent
        if jira_key not in jira_map.index:
            continue

        jira_ticket = jira_map.loc[jira_key]
        fix_version = jira_ticket.get("fix_version")
        jira_status = jira_ticket.get("status")
        sprint_bool_jira = jira_ticket.get("sprint_bool")

        # déterminer la catégorie de version
        version_category = get_version_category(fix_version, config)

        # ------------------------------------------------------------------
        # APPLICATION DES RÈGLES MÉTIER (ordre CRITIQUE)
        # ------------------------------------------------------------------

        # Refactoriser le current_status pour qu'il corresponde exactement au yaml
        if pd.isna(current_status):
            raise ValueError("current_status est NaN ou None")

        try:
            current_status = str(current_status).lower()
        except Exception as e:
            raise ValueError(f"Impossible de convertir en string : {current_status}") from e

        if 'attente de prise' in current_status:
            current_status = config["tuleap_status"]["waiting"]
        elif 'qualification' in current_status:
            current_status = config["tuleap_status"]["in_progress"]
        elif 'production' in current_status:
            current_status = config["tuleap_status"]["fixed"]
        elif 'nnul' in current_status:
            current_status = config["tuleap_status"]["cancelled"]
 
        # Cas par défaut
        new_status = current_status

        # Ticket annulé dans Jira
        if jira_status == config["jira_status"]["cancelled"]:
            new_status = config["tuleap_status"]["cancelled"]

        # Ticket clos dans Jira
        elif jira_status == config["jira_status"]["closed"]:
            new_status = config["tuleap_status"]["fixed"]

        else:

            # Version en production
            if version_category == "production":
                new_status = config["tuleap_status"]["fixed"]

            # Version future
            elif version_category == "future":
                new_status = config["tuleap_status"]["in_progress"]

            # Livraison hors version ou unknown
            else:

                if sprint_bool_jira:
                    new_status = config["tuleap_status"]["in_progress"]
                else:
                    new_status = config["tuleap_status"]["waiting"]



        if aid == 717947:
            print(jira_key)
            print(fix_version, jira_status, sprint_bool_jira, version_category)
            print(current_status, new_status)
            print(jira_status == config["jira_status"]["cancelled"])

        # 2. Livraison hors version
        #elif version_category == "hors_version":

        #    if jira_status == config["jira_status"]["closed"]:
        #        new_status = config["tuleap_status"]["fixed"]

        
        # ------------------------------------------------------------------
        # On ajoute uniquement si le statut change
        # ------------------------------------------------------------------
        if new_status != current_status:
            if aid == 469444:
                print('hello', new_status == current_status)
            updates.append({
                "aid": aid,
                "status": new_status
            })

    # ------------------------------------------------------------------
    # Conversion en DataFrame pour export CSV
    # ------------------------------------------------------------------
    return pd.DataFrame(updates)