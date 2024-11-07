from dataclasses import dataclass

import logging

logging.basicConfig(level=logging.INFO,
                    format='{asctime} {levelname} {message}',
                    style='{'
                    )


@dataclass
class DataGalaxyApi:
    url: str
    token: str


@dataclass(frozen=True)
class DataGalaxyBulkResult:
    total: int
    created: int
    deleted: int
    unchanged: int
    updated: int


@dataclass(frozen=True)
class DataGalaxyPathWithType:
    path: str
    path_type: str


PATH_SEPARATOR = "\\"


BULK_PROPERTIES_FIELDS_TO_REMOVE = ['path', 'typePath', 'location', 'attributes', 'objectUrl', 'childrenCount',
                                    'lastModificationTime', 'creationTime']


def del_useless_keys(members: dict):
    for key in list(members.keys()):
        if key in BULK_PROPERTIES_FIELDS_TO_REMOVE:
            del members[key]
        else:
            pass

    return members


def handle_timeserie(property: dict) -> dict:
    # Temporary solution: only copy the latest value of the TimeSerie
    for key, value in property.items():
        if isinstance(value, dict):
            if 'lastEntry' in value and value['lastEntry'] is not None:
                # Expected format : "Date::Value"
                last_entry = value['lastEntry']
                if 'date' in last_entry and 'value' in last_entry:
                    property[key] = f"{last_entry['date']}::{last_entry['value']}"


def remove_technology_code(node):
    if 'technologyCode' in node:
        del node['technologyCode']

    if 'children' in node:
        for child in node['children']:
            remove_technology_code(child)


def build_bulktree(objects):
    root = []  # Root level for all unique trees

    def find_or_create_child(children, path_segment, type_segment, functional_path_segment, attributes, dpis):
        # Look for a child with the same path and type
        for child in children:
            if child['technicalName'] == path_segment and child['type'] == type_segment:
                # If found, update the child with additional attributes directly if they don't already exist
                for key, value in attributes.items():
                    child.setdefault(key, value)
                return child

        # If not found, create a new node and add it to children
        new_child = {
            'name': functional_path_segment,
            'technicalName': path_segment,
            'type': type_segment,
            **attributes,  # Flatten all attribute key-values into this node
            'children': []
        }
        # specific for dataProcessingItems
        if dpis is not None:
            new_child['dataProcessingItems'] = dpis
        children.append(new_child)
        return new_child

    for obj in objects:
        path_segments = obj['path'][1:].split(PATH_SEPARATOR)
        type_segments = obj['typePath'][1:].split(PATH_SEPARATOR)
        functional_path_segments = obj['functionalPath'][1:].split(PATH_SEPARATOR)
        attributes = obj.get('attributes')
        dpis = obj.get('dataProcessingItems')
        handle_timeserie(obj)

        current_level = root  # Start from the root level

        for i, (path_segment, type_segment, functional_path_segment) in enumerate(zip(path_segments, type_segments, functional_path_segments)):
            # Pass attributes only at the right level (the last)
            attributes_to_send = attributes if i == (len(path_segments) - 1) else {}
            # Pass dpis (if exists) only at the right level (the last)
            dpis_to_send = dpis if i == (len(path_segments) - 1) else None
            next_node = find_or_create_child(current_level, path_segment, type_segment, functional_path_segment, attributes_to_send, dpis_to_send)
            current_level = next_node['children']  # Move to the next level of children

    return root


def find_root_objects(objects: list) -> list:
    root_objects = []
    for obj in objects:
        path_segments = obj['path'][1:].split(PATH_SEPARATOR)
        if len(path_segments) == 1:
            root_objects.append(obj)
    return root_objects


def to_bulk_tree(properties: list) -> list:
    if properties is None or len(properties) == 0:
        logging.warn("Cannot bulk upsert an empty list of objects")
        return 0

    nodes_map = {}
    for property in properties:
        nodes_map[DataGalaxyPathWithType(property['path'], property['typePath'])] = property

    for property in properties:

        if 'attributes' in property:
            property.update(property['attributes'])

        path = property['path']
        path_type = property['typePath']
        del_useless_keys(property)
        handle_timeserie(property)

        # TRANSFORM to bulk item
        path_segments = path[1:].split(PATH_SEPARATOR)
        if len(path_segments) > 1:
            parent_path_segments = path_segments[:-1]
            parent_path_type_segments = path_type[1:].split(PATH_SEPARATOR)[:-1]
            parent_path = f"{PATH_SEPARATOR}{PATH_SEPARATOR.join(parent_path_segments)}"
            parent_path_type = f"{PATH_SEPARATOR}{PATH_SEPARATOR.join(parent_path_type_segments)}"
            parent = nodes_map[DataGalaxyPathWithType(parent_path, parent_path_type)]
            if 'children' in parent:
                parent['children'].append(property)
            else:
                parent['children'] = [property]

    root_nodes = []
    for key, value in nodes_map.items():
        if len(key.path[1:].split(PATH_SEPARATOR)) == 1:
            root_nodes.append(value)

    return root_nodes


def prune_tree(tree, target_tag):
    # Function to recursively prune the tree
    def recursive_prune(node):
        if 'children' in node:
            # Recursively prune children
            node['children'] = [child for child in node['children'] if recursive_prune(child)]
            # Keep this node if it has the target tag or any of its children have the tag
            return 'tags' in node and target_tag in node['tags'] or any(recursive_prune(child) for child in node['children'])
        # Keep leaf nodes only if they have the target tag
        return 'tags' in node and target_tag in node['tags']

    # Prune the tree recursively
    pruned_tree = [node for node in tree if recursive_prune(node)]
    return pruned_tree
