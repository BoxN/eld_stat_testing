import copy
class Stats:
    
    def __init__(self, id, name, group):
        # Base attributes
        self.id = id
        self.name = name
        
        # Stats
        self.damage_percent     = group[0]
        self.critical           = group[1]
        self.maxi               = group[2]
        self.critical_damage    = group[3]

        self.tot = self.get_damage()
    
    def equip(self, other):
        
        new_self = copy.deepcopy(self)

        new_self.id = other.id
        
        #   stats with normalization
        new_self.critical   = 0
        new_self.maxi       = 0
        
        for step, normalization in [(40,1), (35,0.8), (30,0.6), (35,0.4)]:
            if other.critical > step:
                other.critical -= step
                new_self.critical += step*normalization
            else:
                new_self.maxi += other.maxi*normalization
                break
            
        for step, normalization in [(40,1), (40,0.75), (40,0.5), (40,0.25)]:
            if other.new_self.maxi > step:
                other.new_self.maxi -= step
                new_self.maxi += step*normalization
            else:
                new_self.maxi += other.new_self.maxi*normalization
                break
        
        #   free stats
        new_self.damage_percent     += other.damage_percent
        new_self.critical_damage    += other.critical_damage
        
        
        new_self.tot = new_self.get_damage()
        return new_self
    
    def get_damage(self):
        tot = 1
        tot *= 1+self.damage_percent/100
        tot *= 0.5+self.maxi/100
        tot *= 1+self.critical/100*(1-self.critical_damage/100)
        return tot
    
    @staticmethod
    def headers():
        t = '\t\t'
        s  = '[id]'+t
        s += '|tot\t'
        s += '|dmg%\t'
        s += '|maxi\t'
        s += '|crit\t'
        s += '|crit_dmg\t'
        return s
    
    def __gt__(self, other):
        return self.tot > other.tot
    
    def __str__(self):
        t = '\t\t'
        s  = f'[{self.id}]'+t
        s += f'|{self.tot:0.4f}\t'
        s += f'|{self.damage_percent:0.2f}\t'
        s += f'|{self.maxi:0.2f}\t'
        s += f'|{self.critical:0.2f}\t'
        s += f'|{self.critical_damage:0.2f}\t'
        return s

