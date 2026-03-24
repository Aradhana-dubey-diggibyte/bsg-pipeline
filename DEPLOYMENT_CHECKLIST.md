# ✅ Deployment Checklist - BSG Pipeline

## Phase 1: Prerequisites (Check Before Starting)

### Environment Setup
- [ ] Databricks workspace created
- [ ] Databricks cluster exists (note the cluster ID)
- [ ] Databricks Personal Access Token generated
- [ ] GitHub repository created and cloned
- [ ] Python 3.8+ installed locally
- [ ] Git configured locally

### Required Information (Save These!)
```
Workspace URL: https://adb-xxxx.azuredatabricks.net
Cluster ID:   0704-123456-xxxxx
Token:        dapi4xxxxxxxxxxxxxxxxxxxxx
GitHub Repo:  owner/bsg-pipeline
```

### System Requirements
- [ ] macOS / Linux / Windows (with WSL)
- [ ] pip / conda installed
- [ ] Docker installed (for Airflow)
- [ ] 10+ GB free disk space

---

## Phase 2: Local Setup (15 minutes)

### Step 1: Clone Repository
```bash
[ ] git clone https://github.com/owner/bsg-pipeline.git
[ ] cd bsg-pipeline
```

### Step 2: Install Databricks CLI
```bash
[ ] pip install databricks-cli
[ ] databricks --version
# Output: X.Y.Z (any recent version OK)
```

### Step 3: Configure Databricks Authentication
```bash
[ ] databricks configure --token
# Input 1: your workspace URL (https://adb-xxxx.azuredatabricks.net)
# Input 2: your personal access token (dapi4xxx...)
```

### Step 4: Verify Connection
```bash
[ ] databricks workspace list
# Should output list of workspace directories without errors
[ ] echo $DATABRICKS_HOST
# Should output your workspace URL
[ ] echo $DATABRICKS_TOKEN  
# Should output your token (if set as env var)
```

### Step 5: Export Environment Variables
```bash
[ ] export DATABRICKS_HOST="https://adb-xxxx.azuredatabricks.net"
[ ] export DATABRICKS_TOKEN="dapi4xxxxx"
[ ] export CLUSTER_ID="0704-123456-xxxxx"

# Optional: Add to ~/.bashrc or ~/.zshrc for persistence
[ ] Add exports to shell profile
```

**Estimated time**: 15 minutes  
**Success indicators**: 
- ✓ `databricks workspace list` works
- ✓ Environment variables set

---

## Phase 3: Bundle Validation (10 minutes)

### Step 1: Validate YAML Syntax
```bash
[ ] cd bsg-pipeline
[ ] databricks bundle validate -t dev
# Output should show: "Validation complete" with no errors
```

### Step 2: Check Bundle Plan (Dry-Run)
```bash
[ ] databricks bundle plan -t dev
# Output shows what will be created:
# - ingestion_job
# - bronze_job  
# - silver_job
# - gold_job
```

### Step 3: Review Resource Files
```bash
[ ] cat databricks.yml | grep -E "targets|variables|permissions"
# Verify dev/prod targets exist

[ ] cat resources/ingestion_job.yml | grep -E "name|schedule"
# Verify ingestion job is configured

[ ] cat resources/bronze_job.yml | grep -E "depends_on"
# Verify bronze depends on ingestion

[ ] cat resources/silver_job.yml | grep -E "tasks" | head -5
# Verify silver has 4 tasks

[ ] cat resources/gold_job.yml | grep -E "depends_on|timeout"
# Verify gold dependencies and timeout
```

**Estimated time**: 10 minutes  
**Success indicators**:
- ✓ `bundle validate` passes without errors
- ✓ `bundle plan` shows 4 jobs

---

## Phase 4: Deploy to Dev (15 minutes)

### Step 1: Deploy Bundle
```bash
[ ] databricks bundle deploy -t dev
# Output shows:
# - Deployment successful
# - Job IDs created (ingestion_job_id=123, bronze_job_id=124, etc.)
```

### Step 2: Record Job IDs
In the deployment output, you'll see:
```
Resource Updates:
✓ ingestion_job: job_id = 123
✓ bronze_job: job_id = 124
✓ silver_job: job_id = 125
✓ gold_job: job_id = 126
```

**Copy these values**:
```
INGESTION_JOB_ID = ___________
BRONZE_JOB_ID = ___________
SILVER_JOB_ID = ___________
GOLD_JOB_ID = ___________
```

