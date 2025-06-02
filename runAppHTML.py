from flask import Flask, render_template_string, request
import pandas as pd
import plotly.io as pio
import plots
import otherstats
import explainerplot
"""
THIS FILE:
Since the app can only be deployed through my streamlit github account this file is a version of the interface through html
so anyone can run it.
However, it does not have the buttons or exactly the same look as the streamlit app since it is less styled.
In the HTML you can only find the explainer graph at the end instead of through a button like streamlit.
In the rpeort, the screenshots are of the deployment through streamlit that includes buttons, interactions and a nices looking-interface overall
"""
app = Flask(__name__)

df = pd.read_csv("kinetics.csv", sep="\t")
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')

df_XAI = pd.read_csv("XAI_detailed.csv")
df_XAI['Time'] = pd.to_datetime(df_XAI['Time'], format='%Y-%m-%d %H:%M:%S')

hyper_pred = {15: 0.84, 30: 0.72, 60: 0.84, 120: 0.65}
hypo_pred = {15: 0.12, 30: 0.08, 60: 0.10, 120: 0.02}

datestamp = "2021-12-28 23:45:00"

def format_explanation_from_df_html(xai_detailed_df):
    html = '<h3>🧠 Explanation of Hyperglycemia Risk:</h3><ul>'
    hyper_rows = xai_detailed_df[xai_detailed_df['Prediction'] == 'Hyperglycemia']
    for _, row in hyper_rows.iterrows():
        html += f"<li><b>{row['Feature']}</b>: SHAP value {row['SHAP_value']} — {row['Explanation']}</li>"
    html += "</ul>"
    html += '<h3>🧠 Explanation of Hypoglycemia Risk:</h3><ul>'
    hypo_rows = xai_detailed_df[xai_detailed_df['Prediction'] == 'Hypoglycemia']
    for _, row in hypo_rows.iterrows():
        html += f"<li><b>{row['Feature']}</b>: SHAP value {row['SHAP_value']} — {row['Explanation']}</li>"
    html += "</ul>"
    general_rows = xai_detailed_df[xai_detailed_df['Prediction'] == 'General']
    if not general_rows.empty:
        html += "<h3>💡 Hidden relationship in the explanation:</h3><ul>"
        for _, row in general_rows.iterrows():
            html += f"<li>{row['Explanation']}</li>"
        html += "</ul>"
    return html

@app.route("/", methods=["GET", "POST"])
def home():
    selected_day_str = request.form.get("selected_day", None)
    recent_days = df['Time'].dt.normalize().drop_duplicates().sort_values(ascending=False)
    latest_day = df['Time'].dt.normalize().max()
    filtered_days = recent_days[recent_days < latest_day]
    selected_day = None
    if selected_day_str and selected_day_str != "None":
        selected_day = pd.to_datetime(selected_day_str)
    explanation_html = format_explanation_from_df_html(df_XAI)
    fig_glucose = plots.plotGlucose(df, selected_day=selected_day)
    glucose_html = pio.to_html(fig_glucose, full_html=False, include_plotlyjs='cdn')
    other_plots = []
    for stat_type, plot_func in [
        ("🥗 Carbohydrates", otherstats.plotCarbs),
        ("💉 Insulin", otherstats.plotInsulin),
        ("🏃 Exercise (Calories & Distance)", otherstats.plotExercise),
        ("❤️ Heart Rate (BPM)", otherstats.plotBPM)
    ]:
        fig = plot_func(df, selected_day)
        fig_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        other_plots.append((stat_type, fig_html))
    date_x = pd.to_datetime("2021-12-28 20:45:00")
    date_y = pd.to_datetime("2021-12-28 23:45:00")
    fig_expl = explainerplot.plotExplainer(df, date_x, date_y)
    explainer_html = pio.to_html(fig_expl, full_html=False, include_plotlyjs=False)

    return render_template_string("""
    <html>
    <head>
      <title>Glucose Predictor</title>
      <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
      <style>
        body { font-family: Arial, sans-serif; font-size: 18px; margin: 2rem; }
        h1 { color: #2a7ae2; }
        ul { padding-left: 20px; }
        li { margin-bottom: 0.5rem; }
        .section { margin-bottom: 3rem; }
        select { font-size: 18px; padding: 0.5em 1em; }
        .plotly-graph-div { max-width: 900px; margin-bottom: 3rem; }
      </style>
    </head>
    <body>
      <h1>🌿 Glucose Predictor</h1>
      <p><b>Current Time:</b> {{ datestamp }}</p>

      <div class="section">
        <h2>🔮 Prediction Probabilities</h2>
        <ul>
        {% for interval in time_intervals %}
          <li><b>{{interval}}-minute Prediction</b>: Hyperglycemia {{ (hyper_pred[interval]*100)|round(0) }}%, Hypoglycemia {{ (hypo_pred[interval]*100)|round(0) }}%</li>
        {% endfor %}
        </ul>
      </div>

      <div class="section">
        <form method="post">
          <label for="selected_day">Choose a day to explore:</label>
          <select name="selected_day" id="selected_day" onchange="this.form.submit()">
            <option value="None" {% if not selected_day %}selected{% endif %}>Last 24 Hours</option>
            {% for day in filtered_days %}
            <option value="{{day.strftime('%Y-%m-%d')}}" {% if selected_day and day == selected_day %}selected{% endif %}>{{day.strftime('%A, %d %B')}}</option>
            {% endfor %}
          </select>
        </form>
      </div>

      <div class="section">
        <h2>💡 Model Explanation</h2>
        {{ explanation_html|safe }}
      </div>

      <div class="section">
        <h2>📈 Glucose Time Series</h2>
        {{ glucose_html|safe }}
      </div>

      <div class="section">
        <h2>📊 Other Stats</h2>
        {% for stat_type, fig_html in other_plots %}
          <h3>{{ stat_type }}</h3>
          {{ fig_html|safe }}
        {% endfor %}
      </div>

      <div class="section">
        <h2>🔍 Explainer Graph</h2>
        {{ explainer_html|safe }}
      </div>
    </body>
    </html>
    """,
    datestamp=datestamp,
    time_intervals=[15,30,60,120],
    hyper_pred=hyper_pred,
    hypo_pred=hypo_pred,
    filtered_days=filtered_days,
    selected_day=selected_day,
    explanation_html=explanation_html,
    glucose_html=glucose_html,
    other_plots=other_plots,
    explainer_html=explainer_html
    )

if __name__ == "__main__":
    app.run(debug=True)
