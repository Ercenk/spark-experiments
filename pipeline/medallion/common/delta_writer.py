from pyspark.sql import DataFrame


def write_delta(df: DataFrame, path: str, mode: str = "append"):
    df.write.format("delta").mode(mode).save(path)
