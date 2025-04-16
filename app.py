from flask import Flask, render_template
import plotly.io as pio
import plots
import os, json
import pandas as pd

app = Flask(__name__)


@app.route('/')
def index():
    data = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/insulin_carbs_absorption.csv"
    df = pd.read_csv(data, sep=",")

    # Generate the plots
    fig = plots.plotGlucose(df)
    fig_car = plots.plotCarbohydrates(df)

    # Convert figures to HTML for rendering in template
    graph_html = pio.to_html(fig, full_html=False)
    graphcar_html = pio.to_html(fig_car, full_html=False)

    return render_template('index.html', graph_html=graph_html,
                           graphcar_html=graphcar_html)

if __name__ == '__main__':
    app.run(debug=True)
