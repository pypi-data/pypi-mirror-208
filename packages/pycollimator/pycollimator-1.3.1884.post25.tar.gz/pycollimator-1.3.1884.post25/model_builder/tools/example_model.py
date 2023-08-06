from pycollimator.model_builder import core
from pycollimator.model_builder.model import ModelBuilder, OPort, IPort


def create_model():
    ModelBuilder_0 = core.ModelBuilder("Simple Dynamic System", id="ModelBuilder_0")
    Integrator_0 = core.Integrator(
        model=ModelBuilder_0,
        name="Integrator",
        enable_hold="false",
        enable_limits="false",
        enable_reset="false",
        hold_trigger_method="high",
        initial_states="0",
        lower_limit="-1e50",
        reset_trigger_method="rising",
        upper_limit="1.0e50",
        input_names=("in_0",),
        id="Integrator_0",
    )
    Gain_0 = core.Gain(model=ModelBuilder_0, name="Gain", gain="2", id="Gain_0")
    ModelBuilder_0.add_link(OPort(Integrator_0, "out_0"), IPort(Gain_0, "in_0"))
    ModelBuilder_0.add_link(OPort(Gain_0, "out_0"), IPort(Integrator_0, "in_0"))
    return ModelBuilder_0
