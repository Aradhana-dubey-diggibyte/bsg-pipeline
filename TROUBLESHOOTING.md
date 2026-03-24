# 🔧 Troubleshooting Guide - Databricks Asset Bundle ETL Pipeline

## Connection Issues

### Issue: "Unable to connect to Databricks"
**Symptoms**: `requests.exceptions.ConnectionError: Connection refused`

**Solutions**:
```bash
# 1. Verify host URL format
echo $DATABRICKS_HOST
# Should be: https://adb-xxxx.azuredatabricks.net (note https://)

# 2. Check token validity
databricks workspace list
# If fails, token may be expired

# 3. Regenerate token
# Databricks UI → Settings → User Settings → Generate new Token

# 4. Verify network
ping adb-xxxx.azuredatabricks.net

# 5. Check firewall rules
curl -I https://adb-xxxx.azuredatabricks.net
# Should return 200 or 401 (not connection timeout)
```

---

### Issue: "Invalid Databricks token"
**Symptoms**: `401 Unauthorized` or `Invalid credentials`

**Solutions**:
```bash
# 1. List existing tokens
databricks tokens list

# 2. Generate new token
# Databricks UI → Settings → User Settings → Generate Token

# 3. Update environment variable
export DATABRICKS_TOKEN="dapi4_newtoken_xxx"

# 4. Verify new token
databricks workspace list
```

---

## Bundle Deployment Issues

### Issue: "databricks bundle validate fails"
**Symptoms**: `Error: validation failed`, `schema validation error`

**Solutions**:
```bash
# 1. Check YAML syntax
python -m yaml < resources/bronze_job.yml

# 2. Validate specific file
databricks bundle validate --dry-run -t dev

# 3. Check for missing variables
databricks bundle validate -t dev --json | jq '.errors'

# 4. Verify variable definitions
grep -r "cluster_id" databricks.yml

# Common errors:
# - Missing colons after keys
# - Incorrect indentation (YAML is space-sensitive)
# - Undefined variable references
```

**Example Fix**:
```yaml
# ❌ WRONG - Missing colon after "timeout_seconds"
tasks:
  - task_key: bronze
    timeout_seconds 1800

# ✅ CORRECT
tasks:
  - task_key: bronze
    timeout_seconds: 1800
```

---

### Issue: "Variables not substituted in bundle"
**Symptoms**: `${environment}` appears in job names instead of dev/prod

**Solutions**:
```bash
# 1. Check databricks.yml variables section
grep -A 10 "variables:" databricks.yml

# 2. Verify variable is defined
# Should have format: variable_name: "<default_value>"

# 3. Pass variable at deploy time
databricks bundle deploy -t dev --var environment=dev

# 4. Check target configuration
grep -A 5 "targets:" databricks.yml

# Target should reference variables:
# targets:
#   dev:
#     variables:
#       environment: "dev"
```

---

### Issue: "Job already exists" error during deploy
**Symptoms**: `Error: Job with name 'creditcard-dev-bronze' already exists`

**Solutions**:
```bash
# 1. Option A: Destroy and redeploy
databricks bundle destroy -t dev
databricks bundle deploy -t dev

# 2. Option B: Use different job name
# Edit resources/bronze_job.yml and change name to:
# - creditcard-dev-bronze-v2

# 3. Option C: Delete old job manually
databricks jobs list --output json | jq -r '.jobs[] | select(.name | contains("bronze")) | .job_id'
databricks jobs delete --job-id 124

# 4. Check bundle state
databricks workspace ls /Shared/.bundle/
```

---

## Cluster Issues

### Issue: "Cluster not found" or "Invalid cluster ID"
**Symptoms**: `ClusterNotFound: Cluster with id does not exist`

**Solutions**:
```bash
# 1. List available clusters
databricks clusters list

# 2. Find correct cluster ID
databricks clusters list --output json | jq '.clusters[] | {name, cluster_id, state}'

# 3. Copy exact cluster ID to environment
export CLUSTER_ID="0704-123456-xxxxx"

# 4. Verify cluster is running
databricks clusters get --cluster-id $CLUSTER_ID | jq '.state'
# Should be: RUNNING or PENDING

# 5. If not running, start cluster
databricks clusters start --cluster-id $CLUSTER_ID

# 6. Update databricks.yml with correct ID
# Look for: existing_cluster_id: "${cluster_id}"
```

