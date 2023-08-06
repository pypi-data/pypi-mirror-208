import sys


def get_modules_availables():
    return sys.path + "\n" + help("modules")
