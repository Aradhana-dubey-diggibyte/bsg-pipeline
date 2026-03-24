# Databricks Asset Bundle ETL Pipeline - Complete Setup Guide

## Overview

This is a production-ready Databricks Asset Bundle for the Credit Card Fraud Detection ETL pipeline with:
- ✅ 3-layer medallion architecture (Bronze/Silver/Gold)
- ✅ Databricks Asset Bundle for IaC (Infrastructure as Code)
- ✅ GitHub Actions for CI/CD
- ✅ Airflow for orchestration & monitoring
- ✅ Environment-based deployments (Dev/Prod)

---

## Architecture

```
GitHub Repository
    ↓
GitHub Actions (CI/CD)
    ├─ PR Validation (lint, test, security)
    └─ Deploy to Prod (merge to main)
    ↓
Databricks Asset Bundle
    ├─ Dev Environment
    ├─ Prod Environment
    └─ Shared Resources
    ↓
Databricks Jobs (Orchestrated)
    ├─ Ingestion Job (Monthly)
    ├─ Bronze Job (Daily 01:30 UTC)
    ├─ Silver Job (Daily 01:45 UTC)
    └─ Gold Job (Daily 02:15 UTC)
    ↓
Airflow DAGs (Monitoring & Scheduling)
    ├─ Main ETL Pipeline (Daily 02:00 UTC)
    └─ Monitoring DAG (Every 6 hours)
```

---

## Prerequisites

