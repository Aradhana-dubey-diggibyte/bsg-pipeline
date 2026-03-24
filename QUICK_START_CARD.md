# 🚀 QUICK START CARD - BSG Pipeline

**Print this or bookmark it!**

---

## ⏰ TIMELINE: 125 Minutes to Production

```
Phase 1 (10 min)  → Prerequisites
Phase 2 (15 min)  → Local Setup
Phase 3 (10 min)  → Bundle Validation
Phase 4 (15 min)  → Deploy Dev
Phase 5 (20 min)  → GitHub Actions
Phase 6 (30 min)  → Airflow Setup
Phase 7 (15 min)  → Deploy Prod
Phase 8 (10 min)  → Verification
────────────────────────────────
TOTAL:  125 min   ✅ Production Ready
```

---

## 📚 Documentation Quick Links

| Need | File | Read Time |
|------|------|-----------|
| **Architecture & Setup** | SETUP_GUIDE.md | 30 min |
| **Step-by-Step** | DEPLOYMENT_CHECKLIST.md | 120 min |
| **CLI Commands** | COMMANDS_REFERENCE.md | 5 min |
| **Fix Problems** | TROUBLESHOOTING.md | 10 min |
| **Overview** | README_DEPLOYMENT.md | 10 min |
| **Navigation** | INDEX.md | 5 min |

---

## 🔑 Essential Information (Save These!)

```
DATABRICKS_HOST = https://adb-xxxx.azuredatabricks.net
DATABRICKS_TOKEN = dapi4xxxxxxxxxxxxxxxxxxxxx
CLUSTER_ID = 0704-123456-xxxxx
GITHUB_REPO = owner/bsg-pipeline
```

---

## 🎯 Before You Start

- [ ] Databricks workspace ready
- [ ] Existing cluster available (get the ID)
- [ ] Personal Access Token generated
- [ ] GitHub repo cloned locally
- [ ] Python 3.8+ installed
- [ ] Have you read SETUP_GUIDE.md?

---

## 🚄 Fast Track Commands

```bash
# 1. Configure Databricks
databricks configure --token
# Input: workspace URL & token

# 2. Validate bundle
databricks bundle validate -t dev

# 3. Deploy to dev
databricks bundle deploy -t dev

# 4. Record job IDs (write them down!)
databricks jobs list --output json

# 5. Install Airflow
pip install -r airflow/requirements.txt

# 6. Start Airflow
airflow webserver --port 8080 &
airflow scheduler &

# 7. Trigger DAG
airflow dags trigger creditcard_fraud_etl_pipeline
```

---

## 📋 Deployment Checklist Quick Reference

```
Phase 1: Prerequisites
  [ ] Environment variables checked
  [ ] Databricks CLI installed

Phase 2: Local Setup
  [ ] CLI configured with token
  [ ] Connection verified

Phase 3: Validation
  [ ] bundle validate passes
  [ ] bundle plan succeeds

Phase 4: Dev Deploy
  [ ] Jobs deployed (4 jobs)
  [ ] Job IDs recorded

Phase 5: CI/CD
  [ ] GitHub secrets added (3 secrets)
  [ ] Workflows trigger on PR/push

Phase 6: Airflow
  [ ] Airflow webserver running
  [ ] Scheduler running
  [ ] DAGs visible
  [ ] Test run passed

Phase 7: Production
  [ ] Prod jobs deployed (4 jobs)
  [ ] Prod job IDs recorded

Phase 8: Verification
  [ ] All systems operational
  [ ] Data flowing end-to-end
  [ ] Monitoring active
```

---

## 🆘 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| "Connection refused" | Check DATABRICKS_HOST format |
| "Invalid token" | Regenerate token in Databricks UI |
| "Cluster not found" | Run `databricks clusters list`, copy exact ID |
| "Job already exists" | Change job name or delete old job |
| "DAG not found" | Restart Airflow scheduler |
| "Permission denied" | Check token has correct scopes |

**For more**: See TROUBLESHOOTING.md

---

## 📊 Job Schedule Reference

```
1st of Month at 00:00 → INGESTION (30 sec)
              ↓
Daily at 01:30       → BRONZE (2 min)
              ↓
Daily at 01:45       → SILVER (15 min, 4 phases)
              ↓
Daily at 02:15       → GOLD (10 min, 3 phases)
              ↓
Daily by 02:45       → Pipeline Complete ✅
```

---

## 🔧 Common Commands Cheat Sheet

```bash
# Databricks Bundle
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle destroy -t dev

# Databricks Jobs
databricks jobs list
databricks jobs get --job-id 124
databricks jobs run-now --job-id 124
databricks jobs list-runs --job-id 124

# Airflow
airflow webserver --port 8080
airflow scheduler
airflow dags list
airflow dags trigger creditcard_fraud_etl_pipeline
airflow variables list

# GitHub Actions
git push origin feature/xxx     # Triggers pr_validate.yml
git push origin main            # Triggers deploy_prod.yml
```

