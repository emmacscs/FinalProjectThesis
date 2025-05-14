import pandas as pd
import plotly.graph_objects as go

def filter_last_24h_or_day(df, selected_day):
    df['Time'] = pd.to_datetime(df['Time'])
    if selected_day:
        return df[df['Time'].dt.date == selected_day.date()].copy(), selected_day.strftime("%A, %d %B %Y")
    else:
        latest_time = df['Time'].max()
        return df[df['Time'] >= (latest_time - pd.Timedelta(hours=24))].copy(), "Last 24 Hours"


def plotCarbs(df, selected_day=None):
    df_24h, label = filter_last_24h_or_day(df, selected_day)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_24h['Time'],
        y=df_24h['Carbohydrates'],
        name='Carbohydrates',
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Carbs: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin: %{customdata[1]}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Carbohydrates – {label}",
        xaxis_title="Time",
        yaxis_title="Carbohydrates (g)",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[0, max(df_24h['Carbohydrates'].max(), 100)]
    )
    return fig


def plotInsulin(df, selected_day=None):
    df_24h, label = filter_last_24h_or_day(df, selected_day)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_24h['Time'],
        y=df_24h['Insulin absorption'],
        name='Insulin',
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Insulin: %{y}<br>Time: %{x}<br>Minutes since last carbs: %{customdata[0]:.2f}<br>Minutes since last insulin: %{customdata[1]}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Insulin Absorption – {label}",
        xaxis_title="Time",
        yaxis_title="Insulin (units)",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[0, max(df_24h['Insulin absorption'].max(), 50)]
    )
    return fig


def plotBPM(df, selected_day=None):
    df_24h, label = filter_last_24h_or_day(df, selected_day)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_24h['Time'],
        y=df_24h['BPM'],
        name='Heart Rate',
        mode='lines',
        customdata=df_24h[['Calories', 'Distance']].values,
        hovertemplate='BPM: %{y}<br>Time: %{x}<br>Calories: %{customdata[0]:.2f}<br>Distance: %{customdata[1]}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Heart Rate (BPM) – {label}",
        xaxis_title="Time",
        yaxis_title="BPM",
        plot_bgcolor="white",
        xaxis_range=[df_24h['Time'].min(), df_24h['Time'].max()],
        yaxis_range=[0, max(df_24h['BPM'].max(), 200)]
    )
    return fig


def plotExercise(df, selected_day=None):
    df_24h, label = filter_last_24h_or_day(df, selected_day)

    def get_colors(y, threshold, color_over, color_under):
        return [color_over if val > threshold else color_under for val in y]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_24h['Time'],
        y=df_24h['Calories'],
        name='Calories',
        marker_color=get_colors(df_24h['Calories'], 60, 'red', 'blue'),
        customdata=df_24h[['Minutes since last Carbs', 'Minutes since last Insulin']].values,
        hovertemplate='Calories: %{y}<br>Time: %{x}<br>Min since last carbs: %{customdata[0]:.2f}<br>Min since last insulin: %{customdata[1]}<extra></extra>',
        yaxis='y1'
    ))

    fig.add_trace(go.Bar(
        x=df_24h['Time'],
        y=df_24h['Distance'],
        name='Distance',
        marker_color=get_colors(df_24h['Distance'], 20, 'purple', 'green'),
        yaxis='y2'
    ))

    fig.update_layout(
        title=f"Calories & Distance – {label}",
        xaxis=dict(title="Time"),
        yaxis=dict(title="Calories", side='left', range=[0, max(df_24h['Calories'].max(), 100)]),
        yaxis2=dict(title="Distance", overlaying='y', side='right', range=[0, max(df_24h['Distance'].max(), 20)]),
        barmode='group',
        plot_bgcolor="white"
    )
    return fig
