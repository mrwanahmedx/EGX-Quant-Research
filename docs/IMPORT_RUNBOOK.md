# Evidence Import Runbook

The repository is ready to consume the missing original evidence artifacts, but it must not recreate them from narrative summaries.

## 1. Exact quarantine register

Required input: the original machine-readable CSV produced by the reconciliation work.

Expected current count: **47 exact ticker/date ranges**.

Run:

```bash
python scripts/import_quarantine_register.py /path/to/original_register.csv
```

The importer will:

1. parse the CSV using the repository contract,
2. require exactly 47 ranges by default,
3. reject duplicate quarantine IDs,
4. reject ranges crossing the frozen development cutoff,
5. require evidence references,
6. require an accepted source when the disposition is an override,
7. copy and re-parse the destination artifact,
8. only then mark the reconciliation summary as having an exact register.

Do not alter the expected count merely to make an incomplete file pass.

## 2. Point-in-time security master

Required input: a dated security-identity file backed by historical evidence.

Run:

```bash
python scripts/import_security_master.py /path/to/security_master.json
```

Default decision time:

```text
2026-01-31T23:59:59+02:00
```

The importer rejects:

- mappings first published after that decision time,
- mappings whose effective period begins after the development cutoff,
- unresolved identity mappings,
- sector evidence first published after the decision time,
- duplicate identity/effective-date grain.

Current-style metadata can help reconcile names and symbols, but cannot become historical point-in-time evidence merely by being imported.

## 3. Readiness check

After importing evidence:

```bash
python scripts/research_readiness.py
```

The repository should remain blocked until **all** mandatory evidence gates are satisfied. Importing one artifact is not authorization to start modeling.

## 4. Freeze row-level evidence

Once quarantine, security identity, benchmark and corporate-action evidence are complete, build one row-level evidence record per intended security/date grain and freeze it with:

```bash
python scripts/freeze_evidence_manifest.py \
  --evidence /path/to/evidence_rows.json \
  --quarantine-register evidence/quarantine_register.csv \
  --decision-time 2026-01-31T23:59:59+02:00 \
  --code-ref COMMIT_SHA \
  --output evidence/frozen_preholdout_manifest.json
```

The manifest may authorize real development only when every included row passes the evidence contract.

## 5. Holdout rule

None of these import steps require or permit inspection of February-June 2026 holdout observations.

The correct sequence remains:

```text
recover evidence -> validate -> freeze development panel -> freeze research specification -> one-shot holdout
```
