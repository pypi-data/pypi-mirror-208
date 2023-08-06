/**
Hand-written typescript definition of the fmi-2.0-modelDescription schema.

fmi-2.0-modelDescription.schema.json was generated from this file with:

    typescript-json-schema \
      fmi-2.0-modelDescription.ts fmiModelDescription \
      > fmi-2.0-modelDescription.schema.json

*/

/**
 * @minimum 0
 * @TJS-type integer
 */
type Size = number;

export interface LogCategory {
  name: string;
  description?: string;
}

/** @default "local" */
export type Causality =
  | 'parameter'
  | 'calculatedParameter'
  | 'input'
  | 'output'
  | 'local'
  | 'independent';

/** @default "continuous" */
export type Variability =
  | 'constant'
  | 'fixed'
  | 'tunable'
  | 'discrete'
  | 'continuous';

/** @default "continuous" */
export type Initial = 'exact' | 'approx' | 'calculated';

/**
 * Schema for our modelDescription.json converted from FMI modelDescription.xml
 * generated with `typescript-json-schema fmi-2.0-modelDescription.ts fmiModelDescription > fmi-2.0-modelDescription.schema.json`
 */
export interface fmiModelDescription {
  fmiVersion: '2.0';
  modelName: string;
  description?: string;
  generationTool: string;
  guid: string;

  /**
   * @minimum 0
   * @TJS-type integer
   */
  numberOfEventIndicators: number;
  ModelExchange?: {
    modelIdentifier: string;
    canNotUseMemoryManagementFunctions: boolean;
    canGetAndSetFMUstate: boolean;
    canSerializeFMUstate: boolean;
  };
  CoSimulation?: {
    modelIdentifier: string;
    canHandleVariableCommunicationStepSize: boolean;
    canNotUseMemoryManagementFunctions: boolean;
    canGetAndSetFMUstate: boolean;
    canSerializeFMUstate: boolean;
  };
  LogCategories?: LogCategory[];
  DefaultExperiment?: {
    startTime?: number;
    stopTime?: number;
    tolerance?: number;
    stepSize?: number;
  };
  ModelVariables: ScalarVariable[];
}

interface ScalarVariableCommon {
  name: string;
  cml_name: string;
  valueReference: Size;
  causality?: Causality;
  variability?: Variability;
  initial?: Initial;
  description?: string;
}
interface ScalarVariableReal extends ScalarVariableCommon {
  Real: Record<string, unknown>;
}
interface ScalarVariableInteger extends ScalarVariableCommon {
  Integer: Record<string, unknown>;
}
interface ScalarVariableBoolean extends ScalarVariableCommon {
  Boolean: Record<string, unknown>;
}
interface ScalarVariableString extends ScalarVariableCommon {
  String: Record<string, unknown>;
}
interface ScalarVariableEnumeration extends ScalarVariableCommon {
  Enumeration: Record<string, unknown>;
}
export type ScalarVariable =
  | ScalarVariableReal
  | ScalarVariableInteger
  | ScalarVariableBoolean
  | ScalarVariableString
  | ScalarVariableEnumeration;
