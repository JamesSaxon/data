#!/usr/bin/env python 

import sys

import re
import pprint

from zipfile import ZipFile as zf
from csv import DictReader as dictread
from io import TextIOWrapper as tio
zopen = lambda x, y: tio(zf(x, 'r').open(y))




##########################################################
##########################################################

cya_id = ["MPUBID", "CPUBID"]
cya_static = ["CSEX", "CRACE", "CMOB", "CYRB", "BTHORDR", "MAGEBIR", "FSTYRAFT",
              "GED", "HSDIPLOMA", "BS", "BA", "MASTERS", "PHD", "HSTDEGREE_DLI", "HSTDEGREE2012",
              "EVERCOHAB", "EVERMARRY",
              "AGE1B", "AGE2B", "AGE3B", 
              "PRE0010", "PRE0011", "PRE0012", "PRE0013", "PRE0077"]

cya_static_dates = ["1STCOHAB", "1STMARR", "C1DOB", "C2DOB", "C3DOB"]

# Can review/skim this after a first pass.
# Probably want PX variables where available.
cya_psych = ['CSAGE', 'COGNA', 'COGNB', 'COGNC', 'COGND', 'COGNP', 'COGNZ', 'EMOTA', 'EMOTB', 'EMOTC', 'EMOTD', 'EMOTP', 'EMOTZ', 'HOMEA', 'HOMEB', 'HOMEC', 'HOMED', 'HOMEFA', 'HOMEFB', 'HOMEFC', 'HOMEFD', 'HOMEP', 'HOMEZ', 'ACTVTY', 'AFFECT', 'COMPLY', 'DIFFIC', 'FEAR', 'FRIEND', 'FRIENDF', 'INSECUR', 'NEGATV', 'PREDCT', 'SOCIAB', 'ANTI', 'ANTIP', 'ANTIPX', 'ANTIZ', 'ANTIZX', 'ANX', 'ANXP', 'ANXPX', 'ANXZ', 'ANXZX', 'BPEXTP', 'BPEXTR', 'BPEXTZ', 'BPI', 'BPIENRL', 'BPINTP', 'BPINTR', 'BPINTZ', 'BPIP', 'BPIPX', 'BPIZ', 'BPIZX', 'BPTOTP', 'BPTOTR', 'BPTOTZ', 'DEP', 'DEPP', 'DEPPX', 'DEPZ', 'DEPZX', 'HEAD', 'HEADP', 'HEADPX', 'HEADZ', 'HEADZX', 'HYPR', 'HYPRP', 'HYPRPX', 'HYPRZ', 'HYPRZX', 'PEER', 'PEERP', 'PEERPX', 'PEERZ', 'PEERZX', 'PEARLIN_IRT_SCORE_REVISED', 'PEARLIN_ZSCORECW', 'PEARLIN_ZSCORECW_PERCENTILE', 'ROSENBERG_ZSCORECW', 'ROSENBERG_ZSCORECW_PERCENTILE', 'SPPCG', 'SPPCGF', 'SPPCGI', 'SPPCS', 'SPPCSF', 'SPPCSI', 'PPVT', 'PPVTMO', 'PPVTP', 'PPVTZ', 'VERBA', 'VERBAP', 'VERBAZ', 'VERBC', 'VERBCP', 'VERBCZ', 'DIGIT', 'DIGITB', 'DIGITF', 'DIGITZ', 'LOCA', 'LOCAI', 'LOCAP', 'LOCAZ', 'MOTO', 'MOTOP', 'MOTOPX', 'MOTOZ', 'MOTOZX', 'COMP', 'COMPP', 'COMPZ', 'RECOG', 'RECOGP', 'RECOGZ', 'MATH', 'MATHP', 'MATHZ']

cya_self = ['CSAS011A', 'CSAS011B', 'CSAS011C', 'CSAS013A', 'CSAS013B', 'CSAS013C', 'CSAS019A', 'YA98079A', 'YA98079G', 'YA98084', 'YA98085G', 'YA98086', 'YASR-2A', 'YASR-3A', 'YASR-47A', 'YASR-48', 'YASR-54', 'YASR-62A', 'YASR-63', 'YASR-64B', 'YASR-66']

cya_yearly = ["AGEINT", "CSAMWT", "YAWEIGHT", "AGECH", 'DADHM', 'DADLIV', 'DADSEE', 'DADVIS', 'COHAB', 'MARSTAT', 'HGC', 'Q4-75', 'Q4-76', 'REGION', 'URBAN-RURAL']

##########################################################
##########################################################




class Q:

    def __init__(self, q, n):

        self.q = q
        self.n = n
        self.t = dict()

    def __iter__(self):

        return iter(sorted(list(self.t.keys())))

    def __getitem__(self, t):
        
        return self.t[t]

    def __contains__(self, k):

        return k in self.t

    def __str__(self):

        return "{} // {}".format(self.q, list(self.t.keys()))

    def __repr__(self):

        return self.n + " >>>> " + str(sorted(list(self.t.keys())))

    def setv(self):

      self.v = list(self.t.values())[0]

    def valid(self, ti, row, cut = -3):

        return (ti in self) and int(row[self[ti]]) > cut


