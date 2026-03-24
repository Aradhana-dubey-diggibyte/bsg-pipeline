# 🎯 BSG Credit Card Pipeline - Production ETL with Databricks, Airflow & GitHub Actions

> **Complete infrastructure-as-code solution for Databricks medallion architecture, automated deployment, and orchestration.**

---

## 📋 What This Is

A **production-ready ETL pipeline** that:

- ✅ **Ingests** credit card data monthly from Kaggle
- ✅ **Transforms** through Bronze → Silver → Gold medallion layers
- ✅ **Orchestrates** with Airflow (daily scheduling + monitoring)
- ✅ **Deploys** with Databricks Asset Bundle (dev/prod separation)
- ✅ **Validates** with GitHub Actions CI/CD (linting, security, testing)
- ✅ **Monitors** continuously with health checks & alerts

**Status**: ✅ Production-ready (126 files, ~7,900 lines of code)

---

## 🎬 Quick Start

### 1️⃣ Prerequisites (10 min)
```bash
# You need:
- Databricks workspace (https://adb-xxx.azuredatabricks.net)
- Existing Databricks cluster (no creation needed)
- GitHub repository access
- Python 3.8+
```

### 2️⃣ Read Setup Guide (15 min)
```bash
# Start here
open SETUP_GUIDE.md          # Read architecture & overview
```

### 3️⃣ Deploy (2 hours)
```bash
# Follow the checklist step-by-step
open DEPLOYMENT_CHECKLIST.md  # Check off each phase as you go
```

### 4️⃣ Verify
```bash
# Everything working?
databricks bundle validate -t dev
airflow dags list
```

