"""
Define the needed functions.
"""

import subprocess as sp
import graphviz as gv


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


def build_graph(stream, **kwargs):
    """
    Build a dependency graph from the Makefile database.
    """
    tool_fillcolor = "aliceblue"
    file_fillcolor = "darkseagreen"
    graph = gv.Digraph(comment="Makefile")
    graph.attr(rankdir=kwargs.get('direction', 'TB'))
    for line in stream:
        # stream_database will return empty lines and lines with no :
        if ': ' not in line or line.isspace(): 
            continue
        list_token = line.split(':')
        if len(list_token) != 2:
            continue 
        target, dependencies = tuple(list_token)
        # Draw all targets except .PHONY (it isn't really a target).
        if target != ".PHONY":
            graph.node(target)
        add_cmd=False
        cmd = next(stream) # Get the first command of this dependecy
        for dependency in dependencies.strip().split(' '):
            if dependency in ["default", "clean"]:
                continue
            elif target == ".PHONY":
                graph.node(dependency, shape="circle")
            elif target in ["default"]:
                graph.node(dependency, shape="rectangle")
            else:
                if cmd != "" and ':' not in cmd :
                    add_cmd=True
                    graph.node(dependency, shape="rectangle", fillcolor=tool_fillcolor, style="filled")
                    graph.edge(cmd, dependency, dir="back")
                else:
                    graph.node(dependency, shape="rectangle", fillcolor=tool_fillcolor, style="filled")
                    graph.edge(target, dependency, dir="back")
        if add_cmd:
            graph.node(cmd, shape="oval", fillcolor=file_fillcolor, style="filled")
            graph.edge(target, cmd, dir="back")

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

    graph = build_graph(stream_database(), direction=direction)
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
