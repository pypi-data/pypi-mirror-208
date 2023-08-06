#! /usr/bin/env python

import argparse
import sys
import logging
import logging.config
import json

from cellmaps_utils import logutils
from cellmaps_utils import constants
import cellmaps_ppidownloader
from cellmaps_ppidownloader.runner import CellmapsPPIDownloader
from cellmaps_ppidownloader.gene import APMSGeneNodeAttributeGenerator

logger = logging.getLogger(__name__)


def _parse_arguments(desc, args):
    """
    Parses command line arguments

    :param desc: description to display on command line
    :type desc: str
    :param args: command line arguments usually :py:func:`sys.argv[1:]`
    :type args: list
    :return: arguments parsed by :py:mod:`argparse`
    :rtype: :py:class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=constants.ArgParseFormatter)
    parser.add_argument('outdir',
                        help='Directory to write results to')
    parser.add_argument('--edgelist',
                        help='APMS edgelist TSV file in format of:\n'
                             'GeneID1\tSymbol1\tGeneID2\tSymbol2\n'
                             '10159\tATP6AP2\t2\tA2M')
    parser.add_argument('--baitlist',
                        help='APMS baitlist TSV file in format of:\n'
                             'GeneSymbol\tGeneID\t# Interactors\n'
                             '"ADA"\t"100"\t1.')
    parser.add_argument('--provenance',
                        help='Path to file containing provenance '
                             'information about input files in JSON format. '
                             'This is required and not including will output '
                             'and error message with example of file')
    parser.add_argument('--logconf', default=None,
                        help='Path to python logging configuration file in '
                             'this format: https://docs.python.org/3/library/'
                             'logging.config.html#logging-config-fileformat '
                             'Setting this overrides -v parameter which uses '
                             ' default logger. (default None)')
    parser.add_argument('--skip_logging', action='store_true',
                        help='If set, output.log, error.log and '
                             'task_#_start/finish.json '
                             'files will not be created')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increases verbosity of logger to standard '
                             'error for log messages in this module. Messages are '
                             'output at these python logging levels '
                             '-v = ERROR, -vv = WARNING, -vvv = INFO, '
                             '-vvvv = DEBUG, -vvvvv = NOTSET (default no '
                             'logging)')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' +
                                 cellmaps_ppidownloader.__version__))

    return parser.parse_args(args)


def main(args):
    """
    Main entry point for program

    :param args: arguments passed to command line usually :py:func:`sys.argv[1:]`
    :type args: list

    :return: return value of :py:meth:`cellmaps_ppidownloader.runner.CellmapsPPIDownloader.run`
             or ``2`` if an exception is raised
    :rtype: int
    """
    withguids_json = json.dumps(CellmapsPPIDownloader.get_example_provenance(with_ids=True), indent=2)
    register_json = json.dumps(CellmapsPPIDownloader.get_example_provenance(), indent=2)

    desc = """
Version {version}

Loads APMS data specified by --edgelist and --baitlist flags

To use pass in a TSV edgelist file to --edgelist

Format of TSV file:

TODO

The --baitlist flag should be given a TSV file containing APMS baits 
 

Format of TSV file:

TODO

In addition, the --provenance flag is required and must be set to a path 
to a JSON file. 

If datasets are already registered with FAIRSCAPE then the following is sufficient:

{withguids}

If datasets are NOT registered, then the following is required:

{register}

Additional optional fields for registering datasets include 
'url', 'used-by', 'associated-publication', and 'additional-documentation'
    

    """.format(version=cellmaps_ppidownloader.__version__,
               withguids=withguids_json,
               register=register_json)
    theargs = _parse_arguments(desc, args[1:])
    theargs.program = args[0]
    theargs.version = cellmaps_ppidownloader.__version__

    try:
        logutils.setup_cmd_logging(theargs)
        if theargs.provenance is None:
            sys.stderr.write('\n\n--provenance flag is required to run this tool. '
                             'Please pass '
                             'a path to a JSON file with the following data:\n\n')
            sys.stderr.write('If datasets are already registered with '
                             'FAIRSCAPE then the following is sufficient:\n\n')
            sys.stderr.write(withguids_json + '\n\n')
            sys.stderr.write('If datasets are NOT registered, then the following is required:\n\n')
            sys.stderr.write(register_json + '\n\n')
            return 1

        # load the provenance as a dict
        with open(theargs.provenance, 'r') as f:
            json_prov = json.load(f)

        apmsgen = APMSGeneNodeAttributeGenerator(
            apms_edgelist=APMSGeneNodeAttributeGenerator.get_apms_edgelist_from_tsvfile(theargs.edgelist),
            apms_baitlist=APMSGeneNodeAttributeGenerator.get_apms_baitlist_from_tsvfile(theargs.baitlist))

        return CellmapsPPIDownloader(outdir=theargs.outdir,
                                     apmsgen=apmsgen,
                                     skip_logging=theargs.skip_logging,
                                     input_data_dict=theargs.__dict__,
                                     provenance=json_prov).run()
    except Exception as e:
        logger.exception('Caught exception: ' + str(e))
        return 2
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
