"""
Module responsable de l'analyse de l'export CSV Jira.

Les exports Jira sont souvent très complexes :
- nombreuses colonnes
- colonnes dupliquées
- noms variables

Ce module extrait uniquement les informations nécessaires
pour la synchronisation avec Tuleap.
"""

import re
import pandas as pd
from src.version_utils import parse_version



def find_column(df, keyword):
    """
    Recherche dans le dataframe une colonne contenant un mot clé.

    Exemple :
    keyword = "Gravité"

    Si le CSV contient :
    "Champs personnalisés (Gravité)_114"

    la fonction retournera cette colonne.

    Paramètres
    ----------
    df : DataFrame
        Le dataframe Jira

    keyword : str
        Mot clé recherché dans les noms de colonnes

    Retour
    ------
    Nom de la colonne trouvée
    """
    for col in df.columns:
        # comparaison insensible à la casse
        if keyword.lower() in col.lower():
            return col
    return None


def get_version(row, keyword="Version(s) corrigée", how='highest'):
    """
    Détermine la version corrigée la plus élevée pour un ticket Jira.

    Certains exports Jira peuvent contenir plusieurs colonnes
    "Version(s) corrigée(s)" (ex :
    Version(s) corrigée(s), Version(s) corrigée(s).1, etc.).

    Cette fonction :
    1) récupère toutes ces colonnes
    2) supprime les valeurs vides
    3) compare les versions numériquement
    4) retourne la version la plus élevée
    """
    versions = []
    for col in row.index:
        if keyword in col:
            v = row[col]
            # ignorer les valeurs vides
            if isinstance(v, str) and v.strip():
                versions.append(v)

    # s'il n'y a aucune version
    if not versions:
        return None
    
    #### ajouter le livraison hors version ici

    # retourner la version la plus élevée
    assert how in ['highest', 'lowest']
    if how == 'highest':
        return max(versions, key=parse_version)
    else:
        return min(versions, key=parse_version)


def get_sprint(r):
    sprint_cols = [col for col in r.index if col.lower().startswith('sprint')]

    def extract_version(val):
        """
        Extrait une version sous forme de tuple d'entiers depuis 'Sprint Vx.y.z...'
        Exemple: 'Sprint V9.5.4' -> (9, 5, 4)
        """
        if isinstance(val, str):
            match = re.search(r'Sprint\s+V(\d+(?:\.\d+)*)', val)
            if match:
                return tuple(map(int, match.group(1).split('.')))
        return None

    values = [r[col] for col in sprint_cols]

    # Si tous les champs sont NaN → renvoyer exactement le même NaN
    if all(pd.isna(v) for v in values):
        return values[0]

    best_version = None
    best_value = None

    # Cas A : chercher les Sprint Vx.y...
    for v in values:
        version = extract_version(v)
        if version is not None:
            if best_version is None or version > best_version:
                best_version = version
                best_value = v

    if best_value is not None:
        return best_value

    # Cas B : aucun Sprint Vx.y → premier non-null
    for v in values:
        if not pd.isna(v):
            return v

    # Fallback
    return values[0]


def trouver_gravite_ligne(r):
    """
    Pour une ligne r d'un DataFrame :
    - Parcourt toutes les colonnes contenant 'gravité' dans le nom
    - Cherche si la valeur contient 'Majeur', 'Mineur' ou 'Bloquant' (insensible à la casse)
    - Renvoie la valeur exactement telle qu'elle existe dans le DataFrame
    - Sinon renvoie None
    """
    mots = ['Majeur', 'Bloquant', 'Mineur']
    for col in r.index:
        if "gravité" in col.lower():
            val = r[col]
            if pd.notna(val):
                val_str = str(val)
                for mot in mots:
                    if mot.lower() in val_str.lower():
                        return val  # renvoie la valeur originale
    return None


def trouver_composant_ligne(r):
    for col in r.index:
        if "composants" in col.lower():
            if pd.notna(r[col]):
                return col
    return None


def trouver_si_sprint(r):
    for col in r.index:
        if col.lower().startswith('sprint'):
            if pd.notna(r[col]):
                return True
    return False


def trouver_si_DevTestOps(r):
    for col in r.index:
        if "tiquettes" in col.lower():
            if str(r[col]).lower() == 'DevTestOps'.lower():
                return True
    return False


def parse_jira(df):
    """
    Transforme l'export brut Jira en dataframe normalisé.
    On extrait seulement les champs utiles.
    Retourne un dataframe avec les colonnes suivantes :

    key
    summary
    description
    status
    fix_version
    affected_version
    severity
    component
    sprint
    """

    records = []

    # Parcourir tous les tickets Jira
    for _, r in df.iterrows():

        if r['Clé de ticket'] == 'ROC-2792':
            for col in r.index:
                if "sprint" in col.lower() and pd.notna(r[col]):
                    sprint_bool_new = True
                    print('in', r[col], col)
            print(sprint_bool_new, sprint_bool)


        # Recherche dynamique des colonnes 
        severity = trouver_gravite_ligne(r)
        component_col = trouver_composant_ligne(r)
        sprint_bool = trouver_si_sprint(r)
        highest_sprint = get_sprint(r)
        DevTestOps_bool = trouver_si_DevTestOps(r)

        # déterminer la version affectée
        lowest_affected_version = get_version(r, 
            keyword="Affecte la/les version(s)", how='lowest')

        # déterminer la version corrigée
        highest_fix_version = get_version(r, 
            keyword="Version(s) corrigée", how='highest')
        
        record = {

            # identifiant du ticket Jira
            "key": r.get("Clé de ticket"),

            # résumé du bug
            "summary": r.get("Résumé"),

            # description détaillée
            "description": r.get("Description"),

            # statut Jira
            "status": r.get("État"),

            # version dans laquelle le bug est corrigé
            "fix_version": highest_fix_version,

            # version affectée
            "affected_version": lowest_affected_version,

            # gravité du bug
            "severity": severity,

            # composant concerné
            "component": r.get(component_col),

            # sprint renseigné
            "sprint_bool": sprint_bool,

            # sprint le plus élevé
            "sprint": highest_sprint,

            # vérifie la présence de valeur "DevTestOps" pour éviter de créer ces Tuleap
            "DevTestOps" : DevTestOps_bool
        }

        records.append(record)

        if record["key"] == 'ROC-2126':
            print(highest_sprint, )
            print('----------')
            print(r[['Sprint', 'Sprint.1', 'Sprint.2', 'Sprint.3', 
        'Sprint.4', 'Sprint.5', 'Sprint.6', 'Sprint.7', 'Sprint.8']])
            for v in r[['Sprint', 'Sprint.1', 'Sprint.2', 'Sprint.3', 
        'Sprint.4', 'Sprint.5', 'Sprint.6', 'Sprint.7', 'Sprint.8']]:
                if pd.notna(v):
                    print('not na')
                else:
                    print('is na')
            for col in r.index:
                if "sprint" in col.lower():
                    print(col.lower())
                    if pd.notna(r[col]):
                        print('not na')
            print(sprint_bool)
            print(record["sprint_bool"])
            print('----------')


    return pd.DataFrame(records)