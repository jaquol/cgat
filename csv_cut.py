#!/usr/bin/env python
################################################################################
#   Gene prediction pipeline 
#
#   $Id: csv_cut.py 2782 2009-09-10 11:40:29Z andreas $
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
import os, sys, string, re, getopt, time, optparse, math, tempfile

import Experiment
import csv, _csv, hashlib
import CSV

USAGE="""csv_cut.py [OPTIONS] col1 [col2 [...]] < stdin

extract named columns from a csv formatted table

Example:

Extract the two columns gene and length from a table in standard input:

  csv_cut.py gene length < stdin

The script permits the use of patterns. For example, the command 
will select the column gene and all columns that contain the part 'len'

  csv_cut.py gene %len% < stdin
"""

class UniqueBuffer:
    mKeys = {}
    def __init__(self, outfile):
        self.mOutfile = outfile
    def write( self, out ):
        key = hashlib.md5(out).digest()
        if key not in self.mKeys:
            self.mKeys[key] = True
            self.mOutfile.write(out)

class CommentStripper:
    """iterator class for stripping comments from file.
    """
    
    def __init__(self, file ):
        self.mFile = file

    def __iter__(self):
        return self
    
    def next(self):
        while 1:
            line = self.mFile.readline()
            if not line:
                raise StopIteration
            if line[0] != "#":
                return line
        
if __name__ == "__main__":

    parser = optparse.OptionParser( version = "%prog version: $Id: csv_cut.py 2782 2009-09-10 11:40:29Z andreas $")

    parser.add_option( "-r", "--remove", dest="remove", action="store_true",
                       help="remove specified columns, keep all others." )

    parser.add_option( "-u", "--unique", dest="unique", action="store_true",
                       help="output rows are uniq." )

    parser.add_option( "-l", "--large", dest="large", action="store_true",
                       help="large columns. Do not use native python CSV module [default=%default]." )

    parser.add_option( "-f", "--filename-fields", dest="filename_fields", type="string",
                       help="filename with field information.")

    parser.set_defaults(
        remove = False,
        unique = False,
        filename_fields = None,
        )

    (options, args) = Experiment.Start( parser,
                                        add_csv_options  = True,
                                        quiet = True )

    input_fields = args

    if options.filename_fields:
        input_fields = map( lambda x: x[:-1].split("\t")[0],
                            filter( lambda x: x[0] != "#", open(options.filename_fields, "r").readlines()))

                            
    if options.unique:
        outfile = UniqueBuffer(sys.stdout)
    else:
        outfile = options.stdout

    while 1:
        line = sys.stdin.readline()
        
        if not line:
            Experiment.Stop()
            sys.exit(0)
        
        if line[0] == "#": continue
        
        first_line = line
        break
            
    old_fields = first_line[:-1].split("\t")

    if options.remove:
        fields = []
        for x in old_fields:
            if x not in input_fields:
                fields.append( x )
    else:
        fields = []
        for f in input_fields:
            ## do pattern search
            if f[0] == "%" and f[-1] == "%":
                pattern = re.compile( f[1:-1] )
                for o in old_fields:
                    if pattern.search( o ) and o not in fields:
                        fields.append( o )
            else:
                if f in old_fields:
                    fields.append( f )
                    
    if options.large:
        reader = CSV.DictReaderLarge( CommentStripper(sys.stdin),
                                      fieldnames = old_fields,
                                      dialect=options.csv_dialect )
    else:
        reader = csv.DictReader( CommentStripper(sys.stdin),
                                 fieldnames = old_fields,
                                 dialect=options.csv_dialect )

    writer = csv.DictWriter( outfile,
                             fields,
                             dialect=options.csv_dialect,
                             lineterminator = options.csv_lineterminator,
                             extrasaction = 'ignore' )

    print "\t".join(fields)        

    first_row = True
    ninput, noutput, nerrors = 0, 0, 0

    while 1:
        ninput += 1
        try:
            row = reader.next()
        except _csv.Error, msg:
            options.stderr.write( "# error while parsing: %s\n" % (msg ) )
            nerrors += 1
            continue
        except StopIteration:
            break
        if not row: break
        writer.writerow(row)
        noutput += 1

    if options.loglevel >= 1:
        options.stdlog.write( "# ninput=%i, noutput=%i, nerrors=%i\n" % (ninput, noutput, nerrors) )

    Experiment.Stop()
