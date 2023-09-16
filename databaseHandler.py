import mysql.connector

class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

class databaseHandler:
    def __init__(self, host, user, password, database, port):
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
        self.config = self.getConfig()

    def getConfig(self):
        # Préparez la requête SQL avec un paramètre de substitution
        sql = "SELECT * FROM config"
        # Exécutez la requête avec la valeur de maConfig.idSession
        self.cursor.execute(sql)

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
        sql = "INSERT INTO equilibre_values (idEquilibreSession, idEquilibreValues, createdAt, value) VALUES (%s, DEFAULT, DEFAULT, %s)"
        values = (idEquilibreSession, EA)
        print(EA)
        self.cursor.execute(sql, values)
        self.mydb.commit()

    def createEquilibreSession(self, idUser):
        # Exécuter une instruction SQL pour insérer une nouvelle ligne
        sql = sql = "INSERT INTO equilibre_session (idUser, idEquilibreSession, createdAt, age, sexe) VALUES (%s, DEFAULT, DEFAULT, DEFAULT, DEFAULT)"
        values = (idUser,)
        self.cursor.execute(sql, values)

        # Valider la transaction
        self.mydb.commit()

        idHandgripSession = self.cursor.lastrowid
        print("ID auto-incrémenté:", idHandgripSession)
        return idHandgripSession

    def getResults(self,idSession):
        # Préparez la requête SQL avec un paramètre de substitution
        sql = "SELECT idEquilibreValues, idEquilibreSession, value FROM equilibre_values WHERE idEquilibreSession = %s ORDER BY idEquilibreValues DESC LIMIT 2"
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
        