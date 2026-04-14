# Design Decisions: BigQuery Schema Migrator

This document outlines the architectural decisions and trade-offs made during the implementation of the schema migration tool.

## 1. Architectural Approach
The tool follows a **Source of Truth** pattern where the Python `SQLModel` definitions are considered the master state. The BigQuery schema is treated as the target that must be reconciled.

### Key Trade-offs:
* **Static vs. Live Comparison**: I chose to compare the models against a JSON snapshot of the BigQuery schema (`bigquery_schema.json`). 
    * **Benefit**: This allows the tool to run in CI/CD environments without requiring active Google Cloud credentials or a live database connection for every check.
    * **Trade-off**: The tool is only as accurate as the last exported JSON snapshot.

## 2. Safety and Data Integrity
The primary requirement was to ensure "Safe DDL." 

### Decisions:
* **Non-destructive by Default**: The script explicitly avoids generating `DROP COLUMN` or `DROP TABLE` statements. These are flagged as `WARNING` logs to ensure a human reviewer must decide how to handle orphaned data.
* **Type Narrowing**: Changes that could lead to data truncation (e.g., changing a `STRING` to a more restrictive type or making a `NULLABLE` column `REQUIRED`) are flagged as destructive warnings rather than being automated.
* **Manual Backfill Alerts**: BigQuery handles `ADD COLUMN` well, but adding a required column with a default value to an existing table often requires a manual DML `UPDATE` to populate historical rows. The tool flags these instances to prevent production runtime errors.

## 3. Tooling and Package Management
I selected **uv** as the package manager for this project.

### Why uv?
* **Speed**: In a CI/CD context, `uv` installs dependencies significantly faster than standard `pip`.
* **Determinism**: Using `uv.lock` ensures that the exact same versions of `SQLModel` and `SQLAlchemy` are used in development and in the GitHub Actions runner.
* **Workflow Integration**: `uv run` handles virtual environment management transparently, simplifying the CI configuration.

## 4. Communication and Logging
I replaced standard `print()` statements with the Python `logging` module.

### Benefits:
* **Severity Levels**: Using `logger.info()` for safe operations and `logger.warning()` for drift/destructive changes allows for better filtering in production logs.
* **Standardization**: Logging provides consistent formatting (timestamps, log levels), which is essential for auditing migration history.

## 5. Type Mapping and Normalization
BigQuery and SQLAlchemy use slightly different naming conventions for types.

### Decisions:
* **Normalization Map**: I implemented a normalization layer to treat `BOOLEAN` and `BOOL` (or `INTEGER` and `INT64`) as equivalents. This prevents the tool from generating "false positive" drift warnings for types that are functionally identical in BigQuery.
* **Fallback to String**: If a complex custom type is encountered that isn't in the mapping, the tool defaults to `STRING` to avoid crashing, while logging the mismatch for developer review.

## 6. CI/CD Integration
The GitHub Actions workflow is configured to run on all branches. 

### Rationale:
By running on every push, we shift the "schema review" left in the development lifecycle. Developers receive immediate feedback on whether their model changes will require a complex migration before they even open a Pull Request to the `main` branch.