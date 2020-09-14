#!/usr/bin/env python

"""Generates a graph called graph.py, where bar = % of all RSUs sold and 
X-axis labels = indices within vested_quants which were chosen as 'sell_to_cover'"""

__author__ = "Ben Dawes"

import itertools
vested_quants = [...]
withholding = ...
total = sum(vested_quants)
sale_quants = []
which_sold_to_cover = []
for i in range(len(vested_quants)+1):
  for indices_to_sell_to_cover in itertools.combinations(list(range(len(vested_quants))), i):
    total_sold = 0
    print(indices_to_sell_to_cover)
    for j in range(len(vested_quants)):
       if j in indices_to_sell_to_cover:
          total_sold += withholding * vested_quants[j]
       else:
          total_sold += vested_quants[j]
    sale_quants.append(total_sold/total)
    which_sold_to_cover.append(indices_to_sell_to_cover)
print(sale_quants)

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

which_sold_to_cover = [x for _,x in sorted(zip(sale_quants,which_sold_to_cover))]
sale_quants = sorted(sale_quants)
y_pos = np.arange(len(sale_quants))
plt.bar(y_pos, sale_quants, align='center', alpha=0.5)
plt.xticks(y_pos, ["".join(list([str(w) for w in which])) for which in which_sold_to_cover])
plt.ylabel('% RSUs sold')
plt.title('Percentage sold on sell-to-cover combos')
plt.savefig('graph.png')
