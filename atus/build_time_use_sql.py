#!/usr/bin/env python 

from bls_atus_fields import *

def download_atus_data():

  import wget, os
  
  base_address = "http://www.bls.gov/tus/special.requests/atus{}.zip"
  requisite_files = ["resp_2015", "rost_2015", "act_2015", "sum_2015", 
                     "who_2015", "cps_2015", # "rostec_1115", 
                     "wgts_2015"]

  requisite_files = ["resp_2015", "rost_2015", "act_2015", "sum_2015", 
                     "who_2015", "cps_2015", # "rostec_1115", 
                     "wgts_2015"]
  
  for f in requisite_files:
    wget.download(base_address.format(f))
    os.system("unzip atus{}.zip -d atus/ atus{}.dat".format(f, f))

# download_atus_data()


sqlite_file = 'atus.sqlite'

# Connecting to the database file
import sqlite3, csv
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()


def create_atus_table(name, pk, fields, col_list, filename):

  print(fields)
  cur.execute('CREATE TABLE {name} ({cols}, PRIMARY KEY ({pk}))'\
              .format(name = name, cols = ", ".join(fields), pk = ", ".join(pk), ))
  print('CREATE TABLE {name} ({cols}, PRIMARY KEY ({pk}))'\
                    .format(name = name, cols = ", ".join(fields), pk = ", ".join(pk), ))
  
  with open(filename, 'r') as f:
    reader = csv.reader(f)
    header = next(reader) # get the header
    header_idx = [header.index(k) for k, v in col_list]
  
    query = "INSERT INTO {name} ({cols}) VALUES ({vals});".format(
                     name = name, 
                     cols = ", ".join([v for k, v in col_list]),
                     vals = ", ".join(["?" for k, v in col_list]))
  
    to_db = []
    for ri, row in enumerate(reader):
      to_db.append([row[i] for i in header_idx])
  
    cur.executemany(query, to_db)

  print("Finished", filename)



def cps_years_education():

  cur.execute("ALTER TABLE cps ADD years_education INTEGER;")

  query = '''UPDATE cps SET years_education=(CASE
             WHEN educational_attainment = 31 THEN 0
             WHEN educational_attainment = 32 THEN 3
             WHEN educational_attainment = 33 THEN 6
             WHEN educational_attainment = 34 THEN 8
             WHEN educational_attainment = 35 THEN 10
             WHEN educational_attainment = 36 THEN 11
             WHEN educational_attainment = 37 THEN 12
             WHEN educational_attainment = 38 THEN 13
             WHEN educational_attainment = 39 THEN 13
             WHEN educational_attainment = 40 THEN 13 + years_in_college - 1
             WHEN educational_attainment = 41 THEN 15
             WHEN educational_attainment = 42 THEN 15
             WHEN educational_attainment = 43 THEN 17
             WHEN educational_attainment = 44 THEN 17 + (CASE
               WHEN duration_of_masters > 0 THEN duration_of_masters
               ELSE 1 END)
             WHEN educational_attainment = 45 THEN 21
             WHEN educational_attainment = 46 THEN 21
             ELSE -1 END
             );'''

  cur.execute(query);


create_atus_table("roster",      roster_pk,     roster_fields,     roster_list, "atus/atusrost_2015.dat")
create_atus_table("respondents", respondent_pk, respondent_fields, respondent_list, "atus/atusresp_2015.dat")
create_atus_table("activities",  activity_pk,   activity_fields,   activity_list, "atus/atusact_2015.dat")
create_atus_table("cps",         cps_pk,        cps_fields,        cps_list, "atus/atuscps_2015.dat")

cps_years_education()

conn.commit()
conn.close()


