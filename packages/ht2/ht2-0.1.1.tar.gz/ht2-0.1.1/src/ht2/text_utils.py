import re

def add_trailing_space_to_punctuaions(string):
    """for a normal english sentence, check missing 
trailing spaces after punchations, add if missing

    :param string: input sentence
    :type string: str
    """
    string = re.sub('([.,!?()])', r'\1 ', string)
    string = re.sub('\s{2,}', ' ', string)
    return string


def is_chinese_char(char):
    """
    check if a unicode char is a chinese char
    """
    return char >= u'\u4e00' and char <= u'\u9fff'

def string_has_chinese(string):
    """
    check if a unicode char is a chinese char
    """
    for char in string:
        if is_chinese_char(char):
            return True
    return False