CREATE TABLE IF NOT EXISTS raw_dailymed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setid TEXT,
    drug_name TEXT,
    raw_xml_path TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parsed_formulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setid TEXT,
    api_name TEXT,
    strength TEXT,
    dosage_form TEXT,
    route TEXT,
    source TEXT,
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS editable_formulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    setid TEXT,

    api_name TEXT,
    strength TEXT,
    dosage_form TEXT,
    route TEXT,

    api_cost_per_kg REAL,
    excipient_cost REAL,

    formulation_notes TEXT,
    manufacturing_notes TEXT,

    user_edited INTEGER DEFAULT 0,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    brand_name TEXT,
    manufacturer TEXT,

    setid TEXT UNIQUE,

    approval_year TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS market_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    setid TEXT,

    annual_sales_usd REAL,
    competitors INTEGER,

    patent_expiry TEXT,

    launch_complexity TEXT,
    priority_score REAL,

    notes TEXT,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);