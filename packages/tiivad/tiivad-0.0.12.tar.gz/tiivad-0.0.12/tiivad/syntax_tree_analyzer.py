import ast, re
from typing import Set, Type
from enum import Enum

class ValidationType(Enum):
    ALL_OF_THESE = "ALL_OF_THESE"
    ANY_OF_THESE = "ANY_OF_THESE"
    ANY = "ANY"
    NONE_OF_THESE = "NONE_OF_THESE"
    MISSING_AT_LEAST_ONE_OF_THESE = "MISSING_AT_LEAST_ONE_OF_THESE"
    NONE = "NONE"

class SyntaxTreeAnalyzer:
    def __init__(self, tree: ast.Module):
        self.tree = tree
        self.defines_class_names, self.defines_subclass_names = set(), set()
        self.defines_function_names, self.calls_function_names = set(), set()
        self.calls_class_function_names, self.imports_module_names = set(), set()
        self.contains_keyword_names = set(re.findall(r'\w+', ast.unparse(tree)))
        self.contains_loop_tv = self.contains_try_except_tv = self.contains_return_tv = False
        self.is_function_tv = isinstance(tree, ast.FunctionDef)
        self.is_class_tv = isinstance(tree, ast.ClassDef)
        self.is_pure_tv = self.is_function_tv
        defined_vars = set()

        for x in ast.walk(tree):
            if x == tree:
                continue
            if isinstance(x, ast.Import):
                if 'names' in x._fields:
                    for y in x.names:
                        if 'name' in y._fields:
                            self.imports_module_names |= set(y.name.split("."))
            elif isinstance(x, ast.ImportFrom):
                if 'module' in x._fields:
                    self.imports_module_names |= set(x.module.split("."))
            elif isinstance(x, ast.ClassDef):
                self.defines_class_names.add(x.name)
                if 'bases' in x._fields:
                    for y in x.bases:
                        if 'id' in y._fields:
                            self.defines_subclass_names.add((x.name, y.id))
            elif isinstance(x, ast.FunctionDef):
                self.defines_function_names.add(x.name)
            elif isinstance(x, (ast.For, ast.While, ast.comprehension)):
                self.contains_loop_tv = True
            elif isinstance(x, (ast.Try, ast.ExceptHandler)):
                self.contains_try_except_tv = True
            elif isinstance(x, ast.Call):
                if isinstance(x.func, ast.Name):
                    self.calls_function_names.add(x.func.id)
                    defined_vars.add(x.func.id)
                elif isinstance(x.func, ast.Attribute):
                    self.calls_function_names.add(x.func.attr)
                    self.calls_class_function_names.add(x.func.attr)
                    defined_vars.add(x.func.attr)
            elif isinstance(x, ast.arg):
                defined_vars.add(x.arg)
            elif isinstance(x, ast.Name):
                if isinstance(x.ctx, ast.Store):
                    defined_vars.add(x.id)
                elif isinstance(x.ctx, ast.Load):
                    if x.id not in defined_vars:
                        self.is_pure_tv = False
            elif isinstance(x, ast.Return):
                self.contains_return_tv = True


    def imports_module(self, name: str = None) -> bool:
        return len(self.imports_module_names) > 0 if name is None \
            else name in self.imports_module_names

    def defines_class(self, name: str = None) -> bool:
        return len(self.defines_class_names) > 0 if name is None \
            else name in self.defines_class_names

    def defines_subclass(self, name: str, superclass_name: str) -> bool:
        return (name, superclass_name) in self.defines_subclass_names

    def defines_function(self, name: str = None) -> bool:
        return len(self.defines_function_names) > 0 if name is None \
            else name in self.defines_function_names

    def contains_loop(self) -> bool:
        return self.contains_loop_tv

    def contains_try_except(self) -> bool:
        return self.contains_try_except_tv

    def contains_keyword(self, name: str = None) -> bool:
        return len(self.contains_keyword_names) > 0 if name is None \
            else name in self.contains_keyword_names

    def calls_function(self, name: str = None) -> bool:
        return len(self.calls_function_names) > 0 if name is None \
            else name in self.calls_function_names

    def calls_print(self) -> bool:
        return "print" in self.calls_function_names

    def creates_instance(self, name: str = None) -> bool:
        return len(self.calls_function_names & self.defines_class_names) > 0 if name is None \
            else name in self.calls_function_names & self.defines_class_names

    def calls_class_function(self, name: str = None) -> bool:
        return len(self.calls_class_function_names) > 0 if name is None \
            else name in self.calls_class_function_names

    def is_class(self) -> bool:
        return self.is_class_tv

    def is_function(self) -> bool:
        return self.is_function_tv

    def is_recursive(self) -> bool:
        return self.is_function_tv and self.calls_function(self.tree.name)

    def is_pure(self) -> bool:
        return self.is_pure_tv

    def contains_return(self) -> bool:
        return self.contains_return_tv

    def prints_instead_of_returning(self) -> bool:
        return self.is_function_tv and self.calls_print() and not self.contains_return()

    def analyze_with_quantifier(self, target: str, quantifier: str, names: Set[str] = set(),
                                nothing_else: bool = False) -> bool:
        match target:
            case 'imports_module': targetset = self.imports_module_names
            case 'defines_function': targetset = self.defines_function_names
            case 'calls_function': targetset = self.calls_function_names
            case 'contains_keyword': targetset = self.contains_keyword_names
            case 'defines_class': targetset = self.defines_class_names
            case 'creates_instance': targetset = self.defines_class_names & self.calls_function_names
            case 'calls_class_function': targetset = self.calls_class_function_names
            case _: return False
        match quantifier:
            case ValidationType.ALL_OF_THESE.name:
                return names <= targetset and (not nothing_else or targetset <= names)
            case ValidationType.ANY_OF_THESE.name:
                return len(names & targetset) > 0 and (not nothing_else or targetset <= names)
            case ValidationType.ANY.name:
                return len(targetset) > 0
            case ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
                return not (names <= targetset)
            case ValidationType.NONE_OF_THESE.name:
                return len(names & targetset) == 0
            case ValidationType.NONE.name:
                return len(targetset) == 0
            case _:
                return False

if __name__ == '__main__':
    from tiivad.program import Program
    from tiivad.function import Function
    p = Program("../test/samples/prog5-raamat.py")
    f = Function("does_not_define_a", p.get_syntax_tree())
    s = SyntaxTreeAnalyzer(p.get_syntax_tree())
    print(s.analyze_with_quantifier("creates_instance", "ALL_OF_THESE", {'Raamat', 'Jutustus'}, True))

