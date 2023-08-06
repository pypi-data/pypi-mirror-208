"""This script is used to verify that the JSON parser and the Python model
builder produce the same model as the original JSON model.
"""

import argparse
import json

from pycollimator.model_builder import from_json, to_json
from pycollimator.model_builder.to_python import to_python_str


_TEMPLATE = """\
from pycollimator.model_builder import core
from pycollimator.model_builder.model import ModelBuilder, OPort, IPort


def create_model():
{}

    return model_builder
"""


if __name__ == "__main__":
    """
    Usage:
        bazel run //src/lib/pycollimator/model_builder/tools:j2p2j -- models/double_bouncing_ball.json
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=str, help="path to JSON file")
    args = parser.parse_args()

    with open(args.filepath) as f:
        in_json_data = json.load(f)

        model_builder, uuids, uiprops = from_json.parse_json(in_json_data)
        py_str = to_python_str(model_builder)

        # indent all lines in py_str by 4 spaces
        py_str = "\n".join("    " + line for line in py_str.splitlines())
        py_str = _TEMPLATE.format(py_str)

        exec(py_str, globals(), locals())

        model = create_model()
        print(json.dumps(to_json.render_model(model), indent=2))
