from flask import current_app


@current_app.template_filter()
def format_number(num):
    if int(num) == num:
        return int(num)
    return num
