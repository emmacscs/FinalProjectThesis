import plotly.graph_objects as go


def plotExplainer(df, date_x, date_y):
    """
    Plots glucose and related features (carbs, insulin, etc.) between date_x and date_y.
    Mimics plotGlucose structure but zoomed into a specific 2-hour window.
    
    Args:
        df (pd.DataFrame): Main dataset with 'Time', 'Glucose', 'Carbohydrates', etc.
        date_x (datetime): Start of the 2-hour window.
        date_y (datetime): End of the 2-hour window.
    
    Returns:
        go.Figure: Interactive Plotly figure.
    """
    df_window = df[(df['Time'] >= date_x) & (df['Time'] <= date_y)].copy()

    fig = go.Figure()

    # Glucose zones
    fig.add_shape(type="rect", x0=date_x, x1=date_y, y0=-5, y1=3.9,
                  fillcolor="pink", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=date_x, x1=date_y, y0=3.9, y1=10,
                  fillcolor="lightgreen", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=date_x, x1=date_y, y0=10.01, y1=30,
                  fillcolor="beige", opacity=0.5, layer="below", line_width=0)

    # Glucose trace
    fig.add_trace(go.Scatter(
        x=df_window['Time'],
        y=df_window['Glucose'],
        name='Glucose',
        mode='lines',
        customdata=df_window[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last meal: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Stats traces
    stats = [
        ('Carbs', df_window['Carbohydrates'], 'orange', 'Carbs: %{y}<br>Time: %{x}<extra></extra>'),
        ('Insulin', df_window['Rapid Insulin'] + df_window['Long Insulin'], 'purple', 'Insulin: %{y}<br>Time: %{x}<extra></extra>'),
        ('Calories', df_window['Calories'], 'black', 'Calories: %{y}<br>Time: %{x}<extra></extra>'),
        ('Distance', df_window['Distance'], 'green', 'Distance: %{y}<br>Time: %{x}<extra></extra>'),
        ('BPM', df_window['BPM'], 'red', 'BPM: %{y}<br>Time: %{x}<extra></extra>')
    ]

    for name, y_data, color, hover in stats:
        fig.add_trace(go.Scatter(
            x=df_window['Time'],
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
            {"visible": [True] + [False]*5},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": ""}
        ]),
        dict(label="Carbs", method="update", args=[
            {"visible": [True, True, False, False, False, False]},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Carbs (g)"}
        ]),
        dict(label="Insulin", method="update", args=[
            {"visible": [True, False, True, False, False, False]},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Insulin (units)"}
        ]),
        dict(label="Calories", method="update", args=[
            {"visible": [True, False, False, True, False, False]},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Calories (kcal)"}
        ]),
        dict(label="Distance", method="update", args=[
            {"visible": [True, False, False, False, True, False]},
            {"yaxis.title": "Glucose (mmol/L)", "yaxis2.title": "Distance (km)"}
        ]),
        dict(label="BPM", method="update", args=[
            {"visible": [True, False, False, False, False, True]},
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
        title=f"Explainer graph",
        xaxis_title="Time",
        yaxis_title="Glucose (mmol/L)",
        plot_bgcolor="white",
        xaxis_range=[date_x, date_y],
        yaxis_range=[-5, max(df_window['Glucose'].max(), 15)],
        yaxis2=dict(
            title="Secondary Y-axis",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        showlegend=True
    )

    return fig
