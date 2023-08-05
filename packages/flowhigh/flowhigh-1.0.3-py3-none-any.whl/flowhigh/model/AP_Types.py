from enum import Enum


class AP_Types(Enum):
    NonAnsiJoin = 1
    CountDistinct = 2
    CountInOuterJoin = 3
    ScalarQueryInSelect = 4
    SelectStar = 5
    DistinctUsage = 6
    FunctionInWhereClause = 7
    NullWithArithmeticAndString = 8
    FilteringAttributesFromTheNonPreservedSideOfAnOuterJoin = 9
    SearchingForNull = 10
    ImplicitColumnUsage = 11
    ImplicitSelfJoinInSubQuery = 12
    InnerJoinAfterOuterJoin = 13
    ImplicitCrossJoin = 14
    AnonymousColumn = 15
    NullAndNotEqualOperator = 16
    OrVersusInAndNotIn = 17
    OrdinalNumberUsage = 18
    OverloadedJoins = 19
    UnusedCTE = 20
    SelfJoin = 21
    UnionForMultipleFilters = 22
    NaturalJoin = 23
    RegexUsedInsteadOfLike = 24
    UnionUsage = 25
    WhereInsteadOfHaving = 26
    AnonymousSubQuery = 27
    FunctionInJoin = 28
    ParenthesisWithAndOr = 29
    DelayOrAvoidOrderBy = 30
    NotInWithoutNotNullCheckInSubQuery = 31

