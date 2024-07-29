---
orphan: true
---

# Updating `source.yaml`

Here we document the steps to required steps to take when updating the `source.yaml` file.

## Steps

1. Adapt the `sources.yaml` file as required.
   Add a new top level entry if you've added a new PublicOntology entity or add a new source/version while confirming to the yaml structure.
2. If you've added a new source or version, use PublicOntology's `diff` function to determine whether any terms were deleted.
   Consult the rest of the team if so.
   Ensure that your pull request contains a summary of the diff.
3. Specify the new entity or the latest version in your local `.current_source.yaml`. Run the tests.
   Upload the corresponding `.parquet` file to our S3.
4. Get the corresponding md5 sum by running the `determine_md5s.py` script in the scripts folder.
   Add it to the md5 field in the `source.yaml`.
5. Merge your PR to main. Ensure that the parquet file got automatically uploaded to our S3.
6. Make a new release based on our release process.
