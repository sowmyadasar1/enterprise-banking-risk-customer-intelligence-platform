"""
ETL Data Quality Framework — Automated quality checks and reporting for all layers.
Generates DQ scores, row count comparisons, null analysis, and anomaly detection.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path
import json

@dataclass
class DQCheck:
    check_name: str
    dataset: str
    layer: str
    status: str
    value: Any
    threshold: Any
    message: str

class BaseQualityChecker:
    pass

class DataQualityChecker(BaseQualityChecker):
    def check_row_counts(self, raw_df: pd.DataFrame, bronze_df: pd.DataFrame, silver_df: pd.DataFrame, gold_df: pd.DataFrame, dataset_name: str) -> List[DQCheck]:
        checks = []
        raw_count = len(raw_df) if raw_df is not None else 0
        bronze_count = len(bronze_df) if bronze_df is not None else 0
        silver_count = len(silver_df) if silver_df is not None else 0
        gold_count = len(gold_df) if gold_df is not None else 0
        
        if raw_count > 0:
            b_ratio = bronze_count / raw_count
            status = 'PASS' if b_ratio >= 0.95 else 'WARN'
            checks.append(DQCheck('row_count_bronze', dataset_name, 'bronze', status, b_ratio, 0.95, f"Bronze vs Raw row count ratio: {b_ratio:.2f}"))
        
        if bronze_count > 0:
            s_ratio = silver_count / bronze_count
            status = 'PASS' if s_ratio >= 0.90 else 'WARN'
            checks.append(DQCheck('row_count_silver', dataset_name, 'silver', status, s_ratio, 0.90, f"Silver vs Bronze row count ratio: {s_ratio:.2f}"))

        if silver_count > 0:
            g_ratio = gold_count / silver_count
            status = 'PASS' if g_ratio >= 0.80 else 'WARN'
            checks.append(DQCheck('row_count_gold', dataset_name, 'gold', status, g_ratio, 0.80, f"Gold vs Silver row count ratio: {g_ratio:.2f}"))
        return checks

    def check_null_rates(self, df: pd.DataFrame, dataset_name: str, layer: str, threshold: float = 0.30) -> List[DQCheck]:
        checks = []
        if df is None or df.empty:
            return checks
        
        total_rows = len(df)
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_rate = float(null_count / total_rows)
            if null_rate > threshold:
                status = 'FAIL' if null_rate > 0.8 else 'WARN'
                checks.append(DQCheck(f'null_rate_{col}', dataset_name, layer, status, null_rate, threshold, f"Null rate for {col} is {null_rate:.2f}"))
            else:
                checks.append(DQCheck(f'null_rate_{col}', dataset_name, layer, 'PASS', null_rate, threshold, f"Null rate for {col} is {null_rate:.2f}"))
        return checks

    def check_pk_uniqueness(self, df: pd.DataFrame, pk_col: str, dataset_name: str, layer: str) -> DQCheck:
        if df is None or df.empty or pk_col not in df.columns:
            return DQCheck('pk_uniqueness', dataset_name, layer, 'WARN', 0, 1.0, f"PK {pk_col} not found or DF empty")
        is_unique = bool(df[pk_col].is_unique)
        return DQCheck('pk_uniqueness', dataset_name, layer, 'PASS' if is_unique else 'FAIL', is_unique, True, f"PK {pk_col} uniqueness: {is_unique}")

    def check_duplicate_rate(self, df: pd.DataFrame, pk_col: str, dataset_name: str, layer: str) -> DQCheck:
        if df is None or df.empty or pk_col not in df.columns:
            return DQCheck('duplicate_rate', dataset_name, layer, 'WARN', 0, 0, f"PK {pk_col} not found or DF empty")
        dupe_count = int(df.duplicated(subset=[pk_col]).sum())
        dupe_rate = float(dupe_count / len(df))
        status = 'PASS' if dupe_rate == 0 else ('WARN' if dupe_rate < 0.05 else 'FAIL')
        return DQCheck('duplicate_rate', dataset_name, layer, status, dupe_rate, 0, f"Duplicate rate on {pk_col}: {dupe_rate:.4f}")

    def check_referential_integrity(self, child_df: pd.DataFrame, fk_col: str, parent_df: pd.DataFrame, pk_col: str, dataset_name: str, layer: str) -> DQCheck:
        if child_df is None or parent_df is None or fk_col not in child_df.columns or pk_col not in parent_df.columns:
            return DQCheck('referential_integrity', dataset_name, layer, 'WARN', 0, 1.0, "Missing data or columns for RI check")
        
        valid_fks = child_df[fk_col].dropna()
        if len(valid_fks) == 0:
            return DQCheck('referential_integrity', dataset_name, layer, 'PASS', 1.0, 1.0, "No non-null foreign keys to check")
            
        match_count = int(valid_fks.isin(parent_df[pk_col]).sum())
        match_rate = float(match_count / len(valid_fks))
        status = 'PASS' if match_rate == 1.0 else ('WARN' if match_rate >= 0.99 else 'FAIL')
        return DQCheck('referential_integrity', dataset_name, layer, status, match_rate, 1.0, f"RI {fk_col}->{pk_col} match rate: {match_rate:.4f}")

    def check_value_ranges(self, df: pd.DataFrame, dataset_name: str, layer: str) -> List[DQCheck]:
        checks = []
        if df is None or df.empty:
            return checks
        amount_cols = [c for c in df.columns if 'amount' in str(c).lower()]
        for c in amount_cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                invalid_pct = float((df[c] <= 0).mean())
                status = 'PASS' if invalid_pct == 0 else 'WARN'
                checks.append(DQCheck(f'value_range_gt_0_{c}', dataset_name, layer, status, invalid_pct, 0.0, f"{invalid_pct:.2%} of {c} <= 0"))
        
        score_cols = [c for c in df.columns if 'credit_score' in str(c).lower()]
        for c in score_cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                invalid_pct = float((~df[c].between(300, 850)).mean())
                status = 'PASS' if invalid_pct == 0 else 'WARN'
                checks.append(DQCheck(f'value_range_credit_score_{c}', dataset_name, layer, status, invalid_pct, 0.0, f"{invalid_pct:.2%} of {c} outside 300-850"))
        
        age_cols = [c for c in df.columns if 'age' in str(c).lower() and 'page' not in str(c).lower()]
        for c in age_cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                invalid_pct = float((~df[c].between(18, 100)).mean())
                status = 'PASS' if invalid_pct == 0 else 'WARN'
                checks.append(DQCheck(f'value_range_age_{c}', dataset_name, layer, status, invalid_pct, 0.0, f"{invalid_pct:.2%} of {c} outside 18-100"))
        return checks

    def run_all_checks(self, datasets_by_layer: dict, all_datasets: dict) -> List[DQCheck]:
        all_checks = []
        for dataset in all_datasets:
            raw_df = datasets_by_layer.get('raw', {}).get(dataset)
            bronze_df = datasets_by_layer.get('bronze', {}).get(dataset)
            silver_df = datasets_by_layer.get('silver', {}).get(dataset)
            gold_df = datasets_by_layer.get('gold', {}).get(dataset)
            
            all_checks.extend(self.check_row_counts(raw_df, bronze_df, silver_df, gold_df, dataset))
            
            for layer, df in [('bronze', bronze_df), ('silver', silver_df), ('gold', gold_df)]:
                if df is not None:
                    all_checks.extend(self.check_null_rates(df, dataset, layer))
                    if len(df.columns) > 0:
                        pk_col = df.columns[0]
                        all_checks.append(self.check_pk_uniqueness(df, pk_col, dataset, layer))
                        all_checks.append(self.check_duplicate_rate(df, pk_col, dataset, layer))
                    all_checks.extend(self.check_value_ranges(df, dataset, layer))
        return all_checks

    def generate_report(self, checks: List[DQCheck], output_path: Path) -> dict:
        total = len(checks)
        passed = sum(1 for c in checks if c.status == 'PASS')
        warned = sum(1 for c in checks if c.status == 'WARN')
        failed = sum(1 for c in checks if c.status == 'FAIL')
        score = (passed / total * 100) if total > 0 else 0
        
        report_summary = {
            "total_checks": total,
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "overall_score": score
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path.with_suffix('.json'), 'w') as f:
            json.dump([c.__dict__ for c in checks], f, indent=2)
            
        with open(output_path.with_suffix('.md'), 'w') as f:
            f.write(f"# Data Quality Report\n\n")
            f.write(f"**Overall Score:** {score:.2f}%\n\n")
            f.write(f"- Total Checks: {total}\n")
            f.write(f"- Passed: {passed}\n")
            f.write(f"- Warned: {warned}\n")
            f.write(f"- Failed: {failed}\n\n")
            f.write("## Failed Checks\n")
            for c in checks:
                if c.status == 'FAIL':
                    f.write(f"- **{c.dataset} ({c.layer})** - {c.check_name}: {c.message}\n")
                    
        return report_summary
