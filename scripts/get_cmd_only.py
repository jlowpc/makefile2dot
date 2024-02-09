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

    tool_fillcolor = "darkseagreen"
    file_fillcolor = "aliceblue"
    bigtool_fillcolor2 = "orangered"
    cmd_dict = {}
    node_dict = {}
    graph_added = {}
    methods = ['do-yosys', 'do-synth-report', 'do-2_floorplan_debug_macros', 'do-2_1_floorplan', 'do-2_2_floorplan_io', 'do-2_3_floorplan_tdms', 'do-2_4_floorplan_macro', 
    'do-2_5_floorplan_tapcell', 'do-2_6_floorplan_pdn', 'do-3_1_place_gp_skip_io', 'do-3_2_place_iop', 'do-3_3_place_gp', 
    'do-3_4_place_resized', 'do-3_5_place_dp', 'do-4_1_cts', 'do-generate_abstract', 'do-5_1_grt', 'do-5_2_fillcell', 'do-5_3_route', 
    'do-6_report']
    
    cmd_graph = gv.Digraph(comment="Map of filename", node_attr={'style': 'rounded'}, edge_attr={'minlen' : '2'}, strict=True)
    # cmd_graph = pydot.Dot('Command map', graph_type='digraph', strict=True) 
    #cmd_graph.set_node_defaults(style='rounded')
    #cmd_graph.set_edge_defaults(minlen='2')

    for edge in graph.get_edges():
        s = edge.get_source()
        d = edge.get_destination()
        s1 = re.findall('"([^"]*)"', str(s))
        d1 = re.findall('"([^"]*)"', str(d))
        if len(s1)>0 and len(d1) > 0:
            if re.match(r'do.*', d1[0]):
                #cmd_graph.add_node(n1) 
                #cmd_graph.add_node(n2)
                ss = str(s).replace("\"","")
                dd = str(d).replace("\"","")
                n1 = cmd_graph.node(ss, shape="box", fillcolor=tool_fillcolor, style="filled, rounded")
                n2 = cmd_graph.node(dd)
                cmd_graph.edge(ss, dd)
                idx = methods.index(d1[0])
                if (idx>0):
                    n1 = cmd_graph.node(methods[idx-1])
                    #n2 = cmd_graph.node(d1[0], shape="box")
                    # , shape="box", fillcolor=tool_fillcolor, style="filled, rounded"
                    #n1 = pydot.Node(, style="filled, rounded")
                    #n2 = pydot.Node(, fillcolor=tool_fillcolor, style="filled, rounded")
                    #e = pydot.Edge(n1, n2)
                    cmd_graph.edge(methods[idx-1], dd)
                #print(f"s: {s1[0]} -> {d1[0]}")
                #cmd_graph.edge('do-yosys', 'do-2_1_floorplan')
                #cmd_graph.add_edge(pydot.Edge(node_foo, node_bar, ltail=cluster_foo.get_name(), lhead=cluster_bar.get_name()))
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
