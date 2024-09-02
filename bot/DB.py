import logging, sqlite3

class DB:
    def __init__(self, db_filename):
        self.filename = db_filename

    def update(self, table, values, where=None):
        query = f"UPDATE {table} SET "
        if type(values) != type(dict()):
            return None
        values_keys = tuple(values.keys())
        data = [values[values_keys[0]]]
        query += f"{values_keys[0]} = ?"
        for i in values_keys[1:]:
            query += f",\n{i} = ?"
            data.append(values[i])
        if where:
            query += f"\nWHERE {where[0][0]} {where[0][1]} ?"
            data.append(where[0][2])
            for i in where[1:]:
                query += f"\n AND {i[0]} {i[1]} ?"
                data.append(i[2])
        self.query(query, data)
        
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
        query += f"(?"
        data.append(values[0][0])
        for i in values[0][1:]:
            query += ", ?"
            data.append(i)
        query += ")"
        for i in values[1:]:
            query += ", (?"
            data.append(i[0])
            for j in i[1:]:
                query += ", ?"
                data.append(j)
            query += ")"
        self.query(query, data)

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
            query += f"\nWHERE {where[0][0]} {where[0][1]} ?"
            data.append(where[0][2])
            for i in where[1:]:
                query += f"\n AND {i[0]} {i[1]} ?"
                data.append(i[2])
        if limit:
            query += "\n LIMIT ?"
            data.append(limit)
        return self.query(query, data, True)

    def query(self, sql_query, data=[], is_return=False):
        while True:
            try:
                pool = sqlite3.connect(self.filename)
                cursor = pool.cursor()
                cursor.execute(sql_query, data)
                if is_return:
                    res = cursor.fetchall()
                pool.commit()
                cursor.close()
                pool.close()
                if is_return:
                    return res
                return
            except Exception as err:
                logging.exception(err)       