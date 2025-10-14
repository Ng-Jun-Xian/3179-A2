import pandas as pd
import numpy as np

# Read the datasets
domestic = pd.read_csv('Coffee_domestic_consumption.csv')
importers = pd.read_csv('Coffee_importers_consumption.csv')
population = pd.read_csv('country_pop.csv')

# Prepare domestic consumption data
# Extract year columns (those ending with /91, /92, etc.)
year_cols_domestic = [col for col in domestic.columns if '/' in col]
domestic_melted = domestic.melt(
    id_vars=['Country', 'Coffee type'],
    value_vars=year_cols_domestic,
    var_name='Year_Period',
    value_name='Domestic_Consumption'
)
# Convert year period (e.g., "1990/91") to just the first year (1990)
domestic_melted['Year'] = domestic_melted['Year_Period'].str.split('/').str[0].astype(int)
domestic_melted = domestic_melted.drop('Year_Period', axis=1)

# Prepare importers consumption data
# Extract year columns (numeric years)
year_cols_importers = [col for col in importers.columns if col.isdigit()]
importers_melted = importers.melt(
    id_vars=['Country'],
    value_vars=year_cols_importers,
    var_name='Year',
    value_name='Import_Consumption'
)
importers_melted['Year'] = importers_melted['Year'].astype(int)

# Prepare population data
# Extract year columns (numeric years from 1990-2024)
year_cols_pop = [str(year) for year in range(1990, 2025) if str(year) in population.columns]
population_melted = population.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_cols_pop,
    var_name='Year',
    value_name='Population'
)
population_melted['Year'] = population_melted['Year'].astype(int)
population_melted = population_melted.rename(columns={'Country Name': 'Country'})

# Create a mapping for country name variations
country_mapping = {
    'United States': 'United States',
    'Dem. Rep. Congo': 'Congo, Dem. Rep.',
    'Congo': 'Congo, Rep.',
    'Dominican Rep.': 'Dominican Republic',
    'Central African Rep.': 'Central African Republic',
    'Eq. Guinea': 'Equatorial Guinea',
    'Cote d\'Ivoire': 'Cote d\'Ivoire',
}

# Apply country name standardization
domestic_melted['Country'] = domestic_melted['Country'].replace(country_mapping)
importers_melted['Country'] = importers_melted['Country'].str.strip()

# Merge domestic and importers data
merged = pd.merge(
    domestic_melted,
    importers_melted,
    on=['Country', 'Year'],
    how='outer'
)

# Merge with population data
merged = pd.merge(
    merged,
    population_melted[['Country', 'Year', 'Population']],
    on=['Country', 'Year'],
    how='left'
)

# Calculate total consumption (domestic + imports)
merged['Total_Consumption'] = merged['Domestic_Consumption'].fillna(0) + merged['Import_Consumption'].fillna(0)

# Replace zero consumption with NaN for proper calculation
merged.loc[merged['Total_Consumption'] == 0, 'Total_Consumption'] = np.nan

# Calculate per capita consumption (kg per person)
# Note: consumption is in kg, population is in people
merged['Consumption_Per_Capita_kg'] = merged['Total_Consumption'] / merged['Population']

# Also calculate in grams per person per year (more readable)
merged['Consumption_Per_Capita_g'] = merged['Consumption_Per_Capita_kg'] * 1000

# Sort by country and year
merged = merged.sort_values(['Country', 'Year'])

# Select and reorder columns
final_columns = [
    'Country',
    'Year',
    'Coffee type',
    'Population',
    'Domestic_Consumption',
    'Import_Consumption',
    'Total_Consumption',
    'Consumption_Per_Capita_kg',
    'Consumption_Per_Capita_g'
]

merged_final = merged[final_columns]

# Remove rows where we don't have consumption data
merged_final = merged_final[merged_final['Total_Consumption'].notna()]

# Save to CSV
merged_final.to_csv('Coffee_consumption_per_capita.csv', index=False)

print("Dataset created successfully!")
print(f"\nTotal rows: {len(merged_final)}")
print(f"Countries: {merged_final['Country'].nunique()}")
print(f"Year range: {merged_final['Year'].min()} - {merged_final['Year'].max()}")
print("\nSample of the data:")
print(merged_final.head(10))

# Create summary statistics
print("\n=== Summary Statistics ===")
print("\nTop 10 countries by average per capita consumption (kg):")
top_consumers = merged_final.groupby('Country')['Consumption_Per_Capita_kg'].mean().sort_values(ascending=False).head(10)
print(top_consumers)

# Save summary
summary = merged_final.groupby('Country').agg({
    'Consumption_Per_Capita_kg': ['mean', 'min', 'max'],
    'Total_Consumption': ['mean', 'sum'],
    'Year': ['min', 'max']
}).round(4)
summary.to_csv('Coffee_consumption_summary.csv')
print("\nSummary statistics saved to 'Coffee_consumption_summary.csv'")