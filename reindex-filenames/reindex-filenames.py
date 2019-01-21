"""Rename files or directories to incrementing padded numbers, preserving original order.

Takes a directory that looks like this:
diroffiles/
diroffiles//a
diroffiles//b
diroffiles//c
diroffiles//d
diroffiles//e
diroffiles//f
diroffiles//g
diroffiles//h
diroffiles//i
diroffiles//j
diroffiles//k
diroffiles//l
diroffiles//m
diroffiles//n
diroffiles//o
diroffiles//p
diroffiles//q
diroffiles//r
diroffiles//s
diroffiles//t
diroffiles//u
diroffiles//v
diroffiles//w
diroffiles//x
diroffiles//y
diroffiles//z

And makes it look like this:
diroffiles//00000
diroffiles//00001
diroffiles//00002
diroffiles//00003
diroffiles//00004
diroffiles//00005
diroffiles//00006
diroffiles//00007
diroffiles//00008
diroffiles//00009
diroffiles//00010
diroffiles//00011
diroffiles//00012
diroffiles//00013
diroffiles//00014
diroffiles//00015
diroffiles//00016
diroffiles//00017
diroffiles//00018
diroffiles//00019
diroffiles//00020
diroffiles//00021
diroffiles//00022
diroffiles//00023
diroffiles//00024
diroffiles//00025

"""
import argparse
import glob
import os

argparser = argparse.ArgumentParser(description="Rename directories to incrementing padded numbers, preserving original order.")
argparser.add_argument("topdir")
argparser.add_argument("--dry-run", action="store_true", help="Print out what I would do, but don't actually do it.")
cliargs = argparser.parse_args()

dir_s = glob.glob(cliargs.topdir + "/*")
dir_s.sort()

if len(dir_s) > 0:
    index = 1
    for directory in dir_s:
        source = directory
        destination = cliargs.topdir + "/" + "%05d" % index
        print("Move %s to %s" % (source, destination))
        if cliargs.dry_run is not True:
            os.rename(directory, destination)
        index = index + 1
else:
    logging.error("No directories found in %s" % cliargs.topdir)
    exit(1)
