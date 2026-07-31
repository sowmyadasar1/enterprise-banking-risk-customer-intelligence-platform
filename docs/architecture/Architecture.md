# Enterprise System Architecture

The Enterprise Banking Risk & Customer Intelligence Platform is designed to ingest raw operational data and seamlessly transform it into actionable business intelligence and machine learning predictions. 

## High-Level Architecture Diagram

```mermaid
graph TD
    subgraph "Data Sources (Phase 2)"
        R1[Customers JSON]
        R2[Transactions CSV]
        R3[Loans Parquet]
    end

    subgraph "Data Engineering (Phases 3-4)"
        ETL[Medallion ETL Pipeline]
        DW[(Data Warehouse / Star Schema)]
        R1 & R2 & R3 --> ETL
        ETL --> DW
    end

    subgraph "Analytics & Features (Phases 5-6)"
        SQL[SQL Analytics Layer]
        FS[Feature Store]
        DW --> SQL
        DW --> FS
    end

    subgraph "Business Intelligence (Phase 8)"
        PBI[Power BI Dashboards]
        SQL --> PBI
    end

    subgraph "Machine Learning (Phase 7)"
        ML1[Fraud Detection XGBoost]
        ML2[Loan Default XGBoost]
        ML3[Customer Segments K-Means]
        ML4[Revenue Forecast ARIMA]
        FS --> ML1 & ML2 & ML3 & ML4
    end

    subgraph "MLOps & Serving (Phases 9-10)"
        REG[MLflow Model Registry]
        API[FastAPI Service]
        ML1 & ML2 & ML3 & ML4 -.-> REG
        REG --> API
    end

    %% Styles
    classDef source fill:#f9f,stroke:#333,stroke-width:2px;
    classDef data fill:#bbf,stroke:#333,stroke-width:2px;
    classDef ml fill:#bfb,stroke:#333,stroke-width:2px;
    classDef serve fill:#fbb,stroke:#333,stroke-width:2px;
    
    class R1,R2,R3 source;
    class ETL,DW,SQL,FS,PBI data;
    class ML1,ML2,ML3,ML4 ml;
    class REG,API serve;
```

## Technology Choices & Rationale

| Layer | Technology | Rationale for Portfolio / Production |
|-------|------------|--------------------------------------|
| **Data Processing** | `pandas`, custom ETL framework | Simulates PySpark distributed processing logic (Medallion architecture) in a local environment. |
| **Data Warehouse** | `SQLite` (Star Schema) | Provides a fully relational SQL backend that acts as a stand-in for Snowflake/Redshift without requiring cloud credentials. |
| **Machine Learning** | `scikit-learn`, `xgboost`, `statsmodels` | Industry standard for tabular data. XGBoost consistently outperforms deep learning for structured financial data. |
| **Model Tracking** | `MLflow` | The de facto open-source standard for experiment tracking and model registries. |
| **Model Serving** | `FastAPI`, `Pydantic` | Superior performance, async capabilities, and automatic OpenAPI documentation compared to Flask. |
| **Containerization**| `Docker`, `Docker Compose` | Ensures environment reproducibility and demonstrates deployment capabilities to DevOps teams. |

## Architectural Principles
1. **Separation of Concerns**: ETL, Feature Engineering, Model Training, and API Serving are completely decoupled. 
2. **Immutability**: The Data Warehouse is read-only for the ML and BI layers.
3. **Lazy Loading**: The FastAPI service defers model loading until the first request to minimize startup memory overhead.
