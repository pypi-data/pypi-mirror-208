import ast
import re
from enum import Enum

from tiivad.classs import Classs
from tiivad.edutest import create_file
from tiivad.file import File
from tiivad.function import Function
from tiivad.function_execution import FunctionExecution
from tiivad.help_structures import Check
from tiivad.program import Program
from tiivad.program_execution import ProgramExecution


# TODO: Refactor so that the call would be unified for all the similar ones.
# TODO: Function contains keyword vajab töötamiseks funktsiooni objekti, mida me staatiliselt kätte ei saa?


def teisenda(vananimi):
    with open(vananimi, encoding="utf8") as vana:
        failisisu = vana.read()
    failiread = failisisu.splitlines()
    tekkis_viga = False
    try:
        puu = ast.parse(failisisu)
    except:
        return False
    if not tekkis_viga and 'body' in puu._fields:
        for tipp in puu.body:
            vaja_kommenteerida = True
            if isinstance(tipp, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom, ast.Assign)):
                vaja_kommenteerida = False
                if isinstance(tipp, ast.Assign):
                    for x in ast.walk(tipp.value):
                        if isinstance(x, (ast.Call, ast.Name)):
                            vaja_kommenteerida = True
            if vaja_kommenteerida:
                for i in range(tipp.lineno - 1, tipp.end_lineno):
                    failiread[i] = '#' + failiread[i]
    return failiread


def teisenda_fail(failiread, uusnimi, cr_obj_fun=None):
    with open(uusnimi, 'w', encoding="utf8") as uus:
        uus.write('\n'.join(failiread))
        if cr_obj_fun:
            uus.write("\n" + cr_obj_fun)


def create_object_fun(body):
    return f"""def create_object_fun_auto_assess():
    {body}"""


def extract_numbers(s, allow_decimal_comma=False):
    result = []
    if allow_decimal_comma:
        rexp = """((?:\+|\-)?\d+(?:(?:\.|,)\d+)?)"""
    else:
        rexp = """((?:\+|\-)?\d+(?:\.\d+)?)"""

    for item in re.findall(rexp, s):
        try:
            result.append(int(item))
        except:
            try:
                result.append(float(item.replace(",", ".")))
            except:
                pass
    return result


def string_contains_string(str, str2):
    return str in str2


class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


def program_imports_module_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])

    for check in kwargs["generic_checks"]:
        test_result, error_msg = prog.program_imports_module2(check.check_type, check.expected_value,
                                                              check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def program_calls_function_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])

    for check in kwargs["generic_checks"]:
        test_result, error_msg = prog.program_calls_function2(check.check_type, check.expected_value,
                                                              check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            break
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def program_contains_loop_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    test_result, error_msg = prog.program_contains_loop(kwargs["failed_message"])
    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def program_contains_try_except_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    test_result, error_msg = prog.program_contains_try_except(kwargs["failed_message"])
    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def program_calls_print_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    test_result, error_msg = prog.program_calls_print(kwargs["failed_message"])
    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]
    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def program_defines_function_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])

    for check in kwargs["generic_checks"]:
        test_result, error_msg = prog.program_defines_function2(check.check_type, check.expected_value,
                                                                check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            break
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def program_contains_keyword_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])

    for check in kwargs["generic_checks"]:
        test_result, error_msg = prog.program_contains_keyword2(check.check_type, check.expected_value,
                                                                check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            break
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def program_execution_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    kwargs["checks"] = []

    for file in kwargs["input_files"]:
        create_file(file[0], file[1])

    prog = Program(program_name=kwargs["file_name"])
    user_inputs = kwargs["standard_input_data"]
    pe = ProgramExecution(prog, user_inputs)

    try:
        res, _ = pe.program_execution_and_input_count()
        if not res:
            raise
    except:
        kwargs["exception_message"] = pe.program_error_message
        kwargs["test_status"] = TestResult.FAIL.name
        check = Check()
        check.error_message = pe.program_error_message
        check.check_status = TestResult.FAIL.name
        kwargs["checks"] += [check]
        return kwargs

    if pe.io_cap:
        kwargs["actual_output"] = pe.io_cap.get_stdout()
    else:
        kwargs["actual_output"] = ""

    # Standard output checks
    for check in kwargs["generic_checks"]:
        actual_output = kwargs["actual_output"]
        if check.is_numeric:
            actual_output = extract_numbers(kwargs["actual_output"])
            test_result, error_msg = prog.program_output_numbers_correct2(validation_type=check.check_type,
                                                                          expected_output=check.expected_value,
                                                                          nothing_else=check.nothing_else,
                                                                          actual_output=actual_output,
                                                                          failed_message=check.failed_message)
        else:
            test_result, error_msg = prog.program_output_contains_keyword2(check.check_type, check.expected_value,
                                                                           check.nothing_else, actual_output,
                                                                           check.failed_message)

        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            kwargs["checks"] += kwargs["generic_checks"]
            return kwargs
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] += kwargs["generic_checks"]

    # Output file output checks
    for check in kwargs["output_file_checks"]:
        output_file_name = check.file_name
        file_output = File(output_file_name).get_file_text()
        test_result, error_msg = prog.program_output_contains_keyword2(check.check_type, check.expected_value,
                                                                       check.nothing_else, file_output,
                                                                       check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            kwargs["checks"] += kwargs["output_file_checks"]
            return kwargs
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] += kwargs["output_file_checks"]

    threw_error = pe.program_threw_error
    must_not_throw = kwargs["exception_check"]

    # Default check for the case when program executed successfully
    check = Check()
    check.before_message = kwargs["name"]
    check.passed_message = "Programmi käivitus õnnestus"  # TODO: Set as default
    check.failed_message = "Programmi käivitus ebaõnnestus"  # TODO: Set as default

    if must_not_throw is False and not threw_error or must_not_throw and threw_error:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = pe.program_error_message
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] += [check]
    return kwargs


