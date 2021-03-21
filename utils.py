
from grammar.phrase_nodes import *


def tree_string(phrase, add_deprel = False, add_phrasetype = False, recurse = True) -> str:
    if not isinstance(phrase, Monomial): return None
    if not isinstance(phrase, Polynomial): # monomial
        return phrase[Monomial.FORM] + \
               ('_' + phrase[Monomial.CATEGORY] if add_phrasetype else '')
    if len(phrase.children) == 1: # singleton phrase
        return phrase[Monomial.FORM] + \
            ('_' + phrase[Monomial.CATEGORY] if add_phrasetype else '')
    string = '['
    for deprel, child in phrase.children.items():
        if add_deprel:
            string = string + deprel + ':'
        string = string + (tree_string(child, add_deprel, add_phrasetype, recurse) if recurse else child.form()) + ' '
    string = string.rstrip()
    string = string + ']'
    if add_phrasetype:
        string = string + phrase[Monomial.CATEGORY]
    return string

def nodelist_string(nodes : list):
    return '; '.join([tree_string(n, True, False, False) for n in nodes])

import msd_convert 

def msd_info(msd : str) -> str:
    return msd_convert.MSD_to_attribs(msd, msd_convert.ro_MSD_dict)