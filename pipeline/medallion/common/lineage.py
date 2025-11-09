from pyspark.sql import DataFrame
from pyspark.sql.functions import lit


def with_lineage(df: DataFrame, source_file: str, run_id: str) -> DataFrame:
    return df.withColumn("raw_source_file", lit(source_file)).withColumn("load_run_id", lit(run_id))