class P:

    cuid, ruid = 0, 0

    def __init__(self, id = 0, outcome = "C", y = -1, m = -1, ry = -1, created = False):

        self.ry = ry

        if y < 0: y = ry
        self.y = y
        self.m = m
        self.id = id
        self.out = outcome
        self.mwanted = -5
        self.fwanted = -5 
        self.hadusedc = -5 
        self.usingco = -5 

        self.ystarted = -1
        self.mstarted = -1

        self.mult = False

        self.matched = False
        self.nomatch = False

        self.created = created
        if created: 
          P.cuid += 1
          self.uid = P.cuid 
        else:
          P.ruid +=1
          self.uid = P.ruid + 100

    def __lt__(self, other):

        if self.y != other.y: return self.y < other.y
        return self.m < other.m

    def __sub__(self, other):
        
        return (self.y * 12 + self.m) - (other.y * 12 + other.m)

    def __eq__(self, other):
      
        return (self.y == other.y) and (self.m == other.m)

    def __eq__(self, other):
      
        return (self.y == other.y) and (self.m == other.m)

    def __str__(self):

        sym_match = ""
        if self.created: sym_match = "✘"
        if self.matched: sym_match = "✔"
        if self.nomatch: sym_match = "-"

        return "{}{:d}  {:5d}/{:d}  WANTED={:4}    FATHER WANTED={:4}     HAD USED CONTRACEP={:4}    USING CONTRACEP={:4}    ({:2}/{:4})   {:02d} {:s} {}".\
               format(self.out, self.id, self.m, self.y, self.mwanted, self.fwanted, self.hadusedc, self.usingco, self.mstarted, self.ystarted,
                      self.uid, "[Mult]" if self.mult else "", sym_match)

    def csv(self, case):

      edate, sdate = "", ""

      if self.ystarted > 0: sdate = "{:04d}-{:02d}-01".format(self.ystarted, self.mstarted if self.mstarted > 0 else 1)
      elif self.y > 0:

        moffset = 9
        if self.out in "AM": moffset = 3

        m, y = 1, self.y
        if self.m > 0:
            m = 12 + self.m
            m -= moffset
            m = m%12
            if not m: m = 12
            
            if moffset >= self.m: y -= 1
                
        sdate = "{:04d}-{:02d}-01".format(y, m)


      if self.y > 0: edate = "{:04d}-{:02d}-01".format(self.y, self.m if self.m > 0 else 1)


      outcome = self.out
      if outcome == "C": outcome = "L"

      match = 0
      if self.matched: match = 2
      if self.nomatch: match = 1

      return "{case},{p.uid},{outcome},{edate},{sdate},{p.mwanted:d},{p.fwanted:d},{p.hadusedc:d},{p.usingco:d},{match}".format\
             (case = case, p = self, sdate = sdate, edate = edate, outcome = outcome, match = match)


    def intentions(self, q74 = None, q78 = None, q79 = None, q80 = None, q81 = None, q82 = None):

        if q74 > 0:
            self.id = q74
            self.out = "C"

        if q78 == 1: self.hadusedc = True
        elif q78 < -3: self.hadusedc = -4
        else: self.hadusedc = False

        if q78 == 0 or q79 == 1: self.usingco = False
        elif q78 < -3: self.usingco = -4
        else: self.usingco = True

        if q80 == 1: self.mwanted = 1
        else: self.mwanted = q81

        self.fwanted = q82

    def start(self, m, y):

        self.mstarted = m
        self.ystarted = rect_year(y)

    def end_from_start(self):

        if self.m > 0 or self.mstarted < 0: return

        offset = 9
        if self.out in "AMS":
          offset = 3

        self.m = self.mstarted + offset
        self.y = self.ystarted
        if self.m > 12:
          self.m -= 12
          self.y += 1

    def merge(self, other):

        if self.m <= 0:
          self.m = other.m
          self.y = other.y

        if self.id       <= 0: self.id       = other.id
        if self.out     == "": self.out      = other.outcome

        if self.mwanted  <  0: self.mwanted  = other.mwanted
        if self.fwanted  <  0: self.fwanted  = other.fwanted
        if self.hadusedc <  0: self.hadusedc = other.hadusedc
        if self.usingco  <  0: self.usingco  = other.usingco

        if self.ystarted <  0: self.ystarted = other.ystarted
        if self.mstarted <  0: self.mstarted = other.mstarted


global total_records, non_matching_kids
total_records, non_matching_kids = 0, 0
def match_em(cre, rec):

  cre.sort()
  rec.sort()

  global total_records, non_matching_kids
  total_records += 1

  nkids_cre = sum(p.out == "C" for p in cre)
  nkids_rec = sum(p.out == "C" for p in rec)

  # Merge duplicate children in the record (separated by < 6 months).
  if nkids_cre != nkids_rec:

    kids_rec = [pi for pi, p in enumerate(rec) if p.out == "C"]

    remove = []
    # for kra in kids_rec: print(rec[kra])
    for ki, kra in enumerate(kids_rec):
      for krb in kids_rec[ki+1:]:
        if abs(rec[kra] - rec[krb]) < 6:
          # print("!! Merging records -- ")
          # print(rec[kra])
          # print(rec[krb])
          rec[kra].merge(rec[krb])
          remove.append(krb)

    if remove:
      nkids_rec -= len(remove)
      # do it backwards to keep indices intact.
      remove = sorted(list(set(remove)), reverse = True)
      for r in remove: del rec[r]


  kids_cre = [pi for pi, p in enumerate(cre) if p.out == "C"]
  kids_rec = [pi for pi, p in enumerate(rec) if p.out == "C"]

  if nkids_cre == nkids_rec:

    for ci in range(nkids_cre):
      cre[kids_cre[ci]].merge(rec[kids_rec[ci]])
      cre[kids_cre[ci]].matched = True
      rec[kids_rec[ci]].matched = True

  elif any(p.mult for p in cre if p.out == "C") and \
       nkids_cre > nkids_rec:

    for ci in kids_cre:
      for ri in kids_rec:
        if abs(cre[ci] - rec[ri]) < 6 and \
           not cre[ci].matched:
          cre[ci].merge(rec[ri])
          cre[ci].matched = True
          rec[ri].matched = True
          break

  else:

    print("WARNING: {} v. {} children".format(nkids_cre, nkids_rec))
    non_matching_kids += 1

    for ci in kids_cre:
      for ri in kids_rec:
        if abs(cre[ci] - rec[ri]) < 3 and \
           not rec[ri].matched:
          cre[ci].merge(rec[ri])
          cre[ci].matched = True
          rec[ri].matched = True
          break




  # Next try abortions, which (usually)
  # have specific dates.
  for ar in rec:
    if ar.out != "A": continue

    for ac in cre:
      if ac.out != "A": continue

      if abs(ac - ar) < 3 and \
         not ac.matched:
        ac.merge(ar)
        ac.matched = True
        ar.matched = True
        break

    # If it's matched, we're done.
    if ar.matched: continue

    # Otherwise, if there's a created copy
    # without a date, let that match.
    for ac in cre:
      if ac.out != "A": continue

      if ac.y < 0 and ac.m < 0 and \
         not ac.matched:
        ac.merge(ar)
        ac.matched = True
        ar.matched = True
        break


  # Next try abortions, which (usually)
  # have specific dates.
  for mc in cre:

    if mc.out != "M": continue

    for mr in rec:

      if mr.out not in "SM": continue
      if mr.matched: continue

      # miscarriages are recorded at
      # 2-yr intervals in the created hist.
      # print(" ++ ")
      # print(mr)
      # print(mc)
      # print(mr - mc)
      if 13 > mr - mc > -26 or \
         (mc.y == 1984 and mr.y <= 1984):
        mc.merge(mr)
        mc.matched = True
        mr.matched = True
        break

  for p in cre:
    if not p.matched and p.out in "MA" and p.ry >= 1992:
      p.nomatch = True

  cre.sort()
  rec.sort()



