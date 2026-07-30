CREATE TABLE IF NOT EXISTS config.tax_rule_sets (
    rule_set_id STRING NOT NULL,
    rule_set_name STRING NOT NULL,
    version INT NOT NULL,
    status STRING NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_by STRING,
    approved_by STRING,
    created_at TIMESTAMP,
    published_at TIMESTAMP
)
USING DELTA;

CREATE TABLE IF NOT EXISTS config.tax_rule_parameters (
    rule_set_id STRING NOT NULL,
    version INT NOT NULL,
    parameter_name STRING NOT NULL,
    parameter_value STRING NOT NULL,
    data_type STRING NOT NULL,
    description STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS config.tax_filters (
    rule_set_id STRING NOT NULL,
    version INT NOT NULL,
    filter_id STRING NOT NULL,
    filter_name STRING NOT NULL,
    description STRING,
    logical_operator STRING NOT NULL,
    enabled BOOLEAN NOT NULL
)
USING DELTA;

CREATE TABLE IF NOT EXISTS config.tax_filter_conditions (
    rule_set_id STRING NOT NULL,
    version INT NOT NULL,
    condition_id STRING NOT NULL,
    filter_id STRING NOT NULL,
    sequence INT NOT NULL,
    source_type STRING NOT NULL,
    source_name STRING NOT NULL,
    comparison_operator STRING NOT NULL,
    comparison_source_type STRING,
    comparison_value STRING,
    data_type STRING NOT NULL,
    enabled BOOLEAN NOT NULL
)
USING DELTA;

CREATE TABLE IF NOT EXISTS config.tax_decisions (
    rule_set_id STRING NOT NULL,
    version INT NOT NULL,
    decision_id STRING NOT NULL,
    description STRING,
    filter_id STRING NOT NULL,
    expected_filter_result BOOLEAN NOT NULL,
    tax_code STRING NOT NULL,
    result_reason STRING NOT NULL,
    priority INT NOT NULL,
    enabled BOOLEAN NOT NULL
)
USING DELTA;
