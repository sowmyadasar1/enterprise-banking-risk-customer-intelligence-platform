"""
Enterprise Banking Data Warehouse Builder
Usage:
    python run_warehouse.py              # Build and load full warehouse
    python run_warehouse.py --stats      # Print table stats
    python run_warehouse.py --rebuild    # Drop and rebuild
"""

import argparse
from src.warehouse.warehouse_builder import WarehouseBuilder

def main():
    parser = argparse.ArgumentParser(description="Enterprise Banking Data Warehouse Builder")
    parser.add_argument('--stats', action='store_true', help="Print table stats")
    parser.add_argument('--rebuild', action='store_true', help="Drop and rebuild")
    
    args = parser.parse_args()
    
    builder = WarehouseBuilder()
    
    if args.rebuild:
        print("Rebuilding warehouse...")
        builder.rebuild()
    elif not args.stats:
        print("Building warehouse...")
        builder.build()
        
    if args.stats:
        with builder._get_conn() as conn:
            stats = builder.get_stats(conn)
            print("Table Statistics:")
            for table, count in stats.items():
                print(f"  {table}: {count} rows")

if __name__ == "__main__":
    main()
