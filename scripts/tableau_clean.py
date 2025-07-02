# Visualization Preparation Pipeline for Tableau
# Purpose: Prepare cleaned Atlantic Flyway dataset for visualization by handling date formatting,
# duplicate population entries, and quality-based deduplication of records

#THIS CODE DOESNT EFFECT CLEANED DATASET, IT IS ONLY USED TO MAKE VISUALUIZATIONS.

import pandas as pd

# STEP 1: Load the cleaned dataset for visualization
viz_df = pd.read_csv("Cleaned_Atlantic_Flyway_data.csv")

# STEP 2: Construct a clean 'EffectiveSurveyDate' from year, month, and day columns
viz_df['Year'] = viz_df['Year'].astype(str)
viz_df['Month'] = viz_df['Month'].fillna(0).astype(int).astype(str).replace('0', '')
viz_df['Day'] = viz_df['Day'].fillna(0).astype(int).astype(str).replace('0', '')

viz_df['EffectiveSurveyDate'] = viz_df['Year']
viz_df.loc[viz_df['Month'] != '', 'EffectiveSurveyDate'] = viz_df['Year'] + '-' + viz_df['Month']
viz_df.loc[viz_df['Day'] != '', 'EffectiveSurveyDate'] = viz_df['Year'] + '-' + viz_df['Month'] + '-' + viz_df['Day']

# STEP 3: Identify and remove duplicate nest records using the 2:1 Individuals:Nests ratio
pop_df = viz_df[['State', 'EffectiveSurveyDate', 'UnitCounted', 'PopulationEstimate']].dropna(subset=['EffectiveSurveyDate'])
pivot = pop_df.pivot_table(index=['State', 'EffectiveSurveyDate'], columns='UnitCounted', values='PopulationEstimate', aggfunc='sum').reset_index()
pivot['Ratio'] = pivot['Individuals'] / pivot['Nests']

duplicates_to_remove = pivot[pivot['Ratio'] == 2.0]
viz_df = viz_df.merge(duplicates_to_remove[['State', 'EffectiveSurveyDate']], on=['State', 'EffectiveSurveyDate'], how='left', indicator=True)
viz_df = viz_df[~((viz_df['UnitCounted'] == 'Nests') & (viz_df['_merge'] == 'both'))].drop(columns=['_merge'])

# STEP 4: Adjust all remaining Nest-based estimates by multiplying by 2
viz_df.loc[viz_df['UnitCounted'] == 'Nests', 'PopulationEstimate'] *= 2

# STEP 5: Deduplicate records at the colony level using reliability and data quality
viz_df = viz_df[viz_df["ColonyName"].str.strip().str.lower() != "unspecified"]
viz_df["PopulationEstimate"] = pd.to_numeric(viz_df["PopulationEstimate"], errors="coerce")

reliability_rank = {4: 1, 3: 2, 2: 3, 1: 4, 9: 4}
data_quality_rank = {"Precise Estimate": 1, "Good Estimate": 2, "Rough Estimate": 3, "Unknown": 4}

viz_df["ReliabilityRank"] = viz_df["ReliabilityCode"].map(reliability_rank).fillna(4).astype(int)
viz_df["DataQualityRank"] = viz_df["DataQuality"].map(data_quality_rank).fillna(4).astype(int)
viz_df["PopScore"] = viz_df["PopulationEstimate"].fillna(0)
viz_df["CompositeScore"] = viz_df["ReliabilityRank"] * 10000 + viz_df["DataQualityRank"] * 100 - viz_df["PopScore"]

group_keys = ["ColonyName", "State", "Year", "Month", "Species"]
if "Observer" in viz_df.columns:
    group_keys.append("Observer")

idx_best = viz_df.groupby(group_keys)["CompositeScore"].idxmin()
best_records = viz_df.loc[idx_best]

group_counts = viz_df.groupby(group_keys).size()
duplicate_keys = group_counts[group_counts > 1].index
duplicate_mask = viz_df.set_index(group_keys).index.isin(duplicate_keys)
non_duplicate_records = viz_df[~duplicate_mask]

# STEP 6: Combine the best and unique records
deduped_viz_df = pd.concat([best_records, non_duplicate_records], ignore_index=True).drop_duplicates()

# STEP 7: Export final visualization-ready dataset
deduped_viz_df.to_csv("Cleaned_Atlantic_Flyway_VIZ.csv", index=False)
print("✅ Visualization-ready dataset saved as 'Cleaned_Atlantic_Flyway_VIZ.csv'")
