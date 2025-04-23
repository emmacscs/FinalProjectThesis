import plotly.graph_objects as go
import pandas as pd

def makeTime(df):

    # SLICE: 24 HOURS
    end_time = df['Time'].max() #finish time is this precise moment
    start_time = end_time - pd.Timedelta(hours=24)
    df_24h = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)].dropna(subset=['Glucose'])


    #SLICE: 48 hours
    start_48 = end_time - pd.Timedelta(hours=48)
    df_48 = df[(df['Time']>= start_48) & (df['Time'] <= end_time)].dropna(subset=['Glucose'])

    # Weekly slices (let’s say last 4 weeks)
    weekly_slices = []
    for i in range(4):
        end = end_time - pd.Timedelta(weeks=i)
        start = end - pd.Timedelta(weeks=1)
        df_week = df[(df['Time'] >= start) & (df['Time'] < end)].dropna(subset=['Glucose'])
        weekly_slices.append((f"Week of {start.date()}", df_week))

    return df_24h,df_48,weekly_slices

def plotGlucose(df, df_24h, df_48, weekly_slices):
    fig = go.Figure()

    # Glucose zones
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=-5, y1=3.9, fillcolor="pink", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=3.9, y1=10, fillcolor="lightgreen", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=10.01, y1=30, fillcolor="beige", opacity=0.5, layer="below", line_width=0)

    # 24h trace
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['Glucose'],
        name='24h',
        visible=True,
        mode='lines',
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # 48h trace
    fig.add_trace(go.Scatter(
        x=df_48['Time'],
        y=df_48['Glucose'],
        name='48h',
        visible=False,
        mode='lines',
        customdata=df_48[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Weekly traces
    buttons = [
        dict(label="24h", method="update", args=[
            {"visible": [True] + [False]*(1 + len(weekly_slices))},
            {"xaxis.range": [df_24h['Time'].min(), df_24h['Time'].max()]}
        ]),
        dict(label="48h", method="update", args=[
            {"visible": [False, True] + [False]*len(weekly_slices)},
            {"xaxis.range": [df_48['Time'].min(), df_48['Time'].max()]}
        ])
    ]

    for i, (label, df_w) in enumerate(weekly_slices):
        fig.add_trace(go.Scatter(
            x=df_w['Time'],
            y=df_w['Glucose'],
            name=f'Week {label}',
            visible=False,
            mode='lines',
            customdata=df_w[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
            hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
        ))

        button = dict(label=f"Week: {label}",
                      method="update",
                      args=[
                          {"visible": [False, False] + [j == i for j in range(len(weekly_slices))]},
                          {"xaxis.range": [df_w['Time'].min(), df_w['Time'].max()]}
                      ])
        buttons.append(button)

    # Layout
    fig.update_layout(
        updatemenus=[

            dict(
                type="dropdown",
                direction="down",
                x=0.05, y=1.15,
                showactive=True,
                buttons=buttons
            )
        ],
        title="Glucose Trends - Time Explorer",
        xaxis_title="Time",
        yaxis_title="Glucose (mmol/L)",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[-5, max(df['Glucose'].max(), 15)]
    )

    return fig

def plotCarbs(df, df_24h, df_48, weekly_slices):
    fig = go.Figure()

    # Carbohydrates consumption as bar plot for 24h trace
    fig.add_trace(go.Bar(
        x=df_24h['Time'],
        y=df_24h['Carbohydrates'],
        name='24h Carbs',
        visible=True,
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Carbs: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Carbohydrates consumption as bar plot for 48h trace
    fig.add_trace(go.Bar(
        x=df_48['Time'],
        y=df_48['Carbohydrates'],
        name='48h Carbs',
        visible=False,
        customdata=df_48[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Carbs: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Weekly traces for carbohydrates consumption
    buttons = [
        dict(label="24h", method="update", args=[
            {"visible": [True] + [False]*(1 + len(weekly_slices))},
            {"xaxis.range": [df_24h['Time'].min(), df_24h['Time'].max()]}
        ]),
        dict(label="48h", method="update", args=[
            {"visible": [False, True] + [False]*len(weekly_slices)},
            {"xaxis.range": [df_48['Time'].min(), df_48['Time'].max()]}
        ])
    ]

    for i, (label, df_w) in enumerate(weekly_slices):
        fig.add_trace(go.Bar(
            x=df_w['Time'],
            y=df_w['Carbohydrates'],
            name=f'Week {label} Carbs',
            visible=False,
            customdata=df_w[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
            hovertemplate='Carbs: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
        ))

        button = dict(label=f"Week: {label}",
                      method="update",
                      args=[
                          {"visible": [False, False] + [j == i for j in range(len(weekly_slices))]},
                          {"xaxis.range": [df_w['Time'].min(), df_w['Time'].max()]}
                      ])
        buttons.append(button)

    # Layout
    fig.update_layout(
        updatemenus=[dict(type="dropdown", direction="down", x=0.05, y=1.15, showactive=True, buttons=buttons)],
        title="Carbohydrates Consumption - Time Explorer",
        xaxis_title="Time",
        yaxis_title="Carbohydrates (g)",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[0, max(df['Carbohydrates'].max(), 200)]
    )

    return fig

def plotInsulin(df, df_24h, df_48, weekly_slices):
    fig = go.Figure()

    # Insulin doses as bar plot for 24h trace
    fig.add_trace(go.Bar(
        x=df_24h['Time'],
        y=df_24h['Insulin absorption'],
        name='24h Insulin',
        visible=True,
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Insulin: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Insulin doses as bar plot for 48h trace
    fig.add_trace(go.Bar(
        x=df_48['Time'],
        y=df_48['Insulin absorption'],
        name='48h Insulin',
        visible=False,
        customdata=df_48[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Insulin: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Weekly traces for insulin doses
    buttons = [
        dict(label="24h", method="update", args=[
            {"visible": [True] + [False]*(1 + len(weekly_slices))},
            {"xaxis.range": [df_24h['Time'].min(), df_24h['Time'].max()]}
        ]),
        dict(label="48h", method="update", args=[
            {"visible": [False, True] + [False]*len(weekly_slices)},
            {"xaxis.range": [df_48['Time'].min(), df_48['Time'].max()]}
        ])
    ]

    for i, (label, df_w) in enumerate(weekly_slices):
        fig.add_trace(go.Bar(
            x=df_w['Time'],
            y=df_w['Insulin absorption'],
            name=f'Week {label} Insulin',
            visible=False,
            customdata=df_w[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
            hovertemplate='Insulin: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
        ))

        button = dict(label=f"Week: {label}",
                      method="update",
                      args=[
                          {"visible": [False, False] + [j == i for j in range(len(weekly_slices))]},
                          {"xaxis.range": [df_w['Time'].min(), df_w['Time'].max()]}
                      ])
        buttons.append(button)

    # Layout
    fig.update_layout(
        updatemenus=[dict(type="dropdown", direction="down", x=0.05, y=1.15, showactive=True, buttons=buttons)],
        title="Insulin Doses - Time Explorer",
        xaxis_title="Time",
        yaxis_title="Insulin (Units)",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[0, max(df['Insulin absorption'].max(), 50)]
    )

    return fig


def plotBPM(df, df_24h, df_48, weekly_slices):
    fig = go.Figure()

    # Heart rate (BPM) as line plot for 24h trace
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['BPM'],
        name='24h BPM',
        visible=True,
        mode='lines',
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='BPM: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Heart rate (BPM) as line plot for 48h trace
    fig.add_trace(go.Scatter(
        x=df_48['Time'],
        y=df_48['BPM'],
        name='48h BPM',
        visible=False,
        mode='lines',
        customdata=df_48[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='BPM: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Weekly traces for heart rate (BPM)
    buttons = [
        dict(label="24h", method="update", args=[
            {"visible": [True] + [False]*(1 + len(weekly_slices))},
            {"xaxis.range": [df_24h['Time'].min(), df_24h['Time'].max()]}
        ]),
        dict(label="48h", method="update", args=[
            {"visible": [False, True] + [False]*len(weekly_slices)},
            {"xaxis.range": [df_48['Time'].min(), df_48['Time'].max()]}
        ])
    ]

    for i, (label, df_w) in enumerate(weekly_slices):
        fig.add_trace(go.Scatter(
            x=df_w['Time'],
            y=df_w['BPM'],
            name=f'Week {label} BPM',
            visible=False,
            mode='lines',
            customdata=df_w[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
            hovertemplate='BPM: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
        ))

        button = dict(label=f"Week: {label}",
                      method="update",
                      args=[
                          {"visible": [False, False] + [j == i for j in range(len(weekly_slices))]},
                          {"xaxis.range": [df_w['Time'].min(), df_w['Time'].max()]}
                      ])
        buttons.append(button)

    # Layout
    fig.update_layout(
        updatemenus=[dict(type="dropdown", direction="down", x=0.05, y=1.15, showactive=True, buttons=buttons)],
        title="Heart Rate (BPM) - Time Explorer",
        xaxis_title="Time",
        yaxis_title="Heart Rate (BPM)",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[0, max(df['BPM'].max(), 200)]
    )

    return fig