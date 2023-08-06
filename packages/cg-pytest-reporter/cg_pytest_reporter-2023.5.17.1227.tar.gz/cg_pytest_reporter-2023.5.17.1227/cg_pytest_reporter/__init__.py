"""This module contains decorators that can be used to mark certain properties
of a test function or class.
"""
import pytest

suite_name = pytest.mark.cg_suite_name
suite_weight = pytest.mark.cg_suite_weight

name = pytest.mark.cg_name
description = pytest.mark.cg_description
weight = pytest.mark.cg_weight
reason = pytest.mark.cg_reason
hide_stdout = pytest.mark.cg_hide_stdout
hide_stderr = pytest.mark.cg_hide_stderr
