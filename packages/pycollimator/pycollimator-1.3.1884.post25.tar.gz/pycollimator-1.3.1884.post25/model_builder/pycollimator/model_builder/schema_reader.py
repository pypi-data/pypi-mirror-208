import glob
import json
import os
import sys


INPUTS = "inputs"
OUTPUTS = "outputs"

_schemas_path = os.path.join(os.path.dirname(__file__), "schemas")
if not os.path.exists(_schemas_path):
    # path used when running from bazel
    _schemas_path = os.path.join("src", "lib", "model-schemas", "schemas")


def _param(p):
    name = p["name"]
    v = p["default_value"]
    t = p["data_type"]
    if t == "float":
        v = float(v)
    elif t == "int":
        v = int(v)
    elif t == "bool":
        v = str(v).lower()
        if v == "true":
            v = True
        elif v == "false":
            v = False
        else:
            raise TypeError(f"unknown bool value {v} for {name}")
    elif t == "stringlist":
        v = eval(v)
    elif t in ("array1df", "array1di", "array2df", "array2di"):
        v = eval(v)
    elif t == "string":
        pass
    elif t == "any":
        pass
    else:
        raise TypeError(f"unknown param type {t} for {name}")
    return (name, v)


class Schema:
    def __init__(self, json):
        self.json = json
        self.name = json["base"]["name"]
        self.namespace = json["base"]["namespace"]
        self.fullname = f"{self.namespace}.{self.name}"
        param_defs = json.get("parameter_definitions", [])

        self.parameter_definitions = {p["name"]: p for p in param_defs}
        self.default_params = dict(_param(p) for p in param_defs)

        self.default_input_names = None
        self.default_output_names = None

    def __repr__(self) -> str:
        return f"{self.name}: in={self.port_names('inputs')} out={self.port_names('outputs')} parameters={self.default_params}"

    def doc(self, with_description=True) -> str:
        inputs = list(self.port_names("inputs"))
        outputs = list(self.port_names("outputs"))
        doc = f"{self.fullname}("
        for p in self.default_params:
            if isinstance(self.default_params[p], str):
                doc += f"{p}='{self.default_params[p]}', "
            else:
                doc += f"{p}={self.default_params[p]}, "
        doc += f"inputs={inputs}, outputs={outputs}"
        if with_description:
            description: str = self.json["base"].get("description", "")
            description = description.replace("\n", " ")
            doc += f', description="{description}"'
        doc += ")"
        return doc

    @property
    def has_dynamic_input_ports(self):
        has_dyn_ports = bool(self.ports("inputs", "dynamic"))
        has_auto_ports = self.json.get("ports").get("has_automatic_ports", False)
        return has_dyn_ports or has_auto_ports

    @property
    def has_dynamic_output_ports(self):
        has_dyn_ports = bool(self.ports("outputs", "dynamic"))
        has_auto_ports = self.json.get("ports").get("has_automatic_ports", False)
        return has_dyn_ports or has_auto_ports

    def port_names(self, inout, *, n_dyn=None):
        return (
            self.port_names_of_kind(inout, "static")
            + self.port_names_of_kind(inout, "conditional")
            + self.port_names_of_kind(inout, "dynamic", n_dyn)
        )

    def port_names_of_kind(self, inout, kind, n_dyn=0):
        ports = self.ports(inout, kind)
        if kind == "dynamic":
            if not ports:
                return ()
            prefix = "in" if inout == "inputs" else "out"
            if n_dyn is None:
                n_dyn = ports.get("default_count", 0)
            return tuple(f"{prefix}_{i}" for i in range(n_dyn))
        else:
            return tuple(p["name"] for p in ports)

    def ports(self, inout, kind):
        if inout not in ("inputs", "outputs"):
            raise KeyError(f"ports must be inputs or outputs; got {inout}")
        return self.json.get("ports", {}).get(inout, {}).get(kind, [])

    def primary_input_port(self):
        ps = self.ports("inputs", "static")
        if len(ps) == 1:
            return ps[0]["name"]
        return None

    def primary_output_port(self):
        ps = self.ports("outputs", "static")
        if len(ps) == 1:
            return ps[0]["name"]
        return None

    def port_kind(self, inout, portname):
        if portname in self.ports(inout, "static"):
            return "static"
        if portname in self.ports(inout, "conditional"):
            return "conditional"
        else:
            return "dynamic"


def load_schema(path):
    with open(path) as f:
        return Schema(json.load(f))


def load_schemas(namespace):
    root_dir = f"{_schemas_path}/blocks/{namespace}"
    for name in sorted(glob.glob(f"{root_dir}/*.json")):
        yield load_schema(f"{name}")


if __name__ == "__main__":
    for schema in load_schemas("core"):
        print(schema)
