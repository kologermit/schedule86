import mysql.connector as MySQL
from config import mysql as mysql_config
class DB:
    def __init__(self, config):
        self.__pool = MySQL.connect(**config)
        self.__cursor = self.__pool.cursor()

    def update(self, table, values, where=None):
        query = f"UPDATE {table} SET "
        if type(values) != type(dict()):
            return None
        values_keys = tuple(values.keys())
        data = [values[values_keys[0]]]
        query += f"{values_keys[0]} = %s"
        for i in values_keys[1:]:
            query += f",\n{i} = %s"
            data.append(values[i])
        if where:
            query += f"\nWHERE {where[0][0]} {where[0][1]} %s"
            data.append(where[0][2])
            for i in where[1:]:
                query += f"\n AND {i[0]} {i[1]} %s"
                data.append(i[2])
        try:
            cursor = self.__pool.cursor()
            cursor.execute(query, data)
            self.__pool.commit()
            cursor.close()
            return True
        except Exception as err:
            print(err)
            return None
        
        #values = {"col1": "data"}
        #where = (["col1", "=", "data"], ["col2", "=", "data2"])


    def insert(self, table, columns, values):
        # columns = [col1, col2, col3]
        # values = [[val1, val2, val2], []]
        query = f"INSERT INTO {table} "
        data = []
        if type(columns) == type(str()):
            query += f"({columns}) VALUES "
        else:
            query += f"({columns[0]}"
            for i in columns[1:]:
                query += f", {i}"
            query += ") VALUES "
        query += f"(%s"
        data.append(values[0][0])
        for i in values[0][1:]:
            query += ", %s"
            data.append(i)
        query += ")"
        for i in values[1:]:
            query += ", (%s"
            data.append(i[0])
            for j in i[1:]:
                query += ", %s"
                data.append(j)
            query += ")"
        try:
            cursor = self.__pool.cursor()
            cursor.execute(query, data)
            self.__pool.commit()
            cursor.close()
            return True
        except Exception as err:
            print(err)
            return None



    def select(self, table, columns="*", where=None, limit=None):
        query = f"SELECT "
        data = []
        if type(columns) == type(str()):
            query += f"{columns} FROM {table} "
        else:
            query += f"{columns[0]}"
            for i in columns[1:]:
                query += f", {i}"
            query += f" FROM {table}"
        if where:
            query += f"\nWHERE {where[0][0]} {where[0][1]} %s"
            data.append(where[0][2])
            for i in where[1:]:
                query += f"\n AND {i[0]} {i[1]} %s"
                data.append(i[2])
        if limit:
            query += "\n LIMIT %s"
            data.append(limit)
        try:
            cursor = self.__pool.cursor()
            cursor.execute(query, data)
            res = cursor.fetchall()
            self.__pool.commit()
            cursor.close()
            return res
        except Exception as err:
            print(err)
            return None

    def __del__(self):
        try:
            self.__pool.close()
        except:
            pass
        

# database = DB(mysql_config)
# database.update("log", {"text": "updated"}, [["id", "=", 31062]])
# print(database.select("log", ["id", "text"], [["id", "=", 31063]], 10))
# print(database.insert("log", "text", [["jj"], ["123"]]))