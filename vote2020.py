"""
Write a summary of the voter info on theguardian.
"""
import json
from collections import defaultdict
# https://en.wikipedia.org/wiki/Voter_turnout_in_the_United_States_presidential_elections
#  -> eligible population: 239247182
#  65% -> 155510668.30
from stateinfo  import stateinfo

def getjson(url):
    import urllib.request
    with urllib.request.urlopen(url) as response:
        text = response.read()
        return json.loads(text)

lu = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-data/prod/last_updated.json")
states = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-data/prod/data-out/%s/president_details.json" % lu["time"])

ecvinfo = getjson("https://interactive.guim.co.uk/2020/11/us-general-election-geo/bubbles.json")

us = states["US"]
del states["US"]

nelect = defaultdict(int)
nkm2 = defaultdict(float)
nvotes = defaultdict(int)
nvotes["total"] = 154624588 - 135424188# 239247182*0.65-134743405
# 154624588
for k, v in states.items():
    info = ecvinfo[k]
    byparty = {}
    for c in v["candidates"]:
        byparty[c["party"]] = c
        nvotes[c["party"]] += c["votes"]

    t = v["totalVotes"]
    nvotes["total"] += t
    print("%s (%3d) - %10d ; %s" % (
        k, info["ecv"], t,
        " ; ".join("%s:%10d( %6.2f)" % ( p, c["votes"], t and 100*c["votes"]/t ) for p, c in sorted(byparty.items()))))

    totalkm2 = stateinfo[k][3]
    landkm2 = stateinfo[k][6]
    waterkm2 = stateinfo[k][10]
    if k in ('ME', 'NE'):   # (ME)Maine and (NE)Nebraska
        totalvotes = sum(p["votes"] for p in byparty.values())
        rv = byparty["R"]["votes"]
        dv = byparty["D"]["votes"]
        ov = totalvotes - rv - dv
        rv += ov/2
        dv += ov/2

        nelect["R"] += int(info["ecv"] * (rv/totalvotes))
        nelect["D"] += info["ecv"] - int(info["ecv"] * (rv/totalvotes))

    elif byparty["R"]["votes"] > byparty["D"]["votes"]:
        nelect["R"] += info["ecv"]
        nkm2["R"] += landkm2
    elif byparty["D"]["votes"] > byparty["R"]["votes"]:
        nelect["D"] += info["ecv"]
        nkm2["D"] += landkm2
    else:
        nelect["?"] += info["ecv"]
        nkm2["?"] += landkm2
print()
print("electoral votes: %s" % list(nelect.items()))
print("km2: %s" % list(nkm2.items()))
print("total votes: %s" % list(nvotes.items()))
print()

voted = nvotes["R"] + nvotes["O"] + nvotes["D"]
print("R:%10d(%6.2f) D:%10d(%6.2f) O:%10d(%6.2f)  U:%10d(%6.2f)" % (
    nvotes["R"], 100.0*nvotes["R"]/nvotes["total"],
    nvotes["D"], 100.0*nvotes["D"]/nvotes["total"],
    nvotes["O"], 100.0*nvotes["O"]/nvotes["total"],

    (nvotes["total"]-voted), 100.0*(nvotes["total"]-voted)/nvotes["total"]
    ))
print("totalvotes cast: %10d" % nvotes["total"])
