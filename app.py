from flask import Flask, jsonify, render_template, request
import plotly.io as pio
import plots
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
    fig2 = plots.plotCarbs(df,df_24h,df_48h,weekly_slices)
    fig3 = plots.plotInsulin(df,df_24h,df_48h,weekly_slices)
    fig4 = plots.plotGlucose(df,df_24h,df_48h,weekly_slices)
    fig5 = plots.plotBPM(df,df_24h,df_48h,weekly_slices)
    # Convert figures to HTML for rendering in template
    graph_html = pio.to_html(fig, full_html=False)
    carbs_html = pio.to_html(fig2, full_html=False)
    insulin_html = pio.to_html(fig3, full_html=False)
    exercise_html = pio.to_html(fig4, full_html=False)
    bpm_html = pio.to_html(fig5, full_html=False)

    
    # Pass the DataFrame and report to the template
    return render_template('index.html',graph_html=graph_html,carbs_html=carbs_html,insulin_html=insulin_html,exercise_html=exercise_html,bpm_html=bpm_html)


@app.route('/profile.html')
def profile():

    return render_template('profile.html')


@app.route('/index.html')
def index2():

    # Generate the plots
    fig = plots.plotGlucose(df,df_24h,df_48h,weekly_slices)
    # Convert figures to HTML for rendering in template
    graph_html = pio.to_html(fig, full_html=False)


    return render_template('index.html', graph_html=graph_html)


@app.route('/explorer.html')
def explore():
    
    return render_template('explorer.html')

if __name__ == '__main__':
    app.run(debug=True)
