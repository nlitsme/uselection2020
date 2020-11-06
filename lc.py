"""
Processes the counties list, for each county prints:
   * T: total votes received
   * C: nr of votes counted
   * U: nr of votes not yet counted
   * d: how many votes the Democrats are ahead of the Republicans
   * <>: what percentage of the uncounted votes Trump would need to win this County or State.
   * D: how many votes the Democrats got
   * R: how many votes the Republicans got
"""
from collections import defaultdict
import re
NRSTEPS = 10000
def getjson(url):
    import json
    import urllib.request
    with urllib.request.urlopen(url) as response:
        text = response.read()
        return json.loads(text)

def getstate(name):
    if name == "District of Columbia":
        return "DC", "Washington"
    else:
        m = re.match(r'(.*), (\w\w)$', name)
        if m:
            return m.group(2), m.group(1)
    print("---->", name)


lu = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-data/prod/last_updated.json")
print("--> %s" % lu["time"])
counties = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-data/prod/data-out/%s/president_county_details.json" % lu["time"])

ecvinfo = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-geo/bubbles.json")
bystate = defaultdict(lambda:defaultdict(int))

def req(d, r, u):
    if not u:
        if d>r: return "DDD"
        if r>d: return "RRR"
        return "???"
    req = (d-r+u)/u/2
    if req<0:
        return "rrr"
    if req>1:
        return "ddd"
    return "%.2f" % (req*100)

for k, v in counties.items():
    state, name = getstate(v["name"])
    try:
        countedvotes = 0
        byparty = dict()
        for c in v.get("candidates", []):
            byparty[c["party"]] = c["votes"]
            countedvotes += c["votes"]
            bystate[state][c["party"]] += c["votes"]

        factor = v["reporting"]/100.0

        totalvotes = countedvotes/factor
        uncountedvotes = totalvotes - countedvotes

        bystate[state]["total"] += totalvotes
        bystate[state]["counted"] += countedvotes
        bystate[state]["uncounted"] += uncountedvotes

        print("%s - %-30s T:%10d C:%10d(%7.2f) U:%10d(%7.2f); d:%10d(%7.2f)<%7s>; %s" % (state, name,
            totalvotes, countedvotes, 100*countedvotes/totalvotes, uncountedvotes, 100*uncountedvotes/totalvotes,
            byparty["D"]-byparty["R"], (byparty["D"]-byparty["R"])/countedvotes*100.0,
            req(byparty["D"], byparty["R"], uncountedvotes),
            "; ".join("%s:%10d(%7.2f)" % (p, n, n/countedvotes*100.0) for p, n in sorted(byparty.items()))))
    except Exception as e:
        pass
        #print("%s - %-30s - %s" % (state, name, e))

for st, v in sorted(bystate.items()):
    print("%s - %-30s T:%10d C:%10d(%7.2f) U:%10d(%7.2f); d:%10d(%7.2f)<%7s>; %s" % (st, "--total--",
        v["total"], v["counted"], v["counted"]/v["total"]*100, v["uncounted"], v["uncounted"]/v["total"]*100, 
        v["D"]-v["R"], (v["D"]-v["R"])/v["counted"]*100.0,
        req(v["D"], v["R"], v["uncounted"]),
        "; ".join("%s:%10d(%7.2f)" % (p, n, n/v["counted"]*100.0) for p, n in sorted(v.items()) if len(p)==1)))

