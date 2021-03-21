from heuristic_search.parse_search import Possibility, Search, PossibilityScorer
from grammar.phrase_nodes import Monomial
import pandas as pd

LOOKAHEAD = 3


def possibility_to_vector(possibility: Possibility, encoder: dict):
    data = [len(possibility.item_list)]
    for i in range(possibility.index - LOOKAHEAD, possibility.index + LOOKAHEAD):
        if i < 0 or i >= len(possibility.item_list):
            data = data + encoder['']
        else:
            data = data + encoder[possibility.item_list[i][Monomial.CATEGORY]]
    return data

def _spread_score(p : Possibility, score : float):
    if p.score != 0:
        return
    p.score = score
    if p.possibilities:
        for child in p.possibilities:
            _spread_score(child, score - 1.0)
    if p.parent:
        _spread_score(p.parent, score - 1.0)
    

def prep_search_for_learning(s : Search):
    # """This sets the score of all possibilities to 0, then sets the scores of all
    # nodes that lead to a solution (ie nodes in the s.finished list) to 1."""
    """Set the score of the good nodes to -1, and that of the other nodes to the
    negative distance from the solution (solution's parent score is -2, grandpa -3, etc."""
    for p in s.traverse():
        p.score = 0.0
    for good in s.finished:
        _spread_score(good, -1.0)

def generate_learning_data(s : Search, encoder : dict) -> tuple: # returns X,y
    df = pd.DataFrame()
    for p in s.traverse():
        vector = possibility_to_vector(p, encoder)
        vector.append(p.score)
        df = df.append([vector], ignore_index=True)
    num_cols = df.shape[1]
    return df[range(num_cols-1)], df[num_cols-1] # return all cols except last, and last col

class HeuristicScorer(PossibilityScorer):
    def __init__(self, estimator, encoder = None):
        """Estimator is expected to have the functions fit(X,y), predict(X),
        and, preferably, partial_fit(X, y) """
        self.estimator = estimator
        self.encoder = encoder
    def train(self, s : Search):
        prep_search_for_learning(s)
        X, y = generate_learning_data(s, self.encoder)
        self.estimator.fit(X, y)
    def train_partial(self, s : Search):
        prep_search_for_learning(s)
        X, y = generate_learning_data(s, self.encoder)
        self.estimator.partial_fit(X, y)
    def score(self, p : Possibility) -> float:
        X = pd.DataFrame([possibility_to_vector(p, self.encoder)])
        y = self.estimator.predict(X)
        return y[0]
