import graphviz as gv
import re as re
import pydot
from collections import defaultdict

def subgraph(**kwargs):
    output = kwargs.get('output', '')
    view = kwargs.get('view', False)
    remove = ['floorplan', 'cts', 'place', 'route', 'finish']
    edge_pattern = re.compile('"?(.*)"? -> "?(.*)"?')
    node_pattern = re.compile('"?(.*)"? \[(.*)\]')
    num_pattern = re.compile('([1-6])_.+')
    sg = []

    new_graph = pydot.Dot('', graph_type='digraph', strict=True) 
    new_graph.set_node_defaults(style='rounded')
    new_graph.set_edge_defaults(minlen='2')

    sg_name = {'cluster_1' : '1. synthesize', 
               'cluster_2' : '2. floorplan', 
               'cluster_3' : '3. place', 
               'cluster_4' : '4. cts', 
               'cluster_5' : '5. route', 
               'cluster_6' : '6. finish'}
    sg_color = {'cluster_1' : 'darkgreen', 
               'cluster_2' : 'aquamarine3', 
               'cluster_3' : 'gold', 
               'cluster_4' : 'orange', 
               'cluster_5' : 'crimson', 
               'cluster_6' : 'darkred'}
    for i in range(6):
        h = pydot.Subgraph(f'cluster_{i+1}') 
        h.set_node_defaults(shape='box')
        h.set_graph_defaults(label=sg_name[f'cluster_{i+1}'], 
                             style = 'filled',
                             color = sg_color[f'cluster_{i+1}'], 
                             fillcolor = '\"darkgray:gold\"',
                             gradientangle = '0',
                             fontsize = '30pt',
                             page = '8.5,11')
        new_graph.add_subgraph(h)

    graphs = pydot.graph_from_dot_file(kwargs.get('input'))
    graph = graphs[0]
  
    for edge in graph.get_edges():
        s1 = edge.get_source()
        s2 = edge.get_destination()
        if s2 in remove:
            continue
        m2 = num_pattern.search(s1)
        if m2:
            i = int(m2.group(1))-1
            m3 = num_pattern.search(s2)
            e = pydot.Edge(s1, s2)
            if m3:
                j = int(m3.group(1))-1
                if i!=j:
                    new_graph.add_edge(e)
                else:
                    g = new_graph.get_subgraph(f'cluster_{i+1}')
                    g[0].add_edge(e)
            else:
                g = new_graph.get_subgraph(f'cluster_{i+1}')
                g[0].add_edge(e)
        else:
            m2 = num_pattern.search(s2)
            e = pydot.Edge(s1, s2)
            if m2:
                i = int(m2.group(1))-1
                g = new_graph.get_subgraph(f'cluster_{i+1}')
                g[0].add_edge(e)
            else:
                new_graph.add_edge(e)

    for node in graph.get_nodes():
        s1 = node.get_name()
        attr = node.get_attributes()
        s1 = s1.strip().strip('"').strip()
        if s1 != 'node' and s1 not in remove:
            mm = num_pattern.search(s1)
            nn = pydot.Node(name=s1, **attr)
            if mm:
                i = int(mm.group(1))-1
                g = new_graph.get_subgraph(f'cluster_{i+1}')
                g[0].add_node(nn)
            new_graph.add_node(nn)

    if output == "":
       if view:
           new_graph.view()
       else:
           print(new_graph)
    else:
       with open(output, 'w') as file:
           file.write(str(new_graph))
       if view:
           new_graph.view()

import argparse

DESC = "Create a dot graph with subgraph/clusters from a dot graph."
PARSER = argparse.ArgumentParser(description=DESC)
PARSER.add_argument(dest='input', help="input DOT file")
PARSER.add_argument('--direction', '-d', dest='direction', default="BT",
                            help="direction to draw graph ('BT', 'TB', 'LR', or 'RL')")

PARSER.add_argument('--output', '-o', dest='output', default="",
                            help="output file name (default: stdout).")

PARSER.add_argument('--view', '-v', action='store_true',
                            help="view the graph (disables output to stdout)")

ARGS = PARSER.parse_args()

subgraph(input=ARGS.input, direction=ARGS.direction, output=ARGS.output, view=ARGS.view)
