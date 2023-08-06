# Schemas

In [instances](instances) you can find the schemas describing a simulation
model as saved in the database, used by the frontend or by the simulation
engines.

In [block-class](block-class.schema.json) and [blocks/core](blocks/core), you
can find the class definition of the blocks, i.e. the blocks static properties.
Those should be sufficient to auto-generate most of the code related to
handling of those blocks (name, types, feedthrough, etc...).

In [other](other) are definitions for other schemas that aren't part of
a model.

## Limitations

1. Don't use `#/definitions`: this is somehow not supported by `oapi-codegen`.
As a consequence, all types that need a fully-qualified name need to be specified
in their own separate `.schema.json` file.
