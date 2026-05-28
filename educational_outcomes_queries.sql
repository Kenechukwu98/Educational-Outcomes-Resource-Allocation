-- ============================================================
-- Educational Outcomes & Resource Allocation
-- SQL Database Schema + Analysis Queries
-- Dataset: 100 Schools | 5 Regions | 3 School Types
-- ============================================================


-- ============================================================
-- SECTION 1: DATABASE SCHEMA
-- ============================================================

-- Drop tables if they exist (safe re-run)
DROP TABLE IF EXISTS performance_metrics;
DROP TABLE IF EXISTS school_resources;
DROP TABLE IF EXISTS schools;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS school_types;

-- Reference table: regions
CREATE TABLE regions (
    region_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE
);

-- Reference table: school types
CREATE TABLE school_types (
    type_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name   TEXT NOT NULL UNIQUE   -- 'Public', 'Private', 'Charter'
);

-- Core table: schools
CREATE TABLE schools (
    school_id   INTEGER PRIMARY KEY,    -- matches Student_ID in dataset
    school_name TEXT NOT NULL,
    region_id   INTEGER NOT NULL REFERENCES regions(region_id),
    type_id     INTEGER NOT NULL REFERENCES school_types(type_id),
    enrollment  INTEGER NOT NULL
);

-- Resource metrics per school
CREATE TABLE school_resources (
    school_id                  INTEGER PRIMARY KEY REFERENCES schools(school_id),
    num_teachers               INTEGER,
    student_teacher_ratio      REAL,
    budget_per_student_usd     REAL,
    library_books              INTEGER,
    num_computers              INTEGER,
    computer_student_ratio     REAL,
    extracurricular_programs   INTEGER,
    avg_teacher_experience_yrs REAL,
    teacher_qualification_pct  REAL    -- % teachers with advanced degree
);

-- Performance/outcome metrics per school
CREATE TABLE performance_metrics (
    school_id           INTEGER PRIMARY KEY REFERENCES schools(school_id),
    attendance_rate_pct REAL,
    dropout_rate_pct    REAL,
    avg_test_score      REAL,
    graduation_rate_pct REAL,
    pass_rate_pct       REAL,
    stem_score          REAL,
    literacy_score      REAL
);

-- Indexes for common filter/join patterns
CREATE INDEX idx_schools_region   ON schools(region_id);
CREATE INDEX idx_schools_type     ON schools(type_id);
CREATE INDEX idx_resources_budget ON school_resources(budget_per_student_usd);
CREATE INDEX idx_resources_ratio  ON school_resources(student_teacher_ratio);
CREATE INDEX idx_perf_score       ON performance_metrics(avg_test_score);
CREATE INDEX idx_perf_grad        ON performance_metrics(graduation_rate_pct);


-- ============================================================
-- SECTION 2: SEED REFERENCE DATA
-- ============================================================

INSERT INTO regions (region_name) VALUES
    ('North'), ('South'), ('East'), ('West'), ('Central');

INSERT INTO school_types (type_name) VALUES
    ('Public'), ('Private'), ('Charter');


-- ============================================================
-- SECTION 3: LOAD MAIN DATA
-- (Paste or import from CSV — sample rows shown below)
-- When loading from the .xlsx / .csv, map columns as follows:
--   Student_ID          → school_id
--   School_Name         → school_name
--   Region              → JOIN regions
--   School_Type         → JOIN school_types
--   Enrollment          → enrollment
-- ============================================================

-- Example single-row insert (repeat for all 100 rows):
INSERT INTO schools VALUES (1, 'Riverside High',
    (SELECT region_id FROM regions WHERE region_name='North'),
    (SELECT type_id   FROM school_types WHERE type_name='Charter'), 763);

INSERT INTO school_resources VALUES
    (1, 41, 18.6, 2950.87, 2179, 366, 0.48, 18, 3.1, 71.1);

INSERT INTO performance_metrics VALUES
    (1, 70.9, 3.7, 76.9, 87.9, 69.9, 79.3, 77.6);

-- (In practice, use .import or a Python script to bulk-load all 100 rows)


-- ============================================================
-- SECTION 4: DESCRIPTIVE ANALYSIS QUERIES
-- ============================================================

