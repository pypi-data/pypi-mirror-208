def sql360():
    print("""
    import sqlite3
    conn=sqlite3.connect('sql.db')
    c=conn.cursor()
    c.execute("create table sql(first text,last text,pay integer)")
    c.execute("insert into sql values('value','value2',0)")
    c.execute("insert into sql values(?,?,?)",("name","ram",90))
    c.execute("insert into sql values(:name1,:name2,:cost)",{"name1":"value","name2":"name","cost":"900"})
    c.execute("select * from sql where first=:last",{'last':'value'})
    c.execute("select * from sql where first=?",('value',))
    print(c.fetchall())
    conn.commit()
    conn.close()
    """)
