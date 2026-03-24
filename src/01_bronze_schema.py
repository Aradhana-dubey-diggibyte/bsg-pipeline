"""
Bronze Layer: Raw Data Ingestion & Schema Validation
Loads CSV data, enforces schema, and stores in Parquet format
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType, StructField, IntegerType, FloatType, 
    DoubleType, TimestampType, StringType
)

# Initialize Spark
spark = SparkSession.builder \
    .appName("bronze-creditcard") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# Define Bronze Schema
BRONZE_SCHEMA = StructType([
    StructField("time", IntegerType(), False),
    StructField("v1", DoubleType(), False),
    StructField("v2", DoubleType(), False),
    StructField("v3", DoubleType(), False),
    StructField("v4", DoubleType(), False),
    StructField("v5", DoubleType(), False),
    StructField("v6", DoubleType(), False),
    StructField("v7", DoubleType(), False),
    StructField("v8", DoubleType(), False),
    StructField("v9", DoubleType(), False),
    StructField("v10", DoubleType(), False),
    StructField("v11", DoubleType(), False),
    StructField("v12", DoubleType(), False),
    StructField("v13", DoubleType(), False),
    StructField("v14", DoubleType(), False),
    StructField("v15", DoubleType(), False),
    StructField("v16", DoubleType(), False),
    StructField("v17", DoubleType(), False),
    StructField("v18", DoubleType(), False),
    StructField("v19", DoubleType(), False),
    StructField("v20", DoubleType(), False),
    StructField("v21", DoubleType(), False),
    StructField("v22", DoubleType(), False),
    StructField("v23", DoubleType(), False),
    StructField("v24", DoubleType(), False),
    StructField("v25", DoubleType(), False),
    StructField("v26", DoubleType(), False),
    StructField("v27", DoubleType(), False),
    StructField("v28", DoubleType(), False),
    StructField("amount", DoubleType(), False),
    StructField("class", IntegerType(), False),
    StructField("load_timestamp", TimestampType(), False),
    StructField("source_file", StringType(), False),
])

def load_and_validate_csv(csv_path: str) -> pd.DataFrame:
    """Load CSV with pandas first for preprocessing"""
    print(f"Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Rename columns to lowercase
    df.columns = [col.strip().lower() for col in df.columns]
    
    print(f"Initial rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    return df

def validate_bronze_schema(pdf: pd.DataFrame) -> pd.DataFrame:
    """Validate data meets bronze schema requirements"""
    
    print("\n=== VALIDATING BRONZE SCHEMA ===")
    
    # Check for required columns
    required_cols = ['time', 'amount', 'class'] + [f'v{i}' for i in range(1, 29)]
    missing_cols = [col for col in required_cols if col not in pdf.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    
    # Data type validations
    print(" Column check: PASSED")
    
    # Amount validation: must be >= 0
    invalid_amounts = (pdf['amount'] < 0).sum()
    if invalid_amounts > 0:
        print(f"Found {invalid_amounts} negative amounts - removing")
        pdf = pdf[pdf['amount'] >= 0]
    
    # Class validation: must be 0 or 1
    invalid_class = (~pdf['class'].isin([0, 1])).sum()
    if invalid_class > 0:
        print(f" Found {invalid_class} invalid class values - removing")
        pdf = pdf[pdf['class'].isin([0, 1])]
    
    # Missing values check
    missing = pdf.isnull().sum().sum()
    if missing > 0:
        print(f"Found {missing} null values - removing rows with nulls")
        pdf = pdf.dropna()
    
    # Time validation
    if pdf['time'].min() < 0:
        print(f"Found negative time values - removing")
        pdf = pdf[pdf['time'] >= 0]
    
    print(f"✓ Amount check: {(pdf['amount'] >= 0).sum()} valid")
    print(f"✓ Class values: {pdf['class'].value_counts().to_dict()}")
    print(f"✓ Rows after validation: {len(pdf)}")
    
    return pdf

def create_bronze_layer(csv_path: str, output_path: str = "src/bronze"):
    """Main Bronze layer creation function"""
    
    # Ensure output path exists
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Load and validate
    pdf = load_and_validate_csv(csv_path)
    pdf = validate_bronze_schema(pdf)
    
    # Add metadata
    load_ts = datetime.now()
    pdf['load_timestamp'] = load_ts
    pdf['source_file'] = Path(csv_path).name
    
    # Convert to Spark for writing to Delta/Unity Catalog
    print(f"\n=== CREATING BRONZE LAYER ===")
    sdf = spark.createDataFrame(pdf, schema=BRONZE_SCHEMA)
    
    # Write to Unity Catalog as Delta table
    table_name = "data_engineering_workshop.creditcard.creditcard_bronze"
    print(f"Writing to Unity Catalog: {table_name}")
    
    sdf.write \
        .mode("overwrite") \
        .format("delta") \
        .saveAsTable(table_name)
    
    print(f"✓ Bronze layer created successfully")
    print(f"✓ Total records: {sdf.count():,}")
    print(f"✓ Schema validated")
    print(f"✓ Format: Delta (Unity Catalog)")
    print(f"✓ Table: {table_name}")
    
    return table_name

if __name__ == "__main__":
    # Usage
    csv_file = "data/raw/creditcard.csv"
    bronze_output = create_bronze_layer(csv_file)
    print(f"\n BRONZE LAYER COMPLETE: {bronze_output}")
