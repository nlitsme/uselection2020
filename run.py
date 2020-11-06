"""
This script basically does this, but only output the differences.

    while true; do
        date 
        python3 lc.py | grep "total.*[0-9]>\|total.*\<[01]\...)<\|-->" | sort -k 1.117n 
        python3 ls.py | grep "[0-9]>\|\<[01]\...)<\|-->" | sort -k 1.117n 
        sleep 300 
    done
"""

import subprocess
import time
from datetime import datetime
from collections import defaultdict
import re

def runlc():
    try:
        result = subprocess.check_output(["python3", "lc.py"])
        for line in result.decode('utf-8').split("\n"):
            if m := re.match(r'^(\w\w) - (--total.*(?:\d>|\D[01]\...\)<).*)', line):
                yield m.group(1), m.group(2)
    except Except as e:
        print(e)

def runls():
    try:
        result = subprocess.check_output(["python3", "ls.py"])
        for line in result.decode('utf-8').split("\n"):
            if m := re.match(r'^(\w\w) - (.*(?:\d>|\D[01]\...\)<).*)', line):
                yield m.group(1), m.group(2)
    except Except as e:
        print(e)

def main():
    results_lc = defaultdict(str)
    results_ls = defaultdict(str)

    while True:
        now = datetime.now()
        nowprinted = False

        for state, info in runlc():
            if results_lc[state] != info:
                results_lc[state] = info
                if not nowprinted:
                    print(now)
                    nowprinted = True
                print("%s - %s" % (state, info))

        for state, info in runls():
            if results_ls[state] != info:
                results_ls[state] = info
                if not nowprinted:
                    print(now)
                    nowprinted = True
                print("%s - %s" % (state, info))

        time.sleep(300)

if __name__ == '__main__':
    main()
