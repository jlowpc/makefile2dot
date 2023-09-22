"""
Define the needed functions.
"""

import subprocess as sp
import graphviz as gv
import re as re
import os as os


def is_skip_line(line, skip_line_list):
    for sline in skip_line_list:
        if (line==sline): return True
        if (re.search(sline, line)): return True
    return False

def is_filename(name):
    res = bool(re.search(r"\s", name))
    if res: return False
    res = bool(re.search("/", name))
    if res: return True
    return False

def get_filename(fn, i):
    if i==0: return fn
    fn2 = fn + "_(" + str(i) + ')'
    return fn2

def shorten_filename(target, unique_fn_dict):
    if is_filename(target):
        found = False
        (pn, fn) = os.path.split(target)
        if fn in unique_fn_dict:
            for i in range(len(unique_fn_dict[fn])):
                if (unique_fn_dict[fn][i]==pn):
                    target = get_filename(fn, i)
                    found=True
                    break
            if not found:
                i = len(unique_fn_dict[fn])
                unique_fn_dict[fn].append(pn)
                target = get_filename(fn, i)
        else:
            unique_fn_dict[fn] = []
            unique_fn_dict[fn].append(pn)
            target = fn
    return target

def write_map(map_fn, unique_fn_dict):
    graph = gv.Digraph(comment="Map of filename", node_attr={'style': 'rounded'}, edge_attr={'minlen' : '2'}, strict=True)
    graph.attr(rankdir='LR')
    graph.attr(nodesep='0.1')
    for key, values in unique_fn_dict.items():
        for i in range(len(values)):
            key_name = get_filename(key, i)
            value_name = values[i] + "/" + key
            graph.node(key_name, shape="box", fillcolor="darkseagreen", style="filled, rounded")
            graph.node(value_name, shape="box", fillcolor="darkseagreen", style="filled, rounded")
            graph.edge(key_name, value_name)
    with open(map_fn, 'w') as file:
        file.write(str(graph))


def stream_database():
    """
    Generate and yield entries from the Makefile database.

    This function reads a Makefile using the make program (only tested with GNU
    Make) on your machine. It in turn generates the database constructed from
    the Makefile, ignoring default targets ("-r").
    """
    command = ["make", "-prnB"]
    with sp.Popen(command, stdout=sp.PIPE, universal_newlines=True) as proc:
        for line in proc.stdout:
            if line[0] == '#':
                continue
            if line[0] == '&':
                continue
            yield line.strip()

def get_label(add_table_dict, k):
    if add_table_dict is None:
        return None
    if k not in add_table_dict.keys():
        return None
    #print(f"{k} {add_table_dict[k]}")
    vs = add_table_dict[k]
    cell = ""
    for v in vs:
        cell += f"<tr> <td bgcolor=\"orangered\" align=\"left\" >{v}</td> </tr>" 
    label = f"<<table border=\"0\" cellborder=\"1\" cellspacing=\"0\" cellpadding=\"4\"> <tr> <td> <b>{k}</b> </td> </tr> <tr> <td> <table border=\"0\" cellborder=\"0\" cellspacing=\"0\"> {cell}</table></td> </tr></table>>"
    return label

def get_add_tables(add_fn):
    add_edges_list = []
    add_table_dict = {}
    if add_fn is not None:
        with open(add_fn) as f:
            for line in f:
                line = line.strip()
                (t, k, v) = line.split('===')
                if t=='TABLE':
                    cells = v.split(',')
                    add_table_dict[k] = cells
                if t=='EDGES':
                    tt = (k, v)
                    add_edges_list.append(tt)
    return(add_edges_list, add_table_dict)

