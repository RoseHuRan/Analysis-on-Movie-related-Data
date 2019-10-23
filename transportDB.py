import pymysql
import re

db1 = pymysql.connect("localhost", "root", "root", "csc3170")
cursor_ori = db1.cursor()

db2 = pymysql.connect("localhost", "root", "root", "csc3170-2")
cursor_new = db2.cursor()

sql = "SELECT * FROM production_co;"
cursor_new.execute(sql)
result = cursor_new.fetchall()
for each in result:
    if each[1]:
        sql = "SELECT * FROM production_co WHERE pc_id='%s' and pc_name='%s';" % (each[0], each[1])
    else:
        sql = "SELECT * FROM production_co WHERE pc_id='%s';" % (each[0])
    if cursor_ori.execute(sql) == 0:
        sql = "INSERT INTO production_co VALUES ('%s','%s')" % (each[0], each[1])
        cursor_ori.execute(sql)


sql = "SELECT * FROM crew;"
cursor_new.execute(sql)
result = cursor_new.fetchall()
for each in result:
    sql = "SELECT * FROM crew WHERE crew_id='%s';" % (each[0])
    if cursor_ori.execute(sql) == 0:
        sql = "INSERT INTO crew VALUES ('%s','%s')" % (each[0], re.escape(each[1]))
        cursor_ori.execute(sql)


sql = "SELECT * FROM genre;"
cursor_new.execute(sql)
result = cursor_new.fetchall()
genre_dict = {}
genre_id_count = 500
for each in result:
    sql = "SELECT * FROM genre WHERE genre_name='%s';" % (re.escape(each[1]))
    is_in = cursor_ori.execute(sql)
    if is_in == 1:
        genre_dict[each[0]] = cursor_ori.fetchone()[0]
    elif is_in == 0:
        genre_dict[each[0]] = genre_id_count
        sql = "INSERT INTO genre VALUES ('%s','%s')" % (genre_id_count, re.escape(each[1]))
        cursor_ori.execute(sql)
        genre_id_count += 1

sql = "SELECT * FROM movie;"
cursor_new.execute(sql)
result = cursor_new.fetchall()
for each in result:
    sql = "SELECT * FROM movie WHERE imdb_id ='%s';" % (each[0])
    if cursor_ori.execute(sql) == 0:
        sql = "INSERT INTO movie VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor_ori.execute(sql, (
            each[0], each[1], each[2], each[3], each[4], each[5], each[6], each[7],
            each[8], each[9], each[10], each[11], each[12]))


sql = "SELECT * FROM genre_in_mv;"
cursor_new.execute(sql)
result = cursor_new.fetchall()
for each in result:
    sql = "SELECT * FROM genre_in_mv WHERE mv_id='%s';" % (each[1])
    if cursor_ori.execute(sql) == 0:
        sql = "INSERT INTO genre_in_mv VALUES ('%s','%s')" % (genre_dict[each[0]], each[1])
        cursor_ori.execute(sql)


sql = "SELECT * FROM crew_in_mv;"
cursor_new.execute(sql)
result = cursor_new.fetchall()
for each in result:
    sql="SELECT * FROM crew_in_mv WHERE crew_id='%s' and mv_id='%s'and crew_position='%s';" % (each[0], each[1], each[2])
    if cursor_ori.execute(sql) == 0:
        sql = "INSERT INTO crew_in_mv VALUES ('%s','%s','%s')" % (each[0], each[1], each[2])
        cursor_ori.execute(sql)


sql = "SELECT * FROM co_produce_mv;"
cursor_new.execute(sql)
result = cursor_new.fetchall()
for each in result:
    sql = "SELECT * FROM co_produce_mv WHERE mv_id='%s' and co_id='%s';" % (each[0], each[1])
    if cursor_ori.execute(sql) == 0:
        sql = "INSERT INTO co_produce_mv VALUES ('%s','%s')" % (each[0], each[1])
        cursor_ori.execute(sql)



db1.commit()
db1.close()
db2.close()

