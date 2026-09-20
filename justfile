default:
  @just --list

# Download a HuggingFace model snapshot into models/<org>/<name>
# e.g.: just download wfzyx/von-1.0
@download model:
  uv run python -c "import sys, pathlib; from huggingface_hub import snapshot_download; repo = sys.argv[1]; out = pathlib.Path('models') / repo; snapshot_download(repo, local_dir=out); print(f'{repo} -> {out}')" "{{model}}"

# Validate suite data files, invariants, and locked content hashes
@validate:
  uv run python -m bench.validate

# Re-lock suite content hashes after a deliberate edit (default: all suites)
# e.g.: just relock v2
@relock *suites:
  uv run python -m bench.validate --relock {{suites}}
