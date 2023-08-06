#!/usr/bin/env python3

"""
** An adaptation of ``sympy.lambdify`` for torch. **
----------------------------------------------------

The folowing optimisations are performed:

* Compute in place as possible.
* Compatible with gpu input tensor, no mix with cpu.
* Conserve the type, float32 or float64.
* Allway working with mix tensor and float input.
* Dynamic adaptaion of the operation order for minimizing operations.
* Factorisation of redondant patern for minimizing operations.
* Maximize realocation and delete useless vars for memory usage minimization.
"""

import itertools
import math
import numbers
import tokenize
import typing

from sympy.core.basic import Basic
from sympy.core.containers import Tuple
from sympy.core.mul import Mul
from sympy.core.numbers import NumberSymbol, Zero
from sympy.core.symbol import Symbol
from sympy.core.sympify import sympify
from sympy.functions.special.delta_functions import DiracDelta
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication
from sympy.printing.pretty.pretty import pretty
from sympy.simplify.cse_main import cse
import torch



def _expr_to_atomic(expr: Basic, *, _symbols=None) -> list[tuple[Symbol, Basic]]:
    """
    ** Apply ``cse`` and split the sub patterns. **

    Parameters
    ----------
    expr : sympy.core.basic.Basic
        The sympy expression to split.

    Returns
    -------
    replacements : list of (Symbol, expression) pairs
        All of the common subexpressions that were replaced.
        All subexpressions are atomic.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import x, y, z
    >>> from sympy.functions.elementary.trigonometric import sin
    >>> from movia.core.compilation.sympy_to_torch import _expr_to_atomic
    >>> exp = (x + y + z - 1)**2 * ((x + y + z)/(x + 1) + (x + y + z - 1)**2) * (x + 1)**(x + y + z)
    >>> pprint(_expr_to_atomic(exp)) # case cse and sub-patterns
    [(_0, x + y + z),
     (_4, _0 - 1),
     (_1, _4**2),
     (_2, x + 1),
     (_5, _2**_0),
     (_8, 1/_2),
     (_7, _0*_8),
     (_6, _1 + _7),
     (_3, _1*_5*_6)]
    >>> pprint(_expr_to_atomic(sin(sin(sin(1))))) # case replace in func
    [(_2, sin(1)), (_1, sin(_2)), (_0, sin(_1))]
    >>>
    """
    if _symbols is None:
        _symbols = iter(Symbol(f"_{i}") for i in itertools.count())
        rep, final = cse(
            expr, symbols=_symbols, optimizations="basic", order="canonical", list=False
        )
        rep.append((next(_symbols), final))
    else: # if cse is already called
        rep = [(next(_symbols), expr)]

    atom_rep = []
    for var, sub_expr in rep:
        if sub_expr.is_Atom:
            atom_rep.append((var, sub_expr))
            continue
        subs = {}
        for arg in sub_expr.args:
            if not arg.is_Atom:
                atom_rep += _expr_to_atomic(arg, _symbols=_symbols)
                subs[arg] = atom_rep[-1][0]
        if subs:
            sub_expr = sub_expr.xreplace(subs)
        atom_rep.append((var, sub_expr))
    return atom_rep


def _parse_expr(expr: typing.Union[Basic, numbers.Complex, str]) -> Basic:
    """
    ** Converts the expression in sympy compilable expression. **

    Parameters
    ----------
    expr : str or sympy.Expr
        The string representation of the equation.
        Some operators like multiplication can be implicit.

    Returns
    -------
    sympy.core.expr.Expr
        The version sympy of the expression.

    Raises
    ------
    SyntaxError
        If the entered expression does not allow to properly define an equation.

    Examples
    --------
    >>> from movia.core.compilation.sympy_to_torch import _parse_expr
    >>> _parse_expr(0)
    0
    >>> _parse_expr("1/2 + 1/2*cos(2pi(t - i*j))")
    cos(pi*(-2*i*j + 2*t))/2 + 1/2
    >>>
    """
    if isinstance(expr, str):
        transformations = standard_transformations + (implicit_multiplication,)
        try:
            expr = parse_expr(
                expr, transformations=transformations, evaluate=True
            )
        except (tokenize.TokenError, TypeError) as err:
            raise SyntaxError(f"failed to parse {expr}") from err
    elif isinstance(expr, numbers.Complex):
        expr = sympify(expr, evaluate=True)
    if not isinstance(expr, Basic):
        raise SyntaxError(f"need to be expression, not {expr.__class__.__name__}")
    return expr


