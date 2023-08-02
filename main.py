from functools import reduce
import sys
import time
import math
import numpy as np
import pandas as pd
from itertools import combinations_with_replacement
from datetime import datetime
from multiprocessing import Process

from stats import Stats
from character import Character

# File path and name
file_path = "res.txt"
SLOT_NUMER = 37

 #==============base stats for a specific class (not present in db)==============#
 
BASE_STAT_CLASS    = { 'phy_atk':1202,	'mag_atk':1202,	'phy_def':301,	'mag_def':301,	'hp':157000,
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

HEAD_HUNTER = {'dmg_per':-24, 'boss_dmg':80}

def task(tid, combs, i, j, itemized_sockets, all_items, res):
        
    #=============================create specific items ============================#
    BASE_STAT_CLASS_item = Stats('base','class base stats','',attributes=BASE_STAT_CLASS)
    HEAD_HUNTER_force_passive = Stats('HH','unique HH','',attributes=HEAD_HUNTER)

    new_character = Character('Char', '')
    new_character = new_character.equip(BASE_STAT_CLASS_item, BASE_STAT_CLASS_item.slot)
    new_character = new_character.equip(HEAD_HUNTER_force_passive, HEAD_HUNTER_force_passive.slot)
    
    for ii, items in enumerate(combs[i:j]):
        # create a new "character" for each item combination
        new_character.name = 'jeff_%s_%s'%(tid, ii)
        new_character.items = {}
        new_character.attributes = {}

        # add the sockets item with is a Stats object
        
        new_character = new_character.equip(itemized_sockets[items[-1]], itemized_sockets[items[-1]].slot)
        
        # equip all itemsD
        for id in items[:-1]:
            new_character = new_character.equip(all_items[id], all_items[id].slot)
        
        res[tid*(j-i)+ii] = new_character.get_mul()



if __name__ == "__main__": 
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

    #============================sockets combinations===============================#
    avail_sockets = [  
                        Stats('0', 'socket', attributes={'maxi':12}),
                        Stats('0', 'socket', attributes={'crit':12}),
                        Stats('0', 'socket', attributes={'boss_dmg':5})
                    ]

    print(f'Generating sockets combinations: Started')
    start_time = time.time()
    # generate combinations
    sockets_combinations = list(combinations_with_replacement(avail_sockets, 19))

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
    print('minus maxed_crit', len(itemized_sockets))
    itemized_sockets = list(filter(Stats.maxed_maxi, itemized_sockets))
    print('minus maxed_maxi', len(itemized_sockets))

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


    #=============================multithreading============================#
    start_time = time.time()  
    num_tasks = 16

    indexes = np.arange(0, combs_len+1, combs_len/num_tasks, dtype=int)


    res = np.zeros(combs_len)
    process = [ Process(target=task, args=(id, combs, indexes[i], indexes[i+1], itemized_sockets, all_items, res)) 
                for id, i in enumerate(np.arange(num_tasks)) ]

    print('started process:',len(process))
    print('Item placement and damage calculation, Starting')
    # run the process
    for t in process:
        t.start()
    # wait for the process to finish
    print('Waiting for the thread...')

    mul_list = []

    for t in process:   
        t.join()
    print(f'\nItem placement and damage calculation, Complete ({time.time()-start_time}s)')
    #print(f'Size mul_list: {sys.getsizeof(mul_list)}')

    print(res)



    #==============apply the damage calculation to each character===================#
    print(type(res))
    mul_list = res
    m = max(mul_list)
    print(m)
    best_comb_index = np.where(mul_list == m)[0]
    print(best_comb_index)
    best_comb = combs[best_comb_index][0]

    print('best_comb',best_comb)


    best_character = Character('Char', '')
    BASE_STAT_CLASS_item = Stats('base','class base stats','',attributes=BASE_STAT_CLASS)
    HEAD_HUNTER_force_passive = Stats('HH','unique HH','',attributes=HEAD_HUNTER)

    best_character = best_character.equip(BASE_STAT_CLASS_item, BASE_STAT_CLASS_item.slot)
    best_character = best_character.equip(HEAD_HUNTER_force_passive, HEAD_HUNTER_force_passive.slot)

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