-- Q1. Full school profile join (most useful base view)
CREATE VIEW v_school_full AS
SELECT
    s.school_id,
    s.school_name,
    r.region_name                     AS region,
    st.type_name                      AS school_type,
    s.enrollment,
    sr.num_teachers,
    sr.student_teacher_ratio,
    sr.budget_per_student_usd,
    sr.library_books,
    sr.num_computers,
    sr.computer_student_ratio,
    sr.extracurricular_programs,
    sr.avg_teacher_experience_yrs,
    sr.teacher_qualification_pct,
    pm.attendance_rate_pct,
    pm.dropout_rate_pct,
    pm.avg_test_score,
    pm.graduation_rate_pct,
    pm.pass_rate_pct,
    pm.stem_score,
    pm.literacy_score
FROM schools s
JOIN regions      r  ON s.region_id = r.region_id
JOIN school_types st ON s.type_id   = st.type_id
JOIN school_resources    sr ON s.school_id = sr.school_id
JOIN performance_metrics pm ON s.school_id = pm.school_id;


-- Q2. Overall descriptive statistics
SELECT
    ROUND(AVG(avg_test_score),    2) AS mean_test_score,
    ROUND(MIN(avg_test_score),    2) AS min_test_score,
    ROUND(MAX(avg_test_score),    2) AS max_test_score,
    ROUND(AVG(graduation_rate_pct), 2) AS mean_grad_rate,
    ROUND(AVG(dropout_rate_pct),    2) AS mean_dropout_rate,
    ROUND(AVG(pass_rate_pct),       2) AS mean_pass_rate,
    COUNT(*)                          AS total_schools
FROM v_school_full;


-- Q3. Average outcomes by school type
SELECT
    school_type,
    COUNT(*)                               AS n_schools,
    ROUND(AVG(avg_test_score),         2)  AS avg_score,
    ROUND(AVG(graduation_rate_pct),    2)  AS avg_grad_rate,
    ROUND(AVG(pass_rate_pct),          2)  AS avg_pass_rate,
    ROUND(AVG(dropout_rate_pct),       2)  AS avg_dropout,
    ROUND(AVG(budget_per_student_usd), 0)  AS avg_budget,
    ROUND(AVG(attendance_rate_pct),    2)  AS avg_attendance
FROM v_school_full
GROUP BY school_type
ORDER BY avg_score DESC;


-- Q4. Average outcomes by region
SELECT
    region,
    COUNT(*)                               AS n_schools,
    ROUND(AVG(avg_test_score),         2)  AS avg_score,
    ROUND(AVG(graduation_rate_pct),    2)  AS avg_grad_rate,
    ROUND(AVG(budget_per_student_usd), 0)  AS avg_budget,
    ROUND(AVG(dropout_rate_pct),       2)  AS avg_dropout
FROM v_school_full
GROUP BY region
ORDER BY avg_score DESC;


-- Q5. Budget tier analysis
SELECT
    CASE
        WHEN budget_per_student_usd < 3125  THEN '1. Low ($1.5k-$3.1k)'
        WHEN budget_per_student_usd < 4750  THEN '2. Mid-Low ($3.1k-$4.7k)'
        WHEN budget_per_student_usd < 6375  THEN '3. Mid-High ($4.7k-$6.3k)'
        ELSE                                     '4. High ($6.3k-$8.0k)'
    END AS budget_tier,
    COUNT(*)                               AS n_schools,
    ROUND(AVG(avg_test_score),         2)  AS avg_score,
    ROUND(AVG(graduation_rate_pct),    2)  AS avg_grad_rate,
    ROUND(AVG(pass_rate_pct),          2)  AS avg_pass_rate
FROM v_school_full
GROUP BY budget_tier
ORDER BY budget_tier;


-- Q6. Student–teacher ratio tier analysis
SELECT
    CASE
        WHEN student_teacher_ratio <= 10  THEN '1. Excellent (≤10:1)'
        WHEN student_teacher_ratio <= 20  THEN '2. Good (10–20:1)'
        WHEN student_teacher_ratio <= 35  THEN '3. Average (20–35:1)'
        ELSE                                   '4. Poor (>35:1)'
    END AS ratio_tier,
    COUNT(*)                               AS n_schools,
    ROUND(AVG(avg_test_score),         2)  AS avg_score,
    ROUND(AVG(graduation_rate_pct),    2)  AS avg_grad_rate,
    ROUND(AVG(dropout_rate_pct),       2)  AS avg_dropout
FROM v_school_full
GROUP BY ratio_tier
ORDER BY ratio_tier;


-- ============================================================
-- SECTION 5: RANKING & TOP/BOTTOM QUERIES
-- ============================================================

-- Q7. Top 10 schools by test score
SELECT
    school_id,
    school_name,
    region,
    school_type,
    avg_test_score,
    graduation_rate_pct,
    budget_per_student_usd,
    student_teacher_ratio
FROM v_school_full
ORDER BY avg_test_score DESC
LIMIT 10;


