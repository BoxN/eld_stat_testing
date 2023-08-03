from functools import reduce
import sys
import time
import math
import numpy as np
import pandas as pd
from itertools import combinations_with_replacement
from datetime import datetime

from stats import Stats
from character import Character

# File path and name
file_path = "res.txt"
SLOT_NUMER = 37

#============getting all the items from the db.csv file=========================#
print(f'Fetching items from db: Started')
start_time = time.time()

all_items       = []
all_items_ids   = { k:[] for k in range(SLOT_NUMER)}

df = pd.read_csv('db.csv')
for index, row in df.iterrows():
    d = row.dropna().to_dict()
    
    all_items_ids[d['slot']].append(d['id'])
    all_items.append(Stats(d['slot'], d['name'], d['set'],attributes=d))
print(len(all_items), all_items)
#=======filter items_in_slot and prepare for the combination function===========#
all_items_ids_filtered = list(filter(None, all_items_ids.values()))

#================print some info about the objects loaded=======================#
for slot, item in all_items_ids.items():
    if len(item) > 0:
        print(f'slot: {slot:3}, choices:{len(item):3}')
all_items_ids_filtered_len = reduce(lambda a, b: a*len(b), [1,*all_items_ids_filtered])
print(f'Items combinations: {all_items_ids_filtered_len}')

print(f'Fetching items from db: Completed ({time.time()-start_time}s)')
print(f'Size all_items_ids: {sys.getsizeof(all_items_ids)}')
print(f'Size all_items: {sys.getsizeof(all_items)}')



#==============base stats for a specific class (not present in db)==============#
base_class_stats    = { 'phy_atk':1202,	'mag_atk':1202,	'phy_def':301,	'mag_def':301,	'hp':157000,
                        'dmg_per':      18,  
                        'dmg_per_m':    0,
                        'crit':         25,        
                        'maxi':         0,        
                        'crit_dmg':     25,

                        'pola':         0,
                        'specific':     0,
                        'all_s_dmg':    3,
                        'boss_dmg':     0,
                        'adapt':        0,
                        'cdr':          0
                       }

#===============================force passives==================================#
head_hunter = {'dmg_per':-24, 'boss_dmg':80}


#============================sockets combinations===============================#
avail_sockets = [  
                    Stats('0', 'socket', attributes={'maxi':12}),
                    Stats('0', 'socket', attributes={'crit':12}),
                    Stats('0', 'socket', attributes={'boss_dmg':5})
                ]

print(f'Generating sockets combinations: Started')
start_time = time.time()
# generate combinations
sockets_combinations = list(combinations_with_replacement(avail_sockets, 2))

sockets_combinations_len = len(sockets_combinations)
print(f'Socket combinations: {sockets_combinations_len}')

# generate item for each socket combination, grouping sockets into a single item
itemized_sockets = []
for sockets in sockets_combinations:
    tot_socket = Stats('0', 'SOCKETS')
    for socket in sockets:
        tot_socket += socket
    itemized_sockets.append(tot_socket)

print(len(itemized_sockets))
itemized_sockets = list(filter(Stats.maxed_crit, itemized_sockets))
print(len(itemized_sockets))
itemized_sockets = list(filter(Stats.maxed_maxi, itemized_sockets))
print(len(itemized_sockets))

itemized_sockets_ids = np.arange(len(itemized_sockets))

print(f'Generating sockets combinations: Completed ({time.time()-start_time}s)')
print(f'Size itemized_sockets: {sys.getsizeof(itemized_sockets)}')




#=========================combinatory for all items=============================#
print('Generating Items combinations, Starting')
start_time = time.time()

combs = np.array(np.meshgrid(*all_items_ids_filtered, itemized_sockets_ids))
combs = combs.T.reshape(-1,len([*all_items_ids_filtered, itemized_sockets_ids]))
print(combs)

#combs = list(product(*list(items_in_slot_filtered), itemized_sockets))

#combs = random.sample(combs, 100000)
#combs = combs[::500]

combs_len = len(combs)
print(f'Total combinations: {combs_len}')

print(f'Total combinations as expected: {combs_len==(all_items_ids_filtered_len*sockets_combinations_len)}')
print(f'Combinations, Complete ({time.time()-start_time}s)')

print(f'Size combs: {sys.getsizeof(combs)}')


#=============================create specific items ============================#
base_class_stats_item       = Stats('base','class base stats','',attributes=base_class_stats)
head_hunter_force_passive   = Stats('HH','unique HH','',attributes=head_hunter)

new_character = Character('Char', '')
new_character = new_character.equip(base_class_stats_item, base_class_stats_item.slot)
new_character = new_character.equip(head_hunter_force_passive, head_hunter_force_passive.slot)

print(f'Combination evaluation, Starting...')
start_time = time.time()
mul_list = np.empty(combs_len)

for i, items in enumerate(combs):
    # create a new "character" for each item combination
    new_character.name = 'jeff_%s'%(i)
    new_character.items = {}
    new_character.attributes = {}

    # add the sockets item with is a Stats object
    new_character.equip(itemized_sockets[items[-1]], 
                        itemized_sockets[items[-1]].slot)
    
    # equip all itemsD
    for j in items[:-1]:
        new_character.equip(all_items[j], 
                            all_items[j].slot)
    
    mul_list[i] = new_character.get_mul()
    
    print(i/combs_len,end='\r')

print(f'Combination evaluation, Complete ({time.time()-start_time}s)')



#==============apply the damage calculation to each character===================#
#print(mul_list)

m = np.argmax(mul_list)
print(mul_list[m])

best_comb = combs[m]

print('best_comb',best_comb)


best_character = Character('Char', '')
base_class_stats_item = Stats('base','class base stats','',attributes=base_class_stats)
head_hunter_force_passive = Stats('HH','unique HH','',attributes=head_hunter)

best_character = best_character.equip(base_class_stats_item, base_class_stats_item.slot)
best_character = best_character.equip(head_hunter_force_passive, head_hunter_force_passive.slot)

best_character = best_character.equip(itemized_sockets[best_comb[-1]], itemized_sockets[best_comb[-1]].slot)

for id in best_comb[:-1]:
    best_character = best_character.equip(all_items[id], all_items[id].slot)

#print(best_character)
best = best_character.get_damage()

print(best)


#=========================save to file best N entries===========================#
with open(file_path, "w") as file:
    file.write(f'Latest update: {datetime.now()}\n')
    
    output_string = f"{math.trunc(best[0]):<10}{math.trunc(best[1]):<10}\n{best[2]}\n"
    
    file.write(output_string.replace('|0.0','|   '))
    
print('DONE')