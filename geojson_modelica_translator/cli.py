import argparse
import logging
import sys


# Work in progress

def parse_args(args):
    parser = argparse.ArgumentParser(description="Parser")
    parser.set_defaults(log_level=logging.WARNING,
                        extensions=[],
                        command=run)
    opts = vars(parser.parse_args(args))
    return opts


def main(args):
    """Main entry point for external applications

    Args:
        args ([str]): command line arguments
    """
    opts = parse_args(args)
    opts['command'](opts)


def run():
    """Entry point for console script"""
    main(sys.argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
