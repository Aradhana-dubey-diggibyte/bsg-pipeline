"""
Gold Layer - Phase 2: Rolling Metrics & Time-Based Aggregations
Creates hourly, daily aggregations for monitoring and analytics
"""

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("gold-rolling-metrics").getOrCreate()

def create_hourly_aggregations(risk_df):
    """
    Create hourly level aggregations for real-time monitoring
    """
    print("\n=== CREATING HOURLY AGGREGATIONS ===")
    
    # Define hour window
    risk_df = risk_df.withColumn(
        "hour_bucket",
        (F.col("time") / 3600).cast("int") * 3600
    )
    
    hourly = risk_df.groupBy("hour_bucket").agg(
        F.count("*").alias("total_transactions"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(F.sum(F.col("class")) / F.count("*") * 100, 2).alias("fraud_rate_pct"),
        
        F.round(F.avg("amount"), 2).alias("avg_amount"),
        F.round(F.min("amount"), 2).alias("min_amount"),
        F.round(F.max("amount"), 2).alias("max_amount"),
        F.round(F.stddev("amount"), 2).alias("stddev_amount"),
        
        F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)).alias("fraud_amount_sum"),
        F.round(
            F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)) /
            F.sum(F.col("amount")) * 100,
            2
        ).alias("fraud_amount_pct"),
        
        F.countDistinct(F.col("risk_tier")).alias("risk_tiers_present"),
        F.round(F.avg(F.col("fraud_risk_score_pct")), 2).alias("avg_risk_score"),
        
        F.sum(F.when(F.col("is_spike_hour"), 1).otherwise(0)).alias("spike_count"),
        F.sum(F.when(F.col("requires_monitoring"), 1).otherwise(0)).alias("requires_monitoring_count"),
    ).orderBy("hour_bucket")
    
    print(f"✓ Created {hourly.count()} hourly records")
    print(f"  Sample hourly metrics:")
    hourly.limit(3).show(truncate=False)
    
    return hourly

def create_daily_aggregations(risk_df):
    """
    Create daily level aggregations for trend analysis
    """
    print("\n=== CREATING DAILY AGGREGATIONS ===")
    
    # Define day window
    risk_df = risk_df.withColumn(
        "day_bucket",
        (F.col("time") / (24*3600)).cast("int") * (24*3600)
    )
    
    daily = risk_df.groupBy("day_bucket").agg(
        F.count("*").alias("total_transactions"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(F.sum(F.col("class")) / F.count("*") * 100, 2).alias("fraud_rate_pct"),
        F.round(F.sum(F.col("amount")), 2).alias("total_amount"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
        F.round(F.stddev("amount"), 2).alias("stddev_amount"),
        
        F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)).alias("fraud_amount_total"),
        F.countDistinct(F.col("risk_tier")).alias("risk_tiers_present"),
        F.round(F.avg(F.col("fraud_risk_score_pct")), 2).alias("avg_risk_score"),
    ).orderBy("day_bucket")
    
    print(f"✓ Created {daily.count()} daily records")
    
    return daily

