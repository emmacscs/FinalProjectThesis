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

def plotGlucose(df,df_24h,df_48,weekly_slices):
        
    #I use the go figures of plotly
    fig = go.Figure()

    # Add glucose range bands (shaded areas)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                y0=-5, y1=3.9, fillcolor="pink", opacity=0.8, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                y0=3.9, y1=10, fillcolor="lightgreen", opacity=0.8, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                y0=10.01, y1=120, fillcolor="beige", opacity=0.8, layer="below", line_width=0)

    # Add base traces
    fig.add_trace(go.Scatter(x=df_24h['Time'], y=df_24h['Glucose'], name='24h', visible=True, fillcolor= 'black'))
    fig.add_trace(go.Scatter(x=df_48['Time'], y=df_48['Glucose'], name='48h', visible=False, fillcolor= 'black'))

    # Add weekly traces
    for label, df_w in weekly_slices:
        fig.add_trace(go.Scatter(x=df_w['Time'], y=df_w['Glucose'], name=label, visible=False))


    fig.update_layout(
        updatemenus=[
        
            # Dropdown for selecting a specific week
            dict(
                type="dropdown",
                direction="down",
                x=0.1, y=1.15,
                showactive=True,
                buttons=[
                    dict(
                        label="24h",
                        method="update",
                        args=[
                            {"visible": [True, False, False, False, False, False]},
                            {"xaxis": {"range": [df_24h['Time'].min(), df_24h['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="48h",
                        method="update",
                        args=[
                            {"visible": [False, True, False, False, False, False]},
                            {"xaxis": {"range": [df_48['Time'].min(), df_48['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 19/04 - 25/04",
                        method="update",
                        args=[
                            {"visible": [False, False, True, False, False, False]},
                            {"xaxis": {"range": [weekly_slices[0][1]['Time'].min(), weekly_slices[0][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 12/04 - 18/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, True, False, False]},
                            {"xaxis": {"range": [weekly_slices[1][1]['Time'].min(), weekly_slices[1][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 5/04 - 11/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, False, True, False]},
                            {"xaxis": {"range": [weekly_slices[2][1]['Time'].min(), weekly_slices[2][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 29/03 - 4/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, False, False, True]},
                            {"xaxis": {"range": [weekly_slices[3][1]['Time'].min(), weekly_slices[3][1]['Time'].max()]}}
                        ]
                    )
                ]
            )
        ],
        title="Glucose Trends - Time Explorer",
        xaxis_title="Time",
        yaxis_title="Glucose (mmol/L)",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[-5,df['Glucose'].max()]
    )
    return fig


def plotCarbohydrates(df,df_24h,df_48,weekly_slices):
    fig_car = go.Figure()

    # 1. 24h Trace: Group by 30-minute intervals
    df_24h_resampled = df_24h.resample('30T', on='Time').mean()  # '30T' is for 30-minute intervals
    fig_car.add_trace(go.Bar(
        x=df_24h_resampled.index,
        y=df_24h_resampled['Carbohydrates'],
        name='24h (30min intervals)',
        visible=True,
        marker_color='orange'
    ))

    # 2. 48h Trace: Group by 30-minute intervals
    df_48_resampled = df_48.resample('30T', on='Time').mean()  # '30T' is for 30-minute intervals
    fig_car.add_trace(go.Bar(
        x=df_48_resampled.index,
        y=df_48_resampled['Carbohydrates'],
        name='48h (30min intervals)',
        visible=False,
        marker_color='orange'
    ))

    # 3. Weekly Traces: Group by day and compute average carbohydrates
    for label, df_w in weekly_slices:
        # Resample by day (group by day and take the mean)
        df_w_resampled = df_w.resample('60T', on='Time').mean()  # '30T' for daily averages
        fig_car.add_trace(go.Bar(
            x=df_w_resampled.index,
            y=df_w_resampled['Carbohydrates'],
            name=label,
            visible=False,
            marker_color='orange'
        ))

        
    fig_car.update_layout(
        updatemenus=[
        
            # Dropdown for selecting a specific week
            dict(
                type="dropdown",
                direction="down",
                x=0.1, y=1.15,
                showactive=True,
                buttons=[
                    dict(
                        label="24h",
                        method="update",
                        args=[
                            {"visible": [True, False, False, False, False, False]},
                            {"xaxis": {"range": [df_24h['Time'].min(), df_24h['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="48h",
                        method="update",
                        args=[
                            {"visible": [False, True, False, False, False, False]},
                            {"xaxis": {"range": [df_48['Time'].min(), df_48['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 19/04 - 25/04",
                        method="update",
                        args=[
                            {"visible": [False, False, True, False, False, False]},
                            {"xaxis": {"range": [weekly_slices[0][1]['Time'].min(), weekly_slices[0][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 12/04 - 18/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, True, False, False]},
                            {"xaxis": {"range": [weekly_slices[1][1]['Time'].min(), weekly_slices[1][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 5/04 - 11/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, False, True, False]},
                            {"xaxis": {"range": [weekly_slices[2][1]['Time'].min(), weekly_slices[2][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 29/03 - 4/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, False, False, True]},
                            {"xaxis": {"range": [weekly_slices[3][1]['Time'].min(), weekly_slices[3][1]['Time'].max()]}}
                        ]
                    )
                ]
            )
        ],
        title="Carbohydrates Trends - Time Explorer",
        xaxis_title="Time",
        yaxis_title="Carbohydrates",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[df['Carbohydrates'].min(),df['Carbohydrates'].max()]
    )

    return fig_car

    

def plot_stress(df,df_24h,df_48,weekly_slices):
    fig_stress = go.Figure()

    # 1. 24h Trace: Group by 30-minute intervals
    df_24h_resampled = df_24h.resample('30T', on='Time').mean()  # '30T' is for 30-minute intervals
    fig_stress.add_trace(go.Bar(
        x=df_24h_resampled.index,
        y=df_24h_resampled['Stress'],
        name='24h (30min intervals)',
        visible=True,
        marker_color='orange'
    ))

    # 2. 48h Trace: Group by 30-minute intervals
    df_48_resampled = df_48.resample('30T', on='Time').mean()  # '30T' is for 30-minute intervals
    fig_stress.add_trace(go.Bar(
        x=df_48_resampled.index,
        y=df_48_resampled['Stress'],
        name='48h (30min intervals)',
        visible=False,
        marker_color='orange'
    ))

    # 3. Weekly Traces: Group by day and compute average carbohydrates
    for label, df_w in weekly_slices:
        # Resample by day (group by day and take the mean)
        df_w_resampled = df_w.resample('60T', on='Time').mean()  # '30T' for daily averages
        fig_stress.add_trace(go.Bar(
            x=df_w_resampled.index,
            y=df_w_resampled['Stress'],
            name=label,
            visible=False,
            marker_color='orange'
        ))

        
    fig_stress.update_layout(
        updatemenus=[
        
            # Dropdown for selecting a specific week
            dict(
                type="dropdown",
                direction="down",
                x=0.1, y=1.15,
                showactive=True,
                buttons=[
                    dict(
                        label="24h",
                        method="update",
                        args=[
                            {"visible": [True, False, False, False, False, False]},
                            {"xaxis": {"range": [df_24h['Time'].min(), df_24h['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="48h",
                        method="update",
                        args=[
                            {"visible": [False, True, False, False, False, False]},
                            {"xaxis": {"range": [df_48['Time'].min(), df_48['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 19/04 - 25/04",
                        method="update",
                        args=[
                            {"visible": [False, False, True, False, False, False]},
                            {"xaxis": {"range": [weekly_slices[0][1]['Time'].min(), weekly_slices[0][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 12/04 - 18/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, True, False, False]},
                            {"xaxis": {"range": [weekly_slices[1][1]['Time'].min(), weekly_slices[1][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 5/04 - 11/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, False, True, False]},
                            {"xaxis": {"range": [weekly_slices[2][1]['Time'].min(), weekly_slices[2][1]['Time'].max()]}}
                        ]
                    ),
                    dict(
                        label="Week: 29/03 - 4/04",
                        method="update",
                        args=[
                            {"visible": [False, False, False, False, False, True]},
                            {"xaxis": {"range": [weekly_slices[3][1]['Time'].min(), weekly_slices[3][1]['Time'].max()]}}
                        ]
                    )
                ]
            )
        ],
        title="Stress Trends - Time Explorer",
        xaxis_title="Time",
        yaxis_title="Stress",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[df['Stress'].min(),df['Stress'].max()]
    )

    return fig_stress