def rect_year(y, ti = -1):

  if y < 0: return ti

  if y < 1900: y += 1900
  if y < 1950: y += 100

  return y


def attribute_list_79(line, f):

    r = line[f[0]:f[1]].strip().replace(".", "")
    t = line[f[1]:f[2]].strip()
    n = line[f[2]:f[3]].strip()
    q = line[f[3]:].strip()

    try: t = int(t)
    except ValueError: pass

    if "HRS_WORKED_WK_NUM" in q: t = int(q[17:])
    if "STATUS_WK_NUM"     in q: t = int(q[13:])
    if "RELSPPTR"          in q:
        yr = int(q[8:])
        t = yr + (1900 if yr > 50 else 2000)

    if "NUMSPPTR"          in q:
        yr = int(q[8:])
        t = yr + (1900 if yr > 50 else 2000)

    # Some fixes and collapsing.
    q = re.sub(r'FFER-3$', r'FER-3', q)
    q = re.sub(r'MFER-7$', r'FER-3', q)

    q = re.sub(r'MFER-10$', r'Q9-63', q)

    q = re.sub(r'Q9-158C.1', 'Q9-158C.01', q)

    q = re.sub(r'Q9-165F_2.0(\d)~M', r'ABORT\1MO', q)
    q = re.sub(r'Q9-165F_2.0(\d)~Y', r'ABORT\1YR', q)

    q = re.sub(r'FFER-1_21_D', 'FFER-1_2_D', q)
    q = re.sub(r'FFER-3_22', 'FFER-3_2', q)

    if q in ("FFER-140", "MFER-14", "MFER-29"): q = "Q9-66"

    if re.search(r'MISCAR\d\d', q): 
        yr = int(q[6:])
        t = yr + (1900 if yr > 50 else 2000)
        q = 'MISCAR_'

    if "FFER-3_" in q and t < 1984: q += "_"

    q = re.sub(r'Q9-71E_1', r'Q9-71E.01', q)
    q = re.sub(r'Q9-77[\._]([12])[~_]([MY])$', r'Q9-77.0\1~\2', q)
    q = re.sub(r'(Q9-[78][0-247-9])_', r'\1.', q)
    q = re.sub(r'(Q9-[78][0-247-9].)(\d)$', r'\g<1>0\g<2>', q)
    q = re.sub(r'WOMENS-ROLES~', 'WOMENS-ROLES_', q)
    q = re.sub(r'NET_WORTH_\d\d', 'NET_WORTH', q)
    q = re.sub(r'HGCREV\d\d', 'HGCREV', q)
    q = re.sub(r'ENROLLMTREV\d\d', 'ENROLLMTREV', q)
    q = re.sub(r'RELSPPTR\d\d', 'RELSPPTR', q)
    q = re.sub(r'NUMSPPTR\d\d', 'NUMSPPTR', q)
    q = re.sub(r'(C[0-9]+RES)\d\d', r'\1', q)
    q = re.sub(r'(HRS_WORKED_WK_NUM)\d+', r'\1', q) 
    q = re.sub(r'(STATUS_WK_NUM)\d+', r'\1', q) 

    return r, t, n, q


