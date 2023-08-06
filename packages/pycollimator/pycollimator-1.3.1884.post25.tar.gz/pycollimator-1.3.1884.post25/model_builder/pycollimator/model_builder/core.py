import pycollimator.model_builder.model as model
import pycollimator.model_builder.schema_reader as schema_reader


SCHEMAS = {}
CLASSES = {}

for s in schema_reader.load_schemas("core"):
    klass = model._node_class_from_schema(s)
    SCHEMAS[s.name] = s
    CLASSES[s.name] = klass
    globals()[s.name] = klass


def init_integrator(**params):
    if "input_names" not in params:
        ins = ("in_0",)
        if params.get("enable_reset") == "true":
            if "reset" not in ins:
                ins += ("reset",)
            if params.get("enable_external_reset", "true") == "true":
                if "reset_value" not in ins:
                    ins += ("reset_value",)
        elif "enable_reset" in params:
            del params["enable_reset"]
            if "enable_external_reset" in params:
                del params["enable_external_reset"]

        if params.get("enable_hold") == "true":
            if "hold" not in ins:
                ins += ("hold",)
        elif "enable_hold" in params:
            del params["enable_hold"]

        if params.get("enable_limits") == "true":
            if "upper_limit" not in ins:
                ins += ("upper_limit", "lower_limit")
        elif "enable_limits" in params:
            del params["enable_limits"]

        params["input_names"] = ins

    if "lower_limit" in params:
        del params["lower_limit"]
    if "upper_limit" in params:
        del params["upper_limit"]
    if "reset_trigger_method" in params:
        del params["reset_trigger_method"]
    if "hold_trigger_method" in params:
        del params["hold_trigger_method"]

    return params


class Integrator(Integrator):
    def __init__(self, *args, **params):
        super().__init__(*args, **init_integrator(**params))


class IntegratorDiscrete(IntegratorDiscrete):
    def __init__(self, *args, **params):
        super().__init__(*args, **init_integrator(**params))


class PID(PID):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("in_0",)
            if params.get("enable_external_initial_state") == "true":
                if "initial_state" not in ins:
                    ins += ("initial_state",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class PID_Discrete(PID_Discrete):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("in_0",)
            if params.get("enable_external_initial_state") == "true":
                if "initial_state" not in ins:
                    ins += ("initial_state",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class LogicalOperator(LogicalOperator):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = (
                "in_0",
                "in_1",
            )
            if params.get("function") == "not":
                ins = ("in_0",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class RateLimiter(RateLimiter):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("in_0",)
            if params.get("enable_dynamic_upper_limit") == "true":
                if "upper_limit" not in ins:
                    ins += ("upper_limit",)
            if params.get("enable_dynamic_lower_limit") == "true":
                if "lower_limit" not in ins:
                    ins += ("lower_limit",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class Saturate(Saturate):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("in_0",)
            if params.get("enable_dynamic_upper_limit") == "true":
                if "upper_limit" not in ins:
                    ins += ("upper_limit",)
            if params.get("enable_dynamic_lower_limit") == "true":
                if "lower_limit" not in ins:
                    ins += ("lower_limit",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class Adder(Adder):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = [f"in_{k}" for k in range(len(params["operators"]))]
            params["input_names"] = tuple(ins)
        if type(params["operators"]) is list:
            params["operators"] = "".join(params["operators"])
        super().__init__(*args, **params)


class Product(Product):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = [f"in_{k}" for k in range(len(params["operators"]))]
            params["input_names"] = tuple(ins)
        if type(params["operators"]) is list:
            params["operators"] = "".join(params["operators"])
        super().__init__(*args, **params)


class Inport(Inport):
    def __init__(self, *args, **params):
        super().__init__(*args, **params)
        args[0].inports.append(self.name)


class Outport(Outport):
    def __init__(self, *args, **params):
        super().__init__(*args, **params)
        args[0].outports.append(self.name)
