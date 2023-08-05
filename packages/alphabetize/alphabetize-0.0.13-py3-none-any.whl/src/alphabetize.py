import argparse
import glob
import os
import pathlib
import re


def sort_variables(name=None):
    with open(name, 'r+') as file:
        file_lines = file.read().split('\n')
        updated_file = ''
        variable_lines = []
        variable_names = []
        # Loop over each line in the file
        for line in file_lines:
            # Locate variable in a line by '='
            if re.match('.* = .*', string=line):
                # Does the line use any other variables already listed before
                # The previous variable names array are looped over to check if referenced in the current line
                for name in variable_names:
                    # A match indicates it uses a previously defined variable, and thus shouldn't be part of ordering
                    # The variables found so far are ordered and added to the file, followed by the current matched line
                    # The variable name and line are reset to the current line as a variable is still present
                    if re.search(f"\\b({name})\\b", string=line):
                        variable_lines.sort()
                        for ordered_line in variable_lines:
                            updated_file += ordered_line + '\n'
                        variable_names = []
                        for variable_name in re.findall('.*(?= = )', string=line)[0].replace(' ', '').split(','):
                            variable_names.append(variable_name)
                        # variable_names = [re.findall('\\w*(?= = )', string=line)[0]]
                        variable_lines = [line]
                        break
                # No match means the variable is independent and can be added to the sort list
                else:
                    for variable_name in re.findall('.*(?= = )', string=line)[0].replace(' ', '').split(','):
                        variable_names.append(variable_name)
                    # variable_names.append(re.findall('\\w*(?= = )', string=line)[0])
                    variable_lines.append(line)
            # No variable is found, so the variables array found before is sorted and added, before the current line
            # The variable name and line are reset to be empty as there are no variables present
            else:
                variable_lines.sort()
                for ordered_line in variable_lines:
                    updated_file += ordered_line + '\n'
                updated_file += line + '\n'
                variable_names = []
                variable_lines = []
        # Remove final newline created
        updated_file = updated_file.rstrip('\n')
        updated_file = updated_file + '\n'
        # Wipe file contents and write ordered contents
        file.seek(0)
        file.truncate()
        file.write(updated_file)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        nargs="*",
        metavar="FILENAME",
        default="",
        help="Filename to be sorted. Only works for .py files"
    )
    args = parser.parse_args()
    return args.filename


def retrieve_files(pathname):
    # If no path is parsed, all '.py' files are searched in the current directory
    if not pathname:
        directory_search = f"{pathlib.Path().resolve()}\\*.py"
    # If an absolute directory is parsed, all '.py' files are searched in that directory
    elif 'C:\\' in pathname[0]:
        directory_search = f"{pathname[0]}\\*.py"
    # If a relative directory is parsed, all '.py' files are searched in that directory
    else:
        print('here')
        directory_search = f"{pathlib.Path().resolve()}\\{pathname[0]}\\*.py"
    files = []
    for path in glob.glob(directory_search):
        files.append(path)
    return files


def main():
    pathname = parse_args()
    # If the arg parsed contains '.py', that specific file is only used
    if pathname and '.py' in pathname[0]:
        sort_variables(pathname[0])
    else:
        # Retrieves a list of all files from the parsed argument
        files = retrieve_files(pathname)
        for file in files:
            sort_variables(file)
