CREATE TABLE movie_sta AS
SELECT g.mv_id, m.publish_date, g.genre_id, e.genre_name, m.metascore, m.imdb_rating, m.vote_count, m.budget, m.us_gross, m.languages, m.keywords, c.co_id FROM movie m, genre_in_mv g, genre e, co_produce_mv c
WHERE  imdb_id = g.mv_id and imdb_id = c.mv_id and g.genre_id = e.genre_id and length(e.genre_name)>1 and m.publish_date is not null and m.imdb_rating is not null and m.metascore > 0;

ALTER TABLE crew_in_mv
add column star int default 0;

SET SQL_SAFE_UPDATES = 0;
UPDATE crew_in_mv SET star=1 WHERE crew_id  in (select id from 1000_actor_rank);
SET SQL_SAFE_UPDATES = 1;

create view star_count as
select mv_id, count(*) as star_count
from crew_in_mv
where star = 1
group by mv_id;

create table movie_sta_star as
select m.mv_id, publish_date, genre_id, genre_name, metascore as med_rating, imdb_rating, vote_count, budget, us_gross as revenue, languages, keywords, co_id, coalesce(s.star_count,0) as star_count
from movie_sta m
left join star_count s
on m.mv_id = s.mv_id;

CREATE VIEW genre_trend AS
SELECT genre_id, count(*) as num
FROM movie_2011
GROUP BY genre_id
ORDER BY count(*) DESC;

SELECT d.genre_id, g.genre_name, d.num
FROM genre g, genre_trend d
WHERE g.genre_id = d. genre_id AND length(g.genre_name)>1
ORDER BY num DESC;
