# Known issues and screening decisions

Cases flagged under the screening criteria in [README.md](README.md), with the disposition of each. All discovery came from a full audit of both suites against the criteria; the two buckets differ only in what we could do about it — v1 is locked, and v2 was still unlocked at audit time (it has since been locked, after the removals below).

## v1 — preserved (locked)

Recorded v1 scores include these cases. They are kept and documented here as known caveats, not silently fixed, because modifying locked content would invalidate every recorded number.

### `incident_severity` — "Push notifications are arriving several hours late."

- Gold: `1` (low impact; a workaround exists).
- The state names no workaround; the rating rests on an unstated assumption (e.g. "check the app instead"). Under the criteria as written, `2` (degraded core feature, no easy workaround) is equally defensible — careful annotators split.

### `incident_severity` — "Search results are stale until the user manually refreshes the page."

- Gold: `2` (major annoyance; degraded core feature with no easy workaround).
- The state *names* the workaround (manual refresh). By the task's own criteria, level 1 is "a workaround exists", so the label contradicts the question's definitions.

## v2 — removed from `v2.toml`

Removed during pre-lock review. The pre-lock v2 runs (`results/v1v2-*.json` and
`results/historical/` — the GLiNER2, Laya, Jev, and Von 1.0.x rows) predate these removals and still
include all three cases;
`results/benchmark.md` marks the affected task rows with †.

### `grammar_issue` — "I could care less about the results." (was `word_choice`)

- "Could care less" is an established idiom in careful usage guides; a meticulous editor can defensibly mark the sentence `none`, so `word_choice` was not uniquely defensible.

### `commit_intent` — "Remove the deprecated v1 client" (was `refactor`)

- Under the task's own criteria, `chore` ("tooling, dependencies, CI, and other housekeeping") is at least as defensible as `refactor`, and conventional-commit practice splits exactly here. Not decidable either way.

### `fair_housing_violation` — "Apartment available to female tenants only." (was `true`)

- The question's stated protected classes (race, religion, national origin, familial status, disability) omit sex. Answering with the rule as given yields `false`; the gold relied on the real federal statute instead. As written, the case's own text and its label disagreed. (If it is ever resurrected, either add sex to the instructions or keep the gold consistent with the stated rule.)
