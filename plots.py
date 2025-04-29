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

    def get_visible_array(glucose_index=0, stat_index=None, n_weekly=len(weekly_slices)):
        visible = [False] * (2 + n_weekly + 5)  # 2 base traces, n_weekly, 5 stats
        visible[glucose_index] = True
        if stat_index is not None:
            visible[2 + n_weekly + stat_index] = True
        return visible

    # Glucose zones (background)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=-5, y1=3.9, fillcolor="pink", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=3.9, y1=10, fillcolor="lightgreen", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=10.01, y1=30, fillcolor="beige", opacity=0.5, layer="below", line_width=0)

    # Glucose traces
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['Glucose'],
        name='Glucose',
        visible=True,
        mode='lines',
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last meal: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_48['Time'],
        y=df_48['Glucose'],
        name='Glucose',
        visible=False,
        mode='lines',
        customdata=df_48[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last meal: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    for i, (label, df_w) in enumerate(weekly_slices):
        fig.add_trace(go.Scatter(
            x=df_w['Time'],
            y=df_w['Glucose'],
            name=f'Glucose',
            visible=False,
            mode='lines',
            customdata=df_w[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
            hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last meal: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
        ))

    # Stats traces (Carbs, Insulin, Calories, Distance, BPM)
    stats = [
        ('Carbs', df_24h['Carbohydrates'], 'orange', 'Carbs: %{y}<br>Time: %{x}<extra></extra>'),
        ('Insulin', df_24h['Rapid Insulin']+df_24h['Long Insulin'], 'purple', 'Insulin: %{y}<br>Time: %{x}<extra></extra>'),
        ('Calories', df_24h['Calories'], 'black', 'Calories: %{y}<br>Time: %{x}<extra></extra>'),
        ('Distance', df_24h['Distance'], 'green', 'Distance: %{y}<br>Time: %{x}<extra></extra>'),
        ('BPM', df_24h['BPM'], 'red', 'BPM: %{y}<br>Time: %{x}<extra></extra>')
    ]

    for name, y_data, color, hover in stats:
        fig.add_trace(go.Scatter(
            x=df_24h['Time'],
            y=y_data,
            name=name,
            visible=False,
            mode='lines',
            line=dict(color=color),
            yaxis="y2",
            hovertemplate=hover
        ))

    stat_buttons = [
        dict(label="--extra statistics--", method="update", args=[
            {"visible": get_visible_array(glucose_index=0)},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": ""}
        ]),
        dict(label="Carbs", method="update", args=[
            {"visible": get_visible_array(glucose_index=0, stat_index=0)},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Carbs (g)"}
        ]),
        dict(label="Insulin", method="update", args=[
            {"visible": get_visible_array(glucose_index=0, stat_index=1)},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Insulin (units)"}
        ]),
        dict(label="Calories", method="update", args=[
            {"visible": get_visible_array(glucose_index=0, stat_index=2)},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Calories (kcal)"}
        ]),
        dict(label="Distance", method="update", args=[
            {"visible": get_visible_array(glucose_index=0, stat_index=3)},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Distance (km)"}
        ]),
        dict(label="BPM", method="update", args=[
            {"visible": get_visible_array(glucose_index=0, stat_index=4)},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "BPM (beats per minute)"}
        ])
    ]

    # Layout
    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.0,
                y=1.15,
                showactive=True,
                buttons=stat_buttons
            ),
        ],
        title="Glucose Trends - Time Explorer",
        xaxis_title="Time",
        yaxis_title="Glucose (mmol/L)",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[-5, max(df['Glucose'].max(), 15)],
        yaxis2=dict(
            title="Secondary Y-axis",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        showlegend=True
    )

    return fig
