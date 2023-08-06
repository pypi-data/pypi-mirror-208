
from supabase import create_client
import psycopg2
import os

DB_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE'
DB_ADMIN_KEY = "eeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqbHNsYWR0dGJvbG93b29pc3JwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY4MTEyMDQ5MSwiZXhwIjoxOTk2Njk2NDkxfQ.GzE799I13MX10Pbnn--h0_kSkX2md8JqCrTZyiAwniE"


def sql(query):
    try:
        conn = psycopg2.connect(database="postgres", 
                                user="reader",
                                password='password',
                                host="34.131.74.243", 
                                port="5432")
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        cursor.close()
        curs = conn.cursor()
        curs.execute("ROLLBACK")
        conn.commit()
        conn.close()
        raise e
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


key = os.getenv('ATLAS_KEY')

assert key is not None, "ATLAS_KEY is required"

boundary_supabase = create_client(
    'https://tjlsladttbolowooisrp.supabase.co', key)
poi_supabase = create_client('https://tjlsladttbolowooisrp.supabase.co', key)
