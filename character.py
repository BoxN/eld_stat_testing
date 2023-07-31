from stats import Stats

DEMON_REALM_DEBUFF = 0.9
DMG_TYPE = 'mag' # can be 'mag' or 'phys'

class Character(Stats):
    
    def __init__(self, id, name, set, attributes={}):
        
        # Stats
        super().__init__(id, name, set, attributes)
        
        self.items = {}
        self.factors = None
        
        self.sets = [
            {'set':'Chrimson',  'equiped':0, 'required':2, 'effect':{'pola':7}},
            {'set':'Chrimson',  'equiped':0, 'required':4, 'effect':{'pola':13}},
            {'set':'Sage',      'equiped':0, 'required':2, 'effect':{'all_s_dmg':10}},
            {'set':'Sage',      'equiped':0, 'required':4, 'effect':{'crit_dmg':15}},
            {'set':'With HP',   'equiped':0, 'required':4, 'effect':{'dmg_per':5, 'adapt':2}},
            {'set':'Reset',     'equiped':0, 'required':4, 'effect':{'cdr':20, 'adapt':2}},
        ]
    def calculate(self):
        
        total = Stats('TOTAL','','')
        for placement, item in self.items.items():
            total += item
        
        self.attributes = total.attributes
        return self
    
    def equip(self, item, placement):
        self.items[placement] = item
        return self
    
    def apply_normalization(self):
        
        norm_crit = 0
        for x, r in [(40, 1), (35, 0.8), (30, 0.6), (35, 0.4)]:
            if self.attributes['crit'] <= x:
                norm_crit += self.attributes['crit']*r
                self.attributes['crit'] = 0
            else:
                self.attributes['crit'] -= x
                norm_crit += x*r
        self.attributes['crit'] = norm_crit
        
        norm_maxi = 0
        for x, r in [(40, 1), (40, 0.75), (40, 0.5), (40, 0.25)]:
            if self.attributes['maxi'] <= x:
                norm_maxi += self.attributes['maxi']*r
                self.attributes['maxi'] = 0
            else:
                self.attributes['maxi'] -= x
                norm_maxi += x*r
        self.attributes['maxi'] = norm_maxi
        return self

    def apply_sets(self):
        
        for key, item in self.items.items():
            
            for set in self.sets:
                if item.set == set['set']:
                    set['equiped'] += 1
                   
        for i, set in enumerate(self.sets):
            if set['equiped'] >= set['required']:
                set_item = Stats('set',set['set'],set['required'],attributes=set['effect'])
                self.items[str(i)] = set_item
                
        return self
    def get_damage(self):
        
        self.apply_sets()
        self.calculate()
        #print('pre',self.attributes['maxi'])
        self.apply_normalization()
        #print('post',self.attributes['maxi'])
        
        all_factors = {}
        
        all_factors['dmg_per']       = 1+self.attributes['dmg_per']/100
        all_factors['dmg_per_m']     = 1+self.attributes['dmg_per_m']/100
        all_factors['dmg_with_hp']   = 1+self.attributes['dmg_with_hp']/100
        all_factors['maxi']          = 0.5+self.attributes['maxi']/100
        all_factors['crit']          = self.attributes['crit']/100
        all_factors['crit_dmg']      = 1.5+self.attributes['crit_dmg']/100
        all_factors['specific']      = 1+self.attributes['specific']/100
        all_factors['pola']          = 1+self.attributes['pola']/100
        all_factors['all_s_dmg']     = 1+self.attributes['all_s_dmg']/100
        all_factors['boss_dmg']      = 1+self.attributes['boss_dmg']/100
        all_factors['adapt']         = (1-DEMON_REALM_DEBUFF+self.attributes['adapt']/100)/(1-DEMON_REALM_DEBUFF)
        all_factors['cdr']           = 1+self.attributes['cdr']/100
        
        self.factors = Stats(1,'FACTORS', '',attributes=all_factors)
        
        mul = 1
        mul *= all_factors['dmg_per']*all_factors['dmg_per_m']
        mul *= all_factors['dmg_with_hp']*0.8    # specifico per tene con "with hp" maxata a 80% HP
        mul *= all_factors['maxi']
        mul *= (all_factors['crit']*all_factors['crit_dmg'] 
                + all_factors['crit']*1.5)
        mul *= all_factors['specific']
        mul *= all_factors['pola']
        mul *= all_factors['all_s_dmg']
        mul *= all_factors['boss_dmg']
        mul *= all_factors['adapt']
        mul *= all_factors['cdr']
        
        
        
        if DMG_TYPE == 'phys':
            tot = mul*self.attributes['phy_atk']
        elif DMG_TYPE == 'mag':
            tot = mul*self.attributes['mag_atk']
            
        return [mul, tot, self]
    
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

