import copy

class Stats():
    
    def __init__(self, id, name, set, base=None) -> None:
       
        # Base attributes
        self.id = id
        self.name = name
        self.set = set

        # Base Stats
        self.physical_attack    = base["physical_attack"]   if "physical_attack" in base else 0
        self.magical_attack     = base["magical_attack"]    if "magical_attack" in base else 0
        self.physical_defense   = base["physical_defense"]  if "physical_defense" in base else 0
        self.magical_defense    = base["magical_defense"]   if "magical_defense" in base else 0
        self.hp                 = base["hp"]                if "hp" in base else 0

        self.damage_percent     = base["damage_percent"]    if "damage_percent" in base else 0
        self.critical           = base["critical"]          if "critical" in base else 0
        self.maximize           = base["maximize"]          if "maximize" in base else 0
        self.critical_damage    = base["critical_damage"]   if "critical_damage" in base else 0

    def calculate(self, other):
        self.physical_attack    += other.physical_attack
        self.magical_attack     += other.magical_attack
        self.physical_defense   += other.physical_defense
        self.magical_defense    += other.magical_defense
        self.hp                 += other.hp
        
        self.damage_percent     += other.damage_percent
        self.critical_damage    += other.critical_damage
        self.critical           += other.critical
        self.maximize           += other.maximize
        
        
    
    @staticmethod
    def headers():
        s  = f"{'[id]'          :10}"
        s += f"|{'name'         :26}"
        s += f"|{'set'          :10}"
        s += f"|{'phys_atk'     :10}"
        s += f"|{'mag_atk'      :10}"
        s += f"|{'phys_def'     :10}"
        s += f"|{'mag_def'      :10}"
        s += f"|{'hp'           :10}"
        s += f"|{'dmg_perc'     :10}"
        s += f"|{'critical'     :10}"
        s += f"|{'maximize'     :10}"
        s += f"|{'crit_dmg'     :10}"
        return s + "\n"
     
    def __str__(self) -> str:
        
        s =  f"{self.id                     :10}"
        s += f"|{self.name                  :26}"
        s += f"|{self.set                   :10}"
        s += f"|{self.physical_attack       :10}"
        s += f"|{self.magical_attack        :10}"
        s += f"|{self.physical_defense      :10}"
        s += f"|{self.magical_defense       :10}"
        s += f"|{self.hp                    :10}"
        s += f"|{self.damage_percent        :10}"
        s += f"|{self.critical              :10}"
        s += f"|{self.maximize              :10}"
        s += f"|{self.critical_damage       :10}"
        return s + "\n"

    
class Character(Stats):

    def __init__(self, id, name, set, base=None):
        
        # Stats
        super().__init__(id, name, set, base)
        
        self.items = {}

        sets = [
            {'set':'rigo_chrimson','equiped':0, 'required':2, 'effect':{'damage_percent':7}},
            {'set':'rigo_chrimson','equiped':0, 'required':4, 'effect':{'damage_percent':7}}
        ]
    
    
    
    def calculate(self):
        
        for placement, item in self.items.items():
            super().calculate(item)
        
        return self
    
    def equip(self, item, placement):
        self.items[placement] = item
    
    def apply_normalization(self):
        
        norm_crit = 0
        for x, r in [(40, 1), (35, 0.8), (30, 0.6), (35, 0.4)]:
            if self.critical <= x:
                norm_crit += self.critical*r
                self.critical = norm_crit
                break
            else:
                self.critical -= x
                norm_crit += x*r
        
        
        norm_maxi = 0
        for x, r in [(40, 1), (40, 0.75), (40, 0.5), (40, 0.25)]:
            if self.maximize <= x:
                norm_maxi += self.maximize*r
                self.maximize = norm_maxi
                break
            else:
                self.maximize -= x
                norm_maxi += x*r
        

        return self

    def apply_sets(self):
        
        if 
        
        return self
        
    def get_damage(self):
        tot = 1
        tot *= 1+self.damage_percent/100
        tot *= 0.5+self.maximize/100
        tot *= 1+self.critical/100*(1-self.critical_damage/100)
        
        return [tot, self]
    
    @staticmethod
    def headers():
        s  = f"{'TOTAL':12}"
        s += Stats.headers()
        return s
    
    def __gt__(self, other):
        return self.tot > other.tot
    
    def __str__(self):
        
        s = Stats.headers()
        for obj in self.items.values():
            s += f"{obj}"
        s += super().__str__() + "\n"
        return s  + "\n"