---

### Issue: "Cluster policy violations"
**Symptoms**: `Error: Cluster does not comply with workspace policy`

**Solutions**:
```bash
# 1. Check workspace policies
databricks compute policies list --output json

# 2. Get policy details
databricks compute policies get --policy-id policy_123

# 3. Modify cluster to comply
# Edit resources/*.yml files to match policy requirements
# - Check node type (may need i3.xlarge → i3.2xlarge)
# - Check Spark version (may need specific version)
# - Check driver/worker configs

# 4. Contact workspace admin if policy too restrictive
```

---

## Job Execution Issues

### Issue: "Job fails immediately with error"
**Symptoms**: Job state is `FAILED`, no useful details

**Solutions**:
```bash
# 1. Get job details
databricks jobs get --job-id 124

# 2. Get last run info
databricks jobs list-runs --job-id 124 --limit 1

# 3. Get detailed run logs
databricks jobs get-run --run-id 456 | jq '.state_message'

# 4. Access logs from Databricks UI
# Jobs → bronze_job → Last run → View Logs

# 5. Check if file path is correct
# Verify: src/01_bronze_schema.py exists in workspace

# 6. Check Python syntax errors
python -m py_compile src/01_bronze_schema.py
```

**Common Job Failures**:
```python
# ❌ ERROR: Module not found
import src.utils  # Won't work in Databricks

# ✅ CORRECT: Use relative imports or Databricks utils
import utilities  # Separate job or notebook
```

---

### Issue: "Job timeout exceeded"
**Symptoms**: `Job execution timed out after XXX minutes`

**Solutions**:
```bash
# 1. Check current timeout setting
databricks jobs get --job-id 124 | jq '.settings.timeout_seconds'

# 2. Increase timeout (in resources/bronze_job.yml)
timeout_seconds: 1800  # 30 minutes

# 3. Redeploy
databricks bundle deploy -t dev

# 4. If job consistently times out, check:
# - Cluster resources (may need larger instance)
# - Data volume (bronze layer growing too large)
# - Query complexity (optimize transformations)

# 5. Monitor execution time
databricks jobs list-runs --job-id 124 --limit 10 | jq '.runs[] | {start_time, end_time, duration: ((.end_time - .start_time) / 1000)}'
```

---

### Issue: "Job dependency not satisfied"
**Symptoms**: `Failed to resolve job dependency`, job doesn't run

**Solutions**:
```bash
# 1. Check dependency configuration
databricks jobs get --job-id 125 | jq '.settings.tasks[0].depends_on'

# 2. Verify upstream job exists and has correct ID
databricks jobs list --output json | grep 'ingestion\|bronze\|silver'

# 3. If upstream job ID is wrong, update in resources/silver_job.yml:
depends_on:
  - job_key: "bronze_job"  # Must exist in bundle
    outcome: "SUCCEEDED"    # Case sensitive

# 4. Check job runs in sequence
JobStart[Ingestion] → JobEnd[Ingestion]
↓
JobStart[Bronze] → JobEnd[Bronze]
↓
JobStart[Silver]

# If Bronze fails, Silver won't start
```

---

## Airflow DAG Issues

### Issue: "DAG not appearing in Airflow UI"
**Symptoms**: DAG not shown in DAG list

**Solutions**:
```bash
# 1. Check DAG file location
ls -la airflow/dags/creditcard_etl_pipeline.py
# File must exist in airflow/dags/

# 2. Restart Airflow scheduler
# Kill existing scheduler process
pkill airflow

# Start fresh
airflow scheduler &
airflow webserver --port 8080 &

# 3. Verify DAG syntax
python -m py_compile airflow/dags/creditcard_etl_pipeline.py

# 4. Enable DAG manually
airflow dags unpause creditcard_fraud_etl_pipeline

# 5. Check Airflow logs
tail -f ~/airflow/logs/scheduler/latest

# 6. Verify AIRFLOW_HOME
echo $AIRFLOW_HOME
# Should be: /opt/airflow
```

---

### Issue: "DAG task fails with 'Variable not found'"
**Symptoms**: `KeyError: 'INGESTION_JOB_ID'` in DAG execution

