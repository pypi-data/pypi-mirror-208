import os.path
from inspect import signature
from math import ceil, floor
from typing import Callable, Union

from edutest import *


# File checks
def file_exists(file_name: str) -> bool:
    """
    Checks if the file exists in the current working directory.
    :param file_name: str: File name to be checked.
    :return: True if file found, False if file not found.
    """
    return os.path.isfile(file_name)


def file_not_empty(file_name: str) -> bool:
    """
    Checks if the file is empty or not.
    :param file_name: str: File name to be checked.
    :return: True if file NOT empty, False if is empty.
    """
    return os.stat(file_name).st_size > 0


# Täidab programmi etteantud sisenditega
# TODO: Refactor, et teeks vaid ühte asja.
def file_is_python(programminimi, sisendid) -> Union[dict, IOCapturing, float]:
    try:
        globs, cap = run_script(programminimi, sisendid)
    except OutOfInputsError:
        tegelik_sisendite_arv = float('Inf')
    else:
        tegelik_sisendite_arv = len(sisendid) - len(cap.get_remaining_inputs())

    return globs, cap, tegelik_sisendite_arv


# Täidab funktsiooni etteantud argumentide ja sisenditega, kontrollib ka sisendite arvu.
def täidafunk(funktsioon, argumendid, sisendid, oodatav_sisendite_arv=0, veatekst=""):
    try:
        with IOCapturing(sisendid) as cap:
            tegelik_tulemus = funktsioon(*argumendid)
    except Exception as e:
        print(e)
        raise
    return tegelik_tulemus, cap


def fun_returned(returned_result):
    return returned_result is not None


def fun_prints(function):
    return fun_uses_fun(function, "print")


# TODO: See on ainult veateate kirjutamiseks, tuleks mõelda, et kuidas neid üleüldse hallata (veateateid)
# Programmi sisendparameetrite arvu kontrollimine ja teadete väljastamine.
# Veatekst on täiendav info kasutajale vea korral.
def prog_input_count(tegelik_sisendite_arv, oodatav_sisendite_arv, veatekst=""):
    if tegelik_sisendite_arv != oodatav_sisendite_arv:
        if tegelik_sisendite_arv == 0 and oodatav_sisendite_arv > 0:
            teade = "Programm ei küsinud sisendeid.\n"
            teade += "Programm peaks küsima sisendit kasutajalt."
            print(teade)
        elif tegelik_sisendite_arv > 0 and oodatav_sisendite_arv == 0:
            teade = "Programm küsis sisendit.\n"
            teade += "Programm ei tohiks kasutajalt ühtegi sisendit küsida."
            print(teade)
        elif float('Inf') > tegelik_sisendite_arv > 0 and oodatav_sisendite_arv > 0:
            teade = "Programm küsis "
            teade += ("vähem" if tegelik_sisendite_arv < oodatav_sisendite_arv else "rohkem")
            teade += " sisendeid, kui oleks pidanud.\n"
            teade += "Programm küsis " \
                     + ", aga oleks pidanud küsima " + ".\n"
            teade += veatekst
            print(teade)
        elif tegelik_sisendite_arv == float('Inf') and oodatav_sisendite_arv > 0:
            teade = "Programm küsis rohkem sisendeid, kui oleks pidanud.\n"
            teade += "Programm peaks küsima ainult " + ".\n"
            teade += veatekst
            print(teade)


# Function checks:
def prog_has_fun(globals_dict: dict, fun_name: str) -> bool:
    # Programm sisaldab antud funktsiooni definitsiooni
    return fun_name in globals_dict and inspect.isfunction(globals_dict[fun_name])


def fun_input_count_correct(function: Callable, expected_no_of_params: int) -> bool:
    # Funktsioonil on õige arv parameetreid
    # TODO: Nimetada ümber? Sest see nimetus viitaks, et tagastataks arv, mitte tõeväärtus
    return len(signature(function).parameters) == expected_no_of_params


