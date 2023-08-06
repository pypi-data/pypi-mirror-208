import unittest

from shapely import Polygon

from drb.drivers.odata import (
    Expression, ExpressionType, ComparisonOperator,
    LogicalOperator, ArithmeticOperator,
    GroupingOperator, ExpressionFunc
)


class TestExpression(unittest.TestCase):
    foot_print = "geography'SRID=4326;Polygon((" \
                 "104.99934004982643 -74.2320605340525," \
                 "105.27272732082909 -74.28534428112921," \
                 "105.25623295629731 -74.291237938206087))'"

    def test_type(self):
        bool = ExpressionType.bool(True)
        self.assertIsNotNone(bool)
        self.assertIsInstance(bool, Expression)
        self.assertEqual('true', bool.evaluate())

        string = ExpressionType.string('toto')
        self.assertIsNotNone(string)
        self.assertIsInstance(string, Expression)
        self.assertEqual("'toto'", string.evaluate())

        integer = ExpressionType.number(101)
        self.assertIsNotNone(integer)
        self.assertIsInstance(integer, Expression)
        self.assertEqual('101', integer.evaluate())

        array = ExpressionType.collection([1, 2, 3, 4, 5])
        self.assertIsNotNone(array)
        self.assertIsInstance(array, Expression)
        self.assertEqual('[1,2,3,4,5]', array.evaluate())

        property = ExpressionType.property('Odata.CSC.my_prop')
        self.assertIsNotNone(property)
        self.assertIsInstance(property, Expression)
        self.assertEqual('Odata.CSC.my_prop', property.evaluate())

    def test_comparaison_operator(self):
        equal = ComparisonOperator.eq(
            ExpressionType.property('My_Prop'),
            ExpressionType.string('Toto')
        )
        self.assertIsNotNone(equal)
        self.assertIsInstance(equal, Expression)
        self.assertEqual("My_Prop eq 'Toto'", equal.evaluate())

        not_equal = ComparisonOperator.ne(
            ExpressionType.property('My_Prop'),
            ExpressionType.number(100)
        )
        self.assertIsNotNone(not_equal)
        self.assertIsInstance(not_equal, Expression)
        self.assertEqual("My_Prop ne 100", not_equal.evaluate())

        has = ComparisonOperator.has(
            ExpressionType.property('Style'),
            ExpressionType.property("Sales.Color'Yellow'")
        )
        self.assertIsNotNone(has)
        self.assertIsInstance(has, Expression)
        self.assertEqual("Style has Sales.Color'Yellow'", has.evaluate())

        is_member = ComparisonOperator.co_in(
            ExpressionType.property('Address/City'),
            GroupingOperator.group(
                ExpressionType.property("'Redmond', 'London'"))
        )
        self.assertIsNotNone(is_member)
        self.assertIsInstance(is_member, Expression)
        self.assertEqual("Address/City in ('Redmond', 'London')",
                         is_member.evaluate())

        lt = ComparisonOperator.lt(
            ExpressionType.property('Price'),
            ExpressionType.number(20)
        )
        self.assertIsNotNone(lt)
        self.assertIsInstance(lt, Expression)
        self.assertEqual("Price lt 20", lt.evaluate())

        le = ComparisonOperator.le(
            ExpressionType.property('Price'),
            ExpressionType.number(100)
        )
        self.assertIsNotNone(le)
        self.assertIsInstance(le, Expression)
        self.assertEqual("Price le 100", le.evaluate())

        gt = ComparisonOperator.gt(
            ExpressionType.property('Price'),
            ExpressionType.number(20)
        )
        self.assertIsNotNone(gt)
        self.assertIsInstance(gt, Expression)
        self.assertEqual("Price gt 20", gt.evaluate())

        ge = ComparisonOperator.ge(
            ExpressionType.property('Price'),
            ExpressionType.number(100)
        )
        self.assertIsNotNone(ge)
        self.assertIsInstance(ge, Expression)
        self.assertEqual("Price ge 100", ge.evaluate())

    def test_lo_operator(self):
        ge = ComparisonOperator.ge(
            ExpressionType.property('Price'),
            ExpressionType.number(100)
        )
        gt = ComparisonOperator.gt(
            ExpressionType.property('Price'),
            ExpressionType.number(20)
        )

        ope = LogicalOperator.lo_and(ge, gt)
        self.assertIsNotNone(ope)
        self.assertIsInstance(ope, Expression)
        self.assertEqual("Price ge 100 and Price gt 20", ope.evaluate())

        ope = LogicalOperator.lo_or(ge, gt)
        self.assertIsNotNone(ope)
        self.assertIsInstance(ope, Expression)
        self.assertEqual("Price ge 100 or Price gt 20", ope.evaluate())

        ope = LogicalOperator.lo_not(ge)
        self.assertIsNotNone(ope)
        self.assertIsInstance(ope, Expression)
        self.assertEqual("not Price ge 100", ope.evaluate())

    def test_arithmetics_operator(self):
        add = ArithmeticOperator.add(
            ExpressionType.property('Price'),
            ExpressionType.number(5))
        self.assertIsNotNone(add)
        self.assertIsInstance(add, Expression)
        self.assertEqual("Price add 5", add.evaluate())

        sub = ArithmeticOperator.sub(
            ExpressionType.property('Price'),
            ExpressionType.number(5))
        self.assertIsNotNone(sub)
        self.assertIsInstance(sub, Expression)
        self.assertEqual("Price sub 5", sub.evaluate())

        divby = ArithmeticOperator.divby(
            ExpressionType.property('Price'),
            ExpressionType.number(5))
        self.assertIsNotNone(divby)
        self.assertIsInstance(divby, Expression)
        self.assertEqual("Price divby 5", divby.evaluate())

        mul = ArithmeticOperator.mul(
            ExpressionType.property('Price'),
            ExpressionType.number(5))
        self.assertIsNotNone(mul)
        self.assertIsInstance(mul, Expression)
        self.assertEqual("Price mul 5", mul.evaluate())

        div = ArithmeticOperator.div(
            ExpressionType.property('Price'),
            ExpressionType.number(5))
        self.assertIsNotNone(div)
        self.assertIsInstance(div, Expression)
        self.assertEqual("Price div 5", div.evaluate())

        mod = ArithmeticOperator.mod(
            ExpressionType.property('Price'),
            ExpressionType.number(5))
        self.assertIsNotNone(mod)
        self.assertIsInstance(mod, Expression)
        self.assertEqual("Price mod 5", mod.evaluate())

    def test_grouping(self):
        group = ComparisonOperator.gt(
            GroupingOperator.group(
                ArithmeticOperator.add(
                    ExpressionType.property('Price'),
                    ExpressionType.number(5))
                ),
            ExpressionType.number(50)
            )
        self.assertIsNotNone(group)
        self.assertIsInstance(group, Expression)
        self.assertEqual("(Price add 5) gt 50", group.evaluate())

    def test_string_collection_function(self):
        concat = ExpressionFunc.concat(
            ExpressionType.property('City'),
            ExpressionType.string(', ')
        )
        self.assertIsNotNone(concat)
        self.assertIsInstance(concat, Expression)
        self.assertEqual("concat(City,', ')", concat.evaluate())

        contains = ExpressionFunc.contains(
            ExpressionType.property('City'),
            'London'
        )
        self.assertIsNotNone(contains)
        self.assertIsInstance(contains, Expression)
        self.assertEqual("contains(City,'London')", contains.evaluate())

        start = ExpressionFunc.startswith(
            ExpressionType.property('City'),
            'Lo'
        )
        self.assertIsNotNone(start)
        self.assertIsInstance(start, Expression)
        self.assertEqual("startswith(City,'Lo')", start.evaluate())

        end = ExpressionFunc.endswith(
            ExpressionType.property('City'),
            'on'
        )
        self.assertIsNotNone(end)
        self.assertIsInstance(end, Expression)
        self.assertEqual("endswith(City,'on')", end.evaluate())

        index = ExpressionFunc.indexof(
            ExpressionType.property('Company'),
            'Gael'
        )
        self.assertIsNotNone(index)
        self.assertIsInstance(index, Expression)
        self.assertEqual("indexof(Company,'Gael')", index.evaluate())

        length = ExpressionFunc.length(
            ExpressionType.property('Company')
        )
        self.assertIsNotNone(length)
        self.assertIsInstance(length, Expression)
        self.assertEqual("length(Company)", length.evaluate())

        substring = ExpressionFunc.substring(
            ExpressionType.property('Company'),
            1
        )
        eq = ComparisonOperator.eq(
            substring,
            ExpressionType.string('Gael Systems')
        )
        self.assertIsNotNone(eq)
        self.assertIsInstance(eq, Expression)
        self.assertEqual("substring(Company,1) eq 'Gael Systems'",
                         eq.evaluate())

    def test_collection_func(self):
        hasssubset = ExpressionFunc.hassubset(
            ExpressionType.collection([1, 2, 3, 4, 5]),
            ExpressionType.collection([3, 4])
        )
        self.assertIsNotNone(hasssubset)
        self.assertIsInstance(hasssubset, Expression)
        self.assertEqual("hassubset([1,2,3,4,5],[3,4])", hasssubset.evaluate())

        hassubsequence = ExpressionFunc.hassubsequence(
            ExpressionType.collection([1, 2, 3, 4, 5]),
            ExpressionType.collection([3, 5])
        )
        self.assertIsNotNone(hassubsequence)
        self.assertIsInstance(hassubsequence, Expression)
        self.assertEqual("hassubsequence([1,2,3,4,5],[3,5])",
                         hassubsequence.evaluate())

    def test_string_function(self):
        match = ExpressionFunc.matchesPattern(
            ExpressionType.property('CompanyName'),
            ExpressionType.string('%5EA.*e$')
        )
        self.assertIsNotNone(match)
        self.assertIsInstance(match, Expression)
        self.assertEqual("matchesPattern(CompanyName,'%5EA.*e$')",
                         match.evaluate())

        lower = ExpressionFunc.tolower(
            ExpressionType.property('CompanyName')
        )
        self.assertIsNotNone(lower)
        self.assertIsInstance(lower, Expression)
        self.assertEqual("tolower(CompanyName)", lower.evaluate())

        upper = ExpressionFunc.toupper(
            ExpressionType.property('CompanyName')
        )
        self.assertIsNotNone(upper)
        self.assertIsInstance(upper, Expression)
        self.assertEqual("toupper(CompanyName)", upper.evaluate())

        trim = ExpressionFunc.trim(
            ExpressionType.property('CompanyName')
        )
        self.assertIsNotNone(trim)
        self.assertIsInstance(trim, Expression)
        self.assertEqual("trim(CompanyName)", trim.evaluate())

        eq = ComparisonOperator.eq(
            upper,
            ExpressionType.string('GAEL SYSTEMSS')
        )
        self.assertIsNotNone(eq)
        self.assertIsInstance(eq, Expression)
        self.assertEqual("toupper(CompanyName) eq 'GAEL SYSTEMSS'",
                         eq.evaluate())

    def test_date_time_function(self):
        day = ExpressionFunc.day(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(day)
        self.assertIsInstance(day, Expression)
        self.assertEqual("day(StartTime)", day.evaluate())

        date = ExpressionFunc.date(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(date)
        self.assertIsInstance(date, Expression)
        self.assertEqual("date(StartTime)", date.evaluate())

        second = ExpressionFunc.second(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(second)
        self.assertIsInstance(second, Expression)
        self.assertEqual("second(StartTime)", second.evaluate())

        hour = ExpressionFunc.hour(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(hour)
        self.assertIsInstance(hour, Expression)
        self.assertEqual("hour(StartTime)", hour.evaluate())

        minute = ExpressionFunc.minute(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(minute)
        self.assertIsInstance(minute, Expression)
        self.assertEqual("minute(StartTime)", minute.evaluate())

        month = ExpressionFunc.month(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(month)
        self.assertIsInstance(month, Expression)
        self.assertEqual("month(StartTime)", month.evaluate())

        time = ExpressionFunc.time(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(time)
        self.assertIsInstance(time, Expression)
        self.assertEqual("time(StartTime)", time.evaluate())

        totaloffsetminutes = ExpressionFunc.totaloffsetminutes(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(totaloffsetminutes)
        self.assertIsInstance(totaloffsetminutes, Expression)
        self.assertEqual("totaloffsetminutes(StartTime)",
                         totaloffsetminutes.evaluate())

        year = ExpressionFunc.year(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(year)
        self.assertIsInstance(year, Expression)
        self.assertEqual("year(StartTime)", year.evaluate())

        maxdatetime = ExpressionFunc.maxdatetime(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(maxdatetime)
        self.assertIsInstance(maxdatetime, Expression)
        self.assertEqual("maxdatetime(StartTime)", maxdatetime.evaluate())

        mindatetime = ExpressionFunc.mindatetime(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(mindatetime)
        self.assertIsInstance(mindatetime, Expression)
        self.assertEqual("mindatetime(StartTime)", mindatetime.evaluate())

        totalseconds = ExpressionFunc.totalseconds(
            ExpressionType.property('StartTime')
        )
        self.assertIsNotNone(totalseconds)
        self.assertIsInstance(totalseconds, Expression)
        self.assertEqual("totalseconds(StartTime)", totalseconds.evaluate())

        now = ExpressionFunc.now()
        self.assertIsNotNone(now)
        self.assertIsInstance(now, Expression)
        self.assertEqual("now()", now.evaluate())

    def test_arithmetic_function(self):
        ceilling = ExpressionFunc.ceiling(
            ExpressionType.property('Freight')
        )
        self.assertIsNotNone(ceilling)
        self.assertIsInstance(ceilling, Expression)
        self.assertEqual("ceiling(Freight)", ceilling.evaluate())

        floor = ExpressionFunc.floor(
            ExpressionType.property('Freight')
        )
        self.assertIsNotNone(floor)
        self.assertIsInstance(floor, Expression)
        self.assertEqual("floor(Freight)", floor.evaluate())

        round = ExpressionFunc.round(
            ExpressionType.property('Freight')
        )
        self.assertIsNotNone(round)
        self.assertIsInstance(round, Expression)
        self.assertEqual("round(Freight)", round.evaluate())

        eq = ComparisonOperator.eq(
            round,
            ExpressionType.number(32)
        )
        self.assertIsNotNone(eq)
        self.assertIsInstance(eq, Expression)
        self.assertEqual("round(Freight) eq 32", eq.evaluate())

    def test_type_function(self):
        cast = ExpressionFunc.cast(
            ExpressionType.property('ShipCountry'),
            ExpressionType.property('Edm.String')
        )
        self.assertIsNotNone(cast)
        self.assertIsInstance(cast, Expression)
        self.assertEqual("cast(ShipCountry,Edm.String)", cast.evaluate())

        isof = ExpressionFunc.isof(
            ExpressionType.property('ShipCountry')
        )
        self.assertIsNotNone(isof)
        self.assertIsInstance(isof, Expression)
        self.assertEqual("isof(ShipCountry)", isof.evaluate())

        isof = ExpressionFunc.isof(
            ExpressionType.property('ShipCountry'),
            ExpressionType.property('Edm.String')
        )
        self.assertIsNotNone(isof)
        self.assertIsInstance(isof, Expression)
        self.assertEqual("isof(ShipCountry,Edm.String)", isof.evaluate())

    def test_geo_function(self):
        footprint = ExpressionType.footprint(self.foot_print)
        self.assertIsNotNone(footprint)
        self.assertIsInstance(footprint, Expression)
        self.assertEqual(self.foot_print,
                         footprint.evaluate())

        footprint = ExpressionType.footprint(
            Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
        )
        self.assertIsNotNone(footprint)
        self.assertIsInstance(footprint, Expression)
        self.assertEqual("geography'SRID=4326;"
                         "Polygon((0.0 0.0,1.0 0.0,1.0 1.0,0.0 1.0,0.0 0.0))'",
                         footprint.evaluate())

        footprint = ExpressionType.footprint(
            [(-12, 34), (32, 34), (32, 71), (-12, 71), (-12, 34)])
        self.assertIsNotNone(footprint)
        self.assertIsInstance(footprint, Expression)
        self.assertEqual("geography'SRID=4326;Polygon((-12 34,32 34,32 "
                         "71,-12 71,-12 34))'",
                         footprint.evaluate())

        distance = ExpressionFunc.geo_distance(
            ExpressionType.property('CurrentPosition'),
            footprint
        )
        self.assertIsNotNone(distance)
        self.assertIsInstance(distance, Expression)
        self.assertEqual("geo.distance(CurrentPosition,geography'SRID=4326;"
                         "Polygon((-12 34,32 34,32 71,-12 71,-12 34))')",
                         distance.evaluate())

        intersects = ExpressionFunc.geo_intersects(
            ExpressionType.property('CurrentPosition'),
            ExpressionType.property('TargetArea')
        )
        self.assertIsNotNone(intersects)
        self.assertIsInstance(intersects, Expression)
        self.assertEqual("geo.intersects(CurrentPosition,TargetArea)",
                         intersects.evaluate())

        length = ExpressionFunc.geo_length(
            ExpressionType.property('DirectRoute')
        )
        self.assertIsNotNone(length)
        self.assertIsInstance(length, Expression)
        self.assertEqual("geo.length(DirectRoute)", length.evaluate())

    def test_case_function(self):
        values = [
            (
                ComparisonOperator.gt(
                    ExpressionType.property('X'),
                    ExpressionType.number(0)
                ),
                1),
            (ComparisonOperator.lt(
                ExpressionType.property('X'),
                ExpressionType.number(0)
            ),
             -1),
            (
                ExpressionType.bool(True),
                0
            )
        ]
        case = ExpressionFunc.case(values)
        self.assertIsNotNone(case)
        self.assertIsInstance(case, Expression)
        self.assertEqual("case(X gt 0:1,X lt 0:-1,true:0)", case.evaluate())

    def test_lambda_function(self):
        any = ExpressionFunc.any(
            'd',
            ComparisonOperator.gt(
                ExpressionType.property('d/TotalPrice'),
                ExpressionType.number(100)
            )
        )
        self.assertIsNotNone(any)
        self.assertIsInstance(any, Expression)
        self.assertEqual("any(d:d/TotalPrice gt 100)", any.evaluate())

        all = ExpressionFunc.all(
            'a',
            ComparisonOperator.gt(
                ExpressionType.property('a/TotalPrice'),
                ExpressionType.number(100)
            )
        )
        self.assertIsNotNone(all)
        self.assertIsInstance(all, Expression)
        self.assertEqual("all(a:a/TotalPrice gt 100)", all.evaluate())
