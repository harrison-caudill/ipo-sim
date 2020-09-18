#!/usr/bin/env python

"""Calculates all the linear combinations of sell-all/sell-cover for all your grants, and shows you what percentage of your 
total vested RSU grant it will be. You can use this to to see what choices you should make before Day 1 if you want to sell 
X% of your RSUs that will vest Day 1 (since I want to sell enough RSUs on Day 1 to cover my 35% tax).
To use, just modify the RSU_GRANTS array with the vested numbers you'll have DL day (current numbers are notional, obviously)."""

__author__ = "Kevin Today"

import math

# If you're outside of the US, this might be different
MINIMUM_WITHHOLDING = 0.22

# Plug in the VESTED amount you'll have on DL day here
RSU_GRANTS = [
    10000,
    20000,
    2000,
    50000,
]

# =================================================================================
total_rsus = sum(RSU_GRANTS)
num_rsu_grants = len(RSU_GRANTS)
format_str = '{0:0' + str(num_rsu_grants) + 'b}'
num_combos = int(math.pow(2, num_rsu_grants))

sell_strats = []
for i in range(0, num_combos):
    per_grant_elections_binary = format_str.format(i)
    per_grant_elections_arr = [digit == '1' for digit in per_grant_elections_binary]

    rsus_sold = 0
    for idx, sell_all in enumerate(per_grant_elections_arr):
        sell_pct = 1.0 if sell_all else MINIMUM_WITHHOLDING
        rsus_in_grant = RSU_GRANTS[idx]
        rsus_sold += rsus_in_grant * sell_pct

    sell_strats.append( (rsus_sold, rsus_sold / total_rsus, per_grant_elections_arr) )

sell_strats.sort(key=lambda strat: strat[1])

for strat in sell_strats:
    pretty_elections_arr = []
    for idx, sell_all in enumerate(strat[2]):
        grant = RSU_GRANTS[idx]
        if sell_all:
            pretty_elections_arr.append("ALL %s" % grant)
        else:
            pretty_elections_arr.append("COVER %s" % grant)
    joined_elections_str = ", ".join(pretty_elections_arr)
    print("%s (%s) - %s" % (strat[1], strat[0], joined_elections_str))
