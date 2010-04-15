################################################################################
#   Gene prediction pipeline 
#
#   $Id: get_sequences_from_www.py 2782 2009-09-10 11:40:29Z andreas $
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
import os, sys, string, re, tempfile, subprocess, optparse, time, math

"""Convert EMBL formatted file into a tab-separated table.
"""

import Experiment

from Bio import SeqRecord
from Bio.WWW import ExPASy
from Bio.SwissProt import SProt
from Bio import File
    
parser = optparse.OptionParser( version = "%prog version: $Id: get_sequences_from_www.py 2782 2009-09-10 11:40:29Z andreas $")

if __name__ == "__main__":

    parser.add_option("-f", "--field", dest="fields", type="string",
                      help="field to write to table." , action="append" )

    parser.set_defaults(
        fields = [] )

    (options, args) = Experiment.Start( parser )

    s_parser = SProt.RecordParser()

    ninput, nfound, nmissed = 0, 0, 0
    
    for line in sys.stdin:
        if line[0] == "#": continue
        
        id = line[:-1].split("\t")[0]
        ninput += 1

        try:
            result = ExPASy.get_sprot_raw(id).read()
        except IOError:
            options.stdlog.write( "# warning: sequence for id %s not found." % id )
            nmissed += 1
            continue
        
        s_iterator = SProt.Iterator(File.StringHandle(result), s_parser)
        try:
            cur_record = s_iterator.next()        
        except SyntaxError:
            print "# Sequence not found: %s" % id
            continue

        columns = [ id, ]
        for f in options.fields:
            if f == "description":
                columns.append( cur_record.description )
                
            elif f == "references":
                for ref in cur_record.references:
                    columns.append( ref.authors, ref.title )                    
            elif f == "organism_classification":
                columns.append( cur_record.organism_classification )
            elif f == "organism":
                columns.append( cur_record.organism )
            elif f == "sequence":
                columns.append( cur_record.sequence )

        print "\t".join(columns)

        nfound += 1
        
    print "# input=%i, found=%i, missed=%i" % (ninput, nfound, nmissed)
    Experiment.Stop()
