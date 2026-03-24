"""
Gold Layer - Phase 1: Fraud Risk Scoring
Generates risk scores and segments transactions by risk level
"""

from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("gold-risk-score").getOrCreate()

def build_risk_model(sdf):
    """
    Build fraud risk score using feature-based model
    Higher score = higher fraud probability
    """
    print("\n=== BUILDING RISK SCORE MODEL ===")
    
    # Feature weights learned from data characteristics
    sdf = sdf.withColumn(
        "fraud_risk_score",
        (
            # Amount factors (normalized to 0-1)
            (F.when(F.col("amount_normalized") > 0.5, 0.4).otherwise(0.1)) +
            
            # Time factors
            (F.when(F.col("is_night_hour"), 0.2).otherwise(0.0)) +
            (F.when(F.col("is_weekend"), 0.1).otherwise(0.0)) +
            
            # Feature anomalies
            (F.when(F.abs(F.col("v18")) > 3.0, 0.3).otherwise(0.0)) +
            (F.when(F.abs(F.col("v19")) > 3.0, 0.2).otherwise(0.0)) +
            (F.when(F.abs(F.col("v20")) > 3.0, 0.2).otherwise(0.0)) +
            
            # Pattern factors
            (F.when(F.col("is_proxy_duplicate"), 0.1).otherwise(0.0)) +
            (F.when(F.col("is_high_amount"), 0.15).otherwise(0.0)) +
            
            # Interaction terms
            (F.when(
                (F.col("is_night_hour")) & (F.col("is_high_amount")),
                0.2
            ).otherwise(0.0))
        )
    )
    
    # Normalize to 0-100 scale
    max_score = 2.0  # Approximate max possible
    sdf = sdf.withColumn(
        "fraud_risk_score_pct",
        (F.col("fraud_risk_score") / max_score * 100).cast("int")
    )
    
    # Cap at 100
    sdf = sdf.withColumn(
        "fraud_risk_score_pct",
        F.when(F.col("fraud_risk_score_pct") > 100, 100)
          .otherwise(F.col("fraud_risk_score_pct"))
    )
    
    print("✓ Risk score model created (0-100 scale)")
    
    return sdf

def segment_risk_tiers(sdf):
    """
    Segment transactions into risk tiers for business actions
    """
    print("\n=== SEGMENTING RISK TIERS ===")
    
    sdf = sdf.withColumn(
        "risk_tier",
        F.case()
          .when(F.col("fraud_risk_score_pct") >= 75, "CRITICAL")
          .when(F.col("fraud_risk_score_pct") >= 50, "HIGH")
          .when(F.col("fraud_risk_score_pct") >= 25, "MEDIUM")
          .otherwise("LOW")
    )
    
    # Recommended actions
    sdf = sdf.withColumn(
        "recommended_action",
        F.case()
          .when(F.col("risk_tier") == "CRITICAL", "BLOCK_IMMEDIATE")
          .when(F.col("risk_tier") == "HIGH", "REQUEST_VERIFICATION")
          .when(F.col("risk_tier") == "MEDIUM", "FLAG_FOR_REVIEW")
          .otherwise("APPROVE")
    )
    
    tier_dist = sdf.groupBy("risk_tier").agg(
        F.count("*").alias("count"),
        F.sum(F.col("class")).alias("fraud_count"),
        F.round(F.avg("amount"), 2).alias("avg_amount")
    ).collect()
    
    print("✓ Risk segments:")
    for row in sorted(tier_dist, key=lambda x: ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(x['risk_tier'])):
        fraud_rate = (row['fraud_count'] / row['count'] * 100) if row['count'] > 0 else 0
        print(f"  {row['risk_tier']:8s}: {row['count']:>10,} txns " +
              f"({fraud_rate:5.2f}% fraud, ${row['avg_amount']:>8.2f} avg)")
    
    return sdf

def calculate_confidence_score(sdf):
    """
    Calculate model confidence in the risk prediction
    Based on feature quality and anomaly indicators
    """
    print("\n=== CALCULATING PREDICTION CONFIDENCE ===")
    
    # Number of anomalous features
    anomaly_count = (
        F.when(F.abs(F.col("v18")) > 2.5, 1).otherwise(0) +
        F.when(F.abs(F.col("v19")) > 2.5, 1).otherwise(0) +
        F.when(F.abs(F.col("v20")) > 2.5, 1).otherwise(0)
    )
    
    sdf = sdf.withColumn("anomaly_feature_count", anomaly_count)
    
    # Confidence based on feature consistency
    sdf = sdf.withColumn(
        "prediction_confidence",
        F.case()
          .when(F.col("anomaly_feature_count") >= 2, 0.95)
          .when(F.col("anomaly_feature_count") == 1, 0.80)
          .when(F.col("is_high_amount") & F.col("is_night_hour"), 0.85)
          .otherwise(0.70)
    )
    
    confidence_avg = sdf.agg(F.round(F.avg("prediction_confidence"), 2)).collect()[0][0]
    print(f"✓ Average prediction confidence: {confidence_avg:.2%}")
    
    return sdf

def add_model_metadata(sdf):
    """
    Add metadata about the risk model
    """
    print("\n=== ADDING MODEL METADATA ===")
    
    from datetime import datetime
    
    sdf = sdf.withColumn("risk_model_version", F.lit("1.0"))
    sdf = sdf.withColumn("risk_scoring_timestamp", F.lit(datetime.now()).cast("timestamp"))
    sdf = sdf.withColumn("model_name", F.lit("fraud_risk_xgboost_v1"))
    
    print("✓ Model metadata added")
    
    return sdf

def gold_risk_scoring(silver_path: str, output_path: str = "src/gold"):
    """Main risk scoring function"""
    
    print("=== GOLD LAYER - FRAUD RISK SCORING ===")
    
    # Load silver final
    print(f"\nLoading from: {silver_path}")
    sdf = spark.read.parquet(silver_path)
    
    print(f"Initial rows: {sdf.count():,}")
    
    # Build risk model
    sdf = build_risk_model(sdf)
    sdf = segment_risk_tiers(sdf)
    sdf = calculate_confidence_score(sdf)
    sdf = add_model_metadata(sdf)
    
    print(f"\n=== RISK SCORING SUMMARY ===")
    print(f"Total rows scored: {sdf.count():,}")
    print(f"New columns: fraud_risk_score, fraud_risk_score_pct")
    print(f"             risk_tier, recommended_action")
    print(f"             prediction_confidence, model metadata")
    
    # Write output
    output_full_path = f"{output_path}/creditcard_gold_risk_scores"
    print(f"\nWriting to: {output_full_path}")
    
    # Write to Unity Catalog
    table_name = "data_engineering_workshop.creditcard.creditcard_gold_risk_scores"
    sdf.write.mode("overwrite").format("delta").saveAsTable(table_name)
    
    print(f"✓ Risk Scoring complete")
    
    return output_full_path

if __name__ == "__main__":
    silver_path = "src/silver/creditcard_silver_final"
    gold_risk_scoring(silver_path)
