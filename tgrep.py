################################################################################
#   Gene prediction pipeline 
#
#   $Id: tgrep.py 2782 2009-09-10 11:40:29Z andreas $
#
#   Copyright (C) 2004 Andreas Heger
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#################################################################################
import os, sys, string, re, tempfile, subprocess, optparse, time

"""do greps in tab-separated tables.
"""

import Experiment

parser = optparse.OptionParser( version = "%prog version: $Id: tgrep.py 2782 2009-09-10 11:40:29Z andreas $")

if __name__ == "__main__":


    parser.add_option("-c", "--columns", dest="columns", type="string",
                      help="columns to test from table." )

    parser.add_option("-f", "--file", dest="file", type="string",
                      help="columns to test from table.",
                      metavar="FILE" )

    parser.add_option("-d", "--delimiter", dest="delimiter", type="string",
                      help="delimiter of columns." ,
                      metavar="DELIM" )

    parser.add_option("-V", "--invert-match", dest="invert_match", action="store_true",
                      help="invert match." )

    parser.set_defaults( \
        file=None,
        columns="1",
        delimiter = "\t",
        invert_match = False )
                        
    (options, args) = Experiment.Start( parser )

    options.columns = map(lambda x: int(x)-1, options.columns.split(","))

    patterns = []
    if options.file:
        infile = open( options.file, "r")
        for line in infile:
            if line[0] == "#": continue
            patterns.append( line[:-1].split(options.delimiter)[0] )
    else:
        patterns=args

    for line in sys.stdin:

        data = line[:-1].split(options.delimiter)
        found = False

        for c in options.columns:
            
            if data[c] in patterns:
                found = True
                break

        if (not found and options.invert_match) or (found and not options.invert_match):
            print line[:-1]

    Experiment.Stop()
