
from grammar.phrase_nodes import Monomial

current_abbrev = []

def abbrev_to_full(abbrev:str) -> str:
    for t in current_abbrev:
        if t[1] == abbrev:
            return t[0]
    return abbrev

def full_to_abbrev(full:str) -> str:
    for t in current_abbrev:
        if t[0] == full:
            return t[1]
    return full

my_ro_list = [
    ('CATEGORY', Monomial.CATEGORY),
    ('Noun', 'N'),
    ('Verb', 'V'),
    ('Adjective', 'Adj'),
    ('Pronoun', 'Pron'),
    ('Determiner', 'Det'),
    ('Article', 'Det'),
    ('Adverb', 'Adv'),
    ('Adposition', 'P'),
    ('Conjunction', 'C'),
    ('Numeral', 'Num'),
    ('Particle', 'Part'),
# 'Interjection', ,'Abbreviation', 'Residual'
    ('Gender', 'gen'),
    ('masculine', 'masc'),
    ('feminine', 'fem'),
    ('neuter', 'neut'),
    ('Case', 'cas'),
    ('vocative', 'Voc'),
    ('direct', {'Nom', 'Acc'}),
    ('oblique', {'Dat', 'Gen'}),
    ('nominative', 'Nom'),
    ('genitive', 'Gen'),
    ('dative', 'Dat'),
    ('accusative', 'Acc'),
    ('Number', 'nr'),
    ('singular', 'sg'),
    ('plural', 'pl'),
    ('VForm', 'mod'),
    ('indicative', 'Ind'),
    ('subjunctive', 'Subj'),
    ('imperative', 'Imp'),
    ('infinitive', 'Inf'),
    ('participle', 'Part'),
    ('gerund', 'Ger'),
    ('Person', 'pers'),
    ('first', '1'),
    ('second', '2'),
    ('third', '3')
]

current_abbrev = my_ro_list