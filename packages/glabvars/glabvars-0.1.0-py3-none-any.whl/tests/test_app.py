from src.app import GLVariable
from pydantic import parse_raw_as
import pytest


@pytest.fixture
def glab_variables():
    with open("glab2gcl/tests/fixtures/glvars.json", "rb") as f:
        return f.read()


def test_glvariable_can_be_parsed(glab_variables):
    """Test"""
    gl_vars = parse_raw_as(list[GLVariable], glab_variables)
    assert isinstance(gl_vars, list)
    assert all(isinstance(gl_var, GLVariable) for gl_var in gl_vars)
