import functools

import sys
import time
import math
import numpy as np
import pandas as pd
import multiprocessing as mp

from itertools import combinations_with_replacement
from datetime import datetime

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

def task(tid, combs, i, j, new_character, itemized_sockets, all_items, res):
        
    
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
    all_items_ids_filtered_len = functools.reduce(lambda a, b: a*len(b), [1,*all_items_ids_filtered])
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


    #=============================create specific items ============================#
    BASE_STAT_CLASS_item = Stats('base','class base stats','',attributes=BASE_STAT_CLASS)
    HEAD_HUNTER_force_passive = Stats('HH','unique HH','',attributes=HEAD_HUNTER)

    new_character = Character('Char', '')
    new_character = new_character.equip(BASE_STAT_CLASS_item, BASE_STAT_CLASS_item.slot)
    new_character = new_character.equip(HEAD_HUNTER_force_passive, HEAD_HUNTER_force_passive.slot)
    
    
    #=============================multithreading============================#
    start_time = time.time()  
    num_tasks = 8

    indexes = np.arange(0, combs_len+1, combs_len/num_tasks, dtype=int)

    shared_mp_array = mp.Array('f', combs_len)
    #print(np.frombuffer(shared_mp_array.get_obj(), dtype=np.int32))
    processes = []
    
    for id, i in enumerate(range(num_tasks)):
        processes.append(mp.Process(target=task, 
                                    args=(  id, 
                                            combs, 
                                            indexes[i], 
                                            indexes[i+1], 
                                            new_character, 
                                            itemized_sockets, 
                                            all_items, 
                                            shared_mp_array)
                                    )
                         )

    print('started process:',len(processes))
    print('Item placement and damage calculation, Starting')
    
    # run the process
    for p in processes:
        p.start()
        
    print('Waiting for the process to finish...')

    while any(process.is_alive() for process in processes):
        time.sleep(10)
        print(1-np.sum(np.frombuffer(shared_mp_array.get_obj(), dtype=np.int32) == 0)/combs_len)
    
    
    for p in processes:   
        p.join()
    
    # Convert the shared array back to a NumPy array (if needed)
    shared_array = np.frombuffer(shared_mp_array.get_obj(), dtype=np.int32)
    
    print(f'\nItem placement and damage calculation, Complete ({time.time()-start_time}s)')
    #print(f'Size mul_list: {sys.getsizeof(mul_list)}')

    print(shared_array)



    #==============find the best multiplier and get the best set========================#
    m = max(shared_array)
    print('best multiplier',m)
    best_comb_index = np.where(shared_array == m)[0]
    print('best multiplier index',best_comb_index)
    best_comb = combs[best_comb_index][0]
    print('best combination',best_comb)

    # create best item combination
    best_character = Character('Char', '')
    BASE_STAT_CLASS_item = Stats('base','class base stats','',attributes=BASE_STAT_CLASS)
    HEAD_HUNTER_force_passive = Stats('HH','unique HH','',attributes=HEAD_HUNTER)

    # add base class item and force passives
    best_character = best_character.equip(BASE_STAT_CLASS_item, BASE_STAT_CLASS_item.slot)
    best_character = best_character.equip(HEAD_HUNTER_force_passive, HEAD_HUNTER_force_passive.slot)

    # add best sockets
    best_character = best_character.equip(itemized_sockets[best_comb[-1]], itemized_sockets[best_comb[-1]].slot)

    for id in best_comb[:-1]:
        best_character = best_character.equip(all_items[id], all_items[id].slot)

    #print(best_character)
    best = best_character.get_damage()
    print(best)

    #=========================save to file best entry==================================#
    with open(file_path, "w") as file:
        file.write(f'Latest update: {datetime.now()}\n')
        
        output_string = f"{math.trunc(best[0]):<10}{math.trunc(best[1]):<10}\n{best[2]}\n"
        
        file.write(output_string.replace('|0.0','|   '))
        
    print('DONE')