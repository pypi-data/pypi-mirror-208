# Copyright (c) 2022, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html

"""CHKSUM
Compare checksums from the command line easily and with visual feedback.
Goal: A CLI app that isn't picky about the order of arguments (user friendly!!!)"""

import os
import argparse
import importlib.metadata

import checksum
from colorama import Fore, init
init(autoreset=True)

try:
    __version__ = f"chksum {importlib.metadata.version('chksum_cli')} from chksum_cli"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."


class StandaloneMode(argparse.Action):
    """ Custom action for running the interactive mode"""
    def __call__(self, parser, namespace, values, option_string=None):
        # redefined-outer-name -> https://docs.python.org/3/library/argparse.html
        parser.exit(stand_alone(single_run=True))


CHKSUM_LICENSE = """  Copyright (c) 2022, espehon\n  License: https://www.gnu.org/licenses/gpl-3.0.html"""

ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512']

positionals = {}    # for storing positionals their type
method = 'md5'      # algorithm to be used. Currently set as default (not a constant)

interactive_colors = {      # colors used in the interactive mode
                'prompt': Fore.LIGHTBLUE_EX,
                'output': Fore.BLUE,
                'input': Fore.LIGHTWHITE_EX,
                'warn': Fore.LIGHTYELLOW_EX
            }

parser = argparse.ArgumentParser(
    prog="CHKSUM",
    description = (f"Calculate and compare the checksums of files or directories.\nCan also compare against pasted strings. \n{ALGORITHMS = }"),
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog = (f"If the first 2 positional arguments are strings, the algorithm is not needed. Default is {method}.\n\tExample 1: chksum ./file1 ./file2 sha512\n\tExample 2: chksum 123456789ABCDEF 123456789ABCDEF\n\tExample 3: chksum ./dir 123456789ABCDEF\nLikewise, passing only a single path will simply out the digest."),
    add_help = False # free -h from help (-? will be used as help flag)
)
parser.add_argument('-?',
                    '--help',
                    action='help',
                    help="Show this help message and exit."     # make -? help
)
parser.add_argument('-v',
                    '--version',
                    action='version',
                    version=__version__,
                    help="Show package version and exit."
)
parser.add_argument('-i',
                    '--interactive',
                    action=StandaloneMode,
                    nargs=0,
                    help="Run in interactive mode. (mutually exclusive)"
)
parser.add_argument('-d',
                    '--dots',
                    action='store_true',
                    help="Ignore '.' (dot) files from directories."
)
parser.add_argument('position1',
                    type=str,
                    help="Checksum, file, or algorithm"
)
parser.add_argument('position2',
                    type=str,
                    nargs='?',
                    help="Checksum, file, or algorithm"
)
parser.add_argument('position3',
                    type=str,
                    nargs='?',
                    help="Checksum, file, or algorithm"
)

def get_full_path(relative_path: str):
    """Takes a $HOME relative path and returns the absolute path"""
    return os.path.expanduser(relative_path)

def store_dir(value: str, key: int):
    """Stores the value in positionals and marks it as a directory"""
    positionals[key] = {'value': value, 'type': 'dir'}

def store_file(value: str, key: int):
    """Stores the value in positionals and marks it as a file"""
    positionals[key] = {'value': value, 'type': 'file'}

def store_hash(value: str, key: int):
    """Stores the value in positionals and marks it as a hash"""
    positionals[key] = {'value': value, 'type': 'hash'}

def set_algorithm(value: str):
    """Overrides the method with the given value"""
    global method
    method = str.lower(value)

def process_positional(value: str, key: int):
    """
    This function will determine what to do with positional arguments (value) that the user passed.
    It will first check if the value is an algorithm, then if it is a file, then directory.
    The value is considered a hashed value if none of the above.
    Files and directories hashed in order of positionals[iteration].
    """
    if '~' in value:
        value = get_full_path(value)

    if str.lower(value) in ALGORITHMS:
        set_algorithm(value)
    elif os.path.isfile(value):
        store_file(value, key)
    elif os.path.exists(value):
        store_dir(value, key)
    else:
        store_hash(str.lower(value), key) # checksum returns lowercase

def get_hash(path: str, is_directory: bool=False) -> str:
    """Returns the checksum of the given path"""
    if is_directory:
        return checksum.get_for_directory(path, hash_mode=method, filter_dots=args.dots)
    return checksum.get_for_file(path, hash_mode=method)

def yield_license_once() -> object:
    """Generator function for return CHKSUM_LICENSE once"""
    first_run = True
    while True:
        if first_run:
            first_run = False
            yield CHKSUM_LICENSE
        else:
            yield ""


