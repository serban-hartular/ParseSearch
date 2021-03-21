from collections import namedtuple, defaultdict
#from ro_msd_types import *
from msd_convert import ro_msd_types as ro

# taken from
# http://nl.ijs.si/ME/Vault/V4/msd/html/msd-ro.html


MSD_Entry = namedtuple('MSD_Entry', ['position', 'attribute', 'value', 'code'])

types = {'N':ro.noun_type, 'V':ro.verb_type, 'A':ro.adj_type, 'P':ro.pron_type, 'D':ro.det_type, 'T':ro.art_type,
         'R':ro.adv_type, 'S':ro.adp_type, 'C':ro.conj_type, 'M':ro.num_type,
         'Q':ro.part_type, 'Y':ro.abbrev_type, 'I':ro.interj_type, 'X':ro.residual_type, 'Z':ro.punct_type}

def MSD_dict_from_type_iter(type_iter) -> defaultdict:
    # MSD_dict[CATEGORY][Position][code] -> (attribute, value)
    # ex., MSD_dict['N'][2]['m'] -> ('Gender', 'masculine')
    MSD_dict = defaultdict(lambda: None)
    for type in type_iter: # type is a list of tuples, see msd_types
        key = None
        entry = defaultdict(lambda: defaultdict(lambda: None))
        for tuple in type:
            (position, attribute, value, code) = tuple
            if position == 0:
                key = code
            entry[position][code] = (attribute, value)
        MSD_dict[key] = entry
    return MSD_dict

def MSD_to_attribs(MSD: str, MSD_dict : dict) -> dict:
    attribs = dict()
    for pos in range(0, len(MSD)):
        code = MSD[pos]
        if code == '-': continue
        if not MSD_dict[MSD[0]]:
            raise Exception('Error in MSD %s type %s' % (MSD, MSD[0]))
        if not MSD_dict[MSD[0]][pos]:
            raise Exception('Error in MSD %s at pos %d' % (MSD, pos))
        if not MSD_dict[MSD[0]][pos][code]:
            raise Exception('Error in MSD %s at pos %d, code %s' % (MSD, pos, code))
        (attribute, value) =  MSD_dict[MSD[0]][pos][code]
        attribs[attribute] = value
    return attribs

def MSD_to_UPOS(msd : str, msd_to_upos_dict : dict) -> str:
    key = msd[0]
    # try first letter
    if key in msd_to_upos_dict:
        return msd_to_upos_dict[key]
    # try first two letters
    key = msd[0:1]
    if key in msd_to_upos_dict:
        return msd_to_upos_dict[key]
    # unknown. return msd and hope
    return msd

def UPOS_to_MSD(upos:str, msd_to_upos_dict: dict) -> str:
    for d_msd,d_upos in msd_to_upos_dict.items():
        if d_upos == upos:
            return d_msd
    return None

ro_MSD_dict = MSD_dict_from_type_iter(types.values())


