import argparse
import logging
import sys

from toolbox.commands.copy_attributes import copy_attributes_parse, copy_attributes
from toolbox.commands.copy_usages import copy_usages, copy_usages_parse
from toolbox.commands.delete_attributes import delete_attributes_parse, delete_attributes
from toolbox.commands.copy_glossary import copy_glossary_parse, copy_glossary
from toolbox.commands.copy_dictionary import copy_dictionary, copy_dictionary_parse


def run(args):
    """
    Run a command from a list of arguments.

    :param: a list of arguments
    :return: an exit code (0 = successful, 1 = error)
    """
    # create the top-level parser
    parser = argparse.ArgumentParser(description='Toolbox')
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    subparsers = parser.add_subparsers(help='sub-command help', dest='subparsers_name')
    copy_attributes_parse(subparsers)
    delete_attributes_parse(subparsers)
    copy_glossary_parse(subparsers)
    copy_usages_parse(subparsers)
    copy_dictionary_parse(subparsers)
    # parse some argument lists
    result = parser.parse_args(args)
    if result.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Verbose output")

    if result.subparsers_name == 'copy-attributes':
        logging.info(">>> copy_attributes")
        copy_attributes(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target
        )
        logging.info("<<< copy_attributes")
        return 0

    if result.subparsers_name == 'delete-attributes':
        logging.info(">>> delete_attributes")
        delete_attributes(result.url, result.token)
        logging.info("<<< delete_attributes")
        return 0

    if result.subparsers_name == 'copy-glossary':
        logging.info(">>> copy_glossary")
        copy_glossary(result.url_source, result.url_target, result.token_source, result.token_target,
                      result.workspace_source, result.workspace_target)
        logging.info("<<< copy_glossary")
        return 0

    if result.subparsers_name == 'copy-usages':
        logging.info(">>> copy_usages")
        copy_usages(result.url_source, result.url_target, result.token_source, result.token_target,
                    result.workspace_source, result.workspace_target)
        logging.info("<<< copy_usages")
        return 0

    if result.subparsers_name == 'copy-dictionary':
        logging.info(">>> copy_dictionary")
        copy_dictionary(result.url_source, result.url_target, result.token_source, result.token_target,
                        result.workspace_source, result.workspace_target)
        logging.info("<<< copy_dictionary")
        return 0

    parser.print_help(sys.stderr)
    return 1


if __name__ == '__main__':
    code = run(sys.argv[1:])
    sys.exit(code)
