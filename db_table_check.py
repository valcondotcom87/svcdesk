import sqlite3

DB_PATHS = [
	"C:/Users/arama/Documents/itsm-system/backend/db.sqlite3",
	"C:/Users/arama/Documents/db.sqlite3",
]

for path in DB_PATHS:
	conn = sqlite3.connect(path)
	cur = conn.cursor()
	cur.execute("select count(*) from sqlite_master where type='table'")
	total = cur.fetchone()[0]
	cur.execute("select name from sqlite_master where type='table'")
	all_tables = [row[0] for row in cur.fetchall()]
	cur.execute("select name from sqlite_master where type='table' and name like 'cmdb_%'")
	tables = [row[0] for row in cur.fetchall()]
	print(f"{path}: total_tables={total} cmdb_tables={tables}")
	print(f"{path}: all_tables={all_tables}")
	conn.close()
