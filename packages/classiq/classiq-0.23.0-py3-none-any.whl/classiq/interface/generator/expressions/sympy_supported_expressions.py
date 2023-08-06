from typing import Set

BASIC_ARITHMETIC_OPERATORS: Set[str] = {"+", "-", "*", "/", "%"}
MATHEMATICAL_FUNCTIONS: Set[str] = {
    "sin",
    "cos",
    "tan",
    "cot",
    "sec",
    "csc",
    "asin",
    "acos",
    "atan",
    "acot",
    "asec",
    "acsc",
    "sinh",
    "cosh",
    "tanh",
    "coth",
    "sech",
    "csch",
    "asinh",
    "acosh",
    "atanh",
    "acoth",
    "asech",
    "ascsch",
    "exp",
    "log",
    "ln",
    "sqrt",
    "abs",
    "floor",
}
SPECIAL_FUNCTIONS: Set[str] = {
    "erf",
    "erfc",
    "gamma",
    "beta",
    "besselj",
    "bessely",
    "besseli",
    "besselk",
    "dirichlet_eta",
    "polygamma",
    "riemann_zeta",
    "loggamma",
    "factorial",
    "binomial",
    "subfactorial",
    "primorial",
    "bell",
    "bernoulli",
    "euler",
    "catalan",
}
PIECEWISE_FUNCTIONS: Set[str] = {"Piecewise", "Heaviside"}
CONSTANTS: Set[str] = {"pi", "E", "I", "GoldenRatio", "EulerGamma", "Catalan"}
LOGIC_OPERATORS: Set[str] = {
    "And",
    "Or",
    "Not",
    "Xor",
    "Equivalent",
    "Implies",
    "Nand",
    "Nor",
}
RELATIONAL_OPERATORS: Set[str] = {"<", "<=", ">", ">=", "!=", "<>", "Eq"}

SYMPY_SUPPORTED_EXPRESSIONS: Set[str] = (
    BASIC_ARITHMETIC_OPERATORS.union(MATHEMATICAL_FUNCTIONS)
    .union(SPECIAL_FUNCTIONS)
    .union(PIECEWISE_FUNCTIONS)
    .union(CONSTANTS)
    .union(LOGIC_OPERATORS)
    .union(RELATIONAL_OPERATORS)
)