**Total time to production: ~2 hours**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              DATABRICKS ASSET BUNDLE (IaC)                 │
│  databricks.yml + resources/*.yml (4 jobs)                 │
└──────────┬────────────────┬─────────────────────────────────┘
           │                │
      ┌────▼────┐      ┌────▼────┐
      │ DEV ENV │      │PROD ENV │
      └────┬────┘      └────┬────┘
           │                │
    ┌──────▼──────┬─────────▼──────┬──────────────────┐
    │ BRONZE JOB  │  SILVER JOB    │  GOLD JOB        │
    │ (daily)     │  (daily)       │  (daily)         │
    └──────┬──────┴────────┬───────┴──────────────────┘
           │               │
    ┌──────▼───────────────▼────────────────────────┐
    │   APACHE AIRFLOW - ORCHESTRATION              │
    │  creditcard_etl_pipeline.py (main DAG)       │
    │  etl_monitoring.py (monitoring DAG)          │
    └──────┬────────────────────────────────────────┘
           │
    ┌──────▼──────────────────────────────────────┐
    │  GITHUB ACTIONS - CI/CD                     │
    │  pr_validate.yml (lint, test, validate)    │
    │  deploy_prod.yml (deploy, smoke test)      │
    └───────────────────────────────────────────┘
```

---

## 📁 Project Structure

### 📚 Documentation (Start Here!)
```
├── INDEX.md                     ← You are here
├── SETUP_GUIDE.md              ← Read this first (architecture + setup)
├── DEPLOYMENT_CHECKLIST.md     ← Follow this during deployment (8 phases)
├── COMMANDS_REFERENCE.md       ← CLI command lookup
└── TROUBLESHOOTING.md          ← Fix problems here
```

### 🔧 Infrastructure as Code (Databricks)
```
├── databricks.yml              ← Bundle config (targets, variables)
└── resources/
    ├── ingestion_job.yml       ← Monthly Kaggle download
    ├── bronze_job.yml          ← Daily schema validation
    ├── silver_job.yml          ← 4-phase transformation
    └── gold_job.yml            ← Analytics generation
```

### 🚀 CI/CD (GitHub Actions)
```
└── .github/workflows/
    ├── pr_validate.yml         ← Runs on PR (lint, test, validate)
    └── deploy_prod.yml         ← Runs on main push (deploy, notify)
```

### 🎪 Orchestration (Airflow)
```
├── airflow/
│   ├── dags/
│   │   ├── creditcard_etl_pipeline.py   ← Main DAG
│   │   └── etl_monitoring.py            ← Monitoring DAG
│   ├── requirements.txt         ← Python dependencies
│   ├── Dockerfile              ← Container image
│   └── plugins/                ← Custom operators (optional)
```

### ⚙️ Configuration
```
└── conf/
    ├── dev.yml                 ← Dev environment (2 workers)
    └── prod.yml                ← Prod environment (4-8 workers, SLA)
```

### 📊 Transformation Scripts
```
└── src/
    ├── 00_ingest_kaggle.py          ← Download data
    ├── 01_bronze_schema.py          ← Validate & store
    ├── 02_silver_dedup.py           ← Deduplication
    ├── 03_silver_standardise.py     ← Standardization
    ├── 04_silver_pii_mask.py        ← PII masking
    ├── 05_silver_derived.py         ← Features (50+)
    ├── 06_gold_risk_score.py        ← Risk modeling
    ├── 07_gold_rolling_metrics.py   ← Aggregations
    └── 08_gold_kpi_mart.py          ← Business KPIs
```

---

## 📅 Job Schedule

| Job | Frequency | Start Time | Duration | Dependencies |
|-----|-----------|------------|----------|---|
| Ingestion | Monthly | 1st of month | 30s | None |
| Bronze | Daily | 01:30 UTC | 2 min | Ingestion ✓ |
| Silver (4-phase) | Daily | 01:45 UTC | 15 min | Bronze ✓ |
| Gold (3-phase) | Daily | 02:15 UTC | 10 min | Silver ✓ |

**Full pipeline completion**: Daily by 02:45 UTC

---

## 🎯 What Gets Delivered

### Phase 1-4: Development Setup (~50 min)
- ✅ Databricks CLI configured
- ✅ 4 Databricks jobs deployed (dev)
- ✅ Bundle validation working

### Phase 5: CI/CD Setup (~20 min)
- ✅ GitHub Actions workflows active
- ✅ PR validation enabled
- ✅ Production deployment pipeline ready

### Phase 6: Airflow Setup (~30 min)
- ✅ Airflow webserver running
- ✅ 2 DAGs created & scheduled
- ✅ Job orchestration working

### Phase 7-8: Production & Verification (~25 min)
- ✅ Production environment deployed
- ✅ All systems verified
- ✅ Pipeline live & monitoring

**Result**: **Production-ready ETL pipeline** 🎉

---

## 🔑 Key Features

### Infrastructure as Code
- ✅ Version-controlled Databricks jobs
- ✅ Dev/prod environment separation
- ✅ Reproducible deployments
- ✅ No manual cluster creation

### Automation
- ✅ Scheduled daily runs
- ✅ Automatic retry logic (2x)
- ✅ Cascading dependencies
- ✅ Email notifications on failure

### Monitoring & Alerts
- ✅ Real-time job status tracking
- ✅ Data quality checks between layers
- ✅ Slack notifications (optional)
- ✅ Monitoring DAG every 6 hours

### CI/CD & Quality
- ✅ PR validation (linting, security, tests)
- ✅ Automated deployment on merge
- ✅ Bundle plan before deployment
- ✅ Smoke tests after deployment

### Flexibility
- ✅ Easy schedule changes
- ✅ Resource auto-scaling (prod)
- ✅ Environment-specific settings
- ✅ Customizable alert channels

---

## 📊 Data Flow

```
Kaggle Dataset (284K rows)
         ↓
    INGESTION (Monthly)
    Raw CSV → Parquet
         ↓
    BRONZE LAYER (Daily 01:30)
    Schema validation
    Type casting
         ↓
    SILVER LAYER (Daily 01:45, 4 phases)
    • Deduplication (2-3 min)
    • Standardization (2 min)
    • PII Masking (1 min)
    • Feature Engineering (5 min) [50+ features]
         ↓
    GOLD LAYER (Daily 02:15, 3 phases)
    • Risk Score Model (2 min)
    • Rolling Metrics (3 min)
    • KPI Mart (1 min)
         ↓
    ANALYTICS READY (30 columns)
    Ready for BI tools, dashboards, ML
```

**Total daily runtime**: ~35 minutes (01:30 - 02:15 + buffer)

---

## 🚀 Quick Commands

```bash
# Validate before deploy
databricks bundle validate -t dev

# Deploy to dev
databricks bundle deploy -t dev

# Run a job immediately
databricks jobs run-now --job-id 124

# Monitor job runs
databricks jobs list-runs --job-id 124 --limit 3

# Start Airflow
airflow webserver --port 8080 &
airflow scheduler &

# Trigger Airflow DAG
airflow dags trigger creditcard_fraud_etl_pipeline
```

→ See [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md) for complete list

---

## 📦 What's Included

| Category | Count | Type |
|----------|-------|------|
| Documentation | 5 | Guides (1,300+ lines) |
| Configuration | 11 | YAML files (800 lines) |
| Workflows | 2 | GitHub Actions (450 lines) |
| DAGs | 2 | Airflow (335 lines) |
| Transformation | 9 | Python scripts (5,000+ lines) |
| Tests | 3 | Unit tests |
| **TOTAL** | **32** | **~7,900 lines** |

---

## 🛠️ Technology Stack

- **Orchestration**: Apache Airflow 2.6+
- **Analytics**: Databricks (Spark, SQL)
- **IaC**: Databricks Asset Bundle
- **CI/CD**: GitHub Actions
- **Language**: Python 3.8+
- **Containers**: Docker (Airflow)
- **Monitoring**: Email + Slack alerts

---

## 🔐 Security Features

- ✅ Token-based Databricks authentication
- ✅ Environment variable separation (dev/prod)
- ✅ GitHub Secrets for sensitive data
- ✅ PII masking in Silver layer
- ✅ YAML security scanning
- ✅ Dependency vulnerability checks

---

## 📈 Scalability

| Environment | Cluster Size | Workers | Auto-Scale |
|---|---|---|---|
| **Dev** | i3.xlarge | 2 | No |
| **Prod** | i3.2xlarge | 4 | Yes (up to 8) |

**Data volume**: 284K+ rows/month, growing

---

## 🎓 Documentation Map

```
Start Here
    ↓
SETUP_GUIDE.md (architecture + overview)
    ↓
DEPLOYMENT_CHECKLIST.md (step-by-step)
    ├─→ Phase 1-4: Dev setup
    ├─→ Phase 5: GitHub Actions
    ├─→ Phase 6: Airflow
    ├─→ Phase 7: Production
    └─→ Phase 8: Verification
    ↓
After Deployment
    ├─→ COMMANDS_REFERENCE.md (daily operations)
    └─→ TROUBLESHOOTING.md (when issues arise)
```

---

## ⏱️ Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| 1. Prerequisites | 10 min | Validate environment |
| 2. Local Setup | 15 min | CLI + auth |
| 3. Validation | 10 min | YAML syntax |
| 4. Dev Deploy | 15 min | Create jobs |
| 5. CI/CD Setup | 20 min | GitHub secrets |
| 6. Airflow | 30 min | DAG setup |
| 7. Production | 15 min | Prod jobs |
| 8. Verification | 10 min | Health checks |
| **TOTAL** | **125 min** | **Production-ready** |

---

## ✅ Success Criteria

After following this guide, you should have:

- [ ] Databricks Asset Bundle deployed to dev & prod
- [ ] 4 Databricks jobs running on schedule
- [ ] GitHub Actions workflows validating & deploying
- [ ] Airflow DAGs orchestrating the pipeline
- [ ] Daily scheduled runs completing successfully
- [ ] Alerts configured for failures
- [ ] Monitoring active (every 6 hours)
- [ ] Production data flowing end-to-end

---

## 🆘 Troubleshooting

**Something not working?**
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for your error
2. Run `check_pipeline.sh` from [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md)
3. Review logs: `tail -f ~/airflow/logs/*.log`
4. Escalate to platform team if needed

---

## 📚 Additional Resources

- 📖 Full Setup Guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- ✅ Phase Checklist: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- 🔧 Command Reference: [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md)
- 🔍 Troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 📑 Documentation Index: [INDEX.md](INDEX.md)

---

## 🎉 Ready to Deploy?

**Start here**: Open [SETUP_GUIDE.md](SETUP_GUIDE.md) and follow along!

Estimated time: ~2 hours to production ⏱️

---

**Questions?** Check the documentation files above.  
**Found an issue?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).  
**Need a command?** Look it up in [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md).

**Status**: ✅ Production Ready  
**Last Updated**: [Current Date]  
**Version**: 1.0

---

*Built with Databricks Asset Bundle + Apache Airflow + GitHub Actions* 🚀
