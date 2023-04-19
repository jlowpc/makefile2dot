# Visualize Makefile Dependency Graphs

`makefile2dot` produces a Graphviz `dot` graph from a Makefile. To run it,
install `graphviz` and `python`. This version runs on python 3.

```bash
# apt-get install graphviz python
$ pip install makefile2dot
```

## Usage

`makefile2dot` reads the `Makefile` in the current working directory using the
same lookup rules that `make` does (it actually uses `make` to parse the
`Makefile`). By default, it writes the resulting `dot` graph to `stdout`, which
can be read in by `graphviz`. So a nice trick is to pipe output from
`makefile2dot` directly in to `dot`.

For example:

````bash
$ makefile2dot | dot -Tpng > out.png
````

If you just want to see the graph without saving it, you can provide the
`--view` flag:

````bash
$ makefile2dot -v
````

You can select the graph orientation so that it is drawn from top to bottom
(`TB`), bottom to top (`BT`), left to right (`LR`) or right to left (`RL`). For
example:

````bash
$ makefile2dot -v --direction LR
````

draws the graph from left to right, rather than the default bottom to top.

Normal targets are drawn as rectangles, and `.PHONY` targets are drawn as
circles.

## Tips

To test this project in the source directory, add the source directory to the
python path:

````bash
$ export PYTHONPATH=$(pwd)
````
## Changes made with this fork
-- Commands in the makefile is created in the graph
-- Files are in blue rectangle, commands are in green rounded box
-- Added 3 arguments: skip, replace, and map
   skip: lines to be skipped processing in the makefile
   replace: replace an node's name with mapping in replace (format: old --- new)
   map: filenames with more than one level will be shortened and a map DOT file can be created
-- 