def attribute_list_cya(line, f):

    r = line[f[0]:f[1]].strip().replace(".", "")
    t = line[f[1]:f[2]].strip()
    n = line[f[2]:f[3]].strip()
    q = line[f[3]:].strip()

    try: t = int(t)
    except ValueError: pass

    q = re.sub("BPEXTS1994", "BPEXTZ1994", q)
    q = re.sub("BPINTS1994", "BPINTZ1994", q)
    q = re.sub(r'(SPPC[GS]I)\d+', r'\1', q)
    q = re.sub("CSAMWT.*", "CSAMWT", q) # CAREFUL -- DON'T USE UNREV WEIGHTS IN CHECK OUT!!
    q = re.sub("YA..WEIGHT.*", "YAWEIGHT", q) # CAREFUL -- DON'T USE UNREV WEIGHTS IN CHECK OUT!!
    q = re.sub("URBAN-RURAL_REV", "URBAN-RURAL", q) # CAREFUL NOT TO HAVE UNREV IN 2004, 2006 CHECKOUT!

    for v in ["CRES", "C\dRES", "DAD[A-Z]+", "COHAB", "HGC",
              "MARSTAT", "REGION", 
              "AGECH", "AGEINT",

              # The 1986-1988 psychometric variables...
              # for a list: 
              # for s in CSAGE CSAMWT 'HOME INVENTORY' 'HOW MY CHILD USUALLY ACTS' 'BEHAVIOR PROBLEMS INDEX' PEARLIN ROSENBERG SPP PPVT VERBAL 'DIGIT SPAN' 'LOCA' BODY MOTO 'PIAT READING' 'PIAT MATH'; do sed "s/{/ /g" blah | grep "$s"; done > psy
              "CSAGE", "ACTVTY", "AFFECT",
              "ANTI[PZ]*X*", "ANX[PZ]*X*", "BODY[IPZ]*",
              "BODY[IPZ]*", "BPI[PZ]*X*", "BPIENRL", "BPTOT[RPZ]",
              "BPEXT[RPZ]", "BPINT[RPZ]", 
              "COGN[ABCDPZ]", "COMP[PZ]*", "COMPLY", "DEP[PZ]*[X]*",
              "EMOT[ABCDPZ]", "HOME[F]*[ABCDPZ]", 
              "DIFFIC", "DIGIT[ZFB]*", "FEAR", "FRIEND[F]*", "HEAD[PZ]*[X]*", 
              "HYPR[PZ]*[X]*", "INSECUR", "LOCA[IPZ]*",
              "MATH[PZ]*", "NEGATV",
              "MOTO[PZ]*[X]*", "PEER[PZ]*[X]*", "PREDCT", "PPVT[PZ]*", "PPVTMO",
              "RECOG[PZ]*", "VERB[AC][PZ]*",
              "SOCIAB", "SPPC[GS][F]*"
             ]:
      q = re.sub(r'^({})\d+$'.format(v), r'\1', q)

    if q in ['CS926527', 'CS942111', 'CS960411', 'CS98011A']: q = 'CSAS011A'
    if q in ['CS926531', 'CS942127', 'CS960427', 'CS98013A']: q = 'CSAS013A'
    if q in ['CS926535', 'CS942113', 'CS960413', 'CS98011B']: q = 'CSAS011B'
    if q in ['CS926539', 'CS942129', 'CS960429', 'CS98013B']: q = 'CSAS013B'
    if q in ['CS942131', 'CS960431', 'CS98013C']: q = 'CSAS011B'
    if q in ['CS942115', 'CS960415', 'CS98011C']: q = 'CSAS011C'

    if q in ['CS884339', 'CS906769', 'CS927015', 'CS942915', 'CS961234', 'CS98CC1A']: q = 'YASR-48'
    if q in ['CS942153', 'CS960453', 'CS98018A', 'CSAS018A']: q = 'YASR-2A'
    if q in ['CS942211', 'CS960511', 'CS98019A']: q = 'CSAS019A'
    if q in ['YA940627', 'YA960559', 'YA98078']: q = 'YASR-54'

    if q in ['YA940629', 'YA960561']: q = 'YA98079A'
    if q in ['YA940641', 'YA960573']: q = 'YA98079G'
    if q in ['YA940659', 'YA960623']: q = 'YA98084'
    if q in ['YA940723', 'YA960637']: q = 'YA98085G'
    if q in ['YA940729', 'YA960643']: q = 'YA98086'

    if q in ['YA940937', 'YA960837', 'YA98099']: q = 'YASR-62A'
    if q in ['YA940847', 'YA960747', 'YA98095']: q = 'YASR-63'
    if q in ['YA940849', 'YA960749', 'YA98096']: q = 'YASR-64B'
    if q in ['YA940947', 'YA960847', 'YA98102']: q = 'YASR-66'

    return r, t, n, q




def get_var_dict(ifile = "nlsy79_1", child = False):

    f = []
    vd = {}
    for line in zopen(ifile + ".zip", ifile + ".sdf"):
    
        if "Description" in line:
            f = [0]
            f.append(line.find("Year"))
            f.append(line.find("Variable"))
            f.append(line.find("Question"))
            continue
    
        if "----" in line: continue
    
        if f:
            if not child:
              r, t, n, q = attribute_list_79(line, f)
            else: 
              r, t, n, q = attribute_list_cya(line, f)
    
            if q not in vd: 
                vd[q] = Q(q, n)
    
            vd[q].t[t] = r
    
    for v in vd.values(): v.setv()

    return vd

vd = get_var_dict()

from copy import deepcopy as dc
vdc = dc(vd)

def print_var(var, ti, vd, row):

    print("{:<16} {:d} [{:>3}] {}".format(vd[var].q, ti, row[vd[var][ti]], vd[var].n))


def get_var_year(case, var, year = None, vd = vdc, ifile = "nlsy79_1"):

  if var  not in vd:      return "NO SUCH VAR"
  if year not in vd[var]: return "NO SUCH YEAR"

  for row in dictread(zopen(ifile + ".zip", ifile + ".csv")):

    if int(row[vd["CASEID"].v]) == case:
      print_var(var, year, vd, row)
      return



##########################################################
##########################################################
##########################################################

exp_vars = ['FER-3', 'EXP-1', 'EXP-2', 'EXP-3', 
            'EXP-4A', 'EXP-4B', 'EXP-4C', 'EXP-4D', 'EXP-4E', 
            'EXP-5', 'EXP-6', 'EXP-7', 'EXP-8', 'EXP-9', 'EXP-OCC']

exp_years = {ti for ev in exp_vars for ti in vd[ev].t}

def write_exp_csv(idvars, varis, vd,
                  ofile = "_exp.csv",
                  ifile = "nlsy79_1"):

   times = {ti for v in varis for ti in vd[v].t}
    
   with open(ofile, "w") as ofile:

      for row in dictread(zopen(ifile + ".zip", ifile + ".csv")):

          for ti in times:

             vals = [row[vd[v].v] for v in idvars]
             vals.append(str(ti))

             found_data = False
             for v in varis:
                if   not ti in vd[v]: vals.append("")
                elif int(row[vd[v][ti]]) < -3: vals.append("")
                else:
                  vals.append(row[vd[v][ti]])
                  if v not in ["CSAMWT", "YAWEIGHT"] or vals[-1] != "0":
                    found_data = True

             if not found_data: continue

             ofile.write(",".join(vals) + "\n")

##########################################################
##########################################################
##########################################################

static_vars = ['SAMPLE_SEX', 'SAMPLE_RACE',
	       'AFQT-2', 'ASVAB-AR-MK-IRT-ZSCORE', 'ASVAB-WK-PC-IRT-ZSCORE',
               'ROTTER_SCORE',
               'PEARLIN_SCORE', 'PEARLIN_ZSCORECW', 'PEARLIN_ZSCORECW_PERCENTILE',
               'ROSENBERG_SCORE', 'ROSENBERG_ZSCORECW', 'ROSENBERG_ZSCORECW_PERCENTILE',
               "HGC-MOTHER", "HGC-FATHER",
               "R_REL-1", 'R_REL-1_COL',
	             "AGE1B", "AGE2B", "AGE3B", "AGE1M",
               'PREGS', 'NUMKID', "ABORTS", 'MISCAR', 
               'FFER-92', 
               'AGE1P', 'OUT1P', 'FL1M1B', 'MO1M1B', 
               'MO1B2B', 'MO2B3B']

