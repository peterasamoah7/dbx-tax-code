# Databricks notebook source
# MAGIC %md
# MAGIC # Configurable Tax Rule Engine Demo
# MAGIC
# MAGIC Run the SQL files first, then install/import the package.

# COMMAND ----------

from datetime import date
import sys

# For a Databricks Repo, adjust this path to the project root.
project_root = "/Workspace/Repos/<user>/configurable_tax_rule_engine"
if project_root not in sys.path:
    sys.path.insert(0, f"{project_root}/src")

from tax_rule_engine import TaxRuleEngine

# COMMAND ----------

employee_data = [
    ("1001", "UK", "Resident", "Employee", 45000.0, False, False),
    ("1002", "UK", "Resident", "Employee", 38000.0, True, False),
    ("1003", "FR", "NonResident", "Employee", 50000.0, False, False),
    ("1004", "UK", "Resident", "Contractor", 60000.0, False, False),
    ("1005", "UK", "Resident", "Employee", 8000.0, False, False),
    ("1006", "UK", "Resident", "Employee", 55000.0, False, True),
]

employee_columns = [
    "employee_id",
    "country",
    "residency_status",
    "employment_type",
    "annual_income",
    "emergency_tax",
    "has_second_job",
]

employee_df = spark.createDataFrame(employee_data, employee_columns)

display(employee_df)

# COMMAND ----------

engine = TaxRuleEngine(spark, database="config")

result_df, warnings = engine.execute(
    employee_df,
    rule_set_id="UK_TAX_2026",
    as_of_date=date(2026, 7, 30),
    keep_filter_columns=True,
)

for warning in warnings:
    print(f"WARNING: {warning}")

# COMMAND ----------

display(
    result_df.select(
        "employee_id",
        "country",
        "residency_status",
        "employment_type",
        "annual_income",
        "emergency_tax",
        "has_second_job",
        "tax_code",
        "tax_code_reason",
        "matched_decision_id",
        "matched_decision_priority",
        "rule_set_id",
        "rule_set_version",
    )
)

# COMMAND ----------

# Full audit view including intermediate filters
display(result_df)

# COMMAND ----------

expected = {
    "1001": "A",
    "1002": "E",
    "1003": "NR",
    "1004": "REVIEW",
    "1005": "NT",
    "1006": "B",
}

actual = {
    row["employee_id"]: row["tax_code"]
    for row in result_df.select("employee_id", "tax_code").collect()
}

assert actual == expected, f"Unexpected results: {actual}"
print("All sample decisions matched the expected output.")
