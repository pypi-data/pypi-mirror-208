import json
from typing import Any

import numpy as np
import pandas as pd
import pytest
from hamilton import node

from dagworks.tracking import runs

result_base = {
    "observability_type": "REPLACE_ME",
    "observability_value": None,
    "observability_schema_version": "0.0.1",
}


def default_func() -> Any:
    return None


def create_node(name: str, type_: type) -> node.Node:
    return node.Node(name, type_, "", default_func)


@pytest.mark.parametrize(
    "test_result,test_node,observability_type,observability_value",
    [
        (
            pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
            create_node("test", pd.DataFrame),
            "pandas_describe",
            {
                "a": {
                    "25%": 1.5,
                    "50%": 2.0,
                    "75%": 2.5,
                    "count": 3.0,
                    "dtype": "int64",
                    "max": 3.0,
                    "mean": 2.0,
                    "min": 1.0,
                    "std": 1.0,
                },
                "b": {
                    "25%": 4.5,
                    "50%": 5.0,
                    "75%": 5.5,
                    "count": 3.0,
                    "dtype": "int64",
                    "max": 6.0,
                    "mean": 5.0,
                    "min": 4.0,
                    "std": 1.0,
                },
            },
        ),
        (
            pd.Series([1, 2, 3], name="a"),
            create_node("a", pd.Series),
            "pandas_describe",
            {
                "a": {
                    "25%": 1.5,
                    "50%": 2.0,
                    "75%": 2.5,
                    "count": 3.0,
                    "dtype": "int64",
                    "max": 3.0,
                    "mean": 2.0,
                    "min": 1.0,
                    "std": 1.0,
                }
            },
        ),
        (
            pd.Series([None, None, None, None, None], name="a", dtype=np.float64),
            create_node("a", pd.Series),
            "pandas_describe",
            {
                "a": {
                    "25%": None,
                    "50%": None,
                    "75%": None,
                    "count": 0,
                    "dtype": "float64",
                    "max": None,
                    "mean": None,
                    "min": None,
                    "std": None,
                }
            },
        ),
        (
            pd.Series(name="a", data=pd.date_range("20230101", "20230103")),
            create_node("a", pd.Series),
            "pandas_describe",
            {
                "a": {
                    "25%": 1672574400000,
                    "50%": 1672617600000,
                    "75%": 1672660800000,
                    "count": 3,
                    "dtype": "datetime64[ns]",
                    "max": 1672704000000,
                    "mean": 1672617600000,
                    "min": 1672531200000,
                }
            },
        ),
        (
            np.ndarray([1, 2, 3, 4]),
            create_node("test", np.ndarray),
            "unsupported",
            {
                "action": "reach out to the DAGWorks team to add support for this type.",
                "unsupported_type": "<class 'numpy.ndarray'>",
            },
        ),
        (
            [1, 2, 3, 4],
            create_node("test", list),
            "unsupported",
            {
                "action": "reach out to the DAGWorks team to add support for this type.",
                "unsupported_type": "<class 'list'>",
            },
        ),
        (
            {"a": 1},
            create_node("test", dict),
            "unsupported",
            {
                "action": "reach out to the DAGWorks team to add support for this type.",
                "unsupported_type": "<class 'dict'>",
            },
        ),
        (
            1,
            create_node("test", int),
            "primitive",
            {
                "type": "<class 'int'>",
                "value": 1,
            },
        ),
        (
            2.0,
            create_node("test", float),
            "primitive",
            {
                "type": "<class 'float'>",
                "value": 2.0,
            },
        ),
        (
            "3",
            create_node("test", str),
            "primitive",
            {
                "type": "<class 'str'>",
                "value": "3",
            },
        ),
        (
            False,
            create_node("test", bool),
            "primitive",
            {
                "type": "<class 'bool'>",
                "value": False,
            },
        ),
    ],
    ids=[
        "pandas_df",
        "pandas_series",
        "nan_series",
        "datetime_series",
        "numpy_array",
        "list",
        "dict",
        "int",
        "float",
        "str",
        "bool",
    ],
)
def test_process_result_happy(test_result, test_node, observability_type, observability_value):
    """Tests a happy path for the process result function."""
    actual_result = runs.process_result(test_result, test_node)
    expected_result = result_base.copy()
    expected_result["observability_type"] = observability_type
    expected_result["observability_value"] = observability_value
    assert actual_result == expected_result
    # Allows us to double-check that everything can be json-dumped
    json.dumps(actual_result)
