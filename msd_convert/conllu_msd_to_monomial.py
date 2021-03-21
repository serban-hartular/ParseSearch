from pyconll.unit.token import Token
from grammar.phrase_nodes import Monomial
from msd_convert import UPOS_to_MSD, MSD_to_attribs, ro_MSD_dict, abbrev, ro_msd_types
from msd_convert.abbrev import full_to_abbrev

msd_to_upos_dict = ro_msd_types.msd_to_upos_dict 
MSD_dict = ro_MSD_dict
abbrev.current_abbrev = abbrev.my_ro_list

def token_to_monome(t : Token, use_abbrev = True) -> Monomial:
    if t.upos in {'PUNCT', 'SYM'} : return None
    form = t.form
    xpos = t.xpos
    if not xpos or xpos == '_': # no xpos
        xpos = UPOS_to_MSD(t.upos)
    attribs = MSD_to_attribs(xpos, MSD_dict)
    attribs[Monomial.FORM] = form
    attribs[Monomial.LEMMA] = t.lemma
    if not use_abbrev:
        return Monomial(attribs)
    abbrev_attribs = dict()
    for k,v in attribs.items(): # this could be done pythonically 
        if k not in {Monomial.FORM, Monomial.LEMMA}:
            k = full_to_abbrev(k)
            v = full_to_abbrev(v)
        abbrev_attribs[k] = v
    return Monomial(abbrev_attribs)

