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
        'maxi',
        'crit',            
        'crit_dmg',
        
        'pola',
        'specific',
        'all_s_dmg',
        'boss_dmg',
        'adapt',
        
        'cdr',
        'dmg_with_hp',
        'cont_dmg'
    ]
    
    def __init__(self, slot, name, set='', attributes={}):
       
        # Base attributes
        self.slot = slot
        self.name = name
        self.set = set

        self.attributes = {}
        
        
        # save the passed attributes
        for key in Stats.attribute_labels:
            if key in attributes:
                self.attributes[key] = attributes[key]
            else:
                self.attributes[key] = 0.0
        
        #for key in attributes:
        #    self.attributes[key] = attributes[key]
        
    @staticmethod
    def maxed_crit(self):
        return self.attributes['crit'] <= 140
    
    @staticmethod
    def maxed_maxi(self):
        return self.attributes['maxi'] <= 160
    
    @staticmethod
    def sum(stats_list):
        empty = Stats(0, 'TOTAL')
        for elem in stats_list:
            empty = empty + elem
        return empty
    
    @staticmethod
    def headers():
        s  = f"{'[slot]':<10}"
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
            return Stats(other.slot, self.name, other.set, new_attributes)
        else:
            raise TypeError("Unsupported operand type for +")
        
    def __str__(self) -> str:
        
        s =  f"{self.slot                     :10}"
        s += f"|{self.name                  :26}"
        s += f"|{self.set                   :10}"
        for key in Stats.attribute_labels:
            s += f"|{round(self.attributes[key],6):<10}"
        return s

    
