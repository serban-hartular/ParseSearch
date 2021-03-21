
# cyk parser
import itertools
from grammar.phrase_nodes import Monomial, Polynomial
from grammar import Grammar


class CYK_Parser:
    def __init__(self, sequence : list, grammar : Grammar, error_threshold = 1.0):
        # self.sequence = sequence
        self.grammar = grammar
        self.error_threshold = error_threshold
        self.table = []
        self.table.append(list())
        for item in sequence:
            self.table[0].append([item]) # bottom-most row, contains sequence
        for row in range(len(sequence)):
            vector = []
            for col in range(len(sequence)-row):
                vector.append([])
            self.table.append(vector)
    def __getitem__(self, item):
        return self.table[item]
    def __str__(self):
        string = ''
        for row in reversed(range(len(self.table))):
            string = string + str(self.table[row]) + '\n'
        return string
    def __repr__(self):
        return str(self)
    def parse(self):
        self.do_bottom_row()
        for row in range(2, len(self.table)):
            self.do_upper_row(row)
    def do_bottom_row(self):
        row = self.table[1] # bottom row is row 1
        for i in range(len(row)):
            row[i] = list(self.table[0][i]) # copy row 0, which contains tags'n'such 
            self._do_unary_rules(row[i])
    def do_upper_row(self, length : int):
        row = self.table[length]
        for i in range(len(row)):
            target = row[i]
            # try to compose out of substrings of len1 and len2, len1+len2=length
            for len1 in range(1, length):
                len2 = length - len1
                cell1 = self.table[len1][i]
                cell2 = self.table[len2][i + len1]
                # if not cell1 or not cell2: continue # not necessary, itertools.product covers
                # we add the 'pos' feature to mark the order
                for n1, n2 in itertools.product(cell1, cell2):
                    n1[Monomial.POS] = str(0)
                    n2[Monomial.POS] = str(1)
                    for rule in self.grammar:
                        # we try both orderings, this is a free order language
                        polynomial = rule.apply([n1, n2])
                        if polynomial and polynomial.error_score < self.error_threshold and polynomial not in target:
                            target.append(polynomial)
                        polynomial = rule.apply([n2, n1]) # reverse order
                        self._append_if_good(polynomial, target)
            self._do_unary_rules(target)
    def _do_unary_rules(self, cell : list):
        j = 0
        while j < len(cell):
            m = cell[j]
            for rule in self.grammar:
                polynomial = rule.apply([m])
                self._append_if_good(polynomial, cell)
            j += 1
    def _append_if_good(self, polynomial : Polynomial, target : list):
        if polynomial and polynomial.error_score < self.error_threshold and polynomial not in target:
            target.append(polynomial)

def display_parser_state(parser : CYK_Parser):
    # string = ''
    for row in reversed(range(len(parser.table))):
        string = ''
        for cell in parser.table[row]:
            string += '['
            for n in cell:
                string += (n.category() + ',')
            string = string.rstrip(',')
            string += '] '
        print(row, string)

