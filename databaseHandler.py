import mysql.connector
import numpy as np

class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

class databaseHandler:
    def __init__(self, host, user, password, database, port, id):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.cursor = self.mydb.cursor()
        if self.mydb:
            print('db connected')
        self.config = self.getConfig(id)

    def getConfig(self, id):
        # Préparez la requête SQL avec un paramètre de substitution
        sql = "SELECT * FROM config WHERE idConfig = %s"
        # Exécutez la requête avec la valeur de maConfig.idSession
        values = (id,)
        self.cursor.execute(sql, values)

        column_names = [desc[0] for desc in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
            results.append(DictToObject(row_dict))

        # Si vous savez que vous avez toujours un seul résultat, vous pouvez retourner directement cet objet
        if len(results) == 1:
            return results[0]
        else:
            return results
        
    def insertResults(self, idEquilibreSession, EA):

        healthScore = round((EA * -0.15) + 115)
        if (healthScore < 0):
            healthScore = 0

        sql = "INSERT INTO equilibre_values (idEquilibreSession, idEquilibreValues, createdAt, value, healthScore) VALUES (%s, DEFAULT, DEFAULT, %s, %s)"
        values = (idEquilibreSession, EA, healthScore)
        values = [float(x) if isinstance(x, np.float64) else x for x in values]
        self.cursor.execute(sql, values)
        self.mydb.commit()

    def createEquilibreSession(self, idUser):
        # Exécuter une instruction SQL pour insérer une nouvelle ligne
        sql = sql = "INSERT INTO equilibre_session (idUser, idEquilibreSession, createdAt) VALUES (%s, DEFAULT, DEFAULT)"
        values = (idUser,)
        self.cursor.execute(sql, values)

        # Valider la transaction
        self.mydb.commit()

        idHandgripSession = self.cursor.lastrowid
        print("ID auto-incrémenté:", idHandgripSession)
        return idHandgripSession

    def getResults(self,idSession):
        # Préparez la requête SQL avec un paramètre de substitution
        sql = "SELECT idEquilibreValues, idEquilibreSession, value, healthScore FROM equilibre_values WHERE idEquilibreSession = %s ORDER BY idEquilibreValues DESC LIMIT 2"
        values = (idSession,)
        # Exécutez la requête avec la valeur de maConfig.idSession
        self.cursor.execute(sql, values)

        # Récupérez les noms des colonnes
        column_names = [desc[0] for desc in self.cursor.description]

        # Récupérez les résultats dans un tableau d'objets
        results = []

        for row in self.cursor.fetchall():
            # Créez un objet à partir des colonnes de chaque ligne
            obj = dict(zip(column_names, row))
            results.append(obj)
        print(results)
        return results
    



    # Fonction qui simule le comportement du code JavaScript fourni
    # def find_index_by_flexibility(sexe, age, equilibre_value, base_path='/mnt/data/'):
    #     # Sélection du fichier CSV en fonction du sexe
    #     csv_file_path = base_path + ('normes/handgrip_norme_homme.csv' if sexe == 1 else 'normes/handgrip_norme_femme.csv')

    #     # Lecture du fichier CSV
    #     df = pd.read_csv(csv_file_path)
        
    #     # Trouver l'index de la colonne correspondant à l'âge
    #     age_column = str(age - 1)  # Convertir l'âge en chaîne pour la correspondance
        
    #     # Trouver l'index de la première ligne où la valeur de souplesse est supérieure ou égale à souplesse_value
    #     index = df[df[age_column] >= equilibre_value].index[0] if not df[df[age_column] >= equilibre_value].empty else None
        
    #     # Retourner l'index de la ligne, si trouvé
    #     return index

# Exemple d'utilisation de la fonction
# sexe = 1 pour homme, 2 pour femme
# age = âge pour lequel chercher
# souplesse_value = valeur de souplesse à comparer
# Remarque : les fichiers CSV doivent être présents dans le chemin spécifié pour que cela fonctionne.
# find_index_by_flexibility(sexe=1, age=25, souplesse_value=30)

# Cette fonction est une simulation, elle ne sera pas exécutée ici car elle nécessite des fichiers CSV spécifiques.
# Si vous fournissez les fichiers CSV, je pourrais exécuter la fonction et vous montrer le résultat.

        