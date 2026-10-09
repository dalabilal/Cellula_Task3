# Capstone Project - Project Proposal — Olist Delivery Delay Prediction

## 1. Problem Statement

Olist is the largest department store in Brazilian marketplaces, connecting small businesses to multiple sales channels through a single contract. The platform processed over 100,000 orders between 2016 and 2018.

A persistent operational challenge is **late deliveries**. When an order arrives after the estimated delivery date, customers leave negative reviews, contact support, and lose trust in the platform. This damages both Olist's reputation and the individual seller's standing.

**Business question:** Can we predict how late an order will be, and combine that with its price to produce a single, actionable risk score — before the order is even shipped?

## 2. Target Users

- **Olist Operations Team:** Use predictions to flag at-risk orders for proactive customer communication or logistics rerouting.
- **Sellers:** Receive alerts about orders likely to arrive late, allowing them to adjust packaging timelines or choose faster shipping options.
- **Product Team:** Use delay patterns to set more accurate estimated delivery dates.

## 3. Dataset

**Source:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset includes 9 relational tables covering orders, items, payments, reviews, customers, sellers, products, and geolocation. In total, approximately 100,000 anonymized orders with full lifecycle data (purchase → payment → shipment → delivery → review).

**One row in the final dataset represents:** one delivered order, enriched with aggregated item, payment, seller, and geographic features.

**Limitations:**

- Data is from 2016–2018; logistics infrastructure may have changed.
- All identifying names are anonymized.
- Review scores are post-delivery and cannot be used as model features (leakage).

## 4. Approach

### Stage 1 — Data Preparation

- Load and inspect all 9 tables, fix data types, handle missing values.
- Scope to delivered orders only (drop canceled, shipped-but-undelivered, etc.).
- Create target variable: `is_late = 1` if actual delivery date > estimated delivery date.

### Stage 2 — Classification

- Predict `is_late` (binary: 0 = on-time, 1 = late).
- Models: Logistic Regression (baseline), Random Forest, XGBoost.
- Handle class imbalance (~8% late) with balanced class weights.

### Stage 3 — Regression

- Predict `delay_gap` (continuous: actual delivery date − estimated date, in days).
- Models: Linear Regression (baseline), Random Forest, XGBoost.

### Stage 4 — Risk Score

- Combine classification probability × predicted delay × order value into a single operational risk score.

## 5. Success Metrics

| Task           | Metric          | Target   |
| -------------- | --------------- | -------- |
| Classification | ROC-AUC         | > 0.80   |
| Classification | F1 (late class) | > 0.75   |
| Regression     | RMSE            | < 2 days |
| Regression     | R²              | > 0.60   |

**Why these metrics:**

- ROC-AUC over accuracy because the dataset is heavily imbalanced (11:1).
- F1 for the late class specifically because false negatives (missing a late order) are costly.
- RMSE for regression because large errors (predicting 2 days late when it's 20) are especially undesirable.

## 6. Deliverables

1. Five Jupyter notebooks covering the full pipeline (cleaning → merging → EDA → features → modeling).
2. A model-ready feature matrix with 50+ engineered features.
3. Trained XGBoost classification and regression models.
4. A Risk Score proof-of-concept combining both models.
5. **Streamlit Dashboard** — an interactive web app for late delivery simulation and operational insights (see details below).
6. Documentation: main README, proposal, and per-notebook READMEs.

### Streamlit Dashboard — Late Delivery Simulation & Insights

The dashboard serves as the project's user-facing deliverable, translating model outputs into an interactive tool that stakeholders can use without touching code.

**Planned pages:**

| Page | Purpose |
| --- | --- |
| **Overview Dashboard and Geographic Analysis** | High-level KPIs: total orders, late %, average delay, risk score distribution. Filterable by date range, state, and product category. Visual breakdown of which features drive the model's predictions (global SHAP summary + per-prediction waterfall). |
| **Late Delivery Simulator** | Users input order parameters (seller state, customer state, product weight/dimensions, freight value, estimated delivery buffer) and receive a real-time prediction: late probability, predicted delay in days, and risk score. |

**Technical plan:**

- Load the trained XGBoost models (classification + regression) via `joblib`.
- Use `streamlit-folium` for geographic visualizations and `plotly` for interactive charts.
- Provide a CSV upload option so users can batch-score new orders.
- Deploy via Streamlit Community Cloud (free tier) with the GitHub repo as source.

## 7. Tools & Libraries

- **Data:** pandas, NumPy
- **Visualization:** matplotlib, seaborn
- **Modeling:** scikit-learn, XGBoost
- **Dashboard:** Streamlit, streamlit-folium, Plotly
- **Environment:** Google Colab / Jupyter Notebook

## 8. Risks & Mitigations

| Risk                                                       | Mitigation                                                                    |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Class imbalance skews model toward "on-time"               | Use balanced class weights; evaluate with F1 and AUC, not accuracy            |
| Seller performance features leak future data               | Flag for production fix; compute on train-only in deployment                  |
| Geographic features may systematically flag remote regions | Monitor for bias; combine with seller-side features                           |
| Regression targets may be too ambitious                    | Accept classification as primary deliverable; treat regression as exploratory |

## 9. Timeline

| Week | Milestone                             |
| ---- | ------------------------------------- |
| 1    | Data understanding, cleaning, merging |
| 2    | EDA and feature engineering           |
| 3    | Modeling, tuning, risk score          |
| 4    | Streamlit dashboard development       |
| 5    | Documentation, final review           |
