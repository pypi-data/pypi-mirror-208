from tiivad.tests import TestResult
from tiivad.version import __version__ as version


def calculate_test_status(checks):
    for check_result in checks:
        if check_result.check_status == TestResult.FAIL.name:
            return TestResult.FAIL.name
    return TestResult.PASS.name


def format_checks(checks):
    result = []
    for check_result in checks:
        check = {}
        check["title"] = check_result.before_message
        check["status"] = check_result.check_status
        check["feedback"] = check_result.passed_message if check_result.check_status == TestResult.PASS.name \
            else check_result.failed_message
        result.append(check)

    return result


class Results(object):
    __instance = None
    tests = []
    pre_evaluate_error = None
    result_type = "OK_V3"
    points = None
    error = None

    def __new__(cls, val):
        if Results.__instance is None:
            Results.__instance = object.__new__(cls)
        if val is not None:
            Results.__instance.tests.append(val)
        return Results.__instance

    def clear(cls):
        cls.__instance = None

    def calculate_points(self) -> int:
        failed_points = 0
        passed_points = 0
        for test_result in self.tests:
            if test_result.get("test_status", TestResult.FAIL.name) == TestResult.PASS.name:
                passed_points += test_result.get("points_weight", 0)
            else:
                failed_points = test_result.get("points_weight", 0)
        if int(failed_points + passed_points) == 0:
            return 0
        return int(passed_points / (failed_points + passed_points) * 100)

    def format_tests(self):
        tests = []
        for test_result in self.tests:
            result = {}
            result["title"] = test_result.get("name", "")
            result["status"] = calculate_test_status(test_result.get("checks", []))
            result["exception_message"] = test_result.get("exception_message", None)
            result["user_inputs"] = test_result.get("standard_input_data", [])
            result["created_files"] = [{"name": x[0], "content": x[1]} for x in test_result.get("input_files", [])]
            result["actual_output"] = test_result.get("actual_output", None)
            result["checks"] = format_checks(test_result.get("checks", []))

            if result["status"] != TestResult.PASS.name and test_result.get("converted_script", None) is not None:
                result["converted_submission"] = test_result.get("converted_script")
            tests.append(result)
        return tests

    @staticmethod
    def get_producer():
        return f"tiivad v{version}"

    def format_result(self):

        if self.pre_evaluate_error is not None:
            self.tests = []

        if self.error is not None:
            return self.error

        self.points = self.calculate_points()
        test_results = self.format_tests()

        result = {}
        result["result_type"] = self.result_type
        result["producer"] = self.get_producer()
        result["points"] = self.points
        result["pre_evaluate_error"] = self.pre_evaluate_error
        result["tests"] = test_results

        return result


if __name__ == '__main__':
    print(Results({"a", "b"}).tests)
    print(Results(None).tests)
    print(Results({"a", "b"}).tests)
    print(Results(None).tests)
    print(Results({"a", "b"}).tests)
    print(Results(None).tests)
    print(Results({"a", "b"}).tests)
    print(Results(None).tests)
