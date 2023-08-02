from functools import reduce
from stats import Stats

DEMON_REALM_DEBUFF = 0.9
DMG_TYPE = 'mag' # can be 'mag' or 'phys'

class Character(Stats):
    
    def __init__(self, slot, name, set='', attributes={}):
        
        # Stats
        super().__init__(slot, name, set, attributes)
        
        self.items = {}
        self.factors = None
        
        self.sets = [
            {'set':'chrimson',  'equiped':0, 'required':2, 'effect':{'pola':7}},
            {'set':'chrimson',  'equiped':0, 'required':4, 'effect':{'pola':13}},
            {'set':'sage',      'equiped':0, 'required':2, 'effect':{'all_s_dmg':10}},
            {'set':'sage',      'equiped':0, 'required':4, 'effect':{'crit_dmg':15}},
            {'set':'with hp',   'equiped':0, 'required':4, 'effect':{'dmg_per':5, 'adapt':2}},
            {'set':'reset',     'equiped':0, 'required':4, 'effect':{'cdr':8, 'adapt':2}},
            
            {'set':'SK_armor',  'equiped':0, 'required':2, 'effect':{'pola':2}},
            {'set':'SK_armor',  'equiped':0, 'required':4, 'effect':{'crit':7, 'all_s_dmg':4}},
            {'set':'SK_armor',  'equiped':0, 'required':5, 'effect':{'adapt':5}},
            {'set':'SK_weap',   'equiped':0, 'required':2, 'effect':{'all_s_dmg':3}},
            {'set':'SK_weap',   'equiped':0, 'required':3, 'effect':{'pola':5, 'all_s_dmg':2}},
            {'set':'SK_weap',   'equiped':0, 'required':4, 'effect':{'mov':5, 'jump':5}},
            
            {'set':'DrA_armor',  'equiped':0, 'required':2, 'effect':{'cont_dmg':2, 'crit':2}},
            {'set':'DrA_armor',  'equiped':0, 'required':4, 'effect':{'adapt':3, 'maxi':5}},
            {'set':'DrA_armor',  'equiped':0, 'required':5, 'effect':{'pola':5}},
            {'set':'DrA_weap',   'equiped':0, 'required':2, 'effect':{'pola':3, 'crit':5}},
            {'set':'DrA_weap',   'equiped':0, 'required':3, 'effect':{'cont_dmg':5, 'all_s_dmg':2}}
        ]
    
    # sum all
    def calculate(self):
        
        total = Stats('TOTAL','result')
        for placement, item in self.items.items():
            total += item
        
        self.attributes = total.attributes
        return self
    
    # assign an item to a slot
    def equip(self, item, placement):
        self.items[placement] = item
        return self
    
    # change some stats acording to normalization steps
    def apply_normalization(self):
        
        # normalize crit according to the efficency steps
        norm_crit = 0
        for x, r in [(40, 1), (35, 0.8), (30, 0.6), (35, 0.4)]:
            if self.attributes['crit'] <= x:
                norm_crit += self.attributes['crit']*r
                self.attributes['crit'] = 0
            else:
                self.attributes['crit'] -= x
                norm_crit += x*r
        # override previous value
        self.attributes['crit'] = norm_crit
        
        # normalize maxi according to the efficency steps
        norm_maxi = 0
        for x, r in [(40, 1), (40, 0.75), (40, 0.5), (40, 0.25)]:
            if self.attributes['maxi'] <= x:
                norm_maxi += self.attributes['maxi']*r
                self.attributes['maxi'] = 0
            else:
                self.attributes['maxi'] -= x
                norm_maxi += x*r
        # override previous value
        self.attributes['maxi'] = norm_maxi
        
        return self

    def apply_sets(self):
        
        # check all equiped items
        for item in self.items.values():
            # crosscheck all the available set effect
            for set in self.sets:
                
                # update item count for set (2/5, 3/5, 5/5 complete)
                if item.set == set['set']:
                    set['equiped'] += 1
        
        # iterate and equip the set effect when the requirement are satisfied 
        for set in self.sets:
            if set['equiped'] >= set['required']:
                
                # create an item from the set effect stats
                set_item = Stats('set',set['set'], set['required'], attributes=set['effect'])
                
                # assign the item to a custom slot or add of already existing
                if set_item.name in self.items:
                    self.items[set_item.name] += set_item
                else:
                    self.items[set_item.name] = set_item
          
        return self
    def get_damage(self):
        self = self.apply_sets()
        self = self.calculate()
        
        #print('pre',self.attributes['crit'])
        self = self.apply_normalization()
        #print('post',self.attributes['crit'])
        
        all_factors = {}
        
        all_factors['dmg_per_m']     = 1
        all_factors['dmg_per']       = (1+self.attributes['dmg_per']/100)*(1+self.attributes['dmg_per_m']/100)
        all_factors['dmg_with_hp']   = (1+self.attributes['dmg_with_hp']/100)*0.8
        all_factors['maxi']          = 0.5+self.attributes['maxi']/100
        
        all_factors['crit_dmg']      = self.attributes['crit']/100*self.attributes['crit_dmg']/100+1.5
        all_factors['crit']          = 1
        
        all_factors['specific']      = 1+self.attributes['specific']/100
        all_factors['pola']          = 1+self.attributes['pola']/100
        all_factors['all_s_dmg']     = 1+self.attributes['all_s_dmg']/100
        all_factors['boss_dmg']      = 1+self.attributes['boss_dmg']/100
        all_factors['adapt']         = (1-DEMON_REALM_DEBUFF+self.attributes['adapt']/100)/(1-DEMON_REALM_DEBUFF)
        all_factors['cdr']           = 1+self.attributes['cdr']/100
        all_factors['cont_dmg']      = 1+self.attributes['cont_dmg']/100
        
        
        self.factors = Stats('Result','FACTORS',attributes=all_factors)
        
        mul = reduce(lambda a,b: a*b, all_factors.values())
          
        return mul
    
    def get_mul(self):
        self = self.apply_sets()
        self = self.calculate()
        
        if self.attributes['crit'] > 150:
            return 0
        
        if self.attributes['maxi'] > 170:
            return 0
        
        #print('pre',self.attributes['crit'])
        self = self.apply_normalization()
        #print('post',self.attributes['crit'])
        
        all_factors = {}
        
        all_factors['dmg_per_m']     = 1
        all_factors['dmg_per']       = (1+self.attributes['dmg_per']/100)*(1+self.attributes['dmg_per_m']/100)
        all_factors['dmg_with_hp']   = (1+self.attributes['dmg_with_hp']/100)*0.8
        all_factors['maxi']          = 0.5+self.attributes['maxi']/100
        
        all_factors['crit_dmg']      = self.attributes['crit']/100*self.attributes['crit_dmg']/100+1.5
        all_factors['crit']          = 1
        
        all_factors['specific']      = 1+self.attributes['specific']/100
        all_factors['pola']          = 1+self.attributes['pola']/100
        all_factors['all_s_dmg']     = 1+self.attributes['all_s_dmg']/100
        all_factors['boss_dmg']      = 1+self.attributes['boss_dmg']/100
        all_factors['adapt']         = (1-DEMON_REALM_DEBUFF+self.attributes['adapt']/100)/(1-DEMON_REALM_DEBUFF)
        all_factors['cdr']           = 1+self.attributes['cdr']/100
        all_factors['cont_dmg']      = 1+self.attributes['cont_dmg']/100
        
        
        self.factors = Stats('Result','FACTORS',attributes=all_factors)
        
        mul = reduce(lambda a,b: a*b, all_factors.values())
        
        #print(self.attributes['crit'], all_factors['crit'], all_factors['crit_dmg'])

        
        if DMG_TYPE == 'phys':
            tot = mul*self.attributes['phy_atk']
        elif DMG_TYPE == 'mag':
            tot = mul*self.attributes['mag_atk']
            
        return mul
    
    @staticmethod
    def headers():
        s  = f"{'TOTAL':12}"
        s += Stats.headers()
        return s
    
    def __gt__(self, other):
        return self.tot > other.tot
    
    def __str__(self):
        s = ''
        if self.items:
            s = Stats.headers() + '\n'
        for obj in self.items.values():
            s += f"{obj}\n"
        s += super().__str__()
        s += f"\n{self.factors}"
        return s + '\n'