static_dates = ['RDOB', 'BG1P', 'BG1M', 'BG2M', 'BG3M', 'BG4M', 'BG5M', 'BG6M', 'BG7M',
                                'EN1M', 'EN2M', 'EN3M', 'EN4M', 'EN5M', 'EN6M']

def write_static_vars(vd, static_vars, static_dates,
                      ofile = "_static.csv",
                      ifile = "nlsy79_1"):

   # Adding case at the beginning, so one later.
   idx_f92 = 0
   if 'FFER-92' in static_vars:
     idx_f92 = static_vars.index('FFER-92')

   idx_dob = 0
   if 'RDOB' in static_dates:
     idx_dob = len(static_vars) + static_dates.index('RDOB')
    
   with open(ofile, 'w') as ofile:

      for row in dictread(zopen(ifile + ".zip", ifile + ".csv")):

         vals = [row[vd[sv].v] for sv in static_vars]
         
         for sd in static_dates:
            if   ("MO" + sd) in vd and vd["MO"+sd].valid("XRND", row, -4):
              vals.append('{:04d}-{:02d}-01'.format(int(row[vd["YR"+sd].v]),
                                                    int(row[vd["MO"+sd].v])))
            elif (sd + "~M") in vd and vd[sd+"~M"].valid("XRND", row, -4):
              vals.append('{:04d}-{:02d}-01'.format(int(row[vd[sd+"~Y"].v]),
                                                    int(row[vd[sd+"~M"].v])))
            elif (sd + "_M") in vd and vd[sd+"_M"].valid("XRND", row, -4):
              vals.append('{:04d}-{:02d}-01'.format(int(row[vd[sd+"_Y"].v]),
                                                    int(row[vd[sd+"_M"].v])))
            else: vals.append("")


         # Age at first sex reported several times -- take average.
         if idx_f92:
            ages = [int(row[vd["FFER-92"][ti]]) for ti in vd["FFER-92"] if int(row[vd["FFER-92"][ti]]) > 0]
            if ages: vals[idx_f92] = str(ages[0]) # str(sum(ages)/len(ages))

         if idx_dob and "RDOB_Y" in vd:

            dates = ['{:04d}-{:02d}-01'.format(rect_year(int(row[vd["RDOB_Y"][ti]])), int(row[vd["RDOB_M"][ti]]))
                     for ti in vd["RDOB_Y"] if vd["RDOB_Y"].valid(ti, row, 0)]
            if dates: vals[idx_dob] = dates[0]
            

         ofile.write(",".join(vals) + "\n")


##########################################################
##########################################################
##########################################################

yearly_vars = ['AGEATINT', 'HGCREV', 'Q3-10B', 'ENROLLMTREV', 'ESR_COL', 'HRP1', 'HH5-5', 
               'WKSWK-PCY', 'POVSTATUS', 'NET_WORTH', 'TNFI_TRUNC', 
               'RELSPPTR', 'R_REL-2', 'R_REL-3', 'Q9-63', 'Q9-66']

yearly_years = {ti for ev in yearly_vars for ti in vd[ev].t}

##########################################################
##########################################################
##########################################################

fert_vars = sorted([v for v in vd if re.search(r'Q9-\d\d[._]', v)], 
                   key = lambda x: (x.split(".")[1], x))

adtl_vars = ["ABORT{}{}".format(n, p) for n in range(1, 5) for p in ["MO", "YR"]]
adtl_vars += sorted([fv for fv in vd if "FFER" in fv])
adtl_vars += ["FERDATA"]
adtl_vars += ["Q11-5C"]
adtl_vars += ["Q9-64GA"]

adtl_vars.remove("FFER-68_1")
adtl_vars.remove("FFER-70_1")
adtl_vars.remove("FFER-118A_1")
adtl_vars.remove("FFER-118B_1")
adtl_vars.remove("FFER-118A_2")
adtl_vars.remove("FFER-118B_2")

bool_vars = ["FFER-13", "FFER-85", "FFER-86", "FFER-87", 
             "FFER-115", "FFER-110", "FFER-25_", "FFER-26", "Q11-5C", "Q9-64GA"]


fert_years = sorted(list({ti for fv in (fert_vars + adtl_vars) for ti in vd[fv].t}))