def _release_variable_inplace(expr: Basic) -> list[tuple[Symbol, typing.Optional[Basic]]]:
    """
    ** Call ``_expr_to_atomic`` and optimise the memory. **

    Parameters
    ----------
    expr : sympy.core.basic.Basic
        Transmitted to ``_expr_to_atomic``.

    Returns
    -------
    replacements : list of (Symbol, expression or None) pairs
        All of the common subexpressions that were replaced.
        All subexpressions are atomic or None if the variable is not more used.

    Examples
    --------
    >>> from pprint import pprint
    >>> from sympy.abc import x, y, z
    >>> from movia.core.compilation.sympy_to_torch import _release_variable_inplace
    >>> from sympy.functions.elementary.trigonometric import sin
    >>> exp = (x + y + z - 1)**2 * ((x + y + z)/(x + 1) + (x + y + z - 1)**2) * (x + 1)**(x + y + z)
    >>> pprint(_release_variable_inplace(exp))
    [(y, x + y + z),
     (z, None),
     (_4, y - 1),
     (_4, _4**2),
     (x, x + 1),
     (_5, x**y),
     (x, 1/x),
     (x, x*y),
     (y, None),
     (x, _4 + x),
     (_4, _4*_5*x)]
    >>> pprint(_release_variable_inplace(sin(sin(sin(1)))))
    [(_2, sin(1)), (_2, sin(_2)), (_2, sin(_2))]
    >>>
    """
    rep = _expr_to_atomic(expr)
    i = 0
    while i < len(rep):
        symb, expr = rep[i]
        if unused := sorted(
            (s for s in expr.free_symbols if all(s not in e.free_symbols for _, e in rep[i+1:])),
            key=str,
        ):
            rep[i] = (unused[0], expr)
            rep[i+1:] = [(s, e.xreplace({symb: unused[0]})) for s, e in rep[i+1:]]
            if i + 1 != len(rep):
                for symb in unused[1:]:
                    rep.insert(i+1, (symb, None))
                    i += 1
        i += 1
    return rep


def evalf(expr: Basic) -> Basic:
    """
    ** Numerical eval and simplification od the expression. **

    Parameters
    ----------
    expr : sympy.Expr
        The sympy expression to symplify as numerical evaluable.

    Returns
    -------
    sympy.Expr
        The quite equivalent expression with floats.

    Examples
    --------
    >>> import sympy
    >>> from movia.core.compilation.sympy_to_torch import evalf
    >>> evalf(sympy.DiracDelta(0))
    0
    >>> evalf(sympy.pi)
    3.1415926535897932384626433832795
    >>>
    """
    assert isinstance(expr, Basic), expr.__class__.__name__
    if isinstance(expr, Tuple):
        return Tuple(*map(evalf, expr))
    if sub := expr.atoms(DiracDelta):
        expr = expr.xreplace({d: Zero() for d in sub})
    if sub := expr.atoms(NumberSymbol):
        expr  = expr.xreplace({s: s.evalf(n=32) for s in sub})
    return expr.evalf(n=32)


