from pureml.utils.config import load_config
from collections import OrderedDict
import json
import time


def create_nodes(components):
    # print(components)

    nodes = [
        {
            "id": component["name"],
            "text": component["name"],
            "nodeType": component["type"],
            "desc": str(component["desc"]),
            "time": str(component["time"]),
        }
        for component in components
    ]

    return nodes


def create_extra_nodes(nodes, edges):
    # print(components)

    node_nodes = [i["id"] for i in nodes]
    edge_nodes = sum([[i["from"]] + [i["to"]] for i in edges], [])

    extra_nodes = list(set([n for n in edge_nodes if n not in node_nodes]))

    nodes = nodes + [
        {
            "id": n,
            "text": n,
            "nodeType": "unknown",
            "desc": str(None),
            "time": str(time.time()),
        }
        for n in extra_nodes
    ]

    return nodes


def create_edges(components):

    edges = []

    def add_node(node_from, node_to):
        edge_id = "--->".join([node_from, node_to])
        edge = {"id": edge_id, "from": node_from, "to": node_to}

        edges.append(edge)

    for n in components:
        if "parent" in n.keys():
            node_parent = n["parent"]
            node_to = n["name"]

            if node_parent is not None:

                if type(node_parent) == list:

                    for node_from in node_parent:
                        add_node(node_from, node_to)

                else:
                    add_node(node_parent, node_to)

    return edges


def prune_dict_elements(components):
    components_string = [json.dumps(d) for d in components]

    components_string = set(components_string)

    components_loaded = [json.loads(d) for d in components_string]

    return components_loaded


def create_lineage():
    config = load_config()

    load_data = config["load_data"]
    transformer = list(config["transformer"].values())
    dataset = config["dataset"]

    lineage_components = []

    if len(load_data) > 0:
        lineage_components.append(load_data)

    if len(transformer) > 0:
        lineage_components = lineage_components + transformer

    if len(dataset) > 0:
        lineage_components.append(dataset)

    lineage_components = prune_dict_elements(lineage_components)

    edges = create_edges(components=lineage_components)
    edges = prune_dict_elements(edges)

    nodes = create_nodes(components=lineage_components)
    nodes = create_extra_nodes(nodes, edges)
    nodes = prune_dict_elements(nodes)

    lineage = {"edges": edges, "nodes": nodes}

    return lineage


# const nodes = [
#   {
#     id: '1',
#     text: '1'
#   },
#   {
#     id: '2',
#     text: '2'
#   }
# ];

# const edges = [
#   {
#     id: '1-2',
#     from: '1',
#     to: '2'
#   }
# ];
