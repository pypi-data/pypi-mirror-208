import ast

from typing import Tuple, List

from tiivad.program import Program, ValidationType


class Function:
    def __init__(self, function_name: str, program_syntax_tree: ast.Module):
        self.function_name: str = function_name
        self.program_syntax_tree: ast.Module = program_syntax_tree
        self.syntax_tree: ast.Module = None
        self.calls_print: bool = None
        self.params_count: int = None
        self.contains_return: bool = None
        self.contains_loop: bool = None
        self.uses_only_local_vars: bool = None
        self.function_threw_error: bool = None
        self.function_error_message: str = None
        self.contains_try_except: bool = None

    def get_syntax_tree(self) -> ast.FunctionDef:
        """
        Get AST syntax tree of the function at hand.
        :return: Syntax tree of the function at hand.
        """
        if self.syntax_tree is None:
            if not self.program_syntax_tree:
                self.syntax_tree = ""
            else:
                for node in ast.walk(self.program_syntax_tree):
                    if isinstance(node, ast.FunctionDef) and node.name == self.function_name:
                        self.syntax_tree = node
                        break
        if self.syntax_tree is None:
            self.syntax_tree = ""
            self.function_threw_error = True
            self.function_error_message = "Antud nimega funktsiooni ei ole defineeritud."
        return self.syntax_tree

    def get_params_count(self) -> int:
        """
        Get function parameters count.
        :return: Number of parameters.
        """
        if self.params_count is None:
            if not self.get_syntax_tree():
                return -1
            self.params_count = len(self.get_syntax_tree().args.args)
        return self.params_count

    def function_params_count_correct(self, expected_no_of_params: int, failed_message: str = "") -> Tuple[bool, str]:
        """
        Check if function parameters count is correct.
        :param expected_no_of_params: Number of expected parameters.
        :return: True if actual number of parameters is equal to expected number of parameters, False if not.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return self.get_params_count() == expected_no_of_params, failed_message

    def function_params_type_correct(self) -> bool:
        """
        Checks if function arguments are of correct type.
        :return: True if correct type, False if not.
        """
        raise NotImplementedError

    def function_imports_module(self, module_name: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function imports a module.
        :return: True if imports, False if not.
        """
        self.get_syntax_tree()
        if self.function_threw_error:
            return False, failed_message
        for node in ast.walk(self.get_syntax_tree()):
            if isinstance(node, ast.Import):
                if 'names' in node._fields:
                    for mod_name in node.names:
                        if 'name' in mod_name._fields:
                            if mod_name.name == module_name:
                                return True, failed_message
            if isinstance(node, ast.ImportFrom):
                if 'module' in node._fields:
                    for name in node.names:
                        if name.name == module_name:
                            return True, failed_message
                if node.module == module_name:
                    return True, failed_message
        return False, failed_message

    def function_imports_any_module(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function imports any module.
        :return: True if imports any, False if not.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        for node in ast.walk(self.get_syntax_tree()):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                return True, ""
        return False, failed_message

    def function_imports_module2(self, validation_type: str, functions: List[str], nothing_else: bool,
                                 failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function calls another function.
        :param function_name: Function name that is being checked.
        :return: True if the function calls the function, False if doesn't use.
        """
        if self.function_threw_error:
            return False, self.function_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for func in functions:
                if not self.function_imports_module(func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for func in functions:
                if self.function_imports_module(func, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if not self.function_imports_any_module(failed_message)[0]:
                return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for func in functions:
                if self.function_imports_module(func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for func in functions:
                if not self.function_imports_module(func, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.function_imports_any_module(failed_message)[0]:
                return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_calls_function_test: {validation_type}")

        return True, ""

    def function_defines_function(self, function_name: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function defines another function in it.
        :param function_name: Function name that is being checked.
        :return: True if the function defines another function, False if doesn't.
        """
        self.get_syntax_tree()
        if self.function_threw_error:
            return False, failed_message
        return function_name in [c.name for c in ast.walk(self.get_syntax_tree())
                                 if isinstance(c, ast.FunctionDef) and not isinstance(c, ast.Attribute)], failed_message

    def function_defines_function2(self, validation_type: str, functions: List[str], nothing_else: bool,
                                   failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function calls another function.
        :param function_name: Function name that is being checked.
        :return: True if the function calls the function, False if doesn't use.
        """
        if self.function_threw_error:
            return False, self.function_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for func in functions:
                if not self.function_defines_function(func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for func in functions:
                if self.function_defines_function(func, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if not self.function_defines_any_function(failed_message)[0]:
                return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for func in functions:
                if self.function_defines_function(func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for func in functions:
                if not self.function_defines_function(func, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.function_defines_any_function(failed_message)[0]:
                return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_calls_function_test: {validation_type}")

        return True, ""

    def function_defines_any_function(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function defines any other function in it.
        :return: True if the function defines any other function, False if doesn't.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return len([c.name for c in ast.walk(self.get_syntax_tree())
                    if isinstance(c, ast.FunctionDef)
                    and not isinstance(c, ast.Attribute)
                    and c.name != self.function_name]) > 0, failed_message

    def function_is_pure(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if the function is using only local (variables defined inside this function) vars or not.
        :return: True if function uses only local vars, False if not.
        """
        self.get_syntax_tree()
        if self.function_threw_error:
            return False, self.function_error_message
        if self.uses_only_local_vars is None:
            self.uses_only_local_vars = True
            defined_vars = set()
            for node in ast.walk(self.get_syntax_tree()):
                if isinstance(node, ast.arg):
                    defined_vars.add(node.arg)
                    if node.annotation is not None:
                        defined_vars.add(node.annotation.id)
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    defined_vars.add(node.id)
                if isinstance(node, ast.Call) and not isinstance(node.func, ast.Attribute):
                    defined_vars.add(node.func.id)
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id not in defined_vars:
                        self.uses_only_local_vars = False
                        break
        return self.uses_only_local_vars, failed_message

    def function_contains_loop(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function contains a while/for loop.
        :return: True if contains while/if loop, False if not.
        """
        self.get_syntax_tree()
        if self.function_threw_error:
            return False, self.function_error_message
        if self.contains_loop is None:
            self.contains_loop = False
            if self.get_syntax_tree():
                for node in ast.walk(self.get_syntax_tree()):
                    if isinstance(node, (ast.For, ast.While)):
                        self.contains_loop = True
                        break
        return self.contains_loop, failed_message

    def function_contains_try_except(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function contains a try/except block.
        :return: True if contains, False if not.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        if not self.get_syntax_tree():
            return False, failed_message
        if self.contains_try_except is None:
            self.contains_try_except = False
            for node in ast.walk(self.get_syntax_tree()):
                if isinstance(node, (ast.Try, ast.ExceptHandler)):
                    self.contains_try_except = True
                    break
        return self.contains_try_except, failed_message

    def function_calls_function(self, function_name: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function calls another function.
        :param failed_message:
        :param function_name: Function name that is being checked.
        :return: True if the function calls the function, False if doesn't use.
        """
        self.get_syntax_tree()
        if self.function_threw_error:
            return False, self.function_error_message
        return self.function_calls_function_from_set([function_name], failed_message)

    def function_calls_any_function(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function calls any function in it.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if defines any function, False if doesn't.
        """
        if not self.get_syntax_tree():
            return False, failed_message

        for c in ast.walk(self.get_syntax_tree()):
            if isinstance(c, ast.Call):
                return True, ""

        return False, failed_message

    def function_calls_function2(self, validation_type: str, functions: List[str], nothing_else: bool,
                                 failed_message: str = "") -> Tuple[bool, str]:
        """

        :param validation_type:
        :param functions:
        :param nothing_else:
        :param failed_message:
        :return:
        """
        if self.function_threw_error:
            return False, self.function_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for func in functions:
                if not self.function_calls_function(func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for func in functions:
                if self.function_calls_function(func, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if not self.function_calls_any_function(failed_message)[0]:
                return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for func in functions:
                if self.function_calls_function(func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for func in functions:
                if not self.function_calls_function(func, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.function_calls_any_function(failed_message)[0]:
                return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_calls_function_test: {validation_type}")

        return True, ""

    def function_calls_function_from_set(self, functions_list: list[str], failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function calls any of the given functions.
        :param failed_message:
        :param functions_list: Function names that are being checked.
        :return: True if the function calls any of the functions, False if doesn't use.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        result = []
        for c in ast.walk(self.get_syntax_tree()):
            if isinstance(c, ast.Call):
                if isinstance(c.func, ast.Attribute):
                    result.append(c.func.attr)
                    continue
                result.append(c.func.id)
        for fun in functions_list:
            if fun in result:
                return True, ""
        return False, failed_message

    def function_calls_print(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function calls print.
        :return: True if function calls print, False if not.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        if self.calls_print is None:
            self.calls_print = self.function_calls_function("print")[0]

        return self.calls_print, failed_message

    def function_is_recursive(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function is recursive.
        :return: True if recursive, False if not.
        """
        return self.function_calls_function(self.function_name)[0], failed_message

    def function_contains_return(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if function contains a return statement.
        :return: True if contains return, False if not.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        if self.contains_return is None:
            self.contains_return = False
            if not self.get_syntax_tree():
                return False, failed_message
            for node in ast.walk(self.get_syntax_tree()):
                if isinstance(node, ast.Return):
                    self.contains_return = True
                    break
        return self.contains_return, failed_message

    def function_prints_instead_of_returning(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Check if function prints instead of returning.
        :return: True if function contains print and doesn't contain a return.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return not self.function_contains_return() and self.function_calls_print(), failed_message

    @staticmethod
    def function_contains_keyword(function_string: str, keyword: str, failed_message: str = "") \
            -> Tuple[bool, str]:
        if keyword in function_string:
            return True, ""
        else:
            return False, failed_message

    def function_contains_keyword2(self, validation_type: str, keywords: List[str], nothing_else: bool,
                                   function_string: str, failed_message: str = "") -> Tuple[bool, str]:
        """

        :param validation_type:
        :param keywords:
        :param nothing_else:
        :param failed_message:
        :return:
        """
        if self.function_threw_error:
            return False, self.function_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for func in keywords:
                if not self.function_contains_keyword(function_string, func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for func in keywords:
                if self.function_contains_keyword(function_string, func, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for func in keywords:
                if self.function_contains_keyword(function_string, func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for func in keywords:
                if not self.function_contains_keyword(function_string, func, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the function_contains_keyword: {validation_type}")

        return True, ""


if __name__ == '__main__':
    p = Program("../test/samples/solution.py")
    f_name = "test"
    f = Function(f_name, p.get_syntax_tree())
    print(f.get_syntax_tree())
    print(f.get_params_count())
    print(f.function_params_count_correct(1))
    print(f.function_calls_function("print"))
    print(f.function_calls_function_from_set(["print"]))
    print(f.function_imports_module("turtle"))
    print(f.function_imports_any_module())
    print(f.function_defines_function("defined_function"))
    print(f.function_defines_any_function())
    print(f.function_calls_print())
    print(f.function_contains_return())
    print(f.function_contains_loop())
    print(f.function_is_pure())
    print(f.function_prints_instead_of_returning())
    print(f.function_is_recursive())
