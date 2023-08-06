import abc
import re
from typing import Union

from shapely import Polygon


class Expression(abc.ABC):
    @abc.abstractmethod
    def evaluate(self) -> str:
        raise NotImplementedError


class BinaryExpr(Expression):
    def __init__(self, name: str, left: Expression, right: Expression):
        super().__init__()
        self._name = name
        self._left = left
        self._right = right

    def evaluate(self) -> str:
        return f"{self._left.evaluate()} {self._name} {self._right.evaluate()}"


class FunctionExpr(Expression):
    def __init__(self, name, *args):
        super().__init__()
        self._name = name
        self._args = [expr.evaluate() for expr in args]

    def evaluate(self) -> str:
        return f"{self._name}({','.join(self._args)})"


class NotExpr(Expression):
    def __init__(self, expr: Expression):
        super().__init__()
        self._expr = expr

    def evaluate(self) -> str:
        return f"not {self._expr.evaluate()}"


class GroupExpr(Expression):
    def __init__(self, expr):
        super().__init__()
        self._expr = expr

    def evaluate(self) -> str:
        return f"({self._expr.evaluate()})"


class PropExpr(Expression):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def evaluate(self) -> str:
        return self.name


class BooleanExpr(Expression):
    def __init__(self, value: bool):
        super().__init__()
        self.value = value

    def evaluate(self) -> str:
        return 'true' if self.value else 'false'


class NumberExpr(Expression):
    def __init__(self, value: Union[int, float]):
        super().__init__()
        self.value = value

    def evaluate(self) -> str:
        return str(self.value)


class StringExpr(Expression):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def evaluate(self) -> str:
        return f"'{self.value}'"


class CollectionExpr(Expression):
    def __init__(self, value: list):
        super().__init__()
        self.value = value

    def evaluate(self) -> str:
        return f"{self.value}".replace(" ", "")


class Footprint(Expression):
    __pattern = re.compile(r"geography'SRID=4326;Polygon\(\((.+)\)\)'")

    @classmethod
    def from_data(cls, data) -> list:
        p = cls.__pattern.match(data)
        points = []
        if p is not None:
            for coords in p.group(1).split(','):
                lon, lat = coords.split(' ')
                points.append((lon, lat))
        return points

    def __init__(self, points: Union[list, str, Polygon]):
        if isinstance(points, str):
            self._points = self.from_data(points)
        elif isinstance(points, Polygon):
            self._points = [point for point in points.exterior.coords]
        else:
            self._points = points

    def evaluate(self) -> str:
        return "geography'SRID=4326;Polygon(" \
               f"({','.join([f'{p[0]} {p[1]}' for p in self._points])}))'"


class ExpressionType:
    @staticmethod
    def bool(value: bool) -> Expression:
        return BooleanExpr(value)

    @staticmethod
    def string(value: str) -> Expression:
        return StringExpr(value)

    @staticmethod
    def number(value: Union[int, float]):
        return NumberExpr(value)

    @staticmethod
    def collection(value: list):
        return CollectionExpr(value)

    @staticmethod
    def property(value: str):
        return PropExpr(value)

    @staticmethod
    def footprint(points: Union[list, str]):
        return Footprint(points)

    @staticmethod
    def _return(exp: Expression, value):
        if not isinstance(value, str):
            value = str(value)
        return PropExpr(exp.evaluate()+':'+value)


