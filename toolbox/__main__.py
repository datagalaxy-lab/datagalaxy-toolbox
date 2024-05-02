import argparse
import logging
import sys

from toolbox.commands.copy_attributes import copy_attributes_parse, copy_attributes
from toolbox.commands.copy_technologies import copy_technologies_parse, copy_technologies
from toolbox.commands.copy_screens import copy_screens_parse, copy_screens
from toolbox.commands.copy_usages import copy_usages, copy_usages_parse
from toolbox.commands.delete_usages import delete_usages_parse, delete_usages
from toolbox.commands.copy_dataprocessings import copy_dataprocessings, copy_dataprocessings_parse
from toolbox.commands.delete_dataprocessings import delete_dataprocessings, delete_dataprocessings_parse
from toolbox.commands.delete_attributes import delete_attributes_parse, delete_attributes
from toolbox.commands.copy_glossary import copy_glossary_parse, copy_glossary
from toolbox.commands.delete_glossary import delete_glossary_parse, delete_glossary
from toolbox.commands.copy_dictionary import copy_dictionary, copy_dictionary_parse
from toolbox.commands.delete_dictionary import delete_dictionary, delete_dictionary_parse
from toolbox.commands.copy_links import copy_links, copy_links_parse


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
    copy_technologies_parse(subparsers)
    copy_screens_parse(subparsers)
    delete_attributes_parse(subparsers)
    copy_glossary_parse(subparsers)
    delete_glossary_parse(subparsers)
    copy_usages_parse(subparsers)
    delete_usages_parse(subparsers)
    copy_dictionary_parse(subparsers)
    delete_dictionary_parse(subparsers)
    copy_dataprocessings_parse(subparsers)
    delete_dataprocessings_parse(subparsers)
    copy_links_parse(subparsers)
    # parse some argument lists
    result = parser.parse_args(args)
    if result.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Verbose output")

    # Config

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

    if result.subparsers_name == 'copy-technologies':
        logging.info(">>> copy_technologies")
        copy_technologies(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target
        )
        logging.info("<<< copy_technologies")
        return 0

    if result.subparsers_name == 'copy-screens':
        logging.info(">>> copy_screens")
        copy_screens(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.workspace_target
        )
        logging.info("<<< copy_screens")
        return 0

    if result.subparsers_name == 'delete-attributes':
        logging.info(">>> delete_attributes")
        delete_attributes(
            result.url,
            result.token
        )
        logging.info("<<< delete_attributes")
        return 0

    # Modules

    if result.subparsers_name == 'copy-glossary':
        logging.info(">>> copy_glossary")
        copy_glossary(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.workspace_target,
            result.tag_value
        )
        logging.info("<<< copy_glossary")
        return 0

    if result.subparsers_name == 'delete-glossary':
        logging.info(">>> delete_glossary")
        delete_glossary(result.url, result.token, result.workspace)
        logging.info("<<< delete_glossary")
        return 0

    if result.subparsers_name == 'copy-usages':
        logging.info(">>> copy_usages")
        copy_usages(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.workspace_target,
            result.tag_value
        )
        logging.info("<<< copy_usages")
        return 0

    if result.subparsers_name == 'delete-usages':
        logging.info(">>> delete_usages")
        delete_usages(result.url, result.token, result.workspace)
        logging.info("<<< delete_usages")
        return 0

    if result.subparsers_name == 'copy-dictionary':
        logging.info(">>> copy_dictionary")
        copy_dictionary(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.workspace_target,
            result.tag_value
        )
        logging.info("<<< copy_dictionary")
        return 0

    if result.subparsers_name == 'delete-dictionary':
        logging.info(">>> delete_dictionary")
        delete_dictionary(result.url, result.token, result.workspace)
        logging.info("<<< delete_dictionary")
        return 0

    if result.subparsers_name == 'copy-dataprocessings':
        logging.info(">>> copy_dataprocessings")
        copy_dataprocessings(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.workspace_target,
            result.tag_value
        )
        logging.info("<<< copy_dataprocessings")
        return 0

    if result.subparsers_name == 'delete-dataprocessings':
        logging.info(">>> delete_dataprocessings")
        delete_dataprocessings(result.url, result.token, result.workspace)
        logging.info("<<< delete_dataprocessings")
        return 0

    if result.subparsers_name == 'copy-links':
        logging.info(">>> copy_links")
        copy_links(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.workspace_target
        )
        logging.info("<<< copy_links")
        return 0

    parser.print_help(sys.stderr)
    return 1


if __name__ == '__main__':
    code = run(sys.argv[1:])
    sys.exit(code)
