#!/usr/bin/env python
"""
Merge hdf5 files
"""
import os
import sys
import hdf5
import numpy as np
from collections import OrderedDict
from parser import get_args_merge as parser
import msg
import check
import argparse


def get_filelist(bases):

    """look for files which match given bases and return them as list

    Keyword arguments:
    bases -- list of 'path/basename'
    """

    filelist = []

    for base in bases:
        path, fname = os.path.dirname(base) or '.', os.path.basename(base)
        filelist.extend([path + '/' + f for f in os.listdir(path)
                        if f.startswith(fname) and f.endswith(".hdf5")])

    return sorted(filelist)


def merge_data(data_list, attrs_list):

    """Merge dictionaries with data.

    Keyword arguments:
    data_list -- the dictionary with data dictionaries
    """

    data = None
    attrs = None

    for f in data_list:
        size = check.get_size(data_list[f])
        if not data:
            print "\nThe following datasets were found in %s:\n" % f
            msg.list_dataset(data_list[f])
            data = data_list[f]
            attrs = attrs_list[f]
        else:
            print "\nAdding %(n)d entries from %(f)s" % {"n": size, "f": f}
            check.check_keys(data, data_list[f])
            check.check_shapes(data, data_list[f])
            for key in data_list[f]:
                data[key] = np.append(data[key], data_list[f][key], axis=0)
            attrs['n_events'] += attrs_list[f]['n_events']

    return data, attrs


def merge_data_filenames(filelist, outputfile):
    print "The following input files were found:\n"

    for f in filelist:
        print "\t - %s" % f

    data = OrderedDict()
    attrs = OrderedDict()

    for f in filelist:
        data[f], attrs[f] = hdf5.load(f)

    hdf5.save(outputfile, *merge_data(data, attrs))

    msg.info("Done")


if __name__ == '__main__':

    msg.box("HDF5 MANIPULATOR: MERGE")

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--input', type=str, nargs='+',
                        help='input hdf5 list')
    parser.add_argument('--output', type=str,
                        help='output hdf5 file')
    args = parser.parse_args()

    filelist = args.input

    if not filelist:
        msg.error("No files matching --input were found.")
        sys.exit(1)
        
    merge_data_filenames(filelist, args.output)

