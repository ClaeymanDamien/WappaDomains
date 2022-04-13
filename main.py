import argparse
from WappaDomains import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Check if new subdomains were created'
    )
    parser.add_argument(
        '-d', '--domains',
        help="Domain to be analyzed",
        required=True
    )

    parser.add_argument(
        '-o', '--output',
        help="Path folder to save results",
    )

    parser.add_argument(
        '-t', '--type',
        help="Output type (csv = default, txt, small_csv)",
    )

    args = parser.parse_args()

    wappa = WappaDomains(args.domains, args.output, args.type)
    wappa.exec()
