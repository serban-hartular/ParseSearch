from grammar.phrase_nodes import Polynomial, Monomial
from grammar.constraints import ConstraintReport, Constraint


class Rule:
    def __init__(self, ph_type:str, children_names:list, requirements : list, text:str = ''):#, append_flag = False):
        # if f
        self.ph_type = ph_type
        self.children_names = children_names     
        self.requirements = requirements
        self.text = text
        # self.append_flag = append_flag # if flat_flag, nodes will be appended, otherwise, new structure
    def apply(self, children:list) -> Polynomial:
        phrase = self._build_phrase(children)
        if not phrase: return None
        self._apply_requirements(phrase)
        if Monomial.POS in phrase.keys():
            phrase.pop(Monomial.POS)
        phrase.rule = self
        return phrase
    def __len__(self):
        return len(self.children_names)
    def _build_phrase(self, children:list) -> Polynomial:
        if len(children) != len(self.children_names):
            # raise Exception('Wrong number of nodes %d for rule %s' % (len(children), str(self)))
            return None
        phrase = Polynomial({Monomial.CATEGORY: self.ph_type})
        for child_name, child in zip(self.children_names, children):
            phrase.add_child(child_name, child.copy())
        return phrase
    def _apply_requirements(self, phrase:Polynomial):
        requirement : Constraint
        for requirement in self.requirements:
            report:ConstraintReport = requirement.eval_and_resolve(phrase)
            if not report:
                phrase.errors.append(report)
                phrase.error_score += report.score
                # remove positions!
        for child in phrase.children.values():
            if Monomial.POS in child:
                child.pop(Monomial.POS)
        return phrase
    def __repr__(self):
        return self.ph_type + '->' + str(self.children_names)
    def __str__(self):
        string = repr(self)
        for requirement in self.requirements:
            string = string + '\n' + str(requirement)
        return string


class AppendRule(Rule):
    SELF = 'self'
    STAR = '*'
    def __init__(self, ph_type:str, children_names: list, requirements, text:str = ''):
        super().__init__(ph_type, children_names, requirements, text)
        if AppendRule.SELF not in children_names:
            raise Exception('Append Rule: parent must have deprel %s', AppendRule.SELF)
        self.self_index = children_names.index(AppendRule.SELF)

    def apply(self, nodes:list) -> Polynomial:
        if len(nodes) != len(self.children_names):
            # raise Exception('Wrong number of inputs %d for rule %s' % (len(nodes), str(self)))
            return None
        if not isinstance(nodes[self.self_index], Polynomial):
            return None
        phrase = self._build_phrase(nodes) # nodes[self.self_index].copy()
        if not phrase: # could not build. duplicate deprels
            return None
        self._apply_requirements(phrase)
        # after the requirements have been applied, set the childrens' 'pos' correctly
        for i, child in zip(range(0, len(phrase.ordered_children)), phrase.ordered_children):
            child[Monomial.POS] = str(i)
        # and remove one's own pos, which will be set when the next rule is applied
        if Monomial.POS in phrase.keys():
            phrase.pop(Monomial.POS)
        phrase.rule = self
        return phrase
    def _build_phrase(self, nodes:list) -> Polynomial:
        # It's more complicated. Need to mangle deprels can appear multiple times 
        original : Polynomial = nodes[self.self_index]
        phrase = Polynomial(Monomial(nodes[self.self_index])) # we copy the polynominal w/out the kids
        # extract deprels in rule that end with a star (where you can have more than one of that name)
        starred_deprels = {d for d in self.children_names if d.endswith(AppendRule.STAR)}
        # if these deprels are found among the original's nodes, they get an extra star
        for deprel, child in original.children.items():
            if [s for s in starred_deprels if deprel.startswith(s)]: # exists s s.t. deprel starts with it
                deprel = deprel + AppendRule.STAR # add another star to it so it won't match anymore
            phrase.add_child(deprel, child.copy())
        # now to add the nodes from the rules. We need to respect the order give by 'pos' in the node list
        ph_pos = int(phrase[Monomial.POS])
        sorted_items = [z for z in zip(self.children_names, nodes)]
        sorted_items.sort(key=lambda z : z[1][Monomial.POS]) # sort by 'pos'
        for i in range(0, len(sorted_items)):
            deprel, child = sorted_items[i]
            if deprel in phrase.children.keys():
                return None # already has this deprel
            if i < ph_pos:
                phrase.add_child(deprel, child.copy(), i)
            elif i > ph_pos:
                phrase.add_child(deprel, child.copy(), len(phrase.children))
        return phrase

    def __repr__(self):
        return self.ph_type + '+=' + str(self.children_names)


class Headed_Rule(Rule):
    def __init__(self, ph_type: str, children_names: list, head_name:str, attrib_dict:dict,
                 requirements: list, text:str = ''):
        super().__init__(ph_type, children_names, requirements, text)
        self.head_name = head_name
        if self.head_name not in children_names:
            raise Exception('head child "%s" not found in rule %s ' % (head_name, str(children_names)))
        self.attrib_dict = attrib_dict
    
    def apply(self, children:list) -> Polynomial:
        phrase = self._build_phrase(children)
        if not phrase: return None
        self._pass_head_attribs(phrase)
        self._apply_requirements(phrase)
        if Monomial.POS in phrase.keys():
            phrase.pop(Monomial.POS)
        phrase.rule = self
        return phrase
    
    def _pass_head_attribs(self, phrase:Polynomial):
        head = phrase.children[self.head_name]
        attribs = self.attrib_dict[self.ph_type] if self.attrib_dict else head.feature_set()
        for attrib in attribs:
            phrase[attrib] = head[attrib]
            
# class AppendRule_old(Rule):
#     SELF = 'self'
#     DOUBLE_DEPREL_ERROR = float('inf')
#     def __init__(self, ph_type:str, children_names: list, requirements, content:str = ''):
#         super().__init__(ph_type, children_names, requirements, content)
#         if AppendRule.SELF not in children_names:
#             raise Exception('Append Rule: one child must have deprel %s', AppendRule.SELF)
#         self.self_index = children_names.index(AppendRule.SELF)
# 
#     def apply(self, children:list) -> Polynomial:
#         if len(children) != len(self.children_names):
#             raise Exception('Wrong number of inputs %d for rule %s' % (len(children), str(self)))
#         phrase = children[self.self_index].copy()
#         if not isinstance(phrase, Polynomial): return None
#         for deprel, child in zip(self.children_names, children):
#             # for now we keep 'self' in the childrens list because the constraints expect this sh*t 
#             if deprel == AppendRule.SELF:
#                 pass
#             else:
#                 if deprel in phrase.children.keys(): # this deprel already appears
#                     # phrase.error_score = AppendRule.DOUBLE_DEPREL_ERROR
#                     return None
#                 phrase.add_child(deprel, child.copy())
#         self._apply_requirements(phrase)
#         return phrase
#     
#     def __repr__(self):
#         return self.ph_type + '+=' + str(self.children_names)
# 
