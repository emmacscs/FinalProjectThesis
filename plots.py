import pandas as pd
import plotly.graph_objects as go

def plotGlucose(df, selected_day=None):
    # Convert to datetime if not already
    df['Time'] = pd.to_datetime(df['Time'])

    # Filter to selected day (if any), otherwise default to last 24h
    if selected_day:
        day_df = df[df['Time'].dt.date == selected_day.date()].copy()
        title_suffix = selected_day.strftime("%A, %d %B %Y")
    else:
        latest_time = df['Time'].max()
        day_df = df[df['Time'] >= (latest_time - pd.Timedelta(hours=24))].copy()
        title_suffix = "Last 24 Hours"

    fig = go.Figure()

    # Background zones
    fig.add_shape(type="rect", x0=day_df['Time'].min(), x1=day_df['Time'].max(),
                  y0=-5, y1=3.9, fillcolor="pink", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=day_df['Time'].min(), x1=day_df['Time'].max(),
                  y0=3.9, y1=10, fillcolor="lightgreen", opacity=0.5, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=day_df['Time'].min(), x1=day_df['Time'].max(),
                  y0=10.01, y1=30, fillcolor="beige", opacity=0.5, layer="below", line_width=0)

    # Glucose trace
    fig.add_trace(go.Scatter(
        x=day_df['Time'],
        y=day_df['Glucose'],
        name='Glucose',
        visible=True,
        mode='lines',
        customdata=day_df[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Glucose: %{y}<br>Time: %{x}<br>Minutes since last meal: %{customdata[0]:.2f}<br>Minutes since last insulin : %{customdata[1]}<extra></extra>'
    ))

    # Extra stats
    stats = [
        ('Carbs', day_df['Carbohydrates'], 'orange', 'Carbs: %{y}<br>Time: %{x}<extra></extra>'),
        ('Insulin', day_df['Rapid Insulin'] + day_df['Long Insulin'], 'purple', 'Insulin: %{y}<br>Time: %{x}<extra></extra>'),
        ('Calories', day_df['Calories'], 'black', 'Calories: %{y}<br>Time: %{x}<extra></extra>'),
        ('Distance', day_df['Distance'], 'green', 'Distance: %{y}<br>Time: %{x}<extra></extra>'),
        ('BPM', day_df['BPM'], 'red', 'BPM: %{y}<br>Time: %{x}<extra></extra>')
    ]

    for name, y_data, color, hover in stats:
        fig.add_trace(go.Scatter(
            x=day_df['Time'],
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
        title=f"Glucose Trends – {title_suffix}",
        xaxis_title="Time",
        yaxis_title="Glucose (mmol/L)",
        yaxis2=dict(
            title="Secondary Y-axis",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        plot_bgcolor="white",
        xaxis_range=[day_df['Time'].min(), day_df['Time'].max()],
        yaxis_range=[-5, max(day_df['Glucose'].max(), 15)],
        showlegend=True
    )

    return fig
