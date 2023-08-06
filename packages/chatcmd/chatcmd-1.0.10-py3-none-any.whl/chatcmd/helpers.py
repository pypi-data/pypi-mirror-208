import re
import inspect

RESET = '\033[0m'

def library_info():
    print(
    "----------------------------------------------------------------\n"
    "  \033[32mLibrary Name:\033[0m \033[33mChatCMD\033[0m\n"
    "  \033[32mLibrary Source [PyPi]:\033[0m https://pypi.org/naifalshaye/chatcmd\n"
    "  \033[32mLibrary Source [Github]:\033[0m https://github.com/naifalshaye/chatcmd\n"
    "  \033[32mDocumentation:\033[0m https://github.com/naifalshaye/chatcmd#readme\n"
    "  \033[32mBug Tracker:\033[0m https://github.com/naifalshaye/chatcmd/issues\n"
    "  \033[32mPublished Date:\033[0m 2023-05-15\n"
    "  \033[32mLicense:\033[0m MIT\n"
    "  \033[32mAuthor:\033[0m Naif Alshaye\n"
    "  \033[32mAuthor Email:\033[0m naif@naif.io\n"
    "  \033[32mAuthor Website:\033[0m https://naif.io\n"
    "----------------------------------------------------------------"
    )

def color_text(text, color):
    colors = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[97m',
        'black': "\033[0;30m",
        'light_gray': "\033[37m",
        'dark_gray': "\033[1;30m",
        'light_white': "\033[37m",
        'bold': "\033[1m",
        'italic': "\033[3m",
        'underline': "\033[4m",
        'end': "\033[0m",
    }
    return f"{colors[color]}{text}{RESET}"

def success_msg(text):
    print("\n"+color_text(text, 'green'))

def error_msg(text):
    print("\n"+color_text(text, 'red'))
    exit()
#     print("\n"+color_text(text.split('.')[0], 'red'))
#     exit()

def warning_msg(text):
    print("\n"+color_text(text, 'yellow'))

def clear_input(input):
    input = re.sub('[^a-zA-Z0-9 -_=]', '', input.strip())
    return input

def validateInput(prompt):
    if len(prompt.split()) <= 2:
        return False
    return True

def validate_api_key(api_key):
    if api_key[0:3] != 'sk-':
        return False
    if len(api_key) != 51:
        return False
    if not re.match("^[a-zA-Z0-9-]+$", api_key):
        return False
    return True

def get_line_number():
    frame = inspect.currentframe().f_back
    return frame.f_lineno