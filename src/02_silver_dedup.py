"""
Silver Layer - Phase 1: Deduplication
Detects and removes duplicate transactions
"""

import pandas as pd
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("silver-dedup").getOrCreate()

def detect_exact_duplicates(sdf):
    """
    Detect exact duplicate rows (all columns identical)
    Returns: DataFrame with duplicate_flag column
    """
    print("\n=== DETECTING EXACT DUPLICATES ===")
    
    # Window function to identify duplicates
    window = Window.partitionBy(
        "time", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10",
        "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19", "v20",
        "v21", "v22", "v23", "v24", "v25", "v26", "v27", "v28", "amount", "class"
    ).orderBy("load_timestamp")
    
    sdf = sdf.withColumn("rn", F.row_number().over(window))
    
    # Keep only first occurrence (rn = 1)
    exact_dups = sdf.filter(F.col("rn") > 1).count()
    sdf = sdf.filter(F.col("rn") == 1).drop("rn")
    
    print(f"Exact duplicates found: {exact_dups:,}")
    print(f"Rows remaining: {sdf.count():,}")
    
    return sdf

def detect_proxy_duplicates(sdf, time_window_sec=300):
    """
    Detect proxy duplicates: same amount + class within time window
    Indicates likely fraudulent repeat attempts
    """
    print(f"\n=== DETECTING PROXY DUPLICATES (within {time_window_sec}s) ===")
    
    window = Window.orderBy("time").partitionBy("amount", "class") \
        .rangeBetween(-time_window_sec, 0)
    
    sdf = sdf.withColumn(
        "dup_count",
        F.count("time").over(window)
    )
    
    proxy_dups = sdf.filter(F.col("dup_count") > 1).count()
    
    # Flag duplicates but don't remove (might be valuable for fraud detection)
    sdf = sdf.withColumn(
        "is_proxy_duplicate",
        F.when(F.col("dup_count") > 1, True).otherwise(False)
    )
    
    print(f"✓ Proxy duplicates found: {proxy_dups:,}")
    print(f"✓ Total rows: {sdf.count():,}")
    
    return sdf.drop("dup_count")

def deduplicate_silver(bronze_path: str, output_path: str = "src/silver"):
    """Main deduplication function"""
    
    print("=== SILVER LAYER - DEDUPLICATION ===")
    
    # Load bronze layer
    print(f"\nLoading from: {bronze_path}")
    sdf = spark.read.parquet(bronze_path)
    
    initial_count = sdf.count()
    print(f"Initial rows: {initial_count:,}")
    
    # Detect and remove exact duplicates
    sdf = detect_exact_duplicates(sdf)
    
    # Detect proxy duplicates
    sdf = detect_proxy_duplicates(sdf)
    
    # Final statistics
    final_count = sdf.count()
    removed = initial_count - final_count
    
    print(f"\n=== DEDUPLICATION SUMMARY ===")
    print(f"Initial rows: {initial_count:,}")
    print(f"Final rows: {final_count:,}")
    print(f"Removed: {removed:,} ({removed/initial_count*100:.2f}%)")
    print(f"Proxy flag applied: {sdf.filter(F.col('is_proxy_duplicate')).count():,}")
    
    # Write output to Unity Catalog
    table_name = "data_engineering_workshop.creditcard.creditcard_silver_dedup"
    print(f"\nWriting to Unity Catalog: {table_name}")
    
    sdf.write.mode("overwrite").format("delta").saveAsTable(table_name)
    
    print(f"✓ Deduplication complete")
    print(f"✓ Format: Delta (Unity Catalog)")
    print(f"✓ Table: {table_name}")
    
    return table_name

if __name__ == "__main__":
    bronze_path = "src/bronze/creditcard_bronze"
    deduplicate_silver(bronze_path)
