import os
import sys
import sqlite3
import glob


def get_db_connection(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        print(f"[CRITICAL ERROR] Could not connect to database at {db_path}: {e}")
        return None


def validate_queries():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))

    db_path = os.path.join(project_root, "data", "warehouse", "enterprise_dw.db")
    sql_dir = os.path.join(project_root, "sql", "analytics")

    if not os.path.exists(db_path):
        print(
            f"[WARNING] Database not found at {db_path}. Creating a temporary in-memory DB for validation, but queries depending on specific schemas may fail."
        )
        db_path = ":memory:"

    if not os.path.exists(sql_dir):
        print(f"[ERROR] SQL directory not found at {sql_dir}")
        return False

    conn = get_db_connection(db_path)
    if not conn:
        return False

    sql_files = glob.glob(os.path.join(sql_dir, "**", "*.sql"), recursive=True)
    if not sql_files:
        print(f"[INFO] No .sql files found in {sql_dir}")
        conn.close()
        return True

    all_passed = True

    print(f"Validating {len(sql_files)} SQL files...")

    for sql_file in sorted(sql_files):
        filename = os.path.basename(sql_file)

        try:
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()

            cursor = conn.cursor()

            # Try executing as a single statement (for SELECTs with CTEs)
            try:
                cursor.execute(sql_content)
                if cursor.description is not None:
                    # It's a query that returns rows (like SELECT)
                    rows = cursor.fetchall()
                    print(f"[OK] {filename} - returned {len(rows)} rows")
                else:
                    # It's a DDL/DML statement that executed successfully
                    print(f"[OK] {filename} - executed successfully (no rows returned)")
            except (
                sqlite3.Warning,
                sqlite3.OperationalError,
                sqlite3.ProgrammingError,
            ) as e:
                # If it fails, it might be multiple statements. Try executescript.
                if "You can only execute one statement at a time" in str(
                    e
                ) or "incomplete input" in str(e):
                    try:
                        cursor.executescript(sql_content)
                        print(
                            f"[OK] {filename} - executed script with multiple statements successfully"
                        )
                    except Exception as e2:
                        print(f"[ERROR] {filename}: {str(e2)}")
                        all_passed = False
                else:
                    # It was a genuine error with the query logic
                    print(f"[ERROR] {filename}: {str(e)}")
                    all_passed = False

        except Exception as e:
            print(f"[ERROR] {filename}: Failed to read or process file - {str(e)}")
            all_passed = False

    conn.close()
    return all_passed


if __name__ == "__main__":
    success = validate_queries()
    sys.exit(0 if success else 1)