def preg_data(varis, adtl_varis, years, vd,
              ofile = "_fer.csv",
              ifile = "nlsy79_1",
              verbose = False):

  halt = ""

  preg_out = open(ofile, "w")
  pchi_out = open("_preg_child_map.csv", "w")

  for row in dictread(zopen(ifile + ".zip", ifile + ".csv")):

     row = {k : int(v) for k, v in row.items()}

     case = row[vd["CASEID"].v]
     # if case < 10930: continue
     
     if row["R0214800"] != 2: continue # Girls only!

     pregnancies = []
     
     if verbose:
       print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
       print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

     for c in range(1, 1+row[vd["NUMKID"].v]):
         pregnancies.append(P(outcome = "C", id = c, m = row[vd["C%dDOB~M" % c].v], y = row[vd["C%dDOB~Y" % c].v], created = True))

     # Note twins.
     for pi, p in enumerate(pregnancies):
       if pi and p == pregnancies[pi-1]:
         pregnancies[pi-1].mult = True
         p.mult = True

     # cycle through the years that have explicit dates for abortions.
     for a in range(1, 5):
         for ti in vd["ABORT%dMO" % a]:
           if not vd["ABORT%dMO" % a].valid(ti, row, -3): continue

           # Alternatively, if _both_ are negative, kill it.
           if not vd["ABORT%dMO" % a].valid(ti, row, 0) and \
              not vd["ABORT%dYR" % a].valid(ti, row, 0): continue

           if verbose: print(ti, vd["ABORT%dMO" % a][ti], row[vd["ABORT%dMO" % a][ti]], rect_year(row[vd["ABORT%dYR" % a][ti]]))
           pregnancies.append(P(outcome = "A", id = a, created = True, 
                                m = row[vd["ABORT%dMO" % a][ti]],
                                y = rect_year(row[vd["ABORT%dYR" % a][ti]])))

     # Add slots for any extras whose dates are not explicit.
     for a in range(sum([p.out == "A" for p in pregnancies]) + 1, int(row[vd["ABORTS"].v]) + 1):
         pregnancies.append(P(outcome = "A", id = a, created = True))

     nmiscar = 0
     for ti in vd["MISCAR_"]:
        ymiscar = int(row[vd["MISCAR_"][ti]])
        if ymiscar < -2: continue
        if nmiscar == ymiscar: continue
        if ymiscar < nmiscar: print("WARNING -- MISCAR DROPPED!!")
        
        for misc in range(nmiscar+1, ymiscar+1):
            pregnancies.append(P(outcome = "M", id = misc, m = -1, ry = ti, created = True))
        nmiscar = ymiscar

     pregnancies.sort()


     last = 0
     P.cuid, P.ruid = 0, 0
     to_match = []
     for ti in fert_years:

        if ti == 1987: continue

        for itr in range(1, 13):

            varis = []
            templ = "Q9-%d.{:02d}".format(itr)
            for q in [74, 78, 79, 80, 81, 82]:
               if (templ%q) in vd and vd[templ % q].valid(ti, row):
                  if verbose: print_var(templ%q, ti, vd, row)
                  varis.append(int(row[vd[templ % q][ti]]))
               else: varis.append(-5)

            if all(v < 0 for v in varis): continue

            nci = sum(p.out == "C" for p in to_match)

            if varis[0] > 0 and all(v < 0 for v in varis[1:]) and to_match \
               and (to_match[-1].id == 0 or to_match[-1].id == varis[0]) \
               and ti - to_match[-1].y <= 2:
                to_match[-1].id = varis[0]
                to_match[-1].out = "C"
            elif to_match and to_match[-1].out == "P" and ti - to_match[-1].y <= 2 and \
                to_match[-1].id == 0 and to_match[-1].mwanted < 0:
                to_match[-1].intentions(*varis)
                last -= 1
            else: 

                while ti < 1984 and itr - 1 > len(to_match):
                  to_match.append(P(ry = ti, outcome = "X"))

                to_match.append(P(ry = ti)) # tentative year.
                to_match[-1].intentions(*varis)


            # 1986-1990
            if ("FFER-118_%d_M" % itr) in vd and vd["FFER-118_%d_M" % itr].valid(ti, row): 
                to_match[-1].start(row[vd["FFER-118_%d_M" % itr][ti]], 
                                   row[vd["FFER-118_%d_Y" % itr][ti]])

            # 1984 only
            if ("FFER-106_%d_M" % itr) in vd and vd["FFER-106_%d_M" % itr].valid(ti, row): 
                to_match[-1].start(row[vd["FFER-106_%d_M" % itr][ti]], 
                                   row[vd["FFER-106_%d_Y" % itr][ti]])

            # 1984-1990
            if ("FFER-105_%d_M" % itr) in vd and vd["FFER-105_%d_M" % itr].valid(ti, row): 
                to_match[-1].start(row[vd["FFER-105_%d_M" % itr][ti]], 
                                   row[vd["FFER-105_%d_Y" % itr][ti]])

            # 1990/1992 and after.... with some variable "fixes"
            if ("Q9-77.%02d~M" % itr) in vd and vd["Q9-77.%02d~M" % itr].valid(ti, row): 
                to_match[-1].start(row[vd["Q9-77.%02d~M" % itr][ti]], 
                                   row[vd["Q9-77.%02d~Y" % itr][ti]])


        if ti < 1984:

          # Pregnant and _knew it_ last time.
          if ti == 1983 and \
             row[vd["FFER-88"].v] == 1 and \
             last and to_match[last-1].out == "P":
             to_match[last-1].out = "C"

          # Not live births.
          # for 1983, count the non-live births from 1982:
          # there are occasional cases (e.g., case 229, 
          # where births start at 2 instead of 1... WTF).
          nonlive = 0
          if ti == 1983: nonlive = sum(p.out != "C" for p in to_match)
          for itr in range(1, 4):
             if vd["FFER-3_%d_" % itr].valid(ti, row, cut = 0):

               nonlive += 1

               ffer3 = row[vd["FFER-3_%d_" % itr][ti]]
               if nonlive <= len(to_match): 
                  to_match[nonlive-1].out = "CSMA"[ffer3]
               elif len(to_match): 
                  to_match[-1].out = "CSMA"[ffer3]
                 
             # FFER-1_ is 1983 only... 
             if vd["FFER-1_%d_M" % itr].valid(ti, row):
               if not to_match: to_match.append(P(ry = ti, outcome = "A"))

               if nonlive <= len(to_match): 
                  to_match[nonlive-1].m = row[vd["FFER-1_%d_M" % itr][ti]]
                  to_match[nonlive-1].y = rect_year(row[vd["FFER-1_%d_Y" % itr][ti]], ti)
               elif last < len(to_match): 
                  to_match[-1].m = row[vd["FFER-1_%d_M" % itr][ti]]
                  to_match[-1].y = rect_year(row[vd["FFER-1_%d_Y" % itr][ti]], ti)


          # Next, mark pregnancies succeeding live births (FFER-7/11/15)
          for nc in range(1, 6):
            for postc_preg in range(1, 4):
              var = "FFER-{}_{}".format(3 + postc_preg*4, nc)
              if var in vd and vd[var].valid(ti, row, cut = 0):

                children = [pi for pi, p in enumerate(to_match) if p.out == "C"]

                start = 0
                if nc <= len(children): start = children[nc-1] + postc_preg
                if not start: continue

                while start >= len(to_match): to_match.append(P(ry = ti))

                to_match[start].out = "XSMA"[row[vd[var][ti]]]

          # Children born.
          for itr in range(1, 8):

            if vd["FFER-DOB_%d_M" % itr].valid(ti, row, cut = 0):

               pos, nkids = 0, 1
               # while pos < len(to_match) and to_match[pos].out != "C": pos += 1

               while pos < len(to_match) and \
                     (nkids < itr or to_match[pos].out != "C"):
                 if to_match[pos].out == "C": nkids += 1
                 pos += 1

               if pos == len(to_match): to_match.append(P(ry = ti))

               to_match[pos].m = row[vd["FFER-DOB_%d_M" % itr][ti]]
               to_match[pos].y = rect_year(row[vd["FFER-DOB_%d_Y" % itr][ti]])

               pos += 1



        else: # 1984+

          for itr in range(1, 4):
            if vd["FFER-3_%d" % itr].valid(ti, row):
              if last+itr < len(to_match): 
                to_match[last+itr-1].out = "XCMSAP"[row[vd["FFER-3_%d" % itr][ti]]]
              elif len(to_match):
                to_match[-1].out = "XCMSAP"[row[vd["FFER-3_%d" % itr][ti]]]

            if vd["FFER-1_%d_M" % itr].valid(ti, row):
              if last+itr <= len(to_match): 
                to_match[last+itr-1].m = row[vd["FFER-1_%d_M" % itr][ti]]
                to_match[last+itr-1].y = rect_year(row[vd["FFER-1_%d_Y" % itr][ti]])


        # If R is currently pregnant...
        if any(vd[var].valid(ti, row, 0) for var in ["Q9-64GA", "Q11-5C", "FFER-13", "FFER-115"]):
          if len(to_match) == last: to_match.append(P(ry = ti))
          to_match[-1].out = "P"

          # If the dates are available...
          if vd["FFER-12_M"].valid(ti, row):

            to_match[-1].m = row[vd["FFER-12_M"][ti]]
            to_match[-1].y = rect_year(row[vd["FFER-12_Y"][ti]])


        if ti >= 1994:
          for itr in range(1, 10):
            if any(vd["Q9-%s.%02d" % (q, itr)].valid(ti, row, 0) for q in ["158C", "74B"]):

              if last+itr <= len(to_match): to_match[last+itr-1].mult = True
              else: to_match[-1].mult = True


        #### Lots of additional matching variables....
        for fv in adtl_varis:

           if not vd[fv].valid(ti, row, -4): continue

           if any(v in fv for v in bool_vars) and \
              not row[vd[fv][ti]]: continue

           if row[vd[fv][ti]] == 2 and "FFER-2_" in fv: continue    # PREGNANCY LOSS BEFORE CHILD 82/83

           if "FFER-92" in fv: continue
           if "ABORT" in fv: continue

           if verbose: print_var(fv, ti, vd, row)


        for p in to_match[last:]: p.end_from_start()

        if verbose and len(to_match) > last:
            for p in to_match[last:]: print(" --", p)
            print(" -----", ti)

        last = len(to_match)

     if row[vd["NUMKID"].v] == sum(p.out == "C" for p in to_match):
        for pi, pa in enumerate(to_match):
          if pa.out != "P": continue
          if pi + 1 == len(to_match): continue

          pb = to_match[pi+1]
          if pa.y + 2 < pb.y: continue
          pb.merge(pa) # Should the merge go the other way??
          to_match.remove(pa)

     # If pregnancies remain, convert them to children.
     for p in to_match:
       if p.out == "P": p.out = "C"

     # IDs were not recorded for children pre-1983.
     # Construct a naive ID from the birth order.
     nci = 0
     for pi, p in enumerate(to_match):
        if p.out == "C" and p.ry <= 1983 and not p.id:
           nci += 1
           p.id = nci

     if verbose: 
       print("****** {} Pregnancies\n**************".format(len(to_match)))
       print("CASE:", row[vd["CASEID"].v])
       print("NUMKIDS={}  PREGS={}  ABORTS={}  MISCAR={}".
             format(row[vd["NUMKID"].v], row[vd["PREGS"].v], row[vd["ABORTS"].v], row[vd["MISCAR"].v]))
       print("  ===== created variables, pre-match")
       for p in pregnancies: print(p)

     match_em(pregnancies, to_match)

     for pi, p in enumerate(pregnancies):
       preg_out.write(p.csv(case) + "\n")

       if p.out == "C":
         pchi_out.write("{},{},{}\n".format(row[vd["CASEID"].v], p.uid, p.id))


     if verbose:
       print("  ===== v. parsed record")
       for p in to_match: print(p)

       print("  ===== created variables post match =====  CASE", row[vd["CASEID"].v])
       for p in pregnancies: print(p)


     ## Control stuff for paging records.
     if not verbose: continue

     if halt and \
        type(halt) is int and \
        row[vd["CASEID"].v] < halt: continue

     halt = input("continue??")
     try: halt = int(halt)
     except ValueError: pass

     if type(halt) is not int and halt: break

  print(non_matching_kids/total_records)


