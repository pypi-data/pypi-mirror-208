import ast
from typing import Tuple, List

from tiivad.file import File
from tiivad.t import format_error

from enum import Enum


def contains_number(nums, x, allowed_error=0.001):
    for num in nums:
        if abs(num - x) <= allowed_error:
            return True

    return False


class ValidationType(Enum):
    ALL_OF_THESE = "ALL_OF_THESE"
    ANY_OF_THESE = "ANY_OF_THESE"
    ANY = "ANY"
    NONE_OF_THESE = "NONE_OF_THESE"
    MISSING_AT_LEAST_ONE_OF_THESE = "MISSING_AT_LEAST_ONE_OF_THESE"
    NONE = "NONE"


class Program:
    def __init__(self, program_name: str):
        self.file: File = File(program_name)
        self.syntax_tree: ast.Module = None
        self.contains_loop: bool = None
        self.calls_print: bool = None
        self.contains_try_except: bool = None

    def get_syntax_tree(self) -> ast.Module:
        """
        Get AST syntax tree of the program at hand.
        :return: Syntax tree of the program at hand.
        """
        if self.syntax_tree is None:
            try:
                self.syntax_tree = ast.parse(self.file.get_file_text())
            except Exception as e:
                self.syntax_tree = ""
        return self.syntax_tree

    def program_imports_module(self, module_name: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program imports module.
        :param module_name: Module name that is being checked.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if the program imports the specified module, False if doesn't import.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        for node in ast.walk(self.get_syntax_tree()):
            if isinstance(node, ast.Import):
                if 'names' in node._fields:
                    for mod_name in node.names:
                        if 'name' in mod_name._fields:
                            if mod_name.name == module_name:
                                return True, failed_message
                            split_names = mod_name.name.split(".")
                            for split_name in split_names:
                                if split_name == module_name:
                                    return True, failed_message
            if isinstance(node, ast.ImportFrom):
                if 'module' in node._fields:
                    for name in node.names:
                        if name.name == module_name:
                            return True, failed_message
                    if node.module == module_name:
                        return True, failed_message
                    split_names = node.module.split(".")
                    for split_name in split_names:
                        if split_name == module_name:
                            return True, failed_message

        return False, format_error(failed_message, {"module_name": module_name})

    def program_imports_module2(self, validation_type: str, modules: List[str], nothing_else: bool,
                                failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for module in modules:
                if not self.program_imports_module(module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for module in modules:
                if self.program_imports_module(module, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if not self.program_imports_any_module(failed_message)[0]:
                return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for module in modules:
                if self.program_imports_module(module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for module in modules:
                if not self.program_imports_module(module, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.program_imports_any_module(failed_message)[0]:
                return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_imports_module_test: {validation_type}")

        return True, ""

    def program_imports_module_from_set(self, module_names: List[str], failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program imports any given module from the set.
        :param module_names: Module names that are being checked.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if the program imports any module from the set, False if it doesn't import.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        for module_name in module_names:
            if self.program_imports_module(module_name)[0]:
                return True, failed_message
        return False, format_error(failed_message, {"module_name": module_names})

    def program_imports_any_module(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program imports any module.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if imports any, False if not.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        for node in ast.walk(self.get_syntax_tree()):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                return True, failed_message
        return False, failed_message

    def program_defines_function(self, function_name: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program defines a function.
        :param failed_message: The message that will be displayed in case of failing the test.
        :param function_name: Function name that is being checked.
        :return: True if the program defines the function, False if doesn't use.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        defines_function = function_name in [c.name for c in ast.walk(self.get_syntax_tree())
                                             if isinstance(c, ast.FunctionDef) and not isinstance(c, ast.Attribute)]
        if not defines_function:
            failed_message = format_error(failed_message, {"function_name": function_name})

        return defines_function, failed_message

    def program_defines_any_function(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program defines any function in it.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if defines any other function, False if doesn't.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        defines_function = len([c.name for c in ast.walk(self.get_syntax_tree())
                                if isinstance(c, ast.FunctionDef)
                                and not isinstance(c, ast.Attribute)]) > 0

        return defines_function, failed_message

    def program_contains_loop(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program contains a while/for loop (including in functions).
        :return: True if contains a loop, False if not.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        if self.contains_loop is None:
            self.contains_loop = False
            for node in ast.walk(self.get_syntax_tree()):
                if isinstance(node, (ast.For, ast.While, ast.comprehension)):
                    self.contains_loop = True
                    break
        return self.contains_loop, failed_message

    def program_contains_try_except(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program contains a try/except block (including in functions).
        :return: True if contains a try/except block, False if not.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        if self.contains_try_except is None:
            self.contains_try_except = False
            for node in ast.walk(self.get_syntax_tree()):
                if isinstance(node, (ast.Try, ast.ExceptHandler)):
                    self.contains_try_except = True
                    break
        return self.contains_try_except, failed_message

    def program_calls_function(self, function_name: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program calls a given function.
        :param function_name: str, function name to be checked.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if program calls the given function, False if not.
        """
        result, _ = self.program_calls_function_from_set([function_name])
        if not result:
            return result, format_error(failed_message, {"function_name": function_name})
        return result, failed_message

    def program_calls_any_function(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program calls any function in it.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if defines any other function, False if doesn't.
        """
        if not self.get_syntax_tree():
            return False, failed_message

        for c in ast.walk(self.get_syntax_tree()):
            if isinstance(c, ast.Call):
                return True, ""

        return False, failed_message

    def program_calls_function2(self, validation_type: str, modules: List[str], nothing_else: bool,
                                failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for module in modules:
                if not self.program_calls_function(module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for module in modules:
                if self.program_calls_function(module, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if not self.program_calls_any_function(failed_message)[0]:
                return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for module in modules:
                if self.program_calls_function(module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for module in modules:
                if not self.program_calls_function(module, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.program_calls_any_function(failed_message)[0]:
                return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_calls_function_test: {validation_type}")

        return True, ""

    def program_defines_function2(self, validation_type: str, modules: List[str], nothing_else: bool,
                                  failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for module in modules:
                if not self.program_defines_function(module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for module in modules:
                if self.program_defines_function(module, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if not self.program_defines_any_function(failed_message)[0]:
                return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for module in modules:
                if self.program_defines_function(module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for module in modules:
                if not self.program_defines_function(module, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.program_defines_any_function(failed_message)[0]:
                return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_defines_function_test: {validation_type}")

        return True, ""

    def program_calls_function_from_set(self, functions_list: list[str], failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program calls a function from a given list.
        :param functions_list: List of function names.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if any of the functions in list are called, False if not.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        for node in ast.walk(self.get_syntax_tree()):
            if isinstance(node, ast.Call):
                if 'func' in node._fields:
                    if 'id' in node.func._fields:
                        for i in range(len(functions_list)):
                            if node.func.id == functions_list[i]:
                                return True, failed_message
                    if 'attr' in node.func._fields:
                        for i in range(len(functions_list)):
                            if node.func.attr == functions_list[i]:
                                return True, failed_message
        return False, format_error(failed_message, {"functions_list": functions_list})

    def program_calls_print(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if program calls print.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if program calls print, False if not.
        """
        if not self.get_syntax_tree():
            return False, failed_message
        if self.calls_print is None:
            self.calls_print, _ = self.program_calls_function("print")
        return self.calls_print, failed_message

    def program_contains_keyword(self, keyword: str, failed_message: str = "") -> Tuple[bool, str]:
        """

        :param keyword:
        :param failed_message:
        :return:
        """
        if keyword in self.file.get_file_text():
            return True, ""
        else:
            return False, failed_message

    def program_contains_keyword2(self, validation_type: str, modules: List[str], nothing_else: bool,
                                  failed_message: str = "") -> Tuple[bool, str]:
        if validation_type == ValidationType.ALL_OF_THESE.name:
            for module in modules:
                if not self.program_contains_keyword(module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for module in modules:
                if self.program_contains_keyword(module, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for module in modules:
                if self.program_defines_function(module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for module in modules:
                if not self.program_defines_function(module, failed_message)[0]:
                    return True, failed_message
            return False, failed_message
        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_contains_keyword test: {validation_type}")

        return True, ""

    @staticmethod
    def program_output_contains_keyword(output: str, keyword: str, failed_message: str = "") -> Tuple[bool, str]:
        """

        :param output:
        :param keyword:
        :param failed_message:
        :return:
        """
        if keyword in output:
            return True, ""
        else:
            return False, failed_message

    def program_output_contains_keyword2(self, validation_type: str, expected_output: List[str], nothing_else: bool,
                                         actual_output: str, failed_message: str = "") -> Tuple[bool, str]:
        if validation_type == ValidationType.ALL_OF_THESE.name:
            for module in expected_output:
                if not self.program_output_contains_keyword(actual_output, module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for module in expected_output:
                if self.program_output_contains_keyword(actual_output, module, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for module in expected_output:
                if self.program_output_contains_keyword(actual_output, module, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for module in expected_output:
                if not self.program_output_contains_keyword(actual_output, module, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_output_contains_keyword2: {validation_type}")

        return True, ""

    def program_output_numbers_correct2(self, validation_type: str, expected_output: List[str], nothing_else: bool,
                                        actual_output: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        :param actual_output:
        :param validation_type:
        :param expected_output:
        :param nothing_else:
        :param failed_message:
        :return:
        """
        if validation_type == ValidationType.ALL_OF_THESE.name:
            for module in expected_output:
                if not contains_number(actual_output, module):
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for module in expected_output:
                if contains_number(actual_output, module):
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for module in expected_output:
                if contains_number(actual_output, module):
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for module in expected_output:
                if not contains_number(actual_output, module):
                    return True, failed_message
            return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_output_contains_keyword2: {validation_type}")

        return True, ""

    def program_defines_class(self, class_name: str, failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message
        for x in ast.walk(self.get_syntax_tree()):
            if isinstance(x, ast.ClassDef) and x.name == class_name:
                return True, ""
        failed_message = format_error(failed_message, {"class_name": class_name})
        return False, failed_message

    def program_defines_any_class(self, failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message
        for x in ast.walk(self.get_syntax_tree()):
            if isinstance(x, ast.ClassDef):
                return True, ""
        return False, failed_message

    def program_defines_class2(self, validation_type: str, elements: List[str], nothing_else: bool,
                               failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for el in elements:
                if not self.program_defines_class(el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for el in elements:
                if self.program_defines_class(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if self.program_defines_any_class(failed_message)[0]:
                return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for el in elements:
                if self.program_defines_class(el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for el in elements:
                if not self.program_defines_class(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.program_defines_any_class(failed_message)[0]:
                return False, failed_message
            return True, ""
        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_defines_class_test: {validation_type}")

    def program_defines_subclass(self, class_name: str, superclass_name: str, failed_message: str = "") -> \
            Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message
        for x in ast.walk(self.get_syntax_tree()):
            if isinstance(x, ast.ClassDef) and x.name == class_name and len(x.bases) > 0:
                for y in x.bases:
                    if y.id == superclass_name:
                        return True, ""
        failed_message = format_error(failed_message, {"class_name": class_name, "superclass_name": superclass_name})
        return False, failed_message

    def program_calls_class(self, class_name: str, failed_message: str = "") -> Tuple[bool, str]:
        if self.program_defines_class(class_name, failed_message)[0] and \
                self.program_calls_function(class_name, failed_message)[0]:
            return True, ""
        else:
            return False, format_error(failed_message, {"class_name": class_name})

    def program_calls_any_class(self, failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message
        for x in ast.walk(self.get_syntax_tree()):
            if isinstance(x, ast.ClassDef) and self.program_calls_function(x.name, failed_message):
                return True, ""
        return False, failed_message

    def program_calls_class2(self, validation_type: str, elements: List[str], nothing_else: bool,
                             failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for el in elements:
                if not self.program_calls_class(el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for el in elements:
                if self.program_calls_class(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if self.program_calls_any_class(failed_message)[0]:
                return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for el in elements:
                if self.program_calls_class(el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for el in elements:
                if not self.program_calls_class(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.program_calls_any_class(failed_message)[0]:
                return False, failed_message
            return True, ""
        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_calls_class_test: {validation_type}")

    def program_calls_class_function(self, function_name: str, failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message
        for node in ast.walk(self.get_syntax_tree()):
            if isinstance(node, ast.Call):
                if 'func' in node._fields:
                    if 'attr' in node.func._fields:
                        if node.func.attr == function_name:
                            return True, ""
        return False, failed_message

    def program_calls_any_class_function(self, failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message
        for node in ast.walk(self.get_syntax_tree()):
            if isinstance(node, ast.Call):
                if 'func' in node._fields:
                    if 'attr' in node.func._fields:
                        return True, ""
        return False, failed_message

    def program_calls_class_function2(self, validation_type: str, elements: List[str], nothing_else: bool,
                                      failed_message: str = "") -> Tuple[bool, str]:
        if not self.get_syntax_tree():
            return False, failed_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for el in elements:
                if not self.program_calls_class_function(el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for el in elements:
                if self.program_calls_class_function(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if self.program_calls_any_class_function(failed_message)[0]:
                return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for el in elements:
                if self.program_calls_class_function(el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for el in elements:
                if not self.program_calls_class_function(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.program_calls_any_class_function(failed_message)[0]:
                return False, failed_message
            return True, ""

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_calls_class_test: {validation_type}")


if __name__ == '__main__':
    prog = Program("../test/samples/prog5-raamat.py")
    print(prog.program_calls_class_function("print_info"))
    """
    print(prog.program_imports_module("math"))
    print(prog.get_syntax_tree())
    print(prog.program_defines_function("test"))
    print(prog.program_defines_any_function())
    print(prog.program_imports_module("math"))
    print(prog.program_imports_any_module())
    print(prog.program_calls_function("test"))
    print(prog.program_calls_function("ceil"))
    print(prog.program_calls_function_from_set(["t", "test"]))
    print(prog.program_calls_function_from_set(["t", "t2"]))
    print(prog.program_contains_loop())
    print(prog.program_calls_print())
    """
