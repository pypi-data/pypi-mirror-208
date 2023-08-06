#!/usr/bin/env python3

import pycollimator.model_builder.id as id


def _autolayout(model):
    uiprops = {}

    h_spacing = 100
    v_spacing = 100

    def _process_node(node, x, y):
        uiprops[node.id] = {
            "x": x,
            "y": y,
            "show_port_name_labels": node.typename == "core.ReferenceSubmodel",
        }

        # layout all incoming nodes
        n_input = len(node.input_names)
        start_y = y - (n_input - 1) * v_spacing / 2
        for i in range(n_input):
            inport = node.input_port(i)

            if inport not in model.links:
                continue

            in_node = model.links[inport].dst.node
            if in_node.id in uiprops:
                continue
            uiprops[in_node.id] = {
                "x": x - h_spacing,
                "y": start_y + i * v_spacing,
            }

    x, y = 0, 0
    for node in model.nodes.values():
        if node.id in uiprops:
            continue
        _process_node(node, x, y)
        x += 100

    for link in model.links.values():
        uiprops[link.id] = {
            "link_type": {"connection_method": "direct_to_block"},
            "segments": [],
        }

    return uiprops


def handle_reference_submodel_node(model, node, node_json):
    """Additional handling for ReferenceSubmodel nodes"""
    node_json["submodel_reference_uuid"] = model.submodels[node].uuid
    node_json["parameters"].update({k: {"order": i, "value": v} for i, (k, v) in enumerate(node.params.items())})


def render_diagram(model, uiprops):
    if uiprops is None:
        uiprops = _autolayout(model)

    nodes = []
    for node in model.nodes.values():
        nodes.append(render_node(node, uiprops[node.id]))
        if node.typename == "core.ReferenceSubmodel":
            handle_reference_submodel_node(model, node, nodes[-1])

    return {
        "nodes": nodes,
        "links": [render_link(l, uiprops[l.id]) for l in model.links.values()],
        "annotations": [],
    }


def _render_model(model, reference_submodels, groups, uuids=None, uiprops=None, is_submodel=False):
    if uuids:
        id.Id.set_uuid_mapping(uuids)

    if is_submodel:
        groups = {"diagrams": {}, "references": {}}

    for node, group in model.groups.items():
        group_json = _render_model(group, reference_submodels, groups, uuids=uuids, uiprops=uiprops, is_submodel=False)
        groups["diagrams"][group.uuid] = group_json["diagram"]  # render_diagram(group, uiprops)
        groups["references"][node.uuid] = {"diagram_uuid": group.uuid}

    parameters = None
    if is_submodel:
        parameters = [
            {"name": k, "default_value": v, "uuid": id._to_uuid(f"{model.uuid}-{k}")}  # TODO: do we need uuid?
            for k, v in model.parameters.items()
        ]
    else:
        parameters = {k: {"value": v} for k, v in model.parameters.items()}

    reference_submodels.update(
        {
            submodel.uuid: _render_model(
                submodel, reference_submodels, groups, uuids=uuids, uiprops=uiprops, is_submodel=True
            )
            for submodel in model.submodels.values()
        }
    )

    return {
        "name": model.name,
        "uuid": model.uuid,
        "diagram": render_diagram(model, uiprops),
        "submodels": groups if is_submodel else None,
        "parameters": parameters,
        "configuration": model.configuration or {} if not is_submodel else None,
    }


def render_model(model, uuids=None, uiprops=None, is_submodel=False):
    reference_submodels = {}
    groups = {"diagrams": {}, "references": {}}
    model_dict = _render_model(
        model, reference_submodels, groups, uuids=uuids, uiprops=uiprops, is_submodel=is_submodel
    )
    model_dict["reference_submodels"] = reference_submodels
    model_dict["submodels"] = groups
    return model_dict


def render_node(node, uiprops):
    parameters = {}
    for k, v in node.params.items():
        if k not in node.schema.parameter_definitions:
            continue
        if node.schema.parameter_definitions[k].get("data_type", "any") == "string":
            parameters[k] = {"value": str(v), "is_string": True}
        else:
            parameters[k] = {"value": str(v)}

    return {
        "name": node.name,
        "uuid": node.uuid,
        "type": node.typename,
        "inputs": [
            # Note: not including kind, not useful
            {
                "name": name,
            }
            for name in node.input_names
        ],
        "outputs": [
            # Note: not including kind, not useful
            {"name": name}
            for name in node.output_names
        ],
        "parameters": parameters,
        "uiprops": uiprops,
    }


def render_link(link, uiprops):
    src, dst = link.src, link.dst
    return {
        "uuid": link.uuid,
        "name": f"{src.node.name}.{src.name} -> {dst.node.name}.{dst.name}",
        "src": {
            "node": src.node.uuid,
            "port": src.index,
            "node_name": src.node.name,
            "port_name": src.name,
        },
        "dst": {
            "node": dst.node.uuid,
            "port": dst.index,
            "node_name": dst.node.name,
            "port_name": dst.name,
        },
        "uiprops": uiprops,
    }
