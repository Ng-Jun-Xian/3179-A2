import pandas as pd
import os
import re

# Function to standardize country names based on gdp_cleaned.csv
def standardize_country_names():
    # Read the reference file for country names
    gdp_df = pd.read_csv('gdp_cleaned.csv')
    standard_country_names = gdp_df['Country Name'].tolist()
    country_code_map = dict(zip(gdp_df['Country Name'], gdp_df['Country Code']))
    
    # Create a mapping for inconsistent country names
    country_mapping = {
        # Standardize country names
        'Bolivia (Plurinational State of)': 'Bolivia',
        'United States of America': 'United States',
        'Russian Federation': 'Russia',
        'United Republic of Tanzania': 'Tanzania',
        'Viet Nam': 'Vietnam',
        'Republic of Korea': 'South Korea',
        'Democratic People\'s Republic of Korea': 'North Korea',
        'Türkiye': 'Turkey',
        'Côte d\'Ivoire': 'Côte d\'Ivoire',
        'Dem. Rep. Congo': 'Dem. Rep. Congo',
        'Democratic Republic of Congo': 'Dem. Rep. Congo',
        'Congo': 'Congo',
        'Bosnia and Herzegovina': 'Bosnia and Herz.',
        'Bosnia and Herz': 'Bosnia and Herz.',
        'Dominican Rep.': 'Dominican Rep.',
        'Dominican Republic': 'Dominican Rep.',
        'Central African Rep.': 'Central African Rep.',
        'Central African Republic': 'Central African Rep.',
        'Eq. Guinea': 'Eq. Guinea',
        'Equatorial Guinea': 'Eq. Guinea',
        'Timor-Leste': 'Timor-Leste',
        'Hong Kong SAR, China': 'Hong Kong',
        'Brunei Darussalam': 'Brunei',
        'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
        'Venezuela (Bolivarian Republic of)': 'Venezuela',
        'Iran (Islamic Republic of)': 'Iran',
        'Republic of Moldova': 'Moldova',
        'Lao People\'s Democratic Republic': 'Lao PDR',
        'Cabo Verde': 'Cabo Verde',
        'Cape Verde': 'Cabo Verde',
        'Myanmar': 'Myanmar',
        'Burma': 'Myanmar',
        'Syria': 'Syrian Arab Rep.',
        'Syrian Arab Republic': 'Syrian Arab Rep.',
        'North Macedonia': 'North Macedonia',
        'Macedonia': 'North Macedonia',
        'TFYR Macedonia': 'North Macedonia',
        'Czechia': 'Czechia',
        'Czech Republic': 'Czechia',
        'Eswatini': 'Eswatini',
        'Swaziland': 'Eswatini',
        'Kyrgyz Republic': 'Kyrgyzstan',
        'Saint Lucia': 'St. Lucia',
        'Saint Kitts and Nevis': 'St. Kitts and Nevis',
        'Saint Vincent and the Grenadines': 'St. Vincent and the Grenadines'
    }
    
    # Get all CSV files in the directory
    csv_files = [file for file in os.listdir('.') if file.endswith('.csv') and file != 'gdp_cleaned.csv']
    
    for file in csv_files:
        print(f"Processing {file}...")
        try:
            # Special handling for World Bank API files
            if file.startswith('API_'):
                # These files have a specific format with metadata at the top
                # Read the first few rows to check structure
                with open(file, 'r', encoding='utf-8') as f:
                    header_rows = [next(f) for _ in range(5)]
                
                # Skip the header rows for World Bank data files
                df = pd.read_csv(file, skiprows=4)
            else:
                df = pd.read_csv(file)
            
            # Find the column that contains country names
            country_col = None
            possible_country_cols = ['Country', 'Entity', 'Country Name']
            
            for col in possible_country_cols:
                if col in df.columns:
                    country_col = col
                    break
                    
            if country_col is None:
                # Skip files that don't have country data
                print(f"  No country column found in {file}, skipping...")
                continue
            
            # Make a copy of the original names for logging
            original_names = df[country_col].unique().tolist()
            
            # Apply standardization
            df[country_col] = df[country_col].map(lambda x: country_mapping.get(x, x))
            
            # Log the changes
            new_names = df[country_col].unique().tolist()
            changed_names = {name: country_mapping[name] for name in original_names if name in country_mapping}
            if changed_names:
                print(f"  Changed country names in {file}:")
                for orig, new in changed_names.items():
                    print(f"    {orig} -> {new}")
                    
            # Save the modified file
            df.to_csv(file, index=False)
            print(f"  Saved standardized names to {file}")
            
        except Exception as e:
            print(f"  Error processing {file}: {str(e)}")
    
    print("\nCountry name standardization completed!")

if __name__ == "__main__":
    standardize_country_names()