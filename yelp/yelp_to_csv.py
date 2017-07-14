#!/usr/bin/env python 

import json

for ds, fields in [
                   ["business", ["business_id", "neighborhood", "address", "city", "state", "postal_code", "latitude", "longitude", "review_count", "categories"]],
                   ["user",     ["user_id", "review_count", "friends"]],
                   ["tip",      ["business_id", "user_id"]],
                   ["review",   ["review_id", "user_id","business_id"]],
                  ]:

    with open("yelp_{}.csv".format(ds), "w") as out:

        for il in open("yelp_academic_dataset_{}.json".format(ds), "r"):
            js = json.loads(il)

            for arrf in ["categories", "friends"]:
                if arrf in fields:
                   if not js[arrf]: js[arrf] = []
                   cat = "\"\",\"\"".join(js[arrf])
                   cat = "{\"\"" + cat + "\"\"}"
                   js[arrf] = cat

            ol = ",".join(["\"{}\"".format(str(js[fi])) for fi in fields])
            ol = ol.replace ("\"[", "{").replace("]\"", "}")
            ol = ol.replace(",\"\",", ",NULL,")
            out.write(ol + "\n")