def function_contains_loop_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    test_result, error_msg = f.function_contains_loop(kwargs["failed_message"])
    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def function_contains_keyword_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    fun_algus = None
    fun_lopp = None
    try:
        puu = prog.get_syntax_tree()
    except:
        print("error")
        return False
    if 'body' in puu._fields:
        for tipp in puu.body:
            if isinstance(tipp, ast.FunctionDef):
                if tipp.name == f_name:
                    fun_algus = tipp.lineno
                    fun_lopp = tipp.end_lineno
                    break

    if fun_algus is None or fun_lopp is None:
        check = Check()
        check.before_message = "Funktsiooni olemasolu kontroll"
        check.error_message = f"Antud nimega funktsiooni '{f_name}' ei leitud juurtasandilt"
        check.failed_message = f"Antud nimega funktsiooni '{f_name}' ei leitud juurtasandilt"
        check.check_status = TestResult.FAIL.name
        kwargs["test_status"] = TestResult.FAIL.name
        kwargs["checks"] = [check]
        return kwargs

    function_string = "\n".join(prog.file.get_file_text().split("\n")[fun_algus:fun_lopp])

    for check in kwargs["generic_checks"]:
        test_result, error_msg = f.function_contains_keyword2(check.check_type, check.expected_value,
                                                              check.nothing_else, function_string, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            break
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def function_contains_return_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    test_result, error_msg = f.function_contains_return(kwargs["failed_message"])
    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def function_calls_function_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    for check in kwargs["generic_checks"]:
        test_result, error_msg = f.function_calls_function2(check.check_type, check.expected_value,
                                                            check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            break
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def function_is_recursive_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    test_result, error_msg = f.function_is_recursive(kwargs["failed_message"])
    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def function_calls_print_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    test_result, error_msg = f.function_calls_print(kwargs["failed_message"])
    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def function_defines_function_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    for check in kwargs["generic_checks"]:
        test_result, error_msg = f.function_defines_function2(check.check_type, check.expected_value,
                                                              check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            break
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def function_imports_module_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    for check in kwargs["generic_checks"]:
        test_result, error_msg = f.function_imports_module2(check.check_type, check.expected_value,
                                                            check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def function_contains_try_except_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    test_result, error_msg = f.function_contains_try_except(kwargs["failed_message"])

    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def function_is_pure_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name

    prog = Program(program_name=kwargs["file_name"])
    f_name = kwargs["function_name"]
    f = Function(f_name, prog.get_syntax_tree())

    test_result, error_msg = f.function_is_pure(kwargs["failed_message"])

    must_not_contain = kwargs["contains_check"]

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    if not must_not_contain and not test_result or must_not_contain and test_result:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def function_execution_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    kwargs["checks"] = []

    for file in kwargs["input_files"]:
        create_file(file[0], file[1])

    converted_file_name = "converted_file.py"
    cr_obj_fun = None
    if kwargs["function_type"] == "METHOD":
        cr_obj_fun = create_object_fun(kwargs["create_object"])
    converted_file_body = teisenda(kwargs["file_name"])
    kwargs["converted_script"] = "\n".join(converted_file_body)
    if not teisenda_fail(converted_file_body, converted_file_name, cr_obj_fun):
        # TODO: Mis veateadet kuvada tahame? Kas selline olukord võimalik?
        pass

    prog = Program(program_name=converted_file_name)
    pe = ProgramExecution(prog, [])
    f_name = kwargs["function_name"]

    try:
        res, _ = pe.program_execution_and_input_count()
        if not res:
            raise
    except:
        kwargs["exception_message"] = pe.program_error_message
        kwargs["test_status"] = TestResult.FAIL.name
        check = Check()
        check.error_message = pe.program_error_message
        check.check_status = TestResult.FAIL.name
        kwargs["checks"] += [check]
        return kwargs

    if kwargs["function_type"] == "FUNCTION":
        f_obj = pe.globals_dict.get(f_name, None)
    elif kwargs["function_type"] == "METHOD":
        try:
            f_obj = pe.globals_dict.get("create_object_fun_auto_assess", None)
            f_objj = f_obj()
            f_obj = getattr(f_objj, kwargs["function_name"])
        except Exception as e:
            err_msg = f"'create_object' funktsiooni sisu täites tekkis probleem: {str(e)}"
            kwargs["exception_message"] = err_msg
            kwargs["test_status"] = TestResult.FAIL.name
            check = Check()
            check.error_message = err_msg
            check.check_status = TestResult.FAIL.name
            kwargs["checks"] += [check]
            return kwargs
    else:
        raise "function_execution_test doesn't have the mandatory 'function_type' field configured"
    fun_args = kwargs["arguments"]
    fe = FunctionExecution(f_obj, fun_args, kwargs['standard_input_data'], kwargs["return_value"])

    try:
        res, err_msg = fe.function_execution_and_input_count()
        if not res:
            raise
    except:
        kwargs["exception_message"] = str(
            fe.function_error_message if fe.function_error_message is not None else err_msg)
        kwargs["test_status"] = TestResult.FAIL.name
        check = Check()
        check.error_message = str(fe.function_error_message)
        check.check_status = TestResult.FAIL.name
        kwargs["checks"] += [check]
        return kwargs

    check = Check()
    check.before_message = kwargs.get("before_message", kwargs.get("name", ""))
    check.passed_message = kwargs.get("passed_message", "Funktsiooni käivitamine õnnestus")
    check.failed_message = kwargs.get("failed_message", "Funktsiooni käivitamine ebaõnnestus")
    test_result, error_msg = fe.function_return_value_correct()
    if test_result is False:
        kwargs["test_status"] = TestResult.FAIL.name
        check.error_message = error_msg
        check.failed_message = error_msg if check.failed_message == "" else check.failed_message
        check.check_status = TestResult.FAIL.name
        kwargs["checks"] += [check]
        return kwargs
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] += [check]

    kwargs["actual_output"] = fe.io_cap.get_stdout()

    # Standard output checks
    for check in kwargs["generic_checks"]:
        actual_output = kwargs["actual_output"]
        if check.is_numeric:
            actual_output = extract_numbers(kwargs["actual_output"])
            test_result, error_msg = fe.function_output_numbers_correct2(validation_type=check.check_type,
                                                                         outputs=check.expected_value,
                                                                         nothing_else=check.nothing_else,
                                                                         actual_output=actual_output,
                                                                         failed_message=check.failed_message)
        else:
            test_result, error_msg = fe.function_output_correct2(validation_type=check.check_type,
                                                                 outputs=check.expected_value,
                                                                 nothing_else=check.nothing_else,
                                                                 actual_output=actual_output,
                                                                 failed_message=check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            kwargs["checks"] += kwargs["generic_checks"]
            return kwargs
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] += kwargs["generic_checks"]

    # Output file output checks
    for check in kwargs["output_file_checks"]:
        output_file_name = check.file_name
        file_output = File(output_file_name).get_file_text()
        test_result, error_msg = prog.program_output_contains_keyword2(check.check_type, check.expected_value,
                                                                       check.nothing_else, file_output,
                                                                       check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
            kwargs["checks"] += kwargs["output_file_checks"]
            return kwargs
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] += (kwargs["output_file_checks"])
    return kwargs


def class_imports_module_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])
    cl = Classs(class_name=kwargs["class_name"], program_syntax_tree=prog.get_syntax_tree())
    for check in kwargs["generic_checks"]:
        test_result, error_msg = cl.class_imports_module2(check.check_type, check.expected_value,
                                                          check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def class_defines_function_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])
    cl = Classs(class_name=kwargs["class_name"], program_syntax_tree=prog.get_syntax_tree())
    for check in kwargs["generic_checks"]:
        test_result, error_msg = cl.class_defines_function2(check.check_type, check.expected_value,
                                                            check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def class_calls_class_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])
    cl = Classs(class_name=kwargs["class_name"], program_syntax_tree=prog.get_syntax_tree())
    for check in kwargs["generic_checks"]:
        test_result, error_msg = cl.class_calls_class2(check.check_type, check.expected_value,
                                                       check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def class_function_calls_function_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])
    cl = Classs(class_name=kwargs["class_name"], program_syntax_tree=prog.get_syntax_tree())
    for check in kwargs["generic_checks"]:
        test_result, error_msg = cl.class_function_calls_function2(kwargs["class_function_name"], check.check_type,
                                                                   check.expected_value, check.nothing_else,
                                                                   check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def program_defines_class_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])

    for check in kwargs["generic_checks"]:
        test_result, error_msg = prog.program_defines_class2(check.check_type, check.expected_value,
                                                             check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def program_defines_subclass_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]

    test_result, error_msg = prog.program_defines_subclass(kwargs["class_name"], kwargs["superclass_name"],
                                                           check.failed_message)
    if not test_result:
        check.error_message = error_msg
        check.check_status = TestResult.FAIL.name
        kwargs["test_status"] = TestResult.FAIL.name
    else:
        check.check_status = TestResult.PASS.name

    kwargs["checks"] = [check]
    return kwargs


