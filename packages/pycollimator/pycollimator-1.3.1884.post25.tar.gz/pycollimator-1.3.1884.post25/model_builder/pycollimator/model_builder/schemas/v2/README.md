# v2 schemas

An experimental approach to generating schemas and Go types from
TypeScript definitions.

## Generate files

Just run `make`.make

### Why not bazel?

Bazel is not good for this use case: we want to generate files in repo,
not only in bazel cache folders.

### Why not bash?

Bash makes the whole process too slow because it will regenerate files
even if the sources weren't changed.

I'm happy to use something better than Makefile but this was the
fastest solution for me.
