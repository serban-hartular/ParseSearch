from grammar.phrase_nodes import Polynomial, Monomial


class ConstraintReport:
    def __init__(self, path: list, expected, actual, score, form: str = ''):
        self.path = path
        self.expected = expected
        self.actual = actual
        self.score = score
        self.form = form

    def __bool__(self):
        return self.score == 0

    def __str__(self):
        string = ''
        if self.form:
            string = 'in "' + self.form + '" '
        string = string + "expected %s to be %s was %s" % \
                 ('.'.join(self.path), str(self.expected), str(self.actual))
        return string

    def __repr__(self):
        return str(self)


def to_set_(value) -> set:
    if isinstance(value, str): return {value}
    try:
        iterator = iter(value)
        return {v for v in iterator}
    except TypeError as te:
        return {value}


def from_set(value):
    if isinstance(value, str): return value
    try:
        iterator = iter(value)
        if len(value) > 1:
            return value  # set size is > 1, return the set
        else:
            return set(value).pop()  # set is singleton, return the value
    except TypeError as te:
        return value


class Constraint:
    def __init__(self, lexpr: list, rexpr, error_score: float = 1.0, is_none_ok = True, name: str = ''):
        self.lexpr = lexpr
        self.rexpr = rexpr
        self.rexpr_str: bool = isinstance(rexpr, str)
        self.lval = None
        self.rval = None
        self.error_score = error_score
        self.is_none_ok = is_none_ok
        self.name = name

    def __str__(self):
        string = '.'.join(self.lexpr) + '='
        string = string + ('.'.join(self.rexpr) if not self.rexpr_str else self.rexpr)
        return string

    def __repr__(self):
        return str(self)

    # def evaluate(self, node: Polynomial) -> ConstraintReport:
    #     self.lval = Polynomial.get_path(node, self.lexpr)
    #     if self.rexpr_str:
    #         self.rval = self.rexpr
    #     else:
    #         self.rval = Polynomial.get_path(node, self.rexpr)
    #     return self._report_(node[Monomial.FORM])  # self.lval == self.rval
    # 
    # def resolve(self, node: Polynomial) -> ConstraintReport:
    #     if (not self.rval and not self.lval) or (self.rval and self.lval):
    #         return self._report_(node[Monomial.FORM])
    #     if not self.rval:
    #         val = self.lval
    #         expr = self.rexpr
    #     else:
    #         val = self.rval
    #         expr = self.lexpr
    #     Polynomial.set_path(node, expr, val)
    #     return self._report_(node[Monomial.FORM], 0)  # return zero error

    def eval_and_resolve(self, node) -> ConstraintReport:
        # eval_report = self.evaluate(node)
        # if eval_report: return eval_report
        # return self.resolve(node)
        return self.reconcile(node)

    def reconcile(self, node) -> ConstraintReport:
        """Checks if constraint is met. Makes changes to node if possible to make it meet constraint """
        self.lval = Polynomial.get_path(node, self.lexpr)
        self.rval = self.rexpr if self.rexpr_str else Polynomial.get_path(node, self.rexpr)
        if not self.lval and not self.rval:
            #  neither parameter has value (say, case is unknown at this stage). pass
            return self._report_(node[Monomial.FORM], 0)  # 0 score
        if self.lval == self.rval:  # we're good
            return self._report_(node[Monomial.FORM], 0)  # 0 score
        # what if just one of them is None? We set it to the correct value
        if (not self.lval or not self.rval) and not self.is_none_ok:
            return self._report_(node[Monomial.FORM], self.error_score)
        if not self.lval:
            Polynomial.set_path(node, self.lexpr, self.rval)
            return self._report_(node[Monomial.FORM], 0)  # 0 score
        elif not self.rval:
            Polynomial.set_path(node, self.rexpr, self.lval)
            return self._report_(node[Monomial.FORM], 0)  # 0 score
        # try to see if they have requirements in common
        # eg. requirement is case = {Acc, Dat}, and target has case = {Nom, Acc}.
        # in this case, set target (lval) to Acc
        set_lval = to_set_(self.lval)  # make set if singleton
        set_rval = to_set_(self.rval)  # make set if singleton
        intersection = set_lval.intersection(set_rval)
        if not intersection:  # nothing doing
            return self._report_(node[Monomial.FORM])
        # assign intersection to lval and return that it's good
        Polynomial.set_path(node, self.lexpr, from_set(intersection))
        return self._report_(node[Monomial.FORM], 0)

    def _report_(self, form: str = '', error_score=None) -> ConstraintReport:
        """returns an error report"""
        if error_score is None:
            if self.lval == self.rval:
                error_score = 0  # it's a-okay
            else:
                error_score = self.error_score
        return ConstraintReport(self.lexpr, self.rval, self.lval, error_score, form)

class OverwriteConstraint(Constraint):
    def __init__(self, lexpr: list, rexpr, name: str = ''):
        super().__init__(lexpr, rexpr, 0, name)

    def reconcile(self, node) -> ConstraintReport:
        # self.lval = Polynomial.get_path(node, self.lexpr)
        self.rval = self.rexpr if self.rexpr_str else Polynomial.get_path(node, self.rexpr)
        Polynomial.set_path(node, self.lexpr, self.rval)
        return self._report_(node.form(), 0)