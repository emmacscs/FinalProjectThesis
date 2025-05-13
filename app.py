import streamlit as st
import pandas as pd
import datetime
import plots,otherstats,explainerplot  # assuming you saved the updated function in plots.py

# Page config
st.set_page_config(page_title="Glucose Predictor", layout="centered")

# Load your data
data_path = "C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/final.csv"
df = pd.read_csv(data_path, sep="\t")
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')

# Dummy prediction info
timestamp = "2021-12-28 23:45:00"
predicted_glucose = 9.82
hyper_prob = 0.73
hypo_prob = 0.05
explanation_gen = "The high probability of an hypoglycemic episode is due to your behavior in the last two hours."
explanation_shap = "The high probability of hypoglycemic episode is due to your Long Insulin injection at time 2021-12-28 23:00:00."

# App layout
st.title("🌿Glucose Predictor")
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
st.code(explanation_shap)

# Insight Section
st.markdown("---")
if st.button("🧠 Insight into Explanation"):
    st.markdown("### 🧪 Explainer Graph")

    # Define the 2-hour window for the explainer (you can make this dynamic later)
    date_x = pd.to_datetime("2021-12-28 21:45:00")
    date_y = pd.to_datetime("2021-12-28 23:45:00")

    fig_expl = explainerplot.plotExplainer(df, date_x, date_y)
    st.plotly_chart(fig_expl, use_container_width=True)

# Other Stats Section
st.markdown("---")
if st.button("📊 Show Other Stats (24h)"):
    st.markdown("### 🥗 Carbohydrates")
    st.plotly_chart(otherstats.plotCarbs(df), use_container_width=True)

    st.markdown("### 💉 Insulin")
    st.plotly_chart(otherstats.plotInsulin(df), use_container_width=True)

    st.markdown("### 🏃 Exercise (Calories & Distance)")
    st.plotly_chart(otherstats.plotExercise(df), use_container_width=True)

    st.markdown("### ❤️ Heart Rate (BPM)")
    st.plotly_chart(otherstats.plotBPM(df), use_container_width=True)