def check_fun(function: Callable, *args):
    # funktsiooni definitsioon on süntaktiliselt korrektne
    # - standardteek, mis kontrolliks, kas etteantud tekst on valiidne Pythoni programm või mitte
    # - kui file_is_python tagastab veateate, siis see funktsioon võib ikkagi tagastada tõese väärtuse.
    # Kontrollime, et kas funktsioon läheb käima.
    try:
        function(*args)
        return True
    except:
        return False


def fun_input_type(function: Callable, signature_types: list) -> bool:
    # * funktsiooni parameetrid on õiget tüüpi
    # TODO: Kuidas me seda kontrollida võiksime?
    # [param_type_1, param_type_2, param_type_n]
    sig = signature(function)
    p = signature(function).parameters
    # return len() == expected_no_of_params
    # TODO: Pythoni puhul jätame vahele!
    pass


def fun_contains_return(fun_name: Callable):
    # * funktsiooni definitsioon sisaldab etteantud võtmesõna
    # TODO: Miks meil seda vaja on kui me juba teame, et vastav funktsioon eksisteerib?
    # nt kontrollib, et kas tsükli käsk eksisteerib
    # tihti aetakse sassi return ja print
    # Üldisem - "text" ei pea olema funktsioon
    for node in ast.walk(ast.parse(inspect.getsource(fun_name))):
        if isinstance(node, ast.Return):
            return True
    return False


def fun_contains_loop(fun_name: Callable):
    for node in ast.walk(ast.parse(inspect.getsource(fun_name))):
        if isinstance(node, (ast.For, ast.While)):
            return True
    return False


def fun_uses_fun(function: Callable, contains_fun: str) -> bool:
    # * funktsioon kasutab etteantud funktsiooni
    # - nt rekursiivne väljakutse
    # saab kasutada progkontrolli funkpöördub nt
    # Vahel on tarvis kontrollida mitme funktsiooni olemasolu funktsioonis/programmis. Äkki on optimaalsem süntaksipuu
    # luua ühe korra? Võimalus teha funktsioon, mis tagastab süntaksipuu ja see antakse teistele funktsioonidele
    # sisendiks.
    return contains_fun in [c.func.id for c in ast.walk(ast.parse(inspect.getsource(function))) if
                            isinstance(c, ast.Call)]


def fun_uses_local_vars(fun_name: str):
    # * funktsioon kasutab ainult funktsiooni sees defineeritud muutujaid
    # - tarvis kindlaks teha terve programmi globaalsed muutujad
    # - seejärel teha kindlaks, kas kontrollitav funktsioon kasutab sama nimega mõnda muutujat, kui jah, siis vaadata,
    # Implementatsioon: Kas funktsioon kasutab mõnda muutujat, mis ei ole eelnevalt defineeritud selle funktsiooni sees?
    # Võtmesõna "global" kasutamine ka keelata ära
    # 1. Kontrollida, et kas programmi tekst sisaldab sõna "global"
    # 2. Teha kindlaks kõigi programmis defineeritud muutujate hulk
    # 3. Kontrollida, et kui funktsiooni sees oleva programmi muutuja väärtust on enne funktsiooni muudetud, siis on viga.
    defined_vars = set()
    tree = ast.parse(inspect.getsource(fun_name))
    for node in ast.walk(tree):
        if isinstance(node, ast.arg):
            defined_vars.add(node.arg)
            if node.annotation != None:
                defined_vars.add(node.annotation.id)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined_vars.add(node.id)
        if isinstance(node, ast.Call):
            defined_vars.add(node.func.id)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in defined_vars:
                return False
    return True


def fun_user_input_count(fun_name: str, no_of_inputs: int):
    # Funktsioon küsib kasutajalt õiget arvu sisendeid
    pass
    # TODO: Kas seda ei tee juba funktsioon 'täidafunk'?