-- Q8. Bottom 10 schools by test score
SELECT
    school_id,
    school_name,
    region,
    school_type,
    avg_test_score,
    graduation_rate_pct,
    student_teacher_ratio,
    budget_per_student_usd
FROM v_school_full
ORDER BY avg_test_score ASC
LIMIT 10;


-- Q9. Schools with high budget but low scores (resource waste flag)
SELECT
    school_name,
    region,
    school_type,
    ROUND(budget_per_student_usd, 0) AS budget,
    avg_test_score,
    student_teacher_ratio
FROM v_school_full
WHERE budget_per_student_usd > 6000
  AND avg_test_score < 75
ORDER BY avg_test_score ASC;


-- Q10. Schools with low budget but high scores (efficiency stars)
SELECT
    school_name,
    region,
    school_type,
    ROUND(budget_per_student_usd, 0) AS budget,
    avg_test_score,
    student_teacher_ratio
FROM v_school_full
WHERE budget_per_student_usd < 3500
  AND avg_test_score > 80
ORDER BY avg_test_score DESC;


-- ============================================================
-- SECTION 6: ADVANCED ANALYSIS QUERIES
-- ============================================================

-- Q11. Percentile ranking of each school by test score
SELECT
    school_name,
    region,
    avg_test_score,
    ROUND(
        100.0 * (RANK() OVER (ORDER BY avg_test_score) - 1)
        / (COUNT(*) OVER () - 1), 1
    ) AS percentile_rank
FROM v_school_full
ORDER BY percentile_rank DESC;


-- Q12. Schools above average in BOTH score and graduation rate
SELECT
    school_name,
    region,
    school_type,
    avg_test_score,
    graduation_rate_pct,
    budget_per_student_usd
FROM v_school_full
WHERE avg_test_score    > (SELECT AVG(avg_test_score)    FROM performance_metrics)
  AND graduation_rate_pct > (SELECT AVG(graduation_rate_pct) FROM performance_metrics)
ORDER BY avg_test_score DESC;


-- Q13. Correlation proxy — contingency of budget tier vs score tier
-- (Use in Python for actual Pearson r; this gives a cross-tab)
SELECT
    CASE
        WHEN budget_per_student_usd < 3125 THEN 'Low Budget'
        WHEN budget_per_student_usd < 6375 THEN 'Mid Budget'
        ELSE 'High Budget'
    END AS budget_cat,
    CASE
        WHEN avg_test_score < 70 THEN 'Low Score (<70)'
        WHEN avg_test_score < 88 THEN 'Mid Score (70-88)'
        ELSE 'High Score (>88)'
    END AS score_cat,
    COUNT(*) AS n
FROM v_school_full
GROUP BY budget_cat, score_cat
ORDER BY budget_cat, score_cat;


-- Q14. STEM vs Literacy gap by school type
SELECT
    school_type,
    ROUND(AVG(stem_score),     2) AS avg_stem,
    ROUND(AVG(literacy_score), 2) AS avg_literacy,
    ROUND(AVG(stem_score) - AVG(literacy_score), 2) AS stem_literacy_gap
FROM v_school_full
GROUP BY school_type
ORDER BY stem_literacy_gap DESC;


-- Q15. Multi-metric school health scorecard
-- Composite score: avg of normalised test, grad, pass, attendance (all scaled 0-1)
SELECT
    school_name,
    region,
    school_type,
    ROUND(avg_test_score,         1) AS score,
    ROUND(graduation_rate_pct,    1) AS grad_rate,
    ROUND(pass_rate_pct,          1) AS pass_rate,
    ROUND(attendance_rate_pct,    1) AS attendance,
    ROUND(dropout_rate_pct,       1) AS dropout,
    ROUND(
        (avg_test_score / 98.0 * 0.4)
      + (graduation_rate_pct / 99.0 * 0.3)
      + (pass_rate_pct / 92.4 * 0.2)
      + (attendance_rate_pct / 98.5 * 0.1)
      , 3
    ) AS composite_health_score
FROM v_school_full
ORDER BY composite_health_score DESC
LIMIT 20;


-- Q16. Flag at-risk schools (dropout > 10% AND score < 75)
SELECT
    school_name,
    region,
    school_type,
    dropout_rate_pct,
    avg_test_score,
    budget_per_student_usd,
    student_teacher_ratio,
    'AT RISK' AS flag
FROM v_school_full
WHERE dropout_rate_pct > 10
  AND avg_test_score < 75
ORDER BY dropout_rate_pct DESC;


-- ============================================================
-- END OF FILE
-- ============================================================
