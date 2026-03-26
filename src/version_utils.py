"""
Module utilitaire pour la gestion des versions.

Permet de comparer correctement les versions
du type v7.4.3 avec v7.4.10. 
Lexicographiquement : "10" < "3" donc il faut extraire les nombres. 
"""

import re



def parse_version(v):
    """
    Transforme une version en tuple numérique.

    Exemple :

    "v7.4.3" → (7,4,3)

    Paramètres
    ----------
    v : str

    Retour
    ------
    tuple
    """
    # si la version n'est pas une chaîne
    if not isinstance(v, str):
        return None

    # extraire tous les nombres
    nums = re.findall(r"\d+", v)
    if not nums:
        return None

    # convertir les nombres en entier
    return tuple(map(int, nums))


def est_tuple_numerique(elem) -> bool:
    """
    Vérifie si l'élément fourni est un tuple contenant uniquement des nombres (int ou float).

    Args:
        elem: Objet à tester.

    Returns:
        True si elem est un tuple et tous ses éléments sont des nombres, False sinon.
    """
    # Vérifie que c'est un tuple
    if not isinstance(elem, tuple):
        return False

    # Vérifie que chaque élément du tuple est un nombre (int ou float)
    return all(isinstance(x, (int, float)) for x in elem)


def get_version_category(version, config):
    """
    Détermine la catégorie métier d'une version Jira.

    Catégories possibles :
        production
        future
        unknown
        hors_version 

    Gestion spécifique :
    - "LIVRAISON HORS VERSION" → hors_version
    - valeurs non exploitables → unknown
    """

    # ---------------------------------------------------------
    # Normalisation de la valeur
    # ---------------------------------------------------------

    if version is None:
        return "unknown"

    if not isinstance(version, str):
        return "unknown"

    ticket_version = version.strip().upper()

    # ---------------------------------------------------------
    # livraison hors version
    # ---------------------------------------------------------

    if "HORS VERSION" in ticket_version:
        return "hors_version"
    
    # ---------------------------------------------------------
    # production ou future
    # ---------------------------------------------------------

    ticket_version = parse_version(ticket_version)
    prod_version = parse_version(config["version_en_production"])

    assert est_tuple_numerique(prod_version), \
        'La version en prod ne respecte pas le format suivant : "x.y.z..."'

    if ticket_version <= prod_version:
        return "production"
    else:
        return "future"


