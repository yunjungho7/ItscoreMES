from db.connection import get_db_connection

def check_parttypes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Checking unique PARTTYPE in TBL_COM_GOODS...")
        cursor.execute("SELECT DISTINCT PARTTYPE FROM TBL_COM_GOODS")
        rows = cursor.fetchall()
        for r in rows:
            val = r[0]
            if isinstance(val, str):
                print(f"PARTTYPE: [{val}] (bytes: {val.encode('latin-1', 'replace')})")
            else:
                print(f"PARTTYPE: [{val}]")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_parttypes()