def fun_modified_param_type(actual_solution, example_solution):
    # * funktsiooni parameetri muudetud väärtuse tüübistruktuur on õige
    # - nt tuleb etteantud parameetrit muuta (nt järjend), aga funktsioon ise ei tagasta midagi
    # - lõppväärtuse juures tuleb kontrollida, et kas muudetud parameeter on õigete tüüpidega
    # - Kas lihtsalt "jooksutan" funktsiooni ja seejärel vaatan muutuja tüüpi?
    if isinstance(actual_solution, (list, tuple)):
        if len(actual_solution) != len(example_solution):
            return False
        for i in range(len(actual_solution)):
            if not fun_modified_param_type(actual_solution[i], example_solution[i]):
                return False
        return True
    else:
        return type(actual_solution) == type(example_solution)


def fun_modified_param_value(actual_solution, example_solution):
    # funktsiooni parameetri muudetud väärtus on õige
    return actual_solution == example_solution


def check_result(result, expected_result, result_type='str'):
    """
    # * mida tagastatud väärtusele rakendatakse
    # * enne kui väärtuse õigsust kontrollitakse
    # - probleemid siis, kui programm tagastab ujukomaarve, seetõttu võiks vastust kontrollida hoopis vahemikku sobivusega
    # - funktsioon tagastab sõne, aga pole tegelikult oluline, et kas tegemist on suur- või väiketähtedega
    # - ehk me rakendame tudengi kirjutatud funktsiooni poolt tagastatud väärtusele mingi funktsiooni (nt .lower()) ja alles siis võrdleme etteantud tulemusega
    :param result:
    :param expected_result:
    :param result_type:
    :return:
    """
    if result_type == 'str':
        return result.strip().lower() == expected_result
    elif result_type == 'number':
        return floor(float(expected_result)) <= result <= ceil(float(expected_result))
    # TODO: Kas veel mõni tüüp?


def fun_prints_instead_of_returning(fun_name, actual_result):
    return not fun_returned(actual_result) and fun_prints(fun_name)


def fun_return_type_correct(returned_value, expected_type):
    return type(returned_value) == expected_type


def fun_return_value_correct(returned_value, expected_value):
    return returned_value == expected_value


# Väljundi kontrollid
def prog_output_not_empty(output):
    return output is not None and output.strip() != ""


def prog_output_contains_string(output, str):
    return output is not None and str in output


def prog_output_contains_items(output, items):
    if output is None:
        return False
    for i in items:
        if i not in output:
            return False
    return True


def prog_output_contains_only_these_items(output, items):
    if output is None:
        return False
    return sorted(output.strip().split("\n")) == sorted(items)


def prog_output_contains_ordered(output, items):
    if output is None:
        return False
    return output.strip().split("\n") == items


def prog_output_no_of_lines(output, no_of_lines: int):
    if output is None:
        return False
    # TODO: Kas siin peaks tühjad read eemaldama või mitte?
    return len(output.strip().split("\n")) == no_of_lines


def prog_output_contains_no_of_elements_of_type(output, el_type, no_of_elements):
    if output is None:
        return False
    formatted_output = output.strip().split("\n")
    c = 0
    for i in formatted_output:
        if c > no_of_elements:
            return False
        if type(i) == el_type:
            c += 1
    return c == no_of_elements


def prog_output_no_of_lines_not_empty(output, no_of_lines: int):
    if output is None:
        return False
    formatted_output = output.strip().split("\n")
    return len(formatted_output) == no_of_lines


def prog_output_line_contains(output, item, line_nr, arvesta_tühjade_ridadega=False):
    if output is None:
        return False
    formatted_output = output.strip().split("\n")
    return item in formatted_output[line_nr - 1]


def prog_output_line_equals(output, item, line_nr, arvesta_tühjade_ridadega=False):
    if output is None:
        return False
    formatted_output = output.strip().split("\n")
    return item == formatted_output[line_nr - 1]


