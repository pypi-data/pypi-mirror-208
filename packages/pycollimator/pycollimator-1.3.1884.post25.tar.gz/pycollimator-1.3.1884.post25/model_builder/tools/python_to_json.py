import argparse
import json

from pycollimator.model_builder import to_json
from pycollimator.model_builder import core
from pycollimator.model_builder.model import ModelBuilder, OPort, IPort


if __name__ == "__main__":
    """
    Takes a Python model and converts it to JSON. The input
    python code should contain a `create_model` function that
    returns a ModelBuilder object.

    Usage:
        bazel run //src/lib/pycollimator/model_builder/tools:python_to_json -- example_model.py
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("model_path", type=str, help="path to Python model file")
    args = parser.parse_args()

    with open(args.model_path) as f:
        exec(f.read(), globals(), locals())

        model = create_model()
        print(json.dumps(to_json.render_model(model), indent=2))
