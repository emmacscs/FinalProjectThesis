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

    # Glucose zones (background)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=-5, y1=3.9, fillcolor="pink", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=3.9, y1=10, fillcolor="lightgreen", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df['Time'].min(), x1=df['Time'].max(),
                  y0=10.01, y1=30, fillcolor="beige", opacity=0.5, layer="below", line_width=0)

    # 24h trace for Glucose
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['Glucose'],
        name='24h Glucose',
        visible=True,
        mode='lines',
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # 48h trace for Glucose
    fig.add_trace(go.Scatter(
        x=df_48['Time'],
        y=df_48['Glucose'],
        name='48h Glucose',
        visible=False,
        mode='lines',
        customdata=df_48[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Weekly traces for Glucose
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
            name=f'Week {label} Glucose',
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

    # Adding stats traces (Carbs, Insulin, Calories, Distance, BPM)
    # These stats will be plotted on top of the glucose line with a secondary Y-axis

    # Carbs trace (for stats)
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['Carbohydrates'],
        name='Insulin',
        visible=False,
        mode='lines',
        line=dict(color='blue'),
        yaxis="y2",  # Secondary y-axis
        hovertemplate='Carbs: %{y}<br>Time: %{x}<extra></extra>'
    ))

    # Insulin trace (for stats)
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['Rapid Insulin'],
        name='Calories',
        visible=False,
        mode='lines',
        line=dict(color='orange'),
        yaxis="y2",  # Secondary y-axis
        hovertemplate='Insulin: %{y}<br>Time: %{x}<extra></extra>'
    ))

    # Calories trace (for stats)
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['Calories'],
        name='Distance',
        visible=False,
        mode='lines',
        line=dict(color='green'),
        yaxis="y2",  # Secondary y-axis
        hovertemplate='Calories: %{y}<br>Time: %{x}<extra></extra>'
    ))

    # Distance trace (for stats)
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['Distance'],
        name='BPM',
        visible=False,
        mode='lines',
        line=dict(color='purple'),
        yaxis="y2",  # Secondary y-axis
        hovertemplate='Distance: %{y}<br>Time: %{x}<extra></extra>'
    ))

    # BPM trace (for stats)
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['BPM'],
        name='BPM',
        visible=False,
        mode='lines',
        line=dict(color='red'),
        yaxis="y2",  # Secondary y-axis
        hovertemplate='BPM: %{y}<br>Time: %{x}<extra></extra>'
    ))

    # Dropdown for time range selection (24h, 48h, Weekly)
    time_buttons = [
        dict(label="24h", method="update", args=[
            {"visible": [True] + [False]*(1 + len(weekly_slices)) + [False]*5},  # Show only glucose
            {"xaxis.range": [df_24h['Time'].min(), df_24h['Time'].max()]}
        ]),
        dict(label="48h", method="update", args=[
            {"visible": [False, True] + [False]*len(weekly_slices) + [False]*5},  # Show only glucose
            {"xaxis.range": [df_48['Time'].min(), df_48['Time'].max()]}
        ])
    ]

    # Dropdown for selecting stats (Carbs, Insulin, Calories, Distance, BPM)
    stat_buttons = [
        dict(label="--extra statistics--", method="update", args=[
            {"visible": [True, False] + [False]*(1 + len(weekly_slices)) +  [False]*5},  # Show Carbs
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Carbs (g)"}
        ]),
        dict(label="Carbs", method="update", args=[
            {"visible": [True, False] + [False]*(1 + len(weekly_slices)) +  [True] + [False]*4},  # Show Carbs
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Carbs (g)"}
        ]),
        dict(label="Insulin", method="update", args=[
            {"visible": [True, False] + [False]*(1 + len(weekly_slices)) + [False] + [True] + [False]*3},  # Show Insulin
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Insulin (units)"}
        ]),
        dict(label="Calories", method="update", args=[
            {"visible": [True, False] + [False]*(1 + len(weekly_slices)) + [False] + [False] + [True]  + [False]*2},  # Show Calories
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Calories (kcal)"}
        ]),
        dict(label="Distance", method="update", args=[
            {"visible": [True, False] + [False]*(1 + len(weekly_slices)) +[False] + [False] + [False] + [True] + [False]},  # Show Distance
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Distance (km)"}
        ]),
        dict(label="BPM", method="update", args=[
            {"visible": [True, False] + [False]*(1 + len(weekly_slices)) + [False] + [False] + [False] + [False] + [True]},  # Show BPM
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "BPM (beats per minute)"}
        ])
    ]

    # Update layout with the dropdown buttons
    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.05,
                y=1.15,
                showactive=True,
                buttons=time_buttons  # Time selection buttons
            ),
            dict(
                type="dropdown",
                direction="down",
                x=0.2,
                y=1.15,
                showactive=True,
                buttons=stat_buttons  # Stats selection buttons
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
        customdata=df_24h[['Calories', 'Distance']].values,
        hovertemplate='BPM: %{y}<br>Time: %{x}<br>Latest Calories: %{customdata[0]:.2f}<br>Latest Distance : %{customdata[1]}<extra></extra>'
    ))

    # Heart rate (BPM) as line plot for 48h trace
    fig.add_trace(go.Scatter(
        x=df_48['Time'],
        y=df_48['BPM'],
        name='48h BPM',
        visible=False,
        mode='lines',
        customdata=df_48[['Calories', 'Distance']].values,
        hovertemplate='BPM: %{y}<br>Time: %{x}<br>Latest Calories: %{customdata[0]:.2f}<br>Latest Distance : %{customdata[1]}<extra></extra>'
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
            customdata=df_w[['Calories', 'Distance']].values,
            hovertemplate='BPM: %{y}<br>Time: %{x}<br>Latest Calories: %{customdata[0]:.2f}<br>Latest Distance : %{customdata[1]}<extra></extra>'
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

def plotExercise(df, df_24h, df_48, weekly_slices):
    fig = go.Figure()

    def get_colors(y, threshold, color_over, color_under):
        return [color_over if val > threshold else color_under for val in y]

    # Add Calories and Distance bars for 24h
    fig.add_trace(go.Bar(
        x=df_24h['Time'],
        y=df_24h['Calories'],
        name='24h Calories',
        marker_color=get_colors(df_24h['Calories'], 60, 'red', 'blue'),
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Calories: %{y}<br>Time: %{x}<br>Min since last carbs: %{customdata[0]:.2f}<br>Min since last insulin: %{customdata[1]}<extra></extra>',
        yaxis='y1',
        visible=True
    ))

    fig.add_trace(go.Bar(
        x=df_24h['Time'],
        y=df_24h['Distance'],
        name='24h Distance',
        marker_color=get_colors(df_24h['Distance'], 20, 'purple', 'green'),
        yaxis='y2',
        visible=True
    ))

    # Add 48h Calories and Distance
    fig.add_trace(go.Bar(
        x=df_48['Time'],
        y=df_48['Calories'],
        name='48h Calories',
        marker_color=get_colors(df_48['Calories'], 60, 'red', 'blue'),
        customdata=df_48[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Calories: %{y}<br>Time: %{x}<br>Min since last carbs: %{customdata[0]:.2f}<br>Min since last insulin: %{customdata[1]}<extra></extra>',
        yaxis='y1',
        visible=False
    ))

    fig.add_trace(go.Bar(
        x=df_48['Time'],
        y=df_48['Distance'],
        name='48h Distance',
        marker_color=get_colors(df_48['Distance'], 20, 'purple', 'green'),
        yaxis='y2',
        visible=False
    ))

    # Add weekly slices
    for i, (label, df_w) in enumerate(weekly_slices):
        fig.add_trace(go.Bar(
            x=df_w['Time'],
            y=df_w['Calories'],
            name=f'Week {label} Calories',
            marker_color=get_colors(df_w['Calories'], 60, 'red', 'blue'),
            customdata=df_w[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
            hovertemplate='Calories: %{y}<br>Time: %{x}<br>Min since last carbs: %{customdata[0]:.2f}<br>Min since last insulin: %{customdata[1]}<extra></extra>',
            yaxis='y1',
            visible=False
        ))

        fig.add_trace(go.Bar(
            x=df_w['Time'],
            y=df_w['Distance'],
            name=f'Week {label} Distance',
            marker_color=get_colors(df_w['Distance'], 160, 'purple', 'green'),
            yaxis='y2',
            visible=False
        ))

    # Buttons to switch between 24h, 48h, weekly
    total_sets = 2 + len(weekly_slices) * 2
    buttons = []

    # Helper: generate visibility lists
    def visible_list(active_start, size=total_sets):
        return [i in active_start for i in range(size)]

    buttons.append(dict(
        label="24h",
        method="update",
        args=[{"visible": visible_list([0, 1])},
              {"xaxis.range": [df_24h['Time'].min(), df_24h['Time'].max()]}]
    ))

    buttons.append(dict(
        label="48h",
        method="update",
        args=[{"visible": visible_list([2, 3])},
              {"xaxis.range": [df_48['Time'].min(), df_48['Time'].max()]}]
    ))

    for i, (label, df_w) in enumerate(weekly_slices):
        buttons.append(dict(
            label=f"Week: {label}",
            method="update",
            args=[{"visible": visible_list([4 + i * 2, 5 + i * 2])},
                  {"xaxis.range": [df_w['Time'].min(), df_w['Time'].max()]}]
        ))

    # Layout
    fig.update_layout(
        title="Calories & Distance - Time Explorer",
        xaxis=dict(title="Time"),
        yaxis=dict(title="Calories", side='left', range=[0, max(df['Calories'].max(), 100)]),
        yaxis2=dict(title="Distance", overlaying='y', side='right', range=[0, max(df['Distance'].max(), 50)]),
        updatemenus=[dict(type="dropdown", direction="down", x=0.05, y=1.15, showactive=True, buttons=buttons)],
        barmode='group',
        plot_bgcolor="white",
        legend=dict(x=0.8, y=1.2),
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()]
    )

    return fig