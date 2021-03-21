from collections import UserList
from typing import Callable

import itertools
from utils import *
from grammar import Grammar

class PhSequence(UserList):
    def __init__(self, stuff):
        super().__init__(stuff)
    def __str__(self):        
        return PhSequence._polynomial_to_str(self)
    def __repr__(self):
        return str(self)
    @staticmethod
    def _polynomial_to_str(item_list : list) -> str:
        string = ''
        for item in item_list:
            if isinstance(item, Polynomial) and (len(item) > 1 or isinstance(item[0], Polynomial)):
                string = string + '[' + PhSequence._polynomial_to_str(item.ordered_children) + ']' + item[Monomial.CATEGORY] + ' '
            else:
                string = string + item[Monomial.FORM] + '_' + item[Monomial.CATEGORY] + ' '
        return string.rstrip()

class PossibilityScorer():
    def __init__(self, score_fn = None):
        #self._score_fn = score_fn if score_fn else PossibilityScorer.default_heuristic
        if score_fn:
            self.score = score_fn
    def score(self, possibility) -> float:
        return float(-len(possibility))
    # @staticmethod
    # def default_heuristic(possibility) -> float:
    #     return float(-len(possibility))
    

class Possibility:
    id_count = 0
    # Edge = namedtuple('Edge', ['rule', 'possibility'])
    def __init__(self, item_list: PhSequence, index, heuristic_scorer: PossibilityScorer = PossibilityScorer(),
                 parent=None, rule=None):
        self.item_list = PhSequence(item_list)
        self.index = index
        self.possibilities = None
        self.parent = parent
        self.rule = rule
        self.depth = self.parent.depth + 1 if self.parent else 0
        self.heuristic_scorer = heuristic_scorer
        self.id = Possibility.id_count
        self.error_score = sum([i.error_score for i in self.item_list])
        self.score = heuristic_scorer.score(self) - self.error_score
        Possibility.id_count += 1
    def calculate_score(self):
        self.score = self.heuristic_scorer.score(self) - self.error_score
    def __eq__(self, other):
        if not isinstance(other, Possibility):
            return False
        # this is not pythonic
        if self.index != other.index:
            return False
        if len(self.item_list) != len(other.item_list):
            return False
        for i in self.item_list:
            if i not in other.item_list:
                return False
        return True
    def __getitem__(self, item):
        return self.item_list[item]
    def __len__(self):
        return len(self.item_list)
    def expand_possibilities(self, rule_list:list):
        self.possibilities = list()        
        for rule in rule_list: # let's apply the rules
            # extract elements to apply rule to
            candidates = self.item_list[self.index:self.index + len(rule)]
            if len(candidates) != len(rule): # not enough candidates
                continue
            for i in range(0, len(candidates)): # add position info
                candidates[i]['pos'] = str(i)
            # it's a free-order language, do permutations
            for permutation in itertools.permutations(candidates):
                new_phrase:Polynomial = rule.apply(permutation)
                if not new_phrase: continue
                if new_phrase.error_score == float('inf'): # infinite error score! bad
                    continue # skip this possibility
                # let's add the possibility
                new_items = self.item_list.copy()
                del(new_items[self.index:self.index + len(rule)]) # remove the nodes
                new_items.insert(self.index, new_phrase)
                new_possibility = Possibility(PhSequence(new_items), self.index, self.heuristic_scorer, self, rule)
                self.possibilities.append(new_possibility)
        # add previous and next index possibilities, applying no rule
        # if self.index > 0:
        #     self.possibilities.append(Possibility(self.item_list.copy(), self.index - 1, self))
        if self.index < len(self.item_list) - 1:
            self.possibilities.append(Possibility(self.item_list.copy(), self.index + 1, self.heuristic_scorer, self, +1))
        if self.index > 0:
            self.possibilities.append(Possibility(self.item_list.copy(), self.index - 1, self.heuristic_scorer, self, -1))
        self.possibilities.reverse() # last one gets picked first. apply rules in order
    def __str__(self):
        string = str(self.item_list)
        string = string + ' score = ' + str(self.score) + ' index = ' + str(self.index)
        return str(self.id) + ' ' + string + \
               (' parent = ' + str(self.parent.id) + '\n' if self.parent else '')
    def __repr__(self):
        # return nodelist_string(self.item_list)
        return str(self)

    def traverse(self):
        yield self
        if self.possibilities:
            for child in self.possibilities:
                for n in child.traverse():
                    yield n

def default_halt_condition(p : Possibility) -> bool:
    return len(p.item_list) == 1

 

class Search:
    def __init__(self, item_list, grammar : Grammar, heuristic_scorer : PossibilityScorer =PossibilityScorer()):
        Possibility.id_count = 0
        self.grammar = grammar
        self.root = Possibility(item_list, 0, heuristic_scorer, None, None)
        self.dead_end_queue = []
        self.expandable_queue : list = [self.root]
        self.finished = []
        self.heuristic_scorer = heuristic_scorer
    def all_nodes(self) -> list:
        return self.dead_end_queue + self.expandable_queue + self.finished
    def change_scorer(self, heuristic_scorer : PossibilityScorer):
        self.heuristic_scorer = heuristic_scorer
        for p in self.all_nodes():
            p.heuristic_scorer = heuristic_scorer
            p.calculate_score()
    def expand(self, node:Possibility) -> Possibility:
        """Expands the best possibility """
        if not self.expandable_queue:
            return None        
        self.expandable_queue.remove(node)  # move from expandable to dead-end, 
        self.dead_end_queue.append(node)    # since we're going to expand all its possibilities
        node.expand_possibilities(self.grammar) # expand
        # remove possibilities that already appear
        node.possibilities = [p for p in node.possibilities
                              if p not in self.all_nodes()]
        self.expandable_queue = self.expandable_queue + node.possibilities # add new possibilities to queue
        self.expandable_queue.sort(key=lambda p: p.score) # sort queues
        self.dead_end_queue.sort(key=lambda p: p.score)
        return node

    def search(self, halt_condition : Callable[[Possibility], bool] = default_halt_condition):
        while self.expandable_queue:
            best = self.expandable_queue[-1]
            if halt_condition(best):
                self.expandable_queue.remove(best)
                self.finished.append(best)
                return best
            # best : Possibility = self.expand()
            if not self.expand(best): # should not be necessary
                continue
            # self.dead_end_queue.remove(best)
            # self.finished.append(best)
        return self.dead_end_queue[-1]

    def __str__(self):
        return 'Expandable\n' + str(self.expandable_queue) + '\n' #\
               #+ 'Dead-End\n' + str(self.dead_end_queue) + '\n'
    def __repr__(self):
        return str(self)

    def traverse(self):
        for n in self.root.traverse():
            yield n
    