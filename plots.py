import pandas as pd
import plotly.graph_objects as go

def plotGlucose(df):
    # Extract last 24 hours
    latest_time = df['Time'].max()
    df_24h = df[df['Time'] >= (latest_time - pd.Timedelta(hours=24))].copy()

    fig = go.Figure()

    # Background zones
    fig.add_shape(type="rect", x0=df_24h['Time'].min(), x1=df_24h['Time'].max(),
                  y0=-5, y1=3.9, fillcolor="pink", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df_24h['Time'].min(), x1=df_24h['Time'].max(),
                  y0=3.9, y1=10, fillcolor="lightgreen", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=df_24h['Time'].min(), x1=df_24h['Time'].max(),
                  y0=10.01, y1=30, fillcolor="beige", opacity=0.5, layer="below", line_width=0)

    # Glucose trace
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['Glucose'],
        name='Glucose',
        visible=True,
        mode='lines',
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last meal: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Extra stats
    stats = [
        ('Carbs', df_24h['Carbohydrates'], 'orange', 'Carbs: %{y}<br>Time: %{x}<extra></extra>'),
        ('Insulin', df_24h['Rapid Insulin'] + df_24h['Long Insulin'], 'purple', 'Insulin: %{y}<br>Time: %{x}<extra></extra>'),
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

    def get_visible_array(stat_index=None):
        visible = [True] + [False] * len(stats)
        if stat_index is not None:
            visible[1 + stat_index] = True
        return visible

    # Dropdown buttons
    buttons = [
        dict(label="--extra statistics--", method="update", args=[
            {"visible": get_visible_array()},
            {"yaxis2.title": ""}
        ])
    ]

    for i, (name, _, _, _) in enumerate(stats):
        buttons.append(dict(label=name, method="update", args=[
            {"visible": get_visible_array(stat_index=i)},
            {"yaxis2.title": name}
        ]))

    # Layout
    fig.update_layout(
        updatemenus=[dict(
            type="dropdown",
            direction="down",
            x=0.0,
            y=1.15,
            showactive=True,
            buttons=buttons
        )],
        title="Glucose Trends - Last 24 Hours",
        xaxis_title="Time",
        yaxis_title="Glucose (mmol/L)",
        yaxis2=dict(
            title="Secondary Y-axis",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[-5, max(df_24h['Glucose'].max(), 15)],
        showlegend=True
    )

    return fig
