import psycopg2

passwords_to_try = ["admin", "postgres", "password", "root", "1234", "123456", ""]
connected = False

for pwd in passwords_to_try:
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=pwd,
            dbname="postgres",
            connect_timeout=2,
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        ver = cur.fetchone()[0]
        cur.close()
        conn.close()
        print(f"SUCCESS: Password is '{pwd}'")
        print(f"PostgreSQL Version: {ver}")
        connected = True
        break
    except Exception as e:
        print(f"Failed with password '{pwd}': {e}")

if not connected:
    print("RESULT: Needs user password")
