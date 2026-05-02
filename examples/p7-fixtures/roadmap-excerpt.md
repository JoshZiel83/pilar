# Roadmap excerpt — post `/pilar:scaffold-pillars`

This file is a fixture excerpt showing the `## Pillars` section that `/pilar:scaffold-pillars` writes into `roadmap.md` after the user approves the proposed pillar set. Not a complete roadmap — the rest of the engagement's roadmap fields are omitted here.

```markdown
## Pillars

| Pillar ID | Slug | Status |
|---|---|---|
| P-01 | unmet-need | draft |
| P-02 | disease-mechanism | draft |
| P-03 | mechanism-of-action | draft |
| P-04 | clinical-evidence | statements-approved |
| P-05 | clinical-value-framework | draft |
```

In this fixture's snapshot, P-04 has been driven through `/pilar:pillar-narrative P-04` and `/pilar:pillar-statements P-04` (see `pillars/p-04-clinical-evidence.md`); the other four pillars are at their `/pilar:scaffold-pillars` initial state. As the engagement progresses, each pillar's row is updated when its status changes (the writer edits the table directly when transitioning status; or in P9-hardening territory, a roadmap-update helper could automate this).
