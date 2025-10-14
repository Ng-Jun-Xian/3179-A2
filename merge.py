import pandas as pd
import numpy as np

# Read the datasets
domestic = pd.read_csv('Coffee_domestic_consumption.csv')
importers = pd.read_csv('Coffee_importers_consumption.csv')
population = pd.read_csv('country_pop.csv')

# Print a sample of country names from each dataset to identify inconsistencies
print("Sample domestic countries:", domestic['Country'].unique()[:10])
print("Sample importers countries:", importers['Country'].unique()[:10])
print("Sample population countries:", population['Country Name'].unique()[:10])

# Prepare domestic consumption data
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
year_cols_importers = [col for col in importers.columns if col.isdigit()]
importers_melted = importers.melt(
    id_vars=['Country'],
    value_vars=year_cols_importers,
    var_name='Year',
    value_name='Import_Consumption'
)
importers_melted['Year'] = importers_melted['Year'].astype(int)
importers_melted['Country'] = importers_melted['Country'].str.strip()  # Strip whitespace

# Prepare population data
year_cols_pop = [str(year) for year in range(1990, 2025) if str(year) in population.columns]
population_melted = population.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_cols_pop,
    var_name='Year',
    value_name='Population'
)
population_melted['Year'] = population_melted['Year'].astype(int)
population_melted = population_melted.rename(columns={'Country Name': 'Country'})

# Instead of creating a DataFrame, print the counts and some examples
coffee_countries = sorted(set(list(domestic_melted['Country'].unique()) + list(importers_melted['Country'].unique())))
pop_countries = sorted(population_melted['Country'].unique())

print(f"\nTotal unique countries in coffee datasets: {len(coffee_countries)}")
print(f"Total unique countries in population dataset: {len(pop_countries)}")
print("\nSample coffee countries:", coffee_countries[:10])
print("Sample population countries:", pop_countries[:10])

# Create a comprehensive mapping dictionary for problematic countries
coffee_to_population_mapping = {
    # Central African Republic specific mapping
    'Central African Republic': 'Central African Republic',
    'Central African Rep.': 'Central African Republic',
    
    # Fix for specific country names
    'Congo': 'Congo, Rep.',
    'Dem. Rep. Congo': 'Congo, Dem. Rep.',
    'Dominican Rep.': 'Dominican Republic',
    'Eq. Guinea': 'Equatorial Guinea',
    'Cote d\'Ivoire': 'Cote d\'Ivoire',
    'Belgium/Luxembourg': 'Belgium',
    'Russia': 'Russian Federation',
    'USA': 'United States',
    'Czech Republic': 'Czechia',
    'Korea, Rep': 'Korea, Rep.',
    'Laos': 'Lao PDR'
}

# Apply country name standardization
domestic_melted['Country'] = domestic_melted['Country'].replace(coffee_to_population_mapping)
importers_melted['Country'] = importers_melted['Country'].replace(coffee_to_population_mapping)

# Create explicit reverse mapping for population dataset
population_to_coffee_mapping = {
    'Central African Republic': 'Central African Republic',
    'Congo, Rep.': 'Congo',
    'Congo, Dem. Rep.': 'Dem. Rep. Congo',
    'Dominican Republic': 'Dominican Rep.',
    'Equatorial Guinea': 'Eq. Guinea',
    'Russian Federation': 'Russia',
    'Czechia': 'Czech Republic',
    'Korea, Rep.': 'Korea, Rep',
    'Lao PDR': 'Laos'
}

# Apply population mapping
population_melted['Country'] = population_melted['Country'].replace(population_to_coffee_mapping)

# Check for Central African Republic specifically
print("\nChecking Central African Republic data:")
print("In domestic dataset:", 'Central African Republic' in domestic_melted['Country'].values)
print("In importers dataset:", 'Central African Republic' in importers_melted['Country'].values)
print("In population dataset:", 'Central African Republic' in population_melted['Country'].values)

# Merge domestic and importers data
merged = pd.merge(
    domestic_melted,
    importers_melted,
    on=['Country', 'Year'],
    how='outer'
)

# Create a list of countries to manually check
key_countries = ['Central African Republic', 'Dominican Republic', 'Congo', 'Dem. Rep. Congo']

print("\nBefore population merge, checking key countries:")
for country in key_countries:
    in_merged = country in merged['Country'].values
    in_pop = country in population_melted['Country'].values
    print(f"{country}: In merged data: {in_merged}, In population data: {in_pop}")

# Merge with population data
merged = pd.merge(
    merged,
    population_melted[['Country', 'Year', 'Population']],
    on=['Country', 'Year'],
    how='left'
)

# Check for missing population data after merge
missing_pop = merged[merged['Population'].isna()]
missing_pop_countries = missing_pop['Country'].unique()
print(f"\nCountries with missing population data ({len(missing_pop_countries)}):")
if len(missing_pop_countries) > 0:
    print(missing_pop_countries[:10])  # Show first 10
    
    # For Central African Republic, do a direct lookup from population data
    if 'Central African Republic' in missing_pop_countries:
        car_pop = population_melted[population_melted['Country'].str.contains('Central African', case=False)]
        print("\nPopulation data for Central African Republic:")
        print(car_pop[['Country', 'Year', 'Population']].head())
        
        # Direct manual fix for Central African Republic
        for year in range(1990, 2020):
            car_pop_year = car_pop[car_pop['Year'] == year]
            if not car_pop_year.empty:
                pop_value = car_pop_year['Population'].values[0]
                merged.loc[(merged['Country'] == 'Central African Republic') & 
                           (merged['Year'] == year), 'Population'] = pop_value

# Calculate total consumption (domestic + imports)
merged['Total_Consumption'] = merged['Domestic_Consumption'].fillna(0) + merged['Import_Consumption'].fillna(0)

# Replace zero consumption with NaN for proper calculation
merged.loc[merged['Total_Consumption'] == 0, 'Total_Consumption'] = np.nan

# Calculate per capita consumption (kg per person)
merged['Consumption_Per_Capita_kg'] = merged['Total_Consumption'] / merged['Population']

# Also calculate in grams per person per year
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

# Check specifically for Central African Republic data
car_data = merged_final[merged_final['Country'] == 'Central African Republic']
print(f"\nCentral African Republic data points: {len(car_data)}")
if len(car_data) > 0:
    print("Sample of Central African Republic data:")
    print(car_data[['Year', 'Population', 'Total_Consumption', 'Consumption_Per_Capita_kg']].head())

# Save to CSV
merged_final.to_csv('Coffee_consumption_per_capita.csv', index=False)

print("\nDataset created successfully!")
print(f"Total rows: {len(merged_final)}")
print(f"Countries: {merged_final['Country'].nunique()}")
print(f"Year range: {merged_final['Year'].min()} - {merged_final['Year'].max()}")

# Create summary statistics
summary = merged_final.groupby('Country').agg({
    'Consumption_Per_Capita_kg': ['mean', 'min', 'max'],
    'Total_Consumption': ['mean', 'sum'],
    'Year': ['min', 'max']
}).round(4)
summary.to_csv('Coffee_consumption_summary.csv')
print("\nSummary statistics saved to 'Coffee_consumption_summary.csv'")