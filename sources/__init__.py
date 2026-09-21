"""Real-data sample suites: external datasets -> bench TOML samples.

Everything lives in sources/: the source modules convert dataset records into
System One tasks, sources.generate samples a balanced subset with a seed,
freezes it as a suite TOML in sources/samples/, and stamps it with provenance.
The committed sample file is the stable artifact; the seed only reproduces a
selection over a source snapshot (dataset drift is possible — see
sources/README.md). Samples are auto-discovered as unlocked suites by
bench/suites.py, excluded from `--suite all`, and selected with `--sample`.
"""
