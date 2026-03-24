"""
Silver Layer - Phase 4: Feature Engineering & Derived Features
Creates business-relevant features for ML models and analytics
"""

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("silver-derived").getOrCreate()

def create_risk_indicators(sdf):
    """
    Create risk indicator flags based on transaction characteristics
    """
    print("\n=== CREATING RISK INDICATORS ===")
    
    # High amount risk (top 5% by amount)
    amount_p95 = sdf.approxQuantile("amount", [0.95], 0.01)[0]
    
    sdf = sdf.withColumn(
        "high_amount_risk",
        F.col("amount") > amount_p95
    )
    
    # Unusual time risk (night hours)
    sdf = sdf.withColumn(
        "unusual_time_risk",
        F.col("is_night_hour")
    )
    
    # Combined risk score
    risk_score = (
        F.when(F.col("high_amount_risk"), 1).otherwise(0) +
        F.when(F.col("unusual_time_risk"), 1).otherwise(0) +
        F.when(F.col("is_high_amount"), 1).otherwise(0) +
        F.when(F.col("is_proxy_duplicate"), 1).otherwise(0)
    )
    
    sdf = sdf.withColumn("risk_score", risk_score)
    
    # Risk level classification
    sdf = sdf.withColumn(
        "risk_level",
        F.case()
          .when(F.col("risk_score") >= 3, "CRITICAL")
          .when(F.col("risk_score") == 2, "HIGH")
          .when(F.col("risk_score") == 1, "MEDIUM")
          .otherwise("LOW")
    )
    
    risk_dist = sdf.groupBy("risk_level").count().collect()
    print("✓ Risk indicators created:")
    for row in sorted(risk_dist, key=lambda x: x['count'], reverse=True):
        print(f"  {row['risk_level']:8s}: {row['count']:>10,}")
    
    return sdf

def create_feature_interactions(sdf):
    """
    Create interaction features between top fraud indicator features
    V18, V19, V20 are known fraud indicators
    """
    print("\n=== CREATING FEATURE INTERACTIONS ===")
    
    # Feature interactions
    sdf = sdf.withColumn("v18_v19_interaction", F.col("v18") * F.col("v19"))
    sdf = sdf.withColumn("v18_v20_interaction", F.col("v18") * F.col("v20"))
    sdf = sdf.withColumn("v18_amount_interaction", F.col("v18") * F.col("amount_normalized"))
    
    # Feature aggregations
    sdf = sdf.withColumn(
        "feature_variance",
        F.col("v1")  # Placeholder - in practice, calculate variance across all V features
    )
    
    # Isolate suspicious feature combinations
    sdf = sdf.withColumn(
        "high_v18_flag",
        F.abs(F.col("v18")) > 2.0  # 2 std devs from mean
    )
    
    sdf = sdf.withColumn(
        "high_v19_flag",
        F.abs(F.col("v19")) > 2.0
    )
    
    print("✓ Feature interactions created:")
    print(f"  v18_v19_interaction, v18_v20_interaction")
    print(f"  v18_amount_interaction")
    print(f"  high_v18_flag, high_v19_flag")
    
    return sdf

def create_user_behavior_features(sdf):
    """
    Create user/session behavior features
    Note: This dataset doesn't have explicit customer IDs,
    but we can infer about transaction patterns from time series
    """
    print("\n=== CREATING BEHAVIORAL FEATURES ===")
    
    # Transactions per hour window
    window_hour = Window.partitionBy(
        F.floor(F.col("time") / 3600)  # Hour window
    )
    
    sdf = sdf.withColumn(
        "txns_in_hour",
        F.count("time").over(window_hour)
    )
    
    # Fraud rate in hour
    sdf = sdf.withColumn(
        "fraud_in_hour",
        F.sum(F.col("class")).over(window_hour)
    )
    
    # Transaction density
    sdf = sdf.withColumn(
        "transaction_density",
        F.col("txns_in_hour") / 60  # Per minute
    )
    
    # Spike detection
    sdf = sdf.withColumn(
        "is_spike_hour",
        F.col("txns_in_hour") > sdf.agg(F.percentile_approx("txns_in_hour", 0.9)).collect()[0][0]
    )
    
    print("✓ Behavioral features created:")
    print(f"  txns_in_hour, fraud_in_hour")
    print(f"  transaction_density, is_spike_hour")
    
    return sdf

