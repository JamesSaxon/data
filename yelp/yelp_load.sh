#!/bin/bash 

psql -d yelp -U jsaxon << EOD

  DROP TABLE business;
  CREATE TABLE business ("id" text PRIMARY KEY, "neighborhood" text, "address" text, "city" text, "state" text, "postal_code" text, "latitude" float, "longitude" float, "review_count" int, "categories" text[]);
  \\copy business FROM '/media/jsaxon/brobdingnag/data/yelp/yelp_business.csv' DELIMITER ',' CSV NULL as 'NULL';

  DROP TABLE users;
  CREATE TABLE users ("id" text PRIMARY KEY, "review_count" int, "friends" text[]);
  \\copy users FROM '/media/jsaxon/brobdingnag/data/yelp/yelp_user.csv' DELIMITER ',' CSV NULL as 'NULL';

  CREATE TEMPORARY TABLE temp ("business" text, "uid" text);
  \\copy temp FROM '/media/jsaxon/brobdingnag/data/yelp/yelp_tip.csv' DELIMITER ',' CSV NULL as 'NULL';

  DROP TABLE tip;
  CREATE TABLE tip (id SERIAL PRIMARY KEY, "business" text, "uid" text);
  INSERT INTO TIP (business, uid) SELECT business, uid FROM temp;
  DROP TABLE temp;

  DROP TABLE review;
  CREATE TABLE review ("id" text PRIMARY KEY, "uid" text, "business" text);
  \\copy review FROM '/media/jsaxon/brobdingnag/data/yelp/yelp_review.csv' DELIMITER ',' CSV NULL as 'NULL';


EOD


