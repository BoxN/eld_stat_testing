import numpy as np
from itertools import combinations
from itertools import product

import stats

# Creating an object of the class
character = stats(0, 'character base stats', (15, 20, 0, 150))

dmgs = np.arange(0,15,1)
crits = np.arange(0,160,10)
maxis = np.arange(0,140,10)
crit_dmgs = np.arange(0,50,5)


combs = list(product(dmgs, crits, maxis, crit_dmgs))
combs_len = len(combs)

#   Generating items
print(f'Generating {combs_len} combinations')

items = []
for index, group in enumerate(combs):
    items.append(stats(index, f'random item {index}', group))
print('Done')

#   Generating items conbinations
print(f'Generating {combs_len} combinations')

results = []
for item in items:
    results.append(character.equip(item))
print('Done')

ordered_res = sorted(results)

print(stats.headers())
print(ordered_res[0])
print(ordered_res[-1])