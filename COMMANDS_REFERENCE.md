# 🚀 Databricks Asset Bundle - Quick Commands Reference

## Installation & Setup (One-time)

```bash
# 1. Install CLI
pip install databricks-cli

# 2. Configure authentication
databricks configure --token
# Enter: https://adb-xxxx.azuredatabricks.net
# Enter: dapi4xxxxxxxxxxxxxxxxxxxxxxx

# 3. Verify connection
databricks workspace list

# 4. List existing clusters
databricks clusters list
```

---

## Bundle Configuration & Validation

```bash
# Set your cluster ID (save these!)
export CLUSTER_ID="0704-123456-xxxxx"
export WORKSPACE_ID="1234567890"

# Navigate to project
cd bsg-pipeline

# Validate bundle syntax
databricks bundle validate -t dev

# See what will be deployed (dry-run)
databricks bundle plan -t dev
```

---

## Deployment Commands

### Deploy to Dev Environment
```bash
# Deploy to dev
databricks bundle deploy -t dev

# Expected output:
# ✓ Uploading artifacts...
# ✓ Creating jobs...
# ✓ ingestion_job (id: 123)
# ✓ bronze_job (id: 124)
# ✓ silver_job (id: 125)
# ✓ gold_job (id: 126)
```

### Deploy to Production
```bash
# Deploy to prod
databricks bundle deploy -t prod

# Same output but for prod environment
```

### Destroy Bundle (Delete jobs)
```bash
# Remove dev jobs
databricks bundle destroy -t dev

# Remove prod jobs
databricks bundle destroy -t prod
```

---

## Job Management

### List All Jobs
```bash
# List all jobs in workspace
databricks jobs list

# List with JSON output
databricks jobs list --output json
```

### Get Job Details
```bash
# Get specific job info
databricks jobs get --job-id 124

# Get last run info
databricks jobs list-runs --job-id 124 --limit 1
```

### Trigger Job Run
```bash
# Run job immediately
databricks jobs run-now --job-id 124

# With parameters
databricks jobs run-now --job-id 124 --notebook-params '{"param1":"value1"}'
```

### Monitor Job Runs
```bash
# Get run history (last 10)
databricks jobs list-runs --job-id 124 --limit 10

# Get specific run details
databricks jobs get-run --run-id 456

# Get run state
databricks jobs get-run --run-id 456 | jq '.state'
```

### Cancel Running Job
```bash
# Cancel specific run
databricks jobs cancel-run --run-id 456
```

---

## Airflow Integration

### Install Airflow with Databricks
```bash
# Create venv
python -m venv airflow_env
source airflow_env/bin/activate

# Install dependencies
pip install -r airflow/requirements.txt

# Initialize database
export AIRFLOW_HOME=/opt/airflow
airflow db init
```

### Configure Databricks Connection
```bash
# Add connection via CLI
airflow connections add 'databricks_default' \
    --conn-type 'databricks' \
    --conn-host 'https://adb-xxxx.azuredatabricks.net' \
    --conn-password 'dapi4xxxxx'

# Or use UI: Admin → Connections → Create
```

### Set Airflow Variables
```bash
# Set variables
airflow variables set databricks_host "https://adb-xxxx.azuredatabricks.net"
airflow variables set databricks_token "dapi4xxxxx"
airflow variables set ingestion_job_id "123"
airflow variables set bronze_job_id "124"
airflow variables set silver_job_id "125"
airflow variables set gold_job_id "126"
```

### Start Airflow Services
```bash
# Terminal 1: Start webserver
airflow webserver --port 8080

# Terminal 2: Start scheduler
airflow scheduler

# Browse: http://localhost:8080
```

### Trigger Airflow DAG
```bash
# Trigger DAG
airflow dags trigger creditcard_fraud_etl_pipeline

# See DAG runs
airflow dags list-runs --dag-id creditcard_fraud_etl_pipeline

# Get DAG state
airflow dags state creditcard_fraud_etl_pipeline
```

### Monitor DAG Execution
```bash
# List DAG runs
airflow dags list-runs --dag-id creditcard_fraud_etl_pipeline --limit 10

# Get task logs
airflow tasks logs creditcard_fraud_etl_pipeline ingest_data 2024-01-01
```

---

## GitHub Actions

### Trigger Workflows

#### On Pull Request (Auto)
```bash
# Create feature branch and push
git checkout -b feature/update
git push origin feature/update

# Create PR on GitHub → pr_validate.yml runs automatically
```

#### On Push to Main (Auto)
```bash
# Merge PR to main
git checkout main
git pull origin main

# deploy_prod.yml runs automatically
```

### Manual Workflow Trigger (GitHub UI)
```
GitHub → Actions → Deploy to Production → Run Workflow
```

### View Workflow Results
```
GitHub → Actions → Logs → Select workflow run
```

---

## Database/State Management

### View Workspace State
```bash
# List all deployed bundles
databricks workspace list /Shared/.bundle/

# View bundle metadata
databricks workspace read-only /Shared/.bundle/state.json
```

### Clean Up State
```bash
# Remove failed deployments
databricks workspace delete /Shared/.bundle/

# Redeploy clean
databricks bundle deploy -t dev
```

---

## Workspace Management

