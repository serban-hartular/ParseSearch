
from collections import UserDict

class Monomial(UserDict):
    LEMMA = 'lemma'
    CATEGORY = 'CAT'
    FORM = 'form'
    POS = 'pos' # position
    def __init__(self, d):
        super().__init__(d)
        keys = set(self.keys())
        if Monomial.CATEGORY not in keys:
            print(Monomial.CATEGORY + ' not in ' + str(keys))
            raise Exception('Monomial must include %s data' % Monomial.CATEGORY)
        if Monomial.FORM not in keys:
            self[Monomial.FORM] = ''
        self.error_score = 0
        self.errors = list()
    def feature_set(self): # returns attributes except for reserved ones (CATEGORY and FORM)
        return set(self.keys()) - {Monomial.CATEGORY, Monomial.FORM, Monomial.POS}
    def category(self) -> str:
        return self[Monomial.CATEGORY]
    def form(self) -> str:
        return self[Monomial.FORM]
    def __getitem__(self, item):
        if item not in self.keys(): return None
        return super().__getitem__(item)
    def _get_feat_or_child(self, item) -> str:
        if item in self.keys():
            return self[item]
    # def __setitem__(self, key, value):
    #     try:
    #         iterator = iter(value)
    #         value = {v for v in iterator}
    #     except TypeError as te:
    #         value = {value}
    #     super().__setitem__(key, value)



class Polynomial(Monomial):
    def __init__(self, d):
        super().__init__(d)
        self.children = dict() # of monominals
        self[Monomial.FORM] = ''
        self.ordered_children = list()
        self.rule = None
    def add_child(self, deprel : str, child : Monomial, index:int = None):
        """ Adds deprel, child. Does not copy! """
        if deprel in self.children.keys():
            raise Exception('%s already has child %s' % (str(self), deprel))
        self.children[deprel] = child
        if index is None:
            index = int(child[Monomial.POS]) if child[Monomial.POS] else len(self.children)
        self.ordered_children.insert(index, child)
        self.error_score += child.error_score
        self[Monomial.FORM] = self.form()
    def form(self) -> str:
        return ' '.join([c.form() for c in self.ordered_children])
    def __getitem__(self, item):
        if isinstance(item, int):
            return self.ordered_children[item]
        if item in self.children.keys():
            return self.children[item]
        return super().__getitem__(item)
    def __eq__(self, other):
        if not isinstance(other, Polynomial):
            return False
        if self.data != other.data:
            return False
        if len(self.children) != len(other.children):
            return False
        # now to compare the kiddies. keep in mind that you may get deprels pcomp* and pcomp**
        for deprel1 in self.children.keys():
            match = False
            for deprel2 in other.children.keys():
                if deprel1.rstrip('*') == deprel2.rstrip('*') and \
                        self.children[deprel1] == other.children[deprel2]:
                    match = True
                    break
            if not match: # no match for deprel1 child
                return False
        return True
    # def __copy__(self):   # because WTF
    def copy(self):
        c = Polynomial(self.data)
        for deprel, child in self.children.items():
            c.add_child(deprel, child.copy())
        return c
    def _get_feat_or_child(self, item:str):
        if item in self.keys():
            return self[item]
        if item in self.children:
            return self.children[item]
        return None
    @staticmethod
    def get_path(node, path : list):
        path = path.copy()
        item = ''
        while path:
            if not node:
                return None
                #raise Exception('%s has no %s' % (item, path[0]))
            item = path.pop(0)
            node = node._get_feat_or_child(item)
        return node
    @staticmethod
    def set_path(node, path : list, value):
        path = path.copy()
        last = path.pop()
        parent = Polynomial.get_path(node, path)
        if parent is None: return # ! check behavior!
        parent[last] = value
    def __str__(self):
        string = str(self.data)
        if self.children:
            string = string + ' ' + str(set(self.children.keys()))
        return string
    def __repr__(self):
        string = ''
        for child in self.ordered_children:
            deprel = ''
            for k, v in self.children.items():
                if v is child:
                    deprel = k
                    break
            string += (deprel + ":'" + child.form() + "'" + ' ')
        return string + 'err: ' + str(self.error_score)