### 1. Databricks Account & Cluster
- ✓ Databricks workspace (already have one)
- ✓ Existing cluster ID (DON'T create new - use existing)
- ✓ PAT token for authentication

### 2. GitHub Repository
- ✓ Repository SSH key configured
- ✓ Secrets configured in GitHub

### 3. Airflow Setup
- ✓ Airflow instance (local or managed)
- ✓ Databricks connection configured

### 4. Environment Variables
```bash
# Databricks
export DATABRICKS_HOST="https://adb-xxxx.azuredatabricks.net"
export DATABRICKS_TOKEN="dapi4xxxxxxxxxxxxxxxxxxxxxxx"
export CLUSTER_ID="0704-123456-xxxxx"

# GitHub
export GITHUB_REPO="your-org/bsg-pipeline"
export GITHUB_TOKEN="ghp_xxx"

# Airflow
export AIRFLOW_HOME="/opt/airflow"
export AIRFLOW__CORE__DATALAKE_HOME="/opt/airflow"

# Slack (optional)
export SLACK_WEBHOOK="https://hooks.slack.com/services/xxx"
```

---

## Setup Instructions

### Step 1: Initialize Databricks CLI

```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token
# Enter host: https://adb-xxxx.azuredatabricks.net
# Enter token: dapi4xxxxxxxxxxxxxxxxxxxxxxx
```

### Step 2: Configure Bundle Variables

Create `.databricks/config.local.yml`:
```yaml
variables:
  workspace_id: "1234567890"
  cluster_id: "0704-123456-xxxxx"  # YOUR EXISTING CLUSTER
  user_name: "aradhan"
  environment: "dev"
  alert_email: "dev-alerts@company.com"
```

### Step 3: Validate Bundle

```bash
# Move to project root
cd bsg-pipeline

# Validate bundle (dev environment)
databricks bundle validate -t dev

# Show deployment plan
databricks bundle plan -t dev
```

### Step 4: Deploy Bundle (Dev)

```bash
# Deploy to dev environment
databricks bundle deploy -t dev

# Output: Jobs created in Databricks workspace
```

### Step 5: Deploy to Production

```bash
# Update config variables for prod
# Then deploy to prod
databricks bundle deploy -t prod
```

---

## GitHub Actions Setup

### 1. Configure Secrets in GitHub

Go to: Settings → Secrets and Variables → Actions

Add these secrets:
```
DATABRICKS_HOST          = https://adb-xxxx.azuredatabricks.net
DATABRICKS_TOKEN         = dapi4xxxxxxxxxxxxxxxxxxxxxxx
SLACK_WEBHOOK            = https://hooks.slack.com/services/xxx
```

### 2. Push Code to Trigger Workflows

```bash
# Create PR to trigger validation
git checkout -b feature/etl-setup
git push origin feature/etl-setup

# Go to GitHub → Pull Requests → Create PR
# Workflow: pr_validate.yml will automatically run
```

### 3. Merge to Deploy

```bash
# After PR approval, merge to main
git checkout main
git merge feature/etl-setup
git push origin main

# Workflow: deploy_prod.yml will automatically run
```

---

## Airflow Setup

### Step 1: Install Airflow Locally (or use managed service)

```bash
# Create virtual environment
python -m venv airflow_env
source airflow_env/bin/activate

# Install Airflow with Databricks provider
pip install -r airflow/requirements.txt

# Initialize database
export AIRFLOW_HOME=/opt/airflow
airflow db init
```

### Step 2: Create Airflow Connections

```bash
# Databricks connection
airflow connections add 'databricks_default' \
    --conn-type 'databricks' \
    --conn-host 'https://adb-xxxx.azuredatabricks.net' \
    --conn-password 'dapi4xxxxxxxxxxxxxxxxxxxxxxx'

# Or use Airflow UI: Admin → Connections
```

### Step 3: Set Airflow Variables

```bash
# Set variables for job IDs
airflow variables set databricks_host "https://adb-xxxx.azuredatabricks.net"
airflow variables set databricks_token "dapi4xxxxxxxxxxxxxxxxxxxxxxx"
airflow variables set ingestion_job_id "123"
airflow variables set bronze_job_id "124"
airflow variables set silver_job_id "125"
airflow variables set gold_job_id "126"
```

### Step 4: Start Airflow

```bash
# Start webserver
airflow webserver --port 8080

# In another terminal, start scheduler
airflow scheduler

# Access UI: http://localhost:8080
```

### Step 5: Trigger DAG

```bash
# Trigger main pipeline DAG
airflow dags trigger creditcard_fraud_etl_pipeline

# Monitor: Go to http://localhost:8080 → DAGs
```

---

## Job Details

### Ingestion Job
- **Schedule**: Monthly (1st of month)
- **Duration**: ~30-60 minutes
- **Input**: Kaggle API
- **Output**: Raw CSV in `data/raw/`

### Bronze Job
- **Schedule**: Daily at 01:30 UTC
- **Duration**: ~15-30 minutes
- **Input**: Raw CSV
- **Output**: Validated Parquet
- **Dependencies**: Ingestion job

### Silver Job
- **Schedule**: Daily at 01:45 UTC
- **Duration**: ~45-60 minutes
- **Phases**: 
  - Deduplication (02)
  - Standardization (03)
  - PII Masking (04)
  - Feature Engineering (05)
- **Output**: Analysis-ready with 60+ features
- **Dependencies**: Bronze job

### Gold Job
- **Schedule**: Daily at 02:15 UTC
- **Duration**: ~30-45 minutes
- **Phases**:
  - Risk Scoring (06)
  - Rolling Metrics (07)
  - KPI Mart (08)
- **Output**: Business-ready tables
- **Dependencies**: Silver job

---

## Monitoring & Alerts

### Databricks Monitoring
- Go to Workspace → Jobs → Select job
- View run history, logs, and metrics

### Airflow Monitoring
- Go to http://localhost:8080
- View DAG runs, logs, and SLA compliance

### Alert Channels
1. **Email Alerts**: dev-alerts@company.com, prod-alerts@company.com
2. **Slack Notifications**: #data-alerts channel
3. **Job Failures**: Automatic retries (2-3 attempts)

### Key Metrics to Monitor
- Job execution time
- Data volume (rows processed)
- Fraud detection rate
- Failure rate
- SLA compliance

---

## Troubleshooting

### Issue: "Cluster not found"
**Solution**: Ensure CLUSTER_ID is correct:
```bash
# List available clusters
databricks clusters list
```

### Issue: "Permission denied"
**Solution**: Check DATABRICKS_TOKEN and workspace permissions

### Issue: Airflow DAG not triggering
**Solution**: 
1. Check Airflow scheduler is running
2. Verify Databricks connection
3. Check job IDs in DAG variables

### Issue: GitHub Actions failing
**Solution**:
1. Check secrets are configured
2. Verify databricks.yml syntax
3. Check bundle validation

---

## File Structure

```
bsg-pipeline/
├── databricks.yml                           # Main bundle config
├── resources/
│   ├── ingestion_job.yml                   # Ingestion job
│   ├── bronze_job.yml                      # Bronze layer job
│   ├── silver_job.yml                      # Silver layer job
│   └── gold_job.yml                        # Gold layer job
├── .github/workflows/
│   ├── pr_validate.yml                     # PR validation workflow
│   └── deploy_prod.yml                     # Prod deployment workflow
├── conf/
│   ├── dev.yml                             # Dev environment config
│   └── prod.yml                            # Prod environment config
├── airflow/
│   ├── dags/
│   │   ├── creditcard_etl_pipeline.py      # Main ETL DAG
│   │   └── etl_monitoring.py              # Monitoring DAG
│   ├── plugins/                            # Custom operators
│   ├── config/                             # Airflow config
│   ├── requirements.txt                    # Python dependencies
│   └── Dockerfile                          # Docker image
└── src/
    ├── 00_ingest_kaggle.py                # Ingestion script
    ├── 01_bronze_schema.py                # Bronze transformation
    ├── 02_silver_dedup.py                 # Silver dedup
    ├── 03_silver_standardise.py           # Silver standardize
    ├── 04_silver_pii_mask.py              # Silver mask
    ├── 05_silver_derived.py               # Silver features
    ├── 06_gold_risk_score.py              # Gold risk scoring
    ├── 07_gold_rolling_metrics.py         # Gold metrics
    └── 08_gold_kpi_mart.py                # Gold KPI mart
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Databricks cluster exists (not creating new)
- [ ] DATABRICKS_TOKEN is valid
- [ ] CLUSTER_ID is correct
- [ ] GitHub repository has all code
- [ ] GitHub Actions secrets configured
- [ ] Airflow instance ready

### Deployment
- [ ] Run `databricks bundle validate`
- [ ] Run `databricks bundle plan`
- [ ] Run `databricks bundle deploy -t dev`
- [ ] Verify jobs created in Databricks
- [ ] Run manual job test (dev)
- [ ] Deploy to prod `databricks bundle deploy -t prod`

### Post-Deployment
- [ ] Check job run history
- [ ] Monitor first pipeline run
- [ ] Verify data in each layer
- [ ] Set up Airflow monitoring
- [ ] Configure alerts
- [ ] Document runbook

---

## Maintenance

### Regular Tasks
- Monitor job execution times
- Archive old runs (30+ days)
- Update job configurations as needed
- Review failure patterns
- Optimize Spark parameters

### Version Management
- Tag releases: `v1.0.0`, `v1.1.0`, etc.
- Maintain changelog
- Use semantic versioning

### Backup & Recovery
- Databricks: Workspace configuration backup
- Airflow: DAG backup
- Code: Git version control

---

## Next Steps

1. **Execute Setup**: Follow installation steps above
2. **Test Locally**: Run Airflow DAG manually
3. **Monitor Production**: Watch first prod run
4. **Optimize**: Adjust schedules, resources based on metrics
5. **Scaling**: Add more jobs/monitoring as needed

---

## Support & Documentation

- **Databricks Docs**: https://docs.databricks.com
- **Airflow Docs**: https://airflow.apache.org/docs/
- **Asset Bundle**: https://docs.databricks.com/dev-tools/bundles/
- **GitHub Actions**: https://docs.github.com/en/actions

---

**Status**: ✅ Complete Setup Ready  
**Last Updated**: 2024  
**Maintained by**: Data Engineering Team
