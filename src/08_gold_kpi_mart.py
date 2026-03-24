"""
Gold Layer - Phase 3: KPI Mart
Creates aggregated KPIs for business dashboards and reporting
"""

from pyspark.sql import SparkSession, functions as F
from datetime import datetime

spark = SparkSession.builder.appName("gold-kpi-mart").getOrCreate()

def create_overall_kpis(risk_df):
    """
    Calculate organization-wide KPIs
    """
    print("\n=== CREATING OVERALL KPIs ===")
    
    metrics = risk_df.agg(
        # Volume metrics
        F.count("*").alias("total_transactions"),
        F.sum(F.col("class")).alias("fraud_cases"),
        
        # Rate metrics
        F.round(
            F.sum(F.col("class")) / F.count("*") * 100, 3
        ).alias("fraud_rate_pct"),
        
        # Amount metrics
        F.round(F.sum("amount"), 2).alias("total_transaction_amount"),
        F.round(F.avg("amount"), 2).alias("avg_transaction_amount"),
        F.round(F.max("amount"), 2).alias("max_transaction_amount"),
        
        # Fraud amount metrics
        F.round(
            F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)), 2
        ).alias("fraud_total_amount"),
        
        F.round(
            F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)) /
            F.sum(F.col("amount")) * 100,
            2
        ).alias("fraud_amount_pct"),
        
        # Risk metrics
        F.round(F.avg(F.col("fraud_risk_score_pct")), 2).alias("avg_risk_score"),
        
        # Quality metrics
        F.sum(F.when(F.col("is_proxy_duplicate"), 1).otherwise(0)).alias("duplicate_transactions"),
        F.sum(F.when(F.col("requires_monitoring"), 1).otherwise(0)).alias("requires_monitoring_count"),
    )
    
    row = metrics.collect()[0]
    
    print("✓ Overall KPIs calculated:")
    print(f"  Total Transactions: {row['total_transactions']:,}")
    print(f"  Fraud Cases: {row['fraud_cases']}")
    print(f"  Fraud Rate: {row['fraud_rate_pct']:.3f}%")
    print(f"  Total Amount: ${row['total_transaction_amount']:,.2f}")
    print(f"  Fraud Amount: ${row['fraud_total_amount']:,.2f}")
    print(f"  Fraud Loss %: {row['fraud_amount_pct']:.2f}%")
    
    # Convert to KPI mart format
    kpi_rows = []
    for key, value in row.asDict().items():
        kpi_rows.append((key, value, datetime.now()))
    
    return spark.createDataFrame(kpi_rows, ["metric_name", "metric_value", "snapshot_timestamp"])

