import graphviz as gv
import re as re
from collections import defaultdict
import pydot

def create_cmd_only(**kwargs):
    output = kwargs.get('output', '')
    view = kwargs.get('view', False)
    add_fn=kwargs.get('add')
    graphs = pydot.graph_from_dot_file(kwargs.get('input'))
    graph = graphs[0]

    cmd_dict = {}
    next_list = []
    tree_dict = defaultdict(list)
    
    cmd_graph = pydot.Dot('Command map', graph_type='digraph', strict=True) 
    cmd_graph.set_node_defaults(style='rounded')
    cmd_graph.set_edge_defaults(minlen='2')

    for node in graph.get_nodes():
        s1 = node.get_name()
        attr = node.get_attributes()
        if 'fillcolor' in attr:
            if attr['fillcolor'] == 'darkseagreen' or attr['fillcolor'] == 'orangered':
                cmd_dict[s1] = 1

    for edge in graph.get_edges():
        s1 = edge.get_source()
        s2 = edge.get_destination()
        tree_dict[s1].append(s2)

    for key, values in cmd_dict.items():
        already_done = {}
        for item in tree_dict[key]:
            next_list.append(item)
        while (len(next_list) > 0):
            item = next_list.pop()
            if item in cmd_dict:
                n1 = graph.get_node(item)[0]
                n2 = graph.get_node(key)[0]
                #nn1 = pydot.Node(name=item, **(n1.get_attributes()))
                #nn2 = pydot.Node(name=key, **(n2.get_attributes()))
                e = pydot.Edge(key, item)
                cmd_graph.add_node(n1) 
                cmd_graph.add_node(n2)
                cmd_graph.add_edge(e)
            else: 
                if item not in already_done:
                    next_list.append(item)
                already_done[item] = 1
                for item2 in tree_dict[item]:
                    if item2 not in already_done:
                        next_list.append(item2)
                    already_done[item2] = 1
    if output == "":
        if view:
            cmd_graph.view()
        else:
            print(cmd_graph)
    else:
        with open(output, 'w') as file:
            file.write(str(cmd_graph))
        if view:
            cmd_graph.view()

import argparse

DESC = "Create a dot graph containing only commands from a dot graph."
PARSER = argparse.ArgumentParser(description=DESC)
PARSER.add_argument(dest='input', help="input DOT file")
PARSER.add_argument('--direction', '-d', dest='direction', default="BT",
                            help="direction to draw graph ('BT', 'TB', 'LR', or 'RL')")

PARSER.add_argument('--output', '-o', dest='output', default="",
                            help="output file name (default: stdout).")

PARSER.add_argument('--view', '-v', action='store_true',
                            help="view the graph (disables output to stdout)")

PARSER.add_argument('--add', '-a', dest='add_fn',
                    help="file with lines to add a table or edges to graph")

ARGS = PARSER.parse_args()

create_cmd_only(input=ARGS.input, direction=ARGS.direction, output=ARGS.output, view=ARGS.view, add=ARGS.add_fn)