def prog_output_ordered(output, items, arvesta_tühjade_ridadega=False):
    if output is None:
        return False
    # TODO: Kas see pole sama mis üks eelmine funktsioon?
    formatted_output = output.strip().split("\n")
    return formatted_output == items


def prog_output_contains(output, items, arvesta_tühjade_ridadega=False):
    if output is None:
        return False
    # TODO: Kas see pole sama mis üks eelmine funktsioon?
    return sorted(output.strip().split("\n")) == sorted(items)


def get_prog_text(file_name):
    with open(file_name, encoding='utf-8') as f:
        return f.read()


def prog_contains_text(prog_text, text: str):
    if prog_text is None:
        return False
    if text in prog_text:
        return True
    return False


def output_text_correct(output_text, text):
    if output_text is None:
        return False
    if text == output_text:
        return True
    return False


# Kontrollib, kas programm kasutab moodulit
def prog_uses_module(programmisisu, moodulinimi):
    # TODO: Refactor
    # with open(programminimi, encoding='utf-8') as f:
    #     programmisisu = f.read()
    # print(programmisisu)
    süntaksipuu = ast.parse(programmisisu)
    if type(moodulinimi) == str:
        kontrollitavad = [moodulinimi]
    elif type(moodulinimi) == list:
        kontrollitavad = moodulinimi
    for tipp in ast.walk(süntaksipuu):
        if isinstance(tipp, ast.Import):
            if 'names' in tipp._fields:
                for nimi in tipp.names:
                    if 'name' in nimi._fields:
                        for i in range(len(kontrollitavad)):
                            if nimi.name == kontrollitavad[i]:
                                return True
        if isinstance(tipp, ast.ImportFrom):
            if 'module' in tipp._fields:
                for i in range(len(kontrollitavad)):
                    if tipp.module == kontrollitavad[i]:
                        return True
    return False


def prog_uses_fun(programmisisu, funktsiooninimi):
    # TODO: Refactor
    süntaksipuu = ast.parse(programmisisu)
    if type(funktsiooninimi) == str:
        kontrollitavad = [funktsiooninimi]
    elif type(funktsiooninimi) == list:
        kontrollitavad = funktsiooninimi
    for tipp in ast.walk(süntaksipuu):
        if isinstance(tipp, ast.Call):
            if 'func' in tipp._fields:
                if 'id' in tipp.func._fields:
                    for i in range(len(kontrollitavad)):
                        if tipp.func.id == kontrollitavad[i]:
                            return True
                if 'attr' in tipp.func._fields:
                    for i in range(len(kontrollitavad)):
                        if tipp.func.attr == kontrollitavad[i]:
                            return True
    return False


def prog_uses_fun_from_set(program_data, functions_list):
    # TODO: Eelmine funktsioon tegelikult juba teeb seda.
    pass


