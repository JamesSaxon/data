DROP TABLE IF EXISTS traces;
DROP TYPE IF EXISTS system;

CREATE TYPE system AS ENUM ('ios', 'android');

CREATE TABLE traces (
   person  VARCHAR(72),
   time    TIMESTAMP,
   os      SYSTEM,
   app     SMALLINT, 
   prec    INTEGER,
   geoid   BIGINT
);

SELECT AddGeometryColumn('traces', 'loc', 3528, 'POINT', 2);
ALTER TABLE traces ADD COLUMN highway BOOLEAN;

-- CREATE INDEX person_idx ON traces (person);
-- CREATE INDEX loc_gidx ON traces USING GIST (loc);


