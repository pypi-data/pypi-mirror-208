/**
Hand-written typescript definition of the cppblock-modelDescription schema.
Examples can be found in

    src/lib/cml/tests/blocks/CppFunction/*-modelDescription.json

If needed, a json schema can be generated from this file with:

    typescript-json-schema \
      cppblock-modelDescription.ts fmiModelDescription \
      > cppblock-modelDescription.schema.json

This is very similar to the FMI modeldescription schema. Changes:

- One modelDescription contains a list of definitions instead of a single
  definition. Each entry has a name and a version, both arbtirary strings.

- Variables have standard tag fields for their type, e.g. `"type: "float32"`
  instead of `"Real": {}`

- The set of types different: float32, float64, int32, etc. instead of Real,
  Integer. The set describes here matches the FMI 3.0 spec.

- Variables have optional dimensions.
*/

/**
 * @minimum 0
 * @TJS-type integer
 */
type Size = number;

export type Causality = 'parameter' | 'input' | 'output';

export type VarType =
  | 'float64'
  | 'float32'
  | 'int64'
  | 'int32'
  | 'int16'
  | 'int8'
  | 'uint64'
  | 'uint32'
  | 'uint16'
  | 'uint8'
  | 'boolean'
  | 'string';

export interface ModelVariable {
  // display name of the variable; does not have to be a valid identifer
  name: string;
  // name of the variable as used in code; must be a valid identifier
  cname: string;
  // integer identifying the variable
  valueReference: number;
  type: VarType;
  causality: Causality;
  dimensions?: Size[];
  description?: string;
}

export interface cppBlockDefinition {
  name: string;
  description?: string;
  modelVariables: ModelVariable[];
}

export type cppModelDescription = {
  formatVersion: '1.0'; // version of this schema
  sourceFiles: string[]; // list of files that modelDescription was generated from
  blockDefinitions: cppBlockDefinition[];
};
