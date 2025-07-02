# 🐦 **Extracting and Transforming Colonial Waterbird Records in AWS**

🔬 A Scalable Conservation Data Pipeline using Historical Survey Data from the Atlantic Flyway

## 📘 **Project Overview**

This project was completed as part of DAEN 690: Data Analytics Project at George Mason University. The objective was to build an end-to-end AWS data pipeline to extract, clean, validate, and visualize historical colonial waterbird (CWB) survey data across the Atlantic Flyway in support of science-driven conservation planning.

---

## 👥 **Client Profile**

Atlantic Flyway Council (AFC) – Nongame Migratory Bird Technical Section (NMBTS)

🐦 Focus: Monitoring and conserving bird populations in the Atlantic Flyway
🎯 Goal: Support conservation decision-making through reliable historical data extraction

📧 Contacts: 
→ **Ruth Boettcher – Chair, Waterbirds Committee** 
→ **Angela Tringali – Conservation Delivery Specialist**

---

## ☁️ AWS-Based Architecture

The entire pipeline was built in the AWS ecosystem:

* ✅ **Raw data stored in Amazon S3** (`raw/`, `reference/`)
* ✅ **ETL pipelines built using AWS Glue Spark Jobs**
* ✅ **Metadata cataloged using AWS Glue Crawlers**
* ✅ **Data queried via Amazon Athena**
* ✅ **Dashboards created with Tableau from Athena outputs**
![blue_heron_architecture](https://github.com/user-attachments/assets/a4952bca-6850-4c94-9151-58f5f19e277e)


---

## 🧠 Project Objectives

✅ Extract reliable records from large-scale CWB datasets using Glue
✅ Standardize taxonomy (AOU codes) and normalize species names
✅ Fill missing population estimates using fallback logic
✅ Clean and standardize survey metadata (state codes, dates, methods)
✅ Deduplicate records and validate geolocation + survey dates
✅ Deliver live, filterable dashboards via Tableau connected to Athena

---

## 🧹 Data Cleaning Steps in AWS

All cleaning steps were executed through modular **AWS Glue PySpark scripts** on S3-stored Parquet files:

1. **`clean_states.py`**
   → Standardized U.S. state abbreviations using a reference file from S3

2. **`species_filter.py`**
   → Split mixed species column into `AOU_CODE` and `COMMON_NAME`
   → Mapped and imputed missing species names using reference codes
   → Filtered out non-colonial species based on stakeholder-provided list

3. **`standardize_survey_and_fill_population.py`**
   → Filled `PopulationEstimate` using `CorrectedCount` → `UncorrectedCount` fallback logic
   → Labeled fill source for transparency
   → Normalized `SurveyMethod` and `DataQuality` columns

4. **`deduplicate_and_validate_dates.py`**
   → Removed duplicate survey records
   → Validated and formatted `SurveyDate` fields, dropping future/null values

---

## 📊 Dashboards

Published Tableau dashboards connected to Athena:

* **Dashboard 1:** Atlantic Flyway Avian Population Overview
  🔗 [View Dashboard](https://public.tableau.com/app/profile/paidigumal.vivek.patil/viz/ColonialWaterbirdsDistribution-puneethsandeep_17476023622860/Final2?publish=yes)

* **Dashboard 2:** Colony Distribution by Population Size
  🔗 [View Dashboard](https://public.tableau.com/app/profile/paidigumal.vivek.patil/viz/ColonyDistributionasperpopulationsizeperyear-2-shreya_17476020354550/Dashboard1?publish=yes)

* **Dashboard 2.1:** Species-Level Exploration of Colonies
  🔗 [View Dashboard](https://public.tableau.com/app/profile/paidigumal.vivek.patil/viz/Dashboardforcoloniesw_r_tspecies_17476018407520/Dashboard3?publish=yes)

---

## ⚙️ Technologies & Services Used

| Tool/Service       | Purpose                                               |
| ------------------ | ----------------------------------------------------- |
| `Amazon S3`        | Raw and processed data lake storage                   |
| `AWS Glue (Spark)` | Serverless ETL jobs for cleaning and transformation   |
| `AWS Glue Crawler` | Cataloged Parquet outputs into Athena-readable tables |
| `Amazon Athena`    | Serverless querying of cleaned datasets               |
| `Tableau`          | Visualization and stakeholder reporting interface     |
| `Python (PySpark)` | Custom logic for data wrangling in Glue               |
| `Geopy, Pandas`    | Early geolocation-based fixes (Python local)          |

---

## 📌 Key Achievements

📍 Validated over 10,000 site coordinates
📊 Harmonized 40+ years of survey records into clean S3-based datasets
🧬 Aligned species info with modern AOU taxonomy
🧹 Built a reusable AWS Glue ETL framework
📈 Delivered 3 interactive Tableau dashboards connected to Athena

---

## 🌿 Conservation Impact

This project provides decision-makers with a unified, trusted view of historical colonial waterbird data across the Atlantic Flyway. Through scalable AWS infrastructure and interactive dashboards, it improves accessibility and usefulness of ecological data for conservation science.
