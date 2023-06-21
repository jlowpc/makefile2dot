import graphviz as gv
import re as re
from collections import defaultdict

def subgraph(**kwargs):
    output = kwargs.get('output', '')
    view = kwargs.get('view', False)
    edge_pattern = re.compile('"?(.*)"? -> "?(.*)"?')
    node_pattern = re.compile('"?(.*)"? \[(.*)\]')
    num_pattern = re.compile('([1-6])_.+')
    graph = gv.Digraph()
    sg = []
    with open(kwargs.get('input')) as dot:
        graph = gv.Source(dot.read())
    graph2 = gv.Digraph(comment="Subgraph", 
                        node_attr={'style': 'rounded'}, 
                        edge_attr={'minlen' : '2'}, strict=True)
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
               'cluster_6' : 'drakred'}
    for i in range(6):
        sg.append(gv.Digraph(name=f'cluster_{i+1}', 
                             node_attr={'shape': 'box'}, 
                             graph_attr={'label' :  sg_name[f'cluster_{i+1}'], 
                                         'style' : 'filled',
                                         'color' : sg_color[f'cluster_{i+1}'], 
                                         'fillcolor' : 'darkgray:gold',
                                         'gradientangle' : '0',
                                         'fontsize' : '30pt',
                                         'page' : '8.5,11',
                             }))
    for s in graph:
        m1 = edge_pattern.search(s)
        if m1:
            s1 = m1.group(1).strip().strip('"').strip()
            s2 = m1.group(2).strip().strip('"').strip()
            m2 = num_pattern.search(s1)
            if m2:
                i = int(m2.group(1))-1
                sg[i].edge(s1, s2)
            else:
                m2 = num_pattern.search(s2)
                if m2:
                    i = int(m2.group(1))-1
                    sg[i].edge(s1, s2)
                else:
                    graph2.edge(s1, s2)
        else:
            m1 = node_pattern.search(s)
            if m1:
                s1 = m1.group(1).strip().strip('"').strip()
                if s1 != 'node':
                    s2 = m1.group(2).strip()
                    for quoted_part in re.findall(r'\"(.+?)\"', s2):
                        s2 = s2.replace(quoted_part, quoted_part.replace(" ", ""))
                    s2 = s2.replace('"', '')
                    d = {}
                    if s2 != "":
                        d = dict(x.split("=") for x in s2.split())
                    graph2.node(s1, **d) 

    for i in range(6):
        graph2.subgraph(sg[i]) 

    if output == "":
       if view:
           graph2.view()
       else:
           print(graph2)
    else:
       with open(output, 'w') as file:
           file.write(str(graph2))
       if view:
           graph2.view()

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
