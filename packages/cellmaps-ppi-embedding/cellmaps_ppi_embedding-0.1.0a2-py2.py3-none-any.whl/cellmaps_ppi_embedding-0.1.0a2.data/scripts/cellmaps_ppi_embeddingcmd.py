#!python

import argparse
import sys
import logging
import logging.config
import networkx as nx
from cellmaps_utils import logutils
import cellmaps_ppi_embedding
from cellmaps_ppi_embedding.runner import Node2VecEmbeddingGenerator
from cellmaps_ppi_embedding.runner import CellMapsPPIEmbedder

logger = logging.getLogger(__name__)


LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"


class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                argparse.RawDescriptionHelpFormatter):
    """
    Combine two Formatters to get help and default values
    displayed when showing help

    """
    pass


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
                                     formatter_class=Formatter)
    parser.add_argument('outdir', help='Output directory')
    parser.add_argument('--inputdir', required=True,
                        help='Directory where apms_edgelist.tsv file resides')
    parser.add_argument('--dimensions', type=int, default=1024,
                        help='Size of embedding to generate')
    parser.add_argument('--walk_length', type=int, default=80,
                        help='Walk Length')
    parser.add_argument('--num_walks', type=int, default=10,
                        help='Num walks')
    parser.add_argument('--workers', type=int, default=8,
                        help='Number of workers')
    parser.add_argument('--p', type=int, default=2,
                        help='--p value to pass to node2vec')
    parser.add_argument('--q', type=int, default=1,
                        help='--q value to pass to node2vec')
    parser.add_argument('--skip_logging', action='store_true',
                        help='If set, output.log, error.log and '
                             'task_#_start/finish.json '
                             'files will not be created')
    parser.add_argument('--logconf', default=None,
                        help='Path to python logging configuration file in '
                             'this format: https://docs.python.org/3/library/'
                             'logging.config.html#logging-config-fileformat '
                             'Setting this overrides -v parameter which uses '
                             ' default logger. (default None)')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increases verbosity of logger to standard '
                             'error for log messages in this module. Messages are '
                             'output at these python logging levels '
                             '-v = ERROR, -vv = WARNING, -vvv = INFO, '
                             '-vvvv = DEBUG, -vvvvv = NOTSET (default no '
                             'logging)')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' +
                                 cellmaps_ppi_embedding.__version__))

    return parser.parse_args(args)


def main(args):
    """
    Main entry point for program

    :param args: arguments passed to command line usually :py:func:`sys.argv[1:]`
    :type args: list

    :return: return value of :py:meth:`cellmaps_ppi_embedding.runner.CellMapsPPIEmbedder.run`
             or ``2`` if an exception is raised
    :rtype: int
    """
    desc = """
    Version {version}

    Invokes run() method on CellMapsPPIEmbedder

    """.format(version=cellmaps_ppi_embedding.__version__)
    theargs = _parse_arguments(desc, args[1:])
    theargs.program = args[0]
    theargs.version = cellmaps_ppi_embedding.__version__

    try:
        logutils.setup_cmd_logging(theargs)

        gen = Node2VecEmbeddingGenerator(nx_network=nx.read_edgelist(CellMapsPPIEmbedder.get_apms_edgelist_file(theargs.inputdir),
                                                                     delimiter='\t'),
                                         dimensions=theargs.dimensions,
                                         p=theargs.p,
                                         q=theargs.q,
                                         walk_length=theargs.walk_length,
                                         num_walks=theargs.num_walks,
                                         workers=theargs.workers)

        return CellMapsPPIEmbedder(outdir=theargs.outdir,
                                   embedding_generator=gen,
                                   skip_logging=theargs.skip_logging,
                                   inputdir=theargs.inputdir,
                                   input_data_dict=theargs.__dict__).run()
    except Exception as e:
        logger.exception('Caught exception: ' + str(e))
        return 2
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
