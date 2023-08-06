class Check:
    before_message = ""
    passed_message = ""
    failed_message = ""
    check_status = ""
    error_message = ""


class GenericChecks:
    def __init__(self, check_type, nothing_else, expected_value, before_message, passed_message, failed_message,
                 is_numeric, consider_elements_order=None, ):
        self.check_type = check_type
        self.nothing_else = nothing_else
        self.expected_value = expected_value
        self.before_message = before_message
        self.passed_message = passed_message
        self.failed_message = failed_message
        self.check_status = None
        self.error_message = None
        self.is_numeric = is_numeric
        self.consider_elements_order = consider_elements_order

    def __str__(self):
        return {
            "check_type": self.check_type,
            "nothing_else": self.nothing_else,
            "expected_value": self.expected_value,
            "before_message": self.before_message,
            "passed_message": self.passed_message,
            "failed_message": self.failed_message,
            "check_status": self.check_status,
            "error_message": self.error_message,
            "is_numeric": self.is_numeric,
            "consider_elements_order": self.consider_elements_order
        }

    def __repr__(self):
        return {
            "check_type": self.check_type,
            "nothing_else": self.nothing_else,
            "expected_value": self.expected_value,
            "before_message": self.before_message,
            "passed_message": self.passed_message,
            "failed_message": self.failed_message,
            "check_status": self.check_status,
            "error_message": self.error_message,
            "is_numeric": self.is_numeric,
            "consider_elements_order": self.consider_elements_order
        }.__str__()

    def repr_json(self):
        return {
            "check_type": self.check_type,
            "nothing_else": self.nothing_else,
            "expected_value": self.expected_value,
            "before_message": self.before_message,
            "passed_message": self.passed_message,
            "failed_message": self.failed_message,
            "check_status": self.check_status,
            "error_message": self.error_message,
            "is_numeric": self.is_numeric,
            "consider_elements_order": self.consider_elements_order
        }


class OutputFileChecks:
    def __init__(self, file_name, check_type, nothing_else, expected_value, before_message, passed_message,
                 failed_message, consider_elements_order=None):
        self.file_name = file_name
        self.check_type = check_type
        self.nothing_else = nothing_else
        self.expected_value = expected_value
        self.before_message = before_message
        self.passed_message = passed_message
        self.failed_message = failed_message
        self.check_status = None
        self.error_message = None
        self.consider_elements_order = consider_elements_order

    def __str__(self):
        return {
            "file_name": self.file_name,
            "check_type": self.check_type,
            "nothing_else": self.nothing_else,
            "expected_value": self.expected_value,
            "before_message": self.before_message,
            "passed_message": self.passed_message,
            "failed_message": self.failed_message,
            "check_status": self.check_status,
            "error_message": self.error_message,
            "consider_elements_order": self.consider_elements_order
        }

    def __repr__(self):
        return {
            "file_name": self.file_name,
            "check_type": self.check_type,
            "nothing_else": self.nothing_else,
            "expected_value": self.expected_value,
            "before_message": self.before_message,
            "passed_message": self.passed_message,
            "failed_message": self.failed_message,
            "check_status": self.check_status,
            "error_message": self.error_message,
            "consider_elements_order": self.consider_elements_order
        }.__str__()
