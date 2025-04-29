import json
from flask import Flask, render_template
import plotly.io as pio
import plots, otherstats
import pandas as pd

app = Flask(__name__)

data = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/final.csv"
df = pd.read_csv(data, sep="\t")
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
df_24h,df_48h,weekly_slices = plots.makeTime(df)


@app.route('/')
def index():

    # Generate the plots
    fig = plots.plotGlucose(df,df_24h,df_48h,weekly_slices)
    fig2 = otherstats.plotCarbs(df,df_24h,df_48h,weekly_slices)
    fig3 = otherstats.plotInsulin(df,df_24h,df_48h,weekly_slices)
    fig4 = otherstats.plotExercise(df,df_24h,df_48h,weekly_slices)
    fig5 = otherstats.plotBPM(df,df_24h,df_48h,weekly_slices)
    # Convert figures to HTML for rendering in template
    graph_html = pio.to_html(fig, full_html=False)
    carbs_html = pio.to_html(fig2, full_html=False)
    insulin_html = pio.to_html(fig3, full_html=False)
    exercise_html = pio.to_html(fig4, full_html=False)
    bpm_html = pio.to_html(fig5, full_html=False)


    data2 = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/predicted_glucose_and_shap.csv"
    shap_path = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/shap_values_per_interval.csv"
    df2 = pd.read_csv(data2)
    df_shap = pd.read_csv(shap_path)
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    
    # Now ensure that the Timestamp is set as an index, if you want to filter by timestamp
    df2.set_index('Timestamp', inplace=True)

    # Check if the desired timestamp exists in the DataFrame
    timestamp = '2022-04-25 21:00:00'

    # Convert to datetime to avoid any mismatches
    timestamp = pd.to_datetime(timestamp)

    # Extract the necessary values for rendering
    predicted_glucose = df2['Predicted Glucose'].loc[timestamp]
    predicted_class = df2['Predicted Class'].loc[timestamp]
    predicted_probability_hyper = df2['Predicted Probability Hyper'].loc[timestamp]
    predicted_probability_hypo = df2['Predicted Probability Hypo'].loc[timestamp]
   
    
    # Calculate probabilities for hyperglycemia and hypoglycemia from model's prediction
    hyperglycemia_prob = predicted_probability_hyper  # Model's probability for hyperglycemia (class 1)
    hypoglycemia_prob = predicted_probability_hypo  # Complement for hypoglycemia (class 0)
  
    # Pass the DataFrame and report to the template
    return render_template('index.html',graph_html=graph_html,carbs_html=carbs_html,insulin_html=insulin_html,exercise_html=exercise_html,bpm_html=bpm_html,
                           predicted_glucose=predicted_glucose, 
                           hyperglycemia_prob=hyperglycemia_prob,
                           hypoglycemia_prob=hypoglycemia_prob)


@app.route('/profile.html')
def profile():

    return render_template('profile.html')


@app.route('/index.html')
def index2():

    # Generate the plots
    fig = plots.plotGlucose(df,df_24h,df_48h,weekly_slices)
    fig2 = otherstats.plotCarbs(df,df_24h,df_48h,weekly_slices)
    fig3 = otherstats.plotInsulin(df,df_24h,df_48h,weekly_slices)
    fig4 = otherstats.plotExercise(df,df_24h,df_48h,weekly_slices)
    fig5 = otherstats.plotBPM(df,df_24h,df_48h,weekly_slices)
    # Convert figures to HTML for rendering in template
    graph_html = pio.to_html(fig, full_html=False)
    carbs_html = pio.to_html(fig2, full_html=False)
    insulin_html = pio.to_html(fig3, full_html=False)
    exercise_html = pio.to_html(fig4, full_html=False)
    bpm_html = pio.to_html(fig5, full_html=False)


    data2 = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/predicted_glucose_and_shap.csv"
    shap_path = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/shap_values_per_interval.csv"
    df2 = pd.read_csv(data2)
    df_shap = pd.read_csv(shap_path)
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    
    # Now ensure that the Timestamp is set as an index, if you want to filter by timestamp
    df2.set_index('Timestamp', inplace=True)

    # Check if the desired timestamp exists in the DataFrame
    timestamp = '2022-04-25 21:00:00'

    # Convert to datetime to avoid any mismatches
    timestamp = pd.to_datetime(timestamp)

    # Extract the necessary values for rendering
    predicted_glucose = df2['Predicted Glucose'].loc[timestamp]
    predicted_class = df2['Predicted Class'].loc[timestamp]
    predicted_probability_hyper = df2['Predicted Probability Hyper'].loc[timestamp]
    predicted_probability_hypo = df2['Predicted Probability Hypo'].loc[timestamp]

  
    # Create a new DataFrame for extracted hyper and hypo values
    intervals = []
    hyper_values = []
    hypo_values = []

    for index, row in df.iterrows():
        interval = row['Interval']
        shap_values = plots.parse_shap_values(row['SHAP Values'])
        
        for feature_idx, (hyper, hypo) in enumerate(shap_values):
            intervals.append(interval)
            hyper_values.append(hyper)
            hypo_values.append(hypo)

    # Create a new DataFrame with the extracted values
    shap_df = pd.DataFrame({
        "Interval": intervals,
        "Feature Index": [i for i in range(len(intervals))],  # A unique index for each feature per interval
        "Hyper Value": hyper_values,
        "Hypo Value": hypo_values
    })

    # You can generate HTML from this DataFrame using pandas
    html_shaptable = shap_df.to_html(classes="table", index=False)
    
    
    # Calculate probabilities for hyperglycemia and hypoglycemia from model's prediction
    hyperglycemia_prob = predicted_probability_hyper  # Model's probability for hyperglycemia (class 1)
    hypoglycemia_prob = predicted_probability_hypo  # Complement for hypoglycemia (class 0)
  
    # Pass the DataFrame and report to the template
    return render_template('index.html',graph_html=graph_html,carbs_html=carbs_html,insulin_html=insulin_html,exercise_html=exercise_html,bpm_html=bpm_html,
                           predicted_glucose=predicted_glucose, 
                           hyperglycemia_prob=hyperglycemia_prob,
                           html_shaptable=html_shaptable,
                           hypoglycemia_prob=hypoglycemia_prob)


@app.route('/explorer.html')
def explore():
    
    return render_template('explorer.html')

if __name__ == '__main__':
    app.run(debug=True)


