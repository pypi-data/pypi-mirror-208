from sympy.printing.printer import Printer


class SympyStr:
    def _sympystr(self, printer: Printer, *args):
        return str(self)
