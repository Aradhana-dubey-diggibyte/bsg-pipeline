"""
Complete Pipeline Orchestrator
Orchestrates all transformation layers from Bronze → Silver → Gold
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Import all transformation modules
from src.ingest_kaggle import api, KaggleApi
from src._01_bronze_schema import create_bronze_layer
from src._02_silver_dedup import deduplicate_silver
from src._03_silver_standardise import standardize_silver
from src._04_silver_pii_mask import pii_mask_silver
from src._05_silver_derived import feature_engineering_silver
from src._06_gold_risk_score import gold_risk_scoring
from src._07_gold_rolling_metrics import rolling_metrics_gold
from src._08_gold_kpi_mart import kpi_mart_gold

class PipelineOrchestrator:
    """Manages the end-to-end credit card fraud detection pipeline"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.start_time = None
        self.stages_completed = []
        
    def log_stage(self, stage_name: str, status: str, duration: float = None):
        """Log stage completion"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {stage_name}: {status}"
        if duration:
            msg += f" ({duration:.2f}s)"
        print(f"\n{'='*80}")
        print(msg)
        print(f"{'='*80}\n")
        self.stages_completed.append((stage_name, status))
    
    def run_bronze_stage(self, csv_path: str = "data/raw/creditcard.csv") -> str:
        """Run Bronze layer transformation"""
        stage_start = time.time()
        self.log_stage("BRONZE LAYER", "Starting")
        
        try:
            output_path = create_bronze_layer(csv_path)
            duration = time.time() - stage_start
            self.log_stage("BRONZE LAYER", "✓ COMPLETED", duration)
            return output_path
        except Exception as e:
            self.log_stage("BRONZE LAYER", f"✗ FAILED: {str(e)}")
            raise
    
    def run_silver_dedup_stage(self, bronze_path: str) -> str:
        """Run Silver deduplication"""
        stage_start = time.time()
        self.log_stage("SILVER - DEDUPLICATION", "Starting")
        
        try:
            output_path = deduplicate_silver(bronze_path)
            duration = time.time() - stage_start
            self.log_stage("SILVER - DEDUPLICATION", "✓ COMPLETED", duration)
            return output_path
        except Exception as e:
            self.log_stage("SILVER - DEDUPLICATION", f"✗ FAILED: {str(e)}")
            raise
    
    def run_silver_standardize_stage(self, dedup_path: str) -> str:
        """Run Silver standardization"""
        stage_start = time.time()
        self.log_stage("SILVER - STANDARDIZATION", "Starting")
        
        try:
            output_path = standardize_silver(dedup_path)
            duration = time.time() - stage_start
            self.log_stage("SILVER - STANDARDIZATION", "✓ COMPLETED", duration)
            return output_path
        except Exception as e:
            self.log_stage("SILVER - STANDARDIZATION", f"✗ FAILED: {str(e)}")
            raise
    
    def run_silver_mask_stage(self, standardized_path: str) -> str:
        """Run Silver PII masking"""
        stage_start = time.time()
        self.log_stage("SILVER - PII MASKING", "Starting")
        
        try:
            output_path = pii_mask_silver(standardized_path)
            duration = time.time() - stage_start
            self.log_stage("SILVER - PII MASKING", "✓ COMPLETED", duration)
            return output_path
        except Exception as e:
            self.log_stage("SILVER - PII MASKING", f"✗ FAILED: {str(e)}")
            raise
    
    def run_silver_features_stage(self, masked_path: str) -> str:
        """Run Silver feature engineering"""
        stage_start = time.time()
        self.log_stage("SILVER - FEATURE ENGINEERING", "Starting")
        
        try:
            output_path = feature_engineering_silver(masked_path)
            duration = time.time() - stage_start
            self.log_stage("SILVER - FEATURE ENGINEERING", "✓ COMPLETED", duration)
            return output_path
        except Exception as e:
            self.log_stage("SILVER - FEATURE ENGINEERING", f"✗ FAILED: {str(e)}")
            raise
    
    def run_gold_risk_score_stage(self, silver_final_path: str) -> str:
        """Run Gold risk scoring"""
        stage_start = time.time()
        self.log_stage("GOLD - RISK SCORING", "Starting")
        
        try:
            output_path = gold_risk_scoring(silver_final_path)
            duration = time.time() - stage_start
            self.log_stage("GOLD - RISK SCORING", "✓ COMPLETED", duration)
            return output_path
        except Exception as e:
            self.log_stage("GOLD - RISK SCORING", f"✗ FAILED: {str(e)}")
            raise
    
    def run_gold_metrics_stage(self, risk_path: str) -> tuple:
        """Run Gold rolling metrics"""
        stage_start = time.time()
        self.log_stage("GOLD - ROLLING METRICS", "Starting")
        
        try:
            hourly_path, daily_path = rolling_metrics_gold(risk_path)
            duration = time.time() - stage_start
            self.log_stage("GOLD - ROLLING METRICS", "✓ COMPLETED", duration)
            return hourly_path, daily_path
        except Exception as e:
            self.log_stage("GOLD - ROLLING METRICS", f"✗ FAILED: {str(e)}")
            raise
    
    def run_gold_kpi_stage(self, risk_path: str) -> str:
        """Run Gold KPI Mart"""
        stage_start = time.time()
        self.log_stage("GOLD - KPI MART", "Starting")
        
        try:
            output_path = kpi_mart_gold(risk_path)
            duration = time.time() - stage_start
            self.log_stage("GOLD - KPI MART", "✓ COMPLETED", duration)
            return output_path
        except Exception as e:
            self.log_stage("GOLD - KPI MART", f"✗ FAILED: {str(e)}")
            raise
    
    def run_full_pipeline(self, csv_path: str = "data/raw/creditcard.csv"):
        """Execute complete pipeline"""
        print("\n" + "="*80)
        print("CREDITCARD FRAUD DETECTION - FULL PIPELINE EXECUTION")
        print("="*80)
        print(f"Start Time: {datetime.now()}")
        print(f"CSV Source: {csv_path}")
        
        self.start_time = time.time()
        
        try:
            # Bronze
            bronze_path = self.run_bronze_stage(csv_path)
            
            # Silver - Deduplication
            dedup_path = self.run_silver_dedup_stage(bronze_path)
            
            # Silver - Standardization
            standard_path = self.run_silver_standardize_stage(dedup_path)
            
            # Silver - PII Masking
            masked_path = self.run_silver_mask_stage(standard_path)
            
            # Silver - Features
            final_silver_path = self.run_silver_features_stage(masked_path)
            
            # Gold - Risk Scoring
            risk_path = self.run_gold_risk_score_stage(final_silver_path)
            
            # Gold - Metrics
            hourly_path, daily_path = self.run_gold_metrics_stage(risk_path)
            
            # Gold - KPI Mart
            kpi_path = self.run_gold_kpi_stage(risk_path)
            
            # Summary
            total_duration = time.time() - self.start_time
            self.print_summary(total_duration, kpi_path)
            
            return {
                "status": "SUCCESS",
                "duration_seconds": total_duration,
                "bronze_path": bronze_path,
                "silver_final_path": final_silver_path,
                "gold_risk_path": risk_path,
                "gold_metrics_hourly": hourly_path,
                "gold_metrics_daily": daily_path,
                "gold_kpi_mart": kpi_path,
            }
            
        except Exception as e:
            total_duration = time.time() - self.start_time
            print(f"\n{'='*80}")
            print(f"PIPELINE FAILED after {total_duration:.2f}s")
            print(f"Error: {str(e)}")
            print(f"{'='*80}\n")
            raise
    
    def print_summary(self, total_duration: float, kpi_path: str):
        """Print execution summary"""
        print(f"\n{'='*80}")
        print("PIPELINE EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
        print(f"\nStages Completed ({len(self.stages_completed)}):")
        for stage, status in self.stages_completed:
            print(f"  ✓ {stage}: {status}")
        print(f"\nFinal Output: {kpi_path}")
        print(f"End Time: {datetime.now()}")
        print(f"{'='*80}\n")

def main():
    """Main entry point"""
    
    # Configuration
    config = {
        "csv_path": "data/raw/creditcard.csv",
        "log_file": "pipeline_execution.log"
    }
    
    # Run orchestrator
    orchestrator = PipelineOrchestrator(config)
    
    try:
        result = orchestrator.run_full_pipeline(config["csv_path"])
        print(f"\n✓ PIPELINE SUCCESS")
        print(f"\nOutput Paths:")
        for key, value in result.items():
            if key != "status" and key != "duration_seconds":
                print(f"  {key}: {value}")
        return 0
    except Exception as e:
        print(f"\n✗ PIPELINE FAILED: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
