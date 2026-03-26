"""
Module responsable du chargement des fichiers CSV.

Ce module encapsule la lecture des exports Jira et Tuleap.
Cela permet de centraliser la gestion :
- encodage
- séparateurs
- options pandas
"""

import pandas as pd
import glob
pd.set_option('display.max_columns', None)



def load_jira(paths):
    """
    Charge et fusionne plusieurs CSV Jira avec gestion correcte des colonnes.
    """

    if isinstance(paths, str):
        paths = [paths]

    dfs = []

    for path in paths:
        df = pd.read_csv(
            path,
            encoding="utf-8",
            sep=None,          # auto-détection
            engine="python"    # nécessaire pour sep=None
        )

        #print(f"{path} -> {len(df.columns)} colonnes détectées")

        dfs.append(df)

    df_merged = pd.concat(
        dfs,
        axis=0,
        join='outer',
        ignore_index=True
    )

    return df_merged


def load_tuleap(path):
    """
    Charge le fichier CSV exporté depuis Tuleap.

    Tuleap utilise parfois le séparateur ";"
    au lieu de ",".

    On tente donc d'abord avec ";"
    puis avec "," si cela échoue.
    """

    try:

        # tentative avec séparateur ";"
        return pd.read_csv(
            path,
            encoding="utf-8",
            sep=";"
        )

    except Exception:

        # fallback avec séparateur standard
        return pd.read_csv(
            path,
            encoding="utf-8"
        )


if __name__ == '__main__':
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


    print('ANALYSE COLONNES JIRA')
    for c in jira_raw.columns:
        #print(c)
        if 'tiquettes' in c.lower():
            print(c)

    print('JIRA:')
    print(len(jira_raw))
    #print(jira_raw.columns.to_list())
    # etiquettes : 6 et 4
    # sprint : 9 au max
    print(jira_raw['Clé de ticket'].unique())
    print(type(jira_raw.loc[0, 'Clé de ticket']))
    print((jira_raw['Clé de ticket'] == 'ROC-2792').sum())
    result = jira_raw.loc[
    jira_raw['Clé de ticket'] == 'ROC-2792',
    [
        'Version(s) corrigée(s)', 'État', 'ID de ticket',
        'Étiquettes', 'Étiquettes.1', 'Étiquettes.2', 'Étiquettes.3',
        'Étiquettes.4', 'Étiquettes.5',
        'Champs personnalisés (Gravité).1', 'Champs personnalisés (Gravité).2',
        'Champs personnalisés (Gravité).3', 'Champs personnalisés (Gravité).4',
        'Composants', 'Sprint', 'Sprint.1', 'Sprint.2', 'Sprint.3', 
        'Sprint.4', 'Sprint.5', 'Sprint.6', 'Sprint.7', 'Sprint.8'
    ]
    ]
    print(result.to_dict(orient='records')[0])
    print('------------------')
    print(pd.notna(result['Sprint']).any())
    print(result['ID de ticket'])
    print('------------------')

    #print('demarcation')
    #for col in result.index:
    #    if ("sprint" in col.lower()) & pd.notna(result[col]):
    #        print(True)
    #    else:
    #        print(False)

    def trouver_si_sprint(r):
        for col in r.index:
            if "sprint" in col.lower():
                if pd.notna(r[col]):
                    return True
        return False
    
    for _, r in result.iterrows():
        print(trouver_si_sprint(r))
        

    #print(jira_raw['Version(s) corrigée(s)'].unique())
    #print(jira_raw['État'].unique())
    #print(jira_raw['Étiquettes'].unique())
    #print(jira_raw['Étiquettes.1'].unique())
    #print(jira_raw['Étiquettes.2'].unique())
    #print(jira_raw['Étiquettes.3'].unique())
    print(jira_raw['Champs personnalisés (Gravité).1'].unique())
    print(jira_raw['Champs personnalisés (Gravité).2'].unique())
    print(jira_raw['Champs personnalisés (Gravité).3'].unique())
    print(jira_raw['Champs personnalisés (Gravité).4'].unique())
    #print(jira_raw['Composants'].unique())
    #print(jira_raw['Composants.1'].unique())
    #print(jira_raw['Sprint'].unique())
    #print(jira_raw['Sprint.1'].unique())
    #print(jira_raw['Sprint.2'].unique())
    #print(jira_raw['Sprint.3'].unique())
    #print(jira_raw['Champs personnalisés (Gravité ClearQuest)'].unique())
    


    #print(jira_raw['Affecte la/les version(s)'].unique())
    #print(jira_raw['Affecte la/les version(s).1'].unique())
    #print(jira_raw['Affecte la/les version(s).2'].unique())

    print('TULEAP:')
    print(len(tuleap_raw))
    print(tuleap_raw.columns)
    print(tuleap_raw['status'].unique())
    print(tuleap_raw.loc[tuleap_raw['aid'] == 717947, 'status'])