def compare_hashes(hash_1: str, hash_2: str, title: str):
    """
    Compare two strings and highlight differences on output.
    Then output True | False.
    """
    if hash_1.strip() == "" or hash_2.strip() == "":
        print(Fore.YELLOW + "One or more values were blank...")
        return "Value(s) were blank"
    output_row_1 = ""       # first hash to print
    output_row_2 = ""       # second hash to print
    larger_row = None       # keeps track of the larger hash
    offset = 0              # difference in hash sizes
    width = 0               # for title bar formatting
    match [len(hash_1), len(hash_2)]:
        # set logic depending on sizes of hashes for coloring (and to continue where zip stops)
        case [a, b] if a == b:
            width = a
        case [a, b] if a > b:
            offset = a - b
            larger_row = 1
            width = a
        case [a, b] if a < b:
            offset = b - a
            width = b
    for (a, b) in zip(hash_1, hash_2):
        # color matching characters green and non matching yellow (orange)
        if a == b:
            output_row_1 += Fore.GREEN + a
            output_row_2 += Fore.GREEN + b
        else:
            output_row_1 += Fore.YELLOW + a
            output_row_2 += Fore.YELLOW + b
    if offset != 0:  # pickup where zip stopped. Make extra characters red
        if larger_row == 1:
            output_row_1 += Fore.RED + hash_1[-offset :]
        else:
            output_row_2 += Fore.RED + hash_2[-offset :]
    
    # output formatted info
    print()
    print(str.upper("[" + title + "]").center(width, '-'))
    print(output_row_1)
    print(output_row_2)

    if hash_1 == hash_2:    # output the final result
        print(Fore.LIGHTGREEN_EX + "√ Hashes Match\n")
        return True
    else:
        print(Fore.LIGHTRED_EX + "X Hashes Do Not Match\n")
        return False

def output_single_hash(path: str, is_directory: bool=False):
    hash = get_hash(path, is_directory)
    title = str.upper("[" + method + "]").center(len(hash), '-')
    print(title)
    print(hash)


def cli(argv=None):
    """
    Processes the command line arguments and outputs accordingly.
    This is the main logic for the program when ran as one line (not in interactive mode)
    """
    
    global method
    global args
    args = parser.parse_args(argv)              # get args from input

    process_positional(args.position1, 1)   # store positional accordingly

    try:
        process_positional(args.position2, 2)    # store positional accordingly (optional if user wants to know a hash)
        process_positional(args.position3, 3)    # store optional 3rd positional
    except TypeError:
        # There was no third positional and maybe no 2nd
        pass

    if len(positionals) < 2:    # check if single hash mode or possible missing args
        for position in positionals:
            if positionals[position]['type'] == 'file' or positionals[position]['type'] == 'dir':
                output_single_hash(positionals[position]['value'], positionals[position]['type'] == 'dir')
                return 0
        return "Missing positional argument..."

    hashes = []                 # stores the final hashes for output
    iteration = 1               # tracks iteration and doubles as a dictionary key
    hashes_were_prepared = True   # is set to False if this script runs the hash.
    try:
        while len(hashes) < 2 and iteration <= 3:
            # iterate through stored positionals and hash them accordingly
            if iteration in positionals:
                if positionals[iteration]['type'] == 'dir':
                    hashes.append(get_hash(positionals[iteration]['value'], is_directory=True))
                    hashes_were_prepared = False
                elif positionals[iteration]['type'] == 'file':
                    hashes.append(get_hash(positionals[iteration]['value']))
                    hashes_were_prepared = False
                elif positionals[iteration]['type'] == 'hash':
                    hashes.append(positionals[iteration]['value'])
            iteration += 1
    except KeyboardInterrupt:
        print(Fore.YELLOW + "Keyboard Interrupt!")
        return 0
    except PermissionError:
        print(Fore.LIGHTRED_EX + "Permission Denied.")
        return 1

    if hashes_were_prepared:
        method = 'Strings'
    if compare_hashes(hashes[0], hashes[1], method): # test, format, and output hashes
        return 0
    return 1
    

