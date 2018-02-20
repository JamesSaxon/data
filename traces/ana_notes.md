## Precision

- The most obvious thing is that there is a totally bi-modal distribution in the location precision by app.  All save three of the 35 apps in my test set up (65M pings) had > 90% or < 10% imprecise.  My guess is that this means that certain apps "aren't really location-aware."  They get occasionally get an emac address from a router, but they're not approved on the phone to use location.
- The Wifi is a good insight.  I hypothesized that these are Metra cars, which would get nuts numbers of people connecting ... and ~Millennium Station makes sense.  I tested this by looking at the home locations (pings with precision != 0 from 1am to 5am) to see if these were disproportionately suburbanites more-likely to use the Metra.  No dice.
- On the other hand, there is huge variation (orders of magnitude) in the time trend in the fraction of precision 0 codes across the month.  But I'm just playing with 65M rows to start.  I don't know how the csv's are set up -- random other otherwise -- so I may just be seeing their structure.  I'll check this again, with the full dataset.


