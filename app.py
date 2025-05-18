import streamlit as st
import pandas as pd
import datetime
import plots,otherstats,explainerplot  

def apply_global_styles():
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-size: 20px !important;
        }
        .stButton>button {
            font-size: 18px !important;
            padding: 0.75em 1.5em;
        }
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 18px !important;
        }
        .css-1d391kg {
            zoom: 2.0;  /* Slight global zoom */
        }
        </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Glucose Predictor", layout="centered")
apply_global_styles()

df = pd.read_csv("kinetics.csv",sep="\t")
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')

df_XAI = pd.read_csv("XAI_detailed.csv",sep=",")
df_XAI['Time'] = pd.to_datetime(df_XAI['Time'], format='%Y-%m-%d %H:%M:%S')

# Dummy prediction info
datestamp = "2021-12-28 23:45:00"
hyper_prob = 0.84
hypo_prob = 0.12
explanation_gen = ("The high probability of a hyperglycemic episode is due to your behavior in the last two hours.\n"
                   "Most influential factors were:\n"
                   "- insulin\n"
                   "- past glucose levels\n"
                   "- carbohydrates")

hyper_explanations = df_XAI[
    (df_XAI["Prediction"] == "Hyperglycemia") &
    (df_XAI["Explanation"].notna()) &
    (df_XAI["Explanation"].str.contains("Influence"))
]["Explanation"].tolist()

# Add contextual insight if available
general_extras = df_XAI[
    (df_XAI["Prediction"] == "General") &
    (df_XAI["Extra_Explanation"] == "✓ Contextual Insight")
]["Explanation"].tolist()

# Format the explanation text
explanation_shap = "🧠 **Explanation of Hyperglycemia Risk:**\n"
explanation_shap += "The high probability of a hyperglycemic episode is likely due to:\n"

for line in hyper_explanations:
    explanation_shap += f"  • {line}\n"

if general_extras:
    explanation_shap += "\n🔎 **Important Contextual Insights:**\n"
    for insight in general_extras:
        explanation_shap += f"  • {insight}\n"


# App layout
st.title("🌿Glucose Predictor")
st.markdown(f"**Current Time:** {datestamp}")


hyper_pred = {
    30: 0.72,
    60: 0.84,
    120: 0.65
}

hypo_pred = {
    30: 0.05,
    60: 0.10,
    120: 0.02
}

# Time intervals you want to display
time_intervals = [30, 60, 120]

# Display predictions for each interval
for interval in time_intervals:
    with st.expander(f"🔮 {interval}-minute Prediction"):
        st.markdown(f"**Hyperglycemia Probability:** {hyper_pred[interval]:.0%}")
        st.markdown(f"**Hypoglycemia Probability:** {hypo_pred[interval]:.0%}")

# Extract unique recent days (normalized to midnight)
recent_days = df['Time'].dt.normalize().drop_duplicates().sort_values(ascending=False)

# Get the most recent full day
latest_day = df['Time'].dt.normalize().max()

# Exclude it from the dropdown if it's already shown as "Last 24 Hours"
filtered_days = recent_days[recent_days < latest_day]

# Dropdown for day selection
selected_day = st.selectbox(
    "Choose a day to explore",
    options=[None] + list(filtered_days),
    format_func=lambda x: "Last 24 Hours" if x is None else x.strftime("%A, %d %B")
)

# Plot
st.markdown("### 📈 Glucose Time Series")
fig = plots.plotGlucose(df, selected_day=selected_day)
st.plotly_chart(fig, use_container_width=True)


# Explanation
st.markdown("### 💡 Model Explanation")
st.code(explanation_gen)

# Insight Section
st.markdown("---")
if st.button("Insight into Explanation"):
    st.markdown("###  Explainer Graph")

    # Define the 2-hour window for the explainer (you can make this dynamic later)
    date_x = pd.to_datetime("2021-12-28 20:45:00")
    date_y = pd.to_datetime("2021-12-28 23:45:00")

    fig_expl = explainerplot.plotExplainer(df, date_x, date_y)
    st.plotly_chart(fig_expl, use_container_width=True)

# Other Stats Section
st.markdown("---")
if st.button("📊 Show Other Stats"):
    st.markdown("### 🥗 Carbohydrates")
    st.plotly_chart(otherstats.plotCarbs(df,selected_day), use_container_width=True)

    st.markdown("### 💉 Insulin")
    st.plotly_chart(otherstats.plotInsulin(df,selected_day), use_container_width=True)

    st.markdown("### 🏃 Exercise (Calories & Distance)")
    st.plotly_chart(otherstats.plotExercise(df,selected_day), use_container_width=True)

    st.markdown("### ❤️ Heart Rate (BPM)")
    st.plotly_chart(otherstats.plotBPM(df,selected_day), use_container_width=True)