### Step 3: Verify Jobs Created
```bash
[ ] databricks jobs list --output json | grep -E "creditcard-dev"
# Should show 4 jobs with names:
# - creditcard-dev-ingestion
# - creditcard-dev-bronze
# - creditcard-dev-silver
# - creditcard-dev-gold
```

### Step 4: Test Dry Run (Optional)
```bash
[ ] databricks jobs run-now --job-id 123
# This triggers the ingestion job (first in pipeline)
# Monitor at: Databricks UI → Jobs → creditcard-dev-ingestion
[ ] Wait for completion (should take 1-5 minutes)
[ ] Verify job succeeded (no errors)
```

**Estimated time**: 15 minutes  
**Success indicators**:
- ✓ `bundle deploy` completes successfully
- ✓ 4 jobs appear in `jobs list`
- ✓ Job IDs recorded

---

## Phase 5: GitHub Actions Setup (20 minutes)

### Step 1: Add GitHub Secrets
Go to: GitHub → Settings → Secrets and variables → Actions

Add these secrets:
```bash
[ ] DATABRICKS_HOST = "https://adb-xxxx.azuredatabricks.net"
[ ] DATABRICKS_TOKEN = "dapi4xxxxxxxxxxxxxxxxxxxxx"
[ ] SLACK_WEBHOOK = "https://hooks.slack.com/xxxxx" (optional)
```

### Step 2: Verify GitHub Files Exist
```bash
[ ] ls -la .github/workflows/pr_validate.yml
# File should exist and contain linting rules

[ ] ls -la .github/workflows/deploy_prod.yml  
# File should exist and contain deployment steps

[ ] cat .github/workflows/pr_validate.yml | head -10
# Should show: on: pull_request, branches: [main, develop]

[ ] cat .github/workflows/deploy_prod.yml | head -10
# Should show: on: push, branches: [main]
```

### Step 3: Create Feature Branch for Testing
```bash
[ ] git checkout -b feature/test-workflow
[ ] git add .
[ ] git commit -m "Testing CI/CD workflow"
[ ] git push origin feature/test-workflow
```

### Step 4: Create Pull Request
```bash
[ ] Go to GitHub repo
[ ] Click "New Pull Request"
[ ] Base: main, Compare: feature/test-workflow
[ ] Click "Create Pull Request"

[ ] GitHub → Actions tab
[ ] Watch pr_validate.yml run:
    [ ] Job: lint-python ✓
    [ ] Job: security-check ✓
    [ ] Job: validate-yaml ✓
    [ ] Job: unit-tests ✓ (optional, if tests added)
    [ ] Job: databricks-validate ✓
```

### Step 5: Merge PR (This Will Deploy!)
```bash
[ ] PR checks pass
[ ] Click "Merge pull request"
[ ] GitHub → Actions tab
[ ] Watch deploy_prod.yml run:
    [ ] Job: validate ✓
    [ ] Job: deploy ✓
    [ ] Job: smoke-tests ✓
    [ ] Job: notify ✓ (Slack notification, if webhook added)
```

**Estimated time**: 20 minutes  
**Success indicators**:
- ✓ GitHub secrets created (3 secrets)
- ✓ pr_validate.yml runs on PR creation
- ✓ deploy_prod.yml runs on merge
- ✓ All jobs pass (no red X marks)

---

## Phase 6: Airflow Setup (30 minutes)

### Step 1: Create Python Virtual Environment
```bash
[ ] python -m venv airflow_env
[ ] source airflow_env/bin/activate  # On Windows: airflow_env\Scripts\activate
[ ] pip install --upgrade pip
```

### Step 2: Install Airflow Dependencies
```bash
[ ] pip install -r airflow/requirements.txt
# This installs 25+ packages (may take 5-10 minutes)

[ ] Verify installation:
    [ ] python -c "import airflow; print(airflow.__version__)"
    # Output: 2.6.X or higher
```

### Step 3: Initialize Airflow Database
```bash
[ ] export AIRFLOW_HOME=$PWD/airflow
[ ] airflow db init
# This creates airflow.db SQLite database

[ ] ls -la $AIRFLOW_HOME/airflow.db
# File should exist
```

### Step 4: Create Airflow Admin User
```bash
[ ] airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin123

[ ] Save these credentials:
    Username: admin
    Password: admin123
```

### Step 5: Add Databricks Connection
```bash
[ ] airflow connections add databricks_default \
    --conn-type databricks \
    --conn-host $DATABRICKS_HOST \
    --conn-password $DATABRICKS_TOKEN

[ ] Verify:
    [ ] airflow connections list | grep databricks
    [ ] airflow connections test databricks_default
    # Output: "Connection successfully tested"
```

