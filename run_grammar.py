import pyconll
from pyconll.unit import Conll

from msd_convert.conllu_msd_to_monomial import token_to_monome

from grammar.rule_builder import rule_from_string

from grammar.grammar import Grammar
from cyk import *

type_dict = {'VP': {'pers', 'nr', 'mode'}}

rules_str = [
    "NumP[num=sg head=n] -> det:Det[Type=possessive gen=@ nr=@],  n:Num[Type=ordinal]",
    "NumP[num=sg head=n] -> n:Num[Type=ordinal! Definiteness=yes]",
    "NumP[head=n] ->  n:Num[Type=cardinal]",

    "DetP[head=det] -> det:Det",
    "DetP[head=det] -> det:Det[pos=0!] , quant:NumP[num=@ gen=@ cas=@ pos=1!]",
    "DetP[head=quant] -> quant:NumP",
    "DetP[head=quant] -> quant:NumP[pos=0!] , de:P[lemma=de! pos=1!]",
    "DetP += dadj:Adj[num=@ gen=@ cas=@ pos=1!]",

    "NP[head=noun pers~3] -> noun:N",
    "NP[head=pron] -> pron:Pron[Pronoun_Form=strong!]",
    "NP[head=num] -> num:NumP",

    "NP[has_det~T] += det:DetP[nr=@ cas=@ gen=@ pos=0!]",
    "NP += adj:Adj[cas=@ gen=@ nr=@]",
    "NP += comp:PP",
    "NP += idnum:NumP[gen=@ pos=1!]",   # camera 12

    "PP[head=prep] -> prep:P[pos=0!] , noun:NP[cas=@]",

    "VP[head=verb] -> verb:V",
    "VP[head=aux] -> aux:V[Type=auxiliary pos=0] , part:V[VForm=participle]",
    "VP += clitic:Pron[Pronoun_Form=weak!]",

    # "VP[head=verb] -> verb:Vb",
    "VP += subj:NP[nr=@ pers=@ cas=Nom pos=0? has_det=T]",
    "VP += dobj:NP[cas=Acc pos=1?]",
    "VP += iobj:NP[cas==Dat!]",
    "VP += pcomp*:PP",
    "VP += adv*:Adv",

    # "NP[nr~pl] -> n1:NP[cas=@ pos=0!], cc:C[pos=1!] , n2:NP[cas=@ pos=2!]",
    # "VP -> v1:VP[pos=0!], cc:C[pos=1!] , v2:VP[pos=2!]",
    "SP[head=vp] -> part:Part[Type=Subj! pos=0!] , vp:VP[mod=Subj]",
    "VP += dobj:SP"
]

grammar = Grammar([rule_from_string(s) for s in rules_str])


infilename = 'easy.txt.conllu' #'C:\\Users\\ffxvtj\\OneDrive\\Lingv\\Corpus\\ro_rrt-ud-train.conllu'
print("Loading file " + infilename)
conll: Conll = pyconll.load_from_file(infilename)
print("Done loading file")

class ProcessConll:
    def __init__(self, conll, grammar):
        self.conll = conll
        self.i = 0
        self.parses = []
        self.grammar = grammar
    def next(self):
        sentence = conll[self.i]
        print(sentence.content)
        sequence = []
        for token in sentence:
            m : Monomial = token_to_monome(token)
            if m:
                sequence.append(m)
        cyk = CYK_Parser(sequence, self.grammar)
        cyk.parse()
        display_parser_state(cyk)
        self.parses.append(cyk)
        self.i += 1
        return cyk
    def last(self):
        return self.parses[-1]

cp = ProcessConll(conll, grammar)
cyk = cp.next()
