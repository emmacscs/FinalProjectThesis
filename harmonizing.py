import pandas as pd

def harmonize(df_combined):
    temp = df_combined.copy()

    start_time = "2020-11-02 18:09:00"  # Change this to your starting point
    end_time = temp.index.max()  # Or set your desired end time

    time_range = pd.date_range(start=start_time, end=end_time, freq='15T')
    temp.set_index('Time', inplace=True)

    #  glucose value for each 15-minute period
    df_glu = temp.resample('15T')['Glucose'].mean()

    #Carbohydrates consumption added each 15 minutes period
    df_car = temp.resample('15T')['Carbohydrates'].sum()


    #Rapid Insulin added each 15 minutes
    df_rap = temp.resample('15T')['Rapid Insulin'].sum()

    #Long Insulin added each 15 minutes
    df_long = temp.resample('15T')['Long Insulin'].sum()

    #BPM
    df_bpm = temp.resample('15T')['bpm'].mean()

    #calories
    df_calories = temp.resample('15T')['calories'].sum()

    # Distance 
    df_distance = temp.resample('15T')['distance'].sum()

    #stress
    df_st = temp.resample('15T')['Stress'].sum()

    df_har = pd.DataFrame({
        'Time': df_glu.index,
        'Glucose': df_glu,
        'Carbohydrates': df_car,
        'Rapid Insulin': df_rap,
        'Long Insulin': df_long,
        'BPM': df_bpm,
        'Calories': df_calories,
        'Distance': df_distance,
        'Stress': df_st
    })


    # Save the resulting data to a CSV file
    df_har.to_csv( 'harmonized_data.csv', sep='\t', index=False)

    return df_har