### Step 6: Set Airflow Variables
```bash
[ ] airflow variables set DATABRICKS_HOST $DATABRICKS_HOST
[ ] airflow variables set DATABRICKS_TOKEN $DATABRICKS_TOKEN
[ ] airflow variables set INGESTION_JOB_ID <job_id_from_phase_4>
[ ] airflow variables set BRONZE_JOB_ID <job_id_from_phase_4>
[ ] airflow variables set SILVER_JOB_ID <job_id_from_phase_4>
[ ] airflow variables set GOLD_JOB_ID <job_id_from_phase_4>

[ ] Verify variables:
    [ ] airflow variables list
    # Should list 6 variables
```

### Step 7: Start Airflow Services (2 Terminals)

**Terminal 1: Start Webserver**
```bash
[ ] source airflow_env/bin/activate
[ ] export AIRFLOW_HOME=$PWD/airflow
[ ] airflow webserver --port 8080

# Wait for output: "Airflow webserver started on [::]:8080"
```

**Terminal 2: Start Scheduler**
```bash
[ ] source airflow_env/bin/activate
[ ] export AIRFLOW_HOME=$PWD/airflow
[ ] airflow scheduler

# Wait for output: "Starting the scheduler"
```

### Step 8: Access Airflow UI
```bash
[ ] Open browser: http://localhost:8080
[ ] Login with credentials from Step 4
[ ] Click "DAGs" tab
[ ] Verify you see:
    [ ] creditcard_fraud_etl_pipeline (main DAG)
    [ ] etl_pipeline_monitoring (monitoring DAG)
```

### Step 9: Enable DAGs
```bash
[ ] In Airflow UI, find: creditcard_fraud_etl_pipeline
[ ] Toggle on (switch to blue/enabled state)
[ ] Repeat for: etl_pipeline_monitoring
```

### Step 10: Manual DAG Trigger (Test)
```bash
[ ] In Airflow UI:
    [ ] Hover over DAG name
    [ ] Click "Trigger DAG" button
    [ ] DAG starts executing

[ ] Monitor execution:
    [ ] Click DAG name to view graph
    [ ] Watch tasks progress (green = success)
    [ ] Should flow: start → ingest → bronze → silver → gold → end

[ ] Wait for completion (5-15 minutes)
[ ] Check logs for errors (if any tasks red):
    [ ] Click failed task
    [ ] Click "Log" tab
    [ ] Fix issues (typically missing job IDs)
```

**Estimated time**: 30 minutes  
**Success indicators**:
- ✓ Airflow UI accessible at http://localhost:8080
- ✓ 2 DAGs visible
- ✓ Databricks connection test passes
- ✓ All variables set
- ✓ DAG triggers and runs without errors

---

## Phase 7: Production Deployment (15 minutes)

### Step 1: Deploy to Production
```bash
[ ] databricks bundle deploy -t prod
# Output shows prod jobs created:
# - creditcard-prod-ingestion
# - creditcard-prod-bronze
# - creditcard-prod-silver
# - creditcard-prod-gold
```

### Step 2: Record Production Job IDs
```
PROD_INGESTION_JOB_ID = ___________
PROD_BRONZE_JOB_ID = ___________
PROD_SILVER_JOB_ID = ___________
PROD_GOLD_JOB_ID = ___________
```

### Step 3: Verify Production Jobs
```bash
[ ] databricks jobs list --output json | grep -E "creditcard-prod"
# Should show 4 prod jobs

[ ] databricks jobs get --job-id <prod_ingestion_id> | grep -E "name|schedule"
# Verify names and schedules correct
```

### Step 4: Backup & Document
```bash
[ ] Export job configs (backup):
    [ ] mkdir -p backups/prod
    [ ] for i in {ingestion,bronze,silver,gold}; do
          databricks jobs export --job-id <prod_${i}_id> \
          --output-path backups/prod/${i}_job.json
        done

[ ] Document in wiki/runbook:
    [ ] Production job IDs
    [ ] Cluster configuration
    [ ] Schedule times
    [ ] Alert contacts
```

**Estimated time**: 15 minutes  
**Success indicators**:
- ✓ `bundle deploy -t prod` completes successfully
- ✓ 4 prod jobs visible in Databricks
- ✓ Job IDs documented

---

## Phase 8: Final Verification (10 minutes)

### Connectivity Checks
```bash
[ ] Test Databricks connection
    [ ] databricks workspace list

[ ] Test cluster status
    [ ] databricks clusters get --cluster-id $CLUSTER_ID
    # State should be: RUNNING or PENDING

[ ] Test GitHub Actions
    [ ] GitHub → Actions → Workflows all green
```