---

## ✅ Success Indicators (Each Phase)

**After Phase 2**:
```bash
$ databricks workspace list
[lists workspace directories] ✅
```

**After Phase 4**:
```bash
$ databricks jobs list
creditcard-dev-ingestion
creditcard-dev-bronze
creditcard-dev-silver
creditcard-dev-gold
```

**After Phase 6**:
```bash
$ airflow dags list
creditcard_fraud_etl_pipeline     RUNNING ✅
etl_pipeline_monitoring            RUNNING ✅
```

**After Phase 8**:
```bash
$ databricks jobs list-runs --job-id 124
[shows successful runs] ✅
```

---

## 🎓 Documentation Levels

```
BEGINNER
  └─ README_DEPLOYMENT.md (overview)
     └─ Start here for 10-min understanding

INTERMEDIATE
  └─ SETUP_GUIDE.md (architecture + setup)
     └─ Read this for implementation

ADVANCED
  ├─ DEPLOYMENT_CHECKLIST.md (step-by-step)
  ├─ COMMANDS_REFERENCE.md (deep dives)
  └─ TROUBLESHOOTING.md (edge cases)

EXPERT
  └─ Source files
     ├─ databricks.yml
     ├─ resources/*.yml
     ├─ airflow/dags/*.py
     └─ conf/*.yml
```

---

## 📞 Quick Help Matrix

| Question | Answer |
|----------|--------|
| How do I start? | Open SETUP_GUIDE.md |
| How do I deploy? | Follow DEPLOYMENT_CHECKLIST.md |
| What command do I run? | Search COMMANDS_REFERENCE.md |
| Something's broken! | Check TROUBLESHOOTING.md |
| Where's the file? | See INDEX.md |
| What was delivered? | See DELIVERY_SUMMARY.md |

---

## 🏆 Success Checklist (Final)

After everything is done, verify:

```
Infrastructure
  ✅ 4 dev jobs deployed & running
  ✅ 4 prod jobs deployed & running
  ✅ Using existing cluster (no new cluster)

CI/CD
  ✅ GitHub Actions workflows active
  ✅ PR validation working
  ✅ Production deployment working

Orchestration
  ✅ Airflow webserver running (http://localhost:8080)
  ✅ 2 DAGs created & enabled
  ✅ Manual DAG trigger working

Data Pipeline
  ✅ Data flowing daily
  ✅ All 4 layers healthy (bronze/silver/gold)
  ✅ Quality checks passing
  ✅ Monitoring active

Team
  ✅ Documentation accessible
  ✅ Team trained on operations
  ✅ Runbooks updated
  ✅ Alerts configured
```

---

## 🚀 Three Ways to Use This

### Option 1: Follow Step-by-Step (Recommended)
1. Read SETUP_GUIDE.md (30 min)
2. Follow DEPLOYMENT_CHECKLIST.md (120 min)
3. Reference COMMANDS_REFERENCE.md as needed

### Option 2: Quick Deploy
1. Skim SETUP_GUIDE.md Architecture section (5 min)
2. Copy commands from COMMANDS_REFERENCE.md (60 min)
3. Customize for your environment

### Option 3: Expert Mode
1. Review YAML files directly
2. Reference TROUBLESHOOTING.md only if needed
3. Deploy using bundle commands

---

## 💡 Pro Tips

- **Bookmark** this page for quick reference
- **Print** DEPLOYMENT_CHECKLIST.md and check off phases
- **Bookmark** COMMANDS_REFERENCE.md for daily operations
- **Keep note** of your job IDs (Phase 4 output)
- **Test** with `databricks jobs run-now` before production
- **Monitor** logs regularly: `tail -f ~/airflow/logs/*.log`

---

## ⏱️ Time Breakdown

```
Reading Documentation    : 30-45 min
Local Setup             : 25 min
Databricks Deployment   : 30 min
GitHub Actions Setup    : 20 min
Airflow Configuration   : 30 min
Final Verification      : 10 min
────────────────────────────────
TOTAL                   : 2-2.5 hours
```

---

## 🎯 End State

After completing all phases, you'll have:

✅ **Production-ready ETL pipeline**
✅ **Automated Databricks jobs** (dev & prod)
✅ **CI/CD with GitHub Actions**
✅ **Airflow orchestration**
✅ **Monitoring & alerts**
✅ **Complete documentation**
✅ **Team able to operate independently**

---

## 🔗 Quick Navigation

- Start → SETUP_GUIDE.md
- Deploy → DEPLOYMENT_CHECKLIST.md
- Operate → COMMANDS_REFERENCE.md
- Debug → TROUBLESHOOTING.md
- Overview → README_DEPLOYMENT.md
- Map → INDEX.md

---

**Everything you need is prepared and ready.**

**Next Step**: Open `SETUP_GUIDE.md` and begin! 🚀

---

*Quick Start Card v1.0*  
*Last Updated: [Current Date]*  
*Status: ✅ Production Ready*
