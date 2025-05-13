import streamlit as st
import pandas as pd
import plots  # assuming you saved the updated function in plots.py

# Page config
st.set_page_config(page_title="Simple Glucose Predictor", layout="centered")

# Load your data
data_path = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/final.csv"
df = pd.read_csv(data_path, sep="\t")
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')

# Dummy prediction info
timestamp = "2021-12-28 23:45:00"
predicted_glucose = 9.82
hyper_prob = 0.73
hypo_prob = 0.05
explanation = "Top features: insulin_recent=high, meal_carbs=low, activity=none"

# App layout
st.title("🌿 Simple Glucose Predictor")
st.markdown(f"**🕒 Timestamp:** {timestamp}")

col1, col2, col3 = st.columns(3)
col1.metric("Predicted Glucose", f"{predicted_glucose:.2f} mmol/L")
col2.metric("Hyperglycemia Risk", f"{hyper_prob:.0%}")
col3.metric("Hypoglycemia Risk", f"{hypo_prob:.0%}")

# Plot
st.markdown("### 📈 Glucose Time Series (Last 24h)")
fig = plots.plotGlucose(df)
st.plotly_chart(fig, use_container_width=True)

# Explanation
st.markdown("### 💡 Model Explanation")
st.code(explanation)
