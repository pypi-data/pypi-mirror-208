# The purpose of this module is to force sympy to treat python's lists as sympy's Arrays
# which makes our life easier. Otherwise, the following doesn't work:
# sympify("len([1,2,3])"), but instead it raises an exception:
#    AttributeError: 'list' object has no attribute 'is_Float'


from sympy import Array
from sympy.core.sympify import converter

converter[list] = lambda l: Array(l)  # noqa: E741
