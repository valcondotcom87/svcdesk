import sqlite3
import sys
DB='db.sqlite3'
try:
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    print('Before:', cur.execute("SELECT app,name FROM django_migrations WHERE app='compliance'").fetchall())
    cur.execute("DELETE FROM django_migrations WHERE app='compliance' AND name='0001_initial'")
    conn.commit()
    print('After:', cur.execute("SELECT app,name FROM django_migrations WHERE app='compliance'").fetchall())
    conn.close()
except Exception as e:
    print('Error:', e)
    sys.exit(1)
