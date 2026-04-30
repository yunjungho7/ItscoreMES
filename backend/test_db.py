import os
import sys
# Add current dir to sys.path
sys.path.append(os.getcwd())

from db.connection import get_db_connection
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM TBL_PROD_PRODUCEPLAN")
    count = cursor.fetchone()[0]
    print(f"Total rows in TBL_PROD_PRODUCEPLAN: {count}")
    
    cursor.execute("SELECT TOP 5 * FROM TBL_PROD_PRODUCEPLAN")
    rows = cursor.fetchall()
    for r in rows:
        print(r)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
