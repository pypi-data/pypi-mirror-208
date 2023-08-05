import re

from datetime import datetime
from voluptuous import (
    Invalid,
)
from .helpers import (
    date_format,
    time_format,
    datetime_format,
)

time_pattern = 'HH:MM'
date_pattern = 'YYYY-MM-DD'
datetime_pattern = 'YYYY-MM-DD HH:MM:SS'

def ValidString():
    def f(str_data):
        str_data = __string_valid(str_data)
        return str_data
    return f

def ValidInt():
    def f(int_data):
        __int_valid(int_data)
        return int_data
    return f

def ValidAmount():
    def f(float_data):
        __amount_valid(float_data)
        return float_data
    return f

def ValidBoolean():
    def f(bool_data):
        __boolean_valid(bool_data)
        return bool_data
    return f

def ValidDate():
    """
    Custom validator to validate the time range date format.
    """

    def f(date_text):
        date_text = __date_valid(date_text)
        return date_text
    return f

def ValidDateTime():
    """
    Custom validator to validate the time range date format.
    """

    def f(datetime_text):
        datetime_text = __datetime_valid(datetime_text)
        return datetime_text
    return f

def ValidTime(msg=None):
    def f(time_text):
        time_text = __time_valid(time_text)
        return time_text
    return f

def ValidEmail(msg=None):
    """
    Custom validator to validate the email address.
    """
    def f(email):
        email = __email_valid(email)
        return str(email)
    return f

def AllowedPassword():
    """
    Custom validator to validate the password.
    """
    def f(password):
        password = __password_valid(password)
        return str(password)
    return f

def OnlyDigits(msg=None):
    def f(text):
        text = __string_of_integers_valid(text)
        return text
    return f


# The below functions are reused by the base function,
# inorder to follow the DRY principle.
# All the below methods are private, to avoid importing outside this module.
def __boolean_valid(bool_data, msg=None):
    if type(bool_data) != bool:
        raise Invalid(msg or 'Please enter a valid boolean value')

def __int_valid(int_data, msg=None):
    if type(int_data) != int:
        raise Invalid(msg or'Please enter a valid number')

def __amount_valid(int_or_float_data, msg=None):
    if type(int_or_float_data) not in (float, int):
        raise Invalid(msg or 'Please enter a valid value')
        
def __string_valid(str_data, msg=None):
    if type(str_data) != str:
        raise Invalid(msg or 'Please enter a valid string')
    return str_data.strip()

def __date_valid(str_data, msg=None):
    str_data = __string_valid(str_data, msg)
    try:
        datetime.strptime(str_data, date_format)
    except ValueError:
        raise Invalid(msg or f'Date should be of the format {date_pattern}')
    return str_data

def __time_valid(str_data, msg=None):
    str_data = __string_valid(str_data, msg)
    try:
        datetime.strptime(str_data, time_format)
    except ValueError:
        raise Invalid(msg or f'Time should be of the format {time_pattern}')
    return str_data

def __datetime_valid(str_data, msg=None):
    str_data = __string_valid(str_data, msg)
    try:
        datetime.strptime(str_data, datetime_format)
    except ValueError:
        raise Invalid(msg or f'DateTime should be of the format {datetime_pattern}')
    return str_data

def __email_valid(str_data, msg=None):
    str_data = __string_valid(str_data, msg)
    if not re.match("[\w\.\-]*@[\w\.\-]*\.\w+", str_data):
        raise Invalid(msg or ('Please enter a valid Email ID'))
    return str_data

def __password_valid(str_data, msg=None):
    str_data = __string_valid(str_data, msg)
    reg_exp = r'[a-zA-Z0-9~` !@#$%^&*()-_=+{}[]:;"\'<,>.?/|\]*'
    if not re.match(reg_exp, str_data):
        raise Invalid(msg or 'Invalid character(s) in password')
    return str_data

def __string_of_integers_valid(str_data, msg=None):
    str_data = __string_valid(str_data, msg)
    if not str_data.isdigit():
        raise Invalid(msg or 'Only digits are allowed')
    return str_data

# #TODO: Improve
# def ValidPhoneNumberDeprecated(msg=None):
#     """
#     References:
#         - https://en.wikipedia.org/wiki/Telephone_numbering_plan
#         - https://stackoverflow.com/questions/14894899/what-is-the-minimum-length-of-a-valid-international-phone-number
#         - https://stackoverflow.com/questions/3350500/international-phone-number-max-and-min
#     """

#     def f(phone):
#         # if not phone.isdigit():
#         #     raise Invalid(msg or 'Il numero di telefono dovrebbe contenere solo cifre')

#         if len(phone) < 5:
#             raise Invalid(msg or 'Invalid phone number.')

#         if len(phone) > 12:
#             raise Invalid(msg or 'Invalid phone number.')

#         return phone
#     return f


# #TODO: Improve
# def ValidPhoneNumber(msg=None):
#     """
#     This uses the python port of Google's libphonenumber library to validate
#     the phone numbers.

#     Currently, the application allows only indian users to register in the
#     application.
#     """

#     def f(mobile):
#         # if not mobile.startswith('+'):
#         #     mobile = '+91' + mobile
#         # try:
#         #     phonenumber = phonenumbers.parse(mobile, None)

#         #     # Check, if the given number is a valid indian number
#         #     # if phonenumber.country_code != 91:
#         #     #     raise Invalid(
#         #     #         'Currently the registration is not open to users outside '
#         #     #         'India.'
#         #     #     )
#         # except phonenumbers.phonenumberutil.NumberParseException:
#         #     raise Invalid('Not a valid mobile number')

#         return mobile

#     return f


# #TODO: Improve
# def ValidUsername(msg=None):
#     def f(username):
#         # Should start with an alphabet, can end with a digit or an alphabet and can
#         # contain a dot.
#         if not re.match("^[a-zA-Z]+[a-zA-z0-9]*[\.]?[a-zA-Z0-9]+$", str(username)):
#             raise Invalid(
#                 msg or ('Il nome utente dovrebbe iniziare con un alfabeto, può finire'
#                 'con un alfabeto o una cifra e può contenere un punto')
#             )

#         if len(str(username)) > 20:
#             raise Invalid(msg or ('Il nome utente non può contenere più di 20 caratteri'))

#         if len(str(username)) < 4:
#             raise Invalid(msg or ('Il nome utente non può essere inferiore a 4 caratteri'))

#         return str(username)
#     return f


# def ValidWebURL(msg=None):
#     """
#     This is a custom validator for validating a website URL.
#     """

#     def f(url):
#         if not re.match('^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$', str(url)):  # Breaking into multilines doesn't validate properly
#             raise Invalid(msg or 'Use a valid URL')

#         return str(url)
#     return f

# def NonEmptyDict(msg='Cannot be empty'):
#     def f(d):
#         if len(d.keys()) == 0:
#             raise Invalid(msg)
#         return d
#     return f


# def ValidName(msg=None):
#     def f(name):
#         if len(str(name)) > 40 or len(str(name)) < 2:
#             raise Invalid(msg or 'Name should be between 2 and 40 characters')

#         return str(name)
#     return f

