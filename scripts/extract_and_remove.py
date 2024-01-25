import graphviz as gv
import re as re
from collections import defaultdict
import pydot

def extract_and_remove(**kwargs):
    extract = kwargs.get('extract')
    remove = kwargs.get('remove')
    view = kwargs.get('view', False)
    graphs = pydot.graph_from_dot_file(kwargs.get('input'))
    name = kwargs.get('name')
    graph = graphs[0]

    cmd_dict = {}
    next_list = []
    tree_dict = defaultdict(list)
    remove_dict = {}
    remove_dict[name] = 1
    
    extract_graph = pydot.Dot(extract, graph_type='digraph', strict=True) 
    remove_graph = pydot.Dot(remove, graph_type='digraph', strict=True) 
    extract_graph_added = {}
    remove_graph_added = {}

    for edge in graph.get_edges():
        s1 = edge.get_source()
        s2 = edge.get_destination()
        tree_dict[s1].append(s2)
        name1 = re.findall('"([^"]*)"', str(s1))
        name2 = re.findall('"([^"]*)"', str(s2))
        if ((len(name1)>0 and name==name1[0])):
            remove_dict[name2[0]] = 1
        if ((len(name2)>0 and name==name2[0])):
            remove_dict[name1[0]] = 1

    #for node in graph.get_nodes():
    #    s1 = node.get_name()
    #    if (s1.replace('"', '') in remove_dict):
    #        extract_graph.add_node(node)
    #    else:
    #        remove_graph.add_node(node)

    for key, next_list in tree_dict.items():
        while (len(next_list) > 0):
            item = next_list.pop()
        
            n1 = graph.get_node(item)[0]
            n2 = graph.get_node(key)[0]
            e = pydot.Edge(key, item)
            name1 = re.findall('"([^"]*)"', str(n1))
            name2 = re.findall('"([^"]*)"', str(n2))
            if ((len(name1)>0 and name==name1[0]) or (len(name2)>0 and name==name2[0])):
                if str(n1) not in extract_graph_added:
                    extract_graph.add_node(n1) 
                    extract_graph_added[str(n1)] = 1
                if str(n2) not in extract_graph_added:
                    extract_graph.add_node(n2)
                    extract_graph_added[str(n2)] = 1
                extract_graph.add_edge(e)
            else:
                if str(n1) not in remove_graph_added:
                    remove_graph.add_node(n1) 
                    remove_graph_added[str(n1)] = 1
                if str(n2) not in remove_graph_added:
                    remove_graph.add_node(n2)
                    remove_graph_added[str(n2)] = 1
                remove_graph.add_edge(e)

    with open(extract, 'w') as file:
        file.write(str(extract_graph))
    if view:
        extract_graph.view()

    with open(remove, 'w') as file:
        file.write(str(remove_graph))
    if view:
        remove_graph.view()

import argparse

DESC = "Extract a section of dot graph and remove it from the original graph."
PARSER = argparse.ArgumentParser(description=DESC)
PARSER.add_argument(dest='input', help="input DOT file")
PARSER.add_argument('--extract', '-e', dest='extract', help="extract graph output file name.")
PARSER.add_argument('--remove', '-r', dest='remove', help="remove graph output file name.")
PARSER.add_argument('--name', '-n', dest='name', help='The node name to extract')

PARSER.add_argument('--direction', '-d', dest='direction', default="BT",
                            help="direction to draw graph ('BT', 'TB', 'LR', or 'RL')")
PARSER.add_argument('--view', '-v', action='store_true',
                            help="view the graph (disables output to stdout)")



ARGS = PARSER.parse_args()

extract_and_remove(input=ARGS.input, direction=ARGS.direction, extract=ARGS.extract, remove=ARGS.remove, view=ARGS.view, name=ARGS.name)
