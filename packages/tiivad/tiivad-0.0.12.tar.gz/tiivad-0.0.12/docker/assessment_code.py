from tiivad import *

validate_files(['''submission.py'''])
execute_test(file_name='''submission.py''', standard_input_data=['''Kasutajasisend'''],
             input_files=[('''sisendfail.txt''', '''Sisendfaili sisu.''')], generic_checks=[
        GenericChecks(check_type='''ANY_OF_THESE''', nothing_else=None, expected_value=['''down''', '''up'''],
                      consider_elements_order=False, before_message='''Kontrollib, kas väljund sisaldab võtmesõna.''',
                      passed_message='''Programmi väljund sisaldab antud võtmesõna.''',
                      failed_message='''Programmi väljund ei sisalda antud võtmesõna.''')], output_file_checks=[
        OutputFileChecks(file_name='''valjundfail.txt''', check_type='''ALL_OF_THESE''', nothing_else=None,
                         expected_value=['''Väljundfaili eeldatav sisu'''], consider_elements_order=False,
                         before_message='''Kontrollib, kas väljundfail sisaldab võtmesõna.''',
                         passed_message='''Programmi väljundfail sisaldab antud võtmesõna.''',
                         failed_message='''Programmi väljundfail ei sisalda antud võtmesõna.''')], exception_check=True,
             before_message=None, passed_message=None, failed_message=None, type='''program_execution_test''',
             points=1.0, id=None, name='''Programmi käivituse test.''', inputs=None, passed_next=None, failed_next=None,
             visible_to_user=None)
execute_test(file_name='''submission.py''', generic_checks=[
    GenericChecks(check_type='''ALL_OF_THESE''', nothing_else=None, expected_value=['''turtle'''],
                  before_message='''Kontrollib, kas programm impordib mooduli.''',
                  passed_message='''Programm importis mooduli.''',
                  failed_message='''Programm ei importinud moodulit.''')], type='''program_imports_module_test''',
             points=10.0, id=None, name='''Programm impordib mooduli''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', generic_checks=[
    GenericChecks(check_type='''ANY_OF_THESE''', nothing_else=None, expected_value=['''close'''],
                  before_message='''Kontrollib, kas programm kutsub välja turtle funktsiooni.''',
                  passed_message='''Programm kutsus välja vähemalt ühe turtle funktsiooni.''',
                  failed_message='''Programm ei kutsnud välja ühtegi turtle funktsiooni.''')],
             type='''program_calls_function_test''', points=1.0, id=None,
             name='''Programm kutsub välja turtle funktsiooni.''', inputs=None, passed_next=None, failed_next=None,
             visible_to_user=None)
execute_test(file_name='''submission.py''', contains_check=False,
             before_message='''Kontrollib, kas programmis esineb tsükkel.''',
             passed_message='''Programmis esines tsükkel.''', failed_message='''Programmis ei esine ühtegi tsüklit.''',
             type='''program_contains_loop_test''', points=1.0, id=None, name='''Programmis esineb tsükkel.''',
             inputs=None, passed_next=None, failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', contains_check=True,
             before_message='''Kontrollib, kas programmis esineb try/except plokk.''',
             passed_message='''Programmis ei esine try/except plokki.''',
             failed_message='''Programmis esines try/except plokk.''', type='''program_contains_try_except_test''',
             points=1.0, id=None, name='''Programmis ei tohi olla try/except plokki.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', contains_check=False,
             before_message='''Kontrollib, kas programm kutsub välja 'print' käsu.''',
             passed_message='''Programm kutsus välja 'print' käsu.''',
             failed_message='''Programm ei kutsunud välja 'print' käsku.''', type='''program_calls_print_test''',
             points=1.0, id=None, name='''Programm peab välja kutsuma 'print' käsu.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', generic_checks=[
    GenericChecks(check_type='''ANY_OF_THESE''', nothing_else=None,
                  expected_value=['''down''', '''up''', '''seosta_lapsed_ja_vanemad'''],
                  before_message='''Kontrollib, kas programm defineerib vähemalt ühe antud funktsioonidest.''',
                  passed_message='''Programm defineeris vähemalt ühe antud funktsioonidest.''',
                  failed_message='''Programm ei defineerinud välja ühtegi antud funktsioonidest.''')],
             type='''program_defines_function_test''', points=1.0, id=None,
             name='''Programm defineerib vähemalt ühe antud funktsioonidest.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', generic_checks=[
    GenericChecks(check_type='''ANY_OF_THESE''', nothing_else=None,
                  expected_value=['''seosta_lapsed_ja_vanemad''', '''yes''', '''no'''], consider_elements_order=False,
                  before_message='''Kontrollib, kas programm sisaldab võtmesõna.''',
                  passed_message='''Programm sisaldab võtmesõna.''',
                  failed_message='''Programm ei sisalda võtmesõna.''')], type='''program_contains_keyword_test''',
             points=1.0, id=None, name='''Programm sisaldab võtmesõna.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', contains_check=False,
             before_message='''Kontrollib, kas funktsioonis esineb tsükkel.''',
             passed_message='''Funktsioonis esines tsükkel.''',
             failed_message='''Funktsioonis ei esine ühtegi tsüklit.''', type='''function_contains_loop_test''',
             points=1.0, id=None, name='''Funktsioonis esineb tsükkel.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', generic_checks=[
    GenericChecks(check_type='''ANY_OF_THESE''', nothing_else=None, expected_value=['''ff.close()''', '''no'''],
                  consider_elements_order=False, before_message='''Kontrollib, kas funktsioon sisaldab võtmesõna.''',
                  passed_message='''Funktsioon sisaldab võtmesõna.''',
                  failed_message='''Funktsioon ei sisalda võtmesõna.''')], type='''function_contains_keyword_test''',
             points=1.0, id=None, name='''Funktsioon sisaldab võtmesõna.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', contains_check=False,
             before_message='''Kontrollib, kas funktsioonis esineb return.''',
             passed_message='''Funktsioonis esines return.''',
             failed_message='''Funktsioonis ei esine ühtegi return'i.''', type='''function_contains_return_test''',
             points=1.0, id=None, name='''Funktsioonis esineb return.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', generic_checks=[
    GenericChecks(check_type='''ANY_OF_THESE''', nothing_else=None,
                  expected_value=['''down''', '''up''', '''forward''', '''left''', '''right''', '''fd''', '''rt''',
                                  '''lt''', '''bk''', '''goto'''],
                  before_message='''Kontrollib, kas funktsioon kutsub välja turtle funktsiooni.''',
                  passed_message='''Funktsioon kutsus välja vähemalt ühe turtle funktsiooni.''',
                  failed_message='''Funktsioon ei kutsnud välja ühtegi turtle funktsiooni.''')],
             type='''function_calls_function_test''', points=1.0, id=None,
             name='''Funktsioon kutsub välja turtle funktsiooni.''', inputs=None, passed_next=None, failed_next=None,
             visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', contains_check=False,
             before_message='''Kontrollib, kas funktsioon kutsub välja print käsu.''',
             passed_message='''Funktsioon kutsub välja print käsu.''',
             failed_message='''Funktsioon ei kutsu välja print käsku.''', type='''function_calls_print_test''',
             points=1.0, id=None, name='''Funktsioon kutsub välja print käsu.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', contains_check=False,
             before_message='''Kontrollib, kas funktsioon on rekursiivne.''',
             passed_message='''Funktsioonis on rekursiivne.''', failed_message='''Funktsioonis ei ole rekursiivne.''',
             type='''function_is_recursive_test''', points=1.0, id=None, name='''Funktsioonis on rekursiivne.''',
             inputs=None, passed_next=None, failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', generic_checks=[
    GenericChecks(check_type='''ANY_OF_THESE''', nothing_else=None,
                  expected_value=['''down''', '''up''', '''seosta_lapsed_ja_vanemad2'''],
                  before_message='''Kontrollib, kas funktsioon defineerib vähemalt ühe antud funktsioonidest.''',
                  passed_message='''Funktsioon defineeris vähemalt ühe antud funktsioonidest.''',
                  failed_message='''Funktsioon ei defineerinud ühtegi antud funktsioonidest.''')],
             type='''function_defines_function_test''', points=1.0, id=None,
             name='''Funktsioon defineerib vähemalt ühe antud funktsioonidest.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', generic_checks=[
    GenericChecks(check_type='''ALL_OF_THESE''', nothing_else=None, expected_value=['''turtle'''],
                  before_message='''Kontrollib, kas funktsioon impordib mooduli.''',
                  passed_message='''Funktsioon importis mooduli.''',
                  failed_message='''Funktsioon ei importinud moodulit.''')], type='''function_imports_module_test''',
             points=1.0, id=None, name='''Funktsioon importib mooduli turtle.''', inputs=None, passed_next=None,
             failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', contains_check=True,
             before_message='''Kontrollib, kas funktsioonis esineb try/except plokk.''',
             passed_message='''Funktsioonis ei esine try/except plokki.''',
             failed_message='''Funktsioonis esines try/except plokk.''', type='''function_contains_try_except_test''',
             points=1.0, id=None, name='''Funktsioonis ei tohi olla try/except plokki.''', inputs=None,
             passed_next=None, failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''', contains_check=False,
             before_message='''Kontrollib, kas funktsioon kasutab ainult lokaalseid muutujaid.''',
             passed_message='''Funktsioon kasutab ainult lokaalseid muutujaid.''',
             failed_message='''Funktsioon ei kasuta ainult lokaalseid muutujaid.''', type='''function_is_pure_test''',
             points=1.0, id=None, name='''Funktsioon kasutab ainult lokaalseid muutujaid.''', inputs=None,
             passed_next=None, failed_next=None, visible_to_user=None)
