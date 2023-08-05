
from flowhigh.model.TypeCast import TypeCast
from flowhigh.model.TreeNode import TreeNode


class AntiPattern(TypeCast, TreeNode):
    severity: str = None
    readability: str = None
    correctness: str = None
    performance: str = None
    pos: list = []
    link: str = None
    type_: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class AntiPatternBuilder (object):
    construction: AntiPattern

    
    ap_links: dict = {'AP_01': {'severity': 'Warning', 'performance': ' ', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-ansi-89-join-syntax/'}, 'AP_03': {'severity': 'Warning', 'performance': 'Y', 'readability': ' ', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-count-in-the-outer-join/'}, 'AP_09': {'severity': 'Warning', 'performance': ' ', 'readability': ' ', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-filtering-attributes-from-the-non-preserved-side-of-an-outer-join/'}, 'AP_11': {'severity': 'Warning', 'performance': ' ', 'readability': 'Y', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-implicit-column-references/'}, 'AP_14': {'severity': 'Warning', 'performance': ' ', 'readability': 'Y', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-implicit-cross-join/'}, 'AP_13': {'severity': 'Warning', 'performance': ' ', 'readability': ' ', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-inner-join-after-outer-join-in-multi-join-query/'}, 'AP_04': {'severity': 'Warning', 'performance': 'Y', 'readability': 'Y', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-nesting-scalar-subqueries-in-the-select-statement/'}, 'AP_30': {'severity': 'Caution', 'performance': 'Y', 'readability': ' ', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-or-delay-order-by-in-inline-views/'}, 'AP_18': {'severity': 'Caution', 'performance': ' ', 'readability': 'Y', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-ordinal-numbers-when-using-order-by-or-group-by/'}, 'AP_23': {'severity': 'Warning', 'performance': ' ', 'readability': 'Y', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-the-natural-join-clause/'}, 'AP_22': {'severity': 'Caution', 'performance': 'Y', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-union-for-multiple-filter-values/'}, 'AP_20': {'severity': 'Warning', 'performance': 'Y', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-unused-common-table-expressions-cte/'}, 'AP_28': {'severity': 'Caution', 'performance': 'Y', 'readability': ' ', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-using-functions-in-the-join-clause/'}, 'AP_07': {'severity': 'Caution', 'performance': 'Y', 'readability': ' ', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-using-functions-in-the-where-clause/'}, 'AP_26': {'severity': 'Warning', 'performance': 'Y', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/avoid-using-where-to-filter-aggregate-columns/'}, 'AP_02': {'severity': 'Notice', 'performance': 'Y', 'readability': ' ', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/beware-of-count-distinct/'}, 'AP_10': {'severity': 'Warning', 'performance': ' ', 'readability': ' ', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/beware-of-filtering-for-null/'}, 'AP_12': {'severity': 'Caution', 'performance': 'Y', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/beware-of-implicit-self-joins-in-a-correlated-subquery/'}, 'AP_16': {'severity': 'Warning', 'performance': ' ', 'readability': ' ', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/beware-of-null-in-combination-with-not-equal-operator/'}, 'AP_08': {'severity': 'Caution', 'performance': ' ', 'readability': ' ', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/beware-of-null-with-arithmetic-and-string-operations/'}, 'AP_05': {'severity': 'Caution', 'performance': 'Y', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/beware-of-select-star/'}, 'AP_06': {'severity': 'Notice', 'performance': 'Y', 'readability': ' ', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/beware-of-select-distinct/'}, 'AP_19': {'severity': 'Caution', 'performance': 'Y', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/split-multi-join-queries-into-smaller-chunks/'}, 'AP_15': {'severity': 'Warning', 'performance': ' ', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/use-an-alias-for-derived-columns/'}, 'AP_27': {'severity': 'Caution', 'performance': ' ', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/use-an-alias-for-inline-views/'}, 'AP_17': {'severity': 'Caution', 'performance': ' ', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/use-in-or-not-in-for-multiple-or-operators/'}, 'AP_24': {'severity': 'Warning', 'performance': 'Y', 'readability': ' ', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/use-like-instead-of-regex-where-like-is-possible/'}, 'AP_29': {'severity': 'Caution', 'performance': ' ', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/use-parentheses-when-mixing-ands-with-ors/'}, 'AP_25': {'severity': 'Caution', 'performance': 'Y', 'readability': ' ', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/use-union-all-instead-of-union/'}, 'AP_21': {'severity': 'Caution', 'performance': 'Y', 'readability': 'Y', 'correctness': ' ', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/use-window-functions-instead-of-self-joins/'}, 'AP_33': {'severity': 'Caution', 'performance': ' ', 'readability': ' ', 'correctness': 'Y', 'link': 'https://docs.sonra.io/flowhigh/master/docs/sql-optimiser/where-not-in-without-not-null-check-in-subquery/'}}
    
    def __init__(self) -> None:
        super().__init__()
        self.construction = AntiPattern()
    
    def with_severity(self, severity: str):
        if isinstance(severity, str) and severity.startswith("AP_"):
            child = self.ap_links[severity]["severity"]
        else:
            child = None
        self.construction.severity = child
    
    def with_readability(self, readability: str):
        if isinstance(readability, str) and readability.startswith("AP_"):
            child = self.ap_links[readability]["readability"]
        else:
            child = None
        self.construction.readability = child
    
    def with_correctness(self, correctness: str):
        if isinstance(correctness, str) and correctness.startswith("AP_"):
            child = self.ap_links[correctness]["correctness"]
        else:
            child = None
        self.construction.correctness = child
    
    def with_performance(self, performance: str):
        if isinstance(performance, str) and performance.startswith("AP_"):
            child = self.ap_links[performance]["performance"]
        else:
            child = None
        self.construction.performance = child
    
    def with_pos(self, pos: list):
        child = pos
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), pos)):
            self.construction.add_child(node)
        self.construction.pos = child
    
    def with_link(self, link: str):
        if isinstance(link, str) and link.startswith("AP_"):
            child = self.ap_links[link]["link"]
        else:
            child = None
        self.construction.link = child
    
    def with_type(self, type_: str):
        child = type_
        self.construction.type_ = child

    def build(self):
        return self.construction
