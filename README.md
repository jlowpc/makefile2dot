# A Visualizer for Makefiles

## DESCRIPTION

`makefile2dot` produces a Graphviz `dot` graph from a Makefile. To run it,
install `graphviz` and `python`. This version runs on python 3.

```bash
    sudo apt-get install graphviz python
```

## USAGE

`makefile2dot` writes to `stdout` by default, which can be read in by
`graphviz`. So the nice trick is to pipe output from `makefile2dot` directly in
to `dot`. The `Makefile` is read from `stdin` to support piping input as well.

Example usage:

````bash
    makefile2dot <Makefile | dot -Tpng > out.png
````

## Example

This [example Makefile](https://github.com/vak/makefile2dot/blob/master/Makefile) will result in this png-image:
    
![ScreenShot](https://raw.githubusercontent.com/vak/makefile2dot/master/output-examlple.png)
