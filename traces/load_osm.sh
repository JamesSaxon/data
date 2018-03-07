#!/bin/bash

wget 'http://overpass-api.de/api/interpreter?data=(way["railway"~"^subway$|^rail$"](41.57,-88.29,42.01,-87.30);way["highway"~"motorway|motorway_link|motorway_junction|trunk|trunk_link|primary|primary_link|secondary"](41.57,-88.29,42.01,-87.30););(._;>;);out;' -O chicago_highways.osm
wget 'http://overpass-api.de/api/interpreter?data=(way["amenity"="school"](41.57,-88.29,42.01,-87.30););(._;>;);out;' -O chicago_schools.osm

osm2pgsql -E 3528 -G -s -U jsaxon -d network -c chicago_highways.osm
psql network << EOD

	DROP TYPE osm_way_enum;
  CREATE TYPE osm_way_enum AS ENUM ('motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link', 'secondary', 'secondary_link', 'rail', 'subway');

  CREATE TABLE highways (osm_id INTEGER, name TEXT, osm_way osm_way_enum);
  ALTER TABLE highways ADD PRIMARY KEY (osm_id);
  SELECT AddGeometryColumn('highways', 'geom', 3528, 'LINESTRING', 2);
  INSERT INTO highways (osm_id, name, osm_way, geom) SELECT osm_id, name, (CASE WHEN railway IN ('rail', 'subway') THEN railway ELSE highway END)::osm_way_enum AS osm_type, way AS geom FROM planet_osm_line;
  CREATE INDEX ON highways USING GIST (geom);

  INSERT INTO highways (osm_id, name, osm_type, geom) SELECT osm_id, name, (CASE WHEN railway IS NULL THEN highway ELSE railway END)::osm_way AS osm_type, way AS geom FROM planet_osm_line;

EOD


osm2pgsql -E 3528 -G -s -U jsaxon -d network -c chicago_schools.osm
psql network << EOD

  CREATE TABLE schools (osm_id INTEGER, name TEXT);
  ALTER TABLE schools ADD PRIMARY KEY (osm_id);
  SELECT AddGeometryColumn('schools', 'geom', 3528, 'MULTIPOLYGON', 2);
  INSERT INTO schools (osm_id, name, geom) SELECT osm_id, name, ST_Multi(way) FROM planet_osm_polygon;
  CREATE INDEX ON schools USING GIST (geom);

EOD


psql network << EOD

  DROP TABLE planet_osm_line;    
  DROP TABLE planet_osm_nodes;   
  DROP TABLE planet_osm_point;   
  DROP TABLE planet_osm_polygon; 
  DROP TABLE planet_osm_rels;    
  DROP TABLE planet_osm_roads;   
  DROP TABLE planet_osm_ways;    

EOD


