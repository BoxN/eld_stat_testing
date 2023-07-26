from stats import Stats

DEMON_REALM_DEBUFF = 0.9
DMG_TYPE = 'mag' # can be 'mag' or 'phys'

class Character(Stats):
    
    def __init__(self, id, name, set, attributes={}):
        
        # Stats
        super().__init__(id, name, set, attributes)
        
        self.items = {}

        # all sockets are 6% sage
        self.sockets_count = 16
        self.sockets = []
        
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
                self.attributes['crit'] = norm_crit
                break
            else:
                self.attributes['crit'] -= x
                norm_crit += x*r
        
        
        norm_maxi = 0
        for x, r in [(40, 1), (40, 0.75), (40, 0.5), (40, 0.25)]:
            if self.attributes['maxi'] <= x:
                norm_maxi += self.attributes['maxi']*r
                self.attributes['maxi'] = norm_maxi
                break
            else:
                self.attributes['maxi'] -= x
                norm_maxi += x*r
        
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
        self.apply_normalization()

        tot = 1
        tot *= (1+self.attributes['dmg_per']/100)*(1+self.attributes['dmg_per_m']/100)
        tot *= 0.5+self.attributes['maxi']/100
        tot *= 1+self.attributes['crit']/100*(1+self.attributes['crit_dmg']/100)
        tot *= 1+self.attributes['specific']/100
        tot *= 1+self.attributes['pola']/100
        tot *= 1+self.attributes['all_s_dmg']/100
        tot *= 1+self.attributes['boss_dmg']/100
        tot *= (1-DEMON_REALM_DEBUFF+self.attributes['adapt']/100)/(1-DEMON_REALM_DEBUFF)
        tot *= 1+self.attributes['cdr']/100
        
        
        #self.items = {}
        
        if DMG_TYPE == 'phys':
            tot = tot*self.attributes['phy_atk']
        elif DMG_TYPE == 'mag':
            tot = tot*self.attributes['mag_atk']
            
        return [tot, self]
    
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

        return s + '\n'

