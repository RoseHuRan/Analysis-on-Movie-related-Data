from requests import get
from bs4 import BeautifulSoup
import time

import pymysql
import json
import re

# 打开数据库连接
db = pymysql.connect("localhost", "root", "root", "csc3170")
cursor = db.cursor()

# Preparing the monitoring of the loop
start_time = time.time()

#change target year period
years_url = [str(i) for i in range(1999, 1989, -1)]

headers = {"Accept-Language": "en-US, en;q=0.5"}

def get_detail_info(link_str):
    detail_response = ''
    sql = ''
    while True:
        try:
            detail_response = get(link_str, headers=headers)
            break
        except Exception as e:
            print("Request error: ", e)
            continue

    try:
        detail_page_html = BeautifulSoup(detail_response.text, 'html.parser')
        info = json.loads(detail_page_html.find('script', type='application/ld+json').text)
        mv_name = info['name']
        mv_id = info['url'].split('/')[2]
        mv_publish_date = info.get('datePublished', None)
        mv_release_date = info.get('dateCreated', None)
        mv_runtime = info.get('duration', None)
        if 'aggregateRating' in info:
            mv_imdb_rating = info['aggregateRating']['ratingValue']
            mv_rating_count = info['aggregateRating']['ratingCount']
        else:
            mv_imdb_rating, mv_rating_count = None, None

        tmp = detail_page_html.find('div', class_='metacriticScore')
        mv_metascore = int(tmp.text) if tmp is not None else None
        mv_certificate = info.get('contentRating', None)
        mv_languages = detail_page_html.find('h4', text='Language:')
        if mv_languages:
            container = mv_languages.parent
            mv_languages = ''
            for lang in container.find_all('a'):
                mv_languages += lang.text + ' '
            mv_languages = mv_languages.strip()

        mv_budget = detail_page_html.find('h4', text='Budget:')
        if mv_budget:
            mv_budget = mv_budget.next_sibling.strip()

        mv_us_gross = detail_page_html.find('h4', text='Gross USA:')
        if mv_us_gross:
            mv_us_gross = mv_us_gross.next_sibling.strip().replace(',', '')

        # url format: /company/co{id}/
        mv_produces = []
        if 'creator' in info:
            for org in info['creator'] if type(info['creator']) == list else [info['creator']]:
                if org['@type'] == 'Organization':
                    mv_produces.append({'id': org['url'].split('/')[2]})

        mv_genres = []
        if 'genre' in info:
            for genre in info['genre'] if type(info['genre']) == list else [info['genre']]:
                mv_genres.append({'name': genre})

        mv_crews = []
        if 'actor' in info:
            for actor in info['actor'] if type(info['actor']) == list else [info['actor']]:
                mv_crews.append({'id': actor['url'].split('/')[2], 'name': actor['name'], 'position': 'actor'})

        if 'director' in info:
            for director in info['director'] if type(info['director']) == list else [info['director']]:
                mv_crews.append({'id': director['url'].split('/')[2], 'name': director['name'], 'position': 'director'})

        if 'creator' in info:
            for creator in info['creator'] if type(info['creator']) == list else [info['creator']]:
                if creator['@type'] == 'Person':
                    mv_crews.append(
                        {'id': creator['url'].split('/')[2], 'name': creator['name'], 'position': 'creator'})

        mv_keywords = info.get('keywords', None)

        # movie table
        sql = "SELECT * FROM movie WHERE imdb_id='%s'" % mv_id
        if cursor.execute(sql) != 0:
            return False
        sql = "INSERT INTO movie VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (
        mv_id, mv_name, mv_metascore, mv_imdb_rating, mv_rating_count, mv_budget, mv_us_gross, mv_release_date,
        mv_publish_date, mv_certificate, mv_runtime, mv_languages, mv_keywords))

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

        # production_co table
        for co in mv_produces:
            sql = "SELECT * FROM production_co WHERE pc_id='%s'" % co['id']
            if cursor.execute(sql) == 0:
                sql = "INSERT INTO production_co(pc_id) VALUES ('%s')" % co['id']
                cursor.execute(sql)
            sql = "SELECT * FROM co_produce_mv WHERE mv_id='%s' and co_id='%s'" % (mv_id, co['id'])
            if cursor.execute(sql) == 0:
                sql = "INSERT INTO co_produce_mv VALUES ('%s','%s')" % (mv_id, co['id'])
                cursor.execute(sql)

        # crew table
        for crew in mv_crews:
            sql = "SELECT * FROM crew WHERE crew_id='%s'" % crew['id']
            if cursor.execute(sql) == 0:
                sql = "INSERT INTO crew VALUES ('%s','%s')" % (crew['id'], re.escape(crew['name']))
                cursor.execute(sql)
            sql = "SELECT * FROM crew_in_mv WHERE crew_id='%s'and mv_id='%s' and crew_position='%s'" % (
            crew['id'], mv_id, crew['position'])
            if cursor.execute(sql) == 0:
                sql = "INSERT INTO crew_in_mv VALUES ('%s','%s','%s')" % (crew['id'], mv_id, crew['position'])
                cursor.execute(sql)

        print("---------------------finish %d--------------------" % cnt)
        db.commit()
    except Exception as e:
        print("inner: ", e, " --end")
        with open('res/log.txt', 'a') as f:
            f.write(mv_id+'\n')

        print(sql)
        print(mv_id)
        db.rollback()
        # input()


if __name__ == '__main__':

    total = {1999: 3872, 1998: 3726, 1997: 3593, 1996: 3462, 1995: 3431, 1994: 3351, 1993: 3434, 1992: 3559, 1991: 3629, 1990: 3766,
             1989: 3508, 1988: 3616, 1987: 3515, 1986: 3395, 1985: 3408, 1984: 3447, 1983: 3372, 1982: 3342, 1981: 3297, 1980: 3310}
    for i in total: total[i] = int(total[i]*0.1)
    # For every year in the interval 2000-2017
    for year_url in years_url:
        try:
            requests = 0

            result = total[int(year_url)]

            # Make a get request
            while requests*250 < result:
                try:
                    response = get('https://www.imdb.com/search/title?title_type=feature&release_date=' + year_url + '-01-01,'+ year_url + '-12-31'
                                       '&sort=num_votes,desc&count=250&start='+ str(requests*250+1), headers=headers)
                except Exception as e:
                    print("Outer Request Error: ", e)
                    continue

                # Parse the content of the request with BeautifulSoup
                page_html = BeautifulSoup(response.text, 'html.parser')

                # Select all the 250 movie containers from a single page
                mv_containers = page_html.find_all('div', class_='lister-item mode-advanced')

                # For every movie of these 250
                cnt = 0
                for container in mv_containers:
                    cnt += 1
                    link_str = 'https://www.imdb.com' + container.h3.a['href']
                    mv_id = container.h3.a['href'].split('/')[2]
                    sql = "SELECT * FROM movie WHERE imdb_id='%s'" % mv_id
                    if cursor.execute(sql) == 0:
                        get_detail_info(link_str)
                    else:
                        print("skip: ", mv_id)

                # Monitor the requests
                requests += 1
                elapsed_time = time.time() - start_time
                print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))

                # Throw a warning for non-200 status codes
                if response.status_code != 200:
                    print('WARNING: Request: {}; Status code: {}'.format(requests, response.status_code))
        except Exception as e:
            with open('res/log.txt', 'a') as f:
                f.write("year error: %s\n" % year_url)

    db.close()
