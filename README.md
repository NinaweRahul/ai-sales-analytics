#AI-Powered Sales Analytics System

##Overview
This project automates the entire data analysis workflow from natural language query to actionable business insights. 
Users ask questions in plain English, and the system automatically generates SQL queries, executes them, performs statistical analysis, creates visualizations, and produces executive summaries - all powered by Google's Gemini AI.
**Key Impact:** Reduces routine data analysis time from 2-3 hours to ~5 minutes (60% time savings).

---

## Why This Project?

### The Problem
Data analysts spend hours on repetitive tasks: writing SQL, analyzing data, creating charts, and writing reports for stakeholders. This creates bottlenecks in data-driven decision making.

### The Solution
An automated pipeline that transforms natural language questions into complete analysis reports with visualizations and AI-generated insights.

### My Motivation
I built this to:
- **Learn:** Gain hands-on experience with LLM APIs in production
- **Automate:** Eliminate repetitive data workflows
- **Explore:** Understand practical limitations of AI in analytics
- **Share:** Create an open-source template others can use

---

## Features

- **Natural Language SQL Generation** - Ask questions in plain English, get accurate SQL
- **Automated EDA** - Statistical analysis, distributions, insights
- **Auto-Visualization** - Publication-ready charts (PNG exports)
- **AI Executive Summaries** - Business insights and recommendations
- **Tableau Readiness** - CSV/Excel exports optimized for BI tools
- **Production-Ready** - Rate limiting, error handling, logging

---

## System Architecture

```
User Question → Gemini AI → SQL Query → PostgreSQL → Results → 
→ Automated EDA → Visualizations → Gemini AI → Executive Summary → Complete Report
```

**Full Pipeline:**
1. Natural language input
2. Gemini generates SQL with schema context
3. PostgreSQL executes query
4. Pandas processes results
5. Matplotlib creates visualizations
6. Statistical analysis extracts insights
7. Gemini writes executive summary
8. All outputs saved (SQL, charts, reports, Tableau files)

---

## Tech Stack

**Core:**
- Python | PostgreSQL | Google Gemini 

**Libraries:**
- pandas, numpy (data processing)
- psycopg2, SQLAlchemy (database)
- google-genai (AI)
- matplotlib, seaborn (visualization)
- python-dotenv (config)

---

## 📊 Database Schema

### Table: `sales_data`

**113,036 sales transactions** across 18 columns (2011-2016)

```sql
CREATE TABLE sales_data (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Temporal (4 columns)
    date DATE NOT NULL,
    day INTEGER,
    month VARCHAR(20),
    year INTEGER,
    
    -- Customer (3 columns)
    customer_age INTEGER,
    age_group VARCHAR(50),        -- Youth, Young Adults, Adults, Seniors
    customer_gender VARCHAR(10),   -- M, F
    
    -- Geographic (2 columns)
    country VARCHAR(50),
    state VARCHAR(100),
    
    -- Product (3 columns)
    product_category VARCHAR(100),  -- Bikes, Accessories, Clothing
    sub_category VARCHAR(100),
    product VARCHAR(200),
    
    -- Metrics (6 columns)
    order_quantity INTEGER,
    unit_cost DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    profit DECIMAL(10,2),
    cost DECIMAL(10,2),
    revenue DECIMAL(10,2)
);
```
---

## Components

### 1. Query Generator (`query_generator.py`)
- **Purpose:** Natural language → SQL using Gemini
- **Features:** Schema injection, validation, rate limiting
- **AI Model:** gemini-2.0-flash
- **Rate Limit:** 5s delay between requests

### 2. Automated EDA (`automated_eda.py`)
- **Purpose:** Statistical analysis & visualization
- **Analysis:** Mean, median, distributions, correlations
- **Outputs:** PNG charts, CSV/Excel, text reports
- **Backend:** Matplotlib 'Agg' (server-safe)

### 3. Summary Generator (`summary_generator.py`)
- **Purpose:** AI-written executive summaries
- **Sections:** Overview, findings, implications, recommendations
- **AI Model:** gemini-2.0-flash
- **Format:** Professional markdown

### 4. Data Loader (`data_loader.py`)
- **Purpose:** CSV → PostgreSQL pipeline
- **Features:** Bulk insert, type conversion, validation
- **Capacity:** Handles 100K+ rows efficiently

### 5. Main Workflow (`main.py`)
- **Purpose:** Orchestrates complete pipeline
- **Modes:** Interactive CLI, programmatic API
- **Output:** Complete reports with all assets

### 6. Config (`config.py`)
- **Purpose:** Centralized configuration
- **Features:** Env vars, DB pooling, connection testing

---

### Example Questions

- "What are the top 10 products by revenue in 2016?"
- "Show me monthly revenue trends"
- "Which age group has highest profit margin?"
- "Compare sales across countries"
- "What's average order value by gender?"

---

*If this helped you, ⭐ the repo :) *
