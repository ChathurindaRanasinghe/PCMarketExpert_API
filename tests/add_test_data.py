import psycopg2
from psycopg2.extras import RealDictCursor
import time
import pandas as pd


def add_test_data(database: str, password: str):

    while True:
        try:
            conn = psycopg2.connect(host='localhost', database=database,
                                    user='postgres', password=password, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            print("Connection Success! :)")
            break
        except Exception as error:
            print("Connection Failed! :(")
            print("Error: ", error)
            time.sleep(2)

    df = pd.read_csv('./tests/testdata.csv')
    row_count = len(df.index)
    for row in range(row_count):
        query = """
                INSERT INTO "pc-parts" (ID,NAME,PRICES,CATEGORY,BRAND,LINKS,SHOPS,AVAILABILITY,SPECS)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
        record = (df.loc[row, 'id'].item(),
                  df.loc[row, 'name'],
                  df.loc[row, 'prices'],
                  df.loc[row, 'category'],
                  df.loc[row, 'brand'],
                  df.loc[row, 'links'],
                  df.loc[row, 'shops'],
                  df.loc[row, 'availability'],
                  df.loc[row, 'specs']
                  )
        cursor.execute(query,record)
        conn.commit()
