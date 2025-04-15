from flask import Flask, render_template
import plotly.io as pio
import preprocessing, plots, harmonizing, kinetics

app = Flask(__name__)

# Preload data here before the app starts
df = preprocessing.preprocess()
df_24h, df_48h, weekly_slices = preprocessing.divide(df)
df_har = harmonizing.harmonize(df_24h)  # Assuming df_24h is the result from preprocess
df_kinetics = kinetics.run(df_har)
fig = plots.plotGlucose(df,df_24h,df_48h,weekly_slices)
fig_car = plots.plotCarbohydrates(df,df_24h,df_48h,weekly_slices)

@app.route('/')
def index():
    graph_html = pio.to_html(fig, full_html=False)
    graphcar_html = pio.to_html(fig_car,full_html=False)

    return render_template('index.html', graph_html=graph_html,
                           graphcar_html=graphcar_html)
    
if __name__ == '__main__':
    app.run(debug=True)