### Data Quality Checks
```bash
[ ] Query bronze layer:
    [ ] In Databricks Notebook:
    SELECT COUNT(*) as row_count FROM bronze_raw
    [ ] Should show: >100000 (or expected row count)

[ ] Query silver layer:
    [ ] SELECT COUNT(*) as row_count FROM silver_processed
    [ ] Should show: processed data

[ ] Query gold layer:
    [ ] SELECT COUNT(*) as row_count FROM gold_analytics
    [ ] Should show: analytics ready data
```

### Airflow Health Checks
```bash
[ ] Check DAG runs completed
    [ ] airflow dags list-runs creditcard_fraud_etl_pipeline
    [ ] Should show successful runs

[ ] Check monitoring DAG
    [ ] airflow dags list-runs etl_pipeline_monitoring
    [ ] Should show execution history

[ ] Review logs (no errors)
    [ ] tail -100 ~/airflow/logs/dag_id/*.log
    [ ] Should not contain ERROR level logs
```

### Schedule Verification
```bash
[ ] Dev schedule (daily 02:00 UTC):
    [ ] Cron: 0 2 * * *

[ ] Prod schedule (daily 02:00 UTC):
    [ ] Cron: 0 2 * * *

[ ] Monitoring schedule (every 6 hours):
    [ ] Cron: 0 */6 * * *
```

**Estimated time**: 10 minutes  
**Success indicators**:
- ✓ All connections working
- ✓ Data present in all layers
- ✓ DAGs running successfully
- ✓ No error logs

---

## Phase 9: Maintenance & Monitoring (Ongoing)

### Daily Tasks
```bash
[ ] Check Databricks Jobs → Recent Runs (all succeeded)
[ ] Check Airflow Webserver UI (all DAGs green)
[ ] Check for data quality alerts (none expected)
[ ] Review logs for warnings (if any)
```

### Weekly Tasks
```bash
[ ] Review job execution times (any slower?)
[ ] Check data volumes (growing as expected?)
[ ] Verify backup completion
[ ] Check for any failed tasks in last 7 days
```

### Monthly Tasks
```bash
[ ] Review and optimize job configurations
[ ] Update documentation if needed
[ ] Check token expiration (regenerate if <30 days)
[ ] Review cluster usage (resize if needed)
[ ] Backup all configurations
```

### Alerts to Monitor
```bash
Job Failures:
[ ] Email notifications from Databricks (on_failure)
[ ] Slack alerts from GitHub Actions
[ ] Airflow task failure alerts

Data Quality:
[ ] Row count drops unexpectedly → Check source
[ ] Schema changes → Update bronze schema
[ ] Null values spike → Investigate source data
```

---

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Jobs not running | See TROUBLESHOOTING.md → "Job Execution Issues" |
| Connection failed | See TROUBLESHOOTING.md → "Connection Issues" |
| DAG not appearing | See TROUBLESHOOTING.md → "Airflow DAG Issues" |
| Workflow stuck | See TROUBLESHOOTING.md → "GitHub Actions Issues" |
| Data quality drop | See TROUBLESHOOTING.md → "Data Quality Issues" |

---

## Timeline Summary

| Phase | Task | Estimated Time | Cumulative |
|-------|------|-----------------|-----------|
| 1 | Prerequisites | 10 min | 10 min |
| 2 | Local Setup | 15 min | 25 min |
| 3 | Bundle Validation | 10 min | 35 min |
| 4 | Deploy to Dev | 15 min | 50 min |
| 5 | GitHub Actions | 20 min | 70 min |
| 6 | Airflow Setup | 30 min | 100 min |
| 7 | Production Deploy | 15 min | 115 min |
| 8 | Final Verification | 10 min | **125 min** |

**Total: ~2 hours for complete setup**

---

## Sign-Off Checklist

When all phases complete, verify:

```bash
✅ All 8 phases completed
✅ Dev environment fully operational
✅ Production environment deployed
✅ Airflow DAGs running
✅ GitHub Actions workflows green
✅ Data flowing through all layers
✅ Monitoring/alerts configured
✅ Team trained on operations
✅ Documentation updated
✅ Backup procedures tested
```

**Congratulations! Your ETL pipeline is now production-ready!** 🎉

---

**Questions?** Refer to:
- SETUP_GUIDE.md - Detailed setup instructions
- COMMANDS_REFERENCE.md - CLI commands
- TROUBLESHOOTING.md - Common issues & fixes

