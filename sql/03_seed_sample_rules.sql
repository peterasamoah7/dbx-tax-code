DELETE FROM config.tax_decisions
WHERE rule_set_id = 'UK_TAX_2026' AND version = 1;

DELETE FROM config.tax_filter_conditions
WHERE rule_set_id = 'UK_TAX_2026' AND version = 1;

DELETE FROM config.tax_filters
WHERE rule_set_id = 'UK_TAX_2026' AND version = 1;

DELETE FROM config.tax_rule_parameters
WHERE rule_set_id = 'UK_TAX_2026' AND version = 1;

DELETE FROM config.tax_rule_sets
WHERE rule_set_id = 'UK_TAX_2026' AND version = 1;

INSERT INTO config.tax_rule_sets VALUES (
    'UK_TAX_2026',
    'Illustrative UK employee tax-code rules',
    1,
    'PUBLISHED',
    DATE '2026-04-06',
    NULL,
    'business.analyst@example.com',
    'tax.manager@example.com',
    current_timestamp(),
    current_timestamp()
);

INSERT INTO config.tax_rule_parameters VALUES
('UK_TAX_2026', 1, 'personal_allowance', '12570', 'DECIMAL',
 'Illustrative annual personal allowance');

INSERT INTO config.tax_filters VALUES
('UK_TAX_2026', 1, 'F_UK_RESIDENT', 'UK Resident',
 'Person is resident in the United Kingdom', 'AND', true),

('UK_TAX_2026', 1, 'F_TAXABLE_EMPLOYEE', 'Taxable Employee',
 'Employee has income above the personal allowance', 'AND', true),

('UK_TAX_2026', 1, 'F_STANDARD_TAX', 'Standard Tax Eligible',
 'Person qualifies for the standard tax code', 'AND', true),

('UK_TAX_2026', 1, 'F_EMERGENCY_TAX', 'Emergency Tax',
 'Emergency tax indicator is active', 'AND', true),

('UK_TAX_2026', 1, 'F_SECOND_JOB', 'Second Job',
 'Employee has a second job and taxable employment income', 'AND', true),

('UK_TAX_2026', 1, 'F_NON_RESIDENT', 'Non Resident',
 'Person is not a UK resident', 'AND', true),

('UK_TAX_2026', 1, 'F_BELOW_ALLOWANCE', 'Below Allowance',
 'Employee income is at or below the configured allowance', 'AND', true);

INSERT INTO config.tax_filter_conditions VALUES
('UK_TAX_2026', 1, 'C001', 'F_UK_RESIDENT', 1,
 'COLUMN', 'country', 'EQUALS', 'LITERAL', 'UK', 'STRING', true),

('UK_TAX_2026', 1, 'C002', 'F_UK_RESIDENT', 2,
 'COLUMN', 'residency_status', 'EQUALS', 'LITERAL', 'Resident', 'STRING', true),

('UK_TAX_2026', 1, 'C003', 'F_TAXABLE_EMPLOYEE', 1,
 'COLUMN', 'employment_type', 'EQUALS', 'LITERAL', 'Employee', 'STRING', true),

('UK_TAX_2026', 1, 'C004', 'F_TAXABLE_EMPLOYEE', 2,
 'COLUMN', 'annual_income', 'GREATER_THAN', 'PARAMETER',
 'personal_allowance', 'DECIMAL', true),

('UK_TAX_2026', 1, 'C005', 'F_STANDARD_TAX', 1,
 'FILTER', 'F_UK_RESIDENT', 'IS_TRUE', NULL, NULL, 'BOOLEAN', true),

('UK_TAX_2026', 1, 'C006', 'F_STANDARD_TAX', 2,
 'FILTER', 'F_TAXABLE_EMPLOYEE', 'IS_TRUE', NULL, NULL, 'BOOLEAN', true),

('UK_TAX_2026', 1, 'C007', 'F_STANDARD_TAX', 3,
 'COLUMN', 'emergency_tax', 'EQUALS', 'LITERAL', 'false', 'BOOLEAN', true),

('UK_TAX_2026', 1, 'C008', 'F_STANDARD_TAX', 4,
 'COLUMN', 'has_second_job', 'EQUALS', 'LITERAL', 'false', 'BOOLEAN', true),

('UK_TAX_2026', 1, 'C009', 'F_EMERGENCY_TAX', 1,
 'COLUMN', 'emergency_tax', 'EQUALS', 'LITERAL', 'true', 'BOOLEAN', true),

('UK_TAX_2026', 1, 'C010', 'F_SECOND_JOB', 1,
 'FILTER', 'F_TAXABLE_EMPLOYEE', 'IS_TRUE', NULL, NULL, 'BOOLEAN', true),

('UK_TAX_2026', 1, 'C011', 'F_SECOND_JOB', 2,
 'COLUMN', 'has_second_job', 'EQUALS', 'LITERAL', 'true', 'BOOLEAN', true),

('UK_TAX_2026', 1, 'C012', 'F_NON_RESIDENT', 1,
 'FILTER', 'F_UK_RESIDENT', 'IS_FALSE', NULL, NULL, 'BOOLEAN', true),

('UK_TAX_2026', 1, 'C013', 'F_BELOW_ALLOWANCE', 1,
 'COLUMN', 'employment_type', 'EQUALS', 'LITERAL', 'Employee', 'STRING', true),

('UK_TAX_2026', 1, 'C014', 'F_BELOW_ALLOWANCE', 2,
 'COLUMN', 'annual_income', 'LESS_THAN_OR_EQUAL', 'PARAMETER',
 'personal_allowance', 'DECIMAL', true);

INSERT INTO config.tax_decisions VALUES
('UK_TAX_2026', 1, 'D_NON_RESIDENT',
 'Assign the non-resident tax code',
 'F_NON_RESIDENT', true, 'NR', 'Person is not UK resident', 100, true),

('UK_TAX_2026', 1, 'D_BELOW_ALLOWANCE',
 'Assign the below-allowance tax code',
 'F_BELOW_ALLOWANCE', true, 'NT',
 'Income is at or below the personal allowance', 150, true),

('UK_TAX_2026', 1, 'D_STANDARD',
 'Assign the standard tax code',
 'F_STANDARD_TAX', true, 'A',
 'UK resident employee with taxable income', 200, true),

('UK_TAX_2026', 1, 'D_SECOND_JOB',
 'Assign the second-job tax code',
 'F_SECOND_JOB', true, 'B',
 'Employee has taxable income and a second job', 300, true),

('UK_TAX_2026', 1, 'D_EMERGENCY',
 'Assign the emergency tax code',
 'F_EMERGENCY_TAX', true, 'E',
 'Emergency tax indicator is active', 400, true);
