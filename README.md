# Configurable Tax Rule Engine for Databricks

A complete example project for moving tax-code decision logic out of Python and into BA-managed Delta tables.

The project supports:

- BA-managed rule sets, parameters, filters, conditions, and decisions
- reusable filters
- filters that depend on other filters
- dependency ordering
- circular dependency detection
- `AND` and `OR` filter logic
- column, literal, parameter, and filter references
- priority-based decisions
- effective dating and versioning
- audit columns showing matched decisions and intermediate filter outcomes
- validation before execution
- sample Databricks notebook
- unit tests for non-Spark validation logic

## Project structure

```text
configurable_tax_rule_engine/
├── README.md
├── pyproject.toml
├── requirements.txt
├── config/
│   └── sample_rule_export.json
├── notebooks/
│   └── 01_end_to_end_demo.py
├── sql/
│   ├── 01_create_schema.sql
│   ├── 02_create_tables.sql
│   ├── 03_seed_sample_rules.sql
│   └── 04_sample_queries.sql
├── src/
│   └── tax_rule_engine/
│       ├── __init__.py
│       ├── casting.py
│       ├── dependencies.py
│       ├── engine.py
│       ├── loaders.py
│       ├── models.py
│       ├── operators.py
│       ├── validation.py
│       └── exceptions.py
└── tests/
    ├── test_casting.py
    ├── test_dependencies.py
    └── test_validation.py
```

## Business model

The design separates the rules into these concepts:

- **Rule set**: a published, versioned collection of tax rules
- **Parameter**: a configurable value such as a personal allowance
- **Filter**: a named Boolean business check
- **Condition**: one comparison inside a filter
- **Decision**: maps a filter result to a tax code

Example:

```text
F_UK_RESIDENT
    country = "UK"
    AND residency_status = "Resident"

F_TAXABLE_EMPLOYEE
    employment_type = "Employee"
    AND annual_income > personal_allowance

F_STANDARD_TAX
    F_UK_RESIDENT is true
    AND F_TAXABLE_EMPLOYEE is true
    AND emergency_tax = false
    AND has_second_job = false

Decision D_STANDARD
    when F_STANDARD_TAX is true
    assign tax code A
```

## Databricks setup

Run the SQL files in this order:

```text
sql/01_create_schema.sql
sql/02_create_tables.sql
sql/03_seed_sample_rules.sql
```

Then run:

```text
notebooks/01_end_to_end_demo.py
```

The demo notebook creates sample employee data, loads the published rules, validates them, evaluates filters in dependency order, and assigns the final tax code.

## Expected sample output

| employee_id | tax_code | matched_decision_id |
|---|---|---|
| 1001 | A | D_STANDARD |
| 1002 | E | D_EMERGENCY |
| 1003 | NR | D_NON_RESIDENT |
| 1004 | REVIEW | null |
| 1005 | NT | D_BELOW_ALLOWANCE |
| 1006 | B | D_SECOND_JOB |

## BA workflow

A production workflow should use:

```text
Draft tables or rule editor
        ↓
Validation
        ↓
Approval
        ↓
Published rule set
        ↓
Databricks execution
        ↓
Tax code + explanation + rule version
```

BAs should not directly edit production records. Use a draft/publish process or a controlled application over the Delta tables.

## Rule priority

Higher priority numbers win.

The engine sorts decisions from low to high and lets later, higher-priority matches override earlier matches.

## Null behaviour

A condition that evaluates to SQL `NULL` is treated as `False`. This avoids silently assigning a tax code based on incomplete data.

## Running tests locally

The dependency, casting, and validation tests do not require Spark:

```bash
pip install -r requirements.txt
pytest
```

The PySpark engine itself is intended to run inside Databricks or another Spark environment.
