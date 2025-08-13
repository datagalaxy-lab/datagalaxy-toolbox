import logging
from typing import Optional

from toolbox.api.datagalaxy_api_screens import DataGalaxyApiScreen
from toolbox.api.http_client import HttpClient
from toolbox.commands.utils import config_workspace


def copy_screens(url_source: str,
                 url_target: Optional[str],
                 token_source: str,
                 token_target: Optional[str],
                 workspace_source_name: Optional[str],
                 workspace_target_name: Optional[str],
                 http_client: HttpClient) -> int:
    if token_target is None:
        token_target = token_source

    if url_target is None:
        url_target = url_source

    if workspace_source_name is None:
        # Source clientspace
        logging.info("copy_screens - No source workspace name given, will copy screens at the clientspace level")
        source_workspace = None
    else:
        # Source workspace
        logging.info("copy_screens - Source workspace name given, will copy screens at the workspace level")
        source_workspace = config_workspace(
            mode="source",
            url=url_source,
            token=token_source,
            workspace_name=workspace_source_name,
            version_name=None,
            http_client=http_client
        )
        if not source_workspace:
            return 1

    if workspace_target_name is None:
        logging.info("copy_screens - No target workspace name given, will edit screens at the clientspace level")
        target_workspace = None
    else:
        logging.info("copy_screens - Target workspace name given, will edit screens at the workspace level")
        target_workspace = config_workspace(
            mode="target",
            url=url_target,
            token=token_target,
            workspace_name=workspace_target_name,
            version_name=None,
            http_client=http_client
        )
        if not target_workspace:
            return 1

    source_screens_api = DataGalaxyApiScreen(url=url_source, token=token_source, workspace=source_workspace, http_client=http_client)
    target_screens_api = DataGalaxyApiScreen(url=url_target, token=token_target, workspace=target_workspace, http_client=http_client)

    source_screens = source_screens_api.list_screens()
    # target_screens = target_screens_api.list_screens()

    if len(source_screens) == 0:
        raise Exception('Unexpected error: source has no screen')

    for source_screen in source_screens:
        data_type = source_screen.get('dataType')  # example: "property"
        entity_type = source_screen.get('type')  # example: "dimension"
        if data_type is None or entity_type is None:
            continue
        new_categories = []
        for category in source_screen['categories']:
            new_category = {
                    'name': category['name'],
                    'isHidden': category['isHidden'],
                    'attributes': [attribute['name'] for attribute in category['attributes'] if 'name' in attribute]
                }
            if 'isSystem' in category and category['isSystem'] is True:
                new_category['id'] = category['id']
            new_categories.append(new_category)
        if entity_type == "OpenDataSet":
            # temporary to avoid an API error
            continue
        target_screens_api.update_screen(data_type=data_type, entity_type=entity_type, categories=new_categories)

    return 0


def copy_screens_parse(subparsers):
    # create the parser for the "copy-screens" command
    copy_screens_parse = subparsers.add_parser('copy-screens', help='copy-screens help')
    copy_screens_parse.add_argument(
        '--url-source',
        type=str,
        help='url source',
        required=True)
    copy_screens_parse.add_argument(
        '--url-target',
        type=str,
        help='url target',
        required=False)
    copy_screens_parse.add_argument(
        '--token-source',
        type=str,
        help='source token',
        required=True)
    copy_screens_parse.add_argument(
        '--token-target',
        type=str,
        help='target token',
        required=False)
    copy_screens_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=False)
    copy_screens_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=False)
