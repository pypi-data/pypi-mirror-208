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
    try:
        pg_url = os.environ['DATABASE_URL']
        return pg_url
    except KeyError:
        pg_user = os.environ.get('PG_USER', 'postgres')
        pg_password = os.environ.get('PG_PASSWORD', 'postgres')
        pg_host = os.environ.get('PG_HOST', 'localhost')
        pg_port = os.environ.get('PG_PORT', 5432)
        pg_dbname = os.environ.get('PG_DBNAME', 'postgres')
        return f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_dbname}'



def connect(url = connection_url()):
    import psycopg2
    conn = psycopg2.connect(url)

    return conn


def query(sql, url = connection_url()):
    conn = connect(url)
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