def write_schema():

  out = open("nlsy79_schema_1.sql", "w")

  out.write("DROP TABLE IF EXISTS static;\n")
  out.write("DROP TABLE IF EXISTS yearly;\n")
  out.write("DROP TABLE IF EXISTS exp;\n")
  out.write("DROP TABLE IF EXISTS fer;\n")
  out.write("DROP TABLE IF EXISTS cya_static;\n")
  out.write("DROP TABLE IF EXISTS cya_psych;\n")
  out.write("DROP TABLE IF EXISTS cya_self;\n")
  out.write("DROP TABLE IF EXISTS cya_yearly;\n")
  out.write("\n")

  ### STATIC
  out.write("CREATE TABLE static (\n  r INTEGER,\n")
  for v in static_vars:  out.write("  {} INTEGER,\n".format(v.lower().replace('-', '_')))
  for v in static_dates: out.write("  {} STRING,\n".format(v.lower().replace('-', '_')))
  out.write("  PRIMARY KEY (r)\n);\n\n")

  ### YEARLY
  out.write("CREATE TABLE yearly (\n  r INTEGER, y INTEGER,\n")
  for v in yearly_vars: out.write("  {} INTEGER,\n".format(v.lower().replace('-', '_')))
  out.write("  PRIMARY KEY (r,y)\n);\n\n")

  ### EXPECTATIONS
  out.write("CREATE TABLE exp (\n  r INTEGER, y INTEGER,\n")
  for v in exp_vars: out.write("  {} INTEGER,\n".format(v.lower().replace('-', '_')))
  out.write("  PRIMARY KEY (r,y)\n);\n\n")

  ### PREGNANCIES
  out.write("CREATE TABLE fer (\n  r INTEGER, p INTEGER,\n")
  out.write("  outcome CHARACTER(1),\n")
  out.write("  end_date STRING, start_date STRING,\n")
  out.write("  mwanted INTEGER, fwanted INTEGER,\n")
  out.write("  had_used_contracep INTEGER, using_contracep INTEGER,\n")
  out.write("  matched INTEGER,\n")
  out.write("  PRIMARY KEY (r,p)\n);\n\n")

  ### CHILDREN STATIC
  out.write("CREATE TABLE cya_static (\n  r INTEGER, c INTEGER,\n")
  for v in cya_static:  out.write("  {} INTEGER,\n".format(v.lower().replace('-', '_')))
  for v in cya_static_dates: out.write("  {} STRING,\n".format(v.lower().replace('-', '_').replace("1st", "fst")))
  out.write("  PRIMARY KEY (r, c)\n);\n\n")

  ### CYA PSYCH
  out.write("CREATE TABLE cya_psych (\n  r INTEGER, c INTEGER, y INTEGER,\n")
  for v in cya_psych: out.write("  {} INTEGER,\n".format(v.lower().replace('-', '_')))
  out.write("  PRIMARY KEY (r, c, y)\n);\n\n")

  ### CYA SELF
  out.write("CREATE TABLE cya_self (\n  r INTEGER, c INTEGER, y INTEGER,\n")
  for v in cya_self: out.write("  {} INTEGER,\n".format(v.lower().replace('-', '_')))
  out.write("  PRIMARY KEY (r, c, y)\n);\n\n")

  ### CYA YEARLY
  out.write("CREATE TABLE cya_yearly (\n  r INTEGER, c INTEGER, y INTEGER,\n")
  for v in cya_yearly: out.write("  {} INTEGER,\n".format(v.lower().replace('-', '_')))
  out.write("  PRIMARY KEY (r, c, y)\n);\n\n")


  ### IMPORT EVERYTHING
  out.write(".mode csv\n")
  out.write(".import _static.csv static\n")
  out.write(".import _yearly.csv yearly\n")
  out.write(".import _exp.csv exp\n")
  out.write(".import _fer.csv fer\n")
  out.write(".import _cya_static.csv cya_static\n")
  out.write(".import _cya_psych.csv cya_psych\n")
  out.write(".import _cya_self.csv cya_self\n")
  out.write(".import _cya_yearly.csv cya_yearly\n")
  out.write(".mode columns\n\n")

  ### FOR CHILD FILES: MOD 100.
  for t in ["cya_static", "cya_psych", "cya_self", "cya_yearly"]:
    out.write("UPDATE {} SET c=(c%100);\n".format(t))

  ### CLEAN OUT NULL VALUES.
  for tab, cols in [["static", static_vars + static_dates],
                    ["yearly", yearly_vars],
                    ["exp", exp_vars],
                    ["fer", ["end_date", "start_date", "mwanted", "fwanted", "had_used_contracep", "using_contracep", "matched"]],
                    ['cya_static', cya_static + cya_static_dates],
                    ['cya_psych', cya_psych],
                    ['cya_self', cya_self],
                    ['cya_yearly', cya_yearly]
                   ]:
    for c in cols:
      c = c.lower().replace('-', '_')
      c = re.sub(r'^1st', r'fst', c)
      out.write("UPDATE {} SET {}=NULL WHERE {}='';\n".format(tab, c, c))
  out.write("\n\n")



