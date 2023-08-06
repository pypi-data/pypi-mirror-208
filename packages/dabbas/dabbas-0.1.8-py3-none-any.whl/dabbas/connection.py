import os
from pandas import DataFrame


def hello():
    print("Hello, World!")


def upload(df: DataFrame, name: str, **kwargs):
    df.to_sql(name, conn(), **kwargs)


def conn():
    from sqlalchemy import create_engine
    return create_engine(connection_url())


def connection_url():
    pg_user = os.environ['PG_USER']
    pg_password = os.environ['PG_PASSWORD']
    pg_host = os.environ['PG_HOST']
    pg_dbname = os.environ['PG_DBNAME']
    return f'postgresql://{pg_user}:{pg_password}@{pg_host}:5432/{pg_dbname}'


def connect():
    pg_user = os.environ['PG_USER']
    pg_password = os.environ['PG_PASSWORD']
    pg_host = os.environ['PG_HOST']
    pg_dbname = os.environ['PG_DBNAME']

    import psycopg2
    conn = psycopg2.connect(dbname=pg_dbname, user=pg_user,
                            password=pg_password, host=pg_host, port='5432')

    return conn


def query(sql):
    conn = connect()
    cur = conn.cursor()

    try:
        # Execute query and fetch results
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        cur.close()
        conn.close()
        raise e
    finally:
        if cur is not None:
            cur.close()
        conn.close()

    return cur.description, results
