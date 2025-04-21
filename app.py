from flask import Flask, render_template
import plotly.io as pio
import plots
import os, json
import pandas as pd

app = Flask(__name__)


@app.route('/')
def index():
    data = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/insulin_carbs_absorption.csv"
    df = pd.read_csv(data, sep="\t")
    df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
    df_24h,df_48h,weekly_slices = plots.makeTime(df)

    # Generate the plots
    fig = plots.plotGlucose(df,df_24h,df_48h,weekly_slices)
    # Convert figures to HTML for rendering in template
    graph_html = pio.to_html(fig, full_html=False)

    # Pass the DataFrame and report to the template
    return render_template('index.html',graph_html=graph_html)

@app.route('/profile.html')
def profile():

    data = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/insulin_carbs_absorption.csv"
    df = pd.read_csv(data, sep="\t")
    df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
    df_24h,df_48h,weekly_slices = plots.makeTime(df)


    return render_template('profile.html')


@app.route('/index.html')
def index2():
    data = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/insulin_carbs_absorption.csv"
    df = pd.read_csv(data, sep="\t")
    df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
    df_24h,df_48h,weekly_slices = plots.makeTime(df)

    # Generate the plots
    fig = plots.plotGlucose(df,df_24h,df_48h,weekly_slices)
    # Convert figures to HTML for rendering in template
    graph_html = pio.to_html(fig, full_html=False)


    return render_template('index.html', graph_html=graph_html)


@app.route('/explorer.html')
def explore():
    data = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/insulin_carbs_absorption.csv"
    df = pd.read_csv(data, sep="\t")
    df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
    df_24h,df_48h,weekly_slices = plots.makeTime(df)

    return render_template('explorer.html')

if __name__ == '__main__':
    app.run(debug=True)
