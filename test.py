import preprocessing, harmonizing, kinetics

df1=preprocessing.preprocess()  # Load data
df2=harmonizing.harmonize(df1)  # Harmonize data
df3=kinetics.run(df2)  # Run kinetics calculations