def create_statistical_features(sdf):
    """
    Create statistical aggregate features
    """
    print("\n=== CREATING STATISTICAL FEATURES ===")
    
    # Linear combination of features (weighted sum)
    v_cols = [f"v{i}" for i in range(1, 29)]
    
    # Simple feature norm (L2)
    feature_norm = None
    for col in v_cols[:5]:  # Sample first 5 for efficiency
        if feature_norm is None:
            feature_norm = F.col(col) ** 2
        else:
            feature_norm = feature_norm + F.col(col) ** 2
    
    sdf = sdf.withColumn(
        "feature_l2_norm_sample",
        F.sqrt(feature_norm)
    )
    
    # Max feature value
    sdf = sdf.withColumn(
        "max_feature_value",
        F.greatest(*[F.col(col) for col in v_cols[:10]])  # Sample
    )
    
    # Min feature value
    sdf = sdf.withColumn(
        "min_feature_value",
        F.least(*[F.col(col) for col in v_cols[:10]])  # Sample
    )
    
    print("✓ Statistical features created:")
    print(f"  feature_l2_norm_sample, max_feature_value, min_feature_value")
    
    return sdf

def create_time_series_features(sdf):
    """
    Create order and lag-based features for time series analysis
    """
    print("\n=== CREATING TIME SERIES FEATURES ===")
    
    # Row number for ordering
    window_order = Window.orderBy("time")
    
    sdf = sdf.withColumn(
        "transaction_order",
        F.row_number().over(window_order)
    )
    
    # Time delta from previous transaction (lag)
    sdf = sdf.withColumn(
        "time_since_prev",
        F.col("time") - F.lag("time", 1, 0).over(window_order)
    )
    
    # Classify time gaps
    sdf = sdf.withColumn(
        "time_gap_category",
        F.case()
          .when(F.col("time_since_prev") == 0, "immediate")
          .when(F.col("time_since_prev") <= 60, "short")
          .when(F.col("time_since_prev") <= 300, "medium")
          .otherwise("long")
    )
    
    print("✓ Time series features created:")
    print(f"  transaction_order, time_since_prev, time_gap_category")
    
    return sdf

def feature_engineering_silver(masked_path: str, output_path: str = "src/silver"):
    """Main feature engineering function"""
    
    print("=== SILVER LAYER - FEATURE ENGINEERING ===")
    
    # Load masked data
    print(f"\nLoading from: {masked_path}")
    sdf = spark.read.parquet(masked_path)
    
    print(f"Initial rows: {sdf.count():,}")
    print(f"Initial columns: {len(sdf.columns)}")
    
    # Apply feature engineering
    sdf = create_risk_indicators(sdf)
    sdf = create_feature_interactions(sdf)
    sdf = create_user_behavior_features(sdf)
    sdf = create_statistical_features(sdf)
    sdf = create_time_series_features(sdf)
    
    print(f"\n=== FEATURE ENGINEERING SUMMARY ===")
    print(f"Total rows: {sdf.count():,}")
    print(f"Total columns: {len(sdf.columns)}")
    print(f"New engineered features: 20+")
    
    # Write output
    output_full_path = f"{output_path}/creditcard_silver_final"
    print(f"\nWriting to: {output_full_path}")
    
    # Write to Unity Catalog
    table_name = "data_engineering_workshop.creditcard.creditcard_silver_final"
    sdf.write.mode("overwrite").format("delta").saveAsTable(table_name)
    
    print(f"✓ Feature Engineering complete")
    
    return output_full_path

if __name__ == "__main__":
    masked_path = "src/silver/creditcard_silver_masked"
    feature_engineering_silver(masked_path)
