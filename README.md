# Pharma Portfolio Platform

### Intelligent Generic Drug Portfolio Evaluation & Commercial Planning Platform

**Version:** 1.0 Backend Stable
**Organization:** Genvicure
**Technology Stack:** Python • Streamlit • SQLite • Pandas

---

# Overview

The Pharma Portfolio Platform is an enterprise-grade Streamlit application developed to support **US Generic Pharmaceutical Portfolio Evaluation**, **Product Costing**, **Commercial Analysis**, and **API Procurement Planning**.

The platform consolidates regulatory, formulation, costing, and commercial information into a single interactive workflow, allowing business development, portfolio management, formulation scientists, and commercial teams to evaluate generic product opportunities efficiently.

Unlike a traditional dashboard, this application functions as an integrated pharmaceutical business intelligence platform with editable calculations, synchronized costing models, and dynamic commercial planning.

---

# Key Features

## Drug Search & Regulatory Intelligence

* Search generic products using FDA and internal datasets.
* Retrieve Orange Book information.
* Retrieve DailyMed product information.
* Retrieve RxNorm mappings.
* Parse formulation and strength information.
* Manufacturer-specific product selection.
* Automatic dosage form filtering.
* Dynamic manufacturer switching.

---

## Manufacturer Selection

Supports multiple manufacturers for the same product.

Changing the selected manufacturer automatically updates:

* Available strengths
* Formulation tables
* Commercial model
* Economics model
* API planning tables

without requiring manual refresh.

---

## Formulation Costing

Each strength receives its own editable formulation table.

Typical ingredients include:

* API
* Excipient 1
* Excipient 2

Editable fields include:

* mg per unit
* Per Kg Cost

Automatically calculated:

* Per Mg Cost
* Cost per Unit
* Cost per Bottle

Supports:

* Dynamic strength generation
* Automatic ingredient registration
* Bottle size calculations
* Strength-specific totals

---

## Global Ingredient Cost Management

Ingredient costs are maintained as a centralized master.

Changing an ingredient cost automatically updates every table where the ingredient is used.

This provides a single source of truth for formulation costing.

---

## Per Tablet Economics

Automatically calculates:

* API Cost
* Raw Material Cost
* Packaging Material Cost
* Manufacturing Cost
* COGS
* Markup
* Selling Price

Markup values are editable and persist between calculations.

---

## Commercial Analysis

Provides commercial evaluation for every strength.

Calculations include:

* Transfer Price
* Annual Volume
* Annual COGS
* Discount
* Selling Price
* Marketing & Logistics Cost
* Total Profit
* Profit Share

Commercial calculations remain synchronized with formulation and economics data.

---

## API Commercial Planning

Automatically estimates future API procurement requirements.

Calculations include:

* Annual Demand
* Number of Tablets
* Total API Requirement
* Total API (Kg)
* Commercial API Cost

API pricing is synchronized directly from Formulation Costing, ensuring a single source of truth.

---

## Engineering Batch (EB) Planning

Supports multiple Engineering Batch scenarios.

Features include:

* Multiple EB Scenarios
* Independent batch sizes
* Automatic API quantity calculations
* Rounded API quantity
* Manual total batch cost entry
* Parallel scenario comparison

---

## Dynamic Session State Architecture

The application is heavily state-driven using Streamlit Session State.

Key synchronized objects include:

* strength_tables
* strength_totals
* ingredient_costs
* master_df
* economics_df
* discount_values
* markup_values
* year1_values
* eb_tables

This architecture ensures all modules remain synchronized while minimizing duplicate calculations.

---

# Data Sources

The platform integrates multiple pharmaceutical datasets.

* FDA Orange Book
* DailyMed XML
* RxNorm
* Internal commercial datasets
* SQLite project database

---

# Current Workflow

```
Drug Selection
        │
        ▼
Manufacturer Selection
        │
        ▼
Drug Profile Generation
        │
        ▼
Formulation Costing
        │
        ▼
Global Ingredient Costing
        │
        ▼
Per Tablet Economics
        │
        ▼
Commercial Analysis
        │
        ▼
API Commercial Planning
        │
        ▼
Engineering Batch Planning
```

---

# Technology Stack

Backend

* Python
* Pandas
* SQLite

Frontend

* Streamlit

Data Sources

* FDA Orange Book
* DailyMed
* RxNorm

---

# Project Structure

```
pharma-portfolio-platform/

│
├── app/
│   ├── components/
│   ├── database/
│   ├── models/
│   ├── services/
│   └── utils/
│
├── data/
│   ├── orangebook/
│   ├── raw_dailymed/
│   ├── parsed/
│   ├── editable/
│   └── pharma.db
│
├── tests/
│
├── streamlit_app.py
├── requirements.txt
├── create_db.py
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/Tech-genvicure/Costing-Sheet.git
```

Navigate into the project

```bash
cd Costing-Sheet
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run streamlit_app.py
```

---

# Current Version (v1.0)

Completed modules:

* Drug Search
* Manufacturer Selection
* Drug Profile Builder
* Formulation Costing
* Global Ingredient Cost Synchronization
* Per Tablet Economics
* Commercial Analysis
* API Commercial Planning
* Engineering Batch Planning
* Dynamic Session State Synchronization

---

# Planned Enhancements

Frontend

* Enterprise AG Grid integration
* Professional UI redesign
* Genvicure branding
* Enhanced table styling
* Interactive charts
* Dashboard landing page

Backend

* User authentication
* Role-based access
* Audit logging
* Cost history
* Version tracking
* Automated report generation
* Excel export improvements

Deployment

* Private cloud deployment
* Multi-user collaboration
* Secure database integration

---

# Project Status

**Current Development Phase**

Backend functionality is complete and stable.

The next phase focuses on modernizing the user interface with enterprise-grade editable grids, enhanced visualizations, and improved user experience while preserving the existing business logic and calculation engine.

---

# License

Internal proprietary software.

Developed for Genvicure.

All rights reserved.
