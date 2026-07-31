"""
Enterprise Banking Risk & Customer Intelligence Platform
Phase 3 — ETL Pipeline Runner

Usage:
    python run_etl.py                          # Full pipeline, all 29 datasets
    python run_etl.py --datasets customers transactions loans
    python run_etl.py --quality-report         # Print DQ report from last run
    python run_etl.py --validate-only          # Extract + validate, no write
"""
import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(
        description="Enterprise Banking Risk & Customer Intelligence Platform — ETL Runner"
    )
    parser.add_argument(
        "--datasets", nargs="*", default=None,
        help="Specific dataset names to process. If omitted, all 29 are processed."
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Only extract and validate — do not write Bronze/Silver/Gold."
    )
    parser.add_argument(
        "--quality-report", action="store_true",
        help="Generate a data quality report from existing Gold data."
    )
    args = parser.parse_args()

    from src.etl.pipeline import ETLPipeline
    from src.etl.config import CONFIG

    pipeline = ETLPipeline(config=CONFIG)

    if args.validate_only:
        print("Running in VALIDATE-ONLY mode. No data will be written.")
        # Extract + validate only
        from src.etl.extract import DataExtractor
        from src.etl.validate import DatasetValidator
        extractor = DataExtractor(CONFIG)
        validator = DatasetValidator()
        all_raw = extractor.extract_all()
        errors = 0
        for name, df in all_raw.items():
            _, errs, warns = validator.validate(df, name, all_raw)
            if errs:
                print(f"  ✗ {name}: {len(errs)} errors")
                for e in errs:
                    print(f"      {e}")
                errors += 1
            else:
                print(f"  ✓ {name}: {len(df):,} rows validated")
        print(f"\nValidation complete. {len(all_raw)-errors}/{len(all_raw)} datasets passed.")
        sys.exit(0 if errors == 0 else 1)

    # Full pipeline
    t0 = time.time()
    print("\n" + "═"*60)
    print("  Enterprise Banking ETL Pipeline")
    print("═"*60)
    if args.datasets:
        print(f"  Mode: Selective — {args.datasets}")
    else:
        print("  Mode: Full — 29 datasets")
    print("═"*60 + "\n")

    summary = pipeline.run(datasets=args.datasets)

    elapsed = time.time() - t0
    print(f"\nTotal wall-clock time: {elapsed:.1f}s")

    if summary.get("datasets_failed", 0) > 0:
        print(f"\n⚠  {summary['datasets_failed']} datasets failed. Check logs for details.")
        sys.exit(1)

    print("\n✅ ETL Pipeline completed successfully.")
    print(f"   Bronze: {summary['total_bronze_rows']:,} rows")
    print(f"   Silver: {summary['total_silver_rows']:,} rows")
    print(f"   Gold:   {summary['total_gold_rows']:,} rows")
    sys.exit(0)


if __name__ == "__main__":
    main()
