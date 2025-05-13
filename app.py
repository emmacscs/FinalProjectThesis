import streamlit as st
import pandas as pd
import plots, otherstats, explainerplot

# Set page config
st.set_page_config(page_title="T1D Glucose Dashboard", layout="wide", page_icon="💉")

# Custom green background styling
st.markdown("""
    <style>
        body {
            background-color: #e8f5e9;
        }
        .stApp {
            background-color: #e8f5e9;
        }
        .block-container {
            padding-top: 2rem;
        }
        h1, h2, h3, .stMetricValue {
            color: #2e7d32;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load Data ---
df = pd.read_csv("C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/final.csv", sep="\t")
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
df_24h, df_48h, weekly_slices = plots.makeTime(df)

df2 = pd.read_csv("C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/predicted_glucose_and_shap.csv")
df2['Timestamp'] = pd.to_datetime(df2['Timestamp'])
df2.set_index('Timestamp', inplace=True)

df_expl = pd.read_csv("C:/Users/emmxc/OneDrive/Escritorio/thesis/FinalProjectThesis/testings/influential_and_insulin_event.csv")
explanation = df_expl['SHAP Explanation'].iloc[0]

timestamp = pd.to_datetime("2021-12-28 23:45:00")
predicted_glucose = float(df2.loc[timestamp, "Predicted Glucose"])
predicted_probability_hyper = float(df2.loc[timestamp, "Predicted Probability Hyper"])
predicted_probability_hypo = float(df2.loc[timestamp, "Predicted Probability Hypo"])

# --- Page Layout ---
st.title("🌿 Type 1 Diabetes Glucose Dashboard")

st.markdown("##### Prediction for 2021-12-28 23:45:00")
col1, col2, col3 = st.columns(3)
col1.metric("Predicted Glucose", f"{predicted_glucose:.2f} mmol/L")
col2.metric("Hyperglycemia Risk", f"{predicted_probability_hyper:.1%}")
col3.metric("Hypoglycemia Risk", f"{predicted_probability_hypo:.1%}")

st.markdown("### 🔍 Model Explanation")
st.code(explanation)

# --- Plots Section ---
tab1, tab2, tab3 = st.tabs(["📈 Glucose & Vitals", "🍎 Carbs & Insulin", "🧠 Explanation"])

with tab1:
    st.subheader("Glucose Trends")
    st.plotly_chart(plots.plotGlucose(df, df_24h, df_48h, weekly_slices), use_container_width=True)

    st.subheader("Heart Rate")
    st.plotly_chart(otherstats.plotBPM(df, df_24h, df_48h, weekly_slices), use_container_width=True)

    st.subheader("Exercise Events")
    st.plotly_chart(otherstats.plotExercise(df, df_24h, df_48h, weekly_slices), use_container_width=True)

with tab2:
    st.subheader("Carbohydrate Intake")
    st.plotly_chart(otherstats.plotCarbs(df, df_24h, df_48h, weekly_slices), use_container_width=True)

    st.subheader("Insulin Injections")
    st.plotly_chart(otherstats.plotInsulin(df, df_24h, df_48h, weekly_slices), use_container_width=True)

with tab3:
    st.subheader("SHAP Explanation Plot")
    st.plotly_chart(explainerplot.plotExplainer(df, "2021-12-28 21:45:00", "2021-12-28 23:45:00"), use_container_width=True)
