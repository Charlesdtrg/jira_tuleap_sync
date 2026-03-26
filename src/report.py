"""
Module responsable de la génération d'un rapport
de synchronisation.

Le rapport permet de savoir :

- combien de tickets ont été mis à jour
- combien ont été créés
"""

def generate_report(update_df, create_df):
    """
    Génère un rapport texte.

    Paramètres
    ----------
    update_df : DataFrame
        tickets Tuleap mis à jour

    create_df : DataFrame
        tickets Tuleap créés
    """

    report = f"""
Synchronisation terminée

Tickets Tuleap mis à jour : {len(update_df)}
Tickets Tuleap créés : {len(create_df)}
"""

    # écrire le rapport dans un fichier
    with open(
        "output/sync_report.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)