### List Workspace Contents
```bash
# List root
databricks workspace ls /

# List by environment
databricks workspace ls /Workspace/Users/aradhan/bsg-pipeline-dev
databricks workspace ls /Workspace/Shared/bsg-pipeline-prod
```

### Upload Files
```bash
# Upload notebook
databricks workspace import src/01_bronze_schema.py /Workspace/bsg-pipeline/
```

### Download Files
```bash
# Export notebook
databricks workspace export /Workspace/bsg-pipeline/01_bronze_schema.py --is-source
```

---

## Debugging & Troubleshooting

### Check CLI Version
```bash
databricks --version
```

### Test Connection
```bash
# Verify authentication works
databricks workspace list

# Should show workspace paths if successful
```

### View Bundle Configuration
```bash
# Show resolved config
databricks bundle validate -t dev --out json
```

### Get Full Job Specification
```bash
# Export job as JSON
databricks jobs export --job-id 124 --output-path job.json
```

### Check Cluster Status
```bash
# List clusters
databricks clusters list

# Get cluster details
databricks clusters get --cluster-id 0704-123456-xxxxx

# Status should be: RUNNING or PENDING
```

---

## Common Workflows

### Deploy & Test (Dev)
```bash
# 1. Validate
databricks bundle validate -t dev

# 2. Plan
databricks bundle plan -t dev

# 3. Deploy
databricks bundle deploy -t dev

# 4. Get job IDs
databricks jobs list --output json | grep job_id

# 5. Trigger test run
databricks jobs run-now --job-id 124

# 6. Monitor
databricks jobs list-runs --job-id 124 --limit 1
```

### Promote to Production
```bash
# 1. Verify dev is working
databricks jobs list-runs --job-id 124 --limit 5

# 2. Deploy to prod
databricks bundle deploy -t prod

# 3. Run first job
databricks jobs run-now --job-id 224  # prod bronze job

# 4. Monitor
databricks jobs list-runs --job-id 224 --limit 1
```

### Update Job Configuration
```bash
# 1. Edit resources/bronze_job.yml

# 2. Validate
databricks bundle validate -t dev

# 3. Deploy
databricks bundle deploy -t dev

# New configuration takes effect immediately
```

---

## Environment Variables Setup

Save to `~/.bashrc` or `~/.zshrc`:

```bash
# Databricks
export DATABRICKS_HOST="https://adb-xxxx.azuredatabricks.net"
export DATABRICKS_TOKEN="dapi4xxxxxxxxxxxxxxxxxxxxxxx"
export CLUSTER_ID="0704-123456-xxxxx"
export WORKSPACE_ID="1234567890"

# Airflow
export AIRFLOW_HOME="/opt/airflow"
export AIRFLOW__CORE__DATALAKE_HOME="/opt/airflow"

# GitHub
export GITHUB_REPO="org/bsg-pipeline"
export GITHUB_TOKEN="ghp_xxx"
```

Load with:
```bash
source ~/.bashrc
```

---

## Health Check Script

Save as `check_pipeline.sh`:

```bash
#!/bin/bash

echo "🔍 Checking pipeline health..."

# Check Databricks connection
echo -n "Databricks: "
databricks workspace list > /dev/null && echo "✓" || echo "✗"

# Check cluster
echo -n "Cluster: "
databricks clusters get --cluster-id $CLUSTER_ID > /dev/null && echo "✓" || echo "✗"

# Check jobs
echo -n "Jobs: "
databricks jobs list > /dev/null && echo "✓" || echo "✗"

# List recent runs
echo ""
echo "📊 Recent Job Runs:"
databricks jobs list-runs --job-id 124 --limit 3 --output table

echo ""
echo "✅ Health check complete"
```

Run with:
```bash
chmod +x check_pipeline.sh
./check_pipeline.sh
```

---

## Key Metrics to Monitor

```bash
# Job execution time
databricks jobs get-run --run-id 456 | jq '.execution_duration'

# Job status
databricks jobs get-run --run-id 456 | jq '.state'

# Number of tasks in job
databricks jobs get --job-id 124 | jq '.settings.tasks | length'
```

---

## Performance Tuning

### Check Cluster Performance
```bash
# Get cluster configuration
databricks clusters get --cluster-id $CLUSTER_ID

# Modify cluster (if needed)
databricks clusters edit --cluster-id $CLUSTER_ID --attributes attributes.json
```

### Optimize Job Parameters
```bash
# View current job config
databricks jobs get --job-id 124 | jq '.settings'

# Edit and update
databricks jobs update --job-id 124 --attributes-file updates.json
```

---

## Backup & Recovery

### Export All Jobs
```bash
# Export as JSON
databricks jobs list --output json > jobs_backup.json

# Export specific job
databricks jobs export --job-id 124 > bronze_job.json
```

### Import Jobs
```bash
# Import from JSON
databricks jobs import --from-json job.json
```

---

**Quick Reference Summary**:
- ✓ `databricks bundle validate -t dev` - Check syntax
- ✓ `databricks bundle deploy -t dev` - Deploy to dev
- ✓ `databricks jobs run-now --job-id 124` - Trigger job
- ✓ `databricks jobs list-runs --job-id 124` - Check status
- ✓ Airflow DAG: `airflow dags trigger creditcard_fraud_etl_pipeline`

