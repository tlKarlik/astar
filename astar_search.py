import logging
from typing import TypeVar, Dict, Any

from graph import Graph, Node, testMap2
from path import Path

Int_or_Float = TypeVar('Int_or_Float', int, float)

logging.basicConfig(
    filename='output/logging.info',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def aStar(work_graph: Graph) -> Dict:
    """Searches for the shortest path from start to goal."""
    # Set current level to infinity and other counters
    # TODO: add more data to track
    active_paths = {}
    data_dict = {
        'source_path_id': None,
        'work_graph': work_graph,
        'active_paths': active_paths,
        'best_path': Path([], float('inf')),
        'iterations_counter': 0,
        'output_data': []
    }

    # Get the updated path
    node_to_expand = work_graph.getNode(work_graph.start)
    new_path = Path([node_to_expand])
    active_paths[0] = new_path
    data_dict['source_path_id'] = 0

    # Run the iterator
    while node_to_expand is not None:
        data_dict['iterations_counter'] += 1
        data_dict['output_data'].append("----------------------------------------------")
        logging.info("ITERATION {}".format(data_dict['iterations_counter']))
        data_dict['output_data'].append("ITERATION {}".format(data_dict['iterations_counter']))
        node_to_expand = _pathIterate(node_to_expand, data_dict)

    data_dict['output_data'].append("")
    logging.info("The path-finding was successfully completed")
    data_dict['output_data'].append("The path-finding was successfully completed")
    data_dict['output_data'].append("----------------------------------------------")
    data_dict['output_data'].append("")
    logging.info("The fastest path from {} to {} is through the {}".format(
        work_graph.nodes[work_graph.start],
        work_graph.nodes[work_graph.goal],
        data_dict['best_path']
    ))
    data_dict['output_data'].append("The fastest path from {} to {} is through the {}".format(
        work_graph.nodes[work_graph.start],
        work_graph.nodes[work_graph.goal],
        data_dict['best_path']
    ))
    # Return the generated data
    return data_dict


def _pathIterate(source_node: Node, data_dict: Dict[str, Any]):
    """Searches through nodes and creates paths."""
    # 1) Frequently accessed data
    source_path_id = data_dict['source_path_id']
    work_graph = data_dict['work_graph']
    active_paths = data_dict['active_paths']
    output_data = data_dict['output_data']

    output_data.append('There are currently {} active paths'.format(
        len([path for path in active_paths if active_paths[path].enabled])))
    output_data.append('The current tested path is {}'.format(active_paths[source_path_id]))
    output_data.append("Coming from {}".format(source_node))

    # 2) Get all links from source node
    links = work_graph.getLinks(source_node.pos)
    for link in links:
        # A) Get the linked node
        linked_node_pos = link
        link_length = links[link]
        linked_node = work_graph.getNode(linked_node_pos)
        output_data.append('    Now testing a link to {} of length {}'.format(linked_node, link_length))

        # B) If the linked node has already been visited in this path, skip this link and continue with the next
        if linked_node in active_paths[source_path_id]:
            output_data.append("        but it has already been visited in this path and thus will be skipped")
            continue

        # C) Get the complete path from start to the linked node and its weight
        new_path = active_paths[source_path_id] + Path([linked_node], link_length)

        # D) If the new path's length matches or exceeds the length of the current best path to the goal, skip this link
        new_best_length = data_dict['best_path'].length
        if new_path.length >= new_best_length:
            output_data.append("        This path's length is longer than the best path to the goal ({} >= {}) and it"
                               " will be skipped".format(new_path.length, new_best_length))
            continue

        # E) If the linked node is the goal node, update it (the path will always be shorter than  the current best
        # path to the goal, because the longer and equal ones are skipped in the condition above).
        # Also, if the best path changed, check all active paths and disable all that have longer length than
        # the new best goal path. Lastly, disable the new goal path.
        if linked_node_pos == work_graph.goal:
            new_path = goalNodeUpdate(new_path, data_dict)

        # F) If there's any path, active or disabled, that leads to the same node, compare their lengths
        # and disable the longer path.
        best_length = new_path.length
        for path_id in [path_id for path_id in active_paths if active_paths[path_id].last_node == linked_node]:
            # Iterate over the all paths, which have the same ending node as the new path, i.e. the linked node
            best_length = sameNodeCompare(best_length, new_path, path_id, active_paths, linked_node, data_dict)

        # G) Finally, add the new path to active paths
        index = len(active_paths)
        active_paths[index] = new_path
        output_data.append("        {} has been added to the active paths".format(new_path))

    # 3) Disable the fully expanded path
    output_data.append("{} has been fully expanded and thus it has been disabled".format(
        active_paths[source_path_id]))
    active_paths[source_path_id].enabled = False

    # 4) Pick next path to be expanded to be the lowest weighted one from the active path
    enabled_active_paths = {
        active_path: active_paths[active_path] for active_path in active_paths if active_paths[active_path].enabled
    }
    try:
        best_weighted_path_id = min(enabled_active_paths, key=lambda i: enabled_active_paths[i].weight)
    except ValueError:  # ValueError if the active paths don't have any active path
        # Here is the escape condition - if there are no active paths it means that the latest best path is
        # ultimately the best (if it exists).
        # Return None instead of next node to signal the iteration to stop.
        return None
    try:
        output_data.append("The current best path to the goal is {}".format(data_dict['best_path']))
    except IndexError:
        output_data.append("There is no known path to the goal")
    next_node_to_expand = active_paths[best_weighted_path_id].last_node
    data_dict['source_path_id'] = best_weighted_path_id

    # 5) Return the next node to expand
    # return pathIterate(next_node_to_expand, data_dict)
    return next_node_to_expand


def goalNodeUpdate(new_path: Path, data_dict: Dict[str, Any]) -> Path:
    """Update the best goal path and disable all active paths that are longer than the new best goal path."""
    data_dict['output_data'].append("        AND IT IS THE GOAL!")
    active_paths = data_dict['active_paths']
    # Update the best goal path
    data_dict['best_path'] = new_path
    new_best_length = data_dict['best_path'].weight
    # Check all the active paths to weed out the too long ones
    for path_id in [path_id for path_id in active_paths if active_paths[path_id].enabled]:
        path_length = active_paths[path_id].length
        if path_length > new_best_length:
            data_dict['output_data'].appendinfo("        {} has been disabled because it's longer than the new"
                                                " best path to the goal ({} > {})".format(active_paths[path_id],
                                                                                          path_length, new_best_length))
            active_paths[path_id].enabled = False
    # Disable the new goal path to avoid expanding it in future iterations
    data_dict['output_data'].append("        the new path to the goal has been disabled to avoid "
                                    "expanding it in future iterations")
    new_path.enabled = False
    return new_path


def sameNodeCompare(best_length: Int_or_Float, new_path: Path, path_id: int, active_paths: Dict[int, Path],
                    linked_node: Node, data_dict: Dict) -> Int_or_Float:
    """Compare the path with the same ending node to the current shortest path to that node and pick the shorter."""
    path_length = active_paths[path_id].length
    if path_length > best_length:
        data_dict['output_data'].append("        {} has been disabled because this path gets to "
                                        "the {} node faster".format(active_paths[path_id], linked_node.name))
        active_paths[path_id].enabled = False
    else:
        data_dict['output_data'].append("        this path has been disabled because {} gets to "
                                        "the {} node faster".format(active_paths[path_id], linked_node.name))
        new_path.enabled = False
        best_length = path_length
    return best_length


'''
def getPathsWeights(path: Path, active_paths: Dict[Path, Path]) -> Int_or_Float:
    """
    :type path: Path
    :type active_paths: dict
    :rtype: int or float
    """
    if not active_paths[path].enabled:
        return float('inf')
    return active_paths[path].weight
'''

if __name__ == '__main__':
    # work_graph = graph.testMap()
    work_graph = testMap2()
    # print work_graph.getLinks(pos=graph.Pos(0, 0))
    data = aStar(work_graph)
    # start_pos = work_graph.start
    # start_node = work_graph.nodes[start_pos]
    # test_path = Path([start_node])
    # print test_path
