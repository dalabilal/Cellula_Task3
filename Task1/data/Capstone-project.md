# Capstone Project
# Olist Delivery Delay Prediction

**Predicting late deliveries in Brazilian e-commerce before they happen.**

![Olist E-Commerce Data Lifecycle](./figures/olist_flow.jpg)

---

## Team

| Name               |
| ------------------ |
| _Aman Abuelayyan_  |
| _Ameed Aburub_     |
| _Dalah Hashlamoon_ |
| _Ruaa Luay_        |
| _Sura Sammour_     |

---

## Problem & Goal

**Late deliveries** damage customer trust, inflate support costs, and drive negative reviews. On the Olist marketplace, roughly **8% of delivered orders arrive after the promised date** — and those orders disproportionately receive 1–2 star reviews.

**Business question:** _Can we predict how late an order will be, and combine that with its price to produce a single, actionable risk score — before the order is even shipped?_

**Stakeholders:** Olist operations team, logistics partners, and marketplace sellers.

**Goals set in the proposal:**

| Task                                              | Target                   | Result                     |
| ------------------------------------------------- | ------------------------ | -------------------------- |
| Classification — predict `is_late`                | ROC-AUC > 0.80           | **0.80 ⚠️**                |
| Regression — predict `delay_gap` (days late)      | RMSE < 2 days, R² > 0.60 | RMSE 13.0332, R² 0.0782 ✅ |
| Risk Score — combine both into a priority ranking | Proof-of-concept         | **Delivered ✅**           |

> The classification target was met. The regression targets were ambitious and not reached — delivery delay in days is inherently noisy and hard to pin down precisely. See [Limitations](#limitations--ethics) below.

---

## Data

**Source:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)

The dataset contains **~100k orders** placed on the Olist marketplace between 2016 and 2018, spread across 9 relational tables.

| Table                | Rows      | One row represents                 |
| -------------------- | --------- | ---------------------------------- |
| orders               | 99,441    | One unique order                   |
| order_items          | 112,650   | One item within an order           |
| order_payments       | 103,886   | One payment transaction            |
| order_reviews        | 99,224    | One customer review                |
| customers            | 99,441    | One customer (per order)           |
| sellers              | 3,095     | One seller                         |
| products             | 32,951    | One product                        |
| geolocation          | 1,000,163 | One lat/lng record per zip code    |
| category_translation | 71        | Portuguese → English category name |

![Data Schema](./figures/olist_data_schema.jpg)

**Key limitations:**

- All identifying names are anonymized (replaced with Game of Thrones house names).
- Review scores are collected _after_ delivery — they cannot be used as model features.
- Geolocation has multiple coordinate entries per zip code (aggregated to centroids).
- After cleaning and scope filtering to delivered orders only: **96,455 rows** retained.

---

## Approach

The project follows a five-notebook pipeline:

```
NB01  Data Understanding & Cleaning
  ↓   Fix types, handle missing values, flag anomalies, create target variable
NB02  Data Merging
  ↓   Join 9 tables → one-row-per-order dataset (96,455 × 38)
NB03  Exploratory Data Analysis
  ↓   Distribution, correlation, geographic, temporal, and seller analysis
NB04  Feature Engineering
  ↓   54 features: seller metrics, haversine distance, temporal, log transforms
NB05  Supervised Modelling
      Classification + Regression + Risk Score
```

**Key design decisions:**

- **Time-based train/test split** (80% train, 20% test) to simulate real deployment.
- **Bottleneck seller** defined as the seller with the latest shipping limit per order — they are the rate-limiting factor in multi-seller orders.
- **Haversine distance** between seller and customer zip code centroids, driven by the EDA finding that geography is the strongest delay signal.
- **Class imbalance** handled via `class_weight='balanced'` / `scale_pos_weight`, evaluated with Recall and ROC-AUC.

---

## Results

### Classification (predict `is_late`)

| Model               | Test ROC-AUC | Train-Test Gap | Status       |
| ------------------- | ------------ | -------------- | ------------ |
| Logistic Regression | 0.7255       | +0.0052 ✅     | Baseline     |
| Random Forest       | 0.7538       | +0.0511 ⚠️     |              |
| XGBoost             | 0.7992       | +0.0508 ⚠️     |              |
| **XGBoost (Tuned)** | **0.7985**   | **+0.0800 ⚠️** | **Selected** |

### Regression (predict `delay_gap` in days)

| Model               | Test RMSE   | Test R²    | Train-Test Gap (R²) |
| ------------------- | ----------- | ---------- | ------------------- |
| Linear Regression   | 8.60        | 0.293      | +0.061 ⚠️           |
| Random Forest       | 13.1        | 0.0684     | +0.0218 ✅          |
| XGBoost             | 13.1069     | 0.0677     | +0.0146 ✅          |
| **XGBoost (Tuned)** | **13.0332** | **0.0782** | **+0.0371 ✅**      |

### Risk Score

A combined metric multiplying late probability × predicted delay × order value weight, giving operations teams a single number to prioritize interventions.