if __name__ == "__main__":
    print(file_exists("progkontroll.py"))
    print(file_not_empty("progkontroll.py"))
    sisendid = [5, 3] * 20
    oodatav_sisendite_arv = 2
    veatekst = "Programmi sisendid peaksid olema elektriliini pikkus ja kõrvutiasetsevate postide maksimaalkaugus."
    globals_dict, cap, tegelik_sisendite_arv = file_is_python("solution.py", sisendid)
    prog_input_count(tegelik_sisendite_arv, oodatav_sisendite_arv, veatekst)
    print(prog_has_fun(globals_dict, 'test'))
    print(globals_dict['test'])
    print(type(globals_dict['test']))
    # print(fun_input_count(globals_dict['test'], 1))
    print(fun_input_type(globals_dict['test'], [str, str, int]))
    print(fun_uses_fun(globals_dict['test'], 'nottest'))
    # print(globals_dict['test'].__dir__)
    # print(globals_dict.globals)

    print("R")
    prog_output = cap.get_last_stdout()
    print(prog_output)
    print("E")

    tegelik_tulemus, cap = täidafunk(globals_dict['test'], [1], "sisend")
    print(tegelik_tulemus, cap)
    print(fun_returned(tegelik_tulemus))
    print(fun_prints(globals_dict['test']))
    print(fun_prints_instead_of_returning(globals_dict['test'], tegelik_tulemus))
    print(fun_return_type_correct(tegelik_tulemus, int))
    print(fun_return_value_correct(tegelik_tulemus, "2"))

    fun_output = cap.get_last_stdout()
    print("E")

    print(prog_output_not_empty(prog_output))
    print(prog_output.strip())
    print(type(prog_output))
    print(prog_output_contains_string(prog_output, "liini"))
    print(prog_output_contains_string(prog_output, "Liini"))
    print(prog_output_contains_items(prog_output, ["Liini", "iini"]))
    print(
        prog_output_contains_only_these_items(prog_output, ['Liini ehitamiseks läheb vaja minimaalselt 3 posti.', 'u']))
    print(prog_output_contains_ordered(prog_output, ['u', 'Liini ehitamiseks läheb vaja minimaalselt 3 posti.']))
    print(prog_output_contains_ordered(prog_output, ['Liini ehitamiseks läheb vaja minimaalselt 3 posti.', 'u']))
    print(prog_output_no_of_lines(prog_output, 3))
    print(prog_output_no_of_lines(prog_output, 2))
    print(prog_output_contains_no_of_elements_of_type(prog_output, int, 2))
    print(prog_output_contains_no_of_elements_of_type(prog_output, str, 2))
    print(prog_output_contains_no_of_elements_of_type(prog_output, str, 1))
    print(prog_output_contains_no_of_elements_of_type(prog_output, str, 3))
    print(prog_output_no_of_lines_not_empty(prog_output, 2))
    print(prog_output_no_of_lines_not_empty(prog_output, 1))
    print(prog_output_line_contains(prog_output, "ehita", 1))
    print(prog_output_line_contains(prog_output, "ehita", 2))
    print(prog_output_line_contains(prog_output, "asd", 1))
    print(prog_output_line_equals(prog_output, "u", 2))
    print(prog_output_line_equals(prog_output, "u", 1))
    print(prog_output_ordered(prog_output, ['Liini ehitamiseks läheb vaja minimaalselt 3 posti.', 'u']))
    print(prog_output_ordered(prog_output, ['u', 'Liini ehitamiseks läheb vaja minimaalselt 3 posti.']))
    print(prog_output_contains(prog_output, ['Liini ehitamiseks läheb vaja minimaalselt 3 posti.', 'u']))
    print(prog_output_contains(prog_output, ['u', 'Liini ehitamiseks läheb vaja minimaalselt 3 posti.', 'u']))
    print(prog_output_contains(prog_output, ['u', 'Liini ehitamiseks läheb vaja minimaalselt 3 posti.']))

    prog_text = get_prog_text('../test/samples/solution.py')
    print(prog_contains_text(prog_text, "postide"))
    print(prog_contains_text(prog_text, "postide2"))
    print(prog_uses_module(prog_text, "turtle"))
    print(prog_uses_module(prog_text, "math"))
    print(prog_uses_module(prog_text, "ceil"))
    print(prog_uses_fun(prog_text, "test"))
    print(prog_uses_fun(prog_text, "test2"))

    print(check_result(1, 1.2, 'number'))
    print(check_result(2, 1.2, 'number'))
    print(check_result(1.5, 1.5, 'number'))
    print(check_result(0.9, 1.5, 'number'))
    print(check_result(2.1, 1.5, 'number'))

    print(check_result('asd ', 'asd', 'str'))
    print(check_result('asd s', 'asd', 'str'))
    print(check_result('asD', 'asd', 'str'))

    print(fun_contains_return(globals_dict['test']))
    print(fun_contains_loop(globals_dict['test']))
    print(fun_uses_fun(globals_dict['test'], "print"))

    print(check_fun(globals_dict['test'], 2))
