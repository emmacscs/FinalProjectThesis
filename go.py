import pandas as pd

data = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/insulin_carbs_absorption.csv"
# Read the CSV
df = pd.read_csv(data, sep="\t")



print(df.head())