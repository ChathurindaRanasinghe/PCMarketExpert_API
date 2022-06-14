import psycopg2
from psycopg2.extras import RealDictCursor
import time

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

    query = """
            COPY "products" (NAME,PRICE,CATEGORY,BRAND,LINK,SHOP,AVAILABILITY,SPEC)
            FROM 'tests\products_test_data.CSV'
            DELIMITER ','
            CSV HEADER
            """
    cursor.execute(query)
    conn.commit()
