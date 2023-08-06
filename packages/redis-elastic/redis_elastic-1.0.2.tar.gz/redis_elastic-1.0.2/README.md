# Redis ElasticSearch

![](https://i.imgur.com/sEkqRr3.png)

version 1.0.2 (Stable release)

## Summary

This Python code uses various libraries to connect to and manipulate data in different databases. Specifically, it imports the ast, psycopg2, functools, redis, threading, time, json, and pandas libraries, as well as the Elasticsearch and bulk modules of the elasticsearch library.

The Settings_redis_elastic class uses the connection parameters to a Redis server and an Elasticsearch server to create methods that allow you to get data from a PostgreSQL database and send it to an Elasticsearch index through Redis.

In addition, the class uses a decorator to cache the results of a Redis function and another method to update the cache periodically. It also defines a method to convert data stored in Redis to a Pandas DataFrame object.

Finally, the code runs an infinite loop to send the data from Redis to Elasticsearch with a certain time interval. This process is done in a separate thread, while another thread takes care of updating the cache periodically.

## recommendations

Use docker for testing, You can deploy the official containers

[Docker Postgres | 🐘](https://hub.docker.com/_/postgres)

[Docker Redis | 💾](https://hub.docker.com/_/redis)

[Docker Elasticsearch | ⚡](https://hub.docker.com/_/elasticsearch)

### Example by execution

```python
from Warehouse.redis_elastic import Settings_redis_elastic

postgres = {
    "host": "127.0.0.1",
    "port": "5432",
    "user": "etl",
    "password": "123",
    "database": "customer"
}

query = """Select rp.id,rp.name,rp.code from res_partner rp"""

my_object = Settings_redis_elastic("localhost", "6379", "http://localhost:9200")
my_object.fusion(query, "_test", "test", 10, 20, postgres)
``` 

## Documentation

1. The first step is to create an object, and connect redis and elasticsearch

```python
my_object = Settings_redis_elastic("redis_ip", "port_redis", "http://ip_elasticserch:port")
```

2. Variables description


 - query : It is the query that we make from the database, in the first version it works with postgres
 
 - redis_name : Is the name of the collection that Redis saves
 
 - elasticsearch_name : It is the way to feed the Elasticsearch API
 
 - time_redis : The time the SQL query is saved to Redis
 
 - time_elastic : It is the timeout from Redis to elasticsearch,
 **Recommendation:** It should be bigger than <<time_redis>>
 
 - database : It is the connection to the database, it must be a dictionary


Position in the method **fusion**

```python
my_object.fusion(query, redis_name , elasticsearch_name, time_redis, time_elastic, database)
```

## Mode debug

### Example of the tools

```python
from Develop.tools import action

postgres = {
    "host": "127.0.0.1",
    "port": "5432",
    "user": "etl",
    "password": "123",
    "database": "customer"
}

query = """Select rp.id,rp.name,rp.code from res_partner rp"""

action.get_query_dates(postgres, query)
action.get_redis_dates("localhost", 6379, "cached_query_dates_test:():dict_items([])")
``` 

### Actions

**get_query_dates**

With this function you get the results of your query in a Dataframe and print the columns

```python
action.get_query_dates(my_database, my_query)
```

**get_redis_dates**

Get the data from the Redis collection in a Dataframe

```python
action.get_redis_dates(my_ip, port, name_of_colection_redis)
```

