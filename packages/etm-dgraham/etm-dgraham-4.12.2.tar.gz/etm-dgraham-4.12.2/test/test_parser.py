#!/usr/bin/env python3
from dateutil import parser
import pendulum



def parse(s, dayfirst=False, yearfirst=False):
    md = "DD-MM" if dayfirst else "MM-DD"
    ymd = f"YYYY-{md}" if yearfirst else f"{md}-YYYY"
    alt = f"YYYY-MM-DD" if yearfirst else f"{md}-YYYY"
    pi = parser.parserinfo(
            dayfirst=dayfirst,
            yearfirst=yearfirst
            )
    dt = pendulum.instance(parser.parse(s, parserinfo=pi))
    D = "T" if dayfirst else "F"
    Y = "T" if yearfirst else "F"
    print(f"{D} {Y} {s : <10} {dt.format('YYYYMMDD') : <10} {ymd}: {dt.format(ymd) : <10}  {alt}: {dt.format(alt) : <10}")

print(f"D Y  entered    stored       ymd                    alt")

parse("09-10-11", dayfirst=True, yearfirst=True)
parse("10-11", dayfirst=True, yearfirst=True)
parse("10-11-40", dayfirst=True, yearfirst=True)
print()

parse("09-10-11", dayfirst=False, yearfirst=True)
parse("10-11", dayfirst=False, yearfirst=True)
parse("10-11-40", dayfirst=False, yearfirst=True)
print()

parse("2000-3-10", dayfirst=False, yearfirst=True)
parse("3-10", dayfirst=False, yearfirst=True)

print()
parse("2000-3-10", dayfirst=True, yearfirst=True)
