// ModelOverrides
// The first line must contain the name of the top level schema.
//
// Description: Block overrides schema
//
// This schema is used to override the default values of blocks in a model.

// Using name paths instead of UUID paths makes it much easier to work with
// from pycollimator: users can literally just write the name of the signals
// they want. UUIDs would be more robust but for now we base simulations around
// paths by name.

// The types defined here need some backwards compatibility but only up
// to the next release of pycollimator. The data stored in the database for
// simulation purposes can break without impacting the user experience, because
// we don't allow re-running simulations.

export interface ModelOverrides {
  block_overrides?: BlockOverride[];
  recorded_signals?: RecordedSignals;
}

export interface RecordedSignals {
  signal_ids: SignalID[];
}

// Full human-readable path to the port like:
// - Submodel_1.Group_2.Block_3.out_4
// - Submodel_1.Group_2.Outport_5
// Corresponds to 'signal_id' in toc.json
export type SignalID = string;

export interface BlockOverride {
  path: string;
  parameters?: ParameterOverrides;
  outputs?: PortOverrides;
}

export interface ParameterOverrides {
  [k: string]: ParameterValueOverride;
}

export interface ParameterValueOverride {
  value: string;
  is_string?: boolean;
}

export interface PortOverrides {
  [k: string]: PortOverride;
}

export interface PortOverride {
  parameters?: ParameterOverrides;
}
