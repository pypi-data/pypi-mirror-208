import argparse
import glob
import json
import os

from pycollimator.model_builder import from_json
from pycollimator.model_builder.to_python import to_python_str


if __name__ == "__main__":
    """
    Convert a JSON file or folder of JSON files to Python code.

    Usage:
        bazel run //src/lib/pycollimator/model_builder/tools:json_to_python -- models/double_bouncing_ball.json

        OR

        bazel run //src/lib/pycollimator/model_builder/tools:json_to_python -- models/
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=str, help="path to JSON file or folder of JSON files")
    args = parser.parse_args()

    if os.path.isdir(args.filepath):
        for filename in glob.glob(os.path.join(args.filepath, "**/*.json")):
            if filename.endswith(".json"):
                basename = filename.split(".")[-2]
                out_filename = f"{basename}.py"
                with open(filename) as in_f, open(out_filename, "w") as out_f:
                    in_json_data = json.load(in_f)

                    model_builder, uuids, uiprops = from_json.parse_json(in_json_data)
                    out_f.write(to_python_str(model_builder))
    else:
        with open(args.filepath) as f:
            in_json_data = json.load(f)

            model_builder, uuids, uiprops = from_json.parse_json(in_json_data)
            print(to_python_str(model_builder))
