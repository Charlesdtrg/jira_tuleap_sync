"""
Module responsable de la configuration du système de logs.

Les logs sont écrits :
- dans la console
- dans le fichier output/sync.log
"""

import logging
import os


def setup_logger():
    """
    Initialise et configure le logger.

    Retour
    ------
    logger : objet logging
    """

    # vérifier si le dossier output existe
    # sinon on le crée
    if not os.path.exists("output"):
        os.makedirs("output")

    # configuration du système de logs
    logging.basicConfig(

        # niveau minimum de log
        level=logging.INFO,

        # format du message de log
        format="%(asctime)s - %(levelname)s - %(message)s",

        handlers=[

            # écriture dans un fichier
            logging.FileHandler("output/sync.log"),

            # affichage dans la console
            logging.StreamHandler()

        ]
    )

    # création d'un logger nommé "sync"
    return logging.getLogger("sync")