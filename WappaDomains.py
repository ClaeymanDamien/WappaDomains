import os

class WappaDomains:

    def __init__(self, domains, output=None):
        self.__domains = domains
        self.__output = f'{output}/{domains}_wappa.json' if output else f'{domains}_wappa.json'


    # def __exec_wappalyzer(self, domain):
        # os.system()