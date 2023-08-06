import enum


class Language(enum.Enum):
    CHINESE = "中文"
    ENGLISH = "英文"


current_language = Language.CHINESE


def set_lan(lan: Language):
    global current_language
    current_language = lan


def get_lan():
    return current_language
