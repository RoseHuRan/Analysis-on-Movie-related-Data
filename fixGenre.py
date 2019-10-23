import pymysql
from requests import get
from bs4 import BeautifulSoup
import json
import re

def addCharater(character_dict):
    character_dict[455] = '-'
    character_dict[447] = 'a'
    character_dict[461] = 'B'
    character_dict[449] = 'C'
    character_dict[445] = 'D'
    character_dict[451] = 'e'
    character_dict[456] = 'F'
    character_dict[462] = 'g'
    character_dict[458] = 'H'
    character_dict[454] = 'i'
    character_dict[471] = 'k'
    character_dict[464] = 'l'
    character_dict[448] = 'm'
    character_dict[460] = 'n'
    character_dict[450] = 'o'
    character_dict[463] = 'p'
    character_dict[446] = 'r'
    character_dict[453] = 'S'
    character_dict[459] = 't'
    character_dict[467] = 'u'
    character_dict[466] = 'v'
    character_dict[468] = 'W'
    character_dict[452] = 'y'

def get_detail_info(mv_id):
    link_str = 'https://www.imdb.com/title/' + mv_id + '/'
    headers = {"Accept-Language": "en-US, en;q=0.5"}
    while True:
        try:
            detail_response = get(link_str, headers=headers)
            break
        except Exception as e:
            print("Request error: ", e)
            continue
    detail_page_html = BeautifulSoup(detail_response.text, 'html.parser')
    info = json.loads(detail_page_html.find('script', type='application/ld+json').text)
    mv_genres = []
    if 'genre' in info:
        if type(info['genre']) == str:
            mv_genres.append({'name':info['genre']})
        else:
            for genre in info['genre']:
                mv_genres.append({'name': genre})

        sql = "DELETE FROM genre_in_mv WHERE mv_id = '%s'" % mv_id
        cursor.execute(sql)

        # genre table
        genre_id = None
        for genre in mv_genres:
            sql = "SELECT * FROM genre WHERE genre_name='%s'" % re.escape(genre['name'])
            if cursor.execute(sql) == 0:
                sql = "INSERT INTO genre(genre_name) VALUES ('%s')" % re.escape(genre['name'])
                cursor.execute(sql)
                genre_id = cursor.lastrowid
            else:
                genre_id = cursor.fetchone()[0]
            sql = "SELECT * FROM genre_in_mv WHERE genre_id=%d and mv_id='%s'" % (genre_id, mv_id)
            if cursor.execute(sql) == 0:
                sql = "INSERT INTO genre_in_mv VALUES (%d,'%s')" % (genre_id, mv_id)
                cursor.execute(sql)


if __name__ == '__main__':
    db = pymysql.connect("localhost", "root", "root", "csc3170")
    cursor = db.cursor()
    character_dict = {}
    addCharater(character_dict)
    sql = 'SELECT * FROM genre_in_mv WHERE genre_id IN (445,446,447,448,449,450,451,452,453,454,455, 456, 458, 459, 460, 461, 462, 463, 464, 466, 467, 468, 471)'
    cursor.execute(sql)
    result = cursor.fetchall()
    #print(result)

    # genre_id_count = 501
    update_mv_set = set()

    for i in sorted(result):
        #print(i)
        genre_id = i[0]
        mv_id = i[1]
        if mv_id in update_mv_set:
            continue
        else:
            # print(genre_id in character_dict)
            if genre_id in character_dict:
                get_detail_info(mv_id)
                update_mv_set.add(mv_id)
                db.commit()
    db.close()


