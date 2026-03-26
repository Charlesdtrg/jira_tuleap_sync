"""
Fichier principal de l'application.

Ce script orchestre toutes les étapes :

1. Chargement de la configuration
2. Chargement des fichiers CSV Jira et Tuleap
3. Normalisation des données Jira
4. Mise à jour des tickets Tuleap existants
5. Détection des tickets Jira absents dans Tuleap
6. Création du fichier CSV de création de tickets Tuleap
7. Export des résultats
8. Génération d'un rapport

Ce fichier ne contient PAS de logique métier complexe.
Il appelle simplement les modules spécialisés.
"""

from src.logger import setup_logger
from src.config_loader import load_config
from src.loader import load_jira, load_tuleap
from src.jira_parser import parse_jira
from src.tuleap_parser import parse_tuleap
from src.sync_update import update_tuleap_status
from src.sync_create import find_missing_jira, build_tuleap_creation
from src.report import generate_report

import os
import glob
import csv


def main():
    """
    Fonction principale exécutée lorsque l'on lance le script.

    Elle orchestre tout le pipeline de synchronisation.
    """

    # Les logs seront écrits dans output/sync.log
    logger = setup_logger()

    logger.info("Démarrage de la synchronisation")

    # Chargement de la configuration YAML
    # Ce fichier contient les règles métier (statuts, version prod etc)
    config = load_config()

    # Chargement des CSV exportés depuis Jira et Tuleap
    logger.info("Chargement des fichiers CSV")
    #jira_raw = load_jira(["data/Jira CI 2026-03-24T09_04_46+0100.csv", 
    #                      "data/Jira CI 2026-03-24T09_12_37+0100.csv"])
    #tuleap_raw = load_tuleap("data/artifact_bugs_roc (32).csv")

    # --- JIRA : tous les fichiers du dossier ---
    jira_files = glob.glob("data/Jira*.csv")
    jira_raw = load_jira(jira_files)


    # --- TULEAP : un seul fichier ---
    tuleap_files = glob.glob("data/artifact*.csv")
    if not tuleap_files:
        raise FileNotFoundError("Aucun fichier Tuleap trouvé")
    if len(tuleap_files) > 1:
        print("Plusieurs fichiers Tuleap trouvés, on prend le premier")
    tuleap_raw = load_tuleap(tuleap_files[0])

    # Transformation de l'export Jira en structure exploitable
    # L'export Jira contient énormément de colonnes inutiles
    # On ne garde que celles nécessaires.
    logger.info("Parsing des données Jira")
    jira = parse_jira(jira_raw)

    # Normalisation des données Tuleap
    logger.info("Parsing des données Tuleap")
    tuleap = parse_tuleap(tuleap_raw)

    # Étape 1 : Mise à jour des tickets Tuleap existants
    logger.info("Mise à jour des tickets Tuleap existants")
    update_df = update_tuleap_status(tuleap, jira, config)

    # Étape 2 : Identifier les tickets Jira qui n'existent pas dans Tuleap
    logger.info("Recherche des tickets Jira absents dans Tuleap")
    missing = find_missing_jira(jira, tuleap)

    # Création du fichier de création de tickets
    logger.info("Préparation des tickets à créer")
    create_df = build_tuleap_creation(
        missing,
        config
    )

    # Création du dossier output si nécessaire
    if not os.path.exists("output"):
        os.makedirs("output")

    # Export du fichier de mise à jour des tickets
    update_df.to_csv(
        "output/tuleap_update.csv",
        index=False,
        sep=",", 
        encoding="utf-8-sig"
    )

    # Export du fichier de création des tickets
    create_df.columns = [col.replace('"', '') for col in create_df.columns]
    create_df.to_csv(
        "output/tuleap_create.csv",
        index=False,
        encoding="utf-8-sig",   # compatible Windows/Tuleap
        sep=",",                 # séparateur correct
        quoting=csv.QUOTE_ALL,   # met tout le texte entre guillemets
        quotechar='"',           # guillemets pour encadrer le texte
        escapechar='\\'          # échappe les guillemets internes
    )

    # Génération d'un rapport de synchronisation
    generate_report(update_df, create_df)

    logger.info("Synchronisation terminée")


if __name__ == "__main__":
    main()