import logging
from typing import Optional

from toolbox.api.datagalaxy_api_screens import DataGalaxyApiScreen
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def copy_screens(url_source: str,
                 url_target: Optional[str],
                 token_source: str,
                 token_target: Optional[str],
                 workspace_source_name: Optional[str],
                 workspace_target_name: Optional[str]) -> int:
    if token_target is None:
        token_target = token_source

    if url_target is None:
        url_target = url_source

    if workspace_source_name is None:
        logging.info("copy_screens - No source workspace name given : copying the clientspace's screens")
        source_workspace = None
    else:
        logging.info("copy_screens - Source workspace name given : copying the workspace's screens")
        workspaces_api_on_source_env = DataGalaxyApiWorkspace(
            url=url_source,
            token=token_source
        )
        source_workspace = workspaces_api_on_source_env.get_workspace(workspace_source_name)
        if source_workspace is None:
            raise Exception(f'workspace {workspace_source_name} does not exist')

    if workspace_target_name is None:
        logging.info("copy_screens - No target workspace name given : writing on clientspace's screens")
        target_workspace = None
    else:
        logging.info("copy_screens - Target workspace name given : writing on workspace's screens")
        workspaces_api_on_target_env = DataGalaxyApiWorkspace(
            url=url_target,
            token=token_target
        )
        target_workspace = workspaces_api_on_target_env.get_workspace(workspace_target_name)
        if target_workspace is None:
            raise Exception(f'workspace {workspace_target_name} does not exist')

    source_screens_api = DataGalaxyApiScreen(url=url_source, token=token_source, workspace=source_workspace)
    target_screens_api = DataGalaxyApiScreen(url=url_target, token=token_target, workspace=target_workspace)

    source_screens = source_screens_api.list_screens()
    target_screens = target_screens_api.list_screens()

    if len(source_screens) == 0:
        raise Exception('Unexpected error: source has no screen')

    if len(target_screens) == 0:
        raise Exception('Unexpected error: target has no screen')

    if len(source_screens) != len(target_screens):
        raise Exception('Unexpected error: source and target do not have the same number of screens')

    for source_screen in source_screens:
        flag_to_copy = False
        type = source_screen['type']
        # Unsupported types (API issues somehow)
        if type in ["OpenDataSet", "SubStructure", "UsageComponent", "FreeDiagram", "PhysicalDiagram"]:
            logging.info(f'copy_screens - {type} is currently not supported by the API, aborting this screen')
            continue
        target_screen = None
        # We find the corresponding screen in the target space
        for item in target_screens:
            if item['type'] == type:
                target_screen = item
                break
        # The screen has to exist in the target space
        if target_screen is None:
            raise Exception('Unexpected error: screen not found on target space')
        source_categories = source_screen['categories']
        target_categories = target_screen['categories']
        # If the number of categories is different, an update request must be sent
        if len(source_categories) != len(target_categories):
            logging.info(f'copy_screens - Must sent PUT request for {type} because not the same number of categories')
            flag_to_copy = True
        else:
            categories_comparison = list(zip(source_categories, target_categories))
            for category_comparison in categories_comparison:
                source_category = category_comparison[0]
                target_category = category_comparison[1]
                # If the categories contains differences, an update request must be sent
                equal = check_are_categories_equal(source_category, target_category)
                if equal is False:
                    logging.info(f'copy_screens - Must sent PUT request for {type} because categories are different')
                    flag_to_copy = True
                # If the attributes of the category contains differences, an update request must be sent
                equal = check_are_attributes_equal(source_category['attributes'], target_category['attributes'])
                if equal is False:
                    logging.info(f'copy_screens - Must sent PUT request for {type} because attributes are different')
                    flag_to_copy = True
        # Replacing attributes by attribute names for the (potential) update request and deleting id property for custom attributes
        for index, element in enumerate(source_categories):
            source_categories[index]['attributes'] = [attribute['name'] for attribute in element['attributes'] if 'name' in attribute]
            if 'isSystem' not in element or element['isSystem'] is False:
                del source_categories[index]['id']
        source_screen['categories'] = source_categories

        if flag_to_copy is True:
            logging.info(f'copy_screens - Sending PUT request for {type}')
            target_screens_api.update_screen(source_screen)

    return 0


def check_are_categories_equal(source_category, target_category) -> bool:
    if 'isSystem' not in source_category or source_category['isSystem'] is False:
        # Custom category
        logging.info(f'check_are_categories_equal - Custom category detected : {source_category["name"]}')
        return False
    else:
        # DG standard category
        if source_category['id'] != target_category['id']:
            logging.info(f'check_are_categories_equal - Different id : {source_category["id"]} / {target_category["id"]}')
            return False
        if source_category['name'] != target_category['name']:
            logging.info(f'check_are_categories_equal - Different name : {source_category["name"]} / {target_category["name"]}')
            return False
        if source_category['isHidden'] != target_category['isHidden']:
            logging.info(f'check_are_categories_equal - Different isHidden : {source_category["isHidden"]} / {target_category["isHidden"]}')
            return False
    return True


def check_are_attributes_equal(source_attributes, target_attributes) -> bool:
    if len(source_attributes) != len(target_attributes):
        logging.info(f'check_are_attributes_equal - Not the same number of attributes : source {len(source_attributes)} / target {len(target_attributes)}')
        return False
    attributes_comparison = list(zip(source_attributes, target_attributes))
    for attribute_comparison in attributes_comparison:
        source_attribute = attribute_comparison[0]
        target_attribute = attribute_comparison[1]
        if source_attribute['isCustom'] is True:
            # Custom attribute
            logging.info(f'check_are_attributes_equal - Custom attribute detected ({source_attribute["name"]}), need to update')
            return False
        else:
            # DG standard attribute
            if source_attribute['name'] != target_attribute['name']:
                logging.info(f'check_are_attributes_equal - Different name : {source_attribute["name"]} / {target_attribute["name"]}')
                return False
    return True


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
