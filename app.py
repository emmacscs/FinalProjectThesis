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

# Load your data
data_path = "final.csv"
df = pd.read_csv(data_path, sep="")
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')

# Dummy prediction info
timestamp = "2021-12-28 23:45:00"
predicted_glucose = 9.82
hyper_prob = 0.73
hypo_prob = 0.05
explanation_gen = "The high probability of an hyperglycemic episode is due to your behavior in the last two hours."
explanation_shap = "The high probability of hyperglycemic episode is due to your Long Insulin injection at time 2021-12-28 23:00:00."

# App layout
st.title("🌿Glucose Predictor")
st.markdown(f"**🕒 Current Time:** {timestamp}")


# Load prediction & SHAP data
pred_df = pd.read_csv("predicted_glucose_and_shap.csv")
pred_df['Timestamp'] = pd.to_datetime(pred_df['Timestamp'])

# Focus on a specific timestamp (e.g., "2021-12-28 23:45:00")
target_time = pd.to_datetime("2021-12-28 23:45:00")
time_intervals = [30, 60, 120]

# Display each interval prediction with expandable SHAP section
for interval in time_intervals:
    row = pred_df[(pred_df['Timestamp'] == target_time) & (pred_df['Interval'] == interval)]
    if not row.empty:
        row = row.iloc[0]
        with st.expander(f"🔮 {interval}-minute Prediction"):
            st.markdown(f"**Hyperglycemia Probability:** {row['Predicted Probability Hyper']:.0%}")
            st.markdown(f"**Hypoglycemia Probability:** {row['Predicted Probability Hypo']:.0%}")


# Extract unique recent days (normalized to midnight)
recent_days = df['Time'].dt.normalize().drop_duplicates().sort_values(ascending=False)

# Get the most recent full day
latest_day = df['Time'].dt.normalize().max()

# Exclude it from the dropdown if it's already shown as "Last 24 Hours"
filtered_days = recent_days[recent_days < latest_day]

# Dropdown for day selection
selected_day = st.selectbox(
    "📅 Choose a day to explore",
    options=[None] + list(filtered_days),
    format_func=lambda x: "Last 24 Hours" if x is None else x.strftime("%A, %d %B")
)

# Plot
st.markdown("### 📈 Glucose Time Series")
fig = plots.plotGlucose(df, selected_day=selected_day)
st.plotly_chart(fig, use_container_width=True)


# Explanation
st.markdown("### 💡 Model Explanation")
st.code(explanation_shap)

# Insight Section
st.markdown("---")
if st.button("🧠 Insight into Explanation"):
    st.markdown("### 🧪 Explainer Graph")

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
