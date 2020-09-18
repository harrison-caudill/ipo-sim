#!/usr/bin/env python3


"""
If I want to sell a certain percentage (eg 50%) of the RSUs available to me on day one, after tax witholding, which of my grants 
should I choose “sell to cover” and which should I choose “sell all". 
Running the script will prompt you to enter your RSU grants and vested quantities one at a time, 
and produce a graph showing the percentage of RSUs sold for each combination of elections. 
Denominator of the fraction shown in y axis is “total number of shares vested minus withholdings”
Numerator is “total number of shares sold after withholdings given this grant combination”
"""

__author__ = "Diccon Bate"

import itertools
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np


# Get input
grants = []
n = int(input("Enter number of grants: "))
for i in range(n): 
    name = input('Enter grant name (eg RSU-1234): ')
    quantity = int(input('Enter quantity for that grant: '))
    grants.append({"name": name,"quantity": quantity})


# Get combinations
possible_election_combinations = list(itertools.product(["sell_all","sell_to_cover"],repeat=len(grants)))

total_quantity = sum([x["quantity"] for x in grants])

def populate_scenario(grants, election_combination):
    sold_grants = []
    total_sold = 0
    for i, grant in enumerate(grants):
        if election_combination[i] == "sell_all":
            sold_grants.append(grant["name"])
            total_sold += grant["quantity"]
    return {
        "total_sold": total_sold,
        "sold_grants": sold_grants
    }

combinations = []
for combination in possible_election_combinations:
    scenario = populate_scenario(grants, combination)
    scenario["sold_grants"].sort()
    combinations.append({
        "sold_grants": "\n".join(scenario["sold_grants"]), 
        "percentage_sold": (scenario["total_sold"] / total_quantity) * 100
    })
combinations.sort(key=lambda k: k['percentage_sold'])

# Plot combinations
labels = []
values = []

for combo in combinations:
    labels.append(combo["sold_grants"])
    values.append(combo["percentage_sold"])

y_pos = np.arange(len(combinations))

plt.bar(y_pos, values, align='center')
plt.xticks(y_pos, labels)
plt.ylabel('% of total RSUs')
plt.title('% of RSUs by grant combination')
ax = plt.gca()
ax.set_ylim([0,100])
ax.yaxis.set_major_locator(plticker.MultipleLocator(10))
ax.grid(True,axis='y')

plt.show()
