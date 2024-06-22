import argparse
import os
import re
import sys


def find_init_without_super(path, ignore=[]):
	abs_path = os.path.abspath(path)
	ignores_addition = f" with ignores: {ignore}" if ignore else ""
	print(f"Searching for __init__ methods without super().__init__ calls... in '{abs_path}'{ignores_addition}. Continue?\n\n")
	if input("y/n: ") != "y":
		return
	init_pattern = re.compile(r'def __init__\(self[^)]*\):')
	super_pattern = re.compile(r'super\(\).__init__\(')

	for root, _, files in os.walk(path):
		for file in files:
			# Ignore env/ directories
			break_occurred = False
			for ignored_part in ignore:
				if ignored_part in root:
					break_occurred = True
					break
			if break_occurred:
				print(f"Ignoring file: {file} as it contains ignored part '{ignored_part}' in {root}")
				continue
			if file.endswith(".py"):
				file_path = os.path.join(root, file)
				try:
					with open(file_path, 'r', encoding='utf-8') as f:
						content = f.read()
						inits = init_pattern.finditer(content)
						for init in inits:
							start = init.end()
							end = content.find("def ", start)
							if end == -1:
								end = len(content)
							init_body = content[start:end]
							if not super_pattern.search(init_body):
								print("File: {}, Line: {}".format(file_path, content.count('\n', 0, init.start()) + 1))
								print(init.group())
								print()
				except UnicodeDecodeError:
					print(f"Could not decode file: {file_path}")


parser  = argparse.ArgumentParser(description="Search for __init__ methods without super().__init__ calls.")
parser .add_argument("path", type=str, help="Path to search for __init__ methods.")
parser .add_argument("--ignore", nargs='+', default=[], help="Directories to ignore.")
args = parser.parse_args()

find_init_without_super(args.path, args.ignore)
