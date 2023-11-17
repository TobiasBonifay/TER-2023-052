from colorama import Fore, Style


class Log:

    def __init__(self):
        pass

    def debug(self, arg):
        print(Style.BRIGHT + Fore.WHITE + "[DEBUG] - {}".format(arg))

    def output(self, arg):
        print(Style.BRIGHT + Fore.BLUE + "[OUTPUT] - {}".format(arg))