def build_graph(stream, **kwargs):
    """
    Build a dependency graph from the Makefile database.
    """
    tool_fillcolor = "aliceblue"
    file_fillcolor = "darkseagreen"
    bigtool_fillcolor2 = "orangered"
    bigtool = ['yosys', 'drc', 'lvs']
    unique_fn_dict = {}
    graph = gv.Digraph(comment="Makefile", node_attr={'style': 'rounded'}, strict=True)
    graph.attr(rankdir=kwargs.get('direction', 'TB'))
    skip_line_list = kwargs.get('skip_line')
    replace_dict = kwargs.get('replace_dict')
    map_fn = kwargs.get('map')
    add_edges_list = kwargs.get('add_edge')
    add_table_dict = kwargs.get('add_table')
    for line in stream:
        # stream_database will return empty lines and lines with no :
        if is_skip_line(line, skip_line_list): 
            continue
        if ': ' not in line or line.isspace(): 
            continue
        list_token = line.split(':')
        if len(list_token) != 2:
            continue 
        target, dependencies = tuple(list_token)
        target = shorten_filename(target, unique_fn_dict)
        
        # Draw all targets except .PHONY (it isn't really a target).
        if target != ".PHONY":
            label = get_label(add_table_dict, target) 
            if target in bigtool:
                graph.node(target, shape="box", fillcolor=bigtool_fillcolor2, style="filled, rounded", label=label)
            else:
                graph.node(target)
        add_cmd=False
        cmd = next(stream) # Get the first command of this dependecy
        if is_skip_line(cmd, skip_line_list): 
            cmd = next(stream)
            if cmd != "" and ':' not in cmd:
                if is_skip_line(cmd, skip_line_list): 
                    cmd = ""
            else: cmd=""
        if cmd != "":
            if cmd in replace_dict:
                cmd = replace_dict[cmd]

        for dependency in dependencies.strip().split(' '):
            dependency = shorten_filename(dependency, unique_fn_dict)
            if dependency in ["default", "clean"]:
                continue
            elif target == ".PHONY":
                graph.node(dependency, shape="circle")
            elif target in ["default"]:
                graph.node(dependency, shape="rectangle")
            else:
                if cmd != "" and ':' not in cmd :
                    add_cmd=True
                    label = get_label(add_table_dict, dependency) 
                    graph.node(dependency, shape="rectangle", fillcolor=tool_fillcolor, style="filled", label=label)
                    graph.edge(dependency, cmd)
                else:
                    label = get_label(add_table_dict, dependency) 
                    graph.node(dependency, shape="rectangle", fillcolor=tool_fillcolor, style="filled", label=label)
                    graph.edge(dependency, target)
        if add_cmd:
            label = get_label(add_table_dict, cmd) 
            if cmd in bigtool:
                graph.node(cmd, shape="box", fillcolor=bigtool_fillcolor2, style="filled, rounded", label=label)
            else:
                graph.node(cmd, shape="box", fillcolor=file_fillcolor, style="filled, rounded", label=label)
            graph.edge(cmd, target)
    if map_fn is not None and len(unique_fn_dict)>0:
        write_map(map_fn, unique_fn_dict)
    if add_edges_list is not None:
        for et in add_edges_list:
            graph.edge(et[0], et[1])
    return graph


def makefile2dot(**kwargs):
    """
    Visualize a Makefile as a Graphviz graph.
    """
    direction = kwargs.get('direction', "BT")
    if direction not in ["LR", "RL", "BT", "TB"]:
        raise ValueError('direction must be one of "BT", "TB", "LR", RL"')

    output = kwargs.get('output', '')
    view = kwargs.get('view', False)
    skip = kwargs.get('skip')
    replace = kwargs.get('replace')
    map_fn = kwargs.get('map')
    add_fn = kwargs.get('add')
    
    line_list = []
    replace_dict = {}
    if skip is not None:
        with open(skip) as f:
            for line in f: line_list.append(line.rstrip())
    
    if replace is not None:
        with open(replace) as f:
            for line in f: 
                line = line.strip()
                (k, v) = line.split('===')
                replace_dict[k.rstrip()] = v.rstrip()

    add_edges_list, add_table_dict = get_add_tables(add_fn)

    graph = build_graph(stream_database(), direction=direction, skip_line=line_list, replace_dict=replace_dict, map=map_fn,
                        add_edge=add_edges_list, add_table=add_table_dict)
    if output == "":
        if view:
            graph.view()
        else:
            print(graph)
    else:
        with open(output, 'w') as file:
            file.write(str(graph))
        if view:
            graph.view()