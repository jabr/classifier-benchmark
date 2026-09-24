# Historical run records

Superseded generations of the benchmark records, kept for the version history and analysis citations
in [`../benchmark.md`](../benchmark.md) and [`../shape-knowledge.md`](../shape-knowledge.md).
Current-generation records live one level up in `results/`. Every file here is one-record-per-run in
the same envelope as the live ones (`{model: {backend, description, cases, suites, suite_summaries,
summary}}`), so `bench/strata.py` and jq workflows work on them unchanged (`RUNS` in `bench/strata.py`
still points at `v1v2-von.json` here, as the Von 1.0.1 column).

| Record | Generation | Scope | Notes |
|---|---|---|---|
| `von.json` | Von 1.0.0 (CPU) | v1 | first Von record: flat ~0.5 noul probabilities, calm-bias on scores |
| `von-mps.json` | Von 1.0.0 (MPS) | v1 | same generation on MPS |
| `von-1.0.1-mps.json` | Von 1.0.1 (Berta NLI engine) | v1 | the 0.923 / 0.930 v1 row |
| `von-1.0.1-cpu.json` | Von 1.0.1 | v1 | accuracy identical to the MPS run; only latency differs |
| `v1v2-von.json` | Von 1.0.1 | v1+v2 | pre-lock 869-case run; used by `bench/strata.py` |
| `v1v2-laya.json` | Laya 0.3.x root | v1+v2 | pre-lock 869-case run; answers identical to `../laya-0.3.17-mps.json` on all 944 locked cases |
| `laya-mps.json` | Laya 0.3.x root | v1 | |
| `laya-cpu.json` | Laya 0.3.x root | v1 | |
| `jev.json` | Jev 1.13 | v1 | superseded by `../v1v2-jev.json` |
| `gliner2-mps.json` | GLiNER2 large | v1 | superseded by `../v1v2-gliner2.json` |

The pre-lock `v1v2-*` records here include the three cases removed before v2 was locked
([`cases/ISSUES.md`](../../cases/ISSUES.md)); the scoreboards in `../benchmark.md` re-derive those
runs onto the locked cases. `gliner2.json` (the v1-era CPU twin of `gliner2-mps.json`, referenced
nowhere) was deleted in the cleanup that created this directory; it remains recoverable from git
history.