import pyconll
from pyconll.unit import Conll

from msd_convert.conllu_msd_to_monomial import token_to_monome

from grammar.rule_builder import rule_from_string
from heuristic_search.parse_search import *

type_dict = {'VP': {'pers', 'nr', 'mode'}}

rules_str = [
    "NumP[num=sg head=num] -> det:Det[Type=possessive gen=@ nr=@],  num:Num[Type=ordinal]",
    "NumP[num=sg head=num] -> num:Num[Type=ordinal Definiteness=yes]",
    "NumP[head=num] ->  num:Num[Type=cardinal]",
    "NumP[num=pl] += prep:P[lemma=de! pos=1]",

    "DetP[head=det] -> det:Det",
    "DetP[head=det] -> det:Det[pos=0!] , quant:NumP[num=@ gen=@ cas=@ pos=1!]",
    "DetP[head=quant] -> quant:NumP",
    "DetP += dadj:Adj[num=@ gen=@ cas=@ pos=1!]",

    "Nb[head=noun pers~3] -> noun:N",
    # "Nb += num:NumP[num=@ gen=@ pos=0]",
    # # "Nb += num:NumP[num=@ gen=@ pos=0] , prep:P[lemma=de pos=1]",
    # "Nb += det:Det[nr=@ cas=@ gen=@ pos=0!]",
    # "Nb += det:Det[nr=@ cas=@ gen=@ pos=0!] , dadj:Adj[cas=@ gen=@ nr=@ pos=1!]",
    "Nb[has_det=T] += det:DetP[nr=@ cas=@ gen=@ pos=0!]",
    "NP[head=Nb] -> Nb:Nb",
    "NP[head=pron] -> pron:Pron[Pronoun_Form=strong!]",
    "NP[head=num] -> num:NumP",

    "NP += adj:Adj[cas=@ gen=@ nr=@]",
    "NP += comp:PP[prep.lemma=de]",
    "NP += idnum:NumP[gen=@]",

    "PP[head=prep] -> prep:P[pos=0!] , noun:NP[cas=@]",

    "Vb[head=verb] -> verb:V",
    "Vb[head=aux] -> aux:V[Type=auxiliary pos=0] , part:V[VForm=participle]",
    "Vb += clitic:Pron[Pronoun_Form=weak!]",

    "VP[head=verb] -> verb:Vb",
    "VP += subj:NP[nr=@ pers=@ cas=Nom pos=0? has_det=T]",
    "VP += dobj:NP[cas=Acc pos=1?]",
    "VP += iobj:NP[cas=Dat!]",
    "VP += pcomp*:PP",
    "VP += adv*:Adv",

    "NP[nr~pl] -> n1:NP[cas=@ pos=0!], cc:C[pos=1!] , n2:NP[cas=@ pos=2!]",
    "VP -> v1:VP[pos=0!], cc:C[pos=1!] , v2:VP[pos=2!]",
    "SP[head=vp] -> part:Part[Type=Subj! pos=0!] , vp:VP[mod=Subj]",
    "VP += dobj:SP"
]

rules = [rule_from_string(s) for s in rules_str]

infilename = 'simple.txt.conllu'
print("Loading file " + infilename)
conll: Conll = pyconll.load_from_file(infilename)
print("Done loading file")


def count_nodes(phrase: Polynomial) -> int:
    count = 1  # this node
    if not isinstance(phrase, Polynomial):  # it's a monomial
        return count
    for deprel, child in phrase.children.items():
        count += count_nodes(child)
    return count


def possibility_node_count(p: Possibility) -> float:
    count = 0
    for ph in p.item_list:
        count += count_nodes(ph)
    return float(count)


def heuristic_fn(p: Possibility) -> float:
    score = 0
    for item in p.item_list:
        if isinstance(item, Polynomial):
            score -= 1
        else:  # is monominal
            score -= 2
    here: Polynomial = p[p.index]
    after: Polynomial = p[p.index + 1] if p.index + 1 < len(p) else None
    before: Polynomial = p[p.index - 1] if p.index - 1 > 0 else None
    if here.category() == 'NumP' and after and after.category() in {'NP', 'Nb', 'N'}:
        score += 1
    if before and before.category() == 'NumP' and here.category() in {'NP', 'Nb', 'N'}:
        score += 1
    if after and after.category() == 'VP':  # deal with what comes after 'să' first
        score += 1.5
    if before and before.category() == 'VP':  # deal with what comes after 'să' first
        score += 1.5
    return score


i = 0
target = 3
s_list = []
p_list = []
seq_list = []
for sentence in conll:
    m_list = PhSequence([token_to_monome(t) for t in sentence if token_to_monome(t)])
    seq_list.append(m_list)
    print(i)
    s = Search(m_list, rules, heuristic_fn)
    p = s.search()
    print(sentence.content)
    print(str(p))
    s_list.append(s)
    p_list.append(p)
    i += 1
    # if i == 8: break