def create_risk_distribution_kpis(risk_df):
    """
    KPIs for risk distribution across tiers
    """
    print("\n=== CREATING RISK DISTRIBUTION KPIs ===")
    
    risk_dist = risk_df.groupBy("risk_tier").agg(
        F.count("*").alias("transaction_count"),
        F.round(F.count("*") / F.count("").over() * 100, 2).alias("pct_of_total"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(
            F.sum(F.col("class")) / F.count("*") * 100, 2
        ).alias("fraud_rate_pct"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
    )
    
    print("✓ Risk tier KPIs:")
    risk_dist.show()
    
    return risk_dist

def create_action_recommendation_kpis(risk_df):
    """
    KPIs based on recommended actions
    """
    print("\n=== CREATING ACTION RECOMMENDATION KPIs ===")
    
    action_dist = risk_df.groupBy("recommended_action").agg(
        F.count("*").alias("transaction_count"),
        F.round(F.count("*") / F.count("").over() * 100, 2).alias("pct_of_total"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(
            F.sum(F.col("class")) / F.count("*") * 100, 3
        ).alias("fraud_rate_pct"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
    ).orderBy(F.col("fraud_count").desc())
    
    print("✓ Action recommendation KPIs:")
    action_dist.show()
    
    return action_dist

def create_time_based_kpis(risk_df):
    """
    KPIs broken down by time periods
    """
    print("\n=== CREATING TIME-BASED KPIs ===")
    
    # Define time periods
    risk_df = risk_df.withColumn(
        "time_period",
        F.case()
          .when(F.col("hour_of_day") < 6, "Night (0-6)")
          .when(F.col("hour_of_day") < 12, "Morning (6-12)")
          .when(F.col("hour_of_day") < 18, "Afternoon (12-18)")
          .otherwise("Evening (18-24)")
    )
    
    time_kpis = risk_df.groupBy("time_period").agg(
        F.count("*").alias("transaction_count"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(
            F.sum(F.col("class")) / F.count("*") * 100, 2
        ).alias("fraud_rate_pct"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
        F.round(F.sum("amount"), 2).alias("total_amount"),
    )
    
    print("✓ Time-based KPIs:")
    time_kpis.show()
    
    return time_kpis

def create_performance_benchmarks(risk_df):
    """
    Create performance benchmarks and thresholds
    """
    print("\n=== CREATING PERFORMANCE BENCHMARKS ===")
    
    # Calculate percentiles for comparisons
    benchmarks = risk_df.agg(
        # Amount benchmarks
        F.round(F.percentile_approx(F.col("amount"), 0.25), 2).alias("amount_q1"),
        F.round(F.percentile_approx(F.col("amount"), 0.50), 2).alias("amount_median"),
        F.round(F.percentile_approx(F.col("amount"), 0.75), 2).alias("amount_q3"),
        F.round(F.percentile_approx(F.col("amount"), 0.95), 2).alias("amount_p95"),
        F.round(F.percentile_approx(F.col("amount"), 0.99), 2).alias("amount_p99"),
        
        # Risk score benchmarks
        F.round(F.percentile_approx(F.col("fraud_risk_score_pct"), 0.50), 0).alias("risk_score_median"),
        F.round(F.percentile_approx(F.col("fraud_risk_score_pct"), 0.75), 0).alias("risk_score_q3"),
        F.round(F.percentile_approx(F.col("fraud_risk_score_pct"), 0.95), 0).alias("risk_score_p95"),
    )
    
    row = benchmarks.collect()[0]
    print("✓ Performance benchmarks:")
    print(f"  Amount Q1-Median-Q3: ${row['amount_q1']:.2f} - ${row['amount_median']:.2f} - ${row['amount_q3']:.2f}")
    print(f"  Amount P95/P99: ${row['amount_p95']:.2f} / ${row['amount_p99']:.2f}")
    print(f"  Risk Score Median/Q3/P95: {row['risk_score_median']:.0f} / {row['risk_score_q3']:.0f} / {row['risk_score_p95']:.0f}")
    
    return benchmarks

def create_kpi_mart_table(risk_df):
    """
    Create unified KPI mart table with all key metrics
    """
    print("\n=== CREATING UNIFIED KPI MART TABLE ===")
    
    # Calculate all metrics
    overall = risk_df.agg(
        F.lit("Overall").alias("dimension"),
        F.lit("All").alias("category"),
        F.count("*").alias("transactions"),
        F.sum(F.col("class")).alias("frauds"),
        F.round(
            F.sum(F.col("class")) / F.count("*") * 100, 3
        ).alias("fraud_rate_pct"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
        F.round(F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)), 2).alias("fraud_loss"),
        F.lit(datetime.now()).cast("timestamp").alias("snapshot_timestamp")
    )
    
    # By risk tier
    by_tier = risk_df.groupBy(
        F.lit("Risk Tier").alias("dimension"),
        F.col("risk_tier").alias("category")
    ).agg(
        F.count("*").alias("transactions"),
        F.sum(F.col("class")).alias("frauds"),
        F.round(F.sum(F.col("class")) / F.count("*") * 100, 3).alias("fraud_rate_pct"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
        F.round(F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)), 2).alias("fraud_loss"),
        F.lit(datetime.now()).cast("timestamp").alias("snapshot_timestamp")
    )
    
    # By amount bucket
    by_amount = risk_df.groupBy(
        F.lit("Amount Bucket").alias("dimension"),
        F.col("amount_bucket").alias("category")
    ).agg(
        F.count("*").alias("transactions"),
        F.sum(F.col("class")).alias("frauds"),
        F.round(F.sum(F.col("class")) / F.count("*") * 100, 3).alias("fraud_rate_pct"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
        F.round(F.sum(F.when(F.col("class") == 1, F.col("amount")).otherwise(0)), 2).alias("fraud_loss"),
        F.lit(datetime.now()).cast("timestamp").alias("snapshot_timestamp")
    )
    
    # Union all into KPI mart
    kpi_mart = overall.unionByName(by_tier).unionByName(by_amount)
    
    print(f"✓ Unified KPI mart created with {kpi_mart.count()} records")
    
    return kpi_mart

def kpi_mart_gold(risk_path: str, output_path: str = "src/gold"):
    """Main KPI mart function"""
    
    print("=== GOLD LAYER - KPI MART ===")
    
    # Load risk scored data
    print(f"\nLoading from: {risk_path}")
    risk_df = spark.read.parquet(risk_path)
    
    print(f"Total rows: {risk_df.count():,}")
    
    # Create all KPI tables
    overall_kpis = create_overall_kpis(risk_df)
    risk_dist = create_risk_distribution_kpis(risk_df)
    action_kpis = create_action_recommendation_kpis(risk_df)
    time_kpis = create_time_based_kpis(risk_df)
    benchmarks = create_performance_benchmarks(risk_df)
    kpi_mart = create_kpi_mart_table(risk_df)
    
    print(f"\n=== KPI MART SUMMARY ===")
    print(f"Overall KPIs: Created")
    print(f"Risk distribution: Created")
    print(f"Action recommendations: Created")
    print(f"Time-based KPIs: Created")
    print(f"Performance benchmarks: Created")
    print(f"Unified KPI Mart: {kpi_mart.count()} records")
    
    # Write output
    kpi_mart_path = f"{output_path}/creditcard_gold_kpi_mart"
    
    print(f"\nWriting unified KPI Mart: {kpi_mart_path}")
    # Write to Unity Catalog
    kpi_mart.write.mode("overwrite").format("delta").saveAsTable("data_engineering_workshop.creditcard.creditcard_gold_kpi_mart")
    
    print(f"✓ KPI Mart complete")
    
    return kpi_mart_path

if __name__ == "__main__":
    risk_path = "src/gold/creditcard_gold_risk_scores"
    kpi_mart_gold(risk_path)
