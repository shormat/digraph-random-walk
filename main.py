import argparse
import os
import sys

import utils
from file import main

parser = argparse.ArgumentParser(description="Random-walk statistics on a directed graph read from a JSON file")
parser.add_argument('-f', '--file', nargs=1, metavar='FILE', type=str, required=True,
                    help='JSON graph file to read')
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
parser.add_argument('-p', action='store_true',
                    help='Use the arc probabilities from the file instead of a uniform choice')
parser.add_argument('--show', action='store_true', help='Display the graph')
args = parser.parse_args()

if args.debug:
    utils.debugOn()
if args.p:
    utils.pOn()
if args.show:
    utils.showOn()

path = args.file[0]
if not os.path.isfile(path):
    print("The file does not exist.")
    sys.exit()
if os.path.splitext(path)[1] != ".json":
    print("Wrong file extension, .json expected.")
    sys.exit()

main(path)