def program_calls_class_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])

    for check in kwargs["generic_checks"]:
        test_result, error_msg = prog.program_calls_class2(check.check_type, check.expected_value,
                                                           check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def program_calls_class_function_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    prog = Program(program_name=kwargs["file_name"])

    for check in kwargs["generic_checks"]:
        test_result, error_msg = prog.program_calls_class_function2(check.check_type, check.expected_value,
                                                                    check.nothing_else, check.failed_message)
        if not test_result:
            check.error_message = error_msg
            check.check_status = TestResult.FAIL.name
            kwargs["test_status"] = TestResult.FAIL.name
        else:
            check.check_status = TestResult.PASS.name

    kwargs["checks"] = kwargs["generic_checks"]
    return kwargs


def class_instance_test(**kwargs):
    kwargs["test_status"] = TestResult.PASS.name
    kwargs["checks"] = []

    converted_file_name = "converted_file.py"
    cr_obj_fun = create_object_fun(kwargs["create_object"])
    converted_file_body = teisenda(kwargs["file_name"])
    kwargs["converted_script"] = "\n".join(converted_file_body)
    if not teisenda_fail(converted_file_body, converted_file_name, cr_obj_fun):
        # TODO: Mis veateadet kuvada tahame? Kas selline olukord võimalik?
        pass

    prog = Program(program_name=converted_file_name)
    pe = ProgramExecution(prog, [])

    try:
        res, _ = pe.program_execution_and_input_count()
        if not res:
            raise
    except:
        kwargs["exception_message"] = pe.program_error_message
        kwargs["test_status"] = TestResult.FAIL.name
        check = Check()
        check.before_message = kwargs["before_message"]
        check.failed_message = pe.program_error_message
        check.error_message = pe.program_error_message
        check.check_status = TestResult.FAIL.name
        kwargs["checks"] = [check]
        return kwargs

    f_obj = pe.globals_dict.get("create_object_fun_auto_assess", None)
    try:
        obj = f_obj()
    except:
        err_msg = f"Objekti {kwargs['class_name']} loomine või selle peal kutsutavate funktsioonide " \
                  f"väljakutsumine ebaõnnestus"
        kwargs["exception_message"] = err_msg
        kwargs["test_status"] = TestResult.FAIL.name
        check = Check()
        check.before_message = kwargs["before_message"]
        check.failed_message = err_msg
        check.error_message = err_msg
        check.check_status = TestResult.FAIL.name
        kwargs["checks"] = [check]
        return kwargs

    for field in kwargs["fields_final"]:
        if hasattr(obj, field[0]):
            if not getattr(obj, field[0]) == field[1]:
                err_msg = f"Objekti {kwargs['class_name']} väli {field[0]} omab väärtust  {getattr(obj, field[0])}, " \
                          f"kuid peaks omama väärtust: {field[1]}"
                kwargs["exception_message"] = err_msg
                kwargs["test_status"] = TestResult.FAIL.name
                check = Check()
                check.before_message = kwargs["before_message"]
                check.failed_message = err_msg
                check.error_message = err_msg
                check.check_status = TestResult.FAIL.name
                kwargs["checks"] = [check]
                return kwargs
        else:
            err_msg = f"Objektil {kwargs['class_name']} puudub väli {field[0]}"
            kwargs["exception_message"] = err_msg
            kwargs["test_status"] = TestResult.FAIL.name
            check = Check()
            check.before_message = kwargs["before_message"]
            check.failed_message = err_msg
            check.error_message = err_msg
            check.check_status = TestResult.FAIL.name
            kwargs["checks"] = [check]
            return kwargs

    check = Check()
    check.before_message = kwargs["before_message"]
    check.passed_message = kwargs["passed_message"]
    check.failed_message = kwargs["failed_message"]
    check.check_status = TestResult.PASS.name

    kwargs["checks"] += [check]
    return kwargs
