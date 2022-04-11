import os
import re
import csv
import sys
import json

class WappaDomains:

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    WAPPALYZER_PATH = '/source/wappalyzer'

    def __init__(self, domains, output=None):
        self.__domains = domains
        self.__output = output if output else f'{domains}_wappa.csv'

    def __exec_wappalyzer(self, domain):
        try:
            request = os.popen(f'node {self.PROJECT_ROOT + self.WAPPALYZER_PATH}/src/drivers/npm/cli.js {domain}').read()

            return request if not '":{"status":0' in request else None

        except Exception as e:
            print(f'Wappalyzer error: {e}')
            return None

    @staticmethod
    def __convert_string_to_json(string_input):
        try:
            return json.loads(string_input)
        except ValueError as e:
            print(f'JSON conversion error: {e}')
            return None

    @staticmethod
    def __get_technologies(wappa_result):
        technologies = wappa_result['technologies']

        result = {"technologies":[]}

        for technology in technologies:
            category = ""

            for i, categories in enumerate(technology['categories']):
                if i == len(technology['categories'])-1:
                    category += f'{categories["name"]}'
                else:
                    category += f'{categories["name"]} - '

            result['technologies'].append({"name": technology['name'], "version": technology['version'],
                                           "confidence": technology['confidence'], "categories": category})

        return result

    @staticmethod
    def convert_url_domain(url):
        return re.sub(r'https?://', '', url)

    @staticmethod
    def __save_csv(row, output):
        try:
            f = open(output, 'a')
            writer = csv.writer(f)
            writer.writerow(row)
            f.close()
        except IOError:
            print(f'Impossible to save data')

    def __load_domains(self):
        domains = []
        try:
            with open(self.__domains) as input_domains:
                for domain in input_domains:
                    domains.append(domain.strip())

            return domains

        except IOError as e:
            print(f'Impossible to load domains: {e}')
            exit(0)

    @staticmethod
    def check_valid_input(url):
        regex = re.compile(r'((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}')
        return re.match(regex, url) is not None

    def exec(self):

        domains = self.__load_domains()
        domains_len = len(domains)
        header = ['Domain', 'Technology', 'Version', 'Categories', 'Confidence']

        self.__save_csv(header, self.__output)

        for i, domain in enumerate(domains):

            print(f'\r{domain}')
            sys.stdout.write(f'\r{i + 1}/{domains_len}')
            sys.stdout.flush()

            if self.check_valid_input(domain):
                wappa_result = self.__exec_wappalyzer(domain)

                if wappa_result:
                    wappa_json = self.__convert_string_to_json(wappa_result)

                    if wappa_json:
                        technologies = self.__get_technologies(wappa_json)

                        for technology in technologies['technologies']:
                            row = [self.convert_url_domain(domain), technology['name'], technology['version'], technology['categories'],
                                   technology['confidence']]
                            self.__save_csv(row, self.__output)
                else:
                    print('\rPrint error with Wappalyzer')
            else:
                print(f"\r|\r\n--> Invalid format")


