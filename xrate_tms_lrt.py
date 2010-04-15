import sys, string, re, optparse

USAGE = """filter results from an xrate tms run.

This script filters the output of a series computations with xrate_tms.py.

The output is filtered by length (individual minimum length of N- and 
C-terminus).

For each set of nested models, a log likelihood ratio test is performed.

This program takes as input the file lnl.table Makefile.xrate_tms

"""

import Experiment
import Stats
import CSV

if __name__ == "__main__":

    parser = optparse.OptionParser( version = "%prog version: $Id: xrate_tms_lrt.py 2781 2009-09-10 11:33:14Z andreas $", usage = USAGE )

    parser.add_option( "-l", "--min-length", dest = "min_length", type = "int",
                       help="minimum individual length (in nucleotides) of N- and C-terminus [default=%default]." )

    parser.add_option( "-g", "--filename-graph", dest = "filename_graph", type = "string",
                       help="output filename with graph information [default=%default]." )

    parser.set_defaults( min_length = 0,
                         filename_graph = None )

    (options, args) = Experiment.Start( parser, add_csv_options = True )

    # all possible nested models: (complex, simple)
    tests = ( ('none', 'ds'),
              ('none', 'kappa' ),
              ('none', 'omega' ),
              ('none', 'omega-ds' ),
              ('none', 'kappa-ds' ),
              ('omega', 'omega-ds' ),
              ('kappa', 'kappa-ds' ),
              ('ds', 'omega-ds' ),
              ('ds', 'kappa-ds' ),
              ('omega-ds', 'all' ),
              ('kappa-ds', 'all' ),
              ('none', 'all' ), 
              ('kappa', 'all' ),
              ('omega', 'all' ),
              ('ds', 'all'),
              )

    map_model2params = {
        'none' : 8,
        'ds' : 7,
        'omega' : 6,
        'kappa' : 6,
        'omega-ds' : 5,
        'kappa-ds' : 5,
        'all' : 4 }

    reader = CSV.DictReader( sys.stdin,
                             dialect=options.csv_dialect )

    stats = {}
    options.stdout.write( "id" )
    for a, b in tests:
        options.stdout.write( "\t%s:%s\tp%s:%s" % (a, b, a, b))
        stats[(a,b)] = 0

    options.stdout.write( "\n" )

    ninput, noutput, nskipped, nerrors, ntests = 0, 0, 0, 0, 0

    for row in reader:
        ninput += 1

        if int(row['N:len']) <= options.min_length or int(row['C:len']) <= options.min_length :
            nskipped += 1	
            continue

        options.stdout.write( row['id'] )

        for a, b in tests:
            ntests += 1
            lnl_complex = float(row['%s:lnL' % a])
            lnl_simple = float(row['%s:lnL' % b])
            df_complex = map_model2params[a]
            df_simple = map_model2params[b]
            if options.loglevel >= 3:
                options.stdlog.write("# testing %s: ll=%f,df=%i versus %s:lnl=%f,df=%i\n" %\
                                         (a,
                                          lnl_complex,df_complex, 
                                          b, lnl_simple,
                                          df_simple))

            if lnl_complex < lnl_simple:
                nerrors += 1
                options.stdout.write( "\tna\tna" )
                continue

            lrt = Stats.doLogLikelihoodTest( lnl_complex, df_complex, lnl_simple, df_simple )
            if lrt.mPassed: stats[(a,b)] += 1
            
            options.stdout.write( "\t%s\t%5.2e" % (
                    Stats.getSignificance( lrt.mProbability), 
                    lrt.mProbability ) )
            
        options.stdout.write( "\n" )

        noutput += 1

    options.stdout.write( "npassed" )
    for a, b in tests:
        options.stdout.write( "\t%i\t%5.2f" % (stats[(a, b)], 100.0 * stats[(a,b)] / noutput ) )
    options.stdout.write( "\n" )

    if options.filename_graph:
        outfile = open( options.filename_graph, 'w' )
        for a, b in tests:
            outfile.write( "%s\t%s\t%i\t%5.2f\n" % (a, b, stats[(a, b)], 100.0 * stats[(a,b)] / noutput ) )
        outfile.close()

    options.stdout.write( "# ninput=%i, noutput=%i, nskipped=%i, ntests=%i, nerrors=%i\n" % ( ninput, noutput, nskipped, ntests, nerrors))

    Experiment.Stop()
