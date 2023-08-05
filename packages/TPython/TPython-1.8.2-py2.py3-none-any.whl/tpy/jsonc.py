# Import Libs
import json
import re
from typing import List

# Decoder Error
class JSONCDecodeError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

# Parser
def parse_file(file: str) -> dict:
    # Read the contents of the file into a string
    with open(file, 'r') as f:
        content:str = f.read()

    # Remove the comments from the string
    json_str: str = re.sub(r'(\/\/[^\n]*)|(/\*[\s\S]*?\*/)', '', content)

    # Check for broken comments
    tmp_list: List[str] = re.sub(r'"([^"]*)"', '', json_str).splitlines()

    for line_no, element in enumerate(tmp_list, 1):
        if '*/' in element:
            raise JSONCDecodeError(f"expected '/*' before '*/', line {line_no}")
        elif '/*' in element:
            raise JSONCDecodeError(f"expected '*/' after '/*', line {line_no}")
    
    return json.loads(json_str)
