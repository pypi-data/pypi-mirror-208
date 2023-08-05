from ._version import __version__
from . import secmarker_lib

def run_secmarker():
    parser = secmarker_lib.get_parser()
    args = parser.parse_args()
    secmarker_lib.main(args)

