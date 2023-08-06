Module for building models programatically using python. For now the package
is independant from pycollimator but it could be part of pycollimator
in the future.


## Build

Build the wheel:

```
pip install build
python -m build
```

## Usage

Mass spring damper model:
```
from pycollimator.model_builder.core import *
from pycollimator.model_builder.model import ModelBuilder, OPort, IPort


def create_model():
    ModelBuilder_1 = ModelBuilder("Mass Spring Damper", id="ModelBuilder_1")
    ModelBuilder_1.add_parameter("m", "1")  # Mass
    ModelBuilder_1.add_parameter("k", "10")  # Spring constant
    ModelBuilder_1.add_parameter("c", "1")  # Damping constant
    Integrator_2 = Integrator(model=ModelBuilder_1,
                              name="Velocity",
                              initial_states="0",
                              id="Integrator_2")
    Integrator_3 = Integrator(model=ModelBuilder_1,
                              name="Position",
                              initial_states="0",
                              id="Integrator_3")
    Gain_1 = Gain(model=ModelBuilder_1, name="Mass", gain="1/m", id="Gain_1")
    Gain_2 = Gain(model=ModelBuilder_1, name="Spring", gain="-k", id="Gain_2")
    Gain_3 = Gain(model=ModelBuilder_1, name="Damping", gain="-c", id="Gain_3")
    Adder_0 = Adder(model=ModelBuilder_1,
                    operators='++',
                    inputs=['in_0', 'in_1'],
                    outputs=['out_0'],
                    id="Adder_0")
    ModelBuilder_1.add_link(OPort(Integrator_2, "out_0"),
                            IPort(Integrator_3, "in_0"))
    ModelBuilder_1.add_link(OPort(Integrator_3, "out_0"),
                            IPort(Gain_2, "in_0"))
    ModelBuilder_1.add_link(OPort(Integrator_2, "out_0"),
                            IPort(Gain_3, "in_0"))
    ModelBuilder_1.add_link(OPort(Gain_2, "out_0"), IPort(Adder_0, "in_0"))
    ModelBuilder_1.add_link(OPort(Gain_3, "out_0"), IPort(Adder_0, "in_1"))
    ModelBuilder_1.add_link(OPort(Adder_0, "out_0"), IPort(Gain_1, "in_0"))
    ModelBuilder_1.add_link(OPort(Gain_1, "out_0"),
                            IPort(Integrator_2, "in_0"))
    return ModelBuilder_1

```

From JSON:
```
from pycollimator.model_builder import from_json

with open('/some/model.json') as f:
    json_data = json.load(f)
    model_builder, uuids, uiprops = from_json.parse_json(json_data)
```

To JSON:
```
import json
from pycollimator.model_builder import to_json

model_builder = ModelBuider(...)

...

json.dumps(to_json.render_model(model_builder), indent=2)
```

JSON to Python:
```
from pycollimator.model_builder import from_json
from pycollimator.model_builder.to_python import to_python_str


with open('/some/model.json') as f:
    json_data = json.load(f)
    model_builder, uuids, uiprops = from_json.parse_json(json_data)
    print(to_python_str(model_builder))
```
