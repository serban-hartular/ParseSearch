
# format:
# "VP[mod=Ind head=verb] -> subj:NP[nr=@ pers=@ case=N] , verb:V"

from grammar.phrase_nodes import Monomial
from grammar.constraints import Constraint, OverwriteConstraint
from grammar.constraint_rules import Rule
from grammar.constraint_rules import Headed_Rule, AppendRule
import re

DEFAULT_ERROR_SCORE = 1.0

EQUALS = '='
OVERWRITE = '~'
NONE_NOT_OK = '=='

def constraint_from_string(string : str, l_deprel:str = None) -> Constraint:
    """ string format 'cas=N' or 'num=@' or 'gen=subj.gen' or 'num = verb.num'
    @ will be replaced with the lval 
    over-write rule: num/3 means is_bare will be yes no matter what it was before, no error"""
    if EQUALS in string:   separator = EQUALS
    elif OVERWRITE in string: separator = OVERWRITE
    else:               raise Exception('Invalid constraint %s, no separator' % string)
    is_none_ok = (NONE_NOT_OK not in string)
    string = string.replace(NONE_NOT_OK, EQUALS)
    is_overwrite = (separator == OVERWRITE)
    (lstr, rstr) = string.split(separator)
    lstr = lstr.strip()
    rstr = rstr.strip()
    if rstr[-1] == '!': # mandatory condition
        score = float('Inf')
        rstr = rstr[:-1]
    elif '?' in rstr:
        (rstr, score) = rstr.split('?')
        score = float(score) if score else 0.5
    else:
        score = DEFAULT_ERROR_SCORE
    # do lexp
    lstr = lstr.split('.') # split by period -- ie, subj.gen
    lexp = [l_deprel] if l_deprel else []
    lexp = lexp + lstr
    # for item in lstr:
    #     lexp.append(item)
    # do rexp
    rexpr = []
    if rstr == '@':
        rexpr = lstr
    elif '.' in rstr:
        rstr = rstr.split('.')
        for item in rstr:
            rexpr.append(item)
    else: # plain string
        rexpr = rstr
    if is_overwrite:
        return OverwriteConstraint(lexp, rexpr)
    else:
        return Constraint(lexp, rexpr, score, is_none_ok)

def constraint_list_from_string(string : str, l_deprel:str = None):
    # string will look like 'case=2 num=q gen = bizzarre '
    # to make whitespace a separator, replace ' = ' with '='
    string = re.sub('\s*=\s*', '=', string)
    string = string.strip()
    strings = string.split() # whitespace
    return [constraint_from_string(s, l_deprel) for s in strings]

def type_and_constraint_list_from_string(string:str, l_deprel:str = None) -> tuple:
    # string has form 'NP[case=Nom nr=@ pers=@]'
    string = string.strip()
    if '[' not in string: # it's a singleton
        if ' ' in string: # bad
            raise Exception('Bad name ' + string)
        return(string, [])
    try:
        (name, constraint_string) = string.split('[')
    except:
        raise Exception('Error splitting ' + string)
    if constraint_string[-1] != ']':
        raise Exception('%s lacks ]', string)
    constraint_string = constraint_string[:-1] # elim last char
    constraints = constraint_list_from_string(constraint_string, l_deprel)
    return (name.strip(), constraints)

def deprel_type_from_string(string: str) -> tuple:
    string = string.strip()
    try:
        (deprel, type_string) = string.split(':')
    except:
        raise Exception('Missing deprel:item in item %s' % string )
    deprel = deprel.strip()
    (type_name, constraints) = type_and_constraint_list_from_string(type_string, deprel)
    return (deprel, type_name, constraints)

def _get_head_phrase(parent_constraints : list, head_str = 'head') -> str:
    head_name = ''
    for constraint in parent_constraints:
        if constraint.lexpr == [head_str]: # this is a constraint of form 'head=blah'
            head_name = constraint.rexpr # ie, blah
            break
    if head_name:
        parent_constraints.remove(constraint)
    return head_name

def _get_type_constraint(deprel:str, type_name : str, error_score = float('inf')) -> Constraint:
    if deprel:
        return Constraint([deprel, Monomial.CATEGORY], type_name, error_score)
    else:
        return Constraint([Monomial.CATEGORY], type_name, error_score)
    
def rule_from_string(string: str, head_separator = '->', append_separator = '+=',
                     child_separator = ',') -> Rule:
    # "VP[mod=Ind head=verb] -> subj:NP[nr=@ pers=@ case=N] , verb:V"
    # VP += iobj:NP[case=Dat]
    separator = None
    for s in [head_separator, append_separator]:
        if s in string:
            separator = s
            break
    if not separator: raise Exception('No valid rule separator found in %s' % string)
    try:
        (parent, children) = string.split(separator)
    except:
        raise Exception('Error splitting "%s" by %s' % (string, separator))
    parent = parent.strip()
    (parent_name, constraints) = type_and_constraint_list_from_string(parent)
    # get head_name from constraint eg "head=verb". fn removes this constraint if found
    head_name = _get_head_phrase(constraints)
    if separator == append_separator and head_name:
        raise Exception('Cannot append and set phrase head in rule %s' % string)
    deprel_list = list()
    for child_str in children.split(child_separator):
        child_str = child_str.strip()
        (deprel, type_name, child_constraints) = deprel_type_from_string(child_str)
        deprel_list.append(deprel)
        constraints.insert(0, _get_type_constraint(deprel, type_name)) # add constraint that child is of type eg 'NP'
        constraints = constraints + child_constraints
    if head_name:
        return Headed_Rule(parent_name, deprel_list, head_name, None, constraints, string)
    elif separator == append_separator:
        deprel_list.insert(0, AppendRule.SELF) # insert 'self' deprel
        constraints.insert(0, _get_type_constraint('', parent_name)) # add constraint that child is of type eg 'NP'
        return AppendRule(parent_name, deprel_list, constraints, string)
    else:
        return Rule(parent_name, deprel_list, constraints, string)
