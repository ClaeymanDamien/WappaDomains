import os
import re
import csv
import sys
import json
import time


class WappaDomains:

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    WAPPALYZER_PATH = '/source/wappalyzer'
    OUTPUT_TYPE_1 = 'csv'
    OUTPUT_TYPE_2 = 'txt'
    OUTPUT_TYPE_3 = 'small_csv'
    ERROR_FILE_LOG = 'error_unexpected.logs'

    def __init__(self, domains, output=None, output_type=None):
        self.__domains = domains
        self.__output = output if output else f'{domains}_wappa.csv'
        self.__output_type = output_type if output_type else f'csv'

    def __exec_wappalyzer(self, domain):
        try:
            request = os.popen(f'node {self.PROJECT_ROOT + self.WAPPALYZER_PATH}/src/drivers/npm/cli.js {domain}').read()

            return request if not '":{"status":0' in request else None

        except Exception as e:
            self.__log(f'{domain} -> Wappalyzer error: {e}', True)
            return None

    def __convert_string_to_json(self, string_input):
        try:
            return json.loads(string_input)
        except ValueError as e:
            self.__log(f'JSON conversion error: {e}', True)
            return None

    @staticmethod
    def __get_technologies(wappa_result):
        technologies = wappa_result['technologies']

        result = {"technologies":[]}

        for technology in technologies:
            category = ""

            categories_len = len(technology['categories'])

            for i, categories in enumerate(technology['categories']):
                if i == categories_len-1:
                    category += f'{categories["name"]}'
                else:
                    category += f'{categories["name"]} - '

            result['technologies'].append({"name": technology['name'], "version": technology['version'],
                                           "confidence": technology['confidence'], "categories": category})

        return result

    @staticmethod
    def convert_url_domain(url):
        return re.sub(r'https?://', '', url)

    def __save_csv(self, row, output):
        try:
            f = open(output, 'a')
            writer = csv.writer(f)
            writer.writerow(row)
            f.close()
        except IOError:
            self.__log(f'{output} -> Impossible to save data', True)

    def __save_txt(self, row, output):
        try:
            f = open(output, 'a')
            f.write(row + '\n')
            f.close()
        except IOError:
            self.__log(f'{output} -> Impossible to save data', True)

    def __save_file(self, domain, technologies, error=False):
        if self.__output_type == self.OUTPUT_TYPE_2:
            if not error:
                row = f''
                row += f'{domain} => '

                last_techno = len(technologies) -1

                for i, technology in enumerate(technologies):
                    row += f'{technology["name"]} {technology["version"] if technology["version"] else ""} - ' \
                           f'{technology["categories"]} - {technology["confidence"]}{"" if last_techno == i else ", "}'

                self.__save_txt(row, self.__output)
            else:
                self.__save_txt(f'{domain} => ', self.__output)

        elif self.__output_type == self.OUTPUT_TYPE_3:
            if not error:
                techno_formatted_list = list()
                for technology in technologies:
                    row = ''
                    row += f'{technology["name"]}{" " + technology["version"] if technology["version"] else ""} - ' \
                           f'{technology["categories"]} - {technology["confidence"]}'
                    techno_formatted_list.append(f'{row}')
                self.__save_csv([self.convert_url_domain(domain), '\n'.join(techno_formatted_list)], self.__output)
            else:
                self.__save_csv([self.convert_url_domain(domain), ''], self.__output)

        else:
            if not error:
                for technology in technologies:
                    row = [self.convert_url_domain(domain), technology['name'], technology['version'],
                           technology['categories'], technology['confidence']]
                    self.__save_csv(row, self.__output)
            else:
                row = [self.convert_url_domain(domain), '', '', '', '']
                self.__save_csv(row, self.__output)

    def __log(self, string, write=False):
        if write:
            self.__save_txt(f'{time.strftime("%Y-%m-%d %H:%M:%S.%s")}: {string}\n', self.ERROR_FILE_LOG )
        else:
            print(f'\r{time.strftime("%Y-%m-%d %H:%M:%S.%s")}: {string}')

    def __load_domains(self):
        domains = []
        try:
            with open(self.__domains) as input_domains:
                for domain in input_domains:
                    domains.append(domain.strip())

            return domains

        except IOError as e:
            self.__log(f'{self.__domains} -> Impossible to load domains: {e}', True)
            exit(0)

    @staticmethod
    def check_valid_input(url):
        regex = re.compile(r'((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}')
        return re.match(regex, url) is not None


    def exec(self):

        domains = self.__load_domains()
        domains_len = len(domains)

        if self.__output_type == self.OUTPUT_TYPE_1:
            header = ['Domain', 'Technology', 'Version', 'Categories', 'Confidence']
            self.__save_csv(header, self.__output)
        elif self.__output_type == self.OUTPUT_TYPE_3:
            header = ['Domain', 'Technology']
            self.__save_csv(header, self.__output)

        for i, domain in enumerate(domains):

            error = False

            print(f'\r{domain}')
            sys.stdout.write(f'\r{i + 1}/{domains_len}')
            sys.stdout.flush()

            if self.check_valid_input(domain):
                wappa_result = self.__exec_wappalyzer(domain)

                if wappa_result:
                    wappa_json = self.__convert_string_to_json(wappa_result)

                    if wappa_json:
                        technologies = self.__get_technologies(wappa_json)

                        if len(technologies['technologies']):
                            self.__save_file(domain, technologies['technologies'])
                        else:
                            self.__log(f'No technologies detected')
                            error = True
                    else:
                        self.__log(f'{domain} -> JSON format invalid', True)
                        error = True
                else:
                    self.__log(f'{domain} -> Error with Wappalyzer', True)
                    error = True
            else:
                self.__log(f'{domain} -> Domain format invalid', True)
                error = True

            if error:
                self.__save_file(domain, None, error)
