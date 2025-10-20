CREATE OR REPLACE TABLE `lily-demo-ml.churn.agg_input_table` AS
WITH user_first_payment AS (
  SELECT
    user_id,
    MIN(date) AS first_payment_date
  FROM `churney-tech-interview-project.interview_sql_datasets.monthly_payments`
  GROUP BY user_id
),
data_window AS (
  -- Define observation window: exclude last 32 days to allow proper churn observation
  SELECT
    MAX(date) AS data_end_date,
    TIMESTAMP_SUB(MAX(date), INTERVAL 32 DAY) AS observation_cutoff
  FROM `churney-tech-interview-project.interview_sql_datasets.monthly_payments`
),
payment_features AS (
  SELECT
    mp.user_id,
    mp.date,
    ufp.first_payment_date,
    DATE_DIFF(DATE(mp.date), DATE(ufp.first_payment_date), MONTH) AS months_since_signup,
    EXTRACT(MONTH FROM mp.date) AS calendar_month,
    EXTRACT(MONTH FROM ufp.first_payment_date) AS signup_month,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY mp.user_id ORDER BY mp.date) = 1
         THEN 1 ELSE 0 END AS is_first_month

  FROM `churney-tech-interview-project.interview_sql_datasets.monthly_payments` mp
  INNER JOIN user_first_payment ufp
    ON mp.user_id = ufp.user_id
  CROSS JOIN data_window dw
  WHERE mp.date <= dw.observation_cutoff
),
churn_target AS (
  SELECT
    a.user_id,
    a.date AS payment_date,
    CASE
      -- No next payment within 32 days = churn
      WHEN COUNT(b.date) = 0 THEN 1
      -- Has next payment within 32 days = active
      ELSE 0
    END AS is_churn,
    MAX(b.date) AS next_payment_date,
    DATE_DIFF(DATE(MAX(b.date)), DATE(a.date), DAY) AS days_to_next_payment
  FROM `churney-tech-interview-project.interview_sql_datasets.monthly_payments` a
  LEFT JOIN `churney-tech-interview-project.interview_sql_datasets.monthly_payments` b
    ON a.user_id = b.user_id
    AND b.date > a.date
    AND b.date <= TIMESTAMP_ADD(a.date, INTERVAL 32 DAY)
  CROSS JOIN data_window dw
  WHERE a.date <= dw.observation_cutoff
  GROUP BY a.user_id, a.date
)

SELECT
  pf.user_id,
  pf.date AS payment_date,

  -- Original user features
  u.f_0,
  u.f_1,
  u.f_2,
  u.f_3,
  u.f_4,

  -- New features
  pf.months_since_signup,
  pf.calendar_month,
  pf.signup_month,
  pf.is_first_month,
  ct.is_churn,
  CASE
    WHEN ct.is_churn = 1 THEN 'churned'
    ELSE 'active'
  END AS status
FROM payment_features pf
LEFT JOIN `churney-tech-interview-project.interview_sql_datasets.user_table` u
  ON pf.user_id = u.user_id
LEFT JOIN churn_target ct
  ON pf.user_id = ct.user_id
  AND pf.date = ct.payment_date
ORDER BY pf.user_id, pf.date;
