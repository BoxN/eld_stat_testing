import copy

class Stats():
    
    attribute_labels = [
        'phy_atk', 
        'mag_atk',  
        'phy_def',
        'mag_def', 
        'hp',      
                
        'dmg_per',  
        'dmg_per_m',
        'crit',        
        'maxi',        
        'crit_dmg',
        
        'pola',
        'specific',
        'all_s_dmg',
        'boss_dmg',
        'adapt',
        
        'cdr'
    ]
    
    def __init__(self, id, name, set, attributes={}):
       
        # Base attributes
        self.id = id
        self.name = name
        self.set = set

        self.attributes = {}
        
        
        # save the passed attributes
        for key in Stats.attribute_labels:
            self.attributes[key] = 0
        
        for key in attributes:
            self.attributes[key] = attributes[key]
                
    
    @staticmethod
    def sum(stats_list):
        empty = Stats(0, 'TOTAL', '', {})
        for elem in stats_list:
            empty = empty + elem
        return empty
    
    @staticmethod
    def headers():
        s  = f"{'[id]':<10}"
        s += f"|{'name':<26}"
        s += f"|{'set':<10}"
        for key in Stats.attribute_labels:
            s += f"|{key:10}"
        return s

    
    def __add__(self, other):
        if isinstance(other, Stats):
            new_attributes = {}
            for key in Stats.attribute_labels:
                new_attributes[key] = self.attributes[key] + other.attributes[key]
            return Stats(0, 'TOTAL', '', new_attributes)
        else:
            raise TypeError("Unsupported operand type for +")
        
    def __str__(self) -> str:
        
        s =  f"{self.id                     :10}"
        s += f"|{self.name                  :26}"
        s += f"|{self.set                   :10}"
        for key in Stats.attribute_labels:
            s += f"|{self.attributes[key]:<10}"
        return s

    
