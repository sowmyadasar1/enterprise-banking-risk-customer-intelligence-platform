# Optimization Notes

This document outlines key considerations for optimizing analytical queries and database performance.

## Indexing Strategy
- **Primary Keys**: Ensure all dimension and fact tables have appropriate Primary Keys.
- **Foreign Keys**: Index foreign keys used frequently in `JOIN` conditions.
- **Covering Indexes**: Use covering indexes for queries that frequently access a specific subset of columns.
- **Filtered Indexes**: Consider filtered (partial) indexes for large tables where queries frequently filter on a specific boolean or low-cardinality status flag (e.g., `is_active = TRUE`).

## Explain Plans
- Always use `EXPLAIN` (or `EXPLAIN QUERY PLAN` in SQLite) before executing complex queries on large datasets.
- Look out for:
  - **Sequential / Table Scans**: Indicates a missing index if filtering on a large table.
  - **Nested Loops**: Can be inefficient for large datasets; hash joins or merge joins are often preferred.
  - **Temporary Files / Sorts**: Occurs during heavy aggregations or `ORDER BY` without indexes. May require increasing working memory.

## CTEs vs Temp Tables
### Common Table Expressions (CTEs)
- **Pros**: Cleaner code, easier to read, doesn't require explicit cleanup.
- **Cons**: In some engines (like older PostgreSQL versions), CTEs act as optimization fences and are materialized, which can hurt performance if they are large and not reused. (Note: PG 12+ optimizes inline CTEs better).

### Temporary Tables
- **Pros**: Can be indexed. Useful if the intermediate dataset is very large and needs to be joined multiple times in subsequent steps.
- **Cons**: Requires explicit `CREATE TEMP TABLE` and `DROP`, harder to read as a single query flow, adds I/O overhead.
- **Recommendation**: Default to CTEs. Switch to Temp Tables with indexes only if a specific query is experiencing severe performance bottlenecks due to massive intermediate result sets.

## PostgreSQL vs SQLite Performance Considerations
- **Concurrency**: SQLite locks the entire database for writes, while PostgreSQL handles high concurrency beautifully with MVCC.
- **Analytics Functions**: PostgreSQL supports advanced window functions, `ROLLUP`, `CUBE`, and `FILTER` clauses which drastically simplify analytical queries. SQLite has added window function support but lacks some advanced grouping features.
- **Joins**: PostgreSQL has sophisticated Hash and Merge join algorithms. SQLite primarily relies on Nested Loop joins, making indexing absolutely critical for joins in SQLite.
- **Data Types**: PostgreSQL is strictly typed and enforces it. SQLite uses dynamic typing. Be careful with date/time manipulations, as SQLite treats them as strings or numbers, while PostgreSQL has dedicated temporal types.
