import pymysql

DB = dict(host='127.0.0.1', user='root', password='root',
          database='shoes', cursorclass=pymysql.cursors.DictCursor)

def sql(q, p = None, get = False):
    con = pymysql.connect(**DB)
    cur = con.cursor()
    cur.execute(q, p)
    res = cur.fetchall() if get else None
    con.commit()
    con.close()
    return res