**Solutions**:
```bash
# 1. List all Airflow variables
airflow variables list

# 2. Set missing variables
airflow variables set INGESTION_JOB_ID 123
airflow variables set BRONZE_JOB_ID 124
airflow variables set SILVER_JOB_ID 125
airflow variables set GOLD_JOB_ID 126

# 3. Verify variables set
airflow variables get BRONZE_JOB_ID

# 4. Or set via environment file (create airflow_variables.txt)
# INGESTION_JOB_ID=123
# BRONZE_JOB_ID=124
# ... then load via:
airflow variables import airflow_variables.txt

# 5. Set Databricks connection
airflow connections add databricks_default \
    --conn-type databricks \
    --conn-host https://adb-xxxx.azuredatabricks.net \
    --conn-password dapi4_xxx
```

---

### Issue: "Airflow can't connect to Databricks"
**Symptoms**: `Error: Unable to connect to Databricks`, `Unauthorized`

**Solutions**:
```bash
# 1. Verify Databricks connection exists
airflow connections list

# 2. Test connection
airflow connections test databricks_default

# 3. Get connection details
airflow connections get databricks_default

# 4. If missing, create connection
airflow connections add databricks_default \
    --conn-type databricks \
    --conn-host https://adb-xxxx.azuredatabricks.net \
    --conn-login token \
    --conn-password dapi4_xxxxx

# 5. In DAG code, verify correct variable name:
# conn = BaseHook.get_connection('databricks_default')
```

---

## GitHub Actions Issues

### Issue: "Workflow fails with 'Token invalid'"
**Symptoms**: GitHub Actions job shows: `401 Unauthorized`

**Solutions**:
```bash
# 1. Verify GitHub secrets are set
# Go to: GitHub → Settings → Secrets and variables → Actions

# Required secrets:
# - DATABRICKS_HOST
# - DATABRICKS_TOKEN
# - SLACK_WEBHOOK (optional)

# 2. Check secret format
# Each secret should be:
# Name: DATABRICKS_HOST
# Value: https://adb-xxxx.azuredatabricks.net

# 3. Verify no extra spaces
# ❌ WRONG: " dapi4_xxx " (spaces)
# ✅ CORRECT: "dapi4_xxx" (no spaces)

# 4. Regenerate Databricks token if old
# Databricks UI → Settings → Generate new token

# 5. Re-add to GitHub secrets with new token
```

---

### Issue: "Workflow stuck in 'Pending'"
**Symptoms**: Workflow shows 'pending' for 30+ minutes

**Solutions**:
```bash
# 1. Check GitHub Actions quota
# GitHub → Settings → Actions → Usage

# 2. Check for concurrent job limit
# Default is 20 parallel jobs, may need increase for org

# 3. Kill stuck workflow
# GitHub → Actions → Select workflow → Cancel workflow run

# 4. Check runner availability
# Settings → Runners → Verify runner is online

# 5. Try manual trigger
# Actions → Workflow → Run Workflow

# 6. Check for blocking PR reviews
# If workflow requires approval, approve first
```

---

### Issue: "deploy_prod.yml never runs"
**Symptoms**: Workflow created but never triggers on main push

**Solutions**:
```bash
# 1. Check workflow file is correct location
# File must be: .github/workflows/deploy_prod.yml

# 2. Verify trigger condition
# Deploy should trigger on: push to main branch

# In deploy_prod.yml, check:
on:
  push:
    branches: [main]

# 3. Force trigger manually
# GitHub → Actions → Deploy to Production → Run Workflow

# 4. Check if PR protection rules block workflow
# Settings → Branches → Branch protection rules
# Ensure workflow is allowed to run

# 5. Check push was to main (not other branch)
git branch
# Should show: * main
```

---

## Data Quality Issues

### Issue: "Data quality check fails in Airflow DAG"
**Symptoms**: `bronze_quality_check` fails, pipeline stops

