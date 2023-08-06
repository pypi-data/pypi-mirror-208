import redis
import json
import pandas as pd
import psycopg2
import ast


class Qa:
    def __init__(self):
        pass

    def get_query_dates(self, the_database, query):
        parameters = the_database
        conn = psycopg2.connect(**parameters)
        cur = conn.cursor()
        cur.execute(query)

        # Get column names from cursor description
        column_names = [desc[0] for desc in cur.description]

        resultados = cur.fetchall()
        cur.close()
        conn.close()

        dates = pd.DataFrame(resultados, columns=column_names)
        print(dates)
        print("""･*:.｡. .｡.:*･゜ﾟ･*:.｡. .｡.:*･゜COLUMNS NAMES ﾟ･*:.｡. .｡.:*･゜ﾟ･*:.｡. .｡.:*･""")
        print(column_names)
        return dates

    def get_redis_dates(self, ip, port, collection):
        # conexión a la base de datos de Redis
        r = redis.Redis(host=ip, port=port, db=0)

        # obtener los valores de las claves
        cached_query_odoo = r.get(collection).decode('utf8')

        try:
            cached_query_odoo = ast.literal_eval(cached_query_odoo.decode())
            df = pd.DataFrame(cached_query_odoo)

        except Exception:
            data = json.loads(cached_query_odoo)
            df = pd.DataFrame.from_dict(data)

        print(df)
        return df

    def send_dates_to_redis(self, database, query, name_collection_redis):
        pass


action = Qa()
