"""
This iterates over all counties, and calculates what percentage of the uncounted votes
Biden would need to win the election.

Somewhat inefficient, use pypy3 to run this.
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

lu = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-data/prod/last_updated.json")
counties = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-data/prod/data-out/%s/president_county_details.json" % lu["time"])

ecvinfo = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-geo/bubbles.json")
perparty = defaultdict(float)
perstate = defaultdict(lambda:defaultdict(float))
perstate_pct = [ defaultdict(lambda:defaultdict(float)) for _ in range(NRSTEPS+1) ]
total = 0.0
totalcounted = 0
totalnotcounted = 0
for k, v in counties.items():
    state = None
    if v["name"] == "District of Columbia":
        state = "DC"
    else:
        m = re.search(r', (\w\w)$', v["name"])
        if m:
            state = m.group(1)
    if not state:
        print(state, v)

    factor = v.get("reporting", 0)/100.0
    countytotal = 0
    for c in v.get("candidates", []):
        perparty[c["party"]] += factor and c["votes"]/factor
        perstate[state][c["party"]] += factor and c["votes"]/factor
        total += factor and c["votes"]/factor
        totalcounted += c["votes"]
        totalnotcounted += c["votes"]*(1-factor)
        countytotal += c["votes"]
        for pct in range(NRSTEPS+1):
            perstate_pct[pct][state][c["party"]] += c["votes"]

    for pct in range(NRSTEPS+1):
        perstate_pct[pct][state]["R"] += countytotal*(1-factor)*(NRSTEPS-pct)/NRSTEPS
        perstate_pct[pct][state]["D"] += countytotal*(1-factor)*pct/NRSTEPS


print("total = %d" % total)
for k, v in perparty.items():
    print("%s : %10d %6.2f" % (k, v, 100.0*v/total))

print("counted = %d, not counted = %d" % (totalcounted, totalnotcounted))
for pct, result in enumerate(perstate_pct):
    necv = defaultdict(int)
    for k, v in result.items():
        info = ecvinfo[k]
        if k in ('ME', 'NE'):   # (ME)Maine and (NE)Nebraska
            totalvotes = sum(v.values())
            rv = v["R"]
            dv = v["D"]
            ov = totalvotes - rv - dv
            rv += ov/2
            dv += ov/2

            necv["R"] += int(info["ecv"] * (rv/totalvotes))
            necv["D"] += info["ecv"] - int(info["ecv"] * (rv/totalvotes))

        elif v["R"] > v["D"]:
            necv["R"] += info["ecv"]
        elif v["R"] < v["D"]:
            necv["D"] += info["ecv"]
        else:
            necv["?"] += info["ecv"]

    if necv['D']>necv['R']:
        print("%5.2f - D:%3d R:%3d -> %s" % (pct/(NRSTEPS/100), necv['D'] ,necv['R'], "Biden" if necv['D']>necv['R'] else "Trump"))
        break


