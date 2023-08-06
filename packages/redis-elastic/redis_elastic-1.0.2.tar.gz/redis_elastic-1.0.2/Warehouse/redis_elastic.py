import ast
import psycopg2
import functools
import redis
import threading
import time
import json
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class Settings_redis_elastic:
    def __init__(self, ip_redis, port_redis, url_elasticsearch):
        self.ip_redis = ip_redis
        self.port_redis = port_redis
        self.url_elasticsearch = url_elasticsearch

    def fusion(self, query, redis_name, elasticsearch_name, time_redis, time_elastic, database):
        # Creamos un cliente de Redis
        redis_client = redis.Redis(host=self.ip_redis, port=self.port_redis)

        # Decorador para cachear resultados de la función en Redis
        def cache_function_results(function):
            @functools.wraps(function)
            def wrapper(*args, **kwargs):
                # Generamos la clave del caché
                cache_key = f"{function.__name__}{redis_name}:{args}:{kwargs.items()}"
                print("[Key in Redis 🔑]: {}".format(cache_key))
                # Intentamos obtener el resultado del caché
                cached_result = redis_client.get(cache_key)

                # Si existe el resultado en caché, lo devolvemos
                if cached_result is not None:
                    return pd.read_json(cached_result)

                # Si no existe el resultado en caché, ejecutamos la función y lo almacenamos en caché
                result = function(*args, **kwargs)
                redis_client.set(cache_key, result.to_json())
                return result

            return wrapper

        def query_dates():
            # Connection postgres
            parameters = database

            conn = psycopg2.connect(**parameters)
            cur = conn.cursor()

            # Start the query
            cur.execute(query)

            # Get column names from cursor description
            column_names = [desc[0] for desc in cur.description]

            resultados = cur.fetchall()
            cur.close()
            conn.close()

            dates = pd.DataFrame(resultados, columns=column_names)
            return dates

        # Decorar la función query_products con el decorador de caché
        @cache_function_results
        def cached_query_dates():
            return query_dates()

        def update_cache():
            while True:
                # Obtener la versión actual del caché
                cached_version = redis_client.get(f"query_version{redis_name}")

                # Obtener la versión actual de la consulta en la base de datos
                db_version = str(query_dates().values)

                # Si la versión en la base de datos es diferente a la versión en caché,
                # actualizar el caché y la versión en caché
                if cached_version != db_version:
                    redis_client.set(f"query_version{redis_name}", db_version)
                    redis_client.delete(f"cached_query_dates{redis_name}:{()}:dict_items([])")
                    cached_query_dates()
                    print("Cache actualizado")

                # Redis, tiempo de actualization del cache
                time.sleep(time_redis)

        def redis_dates():

            # obtener los valores de las claves
            cached_query_redis = redis_client.get(f"cached_query_dates{redis_name}:():dict_items([])")

            # convertir los datos de bytes a una cadena de caracteres y luego a un diccionario
            # En caso de no realizar el ast, lo parse a un json
            try:
                cached_query_odoo = ast.literal_eval(cached_query_redis.decode())
                df = pd.DataFrame(cached_query_odoo)

            except Exception:
                data = json.loads(cached_query_redis)
                df = pd.DataFrame.from_dict(data)
            return df

        def elastic_indexation():
            client = Elasticsearch(self.url_elasticsearch)

            # Obtiene la variable de columnas de la función query dates
            get_list_columns = query_dates().columns.tolist()
            # print(get_list_columns)
            docs = []
            for i, row in redis_dates().iterrows():
                doc = {
                    '_index': elasticsearch_name,
                    '_id': i,
                    '_source': {field: row[field] for field in get_list_columns}
                }
                docs.append(doc)

            # Indexar documentos en Elasticsearch
            bulk(client, docs)
            client.close()

        # Actualizar el caché al iniciar el programa
        cached_query_dates()

        # Iniciar el hilo para actualizar el caché cada 10 minutos
        threading.Thread(target=update_cache).start()

        # Convertir los datos de Redis
        redis_dates()

        # Elastic search envio de Redis
        while True:
            elastic_indexation()
            print("Agregando datos de Elastic")
            time.sleep(time_elastic)
