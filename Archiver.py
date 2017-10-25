'''Archives files in this way:
1. Get a password & directory name
2. Create a split 7-zip archive for each entry (file or folder) in the IN_DIR
3. Generate parity files with parpar
'''

import os
import sys
import random
import string
import subprocess
import logging
from math import ceil

IN_DIR = 'd:\\int\\'
OUT_DIR = 'e:\\out\\'
LOG_NAME = OUT_DIR + 'files.txt'
RAM_ALLOCATION = '2400M'  # M = megabytes
# use two sets of quotes for compatibility with
# Powershell even if spaces are in the path
ARCHIVER_PATH = '"C:\\Program Files\\7-Zip\\7z.exe"'
PARPAR_PATH = '"c:\\apps\\parpar\\parpar.cmd"'

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def get_random_chars(length=20):
    # https://paragonie.com/blog/2016/05/how-generate-secure-random-numbers-in-various-programming-languages#python-csprng
    csprng = random.SystemRandom()
    # https://stackoverflow.com/questions/2511222/efficiently-generate-a-16-character-alphanumeric-string
    # Using code from Stack Overflow. Question asked by ensnare. Answer by Mark Byers.
    # https://stackoverflow.com/users/216605/ensnare
    # https://stackoverflow.com/users/61974/mark-byers
    # alphanumeric A-z
    # assumed to have good compatibility with terminals and programs
    chars_to_sample = string.ascii_letters + string.digits
    random_chars = ''.join(csprng.choice(chars_to_sample)
                           for _ in range(length))
    return random_chars


def rand_insert(old_str, new_chars):
    """Insert new_chars into old_chars at randomized positions."""
    csprng = random.SystemRandom()
    while new_chars:
        random_int = csprng.randint(0, len(old_str) - 1)
        old_str = old_str[:random_int] + new_chars[0] + old_str[random_int:]
        new_chars = new_chars[1:]
    return old_str


def encrypt_and_split(out_archive_name, mypass, incoming_entry, compression_level):
    # compression_level is the 7-zip command line compression level
    # https://sevenzip.osdn.jp/chm/cmdline/switches/method.htm#ZipX
    # 0 = none, 1 = fastest, 9 = slowest (best compression)
    compression_level = str(compression_level)
    args = (ARCHIVER_PATH + ' a -t7z ' + OUT_DIR +
            out_archive_name + '\\' + out_archive_name + ' -bt -p' + mypass +
            ' -mhe=on -mx' + compression_level +
            # v200m: split into 200 MB chunks
            ' -v200m "' + incoming_entry + '"')
    subprocess.call(args, shell=False)


def folder_size(path='.'):
    # https://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
    # Using code from Stack Overflow. Question asked by Gary Willoughby.
    # Edited by Tshepang. Answer by blakev.
    # https://stackoverflow.com/users/13227/gary-willoughby
    # https://stackoverflow.com/users/321731/tshepang
    # https://stackoverflow.com/users/2714534/blakev
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += folder_size(entry.path)
    return total


def files_to_str(path='.'):
    '''Parse files from path as one long string, non-recursively.'''
    file_str = ''
    for entry in os.scandir(path):
        if entry.is_file():
            file_str = file_str + str(entry.name) + ' '
    return file_str


def make_pars(out_archive_name, target_redundancy=.1):
    par_folder = os.path.join(OUT_DIR, out_archive_name)
    size_bytes = folder_size(par_folder)
    # Seems that num_slices * slice_size is approximately equal to
    # the total size in bytes of the par2 recovery files.
    slice_size = 5905832  # bytes

    def sanitize_slice_size(slice_size):
        if ceil(size_bytes / slice_size) >= 32768:
            logging.warning(
                "The parpar source code indicates there may be a problem here.")
            logging.warning(
                "ceil(this.totalSize / o.sliceSize) must be < 32768.")
        # must be multiple of 4
        if (slice_size % 4) != 0:
            logging.debug("slice_size % 4) != 0")
            slice_size = slice_size + (4 - slice_size % 4)
        # must be even. doing separate test in case of future desire to
        # re-arrange or remove the above %4 check
        if slice_size % 2 != 0:
            logging.debug("slice_size % 2 != 0")
            slice_size = slice_size + 1
        return int(slice_size)
    slice_size = sanitize_slice_size(slice_size)
    num_slices = ceil(target_redundancy * size_bytes / slice_size)
    # must be strings for the subprocess.call to the command line
    slice_size = str(slice_size)
    num_slices = str(num_slices)
    par_files = files_to_str(par_folder)
    # avoid parpar weirdness
    os.chdir(par_folder)
    args = (PARPAR_PATH + ' -o ' + OUT_DIR + out_archive_name +
            # ex. /OUT_DIR/filename/filename.file
            '\\' + out_archive_name + ' --slice-size ' +
            slice_size + ' --recovery-slices ' + num_slices +
            ' --memory ' + RAM_ALLOCATION +
            ' --index --slice-dist pow2 --alt-naming-scheme ' + par_files)
    logging.info("Invoking parpar with this command: ")
    logging.info(args)
    subprocess.call(args, shell=False)


def main():
    '''main program'''
    # An in_entry is a file by itself, or an entire directory (non recursive).
    for in_entry in os.listdir(IN_DIR):
        in_full_dir = os.path.join(IN_DIR, in_entry)
        mypass = get_random_chars(20)
        out_archive_name = get_random_chars(20)
        chars_to_add = input('More characters for the password?')
        mypass = rand_insert(mypass, chars_to_add)
        # log the in_entry and its corresponding archive name and password
        with open(LOG_NAME, 'a') as file:
            file.write('\n' + in_entry + '\n' + mypass +
                       '\n' + out_archive_name + '\n')
        encrypt_and_split(out_archive_name, mypass,
                          in_full_dir, compression_level=1)
        make_pars(out_archive_name)


if __name__ == "__main__":
    main()