class LambdifyTorch:
    '''
    ** Convert a SymPy expression into a function that allows for fast torch numeric evaluation. **

    Examples
    --------
    >>> import torch
    >>> from sympy.abc import x, y, z
    >>> from movia.core.compilation.sympy_to_torch import LambdifyTorch
    >>> LambdifyTorch(x, x + 1)(torch.tensor(1.0))
    tensor(2.)
    >>> exp = (x + y + z - 1)**2 * ((x + y + z)/(x + 1) + (x + y + z - 1)**2) * (x + 1)**(x + y + z)
    >>> print(LambdifyTorch([x, y, z], exp))
    def lambdify(x, y, z):
        """
        ** Autogenerated function for fast torch evaluation. **
    <BLANKLINE>
               x + y + z ⎛               2   x + y + z⎞                2
        (x + 1)         ⋅⎜(x + y + z - 1)  + ─────────⎟⋅(x + y + z - 1)
                         ⎝                     x + 1  ⎠
        """
        for _item in sorted([x, z], key=lambda e: isinstance(e, torch.Tensor)):
            y += _item
        del _item
        del z
        _4 = -1.0
        _4 += y
        _4 *= _4
        x += 1.0
        try:
            _5 = x**y
        except ZeroDivisionError:
            _5 = x * math.inf
        try:
            x **= -1.0
        except ZeroDivisionError:
            x *= math.inf
        x *= y
        del y
        x += _4
        for _item in sorted([_5, x], key=lambda e: isinstance(e, torch.Tensor)):
            _4 *= _item
        del _item
        return _4
    >>>
    '''

    def __init__(self, args: typing.Union[Symbol, list[Symbol]], expr: Basic):
        """
        Parameters
        ----------
        args : sympy.Symbol or list[sympy.Symbol]
            A variable or a list of variables whose nesting represents the
            nesting of the arguments that will be passed to the function.
        expr : sympy.Expr
            An expression or list of expressions to be evaluated.
        """
        if isinstance(args, Symbol):
            args = [args]
        assert isinstance(args, list), args.__class__.__name__
        assert all(isinstance(a, Symbol) for a in args), args
        assert isinstance(expr, Basic), expr.__class__.__name__
        assert expr.free_symbols.issubset(set(args)), expr.free_symbols - set(args)
        graph = _release_variable_inplace(evalf(expr))
        self._body = "\n".join(self._print(e, s) for s, e in graph)
        self._funcstr = (
            f"def lambdify({', '.join(str(s) for s in args)}):\n"
            + '    """\n'
            + "    ** Autogenerated function for fast torch evaluation. **\n"
            + "    \n    "
            + "\n    ".join(
                line.rstrip() for line in pretty(expr, use_unicode=None, num_columns=96).split("\n")
            )
            + '\n    """\n    '
            + "\n    ".join(self._body.split("\n"))
            + f"\n    return {graph[-1][0]}"
        )
        func_code = compile(self._funcstr, filename="", mode="exec")
        context = {"math": math, "torch": torch}
        exec(func_code, context, context) # load the references in context, not in locals()
        self._func = context["lambdify"]

    def __call__(self, *args):
        return self._func(*args)

    def __str__(self):
        return self._funcstr

    def _print(self, expr: Basic, alloc: typing.Optional[Symbol]=None) -> str:
        """
        ** Convert the sympy expr in torch operation. **

        Returns
        -------
        operation : str
            The torch operation with the allocation, can be multiline.
        """
        if expr is None:
            return f"del {alloc}"
        if expr.is_real:
            val = str(float(expr))
            return val if alloc is None else f"{alloc} = {val}"
        if expr.is_complex:
            val = str(complex(expr))
            return val if alloc is None else f"{alloc} = {val}"
        if expr.is_symbol:
            return str(expr) if alloc is None else f"{alloc} = {expr}"
        sympy_name_to_torch_name = {
            "atan": "atan",
            "cos": "cos",
            "exp": "exp",
            "sin": "sin",
        }
        sympy_name = expr.__class__.__name__.lower()
        if (torch_name := sympy_name_to_torch_name.get(sympy_name, None)) is not None:
            return self._general_func(torch_name, expr, alloc)
        if (printer := getattr(self, f"_print_{sympy_name}", None)) is not None:
            return printer(expr, alloc)
        raise NotImplementedError(f"no printer for {expr}, class {expr.__class__.__name__}")

    def _general_func(self, func_name: str, expr: Basic, alloc: typing.Optional[Symbol]) -> str:
        """
        ** Format the functions that takes one scalar or tensor argument. **
        """
        arg = self._print(expr.args[0])
        if alloc == expr.args[0]:
            val_torch = f"torch.{func_name}({arg}, out={alloc})"
        else:
            val_torch = f"torch.{func_name}({arg})"
        val_math = f"math.{func_name}({arg})"
        val = f"{val_torch} if isinstance({arg}, torch.Tensor) else {val_math}"
        return f"({val})" if alloc is None else f"{alloc} = {val}"

    def _print_add(self, expr: Basic, alloc: typing.Optional[Symbol]=None) -> str:
        """
        >>> from sympy.abc import x, y, z
        >>> from movia.core.compilation.sympy_to_torch import LambdifyTorch
        >>> print(LambdifyTorch([x], 1 + x).body) # inplace
        x += 1.0
        >>> print(LambdifyTorch([x], x*(1+x)).body) # not inplace
        _1 = 1.0
        _1 += x
        _1 *= x
        >>> print(LambdifyTorch([x, y], 1 + x + y).body) # inplace
        x += 1.0
        x += y
        >>> print(LambdifyTorch([x, y], x*y*(1 + x + y)).body) # not inplace
        _1 = 1.0
        for _item in sorted([x, y], key=lambda e: isinstance(e, torch.Tensor)):
            _1 += _item
        del _item
        for _item in sorted([x, y], key=lambda e: isinstance(e, torch.Tensor)):
            _1 *= _item
        del _item
        >>> print(LambdifyTorch([x, y, z], 1 + x + y + z).body) # inplace
        x += 1.0
        for _item in sorted([y, z], key=lambda e: isinstance(e, torch.Tensor)):
            x += _item
        del _item
        >>>
        """
        scalar = sum(a for a in expr.args if a.is_number)
        items = [a for a in expr.args if not a.is_number]

        if alloc is None:
            if not items:
                return f"({self._print(scalar)})"
            if len(items) == 1 and not scalar:
                return f"({self._print(items.pop())})"
            if len(items) == 1 and scalar:
                return f"(({self._print(scalar)}) + ({self._print(items.pop())}))"
            items = f"[{', '.join(map(self._print, items))}]"
            item_other = f"sum(sorted({items}, key=lambda e: isinstance(e, torch.Tensor)))"
            if not scalar:
                return item_other
            return f"{self._print(scalar)} + {item_other}"

        try:
            index = items.index(alloc)
        except ValueError:
            assign = "="
        else:
            assign = "+="
            del items[index]
        val = f"{alloc} {assign} {self._print(scalar)}\n" if assign == "=" or scalar else ""
        if len(items) == 1:
            val += f"{alloc} += {self._print(items.pop())}\n"
        elif len(items) >= 2:
            items = f"[{', '.join(map(self._print, items))}]"
            items = f"sorted({items}, key=lambda e: isinstance(e, torch.Tensor))"
            val += f"for _item in {items}:\n"
            val += f"    {alloc} += _item\n"
            val += "del _item\n"
        return val[:-1]

    def _print_infinity(self, _, alloc: typing.Optional[Symbol]=None) -> str:
        """
        >>> from sympy.core.numbers import Infinity
        >>> from movia.core.compilation.sympy_to_torch import LambdifyTorch
        >>> print(LambdifyTorch([], Infinity()).body)
        _0 = math.inf
        >>>
        """
        val = "math.inf"
        return val if alloc is None else f"{alloc} = {val}"

    def _print_mul(self, expr: Basic, alloc: typing.Optional[Symbol]=None) -> str:
        """
        >>> from sympy.abc import x, y, z
        >>> from movia.core.compilation.sympy_to_torch import LambdifyTorch
        >>> print(LambdifyTorch([x], 2*x).body)
        x *= 2.0
        >>> print(LambdifyTorch([x], -x).body)
        x = torch.neg(x, out=x) if isinstance(x, torch.Tensor) else -x
        >>> print(LambdifyTorch([x], x*x).body)
        x *= x
        >>> print(LambdifyTorch([x, y], 2*x*y).body)
        x *= 2.0
        x *= y
        >>> print(LambdifyTorch([x, y], -x*y).body)
        x = torch.neg(x, out=x) if isinstance(x, torch.Tensor) else -x
        x *= y
        >>> print(LambdifyTorch([x, y, z], x*y*z).body)
        for _item in sorted([y, z], key=lambda e: isinstance(e, torch.Tensor)):
            x *= _item
        del _item
        >>> print(LambdifyTorch([x, y, z], 2*x*y*z).body)
        x *= 2.0
        for _item in sorted([y, z], key=lambda e: isinstance(e, torch.Tensor)):
            x *= _item
        del _item
        >>>
        """
        scalar = math.prod(a for a in expr.args if a.is_number)
        items = [a for a in expr.args if not a.is_number]

        if alloc is None:
            if not items:
                return f"({self._print(scalar)})"
            if len(items) == 1 and scalar == 1:
                return f"({self._print(items.pop())})"
            if len(items) == 1 and scalar == -1:
                item_str = self._print(items.pop())
                return (
                    f"torch.neg({item_str}) "
                    f"if isinstance({item_str}, torch.Tensor) "
                    f"else -{item_str}"
                )
            if len(items) == 1:
                return f"(({self._print(scalar)}) * ({self._print(items.pop())}))"
            items = f"[{', '.join(map(self._print, items))}]"
            items = f"math.prod(sorted({items}, key=lambda e: isinstance(e, torch.Tensor)))"
            if scalar != 1:
                items = f"{self._print(scalar)} * {items}"
            return items

        try:
            index = items.index(alloc)
        except ValueError:
            assign = "="
        else:
            assign = "*="
            del items[index]
        val = ""
        if assign == "*=" and scalar == -1:
            val = (
                f"{alloc} = torch.neg({alloc}, out={alloc}) "
                f"if isinstance({alloc}, torch.Tensor) else -{alloc}\n"
            )
        elif assign == "=" or scalar != 1:
            val = f"{alloc} {assign} {self._print(scalar)}\n"
        if len(items) == 1:
            val += f"{alloc} *= {self._print(items.pop())}\n"
        elif len(items) >= 2:
            items = f"[{', '.join(map(self._print, items))}]"
            items = f"sorted({items}, key=lambda e: isinstance(e, torch.Tensor))"
            val += f"for _item in {items}:\n"
            val += f"    {alloc} *= _item\n"
            val += "del _item\n"
        return val[:-1]

    def _print_nan(self, _, alloc: typing.Optional[Symbol]=None) -> str:
        """
        >>> from sympy.core.numbers import NaN
        >>> from movia.core.compilation.sympy_to_torch import LambdifyTorch
        >>> print(LambdifyTorch([], NaN()).body)
        _0 = math.nan
        >>>
        """
        val = "math.nan"
        return val if alloc is None else f"{alloc} = {val}"

    def _print_negativeinfinity(self, _, alloc: typing.Optional[Symbol]=None) -> str:
        """
        >>> from sympy.core.numbers import NegativeInfinity
        >>> from movia.core.compilation.sympy_to_torch import LambdifyTorch
        >>> print(LambdifyTorch([], NegativeInfinity()).body)
        _0 = -math.inf
        >>>
        """
        val = "-math.inf"
        return val if alloc is None else f"{alloc} = {val}"

    def _print_pow(self, expr: Basic, alloc: typing.Optional[Symbol]=None) -> str:
        """
        >>> from sympy.abc import x
        >>> from movia.core.compilation.sympy_to_torch import LambdifyTorch
        >>> print(LambdifyTorch([x], x**3).body)
        try:
            x **= 3.0
        except ZeroDivisionError:
            x *= math.inf
        >>> print(LambdifyTorch([x], x**2).body)
        x *= x
        >>> print(LambdifyTorch([x], x**(1/2)).body)
        x = torch.sqrt(x, out=x) if isinstance(x, torch.Tensor) else math.sqrt(x)
        >>> print(LambdifyTorch([x], x+(x**(-1/2))).body)
        try:
            _1 = x**-0.5
        except ZeroDivisionError:
            _1 = x * math.inf
        _1 += x
        >>> print(LambdifyTorch([x], 1/x).body)
        try:
            x **= -1.0
        except ZeroDivisionError:
            x *= math.inf
        >>> print(LambdifyTorch([x], 2/x).body)
        try:
            x **= -1.0
        except ZeroDivisionError:
            x *= math.inf
        x *= 2.0
        >>>
        """
        base, exp = expr.as_base_exp()
        if exp == .5:
            return self._general_func("sqrt", expr, alloc=alloc)
        if exp == 2:
            return self._print_mul(Mul(base, base, evaluate=False), alloc=alloc)
        if alloc == base:
            return (
                "try:\n"
                f"    {alloc} **= {self._print(exp)}\n"
                "except ZeroDivisionError:\n"
                f"    {alloc} *= math.inf"
            )
        base, exp = self._print(base), self._print(exp)
        if alloc is None:
            return (
                f"({base}**{exp} "
                f"if isinstance({base}, torch.Tensor) or isinstance({exp}, torch.Tensor) "
                f"or {exp} >= 0 or {base} else "
                f"math.inf)"
            )
        return (
            "try:\n"
            f"    {alloc} = {base}**{exp}\n"
            "except ZeroDivisionError:\n"
            f"    {alloc} = {base} * math.inf"
        )

    def _print_tuple(self, expr: Basic, alloc: typing.Optional[Symbol]=None) -> str:
        """
        >>> from sympy.abc import x
        >>> from sympy.core.containers import Tuple
        >>> from movia.core.compilation.sympy_to_torch import LambdifyTorch
        >>> print(LambdifyTorch([], Tuple()).body)
        _0 = ()
        >>> print(LambdifyTorch([x], Tuple(x)).body)
        x = (x,)
        >>> print(LambdifyTorch([x], Tuple(x, x)).body)
        x = (x, x)
        >>>
        """
        if len(expr) == 0:
            val = "()"
        elif len(expr) == 1:
            val = f"({self._print(expr[0])},)"
        else:
            val = f"({', '.join(self._print(a) for a in expr)})"
        return val if alloc is None else f"{alloc} = {val}"

    @property
    def body(self) -> str:
        """
        ** The content of the function. **
        """
        return self._body


class LambdifyHomogeneous(LambdifyTorch):
    """
    ** Like LambdifyTorch accepting list and tuple as input. **

    Examples
    --------
    >>> import torch
    >>> from sympy.abc import x
    >>> from movia.core.compilation.sympy_to_torch import LambdifyHomogeneous
    >>> LambdifyHomogeneous(x, x * (x+1))(torch.tensor(1.0))
    tensor(2.)
    >>> LambdifyHomogeneous(x, [x, x+1])(torch.tensor(1.0))
    [tensor(1.), tensor(2.)]
    >>> LambdifyHomogeneous(x, (x, x+1))(torch.tensor(1.0))
    (tensor(1.), tensor(2.))
    >>>
    """

    def __init__(self,
        args: typing.Union[Symbol, list[Symbol]],
        expr: typing.Union[Basic, list[Basic], tuple[Basic]]
    ):
        if isinstance(expr, tuple):
            self.kind = tuple
            expr = Tuple(*expr)
        elif isinstance(expr, list):
            self.kind = list
            expr = Tuple(*expr)
        else:
            self.kind = Basic
        super().__init__(args, expr)

    def __call__(self, *args):
        res = super().__call__(*args)
        if self.kind is not Basic:
            res = self.kind(res)
        return res
