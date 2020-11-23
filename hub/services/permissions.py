from flask import current_app as app
from flask_jwt_extended import current_user
from hub.exts import db
from hub.services.errors import UserNotAuthenticated, ActionNotAllowed


class Gate:

    @staticmethod
    def check(*args, **kwargs):
        """
        Check a set of gate functions, passed as args. Optionally pass other objects as kwargs
        as required by the gate function.
        """
        gate = Gate()

        try: 
            id = current_user.id
            gate.person = current_user
        except: 
            raise UserNotAuthenticated

        if "roles" in kwargs:
            roles = kwargs["roles"]
        else:
            roles = None

        if "abilities" in kwargs:
            abilities = kwargs["abilities"]
        else:
            abilities = None

        try:
            for f in args:
                if hasattr(gate, f) and callable(func := getattr(gate, f)):
                    func(**kwargs)
        except ActionNotAllowed:
            if not person_has(current_user, abilities, roles):
                raise ActionNotAllowed
        
        return True

    @staticmethod
    def run(ability, **kwargs):
        """
        Run an ability's gate function, specified in it's table row.
        """
        gate = Gate()
        gate.ability = ability
        gate.role    = ability.role
        gate.person  = ability.role.person

        if hasattr(gate, ability.gate_func) and callable(func := getattr(gate, ability.gate_func)):
            return func(**kwargs)
        
        return False

    def user_logged_on(self, **kwargs):
        return

    def user_is_person(self, **kwargs):
        """
        Check if user is the same as the person object
        """
        person = kwargs["person"]

        if person.id != self.person.id:
            raise ActionNotAllowed


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

    return can_user
