# import pandas as pd
# import numpy as np

# # csv_data = pd.read_csv('../data/Leopards vervets and baboons in Laikipia Kenya_part-gps.csv')
# # data_length = csv_data.shape
# # print(csv_data.columns)
# # print(data_length)

# # Load the dataset
# csv_data = pd.read_csv('../data/leopards/Leopards_vervets_and_baboons_Laikipia_Kenya_part_gps.csv')

# # 1. Print general information about the dataset
# print("Dataset Info:")
# print(csv_data.info())
# print("\nDataset Shape (Rows, Columns):", csv_data.shape)

# # 2. Check for NaN values
# print("\nNaN Values Count per Column:")
# print(csv_data.isna().sum())
# print("\nTotal NaN Values in Dataset:", csv_data.isna().sum().sum())

# # 4. Check for duplicate rows
# duplicates = csv_data.duplicated().sum()
# print("\nDuplicate Rows in Dataset:", duplicates)
# if duplicates > 0:
#     print("Duplicate Rows:\n", csv_data[csv_data.duplicated()])

# # 5. Summary statistics to spot outliers or unusual values
# print("\nSummary Statistics for Numerical Columns:")
# print(csv_data.describe())

# # 6. Check for non-numeric entries in numeric columns
# for col in csv_data.select_dtypes(include=[np.number]).columns:
#     non_numeric = csv_data[col].apply(lambda x: isinstance(x, str))
#     if non_numeric.any():
#         print(f"\nNon-numeric values in numeric column '{col}':", csv_data[non_numeric][col])

import pandas as pd

# Load the dataset
csv_data = pd.read_csv('../data/leopards/Leopards_vervets_and_baboons_Laikipia_Kenya_part_gps.csv')

# Print original shape
print("Original Dataset Shape:", csv_data.shape)

# Delete rows where 'location-lat' or 'location-long' have NaN values
csv_data = csv_data.dropna(subset=['location-lat', 'location-long'])

# Print new shape
print("Dataset Shape After Deleting NaN Rows:", csv_data.shape)

# Verify no NaNs remain in 'location-lat' or 'location-long'
print("\nNaN Values in 'location-lat':", csv_data['location-lat'].isna().sum())
print("NaN Values in 'location-long':", csv_data['location-long'].isna().sum())

# Optionally, save the cleaned dataset to a new CSV file
csv_data.to_csv('../data/cleaned_gps_data.csv', index=False)
print("\nCleaned dataset saved to '../data/cleaned_gps_data.csv'")