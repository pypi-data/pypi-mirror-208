def format_error(error_message, mapping_dict):
    for k, v in mapping_dict.items():
        a = {k: "{" + str(v) + "}"}
        try:
            error_message = error_message.format(**a)
        except:
            pass
    return error_message
