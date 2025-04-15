import os
import pandas as pd
import json

def preprocess():
    df_combined = pd.DataFrame()
    
    
    df_read = load_reader_dataset()
    df_sug = load_mySugr_dataset()
    df_fit = load_fitbit_dataset()
    df_stress = load_stressdata()

    df_combined = pd.concat([df_combined, df_read], ignore_index=True)
    df_combined = pd.concat([df_combined, df_sug], ignore_index=True)
    df_combined = pd.concat([df_combined, df_fit], ignore_index=True)
    df_combined = pd.concat([df_combined, df_stress], ignore_index=True)

    print(df_combined.tail())
    df_combined.to_csv('preprocessing.csv',sep='\t', index=False )

    return df_combined


def divide(df):
    # SLICE: 24 HOURS
    end_time = df['Time'].max() #finish time is this precise moment
    start_time = end_time - pd.Timedelta(hours=24)
    df_24h = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)].dropna(subset=['Glucose'])


    #SLICE: 48 hours
    start_48 = end_time - pd.Timedelta(hours=48)
    df_48 = df[(df['Time']>= start_48) & (df['Time'] <= end_time)].dropna(subset=['Glucose'])

    # Weekly slices (let’s say last 4 weeks)
    weekly_slices = []
    for i in range(4):
        end = end_time - pd.Timedelta(weeks=i)
        start = end - pd.Timedelta(weeks=1)
        df_week = df[(df['Time'] >= start) & (df['Time'] < end)].dropna(subset=['Glucose'])
        weekly_slices.append((f"Week of {start.date()}", df_week))

    return df_24h,df_48,weekly_slices


def load_reader_dataset():
        # Specify the path for reader data
        reader_data = "C:/Users/emmxc/OneDrive/Escritorio/FinalProjectThesis/data/reader_data"
        exports = [os.path.join(reader_data, export) for export in os.listdir(reader_data)]
        exports.sort(reverse=False)

        df = pd.read_csv(exports[0], sep="\t")
        for export in exports[1:]:
            df = pd.concat([df, pd.read_csv(export, sep="\t")])

        # Exports usually overlap, so drop the duplicates
        df.drop_duplicates(inplace=True)

        # Dropping columns that are not needed
        df.drop(['Non-numeric Food', 'Non-numeric Long-Acting Insulin','Strip Glucose (mmol/L)','Scan Glucose (mmol/L)','Previous Time', 'Updated Time', 'Non-numeric Rapid-Acting Insulin',
                'Notes', 'Ketone (mmol/L)', 'User Change Insulin (units)', 'Record Type','Correction Insulin (units)','Carbohydrates (grams)', 'ID', 'Meal Insulin (units)'],
                axis=1, inplace=True)

        df.rename(columns={'Rapid-Acting Insulin (units)': 'Rapid Insulin',
                        'Long-Acting Insulin (units)': 'Long Insulin'},
                inplace=True)

        df['Time'] = pd.to_datetime(df['Time'], format="%Y/%m/%d %H:%M")
        df.sort_values(by='Time', inplace=True)

        # Only considering Historical Glucose (reliable 15min measurements) - we're not using Scan Glucose column
        df.rename(columns={'Historic Glucose (mmol/L)': 'Glucose'}, inplace=True)

        return df


def load_mySugr_dataset():
    mySugr_data = "C:/Users/emmxc/OneDrive/Escritorio/FinalProjectThesis/data/mySugr_data/2022_01_09-2022_04_25_export.csv"
    mysugr_df = pd.read_csv(mySugr_data, sep=",")

    # Keeping only the relevant columns
    mysugr_df = mysugr_df[['Date', 'Time', 'Meal Carbohydrates (Grams, Factor 1)']]

    mysugr_df.rename(columns={'Meal Carbohydrates (Grams, Factor 1)': 'Carbohydrates'}, inplace=True)

    mysugr_df["Time"] = pd.to_datetime(mysugr_df["Date"] + " " + mysugr_df["Time"], format="%b %d, %Y %I:%M:%S %p")
    mysugr_df.sort_values(by='Time', inplace=True)
    mysugr_df.drop(['Date'], axis=1, inplace=True)


    return mysugr_df


def read_fitbit_json_export(export_file, export_type):
    with open(export_file, "r") as f:
        j = json.load(f)
    df_read = pd.json_normalize(j)
    df_read["dateTime"] = pd.to_datetime(df_read["dateTime"], format="%m/%d/%y %H:%M:%S")

    if export_type == "heart":
        df_read.rename(columns={"value.bpm": "bpm"}, inplace=True)
        df_read.drop("value.confidence", axis=1, inplace=True)
    elif export_type == "calories":
        df_read.rename(columns={"value": "calories"}, inplace=True)
        df_read["calories"] = df_read["calories"].astype(float)
    elif export_type == "distance":
        df_read.rename(columns={"value": "distance"}, inplace=True)
        df_read["distance"] = df_read["distance"].astype(int)
        # Convert from centimeters to meters
        df_read["distance"] = df_read["distance"] / 100
    else:
        raise Exception("Export type not recognized")
    
    return df_read


def load_fitbit_dataset():
    fitbit_data = "C:/Users/emmxc/OneDrive/Escritorio/FinalProjectThesis/data/fitbit_data/2022_04_25_all_time_export/Physical Activity"

    calories_exports = sorted([os.path.join(fitbit_data, export) for export in os.listdir(fitbit_data) if "calories" in export])
    distance_exports = sorted([os.path.join(fitbit_data, export) for export in os.listdir(fitbit_data) if "distance" in export])
    heart_rate_exports = sorted([os.path.join(fitbit_data, export) for export in os.listdir(fitbit_data) if "heart_rate-" in export and not "resting" in export])

    df_fitbit = read_fitbit_json_export(calories_exports[0], "calories")
    for export in calories_exports[1:]:
        df_fitbit = pd.concat([df_fitbit, read_fitbit_json_export(export, "calories")], ignore_index=True)
    for export in distance_exports:
        df_fitbit = pd.concat([df_fitbit, read_fitbit_json_export(export, "distance")], ignore_index=True)
    for export in heart_rate_exports:
        df_fitbit = pd.concat([df_fitbit, read_fitbit_json_export(export, "heart")], ignore_index=True)

    # Change to 1 minute frequency
    df_fitbit = df_fitbit.set_index('dateTime').resample('1T').agg(
        {'bpm': pd.Series.mean, 'distance': pd.Series.sum, 'calories': pd.Series.sum}).reset_index()

    df_fitbit.rename(columns={"dateTime": "Time"}, inplace=True)
    df_fitbit.sort_values(by='Time', inplace=True)

    return df_fitbit


def load_stressdata():
    stress_data = "C:/Users/emmxc/OneDrive/Escritorio/FinalProjectThesis/data/fitbit_data/2022_04_25_all_time_export/Stress/Stress Score.csv"
    stress_df = pd.read_csv(stress_data, sep=",")
    stress_df = stress_df[['UPDATED_AT', 'STRESS_SCORE']]

    stress_df.rename(columns={'STRESS_SCORE': 'Stress'}, inplace=True)

    stress_df['Time'] = stress_df['UPDATED_AT'].str.replace('T', ' ')
    stress_df['Time'] = pd.to_datetime(stress_df['Time'], format='%Y-%m-%d %H:%M:%S.%f')

    stress_df.drop(['UPDATED_AT'], axis=1, inplace=True)
    stress_df.sort_values(by='Time', inplace=True)


    return stress_df