class ComparisonOperator:
    @staticmethod
    def eq(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('eq', left, right)

    @staticmethod
    def ne(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('ne', left, right)

    @staticmethod
    def has(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('has', left, right)

    @staticmethod
    def co_in(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('in', left, right)

    @staticmethod
    def lt(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('lt', left, right)

    @staticmethod
    def le(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('le', left, right)

    @staticmethod
    def gt(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('gt', left, right)

    @staticmethod
    def ge(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('ge', left, right)


class LogicalOperator:
    # Logical Operators
    @staticmethod
    def lo_and(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('and', left, right)

    @staticmethod
    def lo_or(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('or', left, right)

    @staticmethod
    def lo_not(expr: Expression) -> Expression:
        return NotExpr(expr)


class ArithmeticOperator:
    # Arithmetic Operators
    @staticmethod
    def add(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('add', left, right)

    @staticmethod
    def sub(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('sub', left, right)

    @staticmethod
    def mul(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('mul', left, right)

    @staticmethod
    def div(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('div', left, right)

    @staticmethod
    def divby(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('divby', left, right)

    @staticmethod
    def mod(left: Expression, right: Expression) -> Expression:
        return BinaryExpr('mod', left, right)


class GroupingOperator:
    @staticmethod
    def group(value: Expression):
        return GroupExpr(value)


class ExpressionFunc:
    # String and Collection Functions
    @staticmethod
    def concat(expr: Expression, expr_2: Expression) -> Expression:
        return FunctionExpr('concat', expr, expr_2)

    @staticmethod
    def contains(expr: Expression, content: str) -> Expression:
        return FunctionExpr('contains', expr,
                            ExpressionType.string(content))

    @staticmethod
    def endswith(expr: Expression, suffix: str) -> Expression:
        return FunctionExpr('endswith', expr, ExpressionType.string(suffix))

    @staticmethod
    def startswith(expr: Expression, prefix: str) -> Expression:
        return FunctionExpr('startswith', expr,
                            ExpressionType.string(prefix))

    @staticmethod
    def indexof(expr: Expression, value: str) -> Expression:
        return FunctionExpr('indexof', expr, ExpressionType.string(value))

    @staticmethod
    def length(expr: Expression) -> Expression:
        return FunctionExpr('length', expr)

    @staticmethod
    def substring(expr: Expression, index: Union[int, float]) -> Expression:
        return FunctionExpr('substring', expr, NumberExpr(index))

    # Collection Functions
    @staticmethod
    def hassubset(expr: list, expr_2: list,) -> Expression:
        return FunctionExpr('hassubset',
                            expr,
                            expr_2)

    @staticmethod
    def hassubsequence(expr: Expression, expr_2: Expression,) -> Expression:
        return FunctionExpr('hassubsequence',
                            expr,
                            expr_2
                            )

    # String Functions

    @staticmethod
    def matchesPattern(expr: Expression, expr_2: Expression) -> Expression:
        return FunctionExpr('matchesPattern', expr, expr_2)

    @staticmethod
    def tolower(expr: Expression) -> Expression:
        return FunctionExpr('tolower', expr)

    @staticmethod
    def toupper(expr: Expression) -> Expression:
        return FunctionExpr('toupper', expr)

    @staticmethod
    def trim(expr: Expression) -> Expression:
        return FunctionExpr('trim', expr)

    # Date and Time Functions

    @staticmethod
    def day(expr: Expression) -> Expression:
        return FunctionExpr('day', expr)

    @staticmethod
    def date(expr: Expression) -> Expression:
        return FunctionExpr('date', expr)

    @staticmethod
    def second(expr: Expression) -> Expression:
        return FunctionExpr('second', expr)

    @staticmethod
    def hour(expr: Expression) -> Expression:
        return FunctionExpr('hour', expr)

    @staticmethod
    def minute(expr: Expression) -> Expression:
        return FunctionExpr('minute', expr)

    @staticmethod
    def month(expr: Expression) -> Expression:
        return FunctionExpr('month', expr)

    @staticmethod
    def time(expr: Expression) -> Expression:
        return FunctionExpr('time', expr)

    @staticmethod
    def totaloffsetminutes(expr: Expression) -> Expression:
        return FunctionExpr('totaloffsetminutes', expr)

    @staticmethod
    def totalseconds(expr: Expression) -> Expression:
        return FunctionExpr('totalseconds', expr)

    @staticmethod
    def year(expr: Expression) -> Expression:
        return FunctionExpr('year', expr)

    @staticmethod
    def maxdatetime(expr: Expression) -> Expression:
        return FunctionExpr('maxdatetime', expr)

    @staticmethod
    def mindatetime(expr: Expression) -> Expression:
        return FunctionExpr('mindatetime', expr)

    @staticmethod
    def now() -> Expression:
        return FunctionExpr('now')

    # Arithmetic Functions
    @staticmethod
    def ceiling(expr: Expression) -> Expression:
        return FunctionExpr('ceiling', expr)

    @staticmethod
    def floor(expr: Expression) -> Expression:
        return FunctionExpr('floor', expr)

    @staticmethod
    def round(expr: Expression) -> Expression:
        return FunctionExpr('round', expr)

    # Type Functions

    @staticmethod
    def cast(expr: Expression, expr_2: Expression) -> Expression:
        return FunctionExpr('cast', expr, expr_2)

    @staticmethod
    def isof(expr: Expression, expr_2: Expression = None) -> Expression:
        if expr_2 is None:
            return FunctionExpr('isof', expr)
        return FunctionExpr('isof', expr, expr_2)

    # Geo Functions
    @staticmethod
    def geo_distance(expr: Expression, expr_2: Expression = None)\
            -> Expression:
        return FunctionExpr('geo.distance', expr, expr_2)

    @staticmethod
    def geo_intersects(expr: Expression, expr_2: Expression = None)\
            -> Expression:
        return FunctionExpr('geo.intersects', expr, expr_2)

    @staticmethod
    def geo_length(expr: Expression) -> Expression:
        return FunctionExpr('geo.length', expr)

    @staticmethod
    def csc_intersect(expr: Expression, expr_2: Expression):
        return FunctionExpr('OData.CSC.Intersects', expr, expr_2)

    # Conditional Functions
    @staticmethod
    def case(values: list):
        tmp = tuple([ExpressionType._return(e[0], e[1]) for e in values])
        str = ''
        for t in tmp:
            str += t.evaluate()+','
        return FunctionExpr('case',
                            ExpressionType.property(str[:len(str)-1]))

    # lambda
    @staticmethod
    def any(var: str, exp: Expression):
        return FunctionExpr('any', PropExpr(f'{var}:{exp.evaluate()}'))

    @staticmethod
    def all(var: str, exp: Expression):
        return FunctionExpr('all', PropExpr(f'{var}:{exp.evaluate()}'))