##########################################################
##########################################################
##########################################################


def main():

   write_schema()


   # FIRST THE NLSY79 (MOTHERS)

   write_static_vars(vd, ["CASEID"] + static_vars, static_dates)
   for sv in static_vars: 
     if sv in ['PREGS', 'NUMKID', "ABORTS", 'MISCAR', 'FFER-92']: continue
     vd.pop(sv)

   for sd in static_dates:
       if ("MO" + sd) in vd:
           vd.pop("MO" + sd)
           vd.pop("YR" + sd)

       if (sd + "_M") in vd:
           vd.pop(sd + "_M")
           vd.pop(sd + "_Y")


   write_exp_csv(['CASEID'], exp_vars, vd)
   for ev in exp_vars: vd.pop(ev)
   
   write_exp_csv(['CASEID'], yearly_vars, vd, ofile = "_yearly.csv")
   for ev in yearly_vars: vd.pop(ev)

   
   preg_data(fert_vars, adtl_vars, fert_years, vd, verbose = False)
   for v in fert_vars: del vd[v]
   

   ## NOW CHILD AND YOUNG-ADULT (Children of the NLSY79)

   cyvd = get_var_dict(ifile = "cya79_1", child = True)

   write_static_vars(cyvd, cya_id + cya_static, cya_static_dates,
                     ofile = "_cya_static.csv", ifile = "cya79_1")

   for sv in cya_static: cyvd.pop(sv)
   for sd in cya_static_dates:
     if "1ST" in sd:
       cyvd.pop("MO" + sd)
       cyvd.pop("YR" + sd)
     if "DOB" in sd:
       cyvd.pop(sd + "~M")
       cyvd.pop(sd + "~Y")
      
   write_exp_csv(cya_id, cya_psych, cyvd, ofile = "_cya_psych.csv", ifile = 'cya79_1')
   for v in cya_psych: cyvd.pop(v)

   write_exp_csv(cya_id, cya_self, cyvd, ofile = "_cya_self.csv", ifile = 'cya79_1')
   for v in cya_self: cyvd.pop(v)

   write_exp_csv(cya_id, cya_yearly, cyvd, ofile = "_cya_yearly.csv", ifile = 'cya79_1')
   for v in cya_yearly: cyvd.pop(v)


   with open("blah", "w") as out: out.write(pprint.pformat(cyvd))





if __name__ == "__main__": main()

