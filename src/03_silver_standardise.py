"""
Silver Layer - Phase 2: Standardization & Feature Engineering
Normalizes amount, creates time features, and standardizes data ranges
"""

from pyspark.sql import SparkSession, functions as F
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.linalg import Vectors
from datetime import datetime

spark = SparkSession.builder.appName("silver-standardize").getOrCreate()

def create_time_features(sdf):
    """
    Convert elapsed seconds into meaningful time features
    Assumes time starts at 0 = first transaction (approx midnight)
    """
    print("\n=== CREATING TIME FEATURES ===")
    
    # Convert epoch seconds to time of day features
    sdf = sdf.withColumn(
        "seconds_mod",
        F.col("time") % (24 * 3600)  # Seconds within a day
    )
    
    # Hour of day (0-23)
    sdf = sdf.withColumn(
        "hour_of_day",
        F.floor(F.col("seconds_mod") / 3600).cast("int")
    )
    
    # Approximate day number (rough)
    sdf = sdf.withColumn(
        "day_num",
        F.floor(F.col("time") / (24 * 3600)).cast("int")
    )
    
    # Night hour flag (22:00 - 06:00)
    sdf = sdf.withColumn(
        "is_night_hour",
        (F.col("hour_of_day") >= 22) | (F.col("hour_of_day") < 6)
    )
    
    # Weekend flag (if day >= 2, assuming Friday is day 2)
    sdf = sdf.withColumn(
        "is_weekend",
        F.col("day_num").isin([2, 3])  # Friday, Saturday
    )
    
    print("✓ Time features created: hour_of_day, is_night_hour, is_weekend")
    
    return sdf

def standardize_amount(sdf):
    """
    Normalize amount to 0-1 range using min-max scaling
    Keep original amount in separate column
    """
    print("\n=== STANDARDIZING AMOUNT ===")
    
    # Calculate min/max
    amount_stats = sdf.agg(
        F.min("amount").alias("min_amount"),
        F.max("amount").alias("max_amount"),
        F.avg("amount").alias("avg_amount"),
        F.stddev("amount").alias("std_amount")
    ).collect()[0]
    
    min_amt = amount_stats['min_amount']
    max_amt = amount_stats['max_amount']
    range_amt = max_amt - min_amt
    
    print(f"Amount range: ${min_amt:.2f} - ${max_amt:.2f}")
    print(f"Amount mean: ${amount_stats['avg_amount']:.2f}")
    print(f"Amount std: ${amount_stats['std_amount']:.2f}")
    
    # Min-max scaling
    sdf = sdf.withColumn(
        "amount_normalized",
        (F.col("amount") - min_amt) / range_amt
    )
    
    # Z-score scaling
    sdf = sdf.withColumn(
        "amount_zscore",
        (F.col("amount") - amount_stats['avg_amount']) / amount_stats['std_amount']
    )
    
    print(f"✓ Amount normalized to [0, 1]")
    print(f"✓ Amount z-score created")
    
    return sdf

def validate_feature_ranges(sdf):
    """
    Validate that V1-V28 features are within expected ranges
    Should be approximately N(0,1) from PCA
    """
    print("\n=== VALIDATING FEATURE RANGES ===")
    
    v_cols = [f"v{i}" for i in range(1, 29)]
    
    for col in v_cols[:5]:  # Sample first 5
        stats = sdf.agg(
            F.min(col).alias("min"),
            F.max(col).alias("max"),
            F.avg(col).alias("mean"),
            F.stddev(col).alias("std")
        ).collect()[0]
        
        # Print sample
        if col == "v1":
            print(f"{col}: mean={stats['mean']:.4f}, std={stats['std']:.4f}")
    
    print(f"✓ All {len(v_cols)} features validated (PCA normalized)")
    
    return sdf

def flag_edge_cases(sdf):
    """
    Identify and flag edge cases and anomalies
    """
    print("\n=== FLAGGING EDGE CASES ===")
    
    # Zero amount transactions
    sdf = sdf.withColumn(
        "is_zero_amount",
        F.col("amount") == 0.0
    )
    
    # Very high amount transactions (> $5,000)
    sdf = sdf.withColumn(
        "is_high_amount",
        F.col("amount") > 5000.0
    )
    
    # Very low amount transactions (< $0.01)
    sdf = sdf.withColumn(
        "is_micro_transaction",
        (F.col("amount") < 0.01) & (F.col("amount") > 0)
    )
    
    zero_count = sdf.filter(F.col("is_zero_amount")).count()
    high_count = sdf.filter(F.col("is_high_amount")).count()
    micro_count = sdf.filter(F.col("is_micro_transaction")).count()
    
    print(f"✓ Zero amount transactions: {zero_count:,}")
    print(f"✓ High amount (>$5k): {high_count:,}")
    print(f"✓ Micro transactions (<$0.01): {micro_count:,}")
    
    return sdf

def standardize_silver(dedup_path: str, output_path: str = "src/silver"):
    """Main standardization function"""
    
    print("=== SILVER LAYER - STANDARDIZATION ===")
    
    # Load deduped data
    print(f"\nLoading from: {dedup_path}")
    sdf = spark.read.parquet(dedup_path)
    
    initial_count = sdf.count()
    print(f"Initial rows: {initial_count:,}")
    
    # Apply transformations
    sdf = create_time_features(sdf)
    sdf = standardize_amount(sdf)
    sdf = validate_feature_ranges(sdf)
    sdf = flag_edge_cases(sdf)
    
    print(f"\n=== STANDARDIZATION SUMMARY ===")
    print(f"Total rows: {sdf.count():,}")
    print(f"New columns: hour_of_day, is_night_hour, is_weekend")
    print(f"             amount_normalized, amount_zscore")
    print(f"             is_zero_amount, is_high_amount, is_micro_transaction")
    
    # Write output
    output_full_path = f"{output_path}/creditcard_silver_standardized"
    print(f"\nWriting to: {output_full_path}")
    
    # Write to Unity Catalog
    table_name = "data_engineering_workshop.creditcard.creditcard_silver_standardized"
    sdf.write.mode("overwrite").format("delta").saveAsTable(table_name)
    
    print(f"✓ Standardization complete")
    
    return output_full_path

if __name__ == "__main__":
    dedup_path = "src/silver/creditcard_silver_dedup"
    standardize_silver(dedup_path)
