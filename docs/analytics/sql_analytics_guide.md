# SQL Analytics Guide

Welcome to the SQL Analytics Guide for the Enterprise Banking Risk & Customer Intelligence Platform.

## Overview
This guide provides standards, best practices, and guidelines for writing SQL queries within the platform. Our goal is to ensure consistency, performance, and readability across all analytical queries.

## Formatting Standards
- **Keywords**: Always use UPPERCASE for SQL keywords (e.g., `SELECT`, `FROM`, `WHERE`, `JOIN`).
- **Identifiers**: Use lowercase with underscores (`snake_case`) for table names, column names, and aliases.
- **Indentation**: Use 4 spaces for indentation.
- **Comments**: Use `--` for single-line comments and `/* ... */` for block comments. Document complex logic, business rules, and CTEs.

## Common Table Expressions (CTEs)
We strongly prefer CTEs (`WITH` clauses) over subqueries in the `FROM` or `WHERE` clauses for better readability.
- Name CTEs descriptively.
- Build complex queries step-by-step using sequential CTEs.

## Joins
- Always use explicit `JOIN` syntax (`INNER JOIN`, `LEFT JOIN`, etc.) instead of implicit joins in the `WHERE` clause.
- Ensure join conditions are indexed where applicable.

## Dates and Timestamps
- Use standardized date formats (ISO 8601) when filtering.
- Be mindful of timezones when aggregating temporal data.

## Code Reviews
All new SQL scripts must be peer-reviewed for:
1. Accuracy of business logic.
2. Adherence to formatting standards.
3. Performance and efficiency.
