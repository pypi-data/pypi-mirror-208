# Import Libs
import json
import os
import re
import sys

import tpy.tpy

try:
    from colorama import Fore, init
    init(autoreset=True)
except ModuleNotFoundError:
    sys.exit('Module not found: colorama')

# Defualt Vars
#  It's just the defualt configuration dict, Consider reading https://github.com/Techlord210/TPython/blob/main/config.jsonc instead.
config = {'version': '1.1', 'config': {'notify_updates': True, 'welcome_msg': True, 'exit_msg': True, 'crash_msg': True}, 'colors': {'update': {'text_color': Fore.LIGHTCYAN_EX, 'version_color': Fore.LIGHTGREEN_EX}, 'welcome': {'text_color': Fore.LIGHTCYAN_EX, 'padding_color': Fore.LIGHTCYAN_EX}, 'exit': {'success': {'text_color': Fore.LIGHTCYAN_EX, 'padding_color': Fore.LIGHTCYAN_EX}, 'crash': {'text_color': Fore.LIGHTYELLOW_EX, 'padding_color': Fore.LIGHTYELLOW_EX}}, 'promot': {'default': {'sq_brackets': Fore.LIGHTGREEN_EX, 'number': {'normal': Fore.LIGHTWHITE_EX, 'error': Fore.LIGHTRED_EX}, 'dash': Fore.LIGHTGREEN_EX,'arrow': Fore.LIGHTCYAN_EX, 'indent': {'number_replace': Fore.LIGHTYELLOW_EX, 'sq_brackets': Fore.LIGHTGREEN_EX, 'dash': Fore.LIGHTGREEN_EX, 'arrow': Fore.LIGHTYELLOW_EX}}, 'timeit': {'sq_brackets': Fore.LIGHTGREEN_EX, 'text_color': Fore.LIGHTWHITE_EX, 'dash': Fore.LIGHTGREEN_EX, 'arrow': Fore.LIGHTWHITE_EX, 'time_text': {'text_color': Fore.LIGHTGREEN_EX, 'time_color': Fore.LIGHTYELLOW_EX}, 'indent': {'number_replace': Fore.LIGHTWHITE_EX, 'sq_brackets': Fore.LIGHTGREEN_EX, 'dash': Fore.LIGHTGREEN_EX, 'arrow': Fore.LIGHTWHITE_EX}}}}}
CONFIG_PATH: str = os.path.abspath(os.path.expanduser('~/.TPython/config.jsonc'))
READER_VERSION: str = '1.1'
READ_FILE: bool = False

# Decoder Error
class JSONCDecodeError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

# Parser
def parse_file(file: str) -> dict:
    try:
        # Read the contents of the file into a string
        with open(file, 'r') as f:
            content = f.read()

        # Remove the comments from the string
        json_str = re.sub(r'(\/\/[^\n]*)|(/\*[\s\S]*?\*/)', '', content)

        # Check for broken comments
        tmp_str = re.sub(r'"([^"]*)"', '', json_str)

        if '*/' in tmp_str:
            raise JSONCDecodeError("expected '/*' before '*/'")
        elif '/*' in tmp_str:
            raise JSONCDecodeError("expected '*/' after '/*'")
        elif '/' in tmp_str:
            raise JSONCDecodeError("expected '//' got '/'")
        
        return json.loads(json_str)

    except Exception:
        tpy.tpy.exc()
        return {}

if os.path.isfile(CONFIG_PATH):
    try:
        config = parse_file(CONFIG_PATH)
        READ_FILE = True
    except:
        tpy.tpy.exc()

if config['version'] == READER_VERSION:
    if READ_FILE:
        COLORS = {
            "cyan": Fore.LIGHTCYAN_EX,
            "green": Fore.LIGHTGREEN_EX,
            "red": Fore.LIGHTRED_EX,
            "yellow": Fore.LIGHTYELLOW_EX,
            "white": Fore.LIGHTWHITE_EX,
            "blue": Fore.LIGHTBLUE_EX,
            "black": Fore.LIGHTBLACK_EX,
            "magenta": Fore.LIGHTMAGENTA_EX
        }

        def color_to_code(config: dict) -> dict:
            for key, val in config.items():
                if type(val) == dict:
                    color_to_code(config[key])
                else:
                    config[key] = COLORS.get(val, Fore.WHITE)
            return config
        color_to_code(config['colors'])
else:
    sys.exit(f"{Fore.LIGHTRED_EX}config file version '{Fore.LIGHTYELLOW_EX}{config['version']}{Fore.LIGHTRED_EX}' don't match with reader '{Fore.LIGHTYELLOW_EX}{READER_VERSION}{Fore.LIGHTRED_EX}'")

INP_COLORS = config['colors']['promot']['default']
INP_COLORS_INDENT = config['colors']['promot']['default']['indent']
TNP_COLORS = config['colors']['promot']['timeit']
TNP_COLORS_INDENT = config['colors']['promot']['timeit']['indent']