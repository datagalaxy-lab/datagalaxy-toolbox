import argparse
import logging
import sys

from toolbox.api.http_client import HttpClient
from toolbox.commands.copy_attributes import copy_attributes_parse, copy_attributes
from toolbox.commands.copy_technologies import copy_technologies_parse, copy_technologies
from toolbox.commands.copy_screens import copy_screens_parse, copy_screens
from toolbox.commands.delete_attributes import delete_attributes_parse, delete_attributes
from toolbox.commands.copy_module import copy_module, copy_glossary_parse, copy_dictionary_parse, copy_dataprocessings_parse, copy_usages_parse
from toolbox.commands.copy_links import copy_links, copy_links_parse
from toolbox.commands.delete_module import delete_module, delete_glossary_parse, delete_dictionary_parse, delete_dataprocessings_parse, delete_usages_parse


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
    parser.add_argument("--no-verify-ssl", help="disable SSL certificate verification for HTTPS requests",
                        action="store_true")
    subparsers = parser.add_subparsers(help='sub-command help', dest='subparsers_name')
    # Clientspace
    copy_attributes_parse(subparsers)
    copy_technologies_parse(subparsers)
    copy_screens_parse(subparsers)
    delete_attributes_parse(subparsers)
    # Copy modules
    copy_glossary_parse(subparsers)
    copy_dictionary_parse(subparsers)
    copy_dataprocessings_parse(subparsers)
    copy_usages_parse(subparsers)
    copy_links_parse(subparsers)
    # Delete modules
    delete_glossary_parse(subparsers)
    delete_dictionary_parse(subparsers)
    delete_dataprocessings_parse(subparsers)
    delete_usages_parse(subparsers)

    # parse some argument lists
    result = parser.parse_args(args)
    if result.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Verbose output")

    # Create HTTP client with SSL verification setting
    verify_ssl = not result.no_verify_ssl
    http_client = HttpClient(verify_ssl=verify_ssl)

    # Config

    if result.subparsers_name == 'copy-attributes':
        logging.info(">>> copy_attributes")
        copy_attributes(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            http_client
        )
        logging.info("<<< copy_attributes")
        return 0

    if result.subparsers_name == 'copy-technologies':
        logging.info(">>> copy_technologies")
        copy_technologies(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            http_client
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
            result.workspace_target,
            http_client
        )
        logging.info("<<< copy_screens")
        return 0

    if result.subparsers_name == 'delete-attributes':
        logging.info(">>> delete_attributes")
        delete_attributes(
            result.url,
            result.token,
            http_client
        )
        logging.info("<<< delete_attributes")
        return 0

    # Copy modules
    if result.subparsers_name == 'copy-glossary':
        logging.info(">>> copy_glossary")
        copy_module(
            "Glossary",
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.version_source,
            result.workspace_target,
            result.version_target,
            result.tag_value,
            http_client
        )
        logging.info("<<< copy_glossary")
        return 0

    if result.subparsers_name == 'copy-dictionary':
        logging.info(">>> copy_dictionary")
        copy_module(
            "Dictionary",
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.version_source,
            result.workspace_target,
            result.version_target,
            result.tag_value,
            http_client
        )
        logging.info("<<< copy_dictionary")
        return 0

    if result.subparsers_name == 'copy-dataprocessings':
        logging.info(">>> copy_dataprocessings")
        copy_module(
            "DataProcessing",
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.version_source,
            result.workspace_target,
            result.version_target,
            result.tag_value,
            http_client
        )
        logging.info("<<< copy_dataprocessings")
        return 0

    if result.subparsers_name == 'copy-usages':
        logging.info(">>> copy_usages")
        copy_module(
            "Uses",
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.version_source,
            result.workspace_target,
            result.version_target,
            result.tag_value,
            http_client
        )
        logging.info("<<< copy_usages")
        return 0

    if result.subparsers_name == 'copy-links':
        logging.info(">>> copy_links")
        copy_links(
            result.url_source,
            result.url_target,
            result.token_source,
            result.token_target,
            result.workspace_source,
            result.version_source,
            result.workspace_target,
            result.version_target,
            http_client
        )
        logging.info("<<< copy_links")
        return 0

    # Delete modules
    if result.subparsers_name == 'delete-glossary':
        logging.info(">>> delete_glossary")
        delete_module(
            "Glossary",
            result.url,
            result.token,
            result.workspace,
            result.version,
            http_client
        )
        logging.info("<<< delete_glossary")
        return 0

    if result.subparsers_name == 'delete-dictionary':
        logging.info(">>> delete_dictionary")
        delete_module(
            "Dictionary",
            result.url,
            result.token,
            result.workspace,
            result.version,
            http_client
        )
        logging.info("<<< delete_dictionary")
        return 0

    if result.subparsers_name == 'delete-dataprocessings':
        logging.info(">>> delete_dataprocessings")
        delete_module(
            "DataProcessing",
            result.url,
            result.token,
            result.workspace,
            result.version,
            http_client
        )
        logging.info("<<< delete_dataprocessings")
        return 0

    if result.subparsers_name == 'delete-usages':
        logging.info(">>> delete_usages")
        delete_module(
            "Uses",
            result.url,
            result.token,
            result.workspace,
            result.version,
            http_client
        )
        logging.info("<<< delete_usages")
        return 0

    parser.print_help(sys.stderr)
    return 1


if __name__ == '__main__':
    code = run(sys.argv[1:])
    sys.exit(code)
