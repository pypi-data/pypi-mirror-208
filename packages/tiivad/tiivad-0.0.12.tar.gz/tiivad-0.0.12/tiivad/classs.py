import ast
from typing import Tuple, List
from tiivad.program import Program, ValidationType


class Classs:
    def __init__(self, class_name: str, program_syntax_tree: ast.Module):
        self.class_name: str = class_name
        self.program_syntax_tree: ast.Module = program_syntax_tree
        self.syntax_tree: ast.Module = None
        self.class_threw_error: bool = None
        self.class_error_message: str = None

    def get_syntax_tree(self) -> ast.FunctionDef:
        """
        Get AST syntax tree of the class at hand.
        :return: Syntax tree of the class at hand.
        """
        if self.syntax_tree is None:
            if not self.program_syntax_tree:
                self.syntax_tree = ""
            else:
                for node in ast.walk(self.program_syntax_tree):
                    if isinstance(node, ast.ClassDef) and node.name == self.class_name:
                        self.syntax_tree = node
                        break
        if self.syntax_tree is None:
            self.syntax_tree = ""
            self.class_threw_error = True
            self.class_error_message = "Antud nimega klassi ei ole defineeritud."
        return self.syntax_tree

    def class_imports_module(self, module_name: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if class imports a module.
        :return: True if imports, False if not.
        """
        self.get_syntax_tree()
        if self.class_threw_error:
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

    def class_imports_any_module(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if class imports any module.
        :return: True if imports any, False if not.
        """
        if self.class_threw_error:
            return False, self.class_error_message
        for node in ast.walk(self.get_syntax_tree()):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                return True, ""
        return False, failed_message

    def class_imports_module2(self, validation_type: str, elements: List[str], nothing_else: bool,
                              failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if class calls  function.
        :param function_name: Function name that is being checked.
        :return: True if the class calls the function, False if doesn't use.
        """
        if self.class_threw_error:
            return False, self.class_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for el in elements:
                if not self.class_imports_module(el, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for el in elements:
                if self.class_imports_module(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if not self.class_imports_any_module(failed_message)[0]:
                return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for el in elements:
                if self.class_imports_module(el, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for el in elements:
                if not self.class_imports_module(el, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.class_imports_any_module(failed_message)[0]:
                return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the class_imports_module_test: {validation_type}")

        return True, ""

    def class_defines_function(self, function_name: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if class defines function in it.
        :param function_name: Function name that is being checked.
        :return: True if the class defines function, False if doesn't.
        """
        self.get_syntax_tree()
        if self.class_threw_error:
            return False, failed_message
        return function_name in [c.name for c in ast.walk(self.get_syntax_tree())
                                 if isinstance(c, ast.FunctionDef) and not isinstance(c, ast.Attribute)], \
               failed_message

    def class_defines_any_function(self, failed_message: str = "") -> Tuple[bool, str]:
        """
         Checks if class defines any function in it.
         :return: True if the class defines any function, False if doesn't.
         """
        if self.class_threw_error:
            return False, self.class_error_message
        return len([c.name for c in ast.walk(self.get_syntax_tree())
                    if isinstance(c, ast.FunctionDef)
                    and not isinstance(c, ast.Attribute)
                    and c.name != self.class_name]) > 0, failed_message

    def class_defines_function2(self, validation_type: str, elements: List[str], nothing_else: bool,
                                failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if class calls function.
        :param function_name: Function name that is being checked.
        :return: True if the class calls the function, False if doesn't use.
        """
        if self.class_threw_error:
            return False, self.class_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for el in elements:
                if not self.class_defines_function(el, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for el in elements:
                if self.class_defines_function(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if not self.class_defines_any_function(failed_message)[0]:
                return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for el in elements:
                if self.class_defines_function(el, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for el in elements:
                if not self.class_defines_function(el, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.class_defines_any_function(failed_message)[0]:
                return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the class_defines_function2_test: {validation_type}")

        return True, ""

    def class_calls_class(self, class_name: str, failed_message: str = "") -> Tuple[bool, str]:
        if self.class_threw_error:
            return False, self.class_error_message
        if class_name in set(x.name for x in ast.walk(self.program_syntax_tree) if isinstance(x, ast.ClassDef)):
            for x in ast.walk(self.get_syntax_tree()):
                if isinstance(x, ast.Call) and 'func' in x._fields and 'id' in x.func._fields and \
                        x.func.id == class_name:
                    return True, ""
        return False, failed_message

    def class_calls_any_class(self, failed_message: str = "") -> Tuple[bool, str]:
        if self.class_threw_error:
            return False, self.class_error_message
        allclasses = set(x.name for x in ast.walk(self.program_syntax_tree) if isinstance(x, ast.ClassDef))
        for x in ast.walk(self.get_syntax_tree()):
            if isinstance(x, ast.Call) and 'func' in x._fields and 'id' in x.func._fields and \
                    x.func.id in allclasses:
                return True, ""
        return False, failed_message

    def class_calls_class2(self, validation_type: str, elements: List[str], nothing_else: bool,
                           failed_message: str = "") -> Tuple[bool, str]:
        if self.class_threw_error:
            return False, self.class_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for el in elements:
                if not self.class_calls_class(el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for el in elements:
                if self.class_calls_class(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if self.class_calls_any_class(failed_message)[0]:
                return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for el in elements:
                if self.class_calls_class(el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for el in elements:
                if not self.class_calls_class(el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.class_calls_any_class(failed_message)[0]:
                return False, failed_message
            return True, ""
        else:
            raise NotImplementedError(
                f"The following type is not implemented for the class_calls_class_test: {validation_type}")

    def class_function_calls_function(self, class_function_name: str, function_name: str,
                                      failed_message: str = "") -> Tuple[bool, str]:
        if self.class_threw_error:
            return False, self.class_error_message
        for x in ast.walk(self.get_syntax_tree()):
            if isinstance(x, ast.FunctionDef) and x.name == class_function_name:
                for y in ast.walk(x):
                    if isinstance(y, ast.Call):
                        if 'id' in y.func._fields and y.func.id == function_name:
                            return True, ""
                        if 'attr' in y.func._fields and y.func.attr == function_name:
                            return True, ""
        return False, failed_message

    def class_function_calls_any_function(self, class_function_name: str, failed_message: str = "") -> \
            Tuple[bool, str]:
        if self.class_threw_error:
            return False, self.class_error_message
        for x in ast.walk(self.get_syntax_tree()):
            if isinstance(x, ast.FunctionDef) and x.name == class_function_name:
                for y in ast.walk(x):
                    if isinstance(y, ast.Call):
                        return True, ""
        return False, failed_message

    def class_function_calls_function2(self, class_function_name: str, validation_type: str, elements: List[str],
                                       nothing_else: bool, failed_message: str = "") -> Tuple[bool, str]:
        if self.class_threw_error:
            return False, self.class_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for el in elements:
                if not self.class_function_calls_function(class_function_name, el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for el in elements:
                if self.class_function_calls_function(class_function_name, el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.ANY.name:
            if self.class_function_calls_any_function(class_function_name, failed_message)[0]:
                return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for el in elements:
                if self.class_function_calls_function(class_function_name, el, failed_message)[0]:
                    return False, failed_message
            return True, ""

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for el in elements:
                if not self.class_function_calls_function(class_function_name, el, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE.name:
            if self.class_function_calls_any_function(class_function_name, failed_message)[0]:
                return False, failed_message
            return True, ""
        else:
            raise NotImplementedError(
                f"The following type is not implemented for the class_function_calls_function_test: "
                f"{validation_type}")

    def class_function_execution(self):
        pass

    def class_instance(self):
        pass


# Testimiseks
if __name__ == '__main__':
    p = Program("../test/samples/prog5-raamat.py")
    c = Classs("Jutustus", p.get_syntax_tree())
    # print(c.class_imports_module())
    # print(c.class_imports_any_module())
    # print(c.class_imports_module2(ValidationType.ANY.name, [], True))
    # print(c.class_defines_function("x"))
    # print(c.class_defines_any_function())
    # print(c.class_calls_any_class())
    # print(c.class_function_calls_any_function("suurenda_hinda"))
