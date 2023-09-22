import graphviz as gv
import re as re
from collections import defaultdict
from makefile2dot import get_label, get_add_tables

def create_cmd_only(**kwargs):
    bigtool = ['yosys', 'drc', 'lvs']
    output = kwargs.get('output', '')
    view = kwargs.get('view', False)
    skip=kwargs.get('skip')
    add_fn=kwargs.get('add')
    cmd_pattern = re.compile('"?(.*)"? \[fillcolor=darkseagreen shape=box style="filled, rounded"\]')
    cmd_pattern2 = re.compile('"?(.*)"? \[fillcolor=orangered shape=box style="filled, rounded"\]')
    cmd_pattern3 = re.compile('"?(.*)"? (\[label.*)"')
    edge_pattern = re.compile('"?(.*)"? -> "?(.*)"?')
    graph = gv.Digraph()
    with open(kwargs.get('input')) as dot:
        graph = gv.Source(dot.read())
    cmd_dict = {}
    next_list = []
    tree_dict = defaultdict(list)
    skip_dict = defaultdict(list)
    add_edges_list, add_table_dict = get_add_tables(add_fn)
    if skip is not None:
        with open(skip) as f:
            for line in f: 
                m = edge_pattern.search(line)
                skip_dict[m.group(1).strip().strip('"')].append(m.group(2).strip().strip('"'))

    cmd_graph = gv.Digraph(comment="Command map", node_attr={'style': 'rounded'}, edge_attr={'minlen' : '2'}, strict=True)
    for s in graph:
        #search = re.search(r'(\[.*?\s\])(?=\s|$)', file)
        m1 = cmd_pattern.search(s) or cmd_pattern2.search(s) or cmd_pattern3.search(s)
        if m1:
            ss = m1.group(1).strip().strip('"').strip()
            #print(f"Added command {ss}")
            cmd_dict[ss] = 1
        m2 = edge_pattern.search(s)
        if m2:
            s1 = m2.group(1).strip().strip('"').strip()
            s2 = m2.group(2).strip().strip('"').strip()
            #print(f"{s1} -> {s2}")
            tree_dict[s1].append(s2)
    for key, values in cmd_dict.items():
        already_done = {}
        for item in tree_dict[key]:
            next_list.append(item)
        while (len(next_list) > 0):
            item = next_list.pop()
            if item in cmd_dict:
                add=True
                if key in skip_dict:
                    for i in skip_dict[key]:
                        if (i==item):
                            add=False
                            break
                if add:
                    label_key = get_label(add_table_dict, key)
                    label_item = get_label(add_table_dict, item)
                    if key in bigtool:
                        cmd_graph.node(key, shape="box", fillcolor="orangered", style="filled, rounded", label=label_key)
                    else:
                        cmd_graph.node(key, shape="box", fillcolor="darkseagreen", style="filled, rounded", label=label_key)
                    if item in bigtool:
                        cmd_graph.node(item, shape="box", fillcolor="orangered", style="filled, rounded", label=label_item)
                    else:
                        cmd_graph.node(item, shape="box", fillcolor="darkseagreen", style="filled, rounded", label=label_item)
                    cmd_graph.edge(key, item)
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

PARSER.add_argument('--skip', '-s',dest='skip',
                            help="skip edges to be included in graph")

PARSER.add_argument('--add', '-a', dest='add_fn',
                    help="file with lines to add a table or edges to graph")

ARGS = PARSER.parse_args()

create_cmd_only(input=ARGS.input, direction=ARGS.direction, output=ARGS.output, view=ARGS.view, skip=ARGS.skip, add=ARGS.add_fn)
