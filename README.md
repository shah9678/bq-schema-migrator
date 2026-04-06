# Take-Home: BigQuery Schema Migration Tool

## Overview

Build a migration tool that detects schema drift between SQLModel definitions and a BigQuery dataset, then generates safe DDL to reconcile them.

You have **1 hour**. Use any AI coding tools available to you (Claude Code, Codex, Copilot, Cursor, etc.). Be prepared to talk through your code in the follow-up interview.

## The Problem

You're responsible for a BigQuery dataset whose schema is defined by SQLModel classes in Python. Over time, the models have been updated but the BigQuery tables haven't always been migrated in sync. The schema has drifted.

The file `data/bigquery_schema.json` contains the current BigQuery schema for each table (as reported by the BigQuery API). The file `models.py` contains the SQLModel definitions that represent the desired state.

Your job is to build a tool that:

1. **Compares** the SQLModel definitions against the BigQuery schema
2. **Detects** differences (missing columns, type mismatches, nullable changes, extra columns)
3. **Generates safe DDL** to reconcile the BigQuery schema to match the models

## Requirements

### Schema Diffing
- Detect added columns (in the model but not in BigQuery)
- Detect removed columns (in BigQuery but not in the model)
- Detect type changes (column exists but type differs)
- Detect nullable changes (column exists but nullable differs)

### Safe DDL Generation
- Generate `ALTER TABLE ... ADD COLUMN` for new columns
- Generate `ALTER TABLE ... ALTER COLUMN` for type/nullable changes where safe
- **Flag destructive changes** (column removals, type narrowing) with a warning rather than generating DDL. Do NOT auto-generate DROP COLUMN statements.
- Output should be human-readable and reviewable before execution

### Edge Cases to Handle
- BigQuery type mapping: SQLModel/Python types need to be mapped to BigQuery types (e.g., `str` -> `STRING`, `Optional[float]` -> `FLOAT64 NULLABLE`, `datetime` -> `TIMESTAMP`)
- A column changing from `Optional` to required (nullable -> non-nullable) on a populated table is potentially destructive — flag it
- New columns with `default` values should be noted in the output

## Resources

- [SQLModel documentation](https://sqlmodel.tiangolo.com/) — SQLModel is a library built on top of SQLAlchemy and Pydantic. If you haven't used it before, the key thing to know is that model classes define both the Pydantic validation schema and the database table schema. You can introspect fields and types using standard SQLAlchemy/Pydantic APIs.

## What's Provided

- `models.py` — 5 SQLModel classes representing the desired schema
- `data/bigquery_schema.json` — the current BigQuery schema (intentionally drifted)
- `migrate.py` — an entry point that loads the models and schema

## Running

```bash
# Install dependencies (pip or uv)
pip install .
# or
uv sync

# Run the migration tool
python migrate.py
```

The tool should print a clear report: what's different, what DDL it would generate, and what changes it's flagging as unsafe.

## What We're Looking For

This is not about volume of code. We value:
- Correctness of the diff logic
- Safety-first approach to migrations (protecting against data loss)
- Clean handling of type mapping edge cases
- Clear, reviewable output
- A `DECISIONS.md` explaining your approach and trade-offs

## Submission

Clone this repo, complete the work, and push it to a private GitHub repo. Add [INTERVIEWER_GITHUB_USERNAME] as a collaborator so we can review your submission before the follow-up interview.