def stand_alone(single_run=False):
    """ 
    Interactive mode
    This is the standalone version.
    Logic works as follows:
        1. Get 1 of 3 options from user
        2. Determine which option was given
        3. Ask for 1 of 2 remaining options
        4. Determine which option was given
        5. Ask for final option
        6. Test, format, and output hashes
        7. Ask to rerun
    """
    user = ""                                   # for storing user input
    program_is_running = True                   # for controlling the following while loop
    CWD = os.getcwd()                           # current working directory
    license_generator = yield_license_once()    # generator for printing license on first loop only
    TITLE = fr"""


      _     _                        
     | |   | |                       
  ___| |__ | | _____ _   _ _ __ ___  
 / __| '_ \| |/ / __| | | | '_ ` _ \ 
| (__| | | |   <\__ \ |_| | | | | | |
 \___|_| |_|_|\_\___/\__,_|_| |_| |_|"""

    while program_is_running:
        try:
            print(f"{interactive_colors['output']}{TITLE}")
            print(f"{interactive_colors['output']}{next(license_generator)}")
            print(f"{interactive_colors['output']}\n{ALGORITHMS = }")
            print(f"{interactive_colors['output']}Called at " + CWD + "\n")

            method = None
            hash_1 = None
            hash_2 = None

            include_dots = None
            tries = 3
            hash_strings = 0
            

            while method is None or hash_1 is None or hash_2 is None:
                match [method, hash_1, hash_2]:
                    case [a, b, c] if a is None and (b is None or c is None):
                        user = input(interactive_colors['prompt'] + "Enter Algorithm or Path to File or Directory > " + interactive_colors['input'])
                    case [a, b, c] if a is not None and (b is None or c is None):
                        user = input(interactive_colors['prompt'] + "Enter Path to File or Directory > " + interactive_colors['input'])
                    case [a, b, c] if a is None and not (b is None or c is None):
                        user = input(interactive_colors['prompt'] + "Enter Algorithm > " + interactive_colors['input'])

                if user.strip() == "":
                    tries -= 1
                    print(f"\t{interactive_colors['output']}Nothing was entered; please try again. ({interactive_colors['warn']}{tries}{Fore.BLUE} tries remain)")
                elif str.lower(user) in ALGORITHMS:
                    method = str.lower(user)
                    print(interactive_colors['output'] + "\tAlgorithm entered.")
                else:
                    if '~' in user:
                        user = get_full_path(user)
                    if os.path.isfile(user):
                        print(interactive_colors['output'] + "\tFile entered.")
                    elif os.path.exists(user):
                        print(interactive_colors['output'] + "\tDirectory entered.")
                    else:
                        print(interactive_colors['output'] + "\tHash string entered.")
                        if hash_1 is None or hash_2 is None:
                            hash_strings += 1
                    if hash_1 is None:
                        hash_1 = user
                    elif hash_2 is None:
                        hash_2 = user
                    else:
                        tries -= 1
                        print(interactive_colors['output'] + f"\tYou've already supplied two hash objects. ({interactive_colors['warn']}{tries}{interactive_colors['output']} tries remain)")
                if hash_strings >= 2:
                    method = "STRINGS" # no need for algorithm
                    break
                if tries <= 0:
                    print(interactive_colors['warn'] + "\tNumber of tries exceeded!")
                    raise UserWarning

            for index, thing in enumerate([hash_1, hash_2]):
                if os.path.isfile(thing):
                    if index == 0:
                        hash_1 = checksum.get_for_file(thing, hash_mode=method)
                    else:
                        hash_2 = checksum.get_for_file(thing, hash_mode=method)
                elif os.path.exists(thing):
                    if include_dots is None:
                        include_dots = str.lower(input(interactive_colors['prompt'] + "Do you want to include '.' (dot) files? [Y/n] > " + interactive_colors['input'])).strip() != 'n'
                        print(interactive_colors['output'] + f"\t{include_dots = }")
                    if index == 0:
                        hash_1 = checksum.get_for_directory(thing, hash_mode=method,
                        filter_dots= not include_dots)
                    else:
                        hash_2 = checksum.get_for_directory(thing, hash_mode=method,
                        filter_dots= not include_dots)
                else:
                    if index == 0:
                        hash_1 = str.lower(thing)   # checksum returns lowercase
                    else:
                        hash_2 = str.lower(thing)   # checksum returns lowercase

            # Finally output time!
            if compare_hashes(hash_1, hash_2, method) and single_run: # test, format, and output
                return 0    # if in single run mode, exit program with code 0
            elif single_run:
                return 1    # if in single run mode, exit program with code 1
            # else (if not in single mode) continue though loop

        except KeyboardInterrupt:
            print(interactive_colors['warn'] + "Keyboard Interrupt!")
        except UserWarning:
            print(interactive_colors['output'] + "\tProgress stopped...")
        except PermissionError:
            print(Fore.LIGHTRED_EX + "Permission Denied.")  # this should always be light red

        program_is_running = False
        if single_run is False:
            try:    # Incase the user mashes keyboard interrupt
                user = str.lower(input(f"{interactive_colors['prompt']}\nEnter R to rerun. Anything else will exit. > "))
                if user == 'r':
                    program_is_running = True
                    print('\n' * 3)
            except KeyboardInterrupt:
                print(interactive_colors['warn'] + "Exiting program...")
