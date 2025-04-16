import plotly.graph_objects as go

def plotGlucose(df):
    fig = go.Figure()

    # Plot the Glucose data
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Glucose'], mode='lines', name='Glucose'))

    fig.update_layout(title="Glucose over Time", xaxis_title="Time", yaxis_title="Glucose Level (mmol/L)")
    return fig

def plotCarbohydrates(df):
    fig = go.Figure()

    # Plot the Carbohydrates data
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Carbohydrates'], mode='lines', name='Carbohydrates'))

    fig.update_layout(title="Carbohydrates over Time", xaxis_title="Time", yaxis_title="Carbohydrates (g)")
    return fig
