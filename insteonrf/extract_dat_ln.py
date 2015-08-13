#!/usr/bin/env python
"""
 This is Junk code
 written for onetime use
 for proof of concept
"""
import sys
import os


def extract_dat(inFile):
    startw = ("#Sout2", "#S ")
    print "File = ", inFile
    fileName, fileExtension = os.path.splitext(inFile)

    i = 0
    try:
        with open(inFile, 'rb') as fi:
            if fileExtension == ".csv":
                fi.seek(-92160, 2)

            for li in fi:
                i = i + 1
                if (li.startswith(startw)):
                    print "Line", i
                    break
                else:
                    print "Line not found"
                    print i, "lines checked"
                    return None
                return li.split()[1]

    except EnvironmentError, err:
        print "Opps", inFile
        print err
        raise
        return None


if __name__ == "__main__":
    for filen in sys.argv[1:]:
        datstr = extract_dat(filen)
        print datstr
    exit(0)
