import psycopg2
from psycopg2.extras import RealDictCursor
import time
import pandas as pd


def add_test_data():

    while True:
        try:
            conn = psycopg2.connect(host='localhost', database='PCMarketExpert',
                                    user='postgres', password='Chathurinda99*', cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            print("Connection Success! :)")
            break
        except Exception as error:
            print("Connection Failed! :(")
            print("Error: ", error)
            time.sleep(2)

    df = pd.read_csv('./tests/products_test_data.CSV')
    row_count = len(df.index)
    for row in range(row_count):
        query = """
                INSERT INTO "products" (ID,NAME,PRICE,CATEGORY,BRAND,LINK,SHOP,AVAILABILITY,SPEC)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
        record = (df.loc[row, 'id'].item(),
                  df.loc[row, 'name'],
                  df.loc[row, 'price'].item(),
                  df.loc[row, 'category'],
                  df.loc[row, 'brand'],
                  df.loc[row, 'link'],
                  df.loc[row, 'shop'],
                  df.loc[row, 'availability'],
                  df.loc[row, 'spec']
                  )
        cursor.execute(query,record)
        conn.commit()
