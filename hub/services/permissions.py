from flask import current_app as app
from hub.exts import db


class Gates:

    def __init__(self, ability):
        self.ability = ability
        self.role    = ability.role
        self.person  = ability.role.person

    @staticmethod
    def run(ability):
        gate = Gates(ability)
        if hasattr(gate, ability.gate_func) and callable(func := getattr(gate, ability.gate_func)):
            return func()
        
        return False

    def person_is_active(self):
        return True



def person_has(person, abilities, roles):
    if roles is None and abilities is None:
        return True
    else:
        can_user = False

    if abilities is not None:
        pa = []
        for pr in person.roles:
            pa.append(*pr.abilities)

        try:
            i = iter(abilities)
            for a in abilities:
                if a in pa and pa.run_gate():
                    can_user = True
        except:
            raise ValueError("abilities must be None, list or tuple")
    
    if roles is not None:
        try:
            i = iter(roles)
            for r in roles:
                if r in person.roles:
                    can_user = True
        except:
            raise ValueError("roles must be None, list or tuple")
        
