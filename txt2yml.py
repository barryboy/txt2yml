#!/usr/bin/env python

### IMPORTS ###
import os.path
import argparse
import re

### INTERNAL FUNCTIONS ###

def create_args_parser():
    """Returns a parser for validating commandline arguments"""
    parser = argparse.ArgumentParser(description = 'Format txt transcriptions into yml NegNet input files')
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument('-d', '--dir', dest='dirname', metavar='<DIR>', type=lambda x: is_valid_dir(parser, x), help='a dir with txt files')
    exclusive.add_argument('-f', '--file', dest='filename', metavar='<FILE>', type=lambda x: is_valid_file(parser, x), help='a file to be processed')
    parser.add_argument('-o', '--out', dest='out', metavar='<OUT>', type=lambda x: is_valid_dir(parser, x), help='an output dir')
    return parser

def is_valid_dir(parser, arg):
    """Checks if the 'dirname' argument is a valid directory name.

    Positional arguments:
    parser -- an ArgumentParser instance from argparse
    arg -- the 'dirname' argument
    """
    if not os.path.isdir(arg):
        parser.error("The directory {0} does not exist!".format(arg,))
    else:
        return arg

def is_valid_file(parser, arg, ext='.txt'):
    """Checks if the 'filename' argument points to a valid file.

    Positional arguments:
    parser -- an ArgumentParser instance from argparse
    arg -- the 'filename' argument
    ext -- extension filter (default: '.txt')
    """
    if not os.path.isfile(arg):
        parser.error("The {0} does not exist or is not a valid file".format(arg,))
    else:
        filename, file_extension = os.path.splitext(arg)
        if (file_extension != ext):
            parser.error("{0} has a wrong extension ({1})".format(arg, ext))
        else:
            return arg


def handle_dir(dirname, out):
    """Reads files in 'dirname' directory and processes them in a loop

    Positional arguments:
    dirname -- a source directory
    out -- a target directory to store converted files
    """
    files = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]
    for f in files:
        converted = handle_file(os.path.join(dirname, f), out)

def read_from_file(filename):
    """Tries to read text file using UTF-8 encoding. In case of failure tries again with Windows-1250.

    Positional arguments:
    filename -- the file to read in
    """
    print("--- Reading file")
    try:
        print("------ trying UTF-8")
        f = open(filename, "r")
        try:
            data = f.readlines()
        except:
            print("------ could not read file in UTF-8 format, switching to Windows-1250")
            try:
                print("------ trying Windows-1250")
                f2 = open(filename, "r", encoding = "windows-1250")
                data = f2.readlines()
            except:
                print("------ could not read file in Windows-1250 format. ABORTING")
            finally:
                f2.close()
    except:
        print("------ could not open file")
    finally:
        f.close()
    if ('data' in locals()):
        print("--- File read!")
        return data

def trim_data(data):
    """ ...
    """
    result = []
    for line in data:
        result.append(line.strip())
    return result

def is_beginning_ok(line):
    """ ...
    """
    match_beginning = "^[LP]:? ?"
    return re.findall(match_beginning, line) != []

def split_party_content(line):
    """ ...
    """
    match_beginning = "^([LP]):? ?(.*)$"
    return re.findall(match_beginning, line)[0]

def extract_fline(data):
    """ ...
    """
    new_data = data
    fline = data[0]
    if (is_beginning_ok(fline)):
        print("--- First line is absent. Using 'NA'")
        fline = 'NA'
    else:
        print("--- First line extracted: '{0}'".format(fline))
        new_data = data[1:]
    return (new_data, fline)

def purge_malformed_lines(data):
    """...
    """
    data_out = []
    for i in range(len(data)):
        line = data[i]
        if (is_beginning_ok(line)):
            data_out.append(line)
        else:
            print("--- Found malformed line({0}): '{1}' -> removed".format(i, line))
    return data_out

def save_yml(content, outdir, filename):
    """...
    """
    filename_short = os.path.basename(filename)
    name, extension = os.path.splitext(filename_short)
    out_filename = name + ".yml"
    outpath = os.path.join(outdir, out_filename)
    try:
        out = open(outpath, "w")
        out.write(content)
    except:
        print("!!! Error saving converted file !!!")
    finally:
        out.close()
        print("--- saved converted file in:'{0}'".format(outpath))

def handle_file(filename, outdir):
    """ ...
    """
    print('\n## PROCESSING: \'' + filename + '\'')
    data = read_from_file(filename)
    data = trim_data(data)
    data, fline = extract_fline(data)
    frontmatter = "---\ntitle: \"{0}\"\ncontent:".format(fline)
    footer = "\n...\n"
    data = purge_malformed_lines(data)
    n_utterances = len(data)
    steps = ""
    for i in range(n_utterances):
         line = data[i]
         party, content = split_party_content(line)
         steps += "\n        - step: {0}\n          p: {1}\n          u: \"{2}\"".format(i+1, party, content)
    whole_txt = frontmatter + steps + footer
    save_yml(whole_txt, outdir, filename)

### MAIN LOGIC ###
parser = create_args_parser()
args = parser.parse_args()

if (args.out):
    output_dir = args.out
else:
    if (args.dirname):
        dirpath = os.path.realpath(args.dirname)
    elif (args.filename):
        dirpath = os.path.dirname(os.path.realpath(args.filename))

    output_dir = os.path.join(dirpath, "CONVERTED")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

if (args.dirname):
    handle_dir(args.dirname, output_dir)
elif (args.filename):
    handle_file(args.filename, output_dir)

