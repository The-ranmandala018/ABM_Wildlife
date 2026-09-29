import pandas as pd
import plotly.express as px

# Read the Excel file into a DataFrame
# df = pd.read_excel("..\\Data_old\\Clustered Statistics\\Clustered Probability Matrices\\st\\ProbabilityMatrix_allDays_st_cluster0.xlsx")
df = pd.read_excel("../Results/Clustered Probability Matrices/st/ProbabilityMatrix_allDays_st_cluster0.xlsx")

# Set the index of the DataFrame to 'Locations'
df.set_index('Locations', inplace=True)

# Create a new DataFrame with 'Home', 'School', and 'Other'
df_new = pd.DataFrame(columns=df.columns)  # Ensure columns are defined
df_new.loc['Home'] = df.loc['Home']
df_new.loc['School'] = df.loc['School']
df_new.loc['Other'] = df.drop(['Home', 'School']).sum()

# Transpose the DataFrame for plotting
df_new = df_new.T
df_new.reset_index(inplace=True)
df_new.rename(columns={'index': 'Time'}, inplace=True)

# Plot the new DataFrame using plotly
fig = px.line(df_new, x='Time', y=df_new.columns[1:], title='Location Values Over Time', labels={'value': 'Probability', 'variable': 'Locations'})
fig.show()