import psycopg2
from psycopg2.extras import RealDictCursor
import time

from app.config import settings

while True:
    try:
        conn = psycopg2.connect(host=Settings.database_hostname, database=settings.database_name,
                                user=settings.database_username, password=settings.database_password, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connection Success! :)")
        break
    except Exception as error:
        print("Connection Failed! :(")
        print("Error: ", error)
        time.sleep(2)

query = """
        COPY "products" (NAME,PRICE,CATEGORY,BRAND,LINK,SHOP,AVAILABILITY,SPEC)
        FROM 'products_test_data.CSV'
        DELIMITER ','
        CSV HEADER
        """
cursor.execute(query)
conn.commit()
