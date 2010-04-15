################################################################################
#   Gene prediction pipeline 
#
#   $Id: tree2stats.py 2782 2009-09-10 11:40:29Z andreas $
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
"""
tree2stats.py - compute statistics on trees
===========================================

:Author: Andreas Heger
:Release: $Id$
:Date: |today|
:Tags: Python

Purpose
-------

Read a collection of trees from stdin and compute statistics on
branchlengths over all trees.

Usage
-----

Example::

   python <script_name>.py --help

Type::

   python <script_name>.py --help

for command line help.

Documentation
-------------

Code
----

""" 
import os, sys, string, re, getopt, time, optparse, math, tempfile, subprocess

from types import *

import Experiment
import TreeTools
import Stats

USAGE="""python tree2stats.py [options] < stdin

compute summary statistics for trees.
"""

if __name__ == "__main__":

    parser = optparse.OptionParser( version = "%prog version: $Id: tree2stats.py 2782 2009-09-10 11:40:29Z andreas $",
                                    usage = globals()["__doc__"] )

    parser.add_option("-m", "--method", dest="methods", type="choice", action="append",
                      choices=("branchlengths",),
                      help="methods to apply." )
                      
    parser.set_defaults(
        methods = [],
        filtered_branch_length = -999,
        )

    (options, args) = Experiment.Start( parser, add_pipe_options = True )

    nexus = TreeTools.Newick2Nexus( sys.stdin )
    if options.loglevel >= 1:
        options.stdlog.write( "# read %i trees from stdin.\n" % len(nexus.trees))

    ninput = len(nexus.trees)

    nskipped = 0
    
    for method in options.methods:

        outfile = options.stdout
        
        if method == "branchlengths":

            outfile.write("tree\t%s\n" % "\t".join(Stats.DistributionalParameters().getHeaders()))
            
            for tree in nexus.trees:
                branchlengths = []
                for node in tree.chain.values():
                    # ignore branch length of root if it is zero
                    if not node.prev and node.data.branchlength == 0: continue

                    if node.data.branchlength == options.filtered_branch_length: continue
                    
                    branchlengths.append( node.data.branchlength )
                    
                s = Stats.DistributionalParameters( branchlengths )
                outfile.write("%s\t%s\n" % (tree.name, str(s)) )
            
    if options.loglevel >= 1:
        options.stdlog.write( "# ninput=%i, nskipped=%i\n" % (ninput, nskipped))
        
    Experiment.Stop()
