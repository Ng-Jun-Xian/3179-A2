import pandas as pd

# Read the export data
export_df = pd.read_csv('Coffee_export.csv')

# Read the import data
import_df = pd.read_csv('Coffee_import.csv')

# Filter out invalid data (e.g., -2147483648 values in Brazil's data)
export_df['Total_export'] = export_df['Total_export'].apply(lambda x: x if x > 0 else None)

# Get top 10 exporters
top_exporters = export_df.sort_values('Total_export', ascending=False).head(10)
print("Top 10 Coffee Exporters:")
for idx, (country, total) in enumerate(zip(top_exporters['Country'], top_exporters['Total_export']), 1):
    print(f"{idx}. {country}: {total:,.0f} kg")

print("\n" + "-"*50 + "\n")

# Get top 10 importers
top_importers = import_df.sort_values('Total_import', ascending=False).head(10)
print("Top 10 Coffee Importers:")
for idx, (country, total) in enumerate(zip(top_importers['Country'], top_importers['Total_import']), 1):
    print(f"{idx}. {country}: {total:,.0f} kg")