"""
Silver Layer - Phase 3: PII Masking & Data Governance
Applies data classification and masks sensitive information
"""

from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("silver-pii-mask").getOrCreate()

def mask_sensitive_amounts(sdf):
    """
    Replace actual amounts with 'amount_bucket' for sensitive scenarios
    Useful for non-finance team access
    """
    print("\n=== MASKING SENSITIVE AMOUNTS ===")
    
    # Create amount bucket classification
    sdf = sdf.withColumn(
        "amount_bucket",
        F.when(F.col("amount") == 0, "zero")
          .when((F.col("amount") > 0) & (F.col("amount") <= 50), "micro")
          .when((F.col("amount") > 50) & (F.col("amount") <= 200), "small")
          .when((F.col("amount") > 200) & (F.col("amount") <= 1000), "medium")
          .when(F.col("amount") > 1000, "large")
          .otherwise("unknown")
    )
    
    # Create masked_amount for sensitive data sharing
    # Keep exact values for finance, buckets for others
    sdf = sdf.withColumn(
        "amount_masked",
        F.when(F.col("is_high_amount"), F.lit("REDACTED_HIGH_VALUE"))
          .otherwise(F.round(F.col("amount"), 2))
    )
    
    bucket_dist = sdf.groupBy("amount_bucket").count().collect()
    print("✓ Amount buckets created:")
    for row in bucket_dist:
        print(f"  {row['amount_bucket']:8s}: {row['count']:>10,}")
    
    return sdf

def add_data_classification(sdf):
    """
    Add data classification tags for access control
    PII = Personally Identifiable Information
    """
    print("\n=== ADDING DATA CLASSIFICATION ===")
    
    # Amount is sensitive financial data
    sdf = sdf.withColumn(
        "amount_classification",
        F.lit("SENSITIVE")
    )
    
    # Features are already anonymized (PCA)
    sdf = sdf.withColumn(
        "features_classification",
        F.lit("PUBLIC")
    )
    
    # Class (fraud) is sensitive
    sdf = sdf.withColumn(
        "class_classification",
        F.lit("SENSITIVE")
    )
    
    print("✓ Classification tags applied:")
    print("  amount, class: SENSITIVE")
    print("  v1-v28: PUBLIC (already anonymized)")
    
    return sdf

def add_audit_columns(sdf):
    """
    Add audit trail columns for data governance
    """
    print("\n=== ADDING AUDIT COLUMNS ===")
    
    current_ts = datetime.now()
    
    sdf = sdf.withColumn(
        "pii_masked_timestamp",
        F.lit(current_ts).cast("timestamp")
    )
    
    sdf = sdf.withColumn(
        "data_version",
        F.lit("1.0")
    )
    
    sdf = sdf.withColumn(
        "processing_stage",
        F.lit("silver_masked")
    )
    
    print("✓ Audit columns added: pii_masked_timestamp, data_version, processing_stage")
    
    return sdf

def identify_high_value_transactions(sdf):
    """
    Flag high-value transactions for enhanced monitoring
    """
    print("\n=== IDENTIFYING HIGH-VALUE TRANSACTIONS ===")
    
    sdf = sdf.withColumn(
        "requires_monitoring",
        F.col("is_high_amount") | F.col("is_night_hour")
    )
    
    monitor_count = sdf.filter(F.col("requires_monitoring")).count()
    fraud_monitor = sdf.filter(
        (F.col("requires_monitoring")) & (F.col("class") == 1)
    ).count()
    
    print(f"✓ Transactions requiring monitoring: {monitor_count:,}")
    print(f"✓ Of which are fraud: {fraud_monitor:,}")
    
    return sdf

def apply_redaction_rules(sdf):
    """
    Apply business rules for redacting sensitive data
    """
    print("\n=== APPLYING REDACTION RULES ===")
    
    # Create person viewing scenario columns
    # For compliance team (can see all data)
    sdf = sdf.withColumn(
        "for_compliance",
        F.struct(
            F.col("time"),
            F.col("amount"),
            F.col("class"),
            F.lit("FULL_ACCESS")
        )
    )
    
    # For analytics team (masked amounts)
    sdf = sdf.withColumn(
        "for_analytics",
        F.struct(
            F.col("time"),
            F.col("amount_bucket"),
            F.col("class"),
            F.lit("RESTRICTED_ACCESS")
        )
    )
    
    # For business team (no class/fraud info)
    sdf = sdf.withColumn(
        "for_business",
        F.struct(
            F.col("time"),
            F.col("amount_bucket"),
            F.lit("PUBLIC_ACCESS")
        )
    )
    
    print("✓ Role-based data views created:")
    print("  for_compliance: Full access to all fields")
    print("  for_analytics: Bucketed amounts, sees fraud flag")
    print("  for_business: Public data only")
    
    return sdf

def pii_mask_silver(standardized_path: str, output_path: str = "src/silver"):
    """Main PII masking function"""
    
    print("=== SILVER LAYER - PII MASKING ===")
    
    # Load standardized data
    print(f"\nLoading from: {standardized_path}")
    sdf = spark.read.parquet(standardized_path)
    
    print(f"Initial rows: {sdf.count():,}")
    
    # Apply masking and governance
    sdf = mask_sensitive_amounts(sdf)
    sdf = add_data_classification(sdf)
    sdf = add_audit_columns(sdf)
    sdf = identify_high_value_transactions(sdf)
    
    print(f"\n=== PII MASKING SUMMARY ===")
    print(f"Total rows: {sdf.count():,}")
    print(f"New columns: amount_bucket, amount_masked, amount_classification")
    print(f"             features_classification, class_classification")
    print(f"             pii_masked_timestamp, data_version, processing_stage")
    print(f"             requires_monitoring")
    
    # Write output
    output_full_path = f"{output_path}/creditcard_silver_masked"
    print(f"\nWriting to: {output_full_path}")
    
    # Write to Unity Catalog
    table_name = "data_engineering_workshop.creditcard.creditcard_silver_masked"
    sdf.write.mode("overwrite").format("delta").saveAsTable(table_name)
    
    print(f"✓ PII Masking complete")
    
    return output_full_path

if __name__ == "__main__":
    from datetime import datetime
    
    standardized_path = "src/silver/creditcard_silver_standardized"
    pii_mask_silver(standardized_path)
