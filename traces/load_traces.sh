#!/bin/bash

make_temporary_table="
CREATE TEMPORARY TABLE temp (
  app     SMALLINT, 
  person  TEXT,
  os      VARCHAR(4),
  lat     DOUBLE PRECISION,
  lon     DOUBLE PRECISION,
  pre     INTEGER,
  time    BIGINT
);
"

copy_from_temp="
INSERT INTO traces
  (person, time, os, app, prec, geoid, loc, highway)
(
  SELECT 
    person, to_timestamp(time) AT TIME ZONE 'America/Chicago',
    CASE
         WHEN os = 'AAID' THEN 'android'::system
         WHEN os = 'IDFA' THEN     'ios'::system
    END,
    app, pre, geoid, loc, highway
  FROM temp
);
"

psql traces < trace_schema.sql


for x in data/trace_a[a-m]; do

  echo $x

  psql -d traces <<< "
  
    $make_temporary_table
    \\copy temp FROM '$x' CSV;

    SELECT AddGeometryColumn('temp', 'loc', 3528, 'POINT', 2);
    ALTER TABLE temp ADD COLUMN geoid BIGINT;
    ALTER TABLE temp ADD COLUMN highway BOOLEAN DEFAULT FALSE;

    UPDATE temp SET loc = ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4269), 3528);
    -- CREATE INDEX loc_gidx ON traces USING GIST (loc);

    UPDATE temp SET geoid = tracts15.geoid FROM tracts15 WHERE ST_Contains(geom, loc);
    UPDATE temp SET highway = TRUE FROM highways WHERE ST_DWithin(geom, loc, 10);

    $copy_from_temp

  "

done