def create_risk_tier_distribution(risk_df):
    """
    Create distribution of transactions across risk tiers
    """
    print("\n=== CREATING RISK TIER DISTRIBUTION ===")
    
    tier_dist = risk_df.groupBy("risk_tier").agg(
        F.count("*").alias("count"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(
            F.sum(F.col("class")) / F.count("*") * 100, 2
        ).alias("fraud_rate_pct"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
        F.round(F.sum("amount"), 2).alias("total_amount"),
        F.round(F.avg("fraud_risk_score_pct"), 2).alias("avg_risk_score"),
    ).orderBy(F.col("count").desc())
    
    print("✓ Risk tier distribution:")
    tier_dist.show()
    
    return tier_dist

def create_amount_bucket_analysis(risk_df):
    """
    Analyze fraud by transaction amount ranges
    """
    print("\n=== CREATING AMOUNT BUCKET ANALYSIS ===")
    
    amount_analysis = risk_df.groupBy("amount_bucket").agg(
        F.count("*").alias("transaction_count"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(
            F.sum(F.col("class")) / F.count("*") * 100, 2
        ).alias("fraud_rate_pct"),
        F.round(F.min("amount"), 2).alias("min_amount"),
        F.round(F.max("amount"), 2).alias("max_amount"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
        F.round(F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)), 2).alias("fraud_amount_sum"),
    ).orderBy("transaction_count")
    
    print("✓ Amount bucket fraud analysis:")
    amount_analysis.show()
    
    return amount_analysis

def create_time_of_day_analysis(risk_df):
    """
    Analyze fraud patterns by hour of day and day of week
    """
    print("\n=== CREATING TIME OF DAY ANALYSIS ===")
    
    time_analysis = risk_df.groupBy("hour_of_day", "is_weekend").agg(
        F.count("*").alias("transaction_count"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(
            F.sum(F.col("class")) / F.count("*") * 100, 2
        ).alias("fraud_rate_pct"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
    ).orderBy("hour_of_day", "is_weekend")
    
    print("✓ Time of day fraud patterns:")
    time_analysis.show(24, truncate=False)
    
    return time_analysis

def create_feature_anomaly_stats(risk_df):
    """
    Aggregate statistics on feature anomalies for monitoring
    """
    print("\n=== CREATING FEATURE ANOMALY STATISTICS ===")
    
    anomaly_stats = risk_df.agg(
        F.count("*").alias("total_rows"),
        F.sum(F.when(F.abs(F.col("v18")) > 3.0, 1).otherwise(0)).alias("v18_extreme_count"),
        F.sum(F.when(F.abs(F.col("v19")) > 3.0, 1).otherwise(0)).alias("v19_extreme_count"),
        F.sum(F.when(F.abs(F.col("v20")) > 3.0, 1).otherwise(0)).alias("v20_extreme_count"),
        F.round(F.avg(F.abs(F.col("v18"))), 4).alias("v18_mean_abs"),
        F.round(F.avg(F.abs(F.col("v19"))), 4).alias("v19_mean_abs"),
        F.round(F.avg(F.abs(F.col("v20"))), 4).alias("v20_mean_abs"),
    )
    
    print("✓ Feature anomaly statistics created")
    
    return anomaly_stats

def rolling_metrics_gold(risk_path: str, output_path: str = "src/gold"):
    """Main rolling metrics function"""
    
    print("=== GOLD LAYER - ROLLING METRICS & AGGREGATIONS ===")
    
    # Load risk scored data
    print(f"\nLoading from: {risk_path}")
    risk_df = spark.read.parquet(risk_path)
    
    print(f"Total rows: {risk_df.count():,}")
    
    # Create various aggregations
    hourly = create_hourly_aggregations(risk_df)
    daily = create_daily_aggregations(risk_df)
    tier_dist = create_risk_tier_distribution(risk_df)
    amount_analysis = create_amount_bucket_analysis(risk_df)
    time_analysis = create_time_of_day_analysis(risk_df)
    anomaly_stats = create_feature_anomaly_stats(risk_df)
    
    print(f"\n=== ROLLING METRICS SUMMARY ===")
    print(f"Hourly aggregations: {hourly.count()} records")
    print(f"Daily aggregations: {daily.count()} records")
    print(f"Risk tier distribution: Analyzed")
    print(f"Amount bucket analysis: Analyzed")
    print(f"Time of day patterns: Analyzed")
    print(f"Feature anomalies: Analyzed")
    
    # Write to Unity Catalog
    hourly_table = "data_engineering_workshop.creditcard.creditcard_gold_hourly_metrics"
    daily_table = "data_engineering_workshop.creditcard.creditcard_gold_daily_metrics"
    
    print(f"\nWriting hourly to: {hourly_table}")
    hourly.write.mode("overwrite").format("delta").saveAsTable(hourly_table)
    
    print(f"Writing daily to: {daily_table}")
    daily.write.mode("overwrite").format("delta").saveAsTable(daily_table)
    
    print(f"✓ Rolling Metrics complete")
    print(f"✓ Format: Delta (Unity Catalog)")
    
    return hourly_table, daily_table

if __name__ == "__main__":
    risk_path = "src/gold/creditcard_gold_risk_scores"
    rolling_metrics_gold(risk_path)
