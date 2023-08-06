import platform


def is_win_system():
    """判断系统是否为Windows系统"""
    return platform.system() == "Windows"


def is_linux_system():
    """判断系统是否为Linux系统"""
    return platform.system() == "Linux"
