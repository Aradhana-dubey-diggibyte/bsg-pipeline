# CREDITCARD DATASET ANALYSIS & TRANSFORMATION BLUEPRINT

## 📊 DATASET OVERVIEW

### Basic Statistics
- **Total Records**: 284,808 transactions
- **Time Period**: Captures sequences of transactions over ~2 days  
- **File Size**: ~144 MB (CSV)
- **Data Quality**: No missing values ✓
- **Class Imbalance**: 99.83% Legitimate, 0.17% Fraud (492 frauds)

### Column Structure (31 Total)

| Column | Type | Description |
|--------|------|-------------|
| Time | Integer | Seconds since first transaction (0 to 172,792) |
| V1-V28 | Float | PCA-transformed anonymized features (σ ≈ 1.0) |
| Amount | Float | Transaction amount in USD ($0.00 - $25,691.16) |
| Class | Integer | 0=Legitimate, 1=Fraudulent |

### Key Statistics
- **Amount Range**: $0.00 to $25,691.16
  - Legitimate mean: $88.35
  - Fraud mean: $122.21
- **Features**: Already normalized (PCA transformation) - no scaling needed
- **Temporal Distribution**: Transactions span approximately 2 days

---

## 🔄 MEDALLION ARCHITECTURE TRANSFORMATIONS

### BRONZE LAYER: Data Ingestion & Validation
**Purpose**: Capture raw data with schema enforcement and data lineage

**Transformations**:
1. Load CSV into standardized schema
2. Add ingestion metadata (load_timestamp, source_file)
3. Enforce data types & nullability
4. Implement partition strategy (daily by time window)
5. Store in Parquet format for efficiency

**Quality Checks**:
- All columns present and correct type
- Amount >= 0
- Class in {0, 1}
- Time is monotonic increasing
- Row count validation

---

### SILVER LAYER: Data Cleaning & Standardization
**Purpose**: Clean, deduplicate, and standardize data

#### Phase 1: Deduplication (02_silver_dedup.py)
- **Detect**: Exact duplicate rows (all columns identical)
- **Detect**: Proxy duplicates (same Time + Amount + Class within 5-minute window)
- **Action**: Keep first occurrence, flag duplicates
- **Expected**: < 1% duplicates

#### Phase 2: Standardization (03_silver_standardise.py)
- Normalize Amount to standard scale (0-1 or Z-score)
- Convert Time to meaningful features (hour of day, day of week, is_night)
- Validate feature ranges (V1-V28 should be ~ N(0,1))
- Handle edge cases ($0 transactions, midnight crossings)

#### Phase 3: PII Masking (04_silver_pii_mask.py)
- While data is already anonymized (PCA), add governance:
  - Mask Amount for sensitive analysis to ranges
  - Flag high-value transactions (> $5,000)
  - Add data classification tags

#### Phase 4: Derived Features (05_silver_derived.py)
- Amount buckets: micro ($0-50), small ($50-200), medium ($200-1000), large (>$1000)
- Time features: hour, day_of_week, is_night_hour (22:00-06:00)
- Risk indicators: high_amount_flag, unusual_time_flag
- Feature engineering: interaction terms if needed

---

### GOLD LAYER: Analytics & Business Metrics
**Purpose**: Aggregated, analysis-ready datasets

#### Phase 1: Risk Scoring (06_gold_risk_score.py)
- Compute fraud probability by transaction characteristics
- Build risk segments:
  - LOW: Clean customers, normal patterns
  - MEDIUM: Some anomalies but legitimate
  - HIGH: Multiple fraud indicators present
  - CRITICAL: Strong fraud signals

- Risk factors:
  - High transaction amount
  - Unusual time
  - V18, V19, V20 anomalies (top fraud indicators)

#### Phase 2: Rolling Metrics (07_gold_rolling_metrics.py)
- Hourly aggregations:
  - Transaction count, fraud count, fraud rate
  - Average amount by class
  - Feature statistics (V1-V28 mean/std)
- Customer behavior trends (if customer ID available)
- Fraud spike detection

#### Phase 3: KPI Mart (08_gold_kpi_mart.py)
- Business KPIs for dashboards:
  - Total transactions, fraud cases, fraud rate
  - Total amount, fraud amount, fraud loss %
  - Risk distribution (low/med/high/critical %)
  - Hourly/daily fraud trends

---

## 📁 FILE FORMAT CONVERSION

### CSV → Parquet Benefits
- **Compression**: 5-10x reduction (144 MB → 15-30 MB)
- **Query Speed**: 10-100x faster for analytics
- **Schema**: Enforced & versioned
- **Compatibility**: Works with Spark, Databricks, DuckDB

### Conversion Strategy
```
Raw CSV → Bronze (Parquet) → Silver (Parquet) → Gold (Parquet)
           |                   |                  |
         184 MB             45 MB               20 MB
```

---

## 🎯 RECOMMENDED TRANSFORMATIONS SUMMARY

| Layer | Transformations | Output Records | Format |
|-------|-----------------|-----------------|---------|
| **Bronze** | Schema validation, type conversion | 284,808 | Parquet |
| **Silver** | Dedup, standardize, mask, derive features | 283,000-284,500 | Parquet |
| **Gold** | Scoring, metrics, KPIs | 100-1,000 (aggregated) | Parquet |

---

## 💡 ADDITIONAL RECOMMENDATIONS

1. **Add Customer Dimension**: If available, link transactions to customers
2. **Add Merchant Category**: If available, enable merchant-level analysis
3. **Time Series Analysis**: Detect temporal patterns in fraud
4. **Anomaly Detection**: Isolation Forest on V1-V28 features
5. **Fraud Patterns**: Geographic (if location available) or time-based
6. **Model Scoring**: Apply trained ML model for real-time risk prediction