execute_test(file_name='''submission.py''', function_name='''seosta_lapsed_ja_vanemad''',
             arguments=['''lapsed.txt''', '''nimed.txt'''], standard_input_data=['''Kasutajasisend'''],
             input_files=[('''sisendfail.txt''', '''Sisendfaili sisu.''')], return_value='''3''', generic_checks=[
        GenericChecks(check_type='''ANY_OF_THESE''', nothing_else=None, expected_value=['''down''', '''up'''],
                      consider_elements_order=False,
                      before_message='''Kontrollib, kas funktsiooni väljund sisaldab võtmesõna.''',
                      passed_message='''Funktsiooni väljund sisaldab antud võtmesõna.''',
                      failed_message='''Funktsiooni väljund ei sisalda antud võtmesõna.''')], output_file_checks=[
        OutputFileChecks(file_name='''valjundfail.txt''', check_type='''ALL_OF_THESE''', nothing_else=None,
                         expected_value=['''Väljundfaili eeldatav sisu'''], consider_elements_order=True,
                         before_message='''Kontrollib, kas funktsiooni väljundfail sisaldab võtmesõna.''',
                         passed_message='''Funktsiooni väljundfail sisaldab antud võtmesõna.''',
                         failed_message='''Funktsiooni väljundfail ei sisalda antud võtmesõna.''')],
             type='''function_execution_test''', points=1.0, id=None, name='''Funktsiooni käivituse test.''',
             inputs=None, passed_next=None, failed_next=None, visible_to_user=None)
print(json.dumps(Results(None).format_result(), cls=ComplexEncoder, ensure_ascii=False))
