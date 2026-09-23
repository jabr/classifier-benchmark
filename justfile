default:
  @just --list

# Download a HuggingFace model snapshot into models/<org>/<name>
# e.g.: just download wfzyx/von
@download model:
  uv run python -c "import sys, pathlib; from huggingface_hub import snapshot_download; repo = sys.argv[1]; out = pathlib.Path('models') / repo; snapshot_download(repo, local_dir=out); print(f'{repo} -> {out}')" "{{model}}"

# Validate suite data files, invariants, and locked content hashes
@validate:
  uv run python -m bench.validate

# Lock a reviewed suite (one-time transition): write its digest to cases/hashes.json
# e.g.: just lock v2
@lock *suites:
  uv run python -m bench.validate --lock {{suites}}

# Generate a real-data sample suite from an external source (see sources/README.md)
# e.g.: just gen cfpb --seed 48620
@gen *args:
  uv run python -m sources.generate {{args}}
