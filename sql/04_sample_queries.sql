-- View all published rule sets
SELECT *
FROM config.tax_rule_sets
WHERE status = 'PUBLISHED'
ORDER BY rule_set_id, version DESC;

-- BA-friendly filter view
SELECT
    f.filter_id,
    f.filter_name,
    f.logical_operator,
    c.sequence,
    c.source_type,
    c.source_name,
    c.comparison_operator,
    c.comparison_source_type,
    c.comparison_value,
    c.data_type
FROM config.tax_filters f
JOIN config.tax_filter_conditions c
    ON f.rule_set_id = c.rule_set_id
   AND f.version = c.version
   AND f.filter_id = c.filter_id
WHERE f.rule_set_id = 'UK_TAX_2026'
  AND f.version = 1
ORDER BY f.filter_id, c.sequence;

-- BA-friendly decision view
SELECT
    decision_id,
    description,
    filter_id,
    expected_filter_result,
    tax_code,
    result_reason,
    priority,
    enabled
FROM config.tax_decisions
WHERE rule_set_id = 'UK_TAX_2026'
  AND version = 1
ORDER BY priority DESC;

-- Rule dependency view
SELECT
    filter_id AS dependent_filter,
    source_name AS required_filter
FROM config.tax_filter_conditions
WHERE rule_set_id = 'UK_TAX_2026'
  AND version = 1
  AND source_type = 'FILTER'
ORDER BY dependent_filter, required_filter;
