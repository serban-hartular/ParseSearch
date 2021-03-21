from collections import UserList, defaultdict
from grammar.constraint_rules import *
from grammar.constraints import Constraint


class Grammar(UserList):
    def __init__(self, rules = []):
        super().__init__()
        self.categories = set()
        self.add_rules(rules)
        
    def add_rules(self, rule_iter):
        for rule in rule_iter:
            self.add_rule(rule)
            
    def add_rule(self, rule : Rule):
        self.append(rule)
        self.categories.add(rule.ph_type)
        for req in rule.requirements:
            req: Constraint # add a category
            if req.lexpr[-1] == Monomial.CATEGORY and req.rexpr_str:
                self.categories.add(req.rexpr)
    
    def one_hot_encoder(self) -> dict:
        l = [0] * len(self.categories)  #a list of zeros
        encoder = defaultdict(lambda: l) # which is the default code for unknown symbols
        sorted_cats = list(self.categories) # make a sorted list of categories
        sorted_cats.sort()
        for i in range(len(sorted_cats)):
            code = l.copy() # copy the all-zero list
            code[i] = 1  # change one value to 1
            encoder[sorted_cats[i]] = code  # this is the code
        return encoder
        
