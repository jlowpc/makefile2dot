"""
Test the helper functions in makefile2dot.
"""
import io
from contextlib import redirect_stdout
from makefile2dot import makefile2dot


def test_makefile():
    '''
    Should still return the target.
    '''
    with io.StringIO() as output:
        with redirect_stdout(output):
            makefile2dot(direction="TB")
        result = output.getvalue()

    assert "digraph {" in result
    assert "\trankdir=TB" in result
    assert '\t"output.png"' in result
    assert '\t".twine_checked" [fillcolor=aliceblue shape=rectangle style=filled]' in result
    assert '\t"output.dot" [fillcolor=aliceblue shape=rectangle style=filled]' in result
    assert '\t".twine_checked" -> dist' in result
