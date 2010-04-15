################################################################################
#   Gene prediction pipeline 
#
#   $Id: csv2csv.py 2782 2009-09-10 11:40:29Z andreas $
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


"""do some table magic.

--sort: sort table 


"""
import Experiment
import csv

parser = optparse.OptionParser( version = "%prog version: $Id: csv2csv.py 2782 2009-09-10 11:40:29Z andreas $")

def ConvertDictionary( d ):
    """tries to convert values in a dictionary.
    """

    rx_int = re.compile("^[+-]*[0-9]+$")
    rx_float = re.compile("^[+-]*[0-9.+-eE]+$")
    for k,v in d.items():
        if rx_int.match( v ):
            d[k] = int(v)
        elif rx_float.match( v ):
            d[k] = float(v)

    return d
    
if __name__ == "__main__":

    parser.add_option( "-s", "--sort", dest="sort", type="string" ,
                       help="fields to take (in sorted order).")

    (options, args) = Experiment.Start( parser, add_csv_options  = True)

    reader = csv.DictReader( sys.stdin, dialect=options.csv_dialect )

    if options.sort:
        fields = options.sort.split(",")
    else:
        fields = None
        
    writer = csv.DictWriter( sys.stdout,
                             fields,
                             dialect=options.csv_dialect,
                             lineterminator = options.csv_lineterminator,
                             extrasaction = 'ignore' )

    print "\t".join(fields)
    
    for row in reader:
        row = ConvertDictionary( row )
        writer.writerow(row)
        
    Experiment.Stop()
