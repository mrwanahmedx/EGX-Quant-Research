# Security Policy

## Scope

This repository contains public quantitative-research code and metadata only. It is not intended to store credentials, private financial records, employer information or proprietary datasets.

## Reporting a problem

If you notice a committed secret, private record, confidential file, or other sensitive material:

1. do not copy or redistribute it,
2. report the affected path and commit privately to the repository owner,
3. rotate any exposed credential immediately,
4. remove the material from Git history where required,
5. review downstream forks / caches if the exposure was public.

## Automated controls

CI runs scripts/check_public_boundary.py to reject common sensitive file types, credential filenames, private-key markers and unapproved CSV locations. Automated scanning is a guardrail, not proof that content is safe. Human review remains required.
