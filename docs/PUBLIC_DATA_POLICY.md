# Public-Data and Confidentiality Policy

This repository is intentionally limited to **public, synthetic, or safely derived research material**.

It must never become a place to store employer data, customer data, private brokerage exports, credentials, internal bank models, confidential reports, screenshots from restricted systems, or proprietary datasets.

## Allowed

The repository may contain:

- public market-data interfaces and parsing code,
- small synthetic fixtures,
- sanitized examples that do not reproduce real private records,
- public regulatory / exchange / issuer references,
- machine-readable evidence metadata that contains no confidential source content,
- hashes, row counts and provenance references for local source snapshots,
- public research notes and model-validation code,
- legacy scanner source only when sanitized and reviewed.

## Prohibited

Do not commit:

- employer or customer data,
- internal bank tables, extracts, reports or screenshots,
- internal model parameters or policy documents,
- non-public financial statements or disclosures,
- private brokerage account exports,
- passwords, API keys, tokens, cookies or certificates,
- .env files,
- private keys,
- database files,
- spreadsheets copied from restricted systems,
- raw third-party datasets whose redistribution terms are unclear,
- files containing personally identifiable information.

## Local-only data

Raw research inputs belong outside version control. The intended local structure remains data/raw, data/interim, data/processed, artifacts, and runs. These paths are ignored by Git. Only compact, non-sensitive evidence metadata may be committed.

## Evidence references

Where a local source is needed for reproducibility, commit only metadata such as source name, retrieval timestamp, version or vintage, SHA-256 fingerprint, row count, schema summary, public source URL where appropriate, and QA outcome. A hash proves which local artifact was used without publishing the artifact itself.

## CSV rule

CSV files are allowed only for synthetic examples, evidence templates, and reviewed legacy-scanner fixtures. A new CSV outside those approved locations should fail CI until explicitly reviewed.

## Binary / archive rule

Office files, Power BI files, databases, serialized model/data files, private-key containers and archives are not permitted in this repository. Examples include .xls, .xlsx, .pbix, .db, .sqlite, .parquet, .feather, .pkl, .pickle, .zip, .7z, .rar, .p12, .pfx, .pem and .key.

If a legitimate public artifact must be referenced, store its checksum and provenance rather than the binary itself.

## Secrets

The repository must never contain private keys, GitHub tokens, cloud credentials, broker credentials, or session cookies. A secret discovered in Git history must be treated as compromised and rotated. Removing it from the latest commit is not sufficient.

## Contribution rule

Every pull request must preserve this boundary. If there is uncertainty about whether a file is public-safe, the default action is **do not commit it**.

## Research-integrity distinction

This confidentiality policy is separate from the model-evidence gates. A dataset can be public but still fail research QA. A dataset can be technically useful but still be prohibited from redistribution. Both conditions must be satisfied independently.