**Solutions**:
```bash
# 1. Check Databricks logs
# Jobs → bronze_job → Last Run → View Logs

# 2. Verify data exists
# In Databricks SQL:
SELECT COUNT(*) FROM bronze_raw WHERE month = current_month()

# 3. Check schema expectations
# Query: descriptive statistics on bronze layer
SELECT COUNT(*) total, COUNT(DISTINCT class) unique_classes FROM bronze_raw

# 4. In airflow DAG, check quality thresholds:
# airflow/dags/creditcard_etl_pipeline.py
# Look for: check_bronze_quality()

# 5. Adjust thresholds if needed
# MIN_ROWS_EXPECTED = 10000  # Adjust if data smaller
```

---

## Performance Issues

### Issue: "Pipeline takes longer than usual"
**Symptoms**: Jobs run successfully but take 2x normal time

**Solutions**:
```bash
# 1. Check cluster status
databricks clusters get --cluster-id $CLUSTER_ID

# 2. See if cluster is scaled up
# Look for: num_workers, current_num_workers

# 3. Monitor cluster metrics (Databricks UI)
# Clusters → Select cluster → Metrics

# 4. Check for data skew
# Verify: No single partition has 80%+ of data

# 5. Optimize PySpark code
# - Use caching for repeated reads
# - Partition before joins
# - Use bucketing for large tables

# 6. Increase cluster CPUs if consistently slow
# Edit resources/*.yml:
num_workers: 4  # from 2
node_type_id: "i3.2xlarge"  # larger instance
```

---

## Cleanup & Recovery

### Issue: "Want to start fresh"
**Solutions**:
```bash
# 1. Destroy all jobs (dev)
databricks bundle destroy -t dev

# 2. Clear workspace
databricks workspace delete /Workspace/Users/aradhan/bsg-pipeline-dev

# 3. Redeploy
databricks bundle deploy -t dev

# 4. Full restart (nuclear option)
# - Delete cluster
# - Recreate cluster  
# - Redeploy bundle
# - Restart Airflow
```

---

## Common Error Messages Reference

| Error | Meaning | Fix |
|-------|---------|-----|
| `ClusterNotFound` | Cluster ID invalid | Run `databricks clusters list`, copy correct ID |
| `RESOURCE_EXHAUSTED` | Cluster out of memory | Increase workers or node type |
| `INVALID_PARAMETER_VALUE` | Wrong field in job config | Check resources/*.yml syntax |
| `PERMISSION_DENIED` | Token lacks permissions | Check token has "admin" or "jobs" scope |
| `DEADLINE_EXCEEDED` | Job took too long | Increase timeout_seconds in resources/*.yml |
| `NOT_FOUND (404)` | Resource doesn't exist | Verify job/cluster ID is correct |
| `ALREADY_EXISTS` | Job with name already exists | Change job name or destroy existing |
| `INVALID_STATE` | Can't perform action in current state | Wait for job to complete before retry |

---

## Quick Diagnostics Checklist

```bash
# Run this to check system health:

echo "=== Connection ==="
databricks workspace list > /dev/null && echo "✓ Databricks OK" || echo "✗ Databricks FAILED"

echo "=== Cluster ==="
databricks clusters get --cluster-id $CLUSTER_ID > /dev/null && echo "✓ Cluster OK" || echo "✗ Cluster FAILED"

echo "=== Jobs ==="
databricks jobs list > /dev/null && echo "✓ Jobs OK" || echo "✗ Jobs FAILED"

echo "=== Bundle ==="
databricks bundle validate -t dev > /dev/null && echo "✓ Bundle OK" || echo "✗ Bundle FAILED"

echo "=== Airflow ==="
airflow dags list > /dev/null && echo "✓ Airflow OK" || echo "✗ Airflow FAILED"

echo "=== Variables ==="
[ ! -z "$DATABRICKS_HOST" ] && echo "✓ DATABRICKS_HOST set" || echo "✗ DATABRICKS_HOST missing"
[ ! -z "$DATABRICKS_TOKEN" ] && echo "✓ DATABRICKS_TOKEN set" || echo "✗ DATABRICKS_TOKEN missing"
[ ! -z "$CLUSTER_ID" ] && echo "✓ CLUSTER_ID set" || echo "✗ CLUSTER_ID missing"

echo "=== Diagnostics Complete ==="
```

---

**Need More Help?**
- Databricks Docs: https://docs.databricks.com
- Apache Airflow Docs: https://airflow.apache.org
- GitHub Actions: https://docs.github.com/en/actions
- Contact your workspace admin for access/permission issues

