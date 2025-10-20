"""
Data loading from BigQuery.
"""
import pandas as pd
from google.cloud import bigquery
from validation import Config


def load_data_from_bigquery(
    config: Config,
) -> pd.DataFrame:
    """
    Load data from BigQuery.

    Args:
        config: Configuration object with BigQuery settings

    Returns:
        DataFrame with churn data
    """
    client = bigquery.Client(project=config.bigquery.project_id)

    query = f"""
    SELECT *
    FROM {config.bigquery.table_name}
    """
    df = client.query(query).to_dataframe()
    return df