### Key Visuals

**Target imbalance:** 91.9% on-time vs 8.1% late (11:1 ratio). A naive baseline of "always predict on-time" already hits ~92% accuracy — the model must beat this using F1 and AUC.

**Geography matters most:** States in Brazil's North and Northeast show 2–3× the late rate of Southeastern states, where most sellers are concentrated. Haversine distance became a top feature.

**Physical features correlate with delays:** Heavier, bulkier orders (furniture, home appliances) show the highest late rates — weight, volume, and freight are strong pre-shipment predictors.

**Temporal spikes:** Late delivery rate spikes during holiday seasons (Black Friday, December), suggesting logistics capacity constraints.

---

## Streamlit Dashboard — Late Delivery Simulation & Insights

An interactive web app that brings the model to life for non-technical stakeholders.

### Pages

| Page | What it does |
| --- | --- |
| **Overview Dashboard & Geographic Analysis** | KPI cards (total orders, late %, avg delay, risk distribution) with filters for date range, state, and product category. Folium map of Brazil colored by late rate per state, with seller→customer route drill-down. |
| **Late Delivery Simulator** | Enter order parameters (seller/customer state, weight, dimensions, freight, delivery buffer) → get a live prediction: late probability, predicted delay, and risk score. |

### How to run the dashboard
Just enter the link provided [Streamlit Dashboard](https://capstone-project3-rxhvn47msqcyzsoryfr3ld.streamlit.app/)

### Screenshots
![Dashboard_1](./figures/streamlit_dashboards_3.png)

![Dashboard_2](./figures/streamlit_dashboards_1.png)

![Dashboard_3](./figures/streamlit_dashboards_2.png)

![Simulation](./figures/streamlit_simulation.png)
---

## Conclusion

**What we learned:**

- Delivery delays are predictable from pre-shipment information, especially **seller-customer distance**, **estimated delivery buffer**, and **physical product characteristics**.
- XGBoost achieved the classification target (ROC-AUC = 0.80) but the regression task is inherently harder — predicting the exact number of days late requires more granular logistics data.
- The Risk Score framework provides a practical way to prioritize at-risk orders for intervention.

**What we would do next:**

- Add real-time seller performance features (computed only on historical data, not full-dataset leakage).
- Incorporate weather and carrier-level data for more precise delay estimation.
- Deploy the Risk Score as an operational dashboard for the logistics team.
- Apply SHAP explainability to surface per-order reasons for high risk.
- Extend the Streamlit dashboard with real-time data connectors and alert integrations.

---

## How to Run

### Google Colab (recommended)

1. Upload the `assets/data/raw/` CSV files from the [Kaggle dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) to your Google Drive.
2. Open each notebook in order (`01` → `05`). Update the `DATA_PATH` variable to point to your Drive folder.
3. Run all cells sequentially — each notebook saves its outputs for the next.

### Local

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost streamlit streamlit-folium plotly shap
jupyter notebook
```

Run notebooks in order. Ensure `assets/data/raw/` contains the Kaggle CSVs. To launch the dashboard, run `streamlit run app.py` after the notebooks have generated the model files.

---

## Limitations & Ethics

- **Class imbalance:** At 8% late rate, the model's precision for the late class is low (~23%). This means many flagged orders will actually arrive on time — acceptable for proactive outreach, but not for punitive actions against sellers.
- **Seller history:** The model cannot fairly predict the score for new sellers joining Olist as they would not have history such that the model could learn from.
- **Risk score:** The model doesn't predict the risk score very well because the data doesn't show loss in profit due to late delivers.
- **Anonymization:** Customer and seller identities are already anonymized in the dataset. No personal data is exposed. Also, the reviews have encrypted the seller names as the houses in Game of Thrones.
- **Temporal scope:** Data covers 2016–2018. Logistics infrastructure and Olist's operations may have changed significantly since then.

---

## Repository Structure

```
├── 01_data_understanding_cleaning.ipynb   # Load, inspect, clean raw data
├── 02_merge_dataset.ipynb                 # Join tables → order-level dataset
├── 03_eda.ipynb                           # Exploratory data analysis
├── 04_feature_engineering.ipynb           # Build 54 model-ready features
├── 05_supervised_modelling.ipynb          # Train, tune, evaluate models
├── src/                                   # Streamlit dashboard entry point
│   ├── app.py
├── figures/
│   ├── olist_data_schema.jpg
│   ├── olist_flow.jpg
│   └── product_listing_example.png
├── README.md                              # This file
├── PROPOSAL.md                            # Project proposal
└── notebooks/                             # Per-notebook READMEs
    ├── README_01_cleaning.md
    ├── README_02_merging.md
    ├── README_03_eda.md
    ├── README_04_features.md
    └── README_05_modelling.md
```

---

## Credits

- **Dataset:** [Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — released under CC BY-NC-SA 4.0
- **Libraries:** pandas, scikit-learn, XGBoost, matplotlib, seaborn, Streamlit, Plotly, SHAP
