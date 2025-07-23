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


PATH_SEPARATOR = "\\"


def handle_timeserie(property: dict) -> dict:
    # Temporary solution: only copy the latest value of the TimeSerie
    for key, value in property.items():
        if isinstance(value, dict):
            if 'lastEntry' in value:
                if value['lastEntry'] is None:
                    property[key] = ""
                else:
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
                    handle_timeserie(child)
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
        handle_timeserie(new_child)
        children.append(new_child)
        return new_child

    for obj in objects:
        path_segments = obj['path'][1:].split(PATH_SEPARATOR)
        type_segments = obj['typePath'][1:].split(PATH_SEPARATOR)
        functional_path_segments = obj['functionalPath'][1:].split(PATH_SEPARATOR)
        attributes = obj.get('attributes')
        dpis = obj.get('dataProcessingItems')

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


def create_batches(input_arrays, max_size=5000):
    batches = []  # This will hold the list of arrays
    current_batch = []  # Temporary array to build chunks

    for arr in input_arrays:
        for obj in arr:  # Add each object from the input array
            if len(current_batch) < max_size:
                current_batch.append(obj)
            else:
                # When the current array reaches max size, save it and start a new one
                batches.append(current_batch)
                current_batch = [obj]

    # Add the remaining objects in `current_batch` if it's not empty
    if current_batch:
        batches.append(current_batch)

    return batches


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
