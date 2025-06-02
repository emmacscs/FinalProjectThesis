import streamlit as st
import pandas as pd
import plots, otherstats, explainerplot  

# Global Style Function
def apply_global_styles():
    st.markdown("""
        <style>
        html, body, [class*="css"]  { font-size: 20px !important; }
        .stButton>button { font-size: 18px !important; padding: 0.75em 1.5em; }
        .stSelectbox label, .stRadio label, .stTextInput label { font-size: 18px !important; }
        .css-1d391kg { zoom: 2.0; }
        </style>
    """, unsafe_allow_html=True)


def format_explanation_from_df(xai_detailed_df):
    explanation_shap = "🧠 **Explanation of Hyperglycemia Risk:**\n"
    
    # Helper function for iterating over rows
    def get_explanation_for_prediction(prediction_type):
        rows = xai_detailed_df[xai_detailed_df['Prediction'] == prediction_type]
        explanation = ""
        for _, row in rows.iterrows():
            explanation += f"  • {row['Feature']}: SHAP value {row['SHAP_value']} — {row['Explanation']}\n"
        return explanation

    # Adding hyperglycemia and hypoglycemia explanations
    explanation_shap += get_explanation_for_prediction('Hyperglycemia')
    explanation_shap += "\n🧠 **Explanation of Hypoglycemia Risk:**\n"
    explanation_shap += get_explanation_for_prediction('Hypoglycemia')

    # Add general/contextual insights at the end
    general_rows = xai_detailed_df[xai_detailed_df['Prediction'] == 'General']
    if not general_rows.empty:
        explanation_shap += "\n**Hidden relationship in the explanation:**\n"
        explanation_shap += "\n".join([f"  • {row['Explanation']}" for _, row in general_rows.iterrows()])
    
    return explanation_shap

# Initialize Streamlit page
st.set_page_config(page_title="Glucose Predictor", layout="centered")
apply_global_styles()

# Load DataFrames
df = pd.read_csv("kinetics.csv", sep="\t")
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')

df_XAI = pd.read_csv("XAI_detailed.csv", sep=",")
df_XAI['Time'] = pd.to_datetime(df_XAI['Time'], format='%Y-%m-%d %H:%M:%S')

df_summary = pd.read_csv("XAI_summary.csv", sep=",")
df_summary['Time'] = pd.to_datetime(df_summary['Time'], format='%Y-%m-%d %H:%M:%S')

# Prediction probabilities taken from the classifier notebook, future improvement should be updates as refreshing the page not taken from the notebook 
hyper_pred = {15: 0.84, 30: 0.72, 60: 0.84, 120: 0.65}
hypo_pred = {15: 0.12, 30: 0.08, 60: 0.10, 120: 0.02}

# Current timestamp (Here we just show the interface at a given time, but future research should update it through time)
datestamp = "2021-12-28 23:45:00"
st.title("🌿 Glucose Predictor")
st.markdown(f"**Current Time:** {datestamp}")

# Display prediction probabilities for selected time intervals
time_intervals = [15, 30, 60, 120]
for interval in time_intervals:
    with st.expander(f"🔮 {interval}-minute Prediction"):
        st.markdown(f"**Hyperglycemia Probability:** {hyper_pred[interval]:.0%}")
        st.markdown(f"**Hypoglycemia Probability:** {hypo_pred[interval]:.0%}")

# Filter and display recent days
recent_days = df['Time'].dt.normalize().drop_duplicates().sort_values(ascending=False)
latest_day = df['Time'].dt.normalize().max()
filtered_days = recent_days[recent_days < latest_day]

selected_day = st.selectbox(
    "Choose a day to explore",
    options=[None] + list(filtered_days),
    format_func=lambda x: "Last 24 Hours" if x is None else x.strftime("%A, %d %B")
)

# Plot Glucose Time Series
st.markdown("### 📈 Glucose Time Series")
fig = plots.plotGlucose(df, selected_day=selected_day)
st.plotly_chart(fig, use_container_width=True)

# Model Explanation
st.markdown("### 💡 Model Explanation")
explanation_text = format_explanation_from_df(df_XAI)
st.code(explanation_text)

# Insight Section with Explainer Graph
st.markdown("---")
if st.button("Insight into Explanation"):
    st.markdown("###  Explainer Graph")
    date_x = pd.to_datetime("2021-12-28 20:45:00")
    date_y = pd.to_datetime("2021-12-28 23:45:00")
    fig_expl = explainerplot.plotExplainer(df, date_x, date_y)
    st.plotly_chart(fig_expl, use_container_width=True)

# Other Stats Section
st.markdown("---")
if st.button("📊 Show Other Stats"):
    for stat_type, plot_func in [
        ("🥗 Carbohydrates", otherstats.plotCarbs),
        ("💉 Insulin", otherstats.plotInsulin),
        ("🏃 Exercise (Calories & Distance)", otherstats.plotExercise),
        ("❤️ Heart Rate (BPM)", otherstats.plotBPM)
    ]:
        st.markdown(f"### {stat_type}")
        st.plotly_chart(plot_func(df, selected_day), use_container_width=True)